// System libraries
const assert = require("assert");
const axios = require("axios");
require("dotenv/config");

describe("Update Database", async function () {
  it("Should return status 200 and updated status", async function () {
    this.timeout(600000);

    // Request
    const app = process.env.HEROKU_APP;
    let response = await axios.post(
      `https://${app}.herokuapp.com/update-database`
    );
    assert.equal(response.status, 200);

    // Check for update
    while (response.status != "Updated") {
      await new Promise((resolve) => setTimeout(resolve, 60000));
      response = await axios.get(
        `https://${app}.herokuapp.com/database-status`
      );
    }
  });
});
