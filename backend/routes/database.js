// System libraries
const express = require("express");
const moment = require("moment");

// Own libraries
const connection = require("../connection");
const request = require("../request");
const utils = require("../utils");
const Fundamental = require("../models/Fundamental");
const Info = require("../models/Info");
const Quotation = require("../models/Quotation");

// Routes
const router = express.Router();

router.post("/update-database", (req, res) => {
  _updateFundamentals();
  _updateQuotations();
  res.json({ status: 200 });
});

router.get("/database-status", async (req, res) => {
  let status = "Out of date";
  const fundamentalsDoc = await Info.findOne({ key: "fundamentals" });
  const quotationsDoc = await Info.findOne({ key: "quotations" });
  const todayDate = utils.getTodayDate().toISOString();
  if (
    fundamentalsDoc.occurredAt.toISOString() == todayDate &&
    quotationsDoc.occurredAt.toISOString() == todayDate
  )
    status = "Updated";
  res.json({ status: status });
});

// Functions
async function _updateFundamentals() {
  console.log("Fundamentals...");
  const fundamentalsList = await request.getFundamentals();
  console.log(` > ${fundamentalsList.length} files found.`);
  await connection.updateDatabase(fundamentalsList, Fundamental);
  const newValues = {
    occurredAt: utils.getTodayDate(),
    createdAt: moment.utc(),
  };
  await Info.updateOne({ key: "fundamentals" }, newValues);
}

async function _updateQuotations() {
  console.log("Quotations...");
  const deltaDays = 2;
  const initialDate = utils
    .getTodayDate()
    .subtract(deltaDays, "days")
    .format("DD/MM/YYYY");
  const quotationsList = await request.getQuotations(initialDate);
  console.log(` > ${quotationsList.length} files found.`);
  await connection.updateDatabase(quotationsList, Quotation);
  const newValues = {
    occurredAt: utils.getTodayDate(),
    createdAt: moment.utc(),
  };
  await Info.updateOne({ key: "quotations" }, newValues);
}

// Export
module.exports = router;
