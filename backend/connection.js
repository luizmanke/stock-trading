// Sistem libraries
const mongoose = require("mongoose");
require("dotenv/config");

function connectToMongoDB() {
  mongoose
    .connect(process.env.MONGODB_URL, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    })
    .catch(console.log);
}

function disconnectFromMongoDB() {
  mongoose.connection.close();
}

async function updateDatabase(dataList, model) {
  let filters = [];
  for (data of dataList) {
    let newFilter = { occurredAt: data.occurredAt, ticker: data.ticker };
    filters.push(newFilter);
  }
  await _deleteFromMongoDB(filters, model);
  await _saveInMongoDB(dataList, model);
}

async function _deleteFromMongoDB(filters, model) {
  let promises = [];
  let numberOfDeletes = 0;
  for (filter of filters) {
    let newPromise = model
      .deleteMany(filter)
      .then((result) => (numberOfDeletes += result.deletedCount));
    promises.push(newPromise);
  }
  await Promise.all(promises);
  console.log(` > ${numberOfDeletes} files deleted.`);
}

async function _saveInMongoDB(dataList, schema) {
  let promises = [];
  for (data of dataList) {
    const newSchema = new schema(data);
    let newPromise = newSchema.save();
    promises.push(newPromise);
  }
  await Promise.all(promises);
  console.log(` > ${promises.length} files added.`);
}

// Export
module.exports.connectToMongoDB = connectToMongoDB;
module.exports.disconnectFromMongoDB = disconnectFromMongoDB;
module.exports.updateDatabase = updateDatabase;
