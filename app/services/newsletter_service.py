from celery import shared_task
from config import WEBHOOK_URL, GROUP_ID
from app.models import Order, OrderReview
from bot.models import Bot_user
from bot import Strings
from bot.bot import WebAppInfo
from asgiref.sync import async_to_sync
from payment.services import get_invoice_url
from bot.services.string_service import *
from app.utils.tg_bot import send_newsletter_api
from app.utils.data_classes import *


@shared_task
def send_order_info_to_group(order_id: int):
    order: Order = Order.objects.get(id=order_id)
    bot_user: Bot_user = order.bot_user

    order_items = list(
        order.items.values(
            'product__name', 'quantity', 'price'
        )
    )
    items_text = "\n".join([
        f"🔹 {item['product__name']} x {item['quantity']} - {item['price']} сум"
        for item in order_items
    ])

    text = (
        f"🆕 Новый заказ!\n\n"
        f"🆔 ID заказа: #{order.billz_id or order.id}\n"
        f"🏬 Магазин: {order.shop.name}\n"
        f"👤 Клиент: {order.customer.first_name}\n"
        f"📞 Телефон клиента: {order.customer.phone}\n"
        f"📍 Адрес клиента: {order.customer.address}\n"
        f"🛵 Тип доставки: {order.delivery_type.get_type_display()}\n"
        f"💵 Тип оплаты: {payment_methods.get(order.payment_method, 'Неизвестно')}\n\n"
        f"📦 Состав заказа:\n{items_text}\n\n"
        f"💬 Комментарии: {order.notes}\n\n"
        f"💵 Сумма заказа: {order.subtotal} сум\n"
        f"🚚 Доставка: {order.delivery_price} сум\n"
        f"💰 Общая сумма: {order.total} сум\n\n"
        f"📅 Дата заказа: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"👤 Информация о пользователе бота:\n"
        f"🔹 Имя: {bot_user.name}\n"
        f"🔹 Никнейм: {bot_user.firstname}\n"
        f"🔹 Username: @{bot_user.username}\n"
        f"🔹 Телефон: {bot_user.phone}\n"
        f"🔹 Язык: {'Русский' if bot_user.lang == 1 else 'Узбекский'}\n"
        f"🔹 Дата регистрации: {bot_user.date.strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    inline_buttons = []
    # send confirm order button if order status is need_confirmation
    if order.status == OrderStatus.NEED_CONFIRMATION:
        inline_buttons = [
            [{
                "text": "Подтвердить заказ",
                "callback_data": f"confirm_order-{order.id}"
            }]
        ]
    elif order.delivery_type.type == DeliveryTypeTitle.DuringDay:
        inline_buttons = [[{
            "text": "🚚 Доставлен",
            "callback_data": f"delivered-{order.id}"
        }]]

    send_newsletter_api(bot_user_id=GROUP_ID, text=text, inline_buttons=inline_buttons)
    location = {"latitude": order.latitude, "longitude": order.longitude}
    send_newsletter_api(bot_user_id=GROUP_ID, location=location)


@shared_task
def send_invoice_to_user(order_id):
    order: Order = Order.objects.get(id=order_id)
    bot_user: Bot_user = order.bot_user
    strings = Strings(user_id=bot_user.user_id)

    order_items = list(order.items.values(
            'product__name', 'quantity', 'price'
        ))
    items_text = "\n".join([
        strings.invoice_item.format(
            product=item['product__name'],
            quantity=item['quantity'],
            price=item['price']
        ) for item in order_items
    ])

    text = strings.invoice_message.format(
        order_id=order.id,
        customer_name=order.customer.first_name,
        subtotal=order.subtotal,
        delivery_price=order.delivery_price,
        total=order.total,
        items=items_text
    )

    inline_buttons = [
        [{
            "text": strings.pay,
            "url": async_to_sync(get_invoice_url)(order.pk, order.total, order.payment_method)
        }]
    ]

    send_newsletter_api(bot_user_id=bot_user.user_id, text=text, inline_buttons=inline_buttons)


@shared_task
def send_performer_info_to_client(yandex_trip: YandexTrip):
    order: Order = yandex_trip.order
    bot_user: Bot_user = order.bot_user
    text = performer_info_string(bot_user, yandex_trip)
    send_newsletter_api(
        bot_user_id=bot_user.user_id,
        text = text
    )


@shared_task
def notify_admin_about_performer_arrived(yandex_trip_id):
    yandex_trip: YandexTrip = YandexTrip.objects.get(pk=yandex_trip_id)
    order: Order = yandex_trip.order
    text = perfomer_arrived_pickup_string(yandex_trip)
    send_newsletter_api(
        bot_user_id=GROUP_ID,
        text = text
    )


@shared_task
def notify_client_delivery_arrived(yandex_trip_id):
    yandex_trip: YandexTrip = YandexTrip.objects.get(pk=yandex_trip_id)
    bot_user: Bot_user = yandex_trip.order.bot_user
    text = Strings.delivery_arrived[bot_user.lang]
    send_newsletter_api(
        bot_user_id=bot_user.user_id,
        text=text
    )




@shared_task
def notify_admin_order_delivered(yandex_trip_id):
    yandex_trip: YandexTrip = YandexTrip.objects.get(pk=yandex_trip_id)
    order: Order = yandex_trip.order
    text = Strings.order_delivered[0].format(
        order_id = order.id
    )
    send_newsletter_api(
        bot_user_id=GROUP_ID,
        text = text
    )


@shared_task
def send_gratitude_to_client(yandex_trip_id):
    yandex_trip: YandexTrip = YandexTrip.objects.get(pk=yandex_trip_id)
    bot_user: Bot_user = yandex_trip.order.bot_user
    text = Strings.gratitude_to_client[bot_user.lang]
    send_newsletter_api(
        bot_user_id=bot_user.user_id,
        text=text
    )


@shared_task
def send_gratitude_for_review_to_client(review_id):
    order_review: OrderReview = OrderReview.objects.get(pk=review_id)
    bot_user: Bot_user = order_review.order.bot_user
    text = Strings.gratitude_for_review[bot_user.lang]
    send_newsletter_api(
        bot_user_id=bot_user.user_id,
        text=text
    )


@shared_task
def notify_client_order_error(order_id):
    order: Order = Order.objects.get(pk=order_id)
    bot_user: Bot_user = order.bot_user
    text = Strings.order_error[bot_user.lang].format(order_id=order.id)
    send_newsletter_api(
        bot_user_id=bot_user.user_id,
        text=text
    )

@shared_task
def ask_review_from_user(order_id):
    order: Order = Order.objects.get(pk=order_id)
    bot_user: Bot_user = order.bot_user
    lang = bot_user.get_lang_display()
    text = Strings.ask_review[bot_user.lang]
    inline_buttons = [
        [{
            "text": Strings.leave_feedback[bot_user.lang],
            "web_app": {
                "url": f"{WEBHOOK_URL}/feedback/{order.id}/{lang}"
            }
        }]
    ]
    send_newsletter_api(
        bot_user_id=bot_user.user_id,
        text=text,
        inline_buttons=inline_buttons
    )