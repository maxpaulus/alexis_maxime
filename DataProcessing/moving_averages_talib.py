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

symbol = 'BTC_ETH'

def moving_average(trades,timeperiod):
    trades_agg = pd.DataFrame()
    trades_agg['_id'] = trades['_id'].groupby(pd.TimeGrouper('5Min')).min()
    trades_agg['close'] = trades['close'].groupby(pd.TimeGrouper('5Min')).agg(lambda x: x.iloc[-1])
    trades_agg['high'] = trades['high'].groupby(pd.TimeGrouper('5Min')).max()
    trades_agg['low'] = trades['low'].groupby(pd.TimeGrouper('5Min')).min()
    trades_agg['open'] = trades['open'].groupby(pd.TimeGrouper('5Min')).agg(lambda x: x.iloc[0])
    trades_agg['volume'] = trades['volume'].groupby(pd.TimeGrouper('5Min')).sum()
    trades_agg['date'] = pd.to_datetime(trades_agg._id, unit='s')
    trades_agg = trades_agg.set_index('_id')
    trades_agg['SMA'] = SMA(trades_agg, timeperiod=timeperiod)

    return trades_agg

def modify_doc(doc):
    rq = Requests("poloniex")
    trades = rq.getTrades(symbol, 1497114000, 1497138824)
    trades.index = pd.to_datetime(trades._id, unit='s')

    trades_agg = moving_average(trades,20)
    #trades['date'] = pd.to_datetime(trades.index, format='%Y-%m-%d %H:%M:%S')

    source = ColumnDataSource(data=trades_agg)
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", x_axis_label="Date", tools=TOOLS, plot_width=1000, title = "MSFT Candlestick", y_axis_label='Price')
    p.line('_id', 'SMA', source=source)

    p.xaxis.major_label_orientation = pi / 4
    p.grid.grid_line_alpha = 0.3

    inc = trades_agg.close > trades_agg.open
    dec = trades_agg.open > trades_agg.close
    w = 150

    p.segment(trades_agg.index, trades_agg.high, trades_agg.index, trades_agg.low, color="black")
    p.vbar(trades_agg.index[inc], w, trades_agg.open[inc], trades_agg.close[inc], fill_color="#D5E1DD", line_color="black")
    p.vbar(trades_agg.index[dec], w, trades_agg.open[dec], trades_agg.close[dec], fill_color="#F2583E", line_color="black")


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


io_loop = IOLoop.current()

bokeh_app = Application(FunctionHandler(modify_doc))

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    io_loop.add_callback(server.show, "/")
    io_loop.start()