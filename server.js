const http = require("http");
const path = require("path");
const fsPromises = require("fs").promises;
const url = require('url');

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
  try {
    const { data, error } = await supabase.schema('recipes').rpc('getcategories', {});

    if (error) {
      console.error('Supabase query error:', error);
    }

    //const categories = await response.json();
    res.status(200);
    res.send(JSON.stringify(data));
  } catch (err) {
    res.status(500);
    res.send(JSON.stringify({ error: err.message }));
  }
})

app.listen(PORT, (error) => {
  if (!error) {
    console.log(`Server running on port ${PORT}`)
  } else {
    console.error("Error:", err);
    myEmitter.emit("log", `${err.name}: ${err.message}`, `errLog.txt`);
  }
})