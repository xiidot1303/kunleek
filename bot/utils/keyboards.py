from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from bot import *
from bot.services.redis_service import get_user_lang
from asgiref.sync import sync_to_async


async def _inline_footer_buttons(context: CustomContext, buttons, back=True, main_menu=True):
    new_buttons = []
    if back:
        new_buttons.append(
            InlineKeyboardButton(text=context.words.back, callback_data='back'),
        )
    if main_menu:
        new_buttons.append(
            InlineKeyboardButton(text=context.words.main_menu, callback_data='main_menu'),
        )

    buttons.append(new_buttons)
    return buttons

async def select_lang_keyboard():
    buttons = [Strings.uz_ru]
    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    return markup

async def settings_keyboard(context: CustomContext):

    buttons = [
        [context.words.change_lang],
        [context.words.change_name],
        [context.words.change_phone_number],
        [context.words.main_menu],
    ]

    return buttons

async def build_keyboard(context: CustomContext, button_list, n_cols, back_button=True, main_menu_button=True):
    # split list by two cols
    button_list_split = [button_list[i:i + n_cols] for i in range(0, len(button_list), n_cols)]
    # add buttons back and main menu
    footer_buttons = []
    if back_button:
        footer_buttons.append(
            context.words.back
        )
    if main_menu_button:
        footer_buttons.append(
            context.words.main_menu
        )
    # add footer buttons if available
    buttons = button_list_split + [footer_buttons] if footer_buttons else button_list_split

    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    return reply_markup


async def switch_languages_inline_keyboard(context: CustomContext):
    user_lang_code = await sync_to_async(get_user_lang)(context._user_id)
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=Strings.languages[0] + ( "   ✅" if user_lang_code == 0 else ""),
                    callback_data=f"set_lang-0"
                )
            ],
            [
                InlineKeyboardButton(
                    text=Strings.languages[1] + ( "   ✅" if user_lang_code == 1 else ""),
                    callback_data=f"set_lang-1"
                )
            ],
            [
                InlineKeyboardButton(
                    text=context.words.confirm,
                    callback_data=f"main_menu"
                )
            ]
        ]
    )