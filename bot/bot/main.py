from bot.bot import *
import json
import logging
import traceback
import html
from django.db import close_old_connections
from bot.services.barcode_service import generate_barcode
from app.services.billz_service import BillzService, ClientDetails, APIMethods


async def start(update: Update, context: CustomContext):
    if await is_group(update):
        return

    if await is_registered(update.message.chat.id):
        # some functions
        await main_menu(update, context)
    else:
        hello_text = Strings.hello
        await update.message.reply_text(
            hello_text,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[["UZ 🇺🇿", "RU 🇷🇺"]], resize_keyboard=True, one_time_keyboard=True
            ),
        )
        return SELECT_LANG


async def loyalty_card(update: Update, context: CustomContext):
    bot_user = await get_object_by_update(update)

    # check that barcode image exists
    if not bot_user.card_file:
        file_name, content_file = await generate_barcode(
            user_id=bot_user.user_id, barcode=bot_user.card
        )
        await sync_to_async(bot_user.card_file.save)(file_name, content_file, save=True)
        await bot_user.asave()

    await update.message.reply_photo(
        photo=bot_user.card_file,
        caption=bot_user.card,
        parse_mode=ParseMode.HTML
    )


async def balance(update: Update, context: CustomContext):
    bot_user = await get_object_by_update(update)
    billz_service = BillzService(APIMethods.customer)
    client: ClientDetails = await sync_to_async(billz_service.get_client_by_id)(bot_user.billz_id)
    balance = client.balance
    if balance is None:
        balance = 0

    await update.message.reply_text(
        context.words.your_balance.format(balance=balance),
        parse_mode=ParseMode.HTML
    )


async def change_language(update: Update, context: CustomContext):
    bot_user = await get_object_by_update(update)
    if not bot_user:
        return

    # Change the user's language
    # send message
    reply_markup = await switch_languages_inline_keyboard(context)
    await update.message.reply_text(
        context.words.select_language,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


async def newsletter_update(update: NewsletterUpdate, context: CustomContext):
    bot = context.bot
    if not (update.photo or update.video or update.document or update.location):
        # send text message
        message = await bot.send_message(
            chat_id=update.user_id,
            text=update.text,
            reply_markup=update.reply_markup,
            parse_mode=ParseMode.HTML
        )

    if update.photo:
        # send photo
        message = await bot.send_photo(
            update.user_id,
            update.photo,
            caption=update.text,
            reply_markup=update.reply_markup,
            parse_mode=ParseMode.HTML,
        )
    if update.video:
        # send video
        message = await bot.send_video(
            update.user_id,
            update.video,
            caption=update.text,
            reply_markup=update.reply_markup,
            parse_mode=ParseMode.HTML,
        )
    if update.document:
        # send document
        message = await bot.send_document(
            update.user_id,
            update.document,
            caption=update.text,
            reply_markup=update.reply_markup,
            parse_mode=ParseMode.HTML,
        )
    if update.location:
        # send location
        message = await bot.send_location(
            chat_id=update.user_id,
            latitude=update.location.get('latitude'),
            longitude=update.location.get('longitude')
        )
    if update.pin_message:
        await bot.pin_chat_message(chat_id=update.user_id, message_id=message.message_id)


###############################################################################################
###############################################################################################
###############################################################################################
logger = logging.getLogger(__name__)


async def error_handler(update: Update, context: CustomContext):
    # restart db connection if error is "connection already closed"
    if "connection already closed" in str(context.error):
        await sync_to_async(close_old_connections)()
        return

    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)
    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
    )
    error_message = f"{html.escape(tb_string)}"

    # Finally, send the message
    try:
        await context.bot.send_message(
            chat_id=206261493, text=message, parse_mode=ParseMode.HTML
        )
        for i in range(0, len(error_message), 4000):
            await context.bot.send_message(
                chat_id=206261493, text=f"<pre>{error_message[i:i+4000]}</pre>", parse_mode=ParseMode.HTML
            )
    except Exception as ex:
        print(ex)
