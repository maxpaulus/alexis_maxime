import pandas as pd
from database.Requests import Requests

symbol = 'BTC_ETH'

def aggregate_trades(trades, agg_time):
    trades_agg = pd.DataFrame()
    trades_agg['_id'] = trades['_id'].groupby(pd.TimeGrouper(agg_time)).min()
    trades_agg['close'] = trades['close'].groupby(pd.TimeGrouper(agg_time)).nth(-1)
    trades_agg['high'] = trades['high'].groupby(pd.TimeGrouper(agg_time)).max()
    trades_agg['low'] = trades['low'].groupby(pd.TimeGrouper(agg_time)).min()
    trades_agg['open'] = trades['open'].groupby(pd.TimeGrouper(agg_time)).nth(0)
    trades_agg['volume'] = trades['volume'].groupby(pd.TimeGrouper(agg_time)).sum()
    return trades_agg


rq = Requests("poloniex")
start_ts = 1491004800
agg_time = '5Min'

while start_ts < 1497136768:
    print start_ts
    trades = rq.getTrades(symbol, start_ts, start_ts + 86400)
    trades.index = pd.to_datetime(trades._id, unit='s')
    trades_agg = aggregate_trades(trades, agg_time)

    rq.setAggregatedTrades(symbol, agg_time, trades_agg)
    start_ts = start_ts + 86400