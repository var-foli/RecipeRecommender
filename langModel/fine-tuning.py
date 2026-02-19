import torch, kagglehub, json, os
from transformers import DistilBertForSequenceClassification, AutoTokenizer, BitsAndBytesConfig, pipeline, DistilBertForMaskedLM, DistilBertTokenizer, TrainingArguments, Trainer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset, DatasetDict, load_dataset
import bitsandbytes as bnb
from dotenv import load_dotenv

model_name = "distilbert/distilbert-base-uncased"

'''# testing model initially
model_name = "distilbert-base-uncased"

tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForMaskedLM.from_pretrained(model_name)

nlp = pipeline("fill-mask", model=model, tokenizer=tokenizer)
# example of argentinian dish
example = "A dish comprised of Mixed Beef Cuts,Chorizo,Morcilla,Salt is ethnically [MASK]."

results = nlp(example)
for result in results:
    print(f"{result['token_str']}: {result['score']}")'''



########
tokenizer = AutoTokenizer.from_pretrained(model_name)

load_dotenv()
path = os.getenv('ETHNICITY_DATA_PATH') 

# this command was used to download the dataset locally and in now stored at the path location
#dataset_id = "kaggle/recipe-ingredients-dataset"
#path = kagglehub.dataset_download(dataset_id)

# Load json file
trainDataset = load_dataset("json", data_files=f"{path}/train.json")['train']
print(trainDataset)
print(trainDataset[0])

# Load json file
testDataset = load_dataset("json", data_files=f"{path}/test.json")

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

tokenizedTrainData = trainDataset.map(tokenize, batched=True)
tokenizedEvalData = testDataset.map(tokenize, batched=True)

print(tokenizedTrainData)


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
    quantization_config=bnbConfig
)

model = prepare_model_for_kbit_training(model)


lora_config = LoraConfig(
    r=8,  # Low-rank dimension for the rank of the weight matrices
    lora_alpha=16, # scaling factor for low-rank updates
    lora_dropout=0.05, # dropout rate, regularizes low-rank matrices
    target_modules="all-linear",  # Fine-tuning all linear layers, not sure if need to specify specific modules
)

# incorporates lora config into the model
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()





training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=4,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_steps=10,
    num_train_epochs=3,
    fp16=True,  # Enable mixed precision training
    push_to_hub=False,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenizedTrainData,
    eval_dataset=tokenizedEvalData
)



trainer.train()