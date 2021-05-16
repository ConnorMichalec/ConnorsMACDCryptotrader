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
#client.API_URL = 'https://testnet.binance.vision/api'

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