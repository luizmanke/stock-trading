// System libraries
const assert = require("assert");
const axios = require("axios");
require("dotenv/config");

describe("Update Database", async function () {
  it("Should return status 200", async function () {
    this.timeout(600000);
    const app = process.env.HEROKU_APP;
    const response = await axios.post(
      `https://${app}.herokuapp.com/database/update`
    );
    assert.equal(response.status, 200);
    while (response.status == "Out of date") {
      await new Promise((resolve) => setTimeout(resolve, 60000));
      response = await axios.get(
        `https://${app}.herokuapp.com/database/status`
      );
    }
  });
});
