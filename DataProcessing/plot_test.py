import pandas as pd
from tornado.ioloop import IOLoop
import yaml

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.server.server import Server
from bokeh.themes import Theme
from pymongo import MongoClient
import pandas as pd
import re

client = MongoClient("mongodb://moinolol:bitcoin3000@darkbird.no-ip.info:27017/poloniex")

def getSortedDayTrades(year,month,day):
    appendedString = year+'-'+month+'-'+day
    return db.BTC_ETH_trades.find({"date": {'$regex': appendedString}}).sort('tradeID', 1)

def getGroupedTradesBySecond():
    return db.BTC_ETH_trades.aggregate([
        {"$match": {"timestamp": {"$gt": 1497014000}}},
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

def modify_doc(doc):
    trades = getGroupedTradesBySecond()
    df = pd.DataFrame(list(trades))

    df.index.name = '_id'

    source = ColumnDataSource(data=df)
    print source

    plot = figure(x_axis_type='datetime', y_range=(0.1, 0.13), y_axis_label='Price',
                  title="BTC ETH trades")
    plot.line('_id', 'price', source=source)

    def callback(attr, old, new):
        if new == 0:
            data = df
        else:
            data = df.rolling('{0}D'.format(new)).mean()
        source.data = ColumnDataSource(data=data).data

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change('value', callback)

    doc.add_root(column(slider, plot))

    doc.theme = Theme(json=yaml.load("""
        attrs:
            Figure:
                background_fill_color: "#DDDDDD"
                outline_line_color: white
                toolbar_location: above
                height: 500
                width: 800
            Grid:
                grid_line_dash: [6, 4]
                grid_line_color: white
    """))


db = client.poloniex


io_loop = IOLoop.current()


bokeh_app = Application(FunctionHandler(modify_doc))

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')

    io_loop.add_callback(server.show, "/")
    io_loop.start()