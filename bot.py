from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import sqlite3
import os
from dotenv import load_dotenv
from database import get_user, add_user, update_balance, get_ref_count, get_balance

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Нет имени"
    ref_id = int(message.text.split(" ")[1]) if len(message.text.split()) > 1 else None
    add_user(user_id, username, ref_id)
    await message.answer("👋 Добро пожаловать в бота!")

@dp.message(F.text == "📱 Профиль")
async def profile_handler(message: Message):
    user = get_user(message.from_user.id)
    if not user:
        return await message.answer("Пользователь не найден.")
    balance = get_balance(user[0])
    ref_count = get_ref_count(user[0])
    bot_username = os.getenv("BOT_USERNAME")
    ref_link = f"https://t.me/{bot_username}?start={user[0]}"
    await message.answer(f"👤 <b>Ваш профиль</b>

"
                         f"Имя: {user[1]}
"
                         f"Баланс: {balance} монет
"
                         f"Реферальная ссылка: {ref_link}
"
                         f"Рефералов: {ref_count}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())