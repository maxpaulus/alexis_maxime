import pandas as pd
import yaml
from math import pi
from tornado.ioloop import IOLoop
from pymongo import MongoClient
from talib.abstract import *
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from database.Requests import Requests

symbol = 'BTC_ETH'

def modify_doc(doc):
    rq = Requests("poloniex")
    trades = rq.getTrades(symbol, 1497114000, 1497138824)
    trades['SMA'] = SMA(trades, timeperiod=500)
    print trades

    trades.index.name = '_id'
    source = ColumnDataSource(data=trades)
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title = "MSFT Candlestick", y_axis_label='Price')
    p.line('_id', 'SMA', source=source)

    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3

    inc = trades.close > trades.open
    dec = trades.open > trades.close
    w = 1

    p.segment(trades.index, trades.high, trades.index, trades.low, color="black")
    p.vbar(trades.index[inc], w, trades.open[inc], trades.close[inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(trades.index[dec], w, trades.open[dec], trades.close[dec], fill_color="#F2583E", line_color="black")


    doc.add_root(column(p))

    doc.theme = Theme(json=yaml.load("""
        attrs:
            Figure:
                background_fill_color: "#DDDDDD"
                outline_line_color: white
                toolbar_location: above
                height: 500
                width: 800
            Grid:
                grid_line_dash: [6, 4]
                grid_line_color: white
    """))

db = client.poloniex
io_loop = IOLoop.current()

bokeh_app = Application(FunctionHandler(modify_doc))

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    io_loop.add_callback(server.show, "/")
    io_loop.start()