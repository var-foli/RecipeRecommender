import ollama

def askOllama():

   response = ollama.chat(model='mistral', messages=[
      {
         'role': 'user',
         'content': f'Return an array of ingredient substitutions for paprika inside of square brackets, and no other text.',
         'temperature': 0,
      }
   ])
   print(response['message']['content'])

   response = ollama.chat(model='mistral', messages=[
      {
         'role': 'user',
         'content': f'Return an array of ingredient substitutions for mayonnaise inside of square brackets, and no other text.',
         'temperature': 0,
      }
   ])
   print(response['message']['content'])

   response = ollama.chat(model='mistral', messages=[
      {
         'role': 'user',
         'content': f'Return an array of ingredient substitutions for buttermilk inside of square brackets, and no other text.',
         'temperature': 0,
      }
   ])
   print(response['message']['content'])

   response = ollama.chat(model='mistral', messages=[
      {
         'role': 'user',
         'content': f'Return an array of ingredient substitutions for yautia inside of square brackets, and no other text.',
         'temperature': 0,
      }
   ])
   print(response['message']['content'])

askOllama()