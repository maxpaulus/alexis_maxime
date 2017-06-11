import pandas as pd
from pymongo import MongoClient
from math import log
from time import time
import talib
import numpy as np

client = MongoClient("mongodb://moinolol:bitcoin3000@darkbird.no-ip.info:27017/poloniex")
db = client.poloniex
symbol = 'BTC_ETH'

def get_trade_df(symbol, min_ts, max_ts):
    '''
    Returns a DataFrame of trades for symbol in time range
    '''
    trades_db = db[symbol + '_trades']
    result = trades_db.aggregate([
        {"$match": {"timestamp": {'$gt': min_ts, '$lt': max_ts}}},
        {"$sort": {"timestamp":1}},
        {"$group": {
            "_id": "$timestamp",
            "total_price": {"$sum": {"$multiply": ["$rate", "$amount"]}},
            "volume": {"$sum": "$amount"},
            "high": { "$max": "$rate"},
            "low" : { "$min": "$rate"},
            "open": { "$first" :"$rate"},
            "close": { "$last" :"$rate"}
        }},
        {"$project": {
            "open": "$open",
            "high": "$high",
            "low" : "$low",
            "close": "$close",
            "volume": "$volume"
        }},
        {"$sort": {"_id": 1}}
    ])
    trades = pd.DataFrame(list(result))
    return trades

def get_trades_average(trades):
    '''
    Returns the percent change of a volume-weighted average of trades for each
    data point in DataFrame of book data
    '''

    def mean_trades(x):
        trades_n = trades.iloc[x.indexes[0]:x.indexes[1]]
        if not trades_n.empty:
            return (trades_n.rate*trades_n.amount).sum()/trades_n.amount.sum()
    return trades.apply(mean_trades, axis=1)

trades = get_trade_df(symbol, 1497114000, 1497138824)
#min_ts = trades.index.min() - (60*60*24*50)
#max_ts = trades.index.max()

start = time()
stage = time()
#print trades.values
print talib.SMA(trades['close'])
#print get_trades_average(trades)

#TESTS
inputs = {
    'open': np.random.random(100),
    'high': np.random.random(100),
    'low': np.random.random(100),
    'close': np.random.random(100),
    'volume': np.random.random(100)
}

print talib.SMA(inputs['close'])