// System libraries
const express = require("express");
const moment = require("moment");

// Own libraries
const connection = require("../connection");
const request = require("../request");
const Fundamental = require("../models/Fundamental");
const Quotation = require("../models/Quotation");

// Routes
const router = express.Router();

router.get("/", (req, res) => {
  res.json({ message: "Hello there." });
});

router.post("/update", async (req, res) => {
  try {
    initialTime = new Date();
    connection.connectToMongoDB();

    // Funtamentals
    console.log("Fundamentals...");
    const fundamentalsList = await request.getFundamentals();
    await connection.updateDatabase(fundamentalsList, Fundamental);

    // Quotations
    console.log("Quotations...");
    const deltaDays = 2;
    let initialDate = new Date();
    initialDate = moment(initialDate)
      .subtract(deltaDays, "days")
      .format("DD/MM/YYYY");
    const quotationsList = await request.getQuotations(initialDate);
    await connection.updateDatabase(quotationsList, Quotation);

    connection.disconnectFromMongoDB();
    elapsedTime = new Date() - initialTime;
    console.log(`Elapsed time: ${elapsedTime} ms`);

    res.json({ message: "Done." });
  } catch (error) {
    res.json({ message: String(error) });
  }
});

// Export
module.exports = router;
