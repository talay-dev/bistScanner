import yfinance as yf
from tinydb import TinyDB, Query


class StockPriceFetcher:
    @staticmethod
    def get_stock_price(name):
        ticker = yf.Ticker(name)
        last_close = ticker.history(period="1d", interval="1d").to_dict()["Close"]
        date, price = next((timestamp.strftime('%Y-%m-%d'), price) for timestamp, price in last_close.items())
        return date, price


class StockDataManager:
    def __init__(self, json_file="stock_data.json"):
        self.db = TinyDB(json_file)

    def add_new_stock(self, name):
        if not self.db.search(Query().name == name):
            date, price = StockPriceFetcher.get_stock_price(name)
            self.db.insert({"name": name, date: price})

    def update_stock_price(self, name):
        stock = Query()
        new_date, new_price = StockPriceFetcher.get_stock_price(name)
        self.db.update({"name": name, new_date: new_price}, stock.name == name)

    @property
    def get_stocks(self):
        return self.db.all()

    def remove_expired_stocks(self):
        for i in iter(self.db):
            if len(i.keys()) > 31:
                self.db.remove(doc_ids=[i.doc_id])

    def add_new_stocks(self, stocks):
        for stock in stocks:
            self.add_new_stock(stock)

    def update_stock_prices(self):
        for stock in self.db.all():
            self.update_stock_price(stock["name"])
