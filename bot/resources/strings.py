

class Strings:
    def __init__(self, user_id) -> None:
        self.user_id = user_id

    def __getattribute__(self, key: str):
        if result := object.__getattribute__(self, key):
            if isinstance(result, list):
                from bot.services.redis_service import get_user_lang
                user_id = object.__getattribute__(self, "user_id")
                user_lang_code = get_user_lang(user_id)
                return result[user_lang_code]
            else:
                return result
        else:
            return key

    hello = """🤖 Xush kelibsiz!\n Bot tilini tanlang  🌎 \n\n ➖➖➖➖➖➖➖➖➖➖➖➖\n
    👋 Добро пожаловать \n \U0001F1FA\U0001F1FF Выберите язык бота \U0001F1F7\U0001F1FA"""
    added_group = "Чат успешно добавлена ✅"
    uz_ru = ["UZ 🇺🇿", "RU 🇷🇺"]
    main_menu = ["Asosiy menyu 🏠", "Главное меню 🏠"]
    change_lang = [
        "\U0001F1FA\U0001F1FF Tilni o'zgartirish \U0001F1F7\U0001F1FA",
        "\U0001F1FA\U0001F1FF Сменить язык \U0001F1F7\U0001F1FA",
    ]
    select_lang = [""" Tilni tanlang """, """Выберите язык бота """]
    type_name = ["""Ismingizni kiriting """, """Введите ваше имя """]
    send_number = [
        """Telefon raqamingizni yuboring """,
        """Оставьте свой номер телефона """,
    ]
    leave_number = ["Telefon raqamni yuborish", "Оставить номер телефона"]
    back = ["""🔙 Ortga""", """🔙 Назад"""]
    next_step = ["""Davom etish ➡️""", """Далее ➡️"""]
    seller = ["""Sotuvchi 🛍""", """Продавцам 🛍"""]
    buyer = ["""Xaridor 💵""", """Покупателям 💵"""]
    settings = ["""Sozlamalar ⚙️""", """Настройки ⚙️"""]
    language_change = ["""Tilni o\'zgartirish 🇺🇿🇷🇺""", """Смена языка 🇺🇿🇷🇺"""]
    change_phone_number = [
        """Telefon raqamni o\'zgartirish 📞""",
        """Смена номера телефона 📞""",
    ]
    change_name = ["""Ismni o\'zgartirish 👤""", """Смени имени 👤"""]
    settings_desc = ["""Sozlamalar ⚙️""", """Настройки ⚙️"""]
    your_phone_number = [
        """📌 Sizning telefon raqamingiz: [] 📌""",
        """📌 Ваш номер телефона: [] 📌""",
    ]
    send_new_phone_number = [
        """Yangi telefon raqamingizni yuboring!\n<i>Jarayonni bekor qilish uchun "🔙 Ortga" tugmasini bosing.</i>""",
        """Отправьте свой новый номер телефона!\n<i>Нажмите кнопку "🔙 Назад", чтобы отменить процесс.</i>""",
    ]
    number_is_logged = [
        "Bunday raqam bilan ro'yxatdan o'tilgan, boshqa telefon raqam kiriting",
        "Этот номер уже зарегистрирован. Введите другой номер",
    ]
    changed_your_phone_number = [
        """Sizning telefon raqamingiz muvaffaqiyatli o\'zgartirildi! ♻️""",
        """Ваш номер телефона успешно изменен! ♻️""",
    ]
    your_name = ["""Sizning ismingiz: """, """Ваше имя: """]
    send_new_name = [
        """Ismingizni o'zgartirish uchun, yangi ism kiriting:\n<i>Jarayonni bekor qilish uchun "🔙 Ortga" tugmasini bosing.</i>""",
        """Чтобы изменить свое имя, введите новое:\n<i>Нажмите кнопку "🔙 Назад", чтобы отменить процесс.</i>""",
    ]
    changed_your_name = [
        """Sizning ismingiz muvaffaqiyatli o'zgartirildi!""",
        """Ваше имя успешно изменено!""",
    ]

    order_details = [
        "",
        ""
    ]


    invoice_message = [
        "🧾 <i>Buyurtma ma'lumotlari:</i>\n\n🆔 Buyurtma ID: #{order_id}\n" \
            "👤 Mijoz: {customer_name}\n\n📦 Buyurtma:\n{items}\n\n💵 Jami: {subtotal} so'm\n🚚 " \
                "Yetkazib berish: {delivery_price} so'm\n💰 Umumiy: {total} so'm\n\n" \
                    "<i>Buyurtmani tasdiqlash uchun to'lovni amalga oshiring.</i>",
        "🧾 Информация о заказе:\n\n🆔 ID заказа: {order_id}\n👤 Клиент: {customer_name}\n\n" \
            "📦 Заказ:\n{items}\n\n💵 Итого: {subtotal} сум\n🚚 Доставка: {delivery_price} сум\n💰 Общая сумма: {total} сум" \
            "\n\n<i>Для подтверждения заказа, произведите оплату.</i>"
    ]

    invoice_item = [
        """🔹 {product} x{quantity} - {price} so'm""",
        """🔹 {product} x{quantity} - {price} сум"""
    ]

    pay = [
        """To'lovni amalga oshirish 💳""",
        """Оплатить 💳"""
    ]

    loyalty_card = [
        "💳 Sodiqlik kartam",
        "💳 Карта лояльности"
    ]

    your_balance = [
        "Sizning balansingiz: <b>{balance} so'm</b>",
        "Ваш баланс: <b>{balance} сум</b>"
    ]

    balance = [
        "💰 Balans",
        "💰 Баланс"
    ]

    catalog = [
        "🛒 Katalog",
        "🛒 Каталог"
    ]

    driver_info = [
        """
👤 Kuryer: {courier_name}
🚖 Mashina: {car_color} {car_model} {car_number}
""",
        """
👤 Курьер: {courier_name}
🚖 Машина: {car_color} {car_model} {car_number}"""
    ]

    performer_found_for_your_order = [
        "☑️  Sizning buyurtmangiz yandex yetkazib berish xizmati orqali yetkazib berilmoqda",
        "☑️ Ваш заказ доставляется через службу Яндекс.Доставки."
    ]

    performer_arrived_pickup = [
        "Kuryer buyurtmani qabul qilib olish uchun yetib keldi\nЗаказ #{order_id}",
        "<b>Курьер прибыл.</b>\nЗаказ #{order_id}"
    ]

    delivery_arrived = [
        "🛵 Kuryer manzilga yetib keldi, buyurtmani qabul qilib olishingiz mumkin",
        "🛵 Курьер прибыл, можете забрать заказ."
    ]

    order_delivered = [
        "Buyurtma #{order_id} muvaffaqiyatli yetkazib berildi",
        "Заказ #{order_id} успешно доставлен"
    ]

    gratitude_to_client = [
        "Buyurtmangiz uchun minnatdormiz 😊",
        "Спасибо за ваш заказ 😊"
    ]

    gratitude_for_review = [
        "Xizmatimizni baholaganingizdan minnatdormiz! 😊",
        "Благодарим вас за отзыв! 😊"
    ]

    order_error = [
        "❌ Buyurtma #{order_id} jarayonida xatolik yuz berganligi uchun sizning buyurtmangiz bekor qilindi." \
        "Iltimos qaytatdan urininb ko'ring",
        "❌ Произошла ошибка при обработке заказа #{order_id}. Пожалуйста, попробуйте еще раз."
    ]

    ask_review = [
        "🎉 Buyurtmangiz yetkazildi!\nIltimos, xizmatimizni baholang — bu bizga yanada yaxshiroq bo‘lishga yordam beradi.\nRahmat!",
        "🎉 Заказ доставлен!\nОцените, пожалуйста, наш сервис — ваш отзыв помогает нам становиться лучше.\nСпасибо!"
    ]

    leave_feedback = [
        "📝 Xizmatni baholash",
        "📝 Оставить отзыв"
    ]

    select_language = [
        "Tilni tanlang:",
        "Выберите язык:"
    ]

    languages = [
        "🇺🇿 O'zbekcha",
        "🇷🇺 Русский"
    ]

    confirm = [
        "Tasdiqlash",
        "Подтвердить"
    ]

    order_payment_returned = [
        "<b>Buyurtma #{order_id} to'lovi bekor qilindi ↩️</b>\n\n" \
        "▪️ Miqdor: {amount}\n" \
        "▪️ To'lov tizimi: {payment_system}",
        "<b>Оплата заказа #{order_id} возвращена ↩️</b>\n\n" \
        "▪️ Сумма: {amount}\n" \
        "▪️ Платежная система: {payment_system}",
    ]

    order_payment_return_error = [
        "<b>Buyurtma #{order_id} to'lovini bekor qilish jarayonida xatolik yuz berdi, iltimos operator bilan bog'laning</b>",
        "<b>Ошибка при отмене оплаты заказа #{order_id}, пожалуйста, свяжитесь с оператором</b>"
    ]

    language_successfully_changed = [
        "Bot tili muvaffaqiyatli o'zgartirildi",
        "Язык бота успешно изменен"
    ]

    promocode_already_used = [
        "Siz ushbu promokoddan avval foydalangansiz.",
        "Вы уже использовали этот промокод"
    ]

    invalid_promocode = [
        "Promokod noto'g'ri yoki muddati o'tgan.",
        "Неверный или истекший срок действия промокода."
    ]

    order_items_not_available = [
        "❌ Buyurtma #{order_id} tarkibidagi ba'zi mahsulotlar mavjud emas:\n<i>{products}</i>\n\n" \
            "Iltimos, buyurtmani yangilab qayta urinib ko'ring",
        "❌ Некоторые товары в заказе #{order_id} недоступны:\n<i>{products}</i>\n\n" \
            "Пожалуйста, обновите заказ и попробуйте еще раз"
    ]

    _ = [
        "",
        ""
    ]

    _ = [
        "",
        ""
    ]

    _ = [
        "",
        ""
    ]

    _ = [
        "",
        ""
    ]
