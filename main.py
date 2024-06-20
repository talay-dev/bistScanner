import time
import telebot
import os 
from dotenv import load_dotenv
from scraper import StockDataFetcher
import schedule
import threading

load_dotenv()
fetcher = StockDataFetcher()
bot = telebot.TeleBot(os.getenv("API_KEY"))

def scheduled_job():
    current_date = time.strftime("%d/%m/%Y")
    stock_names = fetcher.fetch_data()
    stock_names = [x for x in stock_names if x[:4] == 'NYSE' or x[:4] == 'BIST' or x[:6] == 'NASDAQ']
    first_message = f"=================\n{current_date}\n{len(stock_names)} Hisse\n=================\n"
    first_message += "\n".join(stock_names) 
    bot.send_message(os.getenv("CHAT_ID"), parse_mode="Markdown", text=first_message )
        
@bot.message_handler(commands=['help'])
def send_welcome(message):
    print(message.chat.id)
    bot.reply_to(message, "Merhaba, bu bot sana her akşam saat 8'de BİST'de goldencross'a başlayan hisseleri gösterir.")    
        
@bot.message_handler(commands=['test'])
def test_functionality(message):
    scheduled_job()
    bot.reply_to(message, "Test başarılı. Hisseleri gönderdim.")

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