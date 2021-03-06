from talib.abstract import *
from database.Requests import Requests

symbol = 'BTC_ETH'
rq = Requests("poloniex")
agg_time = '5Min'
minTs = 1483228831
maxTs = minTs + 2592000

while minTs < 1500562202:
    trades_agg = rq.getAggregatedTrades(symbol, minTs, maxTs, agg_time)
    trades_agg['SMA_50'] = SMA(trades_agg, 50)
    trades_agg['EMA_20'] = EMA(trades_agg, 20)
    bbands = BBANDS(trades_agg, 50, 2, 2)
    trades_agg['UPPER_BOLLINGER_BAND'] = bbands['upperband']
    trades_agg['LOWER_BOLLINGER_BAND'] = bbands['lowerband']
    trades_agg = trades_agg.dropna(axis = 0, how = 'any')
    print trades_agg
    rq.setAggregatedTrades(symbol, agg_time, trades_agg)
    minTs = minTs + 2592000 - 30000
    maxTs = minTs + 2592000
