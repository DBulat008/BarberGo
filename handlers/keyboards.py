from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✂️ Услуги",
                    callback_data="services",
                ),
                InlineKeyboardButton(
                    text="💰 Цены",
                    callback_data="prices",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📅 Записаться",
                    callback_data="booking",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📞 Связаться",
                    callback_data="contact",
                ),
            ],
        ]
    )
