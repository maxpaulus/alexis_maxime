import urllib2
import time
import json
from pymongo import MongoClient
import sys

api = 'https://poloniex.com/public'
symbol = 'BTC_ETH' #sys.argv[1]

limit = 1000   #https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_ETH&depth=10
book_url = '{0}?command=returnOrderBook&currencyPair={1}&depth={2}'\
    .format(api, symbol, limit)

client = MongoClient()
db = client['poloniex']
ltc_books = db[symbol+'_books']


def format_book_entry(entry):
    '''
    Converts book data to float
    '''
    #if all(key in entry for key in ('asks', 'bids')):
     #   entry['amount'] = float(entry['amount'])
      #  entry['price'] = float(entry['price'])
       # entry['timestamp'] = float(entry['timestamp'])
    return entry


def get_json(url):
    '''
    Gets json from the API
    '''
    resp = urllib2.urlopen(url)
    return json.load(resp, object_hook=format_book_entry), resp.getcode()


print 'Running...'
while True:
    start = time.time()
    try:
        book, code = get_json(book_url)
    except Exception as e:
        print e
        sys.exc_clear()
    else:
        if code != 200:
            print code
        else:
            book['_id'] = time.time()
            ltc_books.insert_one(book)
            time_delta = time.time()-start
            if time_delta < 1:
                time.sleep(1-time_delta)
