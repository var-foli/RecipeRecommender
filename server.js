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
  const hasQuery = Object.keys(parsedUrl.query).length > 0;
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
    // Handle query parameters case (recipe search)
    if (hasQuery && (baseUrl === "/" || baseUrl === "/page1.html")) {
      const fileContent = await fsPromises.readFile(filePath, "utf8");
      output = await initialize(params.get("/?recipes"), params.get("numb"));
      const modifiedContent = fileContent.replace("{{output}}", JSON.stringify(output, null, 2));
      res.writeHead(200, { "Content-Type": "text/html" });
      return res.end(modifiedContent);
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