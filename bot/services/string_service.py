from bot.bot import *
from bot.models import Bot_user
from app.models import YandexTrip, Order


def performer_info_string(bot_user: Bot_user, yandex_trip: YandexTrip):
    lang = bot_user.lang
    text = (
        f"{Strings.performer_found_for_your_order[lang]}\n"
        f"{Strings.driver_info[lang]}".format(
            courier_name=yandex_trip.courier_name,
            car_color=yandex_trip.car_color,
            car_model=yandex_trip.car_model,
            car_number=yandex_trip.car_number
        )
    )
    return text


def perfomer_arrived_pickup_string(yandex_trip: YandexTrip):
    lang = 1
    text = (
        f"{Strings.performer_arrived_pickup[lang]}\n"
        f"{Strings.driver_info[lang]}"
    ).format(
        courier_name=yandex_trip.courier_name,
        car_color=yandex_trip.car_color,
        car_model=yandex_trip.car_model,
        car_number=yandex_trip.car_number,
        order_id=yandex_trip.order.id
    )
    return text
