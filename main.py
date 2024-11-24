import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.dispatcher.router import Router

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен бота
API_TOKEN = "TOKEN"

# Создаём бот и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Основной роутер
router = Router()
dp.include_router(router)

# Хранение состояния пользователей
user_data = {}

# ID администратора (для примера, нужно заменить на реальный ID администратора)
ADMIN_ID = 123456789


# Функция для подключения к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row  # Для возврата результатов как словарь
    return conn


# Функция для создания таблицы задач, если она не существует
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        assigned_to TEXT,
                        status TEXT,
                        chat_id INTEGER NOT NULL
                    )''')
    conn.commit()
    conn.close()


def save_task(name, description, assigned_to, status, chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (name, description, assigned_to, status, chat_id) VALUES (?, ?, ?, ?, ?)",
                   (name, description, assigned_to, status, chat_id))
    conn.commit()
    conn.close()


# Загружаем задачи из базы данных
def load_tasks(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE chat_id = ?", (chat_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks


# Обновляем статус задачи
def update_task_status(task_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()


# Удаляем задачу
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


# Функция для создания клавиатуры с кнопками
def main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Добавить задачу", callback_data="add_task"),
        InlineKeyboardButton(text="Помощь", callback_data="help"),
        InlineKeyboardButton(text="Задачи", callback_data="view_tasks")
    ]])
    return keyboard


def manage_tasks_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Управлять заданиями", callback_data="manage_tasks")
    ]])
    return keyboard


def task_info_keyboard(task_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Сменить статус", callback_data=f"change_status_{task_id}"),
        InlineKeyboardButton(text="Удалить задачу", callback_data=f"delete_task_{task_id}"),
        InlineKeyboardButton(text="Назад", callback_data=f"back_to_manage_tasks_{task_id}")
    ]])
    return keyboard


# Функция для проверки прав доступа


# Функция для проверки прав администратора
# Функция для проверки прав администратора
async def is_admin(chat_id, user_id):
    try:
        administrators = await bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in administrators)
    except Exception as e:
        logging.error(f"Error checking admin status: {e}")
        return False

# Команда /start для приветствия
@router.message(Command(commands=["start"]))
async def start_handler(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        await message.reply("👋 Привет! Я Family Quest бот. Готов работать в группе! 🎮", reply_markup=main_keyboard())
    else:
        await message.reply("Этот бот работает только в группах. Добавьте меня в семейный чат!")


# Обработка кнопки "Добавить задачу"
@router.callback_query(lambda c: c.data == "add_task")
async def add_task_callback(callback_query: types.CallbackQuery):
    # Проверяем, является ли пользователь администратором
    is_chat_admin = await is_admin(callback_query.message.chat.id, callback_query.from_user.id)

    if not is_chat_admin:
        # Если пользователь не администратор, уведомляем его
        await callback_query.message.answer(
            "❌ У вас нет прав для добавления задач. Только администратор может это делать.")
        return

    # Продолжаем выполнение для администратора
    await callback_query.message.answer("🔧 Напишите название задачи.")
    user_data[callback_query.from_user.id] = {'step': 'name'}

# Получение названия задачи
@router.message()
async def get_task_details(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return  # Если пользователь не начал создание задачи

    step = user_data[user_id].get('step')

    if step == 'name':  # Этап получения названия задачи
        user_data[user_id]['name'] = message.text.strip()
        user_data[user_id]['step'] = 'description'
        await message.answer("Теперь напишите описание задачи.")
    elif step == 'description':  # Этап получения описания задачи
        user_data[user_id]['description'] = message.text.strip()
        # Предложим выбрать кому назначить задачу
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Для всех участников группы", callback_data="assign_all"),
            InlineKeyboardButton(text="Для конкретного участника", callback_data="assign_user")
        ]])
        await message.answer("Задача создана! Кому хотите её поручить?", reply_markup=keyboard)
        user_data[user_id]['step'] = 'assign'
    elif step == 'user_assignee':  # Если этап назначения пользователя
        assignee = message.text.strip()

        # Проверка на корректный формат ввода #@ник
        if assignee.startswith('#@'):
            assignee = assignee[2:]  # Убираем #@ в начале
            task = user_data[user_id]
            task['assigned_to'] = assignee
            task['status'] = "В процессе"  # Статус по умолчанию
            chat_id = message.chat.id  # Получаем chat_id
            # Сохраняем задачу в базу данных
            save_task(task['name'], task['description'], assignee, task['status'], chat_id)
            await message.answer(f"Задача '{task['name']}' поручена {assignee}. Статус: {task['status']}.")
            del user_data[user_id]  # Удаляем данные пользователя после выполнения задачи
            # Перебрасываем в главное меню
            await message.answer("Задача успешно создана! Вернемся в главное меню.", reply_markup=main_keyboard())
        else:
            await message.answer("Пожалуйста, введите #@ник пользователя в правильном формате.")


@router.callback_query(lambda c: c.data == "assign_user")
async def assign_user_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # Устанавливаем шаг на 'user_assignee', чтобы бот знал, что ждем ввод ника
    user_data[user_id]['step'] = 'user_assignee'
    await callback_query.message.answer(
        "Введите #@ник пользователя, которому нужно поручить задачу. (с символами '#@')")


@router.callback_query(lambda c: c.data == "assign_all")
async def assign_all_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    task = user_data[user_id]
    task['assigned_to'] = 'all'
    task['status'] = "В процессе"  # Статус по умолчанию
    chat_id = callback_query.message.chat.id  # Получаем chat_id из объекта сообщения
    save_task(task['name'], task['description'], task['assigned_to'], task['status'], chat_id)
    await callback_query.message.answer(
        f"Задача '{task['name']}' поручена всем участникам группы. Статус: {task['status']}.")
    del user_data[user_id]
    # Перебрасываем в главное меню
    await callback_query.message.answer("Задача успешно создана! Вернемся в главное меню.",
                                        reply_markup=main_keyboard())


@router.callback_query(lambda c: c.data == "view_tasks")
async def view_tasks(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id  # Получаем ID текущего чата
    tasks = load_tasks(chat_id)  # Загружаем задачи для этого чата
    if not tasks:
        await callback_query.message.answer("На данный момент нет задач.", reply_markup=main_keyboard())
        return

    task_list = ""
    for task in tasks:
        task_list += f"Название: {task['name']}\nОписание: {task['description']}\nПоручено: {task['assigned_to']}\nСтатус: {task['status']}\n\n"

    # Проверка, является ли пользователь администратором
    is_chat_admin = await is_admin(callback_query.message.chat.id, callback_query.from_user.id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Управлять", callback_data="manage_tasks") if is_chat_admin else InlineKeyboardButton(text="Управлять", callback_data="no_access_manage_tasks"),
        InlineKeyboardButton(text="Назад в меню", callback_data="back_to_main_menu")
    ]])

    await callback_query.message.answer(f"Текущие задачи:\n\n{task_list}", reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "help")
async def add_task_callback(callback_query: types.CallbackQuery):
    await callback_query.message.answer("🔧 За помощью обращаться сюда -> https://t.me/ru_literature")


@router.callback_query(lambda c: c.data == "manage_tasks")
async def manage_tasks_callback(callback_query: types.CallbackQuery):
    # Проверяем, является ли пользователь администратором
    is_chat_admin = await is_admin(callback_query.message.chat.id, callback_query.from_user.id)

    if not is_chat_admin:
        await callback_query.message.answer(
            "❌ У вас нет прав для управления задачами. Только администратор может это делать.")
        return

    chat_id = callback_query.message.chat.id  # Получаем ID текущего чата
    tasks = load_tasks(chat_id)  # Загружаем задачи для этого чата
    if not tasks:
        await callback_query.message.answer("На данный момент нет задач для управления.", reply_markup=main_keyboard())
        return

    task_buttons = [
        [InlineKeyboardButton(text=task['name'], callback_data=f"task_{task['id']}") for task in tasks],
        [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_main_menu")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=task_buttons)

    await callback_query.message.answer("Выберите задачу для управления:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("task_"))
async def task_management_callback(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split("_")[1])  # Извлекаем ID задачи
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()

    if not task:
        await callback_query.message.answer("Задача не найдена.")
        return

    keyboard = task_info_keyboard(task_id)

    await callback_query.message.answer(
        f"Задача: {task['name']}\nОписание: {task['description']}\nПоручено: {task['assigned_to']}\nСтатус: {task['status']}",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data.startswith("change_status_"))
async def change_status_callback(callback_query: types.CallbackQuery):
    # Проверяем, является ли пользователь администратором
    is_chat_admin = await is_admin(callback_query.message.chat.id, callback_query.from_user.id)

    if not is_chat_admin:
        # Если пользователь не администратор, уведомляем его
        await callback_query.message.answer(
            "❌ У вас нет прав для изменения статуса задачи. Только администратор может это делать.")
        return

    task_id = int(callback_query.data.split("_")[2])  # Извлекаем ID задачи
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()

    if not task:
        await callback_query.message.answer("Задача не найдена.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="В процессе", callback_data=f"status_in_progress_{task_id}"),
        InlineKeyboardButton(text="Завершена", callback_data=f"status_completed_{task_id}"),
        InlineKeyboardButton(text="Назад", callback_data=f"back_to_manage_tasks_{task_id}")
    ]])

    await callback_query.message.answer(f"Выберите новый статус для задачи '{task['name']}':", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("status_in_progress_"))
async def status_in_progress_callback(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split("_")[3])  # Извлекаем ID задачи
    update_task_status(task_id, "В процессе")
    await callback_query.message.answer(f"Статус задачи изменен на 'В процессе'.",
                                        reply_markup=task_info_keyboard(task_id))


@router.callback_query(lambda c: c.data.startswith("status_completed_"))
async def status_completed_callback(callback_query: types.CallbackQuery):
    task_id = int(callback_query.data.split("_")[2])  # Извлекаем ID задачи
    update_task_status(task_id, "Завершена")
    await callback_query.message.answer(f"Статус задачи изменен на 'Завершена'.",
                                        reply_markup=task_info_keyboard(task_id))


@router.callback_query(lambda c: c.data.startswith("back_to_manage_tasks"))
async def back_to_manage_tasks(callback_query: types.CallbackQuery):
    await manage_tasks_callback(callback_query)


@router.callback_query(lambda c: c.data.startswith("delete_task_"))
async def delete_task_callback(callback_query: types.CallbackQuery):
    # Проверяем, является ли пользователь администратором
    is_chat_admin = await is_admin(callback_query.message.chat.id, callback_query.from_user.id)

    if not is_chat_admin:
        # Если пользователь не администратор, уведомляем его
        await callback_query.message.answer(
            "❌ У вас нет прав для удаления задач. Только администратор может это делать.")
        return

    task_id = int(callback_query.data.split("_")[2])  # Извлекаем ID задачи
    delete_task(task_id)  # Удаляем задачу из базы данных
    await callback_query.message.answer("Задача удалена.", reply_markup=main_keyboard())


@router.callback_query(lambda c: c.data == "back_to_main_menu")
async def back_to_main_menu(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Вы вернулись в главное меню.", reply_markup=main_keyboard())


# Запуск бота
async def main():
    create_table()  # Создаем таблицу, если её нет
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())