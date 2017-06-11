import pandas as pd
from pymongo import MongoClient
from math import log
from time import time
import talib
import numpy as np
from talib.abstract import *

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
            "open": { "$first" :"$rate"},
            "high": { "$max": "$rate"},
            "low" : { "$min": "$rate"},
            "close": { "$last" :"$rate"},
            "volume": {"$sum": "$amount"},
            "total_price": {"$sum": {"$multiply": ["$rate", "$amount"]}}
        }},
        {"$sort": {"_id": 1}}
    ])
    trades = pd.DataFrame(list(result))
    return trades

trades = get_trade_df(symbol, 1497114000, 1497138824)
trades['SMA'] = SMA(trades, timeperiod=25)

print trades