import pandas as pd
import yaml
import math
from math import pi
from tornado.ioloop import IOLoop
from talib.abstract import *
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from database.Requests import Requests
import json

symbol = 'BTC_ETH'
rq = Requests("poloniex")
agg_time = '5Min'
minTs = 1491032712
maxTs = minTs + 2592000
trades_agg = rq.getAggregatedTrades(symbol, minTs, maxTs, agg_time)
trades_agg.index = pd.to_datetime(trades_agg._id, unit='s')

ema_20_init = trades_agg['EMA_20'][0]
sma_50_init = trades_agg['SMA_50'][0]

if ema_20_init > sma_50_init:
    context = "bought"
else:
    context = "sold"

for  index, trade in trades_agg[1:].iterrows():
    if context == "bought" and trade['EMA_20'] < trade['SMA_50']:
        context = "sold"
        print "%s sell %f, profit: %f" %(index,trade['close'],trade['close']-buy_price)
    if context == "sold" and trade['EMA_20'] > trade['SMA_50']:
        context = "bought"
        buy_price = trade['close']
        print "%s buy %f" %(index,trade['close'])

def modify_doc(doc):
    trades_agg.index = pd.to_datetime(trades_agg._id, unit='s')
    source = ColumnDataSource(data=trades_agg)
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", x_axis_label="Date", tools=TOOLS, plot_width=1000, title="BTC_ETH Candlestick",
               y_axis_label='Price')
    p.line('_id', 'SMA_50', source=source)
    p.line('_id', 'EMA_20', source=source, line_color="red")
    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3
    inc = trades_agg.close > trades_agg.open
    dec = trades_agg.open > trades_agg.close
    w = 150
    p.segment(trades_agg.index, trades_agg.high, trades_agg.index, trades_agg.low, color="black")
    p.vbar(trades_agg.index[inc], w, trades_agg.open[inc], trades_agg.close[inc], fill_color="#D5E1DD",
           line_color="black")
    p.vbar(trades_agg.index[dec], w, trades_agg.open[dec], trades_agg.close[dec], fill_color="#F2583E",
           line_color="black")

    doc.add_root(column(p))

io_loop = IOLoop.current()
bokeh_app = Application(FunctionHandler(modify_doc))
server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    io_loop.add_callback(server.show, "/")
    io_loop.start()
#trades_agg['SMA_50'] = SMA(trades_agg, 50)
#trades_agg['EMA_20'] = EMA(trades_agg, 20)
#print trades_agg