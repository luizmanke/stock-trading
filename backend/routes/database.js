// System libraries
const express = require("express");
const moment = require("moment");

// Own libraries
const connection = require("../connection");
const request = require("../request");
const Fundamental = require("../models/Fundamental");
const Info = require("../models/Info");
const Quotation = require("../models/Quotation");

// Routes
const router = express.Router();

router.post("/update", (req, res) => {
  updateFundamentals();
  updateQuotations();
  res.json({ status: 200 });
});

router.get("/status", async (req, res) => {
  const fundamentalsDoc = await Info.findOne({ key: "fundamentals" });
  const quotationsDoc = await Info.findOne({ key: "quotations" });
  const todayDate = _getTodayDate().toISOString();
  if (
    fundamentalsDoc.occurredAt.toISOString() == todayDate &&
    quotationsDoc.occurredAt.toISOString() == todayDate
  ) {
    res.json({ status: "Updated" });
  }
  res.json({ status: "Out of date" });
});

// Functions
async function updateFundamentals() {
  console.log("Fundamentals...");
  const fundamentalsList = await request.getFundamentals();
  console.log(` > ${fundamentalsList.length} files found.`);
  await connection.updateDatabase(fundamentalsList, Fundamental);
  const newValues = { occurredAt: _getTodayDate(), createdAt: moment.utc() };
  await Info.updateOne({ key: "quotations" }, newValues);
}

async function updateQuotations() {
  console.log("Quotations...");
  const deltaDays = 2;
  const initialDate = _getTodayDate()
    .subtract(deltaDays, "days")
    .format("DD/MM/YYYY");
  const quotationsList = await request.getQuotations(initialDate);
  console.log(` > ${quotationsList.length} files found.`);
  await connection.updateDatabase(quotationsList, Quotation);
  const newValues = { occurredAt: _getTodayDate(), createdAt: moment.utc() };
  await Info.updateOne({ key: "quotations" }, newValues);
}

function _getTodayDate() {
  const utc = -3;
  const hoursDelay = 18;
  const todayDate = moment
    .utc()
    .add(utc, "hours")
    .subtract(hoursDelay, "hours")
    .set({ hour: 0, minute: 0, second: 0, millisecond: 0 });
  return todayDate;
}

// Export
module.exports = router;
