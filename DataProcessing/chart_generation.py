from pymongo import MongoClient
import pandas as pd
import numpy as np
from math import *
from database.Requests import Requests


from tornado.ioloop import IOLoop
from talib.abstract import *
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme


#plt.interactive(False)

rq = Requests("poloniex")
symbol = 'BTC_ETH'

#periods = pd.DataFrame(getPeriods(1497138824,1496968000))
#print periods

#def getCandle()
trades = rq.getPricesFromTimeStamp(symbol, 1497114000)
#print trades

def getPeriods(timePeriod):
    numberOfPeriods = ceil(trades.size/timePeriod)
    res = np.array_split(trades, numberOfPeriods)
    result = pd.DataFrame(columns=('_id', 'open', 'close', 'high', 'low', 'volume'))
    for x in res:
        periodicDf = pd.DataFrame(x)['price']
        amount = pd.DataFrame(x)['amount'].sum()
        tuple = [len(result), periodicDf.iloc[0], periodicDf.iloc[-1], periodicDf.values.max(), periodicDf.values.min(), amount]
        result.loc[len(result)] = tuple
    return result

trades_agg = getPeriods(300)
print trades_agg





#trades = getPricesFromTimeStamp()
#print trades
#df = pd.DataFrame(list(trades))
#print getCandleSticks(df, 300)[0]


#print df
#df.plot(x='_id', y='price')
#plt.show()
