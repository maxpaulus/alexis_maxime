import urllib2
import time
import datetime
import json
from pymongo import MongoClient
import sys

api = 'https://poloniex.com/public'
symbol = 'BTC_ETH' #sys.argv[1]

client = MongoClient()
client.poloniex.authenticate('darkbird', 'Morovach1')
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
    resp = urllib2.urlopen(url)
    return json.load(resp, object_hook=format_trade), resp.getcode()


print 'Running...'
start_timestamp = 1483228800
end_timestamp = start_timestamp+10000
while True:
    start = time.time()
    url = '{0}?command=returnTradeHistory&currencyPair'