from flask import Flask, jsonify, request
from database.connectDB import *

user = dbUser()

app = Flask(__name__)

@app.route('/api/db', methods=['GET'])
def get_recipes():
   ingredients = request.args.get('ingredients')
   ingredients = ingredients.split(', ')
   category = request.args.get('category')
   number = request.args.get('numb')

   if (category == "Any"):
      recipeMatches = user.getAnyMatchingRecipes(ingredients, number)
   else:
      recipeMatches = user.getMatchingRecipes(ingredients, category, number)

   return jsonify({"recipes": recipeMatches})

@app.route('/api/categories', methods=['GET'])
def get_categories():
   categories = user.getCategories()
   print("categories is: ", categories)

   return jsonify(categories)

@app.route('/api/alternatives', methods=['GET'])
def get_alternatives():
   ingredient = request.args.get('ingredient')
   print("ingredients for: ", ingredient)

   alternatives = user.getAltIngredients(ingredient)
   print("alternatives is: ", alternatives)

   return jsonify(alternatives)

if __name__ == '__main__':
   app.run(port=5000)