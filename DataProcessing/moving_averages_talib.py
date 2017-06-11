import pandas as pd
from pymongo import MongoClient
from math import log
from time import time
import talib
import numpy as np
from talib.abstract import *
from database.Requests import Requests

client = MongoClient("mongodb://moinolol:bitcoin3000@darkbird.no-ip.info:27017/poloniex")
db = client.poloniex
symbol = 'BTC_ETH'

rq = Requests("poloniex")

trades = rq.getTrades(symbol, 1497114000, 1497138824)
trades['SMA'] = SMA(trades, timeperiod=25)

print trades