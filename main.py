from loader import bot
from random import choice
from api_requests import *
from telebot import types
from message_templates import send_history_message


@bot.message_handler(commands=['start', 'hello-world', 'lowprice', 'highprice', 'bestdeal', 'history', 'help'])
def get_message(message):
    if message.text == '/start':
        text = 'Вас приветствует Hotel Search Assistant!🏢\n' \
               'Я помогу найти вам отель в любой точке мира 😉\n' \
               'Введите /help чтобы узнать о функциях.'
        image = 'https://static.vecteezy.com/system/resources/previews/003/216/630/non_2x/find-hotel-or-search-hotels-concept-with-smartphone-maps-gps-free-vector.jpg'
        bot.send_photo(message.chat.id, image, caption=text)
    elif message.text == "/hello-world":
        bot.send_message(message.chat.id,
                         choice(["Привет👋", "Приветствую!", "Здравствуйте!"]) + '\n' + 'Введите /help чтобы узнать о функциях.')
    elif message.text == "/lowprice" or message.text == "/highprice":
        city_getter(message, message.text[1:])
    elif message.text == '/help':
        text = '⚙Список комманд:\n' \
               '/lowprice - Вывод отелей по возрастанию в цене\n' \
               '/highprice - Вывод отелей по убыванию в цене\n' \
               '/bestdeal - вывод отелей, наиболее подходящих по цене и расположению от центра.\n' \
               '/history - вывод истории поиска отелей.'
        bot.send_message(message.chat.id, text)
    elif message.text == '/history':
        show_history(message)


@bot.message_handler(content_types=['text'])
def greeting_after_text(message):
    if message.text.lower() == "привет":
        bot.send_message(message.chat.id,
                         choice(["Привет👋", "Приветствую", "Здравствуйте!"]) + '\n' + 'Введите /help чтобы узнать о функциях.')
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю 🙁')


def city_getter(message: types.Message, filter_type: str):
    check_in = (dt.datetime.now() + dt.timedelta(1)).date()
    check_out = (dt.datetime.now() + dt.timedelta(2)).date()
    msg = bot.send_message(message.chat.id, "🔎Введите город")
    bot.register_next_step_handler(msg, hotels_count_getter, filter_type, check_in, check_out)


def hotels_count_getter(message: types.Message, filter_type: str, check_in: datetime.date, check_out: datetime.date):
    city = message.text
    city_founded, destination = get_destination(city)
    if not city_founded:
        bot.send_message(message.chat.id, "Город не найден. 🙁")
        return
    msg = bot.send_message(message.chat.id, 'Сколько отелей показать? (до 10)')
    bot.register_next_step_handler(msg, is_photos_need, filter_type, check_in, check_out, destination, city)


def is_photos_need(message, filter_type: str, check_in: datetime.date, check_out: datetime.date, destination, city: str):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Неверный формат ввода 🙁')
        return
    hotels_count = int(message.text)
    if hotels_count not in range(1, 11):
        bot.send_message(message.chat.id, 'Неверное количество отелей 🙁')
        return

    msg = bot.send_message(message.chat.id, 'Показать фотографии? (да/нет)')
    bot.register_next_step_handler(msg, photos_count_getter, filter_type, check_in, check_out, destination, city, hotels_count)


def photos_count_getter(message: types.Message, filter_type: str, check_in: datetime.date, check_out: datetime.date,
                        destination: str, city: str, hotels_count: int):
    if message.text.lower() in ("да", "yes", "д", "y"):
        msg = bot.send_message(message.chat.id, 'Сколько фотографий? (до 3)')
        bot.register_next_step_handler(msg,
                                       check_photos_count,
                                       filter_type,
                                       check_in,
                                       check_out,
                                       destination,
                                       city,
                                       hotels_count,
                                       message.text)
    elif message.text.lower() in ("нет", "no", "н", "n"):
        get_low_or_high_price(message,
                              filter_type,
                              check_in,
                              check_out,
                              destination,
                              city,
                              hotels_count,
                              message.text)
    else:
        bot.send_message(message.chat.id, 'Я вас не понимаю 😕')


def check_photos_count(message: types.Message, filter_type: str, check_in: datetime.date, check_out: datetime.date,
                       destination: str, city: str, hotels_count: int, answer: str):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, 'Неверный формат ввода 🙁')
        return
    photos_count = int(message.text)
    if photos_count not in range(1, 4):
        bot.send_message(message.chat.id, 'Неверное количество фотографий 🙁')
        return
    get_low_or_high_price(message,
                          filter_type,
                          check_in,
                          check_out,
                          destination,
                          city,
                          hotels_count,
                          answer,
                          photos_count=photos_count)


def show_history(message: types.Message):
    history = []
    with sqlite3.connect("history.sqlite") as connection:
        cur = connection.cursor()
        for i in cur.execute("""SELECT * FROM all_history
                                WHERE userId = ?""", (message.chat.id,)).fetchall():
            history.append(i)
            if len(history) == 5:
                break
    for i in history:
        send_history_message(message, i[1], i[2], i[3:])


if __name__ == "__main__":
    bot.infinity_polling()
