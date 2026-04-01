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

if __name__ == '__main__':
   app.run(port=5000)