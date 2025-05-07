from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ban_cb_query = "ban_user"
mercy_cb_query = "mercy_user"

async def create_kb() -> InlineKeyboardMarkup:
    ban_user = InlineKeyboardButton(text="Бан")
    mercy_user = InlineKeyboardButton(text="Пощадити юзера")
    buttons = [ban_user, mercy_user]
    row = [buttons]
    markup = InlineKeyboardMarkup(inline_keyboard=row)
    return markup
