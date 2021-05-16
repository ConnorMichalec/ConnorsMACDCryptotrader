import binance.client as client
import numpy as np
import pandas as pd

import time

import threading

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

class Data():
    @staticmethod
    def split(historicalData):
        #just transpose array; https://stackoverflow.com/questions/30820962/splitting-columns-of-a-numpy-array-easily
        transposed = historicalData.transpose() #flip over it's diagnoal

        transposed = transposed.astype(float)
        return(transposed)

    @staticmethod
    def adjust(historicalData):
        historicalData = np.delete(historicalData, slice(5,12), 1)  #delete unnecessary data, slice() is basically bigger version of [start:stop:step]

        #change time units:
        for i in range(len(historicalData)):
            historicalData[i][0] = i

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
    historical_split = Data.split(historical_adjusted)
    historical_organized = {
        "openTime" : historical_split[0],
        "open" : historical_split[1],
        "high" : historical_split[2],
        "low" : historical_split[3],
        "close" : historical_split[4]
    }

    return(historical_organized)

if __name__ == "__main__":
    app = Visual.App()

    container = {"/":Application(FunctionHandler(app.make_document))}

    server = Server(container, port=5000)

    server.run_until_shutdown()