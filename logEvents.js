//event emitter

const fs = require("fs");
const fsPromises = require("fs").promises;
const path = require("path");

const logEvents = async (message, logName) => {
  //console.log(message);

  try {
    if (!fs.existsSync(path.join(__dirname, "logs"))) {
      await fsPromises.mkdir(path.join(__dirname, "logs"));
    }
    //testing
    await fsPromises.appendFile(path.join(__dirname, "logs", logName), message);
  } catch (err) {
    //console.log(err);
  }
}

module.exports = logEvents;