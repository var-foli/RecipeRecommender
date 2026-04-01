const http = require("http");
const path = require("path");
const fs = require("fs");
const fsPromises = require("fs").promises;
const url = require('url');
const initialize = require('./webpage_fxns');

const logEvents = require("./logEvents");
const EventEmitter = require("events");
class Emitter extends EventEmitter {};

//hosting server locally so we're just giving it port 3500
const PORT = process.env.PORT || 3500;

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
      const ingredients = parsedUrl.query.ingredients;
      const category = parsedUrl.query.category;
      const number = parsedUrl.query.numb;

      try {
        const recipes = await fetch(`http://localhost:5000/api/db?ingredients=${encodeURIComponent(ingredients)}&category=${category}&numb=${number}`)
        const response = await recipes.json()
        res.writeHead(200, { 'Content-Type': 'text/html' });
        return res.end(JSON.stringify(response));
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        return res.end(JSON.stringify({ error: err.message }));
      }

    } else if (baseUrl === '/api/categories') {

      try {
        const response = await fetch('http://localhost:5000/api/categories');
        const categories = await response.json();
        res.writeHead(200, { 'Content-Type': 'text/html' });
        return res.end(JSON.stringify(categories));
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