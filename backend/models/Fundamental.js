// System libraries
const mongoose = require("mongoose");

// Schema
const FundamentalSchema = new mongoose.Schema({
  occurredAt: {
    type: Date,
    required: true,
  },
  ticker: {
    type: String,
    required: true,
  },
  priceToEarnings: {
    type: Number,
    default: null,
  },
  priceToBookValue: {
    type: Number,
    default: null,
  },
  priceToSalesRatio: {
    type: Number,
    default: null,
  },
  dividendYield: {
    type: Number,
    default: null,
  },
  priceToAsset: {
    type: Number,
    default: null,
  },
  priceToWorkingCapital: {
    type: Number,
    default: null,
  },
  priceToEbit: {
    type: Number,
    default: null,
  },
  priceToNetCurrentAsset: {
    type: Number,
    default: null,
  },
  evToEbit: {
    type: Number,
    default: null,
  },
  enterpriseValueToEbitda: {
    type: Number,
    default: null,
  },
  ebitMargin: {
    type: Number,
    default: null,
  },
  netMargin: {
    type: Number,
    default: null,
  },
  currentLiquidity: {
    type: Number,
    default: null,
  },
  returnOnEquity: {
    type: Number,
    default: null,
  },
  returnOnInvestedCapital: {
    type: Number,
    default: null,
  },
  netEquity: {
    type: Number,
    default: null,
  },
  grossDebtToEquity: {
    type: Number,
    default: null,
  },
  cagr: {
    type: Number,
    default: null,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// Export
module.exports = mongoose.model("Fundamental", FundamentalSchema);
