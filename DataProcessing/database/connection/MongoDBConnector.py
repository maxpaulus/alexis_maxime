from pymongo import MongoClient

class MongoDBConnector:

      def __init__(self, host, port, username, password, db):
        str = "mongodb://"+username+":"+password+"@"+host+":"+port+"/"+db
        client = MongoClient(str)
        self.db = client[db]

