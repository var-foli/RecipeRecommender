const path = require("path");

const logEvents = require("./logEvents");
const EventEmitter = require("events");
class Emitter extends EventEmitter {};
const { createClient } = require("@supabase/supabase-js");
const dotenv = require('dotenv');
const express = require('express');

const app = express();

dotenv.config();

//hosting server locally so we're just giving it port 3500
const PORT = process.env.PORT || 3500;

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

const myEmitter = new Emitter();
myEmitter.on("log", (msg, fileName) => logEvents(msg, fileName));

// changed to public according to limitation for static assets https://vercel.com/docs/frameworks/backend/express
app.use(express.static(path.join(__dirname, 'public')))

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'page1.html'))
})

app.get('/api/recipes', async (req, res) => {
  /*
  // for local testing
  const ingredients = req.query.ingredients;
  const category = req.query.category;
  const number = req.query.numb;

  if (category == "Any") {

    try {
      const recipes = await fetch(`http://localhost:5000/api/db?ingredients=${encodeURIComponent(ingredients)}&category=${category}&numb=${number}`)
      const response = await recipes.json()
      res.send(JSON.stringify(response));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ error: err.message }));
    }

  } else {
    try {
      const recipes = await fetch(`http://localhost:5000/api/db?ingredients=${encodeURIComponent(ingredients)}&category=${category}&numb=${number}`)
      const response = await recipes.json()
      res.send(JSON.stringify(response));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      return res.end(JSON.stringify({ error: err.message }));
    }
  }*/
  
  // for vercel deployment
  const ingredients = req.query.ingredients.split(", ");
  const category = req.query.category;
  const number = Number(req.query.numb);

  if (category == "Any") {
    try {
      const { data, error } = await supabase.schema('recipes').rpc('getanymatchingrecipes', {ingredients, number});

      if (error) {
        console.error('Supabase query error:', error);
      }

      res.status(200);
      res.send(JSON.stringify({recipes: data}));
    } catch (err) {
      res.status(500);
      res.send(JSON.stringify({ error: err.message }));
    }
  } else {
    
    try {
      const { data, error } = await supabase.schema('recipes').rpc('getmatchingrecipes', {ingredients, category, number});

      if (error) {
        console.error('Supabase query error:', error);
      }

      res.status(200);
      res.send(JSON.stringify({recipes: data}));
    } catch (err) {
      res.status(500);
      res.send(JSON.stringify({ error: err.message }));
    }
  }
})

app.get('/api/categories', async (req, res) => {
  /*
  // for local testing
  try {
    const response = await fetch('http://localhost:5000/api/categories');
    const categories = await response.json();
    res.send(JSON.stringify(categories));
  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ error: err.message }));
  }
  */
  
  // for vercel deployment
  try {
    const { data, error } = await supabase.schema('recipes').rpc('getcategories', {});

    if (error) {
      console.error('Supabase query error:', error);
    }

    res.status(200);
    res.send(JSON.stringify(data));
  } catch (err) {
    res.status(500);
    res.send(JSON.stringify({ error: err.message }));
  }
})

app.get('/api/alternatives', async (req, res) => {
  /*
  // for local testing
  const ingredient = req.query.ingredient;

  try {
    const recipes = await fetch(`http://localhost:5000/api/alternatives?ingredient=${ingredient}`)
    const response = await recipes.json()
    res.send(JSON.stringify(response));
  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ error: err.message }));
  }*/

  // for vercel deployment
  const ingredient = req.query.ingredient;

  try {
    const { data, error } = await supabase.schema('recipes').rpc('getaltingredients', {ingredient});

    if (error) {
      console.error('Supabase query error:', error);
    }

    res.status(200);
    res.send(JSON.stringify({ alternatives: data }));
  } catch (err) {
    res.status(500);
    res.send(JSON.stringify({ error: err.message }));
  }

});

app.listen(PORT, (error) => {
  if (!error) {
    console.log(`Server running on port ${PORT}`)
  } else {
    console.error("Error:", err);
    myEmitter.emit("log", `${err.name}: ${err.message}`, `errLog.txt`);
  }
})