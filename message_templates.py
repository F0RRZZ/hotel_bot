from api_requests import *
from loader import bot
from telebot import types
from telebot.types import InputMediaPhoto


def send_message_without_hotel_photos(message: types.Message, name: str, address: str, distance_from_destination: float,
                                      price: str, score: float):
    message_text = f'🛎 Название отеля: {name}\n' \
                   f'📍 Адрес: {address}\n' \
                   f'↔ Расстояние от центра: {distance_from_destination} милей\n' \
                   f'💵 Цена: {price}\n' \
                   f'⭐ Оценка: {score}'
    bot.send_message(message.chat.id, message_text)


def send_message_with_hotel_photos(message, name: str, address: str, distance_from_destination: float, price: str,
                                   score: float, photos_links: list):
    message_text = f'🛎 Название отеля: {name}\n' \
                   f'📍 Адрес: {address}\n' \
                   f'↔ Расстояние от центра: {distance_from_destination} милей\n' \
                   f'💵 Цена: {price}\n' \
                   f'⭐ Оценка: {score}'
    medias = []
    for index, link in enumerate(photos_links):
        if index == 0:
            medias.append(InputMediaPhoto(link, caption=message_text))
        else:
            medias.append(InputMediaPhoto(link))
    bot.send_media_group(message.chat.id, medias)


def send_no_result_message(message: types.Message):
    bot.send_message(message.chat.id, "Не нашлось отелей по вашему запросу 😕")


def send_history_message(message: types.Message, command: str, time: str, hotels: tuple):
    text = f'Команда: {command}\n' \
           f'Время: {time[:-7]}\n' \
           f'Отели: '
    for hotel in hotels:
        if hotel is not None:
            text += hotel + ', '
        else:
            text = text[:-2] + '.'
    bot.send_message(message.chat.id, text)

