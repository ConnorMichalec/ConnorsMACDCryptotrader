from bokeh.plotting import figure,show
from bokeh.models import Scale, WheelZoomTool, Button, ColumnDataSource
import numpy as np

import Main

class App():
    def __init__(self):

        self.historical_adjusted = Main.get_historical_adjusted(Main.get_historical_np())
        self.historical_organized = Main.get_historical_organized(self.historical_adjusted)
        self.longEMA_split = Main.Data.split(Main.get_longEMA(self.historical_adjusted))
        self.shortEMA_split = Main.Data.split(Main.get_shortEMA(self.historical_adjusted))

        margin = 0.05
        yHigh = np.amax(self.historical_organized["close"]) + margin*np.amax(self.historical_organized["close"])
        yLow =  np.amin(self.historical_organized["close"]) - margin*np.amin(self.historical_organized["close"])

        self.plot = figure(title="MACD AUTOTRADER - 30M timeframe", plot_height=700, plot_width=1500, x_axis_label="TIME", y_axis_label="ETH PRICE", tools="pan,reset,save", y_range=(yLow, yHigh))
        
        zoomTool = WheelZoomTool()

        self.plot.add_tools(zoomTool)
        self.plot.toolbar.active_scroll = zoomTool
        self.plot.toolbar.logo = None

        self.draw()

    def getGreen(self, historical_adjusted):
        greenData = []

        for i in range(len(historical_adjusted)):
            if(i!=0):
                if(historical_adjusted[i][4] > historical_adjusted[i-1][4]):
                    #if close is higher than previous close add it to green data array
                    greenData.append(historical_adjusted[i])
            
        return(np.array(greenData))


    def getRed(self, historical_adjusted):
        redData = []

        for i in range(len(historical_adjusted)):
            if(i!=0):
                if(historical_adjusted[i][4] < historical_adjusted[i-1][4]):
                    #if close is lower than previous close add it to red data array
                    redData.append(historical_adjusted[i])
            
        return(np.array(redData))



    def draw(self):

        longEMA_split_dic = {
            "time" : self.longEMA_split[0],
            "value" : self.longEMA_split[1]
        }
        shortEMA_split_dic = {
            "time" : self.shortEMA_split[0],
            "value" : self.shortEMA_split[1]
        }

        self.wickSource = ColumnDataSource(data=self.historical_organized)

        self.greenCandleSource = ColumnDataSource(data=Main.get_historical_organized(self.getGreen(self.historical_adjusted)))
        self.redCandleSource = ColumnDataSource(data=Main.get_historical_organized(self.getRed(self.historical_adjusted)))

        self.longEMASource = ColumnDataSource(data=longEMA_split_dic)
        self.shortEMASource = ColumnDataSource(data=shortEMA_split_dic)


        self.plot.segment(x0="openTime", y0="high", x1="openTime", y1="low", color="black", source=self.wickSource)
        self.plot.vbar(x="openTime", width=0.7, top="open", bottom="close", fill_color="#00ff00", line_width=0, source=self.greenCandleSource)
        self.plot.vbar(x="openTime", width=0.7, top="open", bottom="close", fill_color="#ff0000", line_width=0, source=self.redCandleSource)
        self.plot.line(x="time", y="value", legend_label="EMA LONG(50)", line_width=2, line_color="blue", source=self.longEMASource)
        self.plot.line("time", y="value", legend_label="EMA SHORT(25)", line_width=2, line_color="green", source=self.shortEMASource)

    def updateGraphics(self):
        self.wickSource.data = self.historical_organized

        longEMA_split_dic = {
            "time" : self.longEMA_split[0],
            "value" : self.longEMA_split[1]
        }
        shortEMA_split_dic = {
            "time" : self.shortEMA_split[0],
            "value" : self.shortEMA_split[1]
        }

        self.longEMASource.data = longEMA_split_dic
        self.shortEMASource.data = shortEMA_split_dic

        self.greenCandleSource.data = Main.get_historical_organized(self.getGreen(self.historical_adjusted))
        self.redCandleSource.data = Main.get_historical_organized(self.getRed(self.historical_adjusted))
        

    def update(self):
        self.historical_adjusted = Main.get_historical_adjusted(Main.get_historical_np())
        self.historical_organized = Main.get_historical_organized(self.historical_adjusted)
        self.longEMA_split = Main.Data.split(Main.get_longEMA(self.historical_adjusted))
        self.shortEMA_split = Main.Data.split(Main.get_shortEMA(self.historical_adjusted))

        self.updateGraphics()

    def refresh(self):
        pass



    def make_document(self, doc):
        doc.title = "Connor's MACD autotrader"
        doc.add_periodic_callback(self.update, 5000)
        doc.add_root(self.plot)
