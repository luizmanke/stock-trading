// System libraries
const axios = require("axios");
const moment = require("moment");
const querystring = require("querystring");
const HtmlTableToJson = require("html-table-to-json");

async function getFundamentals() {
  const url = "http://fundamentus.com.br/resultado.php";
  const response = await axios.get(url);
  if (response.status != 200) throw "Error during request.";
  const jsonTables = new HtmlTableToJson(response.data);
  const inputJsons = jsonTables["results"][0];
  const fundamentals = _processFundamentals(inputJsons);
  return fundamentals;
}

async function getQuotations(initialDate = "01/01/2020") {
  // Variables
  const options = {
    method: "post",
    url: "https://br.investing.com/instruments/HistoricalDataAjax",
    headers: {
      "User-Agent": "Mozilla/5.0",
      "X-Requested-With": "XMLHttpRequest",
    },
  };
  let data = {
    st_date: initialDate,
    end_date: "01/01/2030",
    interval_sec: "Daily",
  };

  // Get companies
  const companies = await _getCompanies();

  // Get quotations
  let quotations = [];
  for (ticker of Object.keys(companies)) {
    console.log(ticker);
    data["curr_id"] = companies[ticker]["id"];
    options.data = querystring.encode(data);
    const response = await axios(options);
    if (response.status != 200) throw "Error during request.";
    const jsonTables = new HtmlTableToJson(response.data);
    const inputJsons = jsonTables["results"][0];
    const outputJsons = _processQuotations(inputJsons, ticker);
    quotations = quotations.concat(outputJsons);
  }
  console.log(quotations.length);
  return quotations;
}

function _processFundamentals(inputJsons) {
  // Loop jsons
  outputJsons = inputJsons;
  for (json of outputJsons) {
    // Rename
    const KEY_PAIRS = {
      Papel: "ticker",
      "Cota��o": "close",
      "P/L": "priceToEarnings",
      "P/VP": "priceToBookValue",
      PSR: "priceToSalesRatio",
      "Div.Yield": "dividendYield",
      "P/Ativo": "priceToAsset",
      "P/Cap.Giro": "priceToWorkingCapital",
      "P/EBIT": "priceToEbit",
      "P/Ativ Circ.Liq": "priceToNetCurrentAsset",
      "Liq.2meses": "volume",
      "EV/EBIT": "enterpriseValueToEbit",
      "EV/EBITDA": "enterpriseValueToEbitda",
      "Mrg Ebit": "ebitMargin",
      "Mrg. L�q.": "netMargin",
      "Liq. Corr.": "currentLiquidity",
      ROIC: "returnOnInvestedCapital",
      ROE: "returnOnEquity",
      "Patrim. L�q": "netEquity",
      "D�v.Brut/ Patrim.": "grossDebtToEquity",
      "Cresc. Rec.5a": "cagr",
    };
    for (const [old_key, new_key] of Object.entries(KEY_PAIRS)) {
      json[new_key] = json[old_key];
      delete json[old_key];
    }

    // String to float
    for (const key in json) {
      if (key != "ticker") {
        json[key] = json[key].replace("%", "");
        json[key] = json[key].replace(/[.]/g, "");
        json[key] = json[key].replace(/[,]/g, ".");
        json[key] = parseFloat(json[key]);
      }
    }

    // Rescale
    const COLUMNS = [
      "close",
      "priceToEarnings",
      "priceToBookValue",
      "priceToWorkingCapital",
      "priceToEbit",
      "priceToNetCurrentAsset",
      "enterpriseValueToEbit",
      "enterpriseValueToEbitda",
      "currentLiquidity",
      "grossDebtToEquity",
      "volume",
      "netEquity",
    ];
    for (column of COLUMNS) {
      json[column] = json[column] / 100;
    }
    for (column of ["priceToSalesRatio", "priceToAsset"]) {
      json[column] = json[column] / 1000;
    }

    // Add occurredAt
    let utc = new Date().toISOString();
    utc = `${utc.slice(0, 10)}T00:00:00.000Z`;
    json["occurredAt"] = utc;
  }
  return outputJsons;
}

async function _getCompanies() {
  // Variables
  const maxPageNumbers = 100;
  const options = {
    method: "post",
    url: "https://br.investing.com/stock-screener/Service/SearchStocks",
    headers: {
      "User-Agent": "Mozilla/5.0",
      "X-Requested-With": "XMLHttpRequest",
    },
  };
  let data = {
    "country[]": "32",
    "exchange[]": "47",
    "order[col]": "viewData.symbol",
    "order[dir]": "a",
  };

  // Loop pages
  let companies = {};
  for (pageNumber = 1; pageNumber < maxPageNumbers + 1; pageNumber++) {
    data["pn"] = pageNumber;
    options.data = querystring.encode(data);
    const response = await axios(options);
    if (response.status != 200) throw "Error during request.";

    // Loop tickers
    for (content of response.data["hits"]) {
      contentData = content["viewData"];
      ticker = contentData["symbol"];
      companies[ticker] = {
        name: contentData["name"],
        link: contentData["link"],
        volume: content["avg_volume"] || 0,
        id: content["pair_ID"],
      };
    }

    if (Object.keys(companies).length == response.data["totalCount"]) break;
  }

  // Add market ticker
  companies["IBOV"] = {
    name: "IBOV",
    link: null,
    volume: 1000000000,
    id: "941612",
  };

  return companies;
}

function _processQuotations(inputJsons, ticker) {
  // Loop jsons
  let outputJsons = [];
  for (json of inputJsons) {
    if (!json["Último"]) continue;

    // Rename
    const KEY_PAIRS = {
      Data: "occurredAt",
      Último: "close",
      Abertura: "open",
      Máxima: "high",
      Mínima: "low",
      "Vol.": "volume",
      "Var%": "change",
    };
    for (const [old_key, new_key] of Object.entries(KEY_PAIRS)) {
      json[new_key] = json[old_key];
      delete json[old_key];
    }

    // String to date
    json["occurredAt"] = moment(json["occurredAt"], "DD.MM.YYYY").toISOString();

    // String to float
    delete json["change"];
    let multiplier = 1;
    switch (json["volume"][json["volume"].length - 1]) {
      case "K":
        multiplier = 1000;
        break;
      case "M":
        multiplier = 1000000;
        break;
      case "B":
        multiplier = 1000000000;
        break;
    }
    for (const key in json) {
      if (key != "occurredAt") {
        json[key] = json[key].replace("%", "");
        json[key] = json[key].replace(/\b[-]\b/g, "");
        json[key] = json[key].replace(/[,]/g, ".");
        json[key] = parseFloat(json[key]);
      }
    }

    // Rescale
    for (key of ["close", "open", "high", "low"]) {
      json[key] = json[key] / 100;
    }
    json["volume"] = json["volume"] * multiplier;

    // Add ticker
    json["ticker"] = ticker;

    outputJsons.push(json);
  }
  return outputJsons;
}

// Export
module.exports.getFundamentals = getFundamentals;
module.exports.getQuotations = getQuotations;
