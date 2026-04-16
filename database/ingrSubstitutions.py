from ollama import Client
from connectDB import *

user = dbUser()
client = Client()

def askOllama(ingredient):

   message=[
      {
         'role': 'user',
         'content': f'Return an array of commonly found ingredient substitutions for {ingredient} inside of square brackets, and no other text. If no substitutions are possible, return an empty array.',
      }
   ]

   return client.chat('gemma4:31b-cloud', messages=message)['message']['content']

def parseSubstitutions(substitutions):
   result = []
   start = substitutions.find('[')
   end = substitutions.find(']')

   if start == -1 or end == -1:
      return []
   
   altIngredients = substitutions[start+1:end].split(", ")
   for ingredient in altIngredients:
      ingredient = ingredient.strip('"')
      result.append(ingredient)

   return result


ingredients = user.getIngredients()

for ingredient_id, ingredient in ingredients:
   substitutions = askOllama(ingredient)
   substitutionsArray = parseSubstitutions(substitutions)

   for substitution in substitutionsArray:
      user.insertAltIngredient(ingredient_id, substitution)