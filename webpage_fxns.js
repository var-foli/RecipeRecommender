const fs = require('fs');

if (typeof localStorage === "undefined" || localStorage === null) {
    var LocalStorage = require('node-localstorage').LocalStorage;
    localStorage = new LocalStorage('./scratch');
  }

function Recipe(name,book,page,ingredients) {
    this.name = name;
    this.book = book;
    this.page = page;
    this.ingredients = ingredients;
}

function loadFromJson() {
    let text = fs.readFileSync('recipes.json','utf8');
    let recipes = JSON.parse(text);
    let newlist = [];
    for (let i=0; i < recipes.length; i++) {
        let item = recipes[i];
        let newRecipe = new Recipe(item.name,item.book,item.page,item.ingredients);
        newlist.push(newRecipe);
    }
    return newlist;
}

function saveToJson(list) {
    list = JSON.stringify(list);
    fs.writeFileSync("recipes.json",list); 
}

async function find_recipes(list, ingr, numb) {

    let my_ingr = ingr;
    let my_ing_arr = my_ingr.split(", ");
    let number_matches = Number(numb);
    let recipes = {};

    for (let i=0; i < list.length; i++) {
        let recipe_set = new Set(list[i].ingredients);
        let matches = my_ing_arr.filter(element => recipe_set.has(element));
        if (matches.length >= number_matches || matches.length >= list[i].ingredients.length) {
            recipes[list[i].name] = new Array(list[i].book, list[i].page);
        }
    }

    console.log(my_ingr);
    console.log(my_ing_arr);
    console.log(number_matches);
    console.log(recipes);
    return recipes;
    //console.log(recipes);
}

function initialize(recipes, numb) {
    sauerkrautsoup = new Recipe("Sauerkraut Soup", "Joy of Cooking", 238, ["vegetable oil", "kielbasa", "onion", "garlic cloves", "smoked paprika", "caraway seeds", "cabbage", "salt", "sauerkraut", "diced tomatoes", "chicken stock","vegetable stock","chicken broth","vegetable broth", "russet potato", "black pepper", "sour cream", "yogurt"]);
    kimchijjigae = new Recipe("Kimchi Jjigae (Kimchi-Tofu Stew)", "Joy of Cooking", 239, ["vegetable oil", "gochujang", "garlic cloves", "kimchi", "pork shoulder", "country ribs", "pork belly", "gochugaru", "red pepper flakes", "chicken stock","vegetable stock","chicken broth","vegetable broth", "kimchi brine", "firm tofu", "soft tofu", "silken tofu", "toasted sesame oil", "eggs", "green onions", "black pepper", "soy sauce", "fish sauce", "rice"]);
    greenpeasoup = new Recipe("Green Pea Soup", "Joy of Cooking", 238, ["frozen peas", "green peas", "butter", "butter lettuce", "onion", "celery", "chicken stock","vegetable stock","chicken broth","vegetable broth", "potatoes", "tarragon", "mint", "salt", "black pepper", "butter dumplings", "croutons", "sour cream", "creme fraiche", "chopped mint", "tarragon"]);
    newlist = loadFromJson();
    //newlist.push(sauerkrautsoup);
    //newlist.push(kimchijjigae);
    //newlist.push(greenpeasoup);
    //saveToJson(newlist);
    return find_recipes(newlist, recipes, numb);
}

module.exports = initialize;

