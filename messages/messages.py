from aiogram.dispatcher.filters.state import State, StatesGroup


class Form(StatesGroup):
    name_add = State()
    name_delete = State()
