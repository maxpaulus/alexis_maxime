from pymongo import MongoClient
import pandas as pd
import re

client = MongoClient("mongodb://moinolol:bitcoin3000@darkbird.no-ip.info:27017/poloniex")

def getSortedDayTrades(year,month,day):
    appendedString = year+'-'+month+'-'+day
    return db.BTC_ETH_trades.find({"date": {'$regex': appendedString}}).sort('tradeID', 1)


db = client.poloniex

trades = getSortedDayTrades('2017', '06', '09')

counter = 0

df = pd.DataFrame(list(trades))

dfBuys = df[df['type']== "buy"]
print dfBuys['amount'].mean()

dfSells = df[df['type']== "sell"]
print dfSells['amount'].mean()

#df2 = df.groupby(['date'])['amount'].mean()
volume24h = df['amount'].sum()
print volume24h