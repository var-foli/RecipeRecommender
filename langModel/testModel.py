import os
from transformers import DistilBertForSequenceClassification, AutoTokenizer, pipeline
from dotenv import load_dotenv

load_dotenv()
path = os.getenv('ORIGIN_DATA_PATH') 

# this command was used to download the dataset locally and in now stored at the path location
#dataset_id = "kaggle/recipe-ingredients-dataset"
#path = kagglehub.dataset_download(dataset_id)

modelPath = "langModel/trainedModels/distilibert_origins"

tokenizer = AutoTokenizer.from_pretrained(modelPath)
model = DistilBertForSequenceClassification.from_pretrained(modelPath)

IDlabel = model.config.id2label
labelID = model.config.label2id

nlp = pipeline("text-classification", model=model, tokenizer=tokenizer)


examples = [
   "Mixed Beef Cuts, Chorizo, Morcilla, Salt", #Argentinian
   "Banana, Eggs, Baking Powder, Vanilla Extract, Oil, Pecan Nuts, Raspberries", #American
   "Basmati Rice, Beef Stock, Onion, Garlic, Green Chilli, Tomato, Salt, Oil, Turmeric Powder, Cardamom, Cloves, Bay Leaf", #Indian
   "Cabbage Leaves, Olive Oil, Onion, Rosemary, Celery, Basmati Rice, Cooked Chestnut, Cranberry, Vegetable Stock, Balsamic Vinegar, Clear Honey", #Polish
   "Toor dal, Water, Salt, Turmeric, Ghee, Chopped tomatoes, Cumin seeds, Mustard Seeds, Bay Leaf, Green Chilli, Ginger, Cilantro, Red Pepper, Salt, Sugar, Garam Masala" #Indian
   ]

for example in examples:
   results = nlp(example)
   print(example)
   print(results[0]['label'].strip("LABEL_"))
