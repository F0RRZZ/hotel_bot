import telebot


token = os.environ["TOKEN"]
bot = telebot.TeleBot(token, parse_mode=None)
