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
    def insertRecipes(self, meal_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube):

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO recipes.recipes (meal_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (meal_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    # get only the meal_id and ingredients lists for each recipe
    def getAllIngr(self):
        query = f"SELECT meal_id, ingredients FROM recipes.recipes;"

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result

    # updating ingredients after normalizing list
    def updateNormIngr(self, meal_id, norm_ingr):

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("UPDATE recipes.recipes SET normalized_ingredients = %s WHERE meal_id = %s;", (norm_ingr, meal_id))

        # commit the update query
        self.connection.commit()

        # close connection
        cursor.close()
    
    # get all recipe data
    def getRecipes(self):
        query = f"SELECT * FROM recipes.recipes;"

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()

        # close connection
        cursor.close()

        return result


'''user = dbUser()
print(user.getAllIngr())
user.insertRecipes()
user.getRecipes()'''
