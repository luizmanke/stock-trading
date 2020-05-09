// System libraries
const moment = require("moment");

function getTodayDate() {
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
module.exports.getTodayDate = getTodayDate;
