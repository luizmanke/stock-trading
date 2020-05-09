// System libraries
const mongoose = require("mongoose");

// Schema
const InfoSchema = new mongoose.Schema({
  occurredAt: {
    type: Date,
    required: true,
  },
  key: {
    type: String,
    required: true,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

// Export
module.exports = mongoose.model("Info", InfoSchema);
