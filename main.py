# main.py — основной файл бота

import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import logging

# ---------- Настройки ----------
API_TOKEN = "8694731612:AAEAE9q6cg96CRS1kefQX_CUN_aJDfTB-Tc"  # <-- вставь сюда токен твоего бота
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ---------- Данные пользователей ----------
users = {}  # {user_id: {"balance": 1000, "daily_win": 0}}
wheel_bets = {}
wheel_numbers = list(range(37))
red_numbers = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
wheel_open = False

# ---------- Меню ----------
def bottom_menu():
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("Профиль 👤", callback_data="profile"),
        InlineKeyboardButton("Игры 🎮", callback_data="games"),
        InlineKeyboardButton("Рейтинг 🏆", callback_data="rating")
    )
    return keyboard

def games_menu():
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("Рулетка 🎡", callback_data="wheel"),
        InlineKeyboardButton("Кубик 🎲", callback_data="dice"),
        InlineKeyboardButton("Dable 🎯", callback_data="dable")
    )
    return keyboard

def wheel_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Чёрное ⚫", callback_data="black"),
        InlineKeyboardButton("Красное 🔴", callback_data="red"),
        InlineKeyboardButton("Чётное", callback_data="even"),
        InlineKeyboardButton("Нечётное", callback_data="odd"),
        InlineKeyboardButton("1-18", callback_data="1-18"),
        InlineKeyboardButton("19-36", callback_data="19-36"),
        InlineKeyboardButton("1-12", callback_data="1-12"),
        InlineKeyboardButton("13-24", callback_data="13-24"),
        InlineKeyboardButton("25-36", callback_data="25-36"),
        InlineKeyboardButton("0️⃣", callback_data="0")
    )
    return keyboard

# ---------- Хелперы ----------
def get_user(user_id):
    if user_id not in users:
        users[user_id] = {"balance": 1000, "daily_win": 0}
    return users[user_id]

# ---------- Хэндлеры ----------
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    get_user(message.from_user.id)
    await message.answer("Добро пожаловать в казино-бот!", reply_markup=bottom_menu())

@dp.callback_query_handler(lambda c: True)
async def callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = get_user(user_id)
    data = callback_query.data

    if data == "profile":
        await callback_query.message.answer(
            f"💰 Баланс: {user['balance']}\nКнопки управления балансом:",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("Пополнить +100", callback_data="deposit"),
                InlineKeyboardButton("Вывести -100", callback_data="withdraw")
            )
        )
    elif data == "deposit":
        user['balance'] += 100
        await callback_query.message.answer(f"Баланс пополнен! Теперь: {user['balance']}", reply_markup=bottom_menu())
    elif data == "withdraw":
        if user['balance'] >= 100:
            user['balance'] -= 100
            await callback_query.message.answer(f"Вы вывели 100. Баланс: {user['balance']}", reply_markup=bottom_menu())
        else:
            await callback_query.message.answer("Недостаточно средств", reply_markup=bottom_menu())
    elif data == "games":
        await callback_query.message.answer("Выберите игру:", reply_markup=games_menu())
    elif data == "rating":
        top = sorted(users.items(), key=lambda x: x[1]['daily_win'], reverse=True)[:10]
        text = "🏆 Рейтинг игроков за сегодня:\n"
        for idx, (uid, info) in enumerate(top, 1):
            text += f"{idx}. Игрок {uid}: {info['daily_win']}\n"
        await callback_query.message.answer(text, reply_markup=bottom_menu())
    elif data == "wheel":
        await start_wheel(user_id)

# ---------- Рулетка ----------
async def start_wheel(user_id):
    global wheel_open
    if wheel_open:
        await bot.send_message(user_id, "Ставки уже открыты!")
        return
    wheel_open = True
    wheel_bets.clear()
    await bot.send_message(user_id, "Ставки открыты! 20 секунд.", reply_markup=wheel_menu())
    await asyncio.sleep(20)
    await spin_wheel()

async def spin_wheel():
    global wheel_open
    wheel_open = False
    final_number = random.choice(wheel_numbers)
    spin_sequence = random.choices(wheel_numbers, k=15) + [final_number]

    for num in spin_sequence:
        color = "🔴" if num in red_numbers else "⚫"
        await asyncio.sleep(0.5)
        for uid in wheel_bets.keys():
            await bot.send_message(uid, f"🎡 Колесо крутится... {num} {color}")

    color = "🔴" if final_number in red_numbers else "⚫"
    even_odd = "even" if final_number != 0 and final_number % 2 == 0 else "odd"

    for uid, bet in wheel_bets.items():
        user = get_user(uid)
        win = 0
        bet_type = bet['bet_type']
        amount = bet['amount']
        # Здесь можно добавлять правила выигрыша, как в примере выше
        if win > 0:
            user['balance'] += win
            user['daily_win'] += win
            await bot.send_message(uid, f"Вы выиграли {win}! Баланс: {user['balance']}")
        else:
            await bot.send_message(uid, f"Вы проиграли на ставке {bet_type}. 😢")
    wheel_bets.clear()

# ---------- Запуск ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
