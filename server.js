// System libraries
const bodyParser = require("body-parser");
const express = require("express");

// Own libraries
const databaseRoute = require("./backend/routes/database");
const connection = require("./backend/connection");

// Configurations
const port = process.env.PORT || 5000;

// Create server
const server = express();
connection.connectToMongoDB();

// Middlewares
server.use(bodyParser.json());
server.use("/database", databaseRoute);

// Hello world
server.get("/", (req, res) => {
  res.json({ message: "Hello world!" });
});

// Start server
server.listen(port, () => {
  console.log(`Server running on port ${port}...`);
});
