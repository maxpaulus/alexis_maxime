from connection.MongoDBConnector import MongoDBConnector
import pandas as pd

class Requests:

    path = "E:/Documents/Ether Project/db_logins.txt"

    def __init__(self,dbName):
        with open(self.path, 'r') as content_file:
            host = content_file.readline().strip()
            port = content_file.readline().strip()
            username = content_file.readline().strip()
            password = content_file.readline().strip()
        self.db = MongoDBConnector(host, port, username, password, dbName).db

    def getTrades(self, symbol, minTs, maxTs):
        '''
        Returns a DataFrame of trades aggregated by second for symbol in time range
        '''
        trades_db = self.db[symbol + '_trades']
        result = trades_db.aggregate([
            {"$match": {"timestamp": {'$gt': minTs, '$lt': maxTs}}},
            {"$sort": {"timestamp": 1}},
            {"$group": {
                "_id": "$timestamp",
                "open": {"$first": "$rate"},
                "high": {"$max": "$rate"},
                "low": {"$min": "$rate"},
                "close": {"$last": "$rate"},
                "volume": {"$sum": "$amount"},
                "total_price": {"$sum": {"$multiply": ["$rate", "$amount"]}}
            }},
            {"$sort": {"_id": 1}}
        ])
        trades = pd.DataFrame(list(result))
        return trades


    def getSortedDayTrades(self, symbol, year, month, day):
        trades_db = self.db[symbol + '_trades']
        appendedString = year + '-' + month + '-' + day
        result = trades_db.find({"date": {'$regex': appendedString}}).sort('tradeID', 1)
        trades = pd.DataFrame(list(result))
        return trades


    def getPricesFromTimeStamp(self, symbol, minTs, maxTs=-1):
        trades_db = self.db[symbol + '_trades']
        if maxTs != -1:
            result = trades_db.aggregate([
                {"$match": {"timestamp": {'$gt': minTs, '$lt': maxTs}}},
                {"$group": {
                    "_id": "$timestamp",
                    "total_price": {"$sum": {"$multiply": ["$rate", "$amount"]}},
                    "total_quantity": {"$sum": "$amount"},
                }},
                {"$project": {
                    "price": {"$divide": ["$total_price", "$total_quantity"]},
                    "amount": "$total_quantity"
                }},
                {"$sort": {"_id": 1}}
            ])
        else:
            result = trades_db.aggregate([
                {"$match": {"timestamp": {"$gt": minTs}}},
                {"$group": {
                    "_id": "$timestamp",
                    "total_price": {"$sum": {"$multiply": ["$rate", "$amount"]}},
                    "total_quantity": {"$sum": "$amount"},
                }},
                {"$project": {
                    "price": {"$divide": ["$total_price", "$total_quantity"]},
                    "amount": "$total_quantity"
                }},
                {"$sort": {"_id": 1}}
            ])
        trades = pd.DataFrame(list(result))
        return trades


