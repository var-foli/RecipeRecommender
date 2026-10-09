import unicodedata

from connectDB import *

user = dbUser()
recipes = user.getRecipes()

#print(recipes[0])

def parse_ingredient(text):

   def parse_number(number):
      # for ranges like "1-2"
      if "-" in number:
         left, right = number.split("-")

         return (parse_number(left) + parse_number(right)) / 2

      total = 0.0
      parts = number.split()

      for part in parts:
         if "/" in part:
            num, denom = part.split("/")
            total += float(num) / float(denom)
         else:
            try:
                  total += float(part)
            except:
                  if len(part) == 1:
                     total += unicodedata.numeric(part)
                  else:
                     pass
      
      if total != 0:
         return total
      return 0

   # for cases such as "juice of 1"
   if text.lower().startswith("juice of"):
      words = text.split()
      for w in words:
         try:
            return float(w), None
         except:
            continue

   # Remove parentheses content
   without_parentheses = ""
   parentheses = False
   for c in text:
      if c == "(":
         parentheses = True
      elif c == ")":
         parentheses = False
      elif parentheses == False:
         without_parentheses += c

   without_parentheses = without_parentheses.strip()

   number = ""
   value = None

   for index, char in enumerate(without_parentheses):
      if char.isdigit() or char in ".-/ " or unicodedata.numeric(char, False):
         number += char
      else:
         value = without_parentheses[index:].strip()
         if value[:2] == 'x ':
            parts = value.split(' ')
            value = ""
            for part in parts:
               if part != 'x' and all(not c.isdigit() for c in part):
                  value = " ".join([value, part])

         elif value[:2] == '– ' or value[:2] == '- ':
            value = value[2:]

         elif value == ' ' or value == '':
            value = None
            
         else:
            value = value.split('/')[0]
         break

   if number:
      number = parse_number(number)
   else:
      return None, text

   return number, value

'''tests = [
    "1 lb",
    "1/2 cup",
    "4 Cloves Crushed",
    "To taste",
    "200ml",
    "200g/7oz",
    "Juice of 1",
    "1-2tbsp",
    "1 ½ tsp",
    "2",
    "1 (400g) tin",
    "1 1/2 cups (360 milliliters)",
    "2 x 400g tins",
]

for test in tests:
   print(test, " -> ", parse_ingredient(test))'''

measurements = set()

for recipe in recipes:
   # get recipe_id of recipe name in table
   recipe_id = recipe[0]

   for index in range(len(recipe[6])):
      amount, measurement = parse_ingredient(recipe[6][index])

      if measurement and measurement.lower() not in measurements:
         measurements.add(measurement.lower())
         # insert measurement and id form len(set) into tbl
         user.insertMeasurements(len(measurements), measurement.lower())
      
      # get measurement_id
      if measurement:
         measurement_id = user.getMeasurementID(measurement.lower())[0][0]
      else:
         measurement_id = None

      # get ingredient_id of ingredient from ingredients using index from recipe[5][index]
      ingredient = recipe[9][index]
      print(ingredient)
      ingredient_id = user.getIngredientID(ingredient)[0][0]
      print(recipe[1])
      print(ingredient_id)
      print(recipe_id)
      print(amount)
      print(measurement_id)
      
      # insert ingredient_id, recipe_id, amount, measurement_id into recipe_relationships
      user.insertRecipeRelationships(ingredient_id, recipe_id, amount, measurement_id)