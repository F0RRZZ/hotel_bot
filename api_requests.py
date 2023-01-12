import datetime
import os

import requests
import sqlite3
import datetime as dt

from message_templates import send_message_without_hotel_photos, send_no_result_message, send_message_with_hotel_photos
from telebot import types


KEY = os.environ["KEY"]


def get_destination(city: str):
    headers = {
        "X-RapidAPI-Key": KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    url = "https://hotels4.p.rapidapi.com/locations/v3/search"
    querystring = {"q": city,
                   "locale": "en_US",
                   "langid": "1033",
                   "siteid": "300000001"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    response_to_dict = response.json()
    try:
        destination = response_to_dict["sr"][0]
        if 'cityId' in destination:
            destination = destination['cityId']
        elif 'gaiaId' in destination:
            destination = destination['gaiaId']
        print(destination)
        return True, destination
    except IndexError:
        return False, None


def get_low_or_high_price(message: types.Message, filter_type: str, check_in: datetime.date, check_out: datetime.date,
                          destination: str, city: str, hotels_count: int, answer: str, photos_count=0):
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    url = "https://hotels4.p.rapidapi.com/properties/v2/list"
    sort = "PRICE_LOW_TO_HIGH" if filter_type == "lowprice" else "PRICE_HIGH_TO_LOW"
    print(filter_type, check_in, check_out, destination, city, hotels_count, answer, sep="|")
    querystring = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {
            "regionId": destination
        },
        "checkInDate": {
            "day": check_in.day,
            "month": check_in.month,
            "year": check_in.year
        },
        "checkOutDate": {
            "day": check_out.day,
            "month": check_out.month,
            "year": check_out.year
        },
        "rooms": [
            {
                "adults": 2,
                "children": []
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": hotels_count,
        "sort": sort
    }
    response = requests.request("POST", url, headers=headers, json=querystring)
    res_to_dict = response.json()
    try:
        properties_list = res_to_dict['data']['propertySearch']['properties']
        with sqlite3.connect('history.sqlite') as connection:
            cur = connection.cursor()
            names_of_hotels = []
            for index, hotel in enumerate(properties_list):
                if index == hotels_count:
                    break
                if answer in ("нет", "no", "н", "n"):
                    send_message_without_hotel_photos(message,
                                                      hotel['name'],
                                                      hotel['neighborhood']['name'] if hotel[
                                                                                           'neighborhood'] is not None else city,
                                                      hotel['destinationInfo']['distanceFromDestination']['value'],
                                                      hotel['price']['lead']['formatted'],
                                                      hotel['reviews']['score'])
                    names_of_hotels.append(hotel['name'])
                else:
                    links = get_hotel_photos(hotel["id"], photos_count)
                    send_message_with_hotel_photos(message,
                                                   hotel['name'],
                                                   hotel['neighborhood']['name'] if hotel[
                                                                                        'neighborhood'] is not None else city.capitalize(),
                                                   hotel['destinationInfo']['distanceFromDestination']['value'],
                                                   hotel['price']['lead']['formatted'],
                                                   hotel['reviews']['score'],
                                                   links)
                    names_of_hotels.append(hotel['name'])
            names_of_hotels.extend([None] * (10 - len(names_of_hotels)))
            cur.execute("""INSERT INTO all_history(userId, command, time, hotel1, hotel2, hotel3, hotel4, hotel5, hotel6, hotel7, hotel8, hotel9, hotel10)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (message.chat.id, f'/{filter_type}', str(dt.datetime.now()), *names_of_hotels))
    except TypeError:
        send_no_result_message(message)


def get_hotel_photos(hotel_id: str, photos_count: int):
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": KEY,
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": hotel_id
    }
    response = requests.request("POST", url, json=payload, headers=headers)
    response_to_dict = response.json()
    links = []
    for index, image in enumerate(response_to_dict["data"]["propertyInfo"]["propertyGallery"]["images"]):
        if index == photos_count:
            break
        links.append(image["image"]["url"])
    return links
