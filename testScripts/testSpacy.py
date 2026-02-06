import spacy

nlp = spacy.load("en_core_web_sm")
#nlp = spacy.load("en_core_web_trf")

def simplify_ingredient(text):
   doc = nlp(text)
   ingredients = []
    
   for chunk in doc.noun_chunks:
      nouns = []
      
      for i in range(len(chunk)):
         token = chunk[i]
         #print(token.text)
         if token.pos_ in ["NOUN", "PROPN"]:
            # skip if the token is next to a hyphen
            if (i + 1 < len(chunk) and chunk[i + 1].text == "-") or (i > 0 and chunk[i - 1].text == "-"):
               continue
            nouns.append(token.text)
        
      ingredient = " ".join(nouns)
      ingredients.append(ingredient)
    
   print(ingredients)

simplify_ingredient("free-range eggs")
simplify_ingredient("organic grass-fed butter")
simplify_ingredient("fresh basil and mushrooms")
simplify_ingredient("Corn Arepa Filled With Mozarella Cheese")

