import torch, os, collections
from transformers import DistilBertForSequenceClassification, AutoTokenizer, BitsAndBytesConfig, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from dotenv import load_dotenv
from torch.utils.data import WeightedRandomSampler
from transformers import DataCollatorWithPadding

model_name = "distilbert/distilbert-base-uncased"

########
tokenizer = AutoTokenizer.from_pretrained(model_name)

load_dotenv()
path = "training_data/cul_recipes.json"

# Load json file
trainDataset = load_dataset("json", data_files=path)['train']
print(trainDataset)

split_dataset = trainDataset.train_test_split(test_size=0.2, seed=42) 
train_data = split_dataset['train'] 

split_eval = split_dataset['test'].train_test_split(test_size=0.2, seed=42)
eval_data = split_eval['train'] 
test_data = split_eval['test']

print(f'train_data:\n{train_data}')
print(f'eval_data:\n{eval_data}')
print(f'test_data:\n{test_data}')

# map of expected ids to their labels for categories, llm training requires ints as labels
labelID = {}
IDlabel = {}
for id, cuisine in enumerate(trainDataset.unique("Cuisine")):
    labelID[cuisine] = id
    IDlabel[id] = cuisine

# calculating weights (inverse of the probability of selection) for cuisine categories, lower frequencies get higher weights
categoryCounts = collections.Counter(train_data['Cuisine'])
sampleWeights = [len(train_data) / (len(categoryCounts) * categoryCounts[cuisine]) for cuisine in train_data['Cuisine']]
sampler = WeightedRandomSampler(sampleWeights, len(sampleWeights))
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

#preprocessing ingredient lists into tokens
def tokenize(data):
    recipeInfo = []
    for name, ingredients in zip(data['Name'], data['Ingredients']):
        recipeInfo.append(name + ": " + ", ".join(ingredients))
    
    tokenizedData = tokenizer(recipeInfo, padding="max_length", truncation=True)
    
    # converting cuisines to their ID value
    cuisines = []
    if 'Cuisine' in data:
        for cuisine in data['Cuisine']:
            cuisines.append(labelID[cuisine])
        tokenizedData['labels'] = cuisines

    return tokenizedData

# custom trainer to sample the categories relative to their 1/frequencies
class customTrainer(Trainer):
    def get_train_dataloader(self):
        return torch.utils.data.DataLoader(
            self.train_dataset,
            batch_size=self.args.per_device_train_batch_size,
            sampler=sampler,
            collate_fn=data_collator
        )

tokenizedTrainData = train_data.map(tokenize, batched=True).remove_columns(['Name', 'Ingredients', 'Cuisine'])
tokenizedEvalData = eval_data.map(tokenize, batched=True).remove_columns(['Name', 'Ingredients', 'Cuisine'])
tokenizedTestData = test_data.map(tokenize, batched=True).remove_columns(['Name', 'Ingredients', 'Cuisine'])

def compute_metrics(prediction):
    labels = prediction.label_ids
    predictions = prediction.predictions.argmax(-1)

    accuracy = accuracy_score(labels, predictions)
    precision = precision_score(labels, predictions, average='weighted')
    recall = recall_score(labels, predictions, average='weighted')
    f1 = f1_score(labels, predictions, average='weighted')

    with open("finetuningMetrics.log", "a") as file:
        file.write(f'accuracy = {accuracy}, precision = {precision}, recall = {recall}, f1 = {f1}\n')

    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

########


#### for loading model, fine-tuning

# use bitsandbytes config to load model in as a quantized model. this turns its 
# weights from 32-bit floating-point (FP32) numbers into 4-bit floating-point 
# numbers (NF4) (https://huggingface.co/blog/dvgodoy/fine-tuning-llm-hugging-face)
bnbConfig = BitsAndBytesConfig(
   load_in_4bit=True, # enable 4-bit quantization
   bnb_4bit_quant_type="nf4",
   bnb_4bit_use_double_quant=True,
   bnb_4bit_compute_dtype=torch.float16,
   llm_int8_skip_modules=["classifier", "pre_classifier"] # not sure if need this, saw in tutorial https://github.com/dipanjanS/training-fine-tuning-large-language-models-workshop-dhs2024/blob/main/Module-03-Parameter-Efficient-Fine-tuning-LLMs/Solutions/Module_03_LC2_Parameter-Efficient_fine-tuning_BERT_for_Named_Entity_Recognition_QLoRA_Solutions.ipynb
)

model = DistilBertForSequenceClassification.from_pretrained(
    model_name,
    num_labels=len(labelID),
    id2label = IDlabel,
    label2id = labelID,
    device_map="auto",
    #quantization_config=bnbConfig # not using quantization anymore because slowing down trainign and distilibert is a small model anyway
)

model = prepare_model_for_kbit_training(model)



'''lora_config = LoraConfig(
    r=8,  # Low-rank dimension for the rank of the weight matrices
    lora_alpha=16, # scaling factor for low-rank updates
    lora_dropout=0.05, # dropout rate, regularizes low-rank matrices
    target_modules="all-linear",  # Fine-tuning all linear layers, not sure if need to specify specific modules
)'''


# will use this to compare performance of models
lora_config = LoraConfig(
    r=16,              # down from 256
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q_lin", "k_lin", "v_lin", "out_lin"],
)

# incorporates lora config into the model
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()


training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=64, # increased from 4 to increase GPU usage
    per_device_eval_batch_size=32,
    eval_strategy="steps",
    eval_steps=50, # from 100, to see how changes affect training
    save_strategy="epoch",
    learning_rate=1e-4, # increased from 3E-5 because classification can improve with higher rate, decreased from 4e-4 for new dataset
    logging_steps=10,
    num_train_epochs=5,
    #weight_decay=0.01, # this can reduce overfitting
    fp16=True,  # Enable 16-bit floating point precision to reduce memory usage and speed up training
    push_to_hub=False,
)

'''trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenizedTrainData,
    eval_dataset=tokenizedEvalData,
    compute_metrics=compute_metrics,
)'''

trainer = customTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenizedTrainData,
    eval_dataset=tokenizedEvalData,
    compute_metrics=compute_metrics,
    data_collator=data_collator,
)

trainer.train()

# evaluate the model
results = trainer.evaluate(tokenizedEvalData)
print(f'results: {results}')

# evaluate the model
test_results = trainer.evaluate(tokenizedTestData)
print(f'test_results: {test_results}')

merged_model = model.merge_and_unload() # merging the additional adapter weights that were trained with LoRA to the original frozen weights in distilibert
merged_model.config.id2label = IDlabel
merged_model.config.label2id = labelID
merged_model.config.num_labels = len(labelID)
merged_model.save_pretrained("./distilibert_origins")
tokenizer.save_pretrained("./distilibert_origins")