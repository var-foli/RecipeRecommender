import torch, kagglehub, json, os
from transformers import AutoModelForMaskedLM, AutoTokenizer, BitsAndBytesConfig, pipeline, DistilBertForMaskedLM, DistilBertTokenizer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from datasets import Dataset, DatasetDict, load_dataset
import bitsandbytes as bnb
from dotenv import load_dotenv


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


#### for loading model, fine-tuning
model_name = "distilbert/distilbert-base-uncased"

# use bitsandbytes config to load model in as a quantized model. this turns its 
# weights from 32-bit floating-point (FP32) numbers into 4-bit floating-point 
# numbers (NF4) (https://huggingface.co/blog/dvgodoy/fine-tuning-llm-hugging-face)
bnbConfig = BitsAndBytesConfig(
   load_in_4bit=True,
   bnb_4bit_quant_type="nf4",
   bnb_4bit_use_double_quant=True,
   bnb_4bit_compute_dtype=torch.float32
)

model = AutoModelForMaskedLM.from_pretrained(
    model_name,
    device_map="auto",
    quantization_config=bnbConfig
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
print(f'model size: {model.get_memory_footprint()/1e6}')

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


########


load_dotenv()
path = os.getenv('ETHNICITY_DATA_PATH') 

# this command was used to download the dataset locally and in now stored at the path location
#dataset_id = "kaggle/recipe-ingredients-dataset"
# path = kagglehub.dataset_download(dataset_id)

# Load json file
trainDataset = load_dataset("json", data_files=f"{path}/train.json")['train']
print(trainDataset)
print(trainDataset[0])

# Load json file
testDataset = load_dataset("json", data_files=f"{path}/test.json")

#preprocessing ingredient lists into tokens
def tokenize(data):
    recipeIngrs = []
    for row in data['ingredients']:
        recipeIngrs.append(", ".join(row))
    
    return tokenizer(recipeIngrs, padding="max_length", truncation=True)

tokenizedTrainData = trainDataset.map(tokenize, batched=True)