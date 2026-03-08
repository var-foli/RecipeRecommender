import pandas as pd
import ast
import collections

file_path = 'cul_recipes_dataset.csv'
df = pd.read_csv(file_path, sep=';', encoding='unicode_escape')

df = df[['Name', 'Cuisine', 'Ingredients']]

df = df.dropna(subset=['Name', 'Cuisine', 'Ingredients'])

df['Cuisine'] = df['Cuisine'].apply(ast.literal_eval)
df['Ingredients'] = df['Ingredients'].apply(ast.literal_eval)

###################

cuisines = collections.defaultdict(int)
for each in df['Cuisine']:
   for cuisine in each:
      cuisines[cuisine] += 1

cuisines = collections.Counter(cuisines)
for key, count in cuisines.most_common():
    print(f"{key}: {count}")

print(cuisines)

###################

for each in df['Cuisine']:
   for index in range(len(each)):
      each[index] = each[index].replace(" Inspired", "")
      each[index] = each[index].replace("U.S.", "American")
      each[index] = each[index].replace("Tex Mex", "Tex-Mex")
      if each[index] == "Latin":
         each[index] = "Latin American"
      each[index] = each[index].replace("Copycat", "American")

df.loc[df['Name'] == "DIY Finnish Lonkero (a.k.a. Long Drink)",'Cuisine'] = ["Finnish"]
df.loc[df['Name'] == "Mexico Chiquito Punch",'Cuisine'] = ["Mexican"]

df = df[df['Cuisine'] != "Inspired"]
df = df[df['Cuisine'] != "Authentic"]


###################
print("AFTER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
cuisines = collections.defaultdict(int)
for each in df['Cuisine']:
   for cuisine in each:
      cuisines[cuisine] += 1

cuisines = collections.Counter(cuisines)
for key, count in cuisines.most_common():
    print(f"{key}: {count}")

print(cuisines)

###################
