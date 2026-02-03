from bot.bot import *


async def switch_language(update: Update, context: CustomContext):
    query = update.callback_query
    bot_user = await get_object_by_update(update)
    *args, new_lang_code = query.data.split("-")
    new_lang_code = int(new_lang_code)
    bot_user.lang = new_lang_code
    await bot_user.asave()
    # Change the user's language
    # send message
    reply_markup = await switch_languages_inline_keyboard(context)
    await query.edit_message_text(
        text=context.words.select_language,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )