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

router.post("/update", async (req, res) => {
  try {
    initialTime = new Date();
    connection.connectToMongoDB();

    // Funtamentals
    console.log("Fundamentals...");
    const fundamentalsList = await request.getFundamentals();
    console.log(` > ${fundamentalsList.length} files found.`);
    await connection.updateDatabase(fundamentalsList, Fundamental);

    // Quotations
    console.log("Quotations...");
    const utc = -3;
    const deltaDays = 2;
    let initialDate = new Date();
    initialDate = moment(initialDate)
      .add(utc, "hours")
      .subtract(deltaDays, "days")
      .format("DD/MM/YYYY");
    const quotationsList = await request.getQuotations(initialDate);
    console.log(` > ${quotationsList.length} files found.`);
    await connection.updateDatabase(quotationsList, Quotation);

    connection.disconnectFromMongoDB();
    elapsedTime = new Date() - initialTime;
    console.log(`Elapsed time: ${elapsedTime} ms`);

    res.json({ status: 200 });
  } catch (error) {
    console.log(error);
    res.json({ status: 401 });
  }
});

// Export
module.exports = router;
