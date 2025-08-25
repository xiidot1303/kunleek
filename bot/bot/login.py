from bot.bot import *
from app.services.billz_service import BillzService, APIMethods, ClientDetails


async def _to_the_select_lang(update: Update):
    await update_message_reply_text(
        update,
        "Bot tilini tanlang\n\nВыберите язык бота",
        reply_markup=await reply_keyboard_markup([Strings.uz_ru]),

    )
    return SELECT_LANG


async def _to_the_get_name(update: Update):
    await update_message_reply_text(
        update=update,
        text=Strings(user_id=update.effective_user.id).type_name,
        reply_markup=await reply_keyboard_markup([[Strings(user_id=update.effective_user.id).back]], one_time_keyboard=True),
    )
    return GET_NAME


async def _to_the_get_contact(update: Update):
    i_contact = KeyboardButton(
        text=Strings(
            user_id=update.effective_user.id).leave_number, request_contact=True
    )
    await update_message_reply_text(
        update,
        Strings(user_id=update.effective_user.id).send_number,
        reply_markup=await reply_keyboard_markup(
            [[i_contact], [
                Strings(user_id=update.effective_user.id).back]], one_time_keyboard=True
        ),
    )
    return GET_CONTACT


async def select_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "UZ" in text:
        lang = 0
    elif "RU" in text:
        lang = 1
    else:
        return await _to_the_select_lang(update)

    await get_or_create(user_id=update.effective_chat.id)
    obj = await get_object_by_user_id(user_id=update.effective_chat.id)
    obj.lang = lang
    obj.username = update.effective_chat.username
    obj.firstname = update.effective_chat.first_name
    obj.name = update.message.chat.first_name
    obj.phone = ''
    await obj.asave()

    return await _to_the_get_name(update)


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == Strings(user_id=update.effective_user.id).back:
        return await _to_the_select_lang(update)

    obj = await get_object_by_user_id(user_id=update.effective_chat.id)
    obj.name = update.message.text
    obj.username = update.effective_chat.username
    obj.firstname = update.effective_chat.first_name
    await obj.asave()

    return await _to_the_get_contact(update)



async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == Strings(user_id=update.effective_user.id).back:
        return await _to_the_get_name(update)

    if update.message.contact is None or not update.message.contact:
        phone_number = update.message.text
    else:
        phone_number = update.message.contact.phone_number
    # check that phone is available or no
    is_available = await Bot_user.objects.filter(phone=phone_number).afirst()
    if is_available:
        await update_message_reply_text(update, Strings(user_id=update.effective_user.id).number_is_logged)
        return GET_CONTACT
    obj = await get_object_by_user_id(user_id=update.message.chat.id)
    obj.phone = phone_number
    await obj.asave()

    context.job_queue.run_once(
        connect_billz_client_job,
        when=0,
        data=obj.id,
        chat_id=update.effective_chat.id
    )
    
    await main_menu(update, context)
    return ConversationHandler.END


async def connect_billz_client_job(context: CustomContext):
    job = context.job
    bot_user_id = job.data
    bot_user: Bot_user = await Bot_user.objects.aget(id=bot_user_id)
    # get client details from billz
    billz_service = BillzService(APIMethods.clients)
    client_details: ClientDetails = await sync_to_async(billz_service.get_client_by_phone_number)(bot_user.phone)

    if not client_details:
        # create new client in billz
        client_id = await sync_to_async(billz_service.create_client)(
            chat_id=bot_user.user_id,
            first_name=bot_user.name,
            phone_number=bot_user.phone
        )

        client_details: ClientDetails = await sync_to_async(billz_service.get_client_by_id)(client_id)

    bot_user.name = f"{client_details.first_name} {client_details.last_name}"
    bot_user.billz_id = client_details.id

    # create new card if not exist
    if not client_details.card:
        card_code = await sync_to_async(billz_service.create_client_card)(client_details.id)
        client_details.card = card_code
    bot_user.card = client_details.card
    await bot_user.asave()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await _to_the_select_lang(update)
