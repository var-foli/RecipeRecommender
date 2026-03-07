import requests, spacy
from connectDB import *

user = dbUser()
recipeIngrs = user.getAllIngr()
nlp = spacy.load("en_core_web_sm")
includedWords = {"all", "red", "white", "black", "green", "frozen", "smoked", "sweet", "fermented", "sour", "lean"}
convertWords = {"bicarbonate of soda": "baking soda", "soured cream and chive dip": "sour cream and chive dip", "caramelized sugar sauce": "caramel sauce"}

for meal_id, ingredientList in recipeIngrs:
   normIngredients = []
   for phrase in ingredientList:

      # if the ingredient is two-words-long or less, don't normalize it
      if len(phrase.split()) < 3:
         normIngredients.append(phrase.lower())
         continue

      if phrase.lower() in {"little gem lettuce", "fast action yeast", "sweetened condensed milk", "wild garlic leaves", "dried leaves of summer savoury","vegetable stock cube", "five spice powder", "ready rolled shortcrust pastry", "pork back ribs", "chinese five spice powder", "cream of tartar", "makrut lime leaves", "rice flour pancakes", "extra virgin olive oil", "hispi (sweetheart) cabbage", "fillet of steak", "baby lettuce leaves"}:
         normIngredients.append(phrase.lower())
         continue
         
      elif phrase.lower() in convertWords:
         normIngredients.append(convertWords[phrase.lower()])
         continue

      elif phrase.lower() == "raw king prawns":
         phrase = "Raw King Prawns"

      doc = nlp(phrase)
      
      # for every group of nouns in text
      for chunk in doc.noun_chunks:
         nouns = []
         
         # for each token, if token is noun/proper noun and isn't hypenated, 
         # keep it as part of the ingredient name
         for i in range(len(chunk)):
            token = chunk[i]
            # added "all" exception for all purpose flour
            if token.pos_ in ["NOUN", "PROPN"] or token.text.lower() in includedWords:
               # skip if the token is next to a hyphen
               if (i + 1 < len(chunk) and chunk[i + 1].text == "-") or (i > 0 and chunk[i - 1].text == "-"):
                  continue
               
               # additional cases to skip word
               elif (token.text.lower() == "white" and "bread" in phrase) or token.text.lower() == "beaten":
                  continue
               nouns.append(token.text)
         
         # add all ingredient names back to the normalized list of ingredients
         if nouns:
            ingredient = " ".join(nouns)
            normIngredients.append(ingredient.lower())
   if set(normIngredients)-set(ingredientList):
      print(meal_id)
      print(list(set(ingredientList)-set(normIngredients)), list(set(normIngredients)-set(ingredientList)))
    
   user.updateNormIngr(meal_id, normIngredients)