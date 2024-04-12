from email import message
import time
import telebot
import os 
from dotenv import load_dotenv
from scraper import StockDataFetcher
import schedule
from workalendar.europe import Turkey
from datetime import date
import threading

def is_today_working_day():
    cal = Turkey()
    return cal.is_working_day(date.today())

load_dotenv()
fetcher = StockDataFetcher()
bot = telebot.TeleBot(os.getenv("API_KEY"))

def scheduled_job():
    if not is_today_working_day():
        bot.send_message(os.getenv("CHAT_ID"), "Bugün tatil, iyi tatiller :)")
        return
    current_date = time.strftime("%d/%m/%Y")
    stock_names = fetcher.fetch_data()
    Stock_Number = len(stock_names)
    first_message = f"{current_date}\n{Stock_Number} Hisse"
    bot.send_message(os.getenv("CHAT_ID"), first_message)
    message = ""
    for stock_name in stock_names:
        message += stock_name + "\n"    
    bot.send_message(os.getenv("CHAT_ID"), stock_name)
        
        
@bot.message_handler(commands=['help'])
def send_welcome(message):
    print(message.chat.id)
    bot.reply_to(message, "Merhaba, bu bot sana her akşam saat 8'de BİST'de goldencross'a başlayan hisseleri gösterir.")

schedule.every().day.at("16:00").do(scheduled_job)

def start_pooling():
    while True:
        bot.polling(non_stop=True)
        
def start_scheduling():
    while True:
        schedule.run_pending()
        time.sleep(1)
        
pooling_thread = threading.Thread(target=start_pooling)
pooling_thread.start()

scheduling_thread = threading.Thread(target=start_scheduling)
scheduling_thread.start()