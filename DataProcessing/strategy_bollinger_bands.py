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
minTs = 1493251200
maxTs = 1503157317 #minTs + 20592000
trades_agg = rq.getAggregatedTrades(symbol, minTs, maxTs, agg_time)
trades_agg.index = pd.to_datetime(trades_agg._id, unit='s')
position_btc = 1 #BTC
position_eth = 0
fees = 0.0025

first_price =  trades_agg['close'][0]
number_of_trades = 0
fees_paid = 0
cross_over = 0
good_trades = 0
stop_loss_count = 0
#todo: create function to test risk_reward & base_stop_loss adjustments
risk_reward = 6
base_stop_loss = 0.03
context = "sold"

for  index, trade in trades_agg[1:].iterrows():
    #Basic strategy
    if context == "bought":
        if trade['EMA_20'] > trade['SMA_50']:
            cross_over = 1
        if trade['EMA_20'] < trade['SMA_50'] and cross_over == 1 and (trade['close']-buy_price)/trade['close'] > base_stop_loss*risk_reward: #only sell if profits greater than 5%
            context = "sold"
            position_btc = position_eth * (1-fees) * trade['close']
            fees_paid = fees_paid + position_eth * fees * trade['close']
            position_eth = 0
            cross_over = 0
            if trade['close']-buy_price > 0:
                good_trades = good_trades + 1
            print "%s sell %f, profit: %f" %(index,trade['close'],trade['close']-buy_price)
        if (trade['close'] - buy_price) / trade['close'] < -0.02: #stop loss
            context = "sold"
            position_btc = position_eth * (1 - fees) * trade['close']
            fees_paid = fees_paid + position_eth * fees * trade['close']
            position_eth = 0
            stop_loss_count = stop_loss_count +1
            if trade['close']-buy_price > 0:
                good_trades = good_trades + 1
            print "stop loss!"
            print "%s sell %f, profit: %f" % (index, trade['close'], trade['close'] - buy_price)
    if context == "sold":
        if trade['close'] < trade['LOWER_BOLLINGER_BAND']:
            context = "bought"
            position_eth = position_btc * (1-fees)/ trade['close']
            fees_paid = fees_paid + position_btc * fees
            position_btc = 0
            buy_price = trade['close']
            number_of_trades = number_of_trades+1
            print "%s buy %f" %(index,trade['close'])

    last_price = trade['close']

print ""
print "%s total fees paid: %f BTC" %(index,fees_paid)
print "%s number of trades: %d" %(index,number_of_trades)
print "%s accuracy: %f" %(index,good_trades / number_of_trades)
print "%s stop loss count: %d" %(index,stop_loss_count)
print "%s good_trades: %f" %(index,good_trades)
print "%s final balance %f BTC, %f BTC in ETH" %(index,position_btc,position_eth*last_price)
print "%s market comparison: %f BTC" %(index,1*(1-fees) / first_price * (1-fees) * last_price)

def modify_doc(doc):
    trades_agg.index = pd.to_datetime(trades_agg._id, unit='s')
    source = ColumnDataSource(data=trades_agg)
    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", x_axis_label="Date", tools=TOOLS, plot_width=1000, title="BTC_ETH Candlestick",
               y_axis_label='Price')
    p.line('_id', 'SMA_50', source=source)
    p.line('_id', 'EMA_20', source=source, line_color="red")
    p.line('_id', 'LOWER_BOLLINGER_BAND', source=source, line_color="yellow")
    p.line('_id', 'UPPER_BOLLINGER_BAND', source=source, line_color="purple")
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