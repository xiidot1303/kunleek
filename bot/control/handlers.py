from bot import *
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    InlineQueryHandler,
    TypeHandler,
    ConversationHandler
)

from bot.resources.conversationList import *

from bot.bot import (
    main, login, admin_group
)

exceptions_for_filter_text = (~filters.COMMAND) & (~filters.Text(Strings.main_menu))


login_handler = ConversationHandler(
    entry_points=[CommandHandler("start", main.start)],
    states={
        SELECT_LANG: [MessageHandler(
            filters.Text(Strings.uz_ru) & exceptions_for_filter_text,
            login.select_lang
        )],
        GET_NAME: [MessageHandler(filters.TEXT & exceptions_for_filter_text, login.get_name)],
        GET_CONTACT: [MessageHandler(filters.ALL & exceptions_for_filter_text, login.get_contact)],
    },
    fallbacks=[
        CommandHandler('start', login.start)
    ],
    name="login",
    persistent=True,

)

loyalty_card_handler = MessageHandler(
    filters.Text(Strings.loyalty_card) & exceptions_for_filter_text,
    main.loyalty_card
)

balance_handler = MessageHandler(
    filters.Text(Strings.balance) & exceptions_for_filter_text,
    main.balance
)

confirm_order_handler = CallbackQueryHandler(
    pattern=r"confirm_order-(\d+)",
    callback=admin_group.confirm_order
)

order_delivered_handler = CallbackQueryHandler(
    pattern=r"delivered-(\d+)",
    callback=admin_group.order_delivered
)

handlers = [
    login_handler,
    loyalty_card_handler,
    balance_handler,
    confirm_order_handler,
    order_delivered_handler,
    TypeHandler(type=NewsletterUpdate, callback=main.newsletter_update)
]