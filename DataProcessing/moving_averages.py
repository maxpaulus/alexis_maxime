import pandas as pd
from pymongo import MongoClient
from math import log
from time import time

client = MongoClient("mongodb://moinolol:bitcoin3000@darkbird.no-ip.info:27017/poloniex")
db = client.poloniex
symbol = 'BTC_ETH'

def get_trades_indexes(trades, offset, live=False):
    '''
    Returns indexes of trades in offset range for each data point in DataFrame
    of book data
    '''
    def indexes(ts):
        ts = int(ts)
        i_0 = trades.timestamp.searchsorted([ts-offset], side='left')[0]
        if live:
            i_n = -1
        else:
            i_n = trades.timestamp.searchsorted([ts-1], side='right')[0]
        return (i_0, i_n)
    return trades.index.map(indexes)

def get_trade_df(symbol, min_ts, max_ts, convert_timestamps=False):
    '''
    Returns a DataFrame of trades for symbol in time range
    '''
    trades_db = db[symbol+'_trades']
    query = {'timestamp': {'$gt': min_ts, '$lt': max_ts}}
    cursor = trades_db.find(query).sort('_id', 1)
    trades = pd.DataFrame(list(cursor))
    if not trades.empty:
        trades = trades.set_index('_id')
        if convert_timestamps:
            trades.index = pd.to_datetime(trades.date, format='%Y-%m-%d %H:%M:%S')
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

trades = get_trade_df(symbol, 1497114000, 1497138824,False)
trades['indexes'] = get_trades_indexes(trades, 60*60*24*50)
#min_ts = trades.index.min() - (60*60*24*50)
#max_ts = trades.index.max()

start = time()
stage = time()
#print trades
print trades.columns.values
print get_trades_average(trades)