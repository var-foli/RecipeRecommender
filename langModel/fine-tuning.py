import torch, os
from transformers import DistilBertForSequenceClassification, AutoTokenizer, BitsAndBytesConfig, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import load_dataset
from dotenv import load_dotenv

model_name = "distilbert/distilbert-base-uncased"

########
tokenizer = AutoTokenizer.from_pretrained(model_name)

load_dotenv()
path = os.getenv('ORIGIN_DATA_PATH') 

# this command was used to download the dataset locally and in now stored at the path location
#dataset_id = "kaggle/recipe-ingredients-dataset"
#path = kagglehub.dataset_download(dataset_id)

# Load json file
trainDataset = load_dataset("json", data_files=f"{path}/train.json")['train']
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
for id, cuisine in enumerate(trainDataset.unique("cuisine")):
    labelID[cuisine] = id
    IDlabel[id] = cuisine

#preprocessing ingredient lists into tokens
def tokenize(data):
    recipeIngrs = []
    for row in data['ingredients']:
        recipeIngrs.append(", ".join(row))
    
    tokenizedData = tokenizer(recipeIngrs, padding="max_length", truncation=True)
    
    # converting cuisines to their ID value
    cuisines = []
    if 'cuisine' in data:
        for cuisine in data['cuisine']:
            cuisines.append(labelID[cuisine])
        tokenizedData['labels'] = cuisines

    return tokenizedData

tokenizedTrainData = train_data.map(tokenize, batched=True)
tokenizedEvalData = eval_data.map(tokenize, batched=True)
tokenizedTestData = test_data.map(tokenize, batched=True)

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
    r=256, # higher rank than 8 for less information loss for more complex task
    lora_alpha=64, 
    lora_dropout=0.05,
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
    eval_steps=100,
    save_strategy="epoch",
    learning_rate=4e-4, # increased from 3E-5 because classification can improve with higher rate
    logging_steps=10,
    num_train_epochs=5,
    #weight_decay=0.01, # this can reduce overfitting
    fp16=True,  # Enable 16-bit floating point precision to reduce memory usage and speed up training
    push_to_hub=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenizedTrainData,
    eval_dataset=tokenizedEvalData,
    compute_metrics=compute_metrics,
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