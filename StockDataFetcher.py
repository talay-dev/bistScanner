import requests
import json
import logging


class StockDataFetcher:
    def __init__(self, config_file="params.json", log_file="logs.log"):
        # Configure logging
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            handlers=[logging.FileHandler(filename=log_file)])
        self.logger = logging.getLogger(self.__class__.__name__)

        # Load parameters from the configuration file
        try:
            with open(config_file, 'r') as file:
                self.params = json.load(file)
        except FileNotFoundError:
            self.logger.error(f"Configuration file {config_file} not found.")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"Error decoding JSON from the configuration file {config_file}.")
            raise

        # Define API URL and headers
        self.url = "https://scanner.tradingview.com/global/scan"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/58.0.3029.110 Safari/537.36",
            "Referer": "https://www.tradingview.com/screener/",
        }

    @property
    def fetch_data(self):
        """Fetch stock data from the TradingView API."""
        try:
            response = requests.post(self.url, headers=self.headers, json=self.params)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch stock data: {e}")
            return []

        # Process the response data
        self.logger.info("Stock data successfully fetched")
        try:
            stock_data = response.json()["data"]
            stock_data = [stock['s'] for stock in stock_data]
            stock_data = [x for x in stock_data if x.startswith(('NYSE', 'BIST', 'NASDAQ'))]
            return [
                (symbol.split(':')[1] + '.IS') if symbol.startswith('BIST') else symbol.split(':')[1]
                for symbol in stock_data]


        except (KeyError, json.JSONDecodeError) as e:
            self.logger.error(f"Error processing stock data: {e}")
            return []
