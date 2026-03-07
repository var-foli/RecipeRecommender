import pandas as pd
import ast
import collections

file_path = 'cul_recipes_dataset.csv'
df = pd.read_csv(file_path, sep=';', encoding='unicode_escape')

'''print(df.head()['Cuisine'])
print(df.shape)
print(df.columns)
print(df['Cuisine'].nunique())'''

df = df.dropna(subset=['Name', 'Category',  'Cuisine', 'Ingredients'])

df['Cuisine'] = df['Cuisine'].apply(ast.literal_eval)

cuisines = collections.defaultdict(int)
for each in df['Cuisine']:
   for cuisine in each:
      cuisines[cuisine.replace(" Inspired", "")] += 1

cuisines = collections.Counter(cuisines)
for key, count in cuisines.most_common():
    print(f"{key}: {count}")

print(cuisines)