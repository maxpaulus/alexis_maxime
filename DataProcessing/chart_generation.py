from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import talib
import numpy as np
from math import *
from database.Requests import Requests
plt.interactive(False)

rq = Requests("poloniex")
symbol = 'BTC_ETH'

#periods = pd.DataFrame(getPeriods(1497138824,1496968000))
#print periods

#def getCandle()
trades = rq.getSortedDayTrades(symbol, '2017', '06', '09')
print trades
#trades = getPricesFromTimeStamp()
#print trades
#df = pd.DataFrame(list(trades))
#print getCandleSticks(df, 300)[0]


#print df
#df.plot(x='_id', y='price')
#plt.show()
