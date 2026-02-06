import requests
from database.connectDB import *

mealAPIurl = "https://www.themealdb.com/api/json/v1/1/search.php?f="
user = dbUser()

for ascii in list(range(48, 58)) + list(range(97, 123)):
   letter = chr(ascii)
   response = requests.get(f'{mealAPIurl}{letter}')
   
   if not response.ok:
      print(f"Request for {letter} failed with status code: {response.status_code}")
      continue

   if response.json()['meals'] == None:
      continue

   for data in response.json()['meals']:

      meal_id = data['idMeal']
      name = data['strMeal']
      category = data['strCategory']
      ethnicity = data['strArea']

      if data['strTags'] == None:
         tags = None
      else:
         tags = data['strTags'].split(",")

      ingredients = []
      measurements = []

      for ingrNum in range(1, 21):
         if data[f'strIngredient{ingrNum}'] != None and data[f'strIngredient{ingrNum}'] != "":
            ingredients.append(data[f'strIngredient{ingrNum}'])
         if data[f'strMeasure{ingrNum}'] != None and data[f'strMeasure{ingrNum}'] != "" and data[f'strMeasure{ingrNum}'] != " ":
            measurements.append(data[f'strMeasure{ingrNum}'])

      source = data['strSource']
      youtube = data['strYoutube']

      print(f'parsed data for {name}, {meal_id}')

      try:
         user.insertRecipes(meal_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube)
      except Exception as e:
         print(f"faced exception when adding to DB for {name}, {meal_id}: {e}")

user.getRecipes()