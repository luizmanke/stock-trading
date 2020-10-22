# Stock Trading

The purpose of this project is to automate stock tradings on the Brazillian market.

The latests analysis and performances are availabe through services.
And, once a day, new data is collected, evaluated and stored in the cloud.

## Algorithm

The success of this solution is based on a simple forumla: select and hold profitable companies that are in good prices.
This is done by correlating profit and price indicators, such as Return on Equity and Price-Earnings, respectively.

To evaluate, a backtest was performed with data from 2012 until 2019, splitted into different periods.
The results were compared with the baseline (market index = Ibovespa).
Some of the evaluation indicators are as follows:
* Annual profit
* Sharpe ratio
* Drawdown
* Number of trades
* Profit factor
* Recuperation factor

<img src="https://github.com/luizmanke/cream-stock-market/blob/master/backend/analytics/backtest/reference/2013-09-01_2016-09-01.png" width="500">  <img src="https://github.com/luizmanke/cream-stock-market/blob/master/backend/analytics/backtest/reference/2017-01-01_2019-12-30.png" width="500">

## Data

All the data needed is obtained from web scraping.

The company's fundamentals come from:

http://fundamentus.com.br

The stock's quotations come from:

https://br.investing.com

## Architecture

To maintain free services:
* Flask framework was used to implement the API resources.
* Heroku was chosen to host the container.
* MongoDB is used to store the collected and analyzed data.

## Services

Get the latests stock analysis:

http://creamstockmarket.herokuapp.com/get-indicators

Get the performance of the solution, as well as the market:

http://creamstockmarket.herokuapp.com/get-performances

## Future work

* Create a web interface
* Make use of Machine Learning