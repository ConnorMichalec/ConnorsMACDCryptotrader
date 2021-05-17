import binance.client as client
import numpy as np
import pandas as pd

import time

import threading

import json

import Visual, Binance

from bokeh.plotting import figure,show
from bokeh.models import Scale, WheelZoomTool
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers.function import FunctionHandler



#http://matthewrocklin.com/blog/work/2017/06/28/simple-bokeh-server

class PriceCalculations():
    @staticmethod
    def calculateLongEMA(data):
        span = 50
        #convert np to panda dataframe
        df = pd.DataFrame(data, columns = ["openTime", "open", "high", "low", "close"])
        df["ewm"] = df["close"].ewm(span=span,min_periods=0,adjust=False,ignore_na=False).mean()
        df = df.drop(["open", "high", "low", "close"], axis=1)
        data = df.to_numpy()

        return(data)

    @staticmethod
    def calculateShortEMA(data):
        span = 25
        #convert np to panda dataframe
        df = pd.DataFrame(data, columns = ["openTime", "open", "high", "low", "close"])
        df["ewm"] = df["close"].ewm(span=span,min_periods=0,adjust=False,ignore_na=False).mean()
        df = df.drop(["open", "high", "low", "close"], axis=1)
        data = df.to_numpy()

        return(data)

    @staticmethod
    def identifyHistoricalMACross(data, longEMA, shortEMA):
        #identify MA crossings in the past(this includes any crossings that were not traded)

        crossings = []

        for candleIndex in range(len(data)):
            if(candleIndex!=0):
                #check if the short EMA is above/equal to the long ema in the current candle
                if(shortEMA[candleIndex][1] >= longEMA[candleIndex][1]):
                    #check if the previous candle also BELOW the long ema, if so the current candle is a crossing point
                    if(shortEMA[candleIndex-1][1] < longEMA[candleIndex-1][1]):
                        crossings.append([data[candleIndex][0], shortEMA[candleIndex][1], "LONG"]) #time, price, position

                #Do the opposite for bearish indicators:
                elif(shortEMA[candleIndex][1] <= longEMA[candleIndex][1]):
                    if(shortEMA[candleIndex-1][1] > longEMA[candleIndex-1][1]):
                        crossings.append([data[candleIndex][0], shortEMA[candleIndex][1], "SHORT"]) #time, price, position

        return(crossings)



                


    #@staticmethod
    #def identifyCrossIndicator(price_1, price_2,

class Data():
    @staticmethod
    def split(historicalData):
        #just transpose array; https://stackoverflow.com/questions/30820962/splitting-columns-of-a-numpy-array-easily
        transposed = historicalData.transpose() #flip over it's diagnoal
        return(transposed)

    @staticmethod
    def convertFloat(data):
        return(data.astype(float))


    @staticmethod
    def adjust(historicalData):
        historicalData = np.delete(historicalData, slice(5,12), 1)  #delete unnecessary data, slice() is basically bigger version of [start:stop:step]

        return(historicalData)


def get_longEMA(historical_adjusted):
    longEMA = PriceCalculations.calculateLongEMA(historical_adjusted)
    return(longEMA)

def get_shortEMA(historical_adjusted):
    shortEMA = PriceCalculations.calculateShortEMA(historical_adjusted)
    return(shortEMA)

def get_historical_np():
    return(np.array(Binance.getHistorical()))

def get_historical_adjusted(historical_np):
    return(Data.adjust(historical_np))

def get_historical_organized(historical_adjusted):
    historical_split = Data.convertFloat(Data.split(historical_adjusted))
    historical_organized = {
        "openTime" : historical_split[0],
        "open" : historical_split[1],
        "high" : historical_split[2],
        "low" : historical_split[3],
        "close" : historical_split[4]
    }

    return(historical_organized)

def organizeHistoricalMACross(historical_macross):

    historical_macross_organized = Data.split(np.array(historical_macross)) #transpose
    historical_macross_organized = {
        "openTime" : historical_macross_organized[0],
        "price" : historical_macross_organized[1],
        "position" : historical_macross_organized[2]
    }

    colors = []

    #add color data for graph:
    for dictionaryIndex in range(len(historical_macross_organized["position"])):
        if(historical_macross_organized["position"][dictionaryIndex] == "LONG"):
            colors.append("#00ff00")
        else:
            colors.append("#ff0000")

    historical_macross_organized["color"] = colors

    return(historical_macross_organized)

def organizeEMA(longOrShortEMA):
    EMA_transposed = Data.convertFloat(Data.split(longOrShortEMA))
    EMA_organized = {
            "time" : EMA_transposed[0],
            "value" : EMA_transposed[1]
    }
    return(EMA_organized)

def fetchPosition(history):
    #get latest position
    position = history[len(history)-1]["position"]

    return(position)

def fetchHistory():
    #get history of all trades

    file = open("tradeData.json")
    fileData = file.read()
    jsonData = json.loads(fileData)
    history = jsonData["trade_history"]

    return(history)

def fetchHistory_adjusted(history):
    openTime_l = []
    price_l = []
    amount_l = []
    position_l = []
    color_l = []

    for dic in history:
        openTime_l.append(dic["openTime"])
        price_l.append(dic["price"])
        amount_l.append(dic["amount"])
        position_l.append(dic["position"])
        if(dic["position"]=="SHORT"):
            color_l.append("red")
        else:
            color_l.append("green")


    #condense history into one dictionary with arrays for each value
    history_adjusted = {
        "openTime" : openTime_l,
        "price" : price_l,
        "amount" : amount_l,
        "position" : position_l,
        "color" : color_l
    }
    
    return(history_adjusted)

#THIS WILL EXECUTE TRADES, BE CAREFUL
def APPLY_POSITION():
    pass

if __name__ == "__main__":
    app = Visual.App()

    container = {"/":Application(FunctionHandler(app.make_document))}

    server = Server(container, port=5000)

    server.run_until_shutdown()