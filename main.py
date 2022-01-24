import asyncio

from config import get_config
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from messages.messages import Form

import aioschedule

import sqlite3

TOKEN = get_config().get("TOKEN")
# bot's settings
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# keyboard created
button1 = KeyboardButton('/добавить')
button2 = KeyboardButton('/удалить')
button3 = KeyboardButton('/список')
button4 = KeyboardButton('/помощь')
markup = ReplyKeyboardMarkup().row(button1, button2).add(button3, button4)


# функция подключния к бд
def ensure_connection(func):
    def inner(*args, **kwargs):
        global conn
        with sqlite3.connect('users.db', check_same_thread=False) as conn:
            kwargs['conn'] = conn
            res = func(*args, **kwargs)
        return res

    return inner


# создание бд
@ensure_connection
def init_db(conn, force: bool = False):
    c = conn.cursor()
    if force:
        c.execute('DROP TABLE IF EXISTS users')

    c.execute('''
		CREATE TABLE IF NOT EXISTS users (
			user_id     INTEGER NOT NULL,
			freezer     TEXT,
			remain INTEGER)
	''')
    conn.commit()


# сообщение при старте
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет! Я бот холодильник. \n "
                        "Если не знаешь как мной пользоваться, нажми помощь)", reply_markup=markup)


@dp.message_handler(commands=["помощь"], commands_prefix="!/")
async def help(message: types.Message):
    await message.answer('Бот, следящий за сроками продуктов. \n' +
                         'Функции: \n' +
                         '/добавить - добавление вашего продукта \n' +
                         '/удалить - удаление вашего продукта \n' +
                         '/список - выводит все содержимое вашего холодильника) \n' +
                         '/отмена - отменяет последнее действие')


@dp.message_handler(state='*', commands=['отмена'])
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        # User is not in any state, ignoring
        return

    # Cancel state and inform user about it
    await state.finish()
    await message.answer("Отмена действия")


@dp.message_handler(commands=["добавить"], commands_prefix="!/")
async def add(message: types.Message):
    await message.answer("Введите продукт и срок годности через пробел")

    # переход в функцию add_product
    await Form.name_add.set()


@dp.message_handler(state=Form.name_add)
async def add_product(message: types.Message, state: FSMContext):
    # завершение цепочки ответов
    await state.finish()

    try:
        c = conn.cursor()
        prod, rem = message.text.split(' ')
        sql = f'INSERT INTO users (user_id, freezer, remain) VALUES ({message.from_user.id}, "{prod}", {rem})'
        c.execute(sql)
        conn.commit()
        await message.reply(f"{message.text} добавлен в список!")
    except:
        await message.reply("Произошла ошибка!")


@dp.message_handler(commands=["удалить"], commands_prefix="!/")
async def delete(message: types.Message):

    c = conn.cursor()
    prod = message.text
    sql = f'SELECT freezer, remain FROM users WHERE user_id = {message.from_user.id}'
    c.execute(sql)
    string = ''

    for name, key in c.fetchall():
        string += '\n' + name

    await message.answer(f"Ваши продукты: " + string)
    await message.answer("введите продукт который надо удалить")

    await Form.name_delete.set()


@dp.message_handler(state=Form.name_delete)
async def delete_product(message: types.Message, state: FSMContext):

    await state.finish()

    try:
        c = conn.cursor()
        prod = message.text
        sql = f'DELETE FROM users WHERE user_id = {message.from_user.id} AND freezer = "{prod}"'
        c.execute(sql)
        conn.commit()
        await message.answer("Продукт успешно удалён!")
    except:
        await message.reply(f"Произошла ошибка! проверьте введенные данные и повторите попытку снова!")


@dp.message_handler(commands=["список"], commands_prefix="!/")
async def spis(message: types.Message):

    c = conn.cursor()
    prod = message.text
    sql = f'SELECT freezer, remain FROM users WHERE user_id = {message.from_user.id}'
    c.execute(sql)
    string = ''

    for name, key in c.fetchall():
        string += name + ' ' + str(key) + '\n'

    if string == '':
        await message.reply('В вашем холодильнике ничего нет. Скорее сходите закупиться!')
    else:
        await message.reply('Список продуктов в холодильнике: \n' + string)


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer("Неизвестная команда \n "
                         "напишите /помощь если возникли проблемы")


async def test():
    # await bot.send_message(chat_id=, text='dd')
    print(1)


async def scheduler():
    aioschedule.every().day.at("22:03").do(test)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    init_db()
    # executor.start_polling(dp, skip_updates=True)
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
