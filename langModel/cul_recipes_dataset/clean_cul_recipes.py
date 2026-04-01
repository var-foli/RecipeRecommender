import pandas as pd
import ast
import collections


def leastFrequent(cuisineList, cuisines):
   leastFrequent = ""

   # get the least frequent cuisine based on cuisine frequencies dict
   for value in cuisineList:
      if leastFrequent == "":
         leastFrequent = value
      else:
         if cuisines[value] < cuisines[leastFrequent]:
            leastFrequent = value
   
   return leastFrequent

def ingredientsList(ingredientsData):
   ingredientNames = []

   for ingredientDict in ingredientsData:
      ingredientNames.append(ingredientDict["ingredient"])

   return ingredientNames



file_path = 'cul_recipes_dataset.csv'

df = pd.read_csv(file_path, sep=';', encoding='latin-1')

df = df[['Name', 'Cuisine', 'Ingredients']]

df = df.dropna(subset=['Name', 'Cuisine', 'Ingredients'])

df['Cuisine'] = df['Cuisine'].apply(ast.literal_eval)
df['Ingredients'] = df['Ingredients'].apply(ast.literal_eval)

df = df.drop_duplicates(subset=['Name'])

print(df)

###################

cuisines = collections.defaultdict(int)
for each in df['Cuisine']:
   for cuisine in each:
      cuisines[cuisine] += 1

OGcuisines = collections.Counter(cuisines)

#print(OGcuisines.most_common())

###################

for each in df['Cuisine']:
   for index in range(len(each)):
      each[index] = each[index].replace(" Inspired", "")
      each[index] = each[index].replace("U.S.", "American")
      each[index] = each[index].replace("Tex Mex", "Tex-Mex")
      each[index] = each[index].replace("Copycat", "American")
      if each[index] == "Latin":
         each[index] = "Latin American"
      
df.at[df.index[df['Name'] == "DIY Finnish Lonkero (a.k.a. Long Drink)"][0], 'Cuisine'] = ["Finnish"]
df.at[df.index[df['Name'] == "Mexico Chiquito Punch"][0], 'Cuisine'] = ["Mexican"]
df.at[df.index[df['Name'] == "Trinidad Pelau"][0], 'Cuisine'] = ["Caribbean"]

# removing instances of Inspired, Authentic, or World from cuisine categories and dropping rows that are no longer labeled
df['Cuisine'] = df['Cuisine'].apply(lambda cuisineList: [cuisine for cuisine in cuisineList if cuisine not in ["Inspired", "Authentic", "World"]])
df = df[df['Cuisine'].apply(lambda cuisineList: len(cuisineList) > 0)]

# remove duplicates from cuisine lists
df['Cuisine'] = df['Cuisine'].apply(lambda cuisineList: list(set(cuisineList)))

# initialize dictionary of frequencies of each cuisine
cuisines = collections.defaultdict(int)
for each in df['Cuisine']:
   for cuisine in each:
      cuisines[cuisine] += 1
# convert all lists of cuisines to just one, least frequent cuisine
df['Cuisine'] = df['Cuisine'].apply(lambda cuisineList: leastFrequent(cuisineList, cuisines))

df['Ingredients'] = df['Ingredients'].apply(lambda ingredientsData: ingredientsList(ingredientsData))

#remove ® symbol from any recipe names
df['Name'] = df['Name'].apply(lambda recipeName: recipeName.replace("®",""))

###################
print("AFTER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
cuisines = collections.defaultdict(int)
for each in df['Cuisine']:
   cuisines[each] += 1

cuisines = collections.Counter(cuisines)
for key, count in cuisines.most_common():
    print(f"{key}: {count}")

print(df)

#print(cuisines.most_common())

'''for key, count in cuisines.most_common():
   print(f'{key}: {count}-{OGcuisines[key]} = {count - OGcuisines[key]}')

print(df.loc[df['Name'] == "DIY Finnish Lonkero (a.k.a. Long Drink)"])


pd.set_option('display.max_colwidth', None)
print(df[df['Cuisine'].apply(lambda cuisineList: len(cuisineList) > 1)][['Name','Cuisine']])'''


###################

json_string = df.to_json(orient='records')

with open("cul_recipes.json", 'w') as myFile:
   myFile.write(json_string)