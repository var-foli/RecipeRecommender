import psycopg2, os
from dotenv import load_dotenv

class dbUser: 
    def __init__(self):
        load_dotenv()

        username = os.getenv('PG_USER') 
        password = os.getenv('PG_PASS') 

        # connecting to database
        self.connection = psycopg2.connect(
            dbname="recipesDB",
            user=username,
            password=password,
            host="localhost",
            port="5432"
        )

    # insert new data into recipesDB
    def insertRecipes(self, recipe_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube):

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO recipes.recipes_old (recipe_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (recipe_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    # get only the meal_id and ingredients lists for each recipe
    def getAllIngr(self):
        query = f"SELECT recipe_id, ingredients FROM recipes.recipes_old;"

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result

    # updating ingredients after normalizing list
    def updateNormIngr(self, recipe_id, norm_ingr):

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("UPDATE recipes.recipes_old SET normalized_ingredients = %s WHERE recipe_id = %s;", (norm_ingr, recipe_id))

        # commit the update query
        self.connection.commit()

        # close connection
        cursor.close()
    
    # get all recipe data
    def getRecipes(self):
        query = f"SELECT * FROM recipes.recipes_old;"

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result
    
    # get all original measurement data
    def getMeasurements(self):
        query = f"SELECT measurements FROM recipes.recipes_old;"

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result

    # insert float measurement_id and measurement into measurements table
    def insertMeasurements(self, measurement_id, measurement):
        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO recipes.measurements (measurement_id, measurement) VALUES (%s, %s);", (measurement_id, measurement))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    # get id of measurement
    def getMeasurementID(self, measurement):
        # set cursor and execute
        cursor = self.connection.cursor()

        cursor.execute("SELECT measurement_id FROM recipes.measurements WHERE measurement = %s;", (measurement,))

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result
    
    # get id of ingredient
    def getIngredientID(self, ingredient):
        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("SELECT ingredient_id FROM recipes.ingredients WHERE ingredient = %s;", (ingredient,))

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result
    
    # insert ingredient_id, recipe_id, amount, measurement_id into recipe_relationships
    def insertRecipeRelationships(self, ingredient_id, recipe_id, amount, measurement_id):
        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO recipes.recipe_relationships (ingredient_id, recipe_id, measurement_amount, measurement_id) VALUES (%s, %s, %s, %s) ON CONFLICT (ingredient_id, recipe_id) DO UPDATE SET measurement_amount = recipe_relationships.measurement_amount + EXCLUDED.measurement_amount;", (ingredient_id, recipe_id, amount, measurement_id))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    '''# get ids of all recipes
    def getRecipeIDs(self):
        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("SELECT recipe_id FROM recipes.recipes;")

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result
    
    def getRecipeIngr(self, recipe_id):
        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("SELECT ingredient FROM recipes.recipe_relationships r JOIN recipes.ingredients i ON r.ingredient_id = i.ingredient_id WHERE recipe_id = %s;", (recipe_id,))

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result'''
    
    def getRecipeIngrs(self):
        # set cursor and execute
        cursor = self.connection.cursor()
        # https://stackoverflow.com/questions/32861500/group-by-column-to-get-array-results-in-postgresql array_agg to get ingredients as array for each recipe
        cursor.execute("SELECT recipe_id, ARRAY_AGG(ingredient) as ingredients FROM recipes.recipe_relationships r JOIN recipes.ingredients i ON r.ingredient_id = i.ingredient_id GROUP BY recipe_id;")

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result
    
    def insertRecipeCat(self, recipe_id, category):
        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("UPDATE recipes.recipes SET category = %s WHERE recipe_id = %s;", (category, recipe_id))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()