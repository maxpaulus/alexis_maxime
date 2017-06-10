from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
plt.interactive(False)

client = MongoClient("mongodb://moinolol:bitcoin3000@darkbird.no-ip.info:27017/poloniex")
db = client.poloniex

def getSortedDayTrades(year,month,day):
    appendedString = year+'-'+month+'-'+day
    return db.BTC_ETH_trades.find({"date": {'$regex': appendedString}}).sort('tradeID', 1)

def getPricesFromTimeStamp():
    result = db.BTC_ETH_trades.aggregate([
     { "$match": { "timestamp": { "$gt": 1496963467} } },
     { "$group": {
      "_id": "$timestamp",
      "total_price": { "$sum": { "$multiply": [ "$rate", "$amount" ] } },
      "total_quantity": { "$sum": "$amount" },
     }},
    { "$project": {
      "price": { "$divide": [ "$total_price", "$total_quantity" ] },
      "amount": "$total_quantity"
     } },
     { "$sort": {"_id": 1} }
    ])
    return result

#trades = getSortedDayTrades('2017', '06', '09')
trades = getPricesFromTimeStamp()
print trades
df = pd.DataFrame(list(trades))
print df
df.plot(x='_id', y='price')
plt.show()
