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
    main,
)

exceptions_for_filter_text = (~filters.COMMAND) & (~filters.Text(Strings.main_menu))

start = CommandHandler('start', main.start)

handlers = [
    start,
    TypeHandler(type=NewsletterUpdate, callback=main.newsletter_update)
]