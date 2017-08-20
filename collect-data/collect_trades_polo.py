import urllib2
import time
import datetime
import json
from pymongo import MongoClient
import sys

api = 'https://poloniex.com/public'
symbol = 'BTC_ETH' #sys.argv[1]

client = MongoClient("mongodb://darkbird:Morovach1@darkbird.no-ip.info:27017/poloniex")
db = client['poloniex']
ltc_trades = db[symbol+'_trades']


def format_trade(trade):
    '''
    Formats trade data
    '''
    if all(key in trade for key in ('globalTradeID', 'amount', 'rate', 'date')):
        trade['_id'] = trade.pop('globalTradeID')
        trade['amount'] = float(trade['amount'])
        trade['rate'] = float(trade['rate'])
        trade['timestamp'] = float(time.mktime(datetime.datetime.strptime(trade['date'], "%Y-%m-%d %H:%M:%S").timetuple()))

    return trade


def get_json(url):
    '''
    Gets json from the API
    '''
    print 'get json...'
    resp = urllib2.urlopen(url, timeout=10)
    print 'Resp: %s' % resp
    print 'RespCode: %s' % resp.getcode()
    return json.load(resp, object_hook=format_trade), resp.getcode()


print 'Running...'
start_timestamp = 1501709220 #1497402383
end_timestamp = start_timestamp+10000
while True:
    start = time.time()
    print 'Time: %d' %start
    url = '{0}?command=returnTradeHistory&currencyPair={1}&start={2}&end={3}' \
        .format(api, symbol, start_timestamp, end_timestamp)
    try:
        trades, code = get_json(url)
        print 'Code: %s' %code
    except Exception as e:
        print e
        sys.exc_clear()
    else:
        if code != 200:
            print code
        else:
            print 'debut else'
            for trade in trades:
                ltc_trades.update_one({'_id': trade['_id']},
                                      {'$setOnInsert': trade}, upsert=True)
            start_timestamp = trades[0]['timestamp'] - 5
            end_timestamp = start_timestamp + 10000
            print 'new_start_timestamp %d' %start_timestamp
            print 'new_end_timestamp %d' %end_timestamp
            time_delta = time.time() - start
            if time_delta < 0.25:  # 1.0:
                time.sleep(0.25 - time_delta)  # 1