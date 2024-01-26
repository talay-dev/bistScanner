import logging
import requests
import json


class StockDataFetcher:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
        self.params = json.load(open("params.json"))
        self.url = "https://scanner.tradingview.com/global/scan"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Referer": "https://www.tradingview.com/screener/",
        }

    def fetch_data(self):
        response = requests.post(self.url, headers=self.headers, json=self.params)
        if response.status_code == 200:
            info_dict = json.loads(response.text)
            stock_data = info_dict["data"]
            stock_names = [stock['s'] for stock in stock_data]
        else:
            logging.error("Request failed, status code %d", response.status_code)
        return stock_names

