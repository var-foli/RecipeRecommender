const http = require("http");
const path = require("path");
const fsPromises = require("fs").promises;
const url = require('url');

const logEvents = require("./logEvents");
const EventEmitter = require("events");
class Emitter extends EventEmitter {};
const { createClient } = require("@supabase/supabase-js");
const dotenv = require('dotenv');

dotenv.config();

//hosting server locally so we're just giving it port 3500
const PORT = process.env.PORT || 3500;

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

const myEmitter = new Emitter();
myEmitter.on("log", (msg, fileName) => logEvents(msg, fileName));

//function for serving the data
const serveFile = async (filePath, contentType, response) => {
  try {
    const rawData = await fsPromises.readFile(filePath);
    response.writeHead(200, {"Content-Type": contentType})
    response.end(rawData);
  } catch (err) {
    myEmitter.emit("log", `${err.name}: ${err.message}`, `errLog.txt`);
    response.statusCode = 500;
    response.end();
  }
}

//creating server, takes a request (req) and a response(res)
const server = http.createServer( async (req, res) => {

  const parsedUrl = url.parse(req.url, true);
  const params = new URLSearchParams(req.url);
  const baseUrl = parsedUrl.pathname;
  const extension = path.extname(baseUrl);

  let contentType;

  //using switch statement to indicate content type
  switch (extension) {
    case ".css":
      contentType = "text/css";
      break;
    case ".js":
      contentType = "text/javascript";
      break;
    case ".json":
      contentType = "application/json";
      break;
    case ".jpg":
      contentType = "image/jpeg";
      break;
    case ".ico":
      break;
    //covers cases of / or .html or ?
    default:
      contentType = "text/html";
  }

  // Determine the file path based on URL
  let filePath = baseUrl === "/" ? path.join(__dirname, "page1.html") : path.join(__dirname, baseUrl);
  
  // If there's no extension and URL doesn't end with /, add .html
  if (!extension && baseUrl.slice(-1) !== "/") {
    filePath += ".html";
  }
  
  try {
    // api endpoints for requesting recipes/category data
    if (baseUrl === '/api/recipes') {
      const ingredients = parsedUrl.query.ingredients.split(", ");
      const category = parsedUrl.query.category;
      const number = Number(parsedUrl.query.numb);

      if (category == "Any") {
        try {
          const { data, error } = await supabase.schema('recipes').rpc('getanymatchingrecipes', {ingredients, number});

          if (error) {
            console.error('Supabase query error:', error);
          }

          res.writeHead(200, { 'Content-Type': 'text/html' });
          return res.end(JSON.stringify({recipes: data}));
        } catch (err) {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          return res.end(JSON.stringify({ error: err.message }));
        }
      } else {
        try {
          const { data, error } = await supabase.schema('recipes').rpc('getmatchingrecipes', {ingredients, category, number});

          if (error) {
            console.error('Supabase query error:', error);
          }

          res.writeHead(200, { 'Content-Type': 'text/html' });
          return res.end(JSON.stringify({recipes: data}));
        } catch (err) {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          return res.end(JSON.stringify({ error: err.message }));
        }
      }


      

    } else if (baseUrl === '/api/categories') {

      try {
        const { data, error } = await supabase.schema('recipes').rpc('getcategories', {});
        
        if (error) {
          console.error('Supabase query error:', error);
        }

        //const categories = await response.json();
        res.writeHead(200, { 'Content-Type': 'text/html' });
        return res.end(JSON.stringify(data));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: err.message }));
      }

    }
    
    // Serve the file normally
    await serveFile(filePath, contentType, res);
    
  } catch (err) {
    console.error("Error:", err);
    myEmitter.emit("log", `${err.name}: ${err.message}`, `errLog.txt`);
    res.statusCode = 500;
    res.end("Server Error");
  }
});

server.listen(PORT, () => console.log(`Server running on port ${PORT}`))