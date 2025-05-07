from aiogram.exceptions import TelegramForbiddenError
from config import ban_words, TOKEN
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import BotCommand
from aiogram.filters import Command
import asyncio
from db_info.engine import create_db, drop_db, session_maker
from db_interact import orm_select_chat_id, orm_add_chat, orm_check_mute
from midddleware import DatabaseSession
from keyboards import create_kb, ban_cb_query

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def set_custom_commands():
    bot_commands = [
        BotCommand(command = "/start", description = "Привітанння бота"),
        BotCommand(command = "/check", description= "Перевірити всі попередні повідомлення на наявність банворда"),
        BotCommand(command = "/exit", description = "Закінчення поллінгу"),
        BotCommand(command = "/mute", description = "Замутити бота")
    ]
    await bot.set_my_commands(bot_commands)

@dp.message()
async def check_words(message: types.Message):
    #Перевірка на існування айдішки чату в БД

    async with session_maker() as session:
        chat_exists = await orm_select_chat_id(session, message.chat.id)

        if not chat_exists:
            chat_admins = await bot.get_chat_administrators(message.chat.id)

            admin_list = [
                {
                    "admin_id": admin.user.id,
                    "admin_tag": admin.user.username or admin.user.full_name
                }
                for admin in chat_admins if not admin.is_anonymous and admin.id != bot.id  # Враховую анонімних адмінів
            ]

            await orm_add_chat(session, {
                "id": message.chat.id,
                "chat_name": message.chat.title,
                "chat_admins": admin_list,
            })

    #Перевірка на наявність банвордів
    ban_list = []
    if message.from_user.id != bot.id:
        for word in ban_words:
            if word in message.text.lower():
                ban_list.append(word)
        if ban_list:
            await message.answer(f"Слова ({", ".join(ban_list)}) зафіксоване в рядку '{message.text}'")
            unmuted: bool
            async with session_maker() as session:
                unmuted = await orm_check_mute(session, message.chat.id)
            if not unmuted:
                #await tag_admins_if_muted(message)
                await mute_user(message.chat.id, message.from_user.id, message.from_user.full_name)
            else :
                await tag_admins_if_muted(message)
            return
    #await message.answer(text=message.text)


@dp.message(Command("start"))
async def start_msg(message: types.Message):
    await message.answer("Привіт, я бот-модератор. Напишіть, як у вас справи!")


async def mute_user(chat_id, user_id, user_name):
    #await bot.restrict_chat_member(chat_id, user_id, permissions=types.ChatPermissions(can_send_messages=False))

    await bot.send_message(chat_id, f"Користувача {user_name} замучено в групі. Тегаю адмінів")
    try:
        admin_list = await bot.get_chat_administrators(chat_id)
        admin_names = [admin.user.username for admin in admin_list if admin.user.id != bot.id and admin.user.id != user_id and admin.user.username]
        await bot.send_message(chat_id, f"@{', @'.join(admin_names)}")
        if not admin_names:
            await bot.send_message(chat_id, f"Кароч, адмінів нема, думайте самі що з чудіком робити.")
    except Exception as e:
        await bot.send_message(chat_id, "Кароч самі думайте що з цим чудіком робити")


async def tag_admins_if_muted(message: types.Message):
    chat_id = message.chat.id
    admin_list = await bot.get_chat_administrators(chat_id)
    admin_ids = [admin.user.id for admin in admin_list if admin.user.id != bot.id and admin.user.id != message.from_user.id and admin.user.username]
    if message.chat.username:
        text_link = (f'Юзер @{message.from_user.username} надіслав нехороше повідомлення в чаті {message.chat.title}. '
                     f'Бот замучений, тому перегляньте <a href="https://t.me/{message.chat.username}/{message.message_id}">повідомлення</a>')
    else:
        text_link = (f'Юзер @{message.from_user.username} надіслав нехороше повідомлення в чаті {message.chat.title}. '
                     f'Група приватна, тому форварджу повідомлення.')
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id,
                                   text_link, parse_mode="HTML")
            if message.chat.username is None:
                await bot.forward_message(admin_id, message.chat.id, message.message_id)
        except TelegramForbiddenError:
            print(f'До юзера {admin_id} повідомлення не дійшло')


async def admin_choice(chat_id):
    markup = create_kb()
    await bot.send_message(chat_id, "Ви хочете замутити даного юзера в групі?", reply_markup=markup)


'''@dp.callback_query(F.data == ban_cb_query)
async def callback_ban(chat_id, user_id):
    await mute_user()'''


async def on_startup():
    run_param = False
    if run_param:
        await drop_db()
    await create_db()


async def on_shutdown():
    print("Мінус бот")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DatabaseSession(session_pool=session_maker))

    print(' Оцей ваш поллінг...')
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(' Програму зупинено вручну.')
