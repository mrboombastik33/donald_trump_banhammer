import config
import logging
from aiogram import Bot, Dispatcher, types, flags
from aiogram.types import BotCommand
from aiogram.filters import Command
from aiogram import Router, F
import asyncio
logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=config.TOKEN)
dp = Dispatcher()


async def set_custom_commands():
    bot_commands = [
        BotCommand(command = "/start", description = "Привітанння бота"),
        BotCommand(command = "/check", description= "Перевірити всі попередні повідомлення на наявність банворда"),
        BotCommand(command = "/exit", description = "Закінчення поллінгу")
    ]
    await bot.set_my_commands(bot_commands)


def check_mute(func):
    async def wrapper(*args, **kwargs):
        if config.CHAT_ID in config.MUTED_GROUPS:
            await bot.send_message("Бота замучено в даній групі")
            await bot.send_message(config.CHAT_ID, f"{args}, {kwargs}")
            print(f"{args}, {kwargs}")
        else: await func(*args, **kwargs)
    return wrapper


@dp.message()
async def check_words(message: types.Message):
    ban_list = []
    if message.from_user.id != bot.id:
        for word in config.ban_words:
            if word in message.text.lower():
                ban_list.append(word)
        if ban_list:
            await message.answer(f"Слова ({", ".join(ban_list)}) зафіксоване в рядку '{message.text}'")
            await mute_user(message.from_user.id, message.from_user.full_name)
    await message.answer(text=message.text)


@dp.message(Command("start"))
@flags.authorization(is_authorized=True)
async def start_msg(message: types.Message):
    await message.answer("Привіт, я бот-модератор!")


async def mute_user(user_id, user_name):
    #await bot.restrict_chat_member(config.CHAT_ID, user_id, permissions=types.ChatPermissions(can_send_messages=False))
    await bot.send_message(config.CHAT_ID, f"Користувача {user_name} замучено в групі. Тегаю адмінів")
    try:
        admin_names = [admin.user.username for admin in config.CHAT_ADMINISTRATORS]
        await bot.send_message(config.CHAT_ID, f"@{', @'.join(admin_names)}")
    except Exception as e:
        await bot.send_message(config.CHAT_ID, "Кароч самі думайте що з цим чудіком робити")


@dp.message(Command("mute_bot"))
async def exit_polling(msg = types.Message):
    if msg.from_user.id in config.CHAT_ADMINISTRATORS:
        config.MUTED_GROUPS.append(config.CHAT_ID)
    else: pass


async def main():
    print(' Оцей ваш поллінг...')

    config.CHAT_ADMINISTRATORS = await bot.get_chat_administrators(config.CHAT_ID)

    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(' Програму зупинено вручну.')
