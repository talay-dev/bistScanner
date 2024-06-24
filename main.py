import os
import threading
import time
import textwrap
from datetime import datetime

import pytz
import schedule
import telebot
from dotenv import load_dotenv

from StockDataFetcher import StockDataFetcher
from StockDataManager import StockDataManager


class BotHandler:
    def __init__(self):
        load_dotenv()
        self.fetcher = StockDataFetcher()
        self.data_manager = StockDataManager()
        self.bot = telebot.TeleBot(os.getenv("API_KEY"))
        self.schedule_time = os.getenv("SCHEDULED_TIME")
        self.timezone = os.getenv("SCHEDULED_TIMEZONE_UTC")

    def scheduled_job(self):
        current_date = time.strftime("%d/%m/%Y")
        stock_names = self.fetcher.fetch_data
        self.data_manager.add_new_stocks(stock_names)
        self.data_manager.remove_expired_stocks()
        self.data_manager.update_stock_prices()

        stock_names = [stock.replace('.IS', '-BIST') if stock.endswith('.IS') else stock for stock in stock_names]

        first_message: str = f"=================\n{current_date}\n{len(stock_names)} Hisse\n=================\n"
        first_message += "\n".join(stock_names)
        self.bot.send_message(os.getenv("CHAT_ID"), parse_mode="Markdown", text=first_message)

    def start_pooling(self):
        while True:
            self.bot.polling(non_stop=True)

    def schedule_hour(self):
        """
        This function calculates the scheduled time in UTC timezone of server.
        :return: Scheduled time in UTC timezone as HH:MM
        """
        time_sign = "-" if self.timezone[0] == "+" else "-"
        timezone = pytz.timezone(f"Etc/GMT{time_sign}{int(self.timezone[1:3])}")
        now = datetime.now()
        difference = (now.astimezone().utcoffset() - timezone.utcoffset(now))
        return (now.replace(hour=int(self.schedule_time[0:2]),
                            minute=int(self.schedule_time[3:5]),
                            second=0) + difference).strftime("%H:%M")

    def start_scheduling(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def run(self):
        @self.bot.message_handler(commands=['help'])
        def send_welcome(message):
            self.bot.send_message(message.chat.id, textwrap.dedent("""
                              Merhaba, bu bot sana her gün Türk ve Amerikan borsalarında goldencross'a başlayan hisseleri gösterir.
                              Mevcut komutlar:
                              /test - Test mesajı gönderir
                              /help - Yardım mesajı gönderir
                              /performans - Son 30 günde listelenen hisselerin performansını listeler
                              """))

        @self.bot.message_handler(commands=['test'])
        def test_functionality(message):
            self.scheduled_job()
            self.bot.send_message(message.chat.id, "Test başarılı. Hisseleri gönderdim.")

        @self.bot.message_handler(commands=['performans'])
        def past_performance(message):
            stocks = self.data_manager.get_stocks
            return_message = "Son 30 günde listelenen hisselerin performansı:\n"
            for stock in stocks:
                stock_name = stock["name"]
                if stock_name.endswith('.IS'):
                    stock_name = stock_name.replace('.IS', '-BIST')
                stock_data = list(stock.values())[1:]
                stock_performance = round((stock_data[-1] - stock_data[0]) / stock_data[0] * 100, 2)
                return_message += f"{stock_name}: %{stock_performance} ({(len(stock_data) - 1)} gün)\n"
            self.bot.send_message(message.chat.id, return_message)

        schedule.every().day.at(self.schedule_hour()).do(self.scheduled_job)

        pooling_thread = threading.Thread(target=self.start_pooling)
        pooling_thread.start()

        scheduling_thread = threading.Thread(target=self.start_scheduling)
        scheduling_thread.start()


if __name__ == "__main__":
    bot_handler = BotHandler()
    bot_handler.run()
