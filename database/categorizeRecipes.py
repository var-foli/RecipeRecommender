import os
from transformers import DistilBertForSequenceClassification, AutoTokenizer, pipeline
from dotenv import load_dotenv
from connectDB import *

user = dbUser()

load_dotenv()
path = os.getenv('ORIGIN_DATA_PATH') 

modelPath = "langModel/trainedModels/distilibert_origins"

tokenizer = AutoTokenizer.from_pretrained(modelPath)
model = DistilBertForSequenceClassification.from_pretrained(modelPath)

IDlabel = model.config.id2label
labelID = model.config.label2id

nlp = pipeline("text-classification", model=model, tokenizer=tokenizer)

recipeIngrs = user.getRecipeIngrs()

for recipe_id, name, ingredients in recipeIngrs:
   
   results = nlp(name + ": " + ", ".join(ingredients))
   category = results[0]['label'].strip("LABEL_")

   user.insertRecipeCat(recipe_id, category)

