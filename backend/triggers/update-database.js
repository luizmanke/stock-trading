// System libraries
const assert = require("assert");
const axios = require("axios");

describe("Update Database", async function () {
  it("Should return status 200", function () {
    const app = process.env.HEROKU_APP;
    url = `https://${app}.herokuapp.com/database/update`;
    const response = await axios.post(url);
    assert.equal(response.status, 200);
  });
});
