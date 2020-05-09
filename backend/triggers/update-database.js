// System libraries
const assert = require("assert");
const axios = require("axios");
require("dotenv/config");

describe("Update Database", function () {
  it("Should return status 200 and updated", async function () {
    this.timeout(600000);
    const app = process.env.HEROKU_APP;
    const url = `https://${app}.herokuapp.com`;
    let response = null;

    // Request
    response = await axios.post(`${url}/update-database`);
    assert.equal(response["data"]["status"], 200);

    // Check for update
    const neededStatus = "Updated";
    for (i = 0; i < 5; i++) {
      await new Promise((resolve) => setTimeout(resolve, 60000));
      response = await axios.get(`${url}/database-status`);
      if (response["data"]["status"] == neededStatus) break;
    }
    assert.equal(response["data"]["status"], neededStatus);
  });
});
