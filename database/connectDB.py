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

    def insertRecipes(self, meal_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube):

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO recipes.recipes (meal_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (meal_id, name, category, ethnicity, tags, ingredients, measurements, source, youtube))

        # commit the insertion query
        self.connection.commit()

        # close connection
        cursor.close()

    def getRecipes(self):
        query = f"select * from recipes.recipes where meal_id = '52999';"

        # set cursor and execute
        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()

        # close connection
        cursor.close()

        print(result[0])

    



'''user = dbUser()

user.insertRecipes()
user.getRecipes()'''
