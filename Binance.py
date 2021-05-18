import binance.client as client

#https://docs.bokeh.org/en/latest/docs/gallery/candlestick.html <- used as reference code for graph

#This is my first attempt at making a trading bot.
#Right now what it does is it trades the macd crossovers based on the provided time frame


####ACCESS ACCOUNT####
api_key = input("KEY:")
api_secret = input("SECRET:")

timeframe = "30m"

#Binance US
#https://www.reddit.com/r/BinanceExchange/comments/dahxcq/binance_us_api_python_wrapper/
client = client.Client(api_key, api_secret, tld="us")

#Open time
#Open
#High
#Low
#Close
#Volume
#Close time

#Quote asset volume
#Number of trades
#Taker buy base asset volume
#Taker Buy quote asset volume
#Ignore

def getHistorical():
    #earliestPossible = client._get_earliest_valid_timestamp("ETHUSDT", timeframe)
    historical = client.get_historical_klines("ETHUSDT", timeframe, "1 weeks ago UTC")
    return(historical)


#TODO: Implement a lmit system instead of using market orders, also add support to choose how much
#Currently uses 92% of the available balance to BUY order, (it will still sell off all available eth tho)
buy_percent = 0.92

def EXECUTE_SELL(volume):

    order = client.create_order(symbol="ETHUSDT", side="SELL", type="MARKET", quantity=volume)

def EXECUTE_BUY(volume):
    
    order = client.create_order(symbol="ETHUSDT", side="BUY", type="MARKET", quantity=volume)

def getBuyTradeVolume():
    #buy percentage*balance usdt WORTH of eth, buy orders have to be in eth tho so convert to eth price.
    balance = float(client.get_asset_balance(asset="USDT")["free"])
    price = float(client.get_symbol_ticker(symbol="ETHUSDT")["price"])
    volume = round((balance * buy_percent) / price, 5) #binance does not like lots of percision so round to 5 decimal places(lot size error)

    return(volume)

def getSellTradeVolume():
    #sell all eth.
    balance = float(client.get_asset_balance(asset="ETH")["free"])
    volume = round((balance), 5) #binance does not like lots of percision so round to 5 decimal places(lot size error)

    return(volume)

