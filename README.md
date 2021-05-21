# ConnorsMACDCryptotrader
My first attempt at an auto trading software

Currently uses MACD like indicators and places trades based on 25EMA crossing 50EMA on the 30 minute timeframe.

In a volatile market it seems to be quite profitable(as tested so far) but I suspect in a sideways moving market it wont make much gains. However tweaking to code for a lower timeframe MIGHT work. 
Keep in mind it uses quite primitive strategies so it has many weaknesses, especially because it does not take trading volume into account.



to use this simply do python3 Main.py and enter ur binance api key and secret(google on how to setup that, make sure trading is enabled for it).

go in browser to localhost:5000 for the interface thingy(binance api is weird about connecting through another ip so change the code todo that). 
