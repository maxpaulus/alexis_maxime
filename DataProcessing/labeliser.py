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

def aggregate_trades(trades, agg_time):
    trades_agg = pd.DataFrame()
    trades_agg['_id'] = trades['_id'].groupby(pd.TimeGrouper(agg_time)).min()
    trades_agg['close'] = trades['close'].groupby(pd.TimeGrouper(agg_time)).agg(lambda x: x.iloc[-1])
    trades_agg['high'] = trades['high'].groupby(pd.TimeGrouper(agg_time)).max()
    trades_agg['low'] = trades['low'].groupby(pd.TimeGrouper(agg_time)).min()
    trades_agg['open'] = trades['open'].groupby(pd.TimeGrouper(agg_time)).agg(lambda x: x.iloc[0])
    trades_agg['volume'] = trades['volume'].groupby(pd.TimeGrouper(agg_time)).sum()
    trades_agg['date'] = pd.to_datetime(trades_agg._id, unit='s')
    trades_agg = trades_agg.set_index('_id')
    return trades_agg


rq = Requests("poloniex")
trades = rq.getTrades(symbol, 1497114000, 1497138824)
trades.index = pd.to_datetime(trades._id, unit='s')

trades_agg = aggregate_trades(trades, '30Min')

bottom = 100000000
top = 0

for x in trades_agg:
    if trades_agg['low'] < bottom &&