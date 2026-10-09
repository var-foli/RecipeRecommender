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

        # insert measurement amount for each unique ingredient in a recipe - if the measurement amount already exists, add to it
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
        cursor.execute("SELECT rr.recipe_id, r.name, ARRAY_AGG(i.ingredient) as ingredients FROM recipes.recipe_relationships rr JOIN recipes.ingredients i ON rr.ingredient_id = i.ingredient_id JOIN recipes.recipes r ON rr.recipe_id = r.recipe_id GROUP BY rr.recipe_id, r.name;")

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

    # get id of measurement
    def getMeasurements(self):
        # set cursor and execute
        cursor = self.connection.cursor()

        cursor.execute("SELECT measurement_id, measurement FROM recipes.measurements")

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result
    
    # update measurement
    def updateMeasurement(self, measurement, measurement_id):
        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("UPDATE recipes.measurements SET measurement = %s WHERE measurement_id = %s;", (measurement, measurement_id))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    # get duplicate measurements
    def getDupMeasurements(self):
        # set cursor and execute
        cursor = self.connection.cursor()

        cursor.execute("SELECT measurement, ARRAY_AGG(measurement_id ORDER BY measurement_id) as dup_ids FROM recipes.measurements GROUP BY measurement HAVING COUNT(*) > 1")

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result
    
    # update old measurement IDs to map to new, grouped IDs
    def updateIngrMeasureIds(self, new_m_id, old_m_id):
        # set cursor and execute
        cursor = self.connection.cursor()
        # need to use ANY() because using with python array https://stackoverflow.com/questions/34627026/in-vs-any-operator-in-postgresql
        cursor.execute("UPDATE recipes.recipe_relationships SET measurement_id = %s WHERE measurement_id = ANY(%s);", (new_m_id, old_m_id))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    # remove any old measurements after normalization
    def deleteMeasurements(self, ids_to_delete):
        # set cursor and execute
        cursor = self.connection.cursor()

        cursor.execute("DELETE FROM recipes.measurements WHERE measurement_id = ANY(%s);", (ids_to_delete,))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    # get recipe matching requirements
    def getMatchingRecipes(self, ingredients, category, number):
        # set cursor and execute
        cursor = self.connection.cursor()

        cursor.execute("SELECT r.name, r.source, r.youtube, r.category, ARRAY_AGG(i.ingredient) as ingredients, ARRAY_AGG(rr.measurement_amount) as measurement_amounts, ARRAY_AGG(m.measurement) as measurements, COUNT(i.ingredient) FILTER (WHERE i.ingredient = ANY(%s)) as match_count FROM recipes.recipes r JOIN recipes.recipe_relationships rr ON r.recipe_id = rr.recipe_id JOIN recipes.ingredients i ON rr.ingredient_id = i.ingredient_id JOIN recipes.measurements m ON rr.measurement_id = m.measurement_id WHERE r.category = %s GROUP BY r.name, r.source, r.youtube, r.category HAVING COUNT(i.ingredient) FILTER (WHERE i.ingredient = ANY(%s)) >= %s ORDER BY match_count DESC", (ingredients, category, ingredients, int(number)))

        result = cursor.fetchall()

        # close connection
        cursor.close()

        recipeData = []

        for recipe in result:
            recipeData.append({"name": recipe[0],"source": recipe[1], "youtube": recipe[2], "category": recipe[3], "ingredients": recipe[4], "measurement_amounts": recipe[5], "measurements": recipe[6], "match_count": recipe[7]})

        return recipeData
    
    # get recipe matching requirements for any category
    def getAnyMatchingRecipes(self, ingredients, number):
        # set cursor and execute
        cursor = self.connection.cursor()

        cursor.execute("SELECT r.name, r.source, r.youtube, r.category, ARRAY_AGG(i.ingredient) as ingredients, ARRAY_AGG(rr.measurement_amount) as measurement_amounts, ARRAY_AGG(m.measurement) as measurements, COUNT(i.ingredient) FILTER (WHERE i.ingredient = ANY(%s)) as match_count FROM recipes.recipes r JOIN recipes.recipe_relationships rr ON r.recipe_id = rr.recipe_id JOIN recipes.ingredients i ON rr.ingredient_id = i.ingredient_id JOIN recipes.measurements m ON rr.measurement_id = m.measurement_id GROUP BY r.name, r.source, r.youtube, r.category HAVING COUNT(i.ingredient) FILTER (WHERE i.ingredient = ANY(%s)) >= %s ORDER BY match_count DESC", (ingredients, ingredients, int(number)))

        result = cursor.fetchall()

        # close connection
        cursor.close()

        recipeData = []

        for recipe in result:
            recipeData.append({"name": recipe[0],"source": recipe[1], "youtube": recipe[2], "category": recipe[3], "ingredients": recipe[4], "measurement_amounts": recipe[5], "measurements": recipe[6], "match_count": recipe[7]})

        return recipeData
    
    # get all unique categories
    def getCategories(self):
        # set cursor and execute
        cursor = self.connection.cursor()

        cursor.execute("SELECT DISTINCT category from recipes.recipes ORDER BY category")

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return [row[0] for row in result]
    
    # get all ingredients
    def getIngredients(self):
        cursor = self.connection.cursor()

        cursor.execute("SELECT ingredient_id, ingredient from recipes.ingredients")

        result = cursor.fetchall()

        cursor.close()

        return result
    
    # insert alternative ingredients
    def insertAltIngredient(self, ingredient_id, alt_ingredient):
        cursor = self.connection.cursor()

        cursor.execute("INSERT INTO recipes.alt_ingredients (ingredient_id, alt_ingredient) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (ingredient_id, alt_ingredient))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    # get all alternative ingredients for the ingredient
    def getAltIngredients(self, ingredient):
        cursor = self.connection.cursor()

        cursor.execute("SELECT a.alt_ingredient FROM recipes.alt_ingredients a JOIN recipes.ingredients i ON a.ingredient_id = i.ingredient_id WHERE i.ingredient = %s;", (ingredient,))

        result = cursor.fetchall()

        cursor.close()

        return result