from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from handlers.keyboards import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "✂️ Добро пожаловать в BarberGo!\n\n"
        "Выберите нужный раздел:",
        reply_markup=main_menu_keyboard(),
    )