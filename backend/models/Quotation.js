// System libraries
const mongoose = require("mongoose");

// Schema
const QuotationSchema = new mongoose.Schema({
  occurredAt: {
    type: Date,
    required: true,
  },
  ticker: {
    type: String,
    required: true,
  },
  close: {
    type: Number,
    default: null,
  },
  high: {
    type: Number,
    default: null,
  },
  low: {
    type: Number,
    default: null,
  },
  open: {
    type: Number,
    default: null,
  },
  volume: {
    type: Number,
    default: null,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// Export
module.exports = mongoose.model("Quotation", QuotationSchema);
