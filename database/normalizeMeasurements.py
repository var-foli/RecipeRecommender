from connectDB import *

measurementMappings = {
   'beaten': None,
   'boiled': None,
   'boneless': None,
   'as required': None,
   'chopped': None,
   'chopped into ½-inch pieces': None,
   'bashed to break shells': None,
   'chopped': None,
   ' tins': 'tin(s)',
   'tin': 'tin(s)',
   '14-ounce can': 'can(s)', 
   'can': 'can(s)', 
   'cans': 'can(s)',
   'bulb chopped into ½-inch pieces': 'bulb',
   'crushed': None,
   'diced': None,
   'dried': None,
   'for brushing': None,
   'for frying': None,
   'for greasing': None,
   'free-range': None,
   'fry': None,
   'grating': None,
   'ground': None,
   'halved': None,
   'inch': None,
   'g': 'gram(s)',
   'l': 'liter(s)',
   'leaf': 'leaf (leaves)',
   'leaves': 'leaf (leaves)',
   'mashed': None,
   'meaty shanks': 'shanks',
   'minced': None,
   'peeled and sliced': None,
   'pod of': 'pods(s)',
   'pods': 'pods(s)',
   'pounded to 1cm thickness': None,
   'qt': 'quart(s)',
   'quartered': None,
   'quarts neutral frying': 'quart(s)',
   'rashers  chopped dry-cured': None,
   'rd': None,
   'red': None,
   'red deseeded and finely sliced, to serve': None,
   'rinsed and patted dry': None,
   'seperated': None,
   'shaved': None,
   'shredded': None,
   'skinned': None,
   'skinnless': None,
   'slice': 'slice(s)',
   'small cut chunks': None,
   'small cut into chunks': None,
   'small finely diced': 'small',
   'small peeled and coarsely grated': 'small',
   'spinkling': 'sprinkling',
   'sprinking': 'sprinkling',
   'stalk chopped': 'stalk',
   'steamed': None,
   'stick': 'stick(s)',
   'sticks': 'stick(s)',
   'tail': None,
   'thin cut': None,
   'thin piece': 'piece(s)',
   'thinly sliced': None,
   'thumb sized peeled and very finely grated': None,
   'to glaze': None,
   'to serve': None,
   'top': None,
   'trimmed and roughly chopped; reserve any fronds to garnish': None,
   'white': None,
   'yolk': None,
   'yolkes': None,
   'ancho': None,
   # special case, 1 and 1/8 cup of water
   'and 1': 'cup(s)',
   'cm finely chopped': 'cm',
   'cm piece': 'cm',
   'cm piece finely chopped': 'cm',
   'cut thick slices': 'slices',
   'cut into 1': None,
   'cut thin wedges': None,
   'cut into 1.5cm-thick slices': None,
   'fresh kaffir leaves': None,
   'juice': None,
   'the juice and zest of one': None,
   'zest and juice of 1': None,
   'zest and juice of 2': None,
   'zest of 1': None,
   'zest of 2': None,
   'juice of 1, the other halved': None,
   'juice of 1/2': None,
   'juice of half': None,
   'juice/zest of one': None,
   'pieces': 'piece(s)',
   'slices': 'slice(s)',
   'whole': None
}

def convertMeasurement(measurement):
   if 'clove' in measurement:
      return 'clove(s)'

   elif 'cup' in measurement:
      return 'cup(s)'

   elif 'drizzle' in measurement:
      return 'drizzle'

   elif len(measurement) > 2 and measurement[:2] == 'g ':
      return 'gram(s)'

   elif 'garnish' in measurement:
      return 'garnish'

   elif 'handful' in measurement:
      return 'handful(s)'

   elif 'head' in measurement:
      return 'head(s)'

   elif 'kg' in measurement:
      return 'kilogram(s)'

   elif 'knob' in measurement:
      return 'knob(s)'

   elif 'litre' in measurement:
      return 'liter(s)'

   elif 'large' in measurement:
      return 'large'

   elif 'lb' in measurement:
      return 'pound(s)'

   elif 'medium' in measurement:
      return 'medium'

   elif 'ml' in measurement:
      return 'milliliter(s)'

   elif 'ounce' in measurement:
      return 'ounce(s)'

   elif 'oz' in measurement:
      return 'ounce(s)'

   elif 'pack' in measurement:
      return 'pack'

   elif 'part' in measurement:
      return 'part(s)'

   elif 'pinch' in measurement:
      return 'pinch(es)'

   elif 'pound' in measurement:
      return 'pound(s)'

   elif 'slices' in measurement:
      return 'slice(s)'

   elif 'sprig' in measurement:
      return 'sprig(s)'

   elif 'tablespoon' in measurement or 'tbls' in measurement or 'tbs' in measurement or 'tbsp' in measurement:
      return 'tablespoon(s)'

   elif 'teaspoon' in measurement or 'tsp' in measurement:
      return 'teaspoon(s)'

   elif 'slices' in measurement:
      return 'slice(s)'

   elif 'cut' in measurement:
      return None

   elif 'finely' in measurement:
      return None

   elif 'sliced' in measurement:
      return None
   
   elif measurement and 'grams' in measurement:
      return 'gram(s)'

   elif measurement and 'grated' in measurement:
      return None
   
   else:
      return measurement
   
user = dbUser()
measurements = user.getMeasurements()

# updating measurements accordinly
'''for measurement_id, measurement in measurements:
   if measurement in measurementMappings:
      newMeasurement = measurementMappings[measurement]

   else:
      newMeasurement = convertMeasurement(measurement)

   if newMeasurement != measurement:
      user.updateMeasurement(newMeasurement, measurement_id)'''


duplicateMeasurements = user.getDupMeasurements()

for measurement, duplicateIds in duplicateMeasurements:
   # point all measurement ids to first id and delete the old ids
   user.updateIngrMeasureIds(duplicateIds[0], duplicateIds[1:])
   user.deleteMeasurements(duplicateIds[1:])