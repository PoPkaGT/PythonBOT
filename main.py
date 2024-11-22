import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.router import Router
from aiogram.filters import Command

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен бота
API_TOKEN = "7205454995:AAHNSTK4btRmMlvFEMeyIe-P_4jwEfw-FYY"

# Создаём бот и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Основной роутер
router = Router()
dp.include_router(router)

# Функция для создания клавиатуры с кнопками
def main_keyboard():
    # Создаем клавиатуру, передавая список кнопок в поле inline_keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Button 1", callback_data="button_1"),
         InlineKeyboardButton(text="Button 2", callback_data="button_2")]
    ])
    return keyboard
# Команда /start для приветствия
@router.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        await message.reply("👋 Привет! Я Family Quest бот. Готов работать в группе! 🎮", reply_markup=main_keyboard())
    else:
        await message.reply("Этот бот работает только в группах. Добавьте меня в семейный чат!")

# Обработка кнопок
@router.callback_query(lambda c: c.data == "add_task")
async def add_task_callback(callback_query: types.CallbackQuery):
    await callback_query.message.answer("🔧 Напишите задачу, которую хотите добавить.")
    # После этого мы ожидаем текст от пользователя для добавления задачи.

@router.callback_query(lambda c: c.data == "done_task")
async def done_task_callback(callback_query: types.CallbackQuery):
    await callback_query.message.answer("✅ Задача отмечена как выполненная!")
    # Здесь можно реализовать логику завершения задачи, например, отметить задачу как завершенную в базе данных.

@router.callback_query(lambda c: c.data == "help")
async def help_callback(callback_query: types.CallbackQuery):
    help_text = (
        "🤖 Family Quest Bot – Помощник для вашей семьи!\n\n"
        "Возможности:\n"
        "- Добавление задач: Нажмите на кнопку 'Добавить задачу'.\n"
        "- Завершение задач: Нажмите на кнопку 'Завершить задачу'.\n"
        "- Помощь: Нажмите на кнопку 'Помощь'.\n"
    )
    await callback_query.message.answer(help_text)

# Запуск бота
async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if name == "main":
    asyncio.run(main())