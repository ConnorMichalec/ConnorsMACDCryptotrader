from bokeh.plotting import figure,show
from bokeh.models import Scale, WheelZoomTool, Button, ColumnDataSource, Div, Column, Row, Span
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.core.properties import Dict

from datetime import timedelta

import numpy as np

import Main

class App():
    def __init__(self):
        self.initializeData()

        margin_y = 0.05
        margin_x = 0
        yHigh = np.amax(self.historical_organized["close"]) + margin_y*np.amax(self.historical_organized["close"])
        yLow =  np.amin(self.historical_organized["close"]) - margin_y*np.amin(self.historical_organized["close"])

        xHigh = np.amax(self.historical_organized["openTime"]) + margin_x*np.amax(self.historical_organized["openTime"])
        xLow =  np.amin(self.historical_organized["openTime"]) - margin_x*np.amin(self.historical_organized["openTime"])


        self.plot = figure(title="MACD AUTOTRADER - 30M timeframe", plot_height=900, plot_width=1400, x_axis_label="TIME", y_axis_label="PRICE", tools="pan,reset,save", y_range=(yLow, yHigh), x_range=(xLow, xHigh))
        
        zoomTool = WheelZoomTool()

        self.plot.add_tools(zoomTool)
        self.plot.toolbar.active_scroll = zoomTool
        self.plot.toolbar.logo = None
        


        self.initializeGraphics()

    def getGreenCandles(self, historical_adjusted):
        greenData = []

        for i in range(len(historical_adjusted)):
            if(i!=0):
                if(historical_adjusted[i][4] > historical_adjusted[i-1][4]):
                    #if close is higher than previous close add it to green data array
                    greenData.append(historical_adjusted[i])
            
        return(np.array(greenData))


    def getRedCandles(self, historical_adjusted):
        redData = []

        for i in range(len(historical_adjusted)):
            if(i!=0):
                if(historical_adjusted[i][4] < historical_adjusted[i-1][4]):
                    #if close is lower than previous close add it to red data array
                    redData.append(historical_adjusted[i])
            
        return(np.array(redData))

    def getLastTradeDivHTML(self):
        #check if there is a trade history:
        if(len(self.tradeHistory)!=0):
            lastTrade = self.tradeHistory[len(self.tradeHistory)-1]
            html = """
            <table style='width:100%; border: 1px solid black; font-size: 15px; padding: 10px'; border-collapse: collapse;>
                <caption>LAST TRADE</caption>
                <tr>
                    <th>Open time</th>
                    <th>Position</th>
                    <th>Price</th>
                    <th>Amount</th>
                </tr>
                <tr>
                    <td style='border: 1px solid black; font-size: 15px;'>"""+lastTrade["openTime"]+"""
                    <td style='border: 1px solid black; font-size: 15px;'>"""+lastTrade["position"]+"""
                    <td style='border: 1px solid black; font-size: 15px;'>"""+lastTrade["price"]+"""
                    <td style='border: 1px solid black; font-size: 15px;'>"""+lastTrade["amount"]+"""
                </tr>
            </table>"""
        
        else:
            html = """
            <p style='color: yellow;'>No trade history</p>
            """

        return(html)





    def initializeGraphics(self):
        #https://stackoverflow.com/questions/52463431/how-to-change-display-format-of-time-in-seconds-to-date-in-x-axis-in-bokeh-chart
        self.plot.xaxis.formatter = DatetimeTickFormatter(days="%d-%b-%Y", hours="%H:%M", seconds="%S")

        #figures:

        self.plot.segment(x0="openTime", y0="high", x1="openTime", y1="low", color="black", source=self.historicalSource)

        #Ensure each bar is 30 minutes in width(converted from milliseconds timecode) using timedelta
        self.plot.vbar(x="openTime", width=timedelta(minutes=30), top="open", bottom="close", fill_color="#ffffff", line_color="#00ff00", line_width=1, source=self.greenCandleSource)
        self.plot.vbar(x="openTime", width=timedelta(minutes=30), top="open", bottom="close", fill_color="#ffffff", line_color="#ff0000", line_width=1, source=self.redCandleSource)

        #deciding candle special infinite line overlay thing:
        self.tradeSpan = Span(location=self.historical_organized["openTime"][len(self.historical_organized["close"])-2], line_width=1, dimension="height", line_color="#000000", line_alpha=0.5)
        self.plot.add_layout(self.tradeSpan)

        #EMA lines
        self.plot.line(x="time", y="value", legend_label="EMA LONG(150)", line_width=2, line_color="blue", source=self.longEMASource)
        self.plot.line("time", y="value", legend_label="EMA SHORT(100)", line_width=2, line_color="green", source=self.shortEMASource)


        #display historical trades:
        self.plot.text(x="openTime", y="price", x_offset=-25, y_offset=40, color="color", text="position", text_font_size="20px", source=self.historicalTradeSource)
        self.plot.text(x="openTime", y="price", x_offset=-25, y_offset=50, color="#000000", text="price", text_font_size="10px", source=self.historicalTradeSource)
        self.plot.text(x="openTime", y="price", x_offset=-25, y_offset=60, color="#000000", text="amount", text_font_size="10px", source=self.historicalTradeSource)
        self.plot.text(x="openTime", y="price", x_offset=-25, y_offset=70, color="#000000", text="openTime", text_font_size="10px", source=self.historicalTradeSource)
        self.plot.circle(x="openTime", y="price", color="color", size=6, angle=0.785, source=self.historicalTradeSource)
        self.plot.line(x="openTime", y="price",  legend_label="TRADE HISTORY", line_width=2, line_color="black", source=self.historicalTradeSource)


        #display all historical MA crossings:
        self.plot.plus(x="openTime", y="price", color="color", size=15, alpha=0.6, angle=0.785, source=self.historicalMACrossSource)





        #glyphs:


        self.priceDIV = Div(text=("ETH: "+str(self.historical_organized["close"][len(self.historical_adjusted)-1])+"USDT"), style=
        {
            "font-size" : "20px", 
            "color" : "#505050",
            "font-size" : "40px"
        })

        self.positionDIV = Div(text=("POSITION: "+str(self.position)))

        if(self.position == "LONG"):
            self.positionDIV.style = {
                "color" : "#00FF00",
                "font-size" : "20px", 
                "font-size" : "25px",
                "border" : "1px solid black"
            }
        elif(self.position == "SHORT"):
            self.positionDIV.style = {
                "color" : "#FF0000",
                "font-size" : "20px", 
                "font-size" : "25px",
                "border" : "1px solid black"
            }
        else:
            self.positionDIV.style = {
                "color" : "#FFFF00",
                "font-size" : "20px", 
                "font-size" : "25px",
                "border" : "1px solid black"
            }

        self.lastTradeDIV = Div(text=(self.getLastTradeDivHTML()))



    def updateExternalData(self):
        #display stuff outside the plot
        self.priceDIV.text = "ETH: "+str(self.historical_organized["close"][len(self.historical_adjusted)-1])+"USDT"
        self.positionDIV.text = "POSITION: "+str(self.position)
        
        if(self.position == "LONG"):
            self.positionDIV.style = {
                "color" : "#00FF00",
                "font-size" : "20px", 
                "font-size" : "25px",
                "border" : "1px solid black"
            }
        elif(self.position == "SHORT"):
            self.positionDIV.style = {
                "color" : "#FF0000",
                "font-size" : "20px", 
                "font-size" : "25px",
                "border" : "1px solid black"
            }
        else:
            self.positionDIV.style = {
                "color" : "#FFFF00",
                "font-size" : "20px", 
                "font-size" : "25px",
                "border" : "1px solid black"
            }

        self.lastTradeDIV.text = self.getLastTradeDivHTML()
        

    def initializeData(self):
        #initial data:
        self.updateData()


        #sources:

        self.historicalSource = ColumnDataSource(data=self.historical_organized)
        self.greenCandleSource = ColumnDataSource(data=Main.get_historical_organized(self.getGreenCandles(self.historical_adjusted)))
        self.redCandleSource = ColumnDataSource(data=Main.get_historical_organized(self.getRedCandles(self.historical_adjusted)))
        self.longEMASource = ColumnDataSource(data=self.longEMA_organized)
        self.shortEMASource = ColumnDataSource(data=self.shortEMA_organized)
        self.historicalTradeSource = ColumnDataSource(data=self.tradeHistory_organized)
        self.historicalMACrossSource = ColumnDataSource(data=self.historicalMACross_organized)


    def updateSourceData(self):
        #updates the graphics to the latest data fetched
        self.historicalSource.data = self.historical_organized
        self.longEMASource.data = self.longEMA_organized
        self.shortEMASource.data = self.shortEMA_organized
        self.greenCandleSource.data = Main.get_historical_organized(self.getGreenCandles(self.historical_adjusted))
        self.redCandleSource.data = Main.get_historical_organized(self.getRedCandles(self.historical_adjusted))
        self.tradeSpan.location = self.historical_organized["openTime"][len(self.historical_organized["close"])-2]
        self.historicalTradeSource.data = self.tradeHistory_organized
        self.historicalMACrossSource.data = self.historicalMACross_organized

        

    def update(self):
        self.updateData()
        self.updateSourceData()
        self.updateExternalData()
        Main.update(self.historical_adjusted, self.longEMA, self.shortEMA, self.tradeHistory_organized)


    def updateData(self):
        #updates all the data
        self.historical_adjusted = Main.get_historical_adjusted(Main.get_historical_np())
        self.historical_organized = Main.get_historical_organized(self.historical_adjusted)
        self.longEMA = Main.get_longEMA(self.historical_adjusted)
        self.shortEMA = Main.get_shortEMA(self.historical_adjusted)
        self.longEMA_organized = Main.organizeEMA(self.longEMA)
        self.shortEMA_organized = Main.organizeEMA(self.shortEMA)
        self.tradeHistory = Main.fetchHistory()
        self.tradeHistory_organized = Main.fetchHistory_organized(self.tradeHistory)
        self.position = Main.fetchPosition(self.tradeHistory)
        self.historicalMACross = Main.PriceCalculations.identifyHistoricalMACross(self.historical_adjusted, self.longEMA, self.shortEMA)
        self.historicalMACross_organized = Main.organizeHistoricalMACross(self.historicalMACross) 
        



    def make_document(self, doc):
        doc.title = "Connor's MACD autotrader"
        doc.add_periodic_callback(self.update, 5000)

        #https://stackoverflow.com/questions/56137866/how-to-display-plot-in-bokeh-div

        #stuff on the side of graph
        external = Column()
        external.children.append(self.priceDIV)
        external.children.append(self.positionDIV)
        external.children.append(self.lastTradeDIV)

        layout = Row()
        layout.children.append(self.plot)
        layout.children.append(external)
        doc.add_root(layout)
