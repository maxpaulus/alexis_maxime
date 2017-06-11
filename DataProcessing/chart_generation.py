from pymongo import MongoClient
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go
import talib
import numpy as np
from math import *
from database.Requests import Requests
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
    result = pd.DataFrame(columns=('Open','Close','High','Low'))
    for x in res:
        periodicDf = pd.DataFrame(x)['price']
        tuple = [periodicDf.iloc[0], periodicDf.iloc[-1], periodicDf.values.max(), periodicDf.values.min()]
        result.loc[len(result)] = tuple
    return result

df = getPeriods(300)

trace = go.Candlestick(x=df.index,
                       open=df.Open,
                       high=df.High,
                       low=df.Low,
                       close=df.Close)
data = [trace]
py.iplot(data, filename='simple_candlestick')


#trades = getPricesFromTimeStamp()
#print trades
#df = pd.DataFrame(list(trades))
#print getCandleSticks(df, 300)[0]


#print df
#df.plot(x='_id', y='price')
#plt.show()
