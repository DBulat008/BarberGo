import os
import re
from database import save_booking, is_time_available

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from dotenv import load_dotenv
from datetime import datetime
from handlers.keyboards import main_menu_keyboard
from handlers.states import BookingForm

load_dotenv()

ADMIN_ID = int(os.getenv("ADMIN_ID"))

router = Router()

# =========================
# УСЛУГИ
# =========================

@router.callback_query(F.data == "services")
async def services_handler(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="back_main",
                )
            ]
        ]
    )

    await callback.message.answer(
        "✂️ Наши услуги:\n\n"
        "💈 Мужская стрижка — 1200 ₽\n"
        "🧔 Стрижка + борода — 1800 ₽\n"
        "💇‍♂️ Моделирование бороды — 800 ₽\n"
        "👦 Детская стрижка — 1000 ₽",
        reply_markup=keyboard,
    )

    await callback.answer()

# =========================
# ЦЕНЫ
# =========================

@router.callback_query(F.data == "prices")
async def prices_handler(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="back_main",
                )
            ]
        ]
    )

    await callback.message.answer(
        "💰 Прайс-лист:\n\n"
        "💈 Мужская стрижка — 1200 ₽\n"
        "🧔 Стрижка + борода — 1800 ₽\n"
        "💇‍♂️ Моделирование бороды — 800 ₽\n"
        "👦 Детская стрижка — 1000 ₽",
        reply_markup=keyboard,
    )

    await callback.answer()


# =========================
# НАЧАЛО ЗАПИСИ
# =========================

@router.callback_query(F.data == "booking")
async def booking_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(BookingForm.choosing_service)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💈 Мужская стрижка",
                    callback_data="booking_haircut",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧔 Стрижка + борода",
                    callback_data="booking_beard",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💇‍♂️ Моделирование бороды",
                    callback_data="booking_model",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👦 Детская стрижка",
                    callback_data="booking_kids",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_main",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_booking",
                ),
            ],
        ]
    )

    await callback.message.answer(
        "📅 Выберите услугу:",
        reply_markup=keyboard,
    )

    await callback.answer()


# =========================
# ВЫБОР УСЛУГИ
# =========================

@router.callback_query(
    BookingForm.choosing_service,
    F.data.startswith("booking_")
)
async def service_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    services = {
        "haircut": "Мужская стрижка",
        "beard": "Стрижка + борода",
        "model": "Моделирование бороды",
        "kids": "Детская стрижка",
    }

    service_key = callback.data.removeprefix("booking_")
    service = services.get(service_key)

    if service is None:
        await callback.answer("Неизвестная услуга")
        return

    await state.update_data(service=service)
    await state.set_state(BookingForm.choosing_master)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💈 Алексей",
                    callback_data="master_alex",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✂️ Максим",
                    callback_data="master_max",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Дмитрий",
                    callback_data="master_dmitry",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_service",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_booking",
                ),
            ],
        ]
    )

    await callback.message.answer(
        f"✅ Услуга: {service}\n\n"
        "👤 Выберите мастера:",
        reply_markup=keyboard,
    )

    await callback.answer()


# =========================
# ВЫБОР МАСТЕРА
# =========================

@router.callback_query(
    BookingForm.choosing_master,
    F.data.startswith("master_")
)
async def master_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    masters = {
        "alex": "Алексей",
        "max": "Максим",
        "dmitry": "Дмитрий",
    }

    master_key = callback.data.removeprefix("master_")
    master = masters.get(master_key)

    if master is None:
        await callback.answer("Неизвестный мастер")
        return

    await state.update_data(master=master)
    await state.set_state(BookingForm.choosing_date)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_master",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_booking",
                ),
            ],
        ]
    )

    await callback.message.answer(
        f"💈 Мастер: {master}\n\n"
        "📅 Напишите желаемую дату.\n"
        "Например: 29.09",
        reply_markup=keyboard,
    )


# =========================
# ВВОД ДАТЫ
# =========================

@router.message(BookingForm.choosing_date)
async def date_handler(
    message: Message,
    state: FSMContext
):
    date_text = message.text.strip()

    try:
        parsed_date = datetime.strptime(
            date_text,
            "%d.%m"
        ).date()
    except ValueError:
        await message.answer(
            "❌ Неверная дата.\n\n"
            "Введите дату в формате ДД.ММ\n"
            "Например: 29.10"
        )
        return

    today = datetime.now().date()

    parsed_date = parsed_date.replace(year=today.year)

    if parsed_date < today:
        await message.answer(
            "❌ Эта дата уже прошла.\n\n"
            "Введите будущую дату."
        )
        return

    await state.update_data(
        date=parsed_date.strftime("%d.%m.%Y")
    )

    await state.set_state(
        BookingForm.choosing_time
    )

    await message.answer(
        f"✅ Дата: {parsed_date.strftime('%d.%m.%Y')}\n\n"
        "🕐 Теперь введите желаемое время.\n"
        "Например: 15:00"
    )
@router.message(BookingForm.choosing_time)
async def time_handler(
    message: Message,
    state: FSMContext
):
    time_text = message.text.strip()
    if not re.fullmatch(r"\d{2}:\d{2}", time_text):
        await message.answer(
            "❌ Неверный формат времени.\n\n"
            "Введите время в формате ЧЧ:ММ.\n"
            "Например: 12:00"
        )
        return

    try:
        selected_time = datetime.strptime(
            time_text,
            "%H:%M"
        ).time()
    except ValueError:
        await message.answer(
            "❌ Неверное время.\n\n"
            "Введите время в формате ЧЧ:ММ.\n"
            "Например: 15:00"
        )
        return
    if selected_time.minute not in (0, 30):
        await message.answer(
            "❌ Можно выбрать только время с шагом 30 минут.\n\n"
            "Например: 12:00 или 12:30."
        )
        return

    if selected_time.hour < 9 or selected_time.hour >= 20:
        await message.answer(
            "❌ В это время барбершоп не работает.\n\n"
            "Введите время с 09:00 до 19:59."
        )
        return

    data = await state.get_data()

    master = data["master"]
    date = data["date"]

    if not is_time_available(master, date, time_text):
        await message.answer(
            "❌ Это время уже занято.\n\n"
            "Введите другое время."
        )
        return

    await state.update_data(time=time_text)

    await state.set_state(BookingForm.entering_name)

    keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="back_date",
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel_booking",
            ),
        ],
    ]
)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_date",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_booking",
                ),
            ],
        ]
    )

    await message.answer(
        f"✅ Время: {time_text}\n\n"
        "👤 Теперь напишите ваше имя.",
        reply_markup=keyboard,
    )

@router.message(BookingForm.entering_name)
async def name_handler(
    message: Message,
    state: FSMContext
):
    name = message.text.strip()

    if not re.fullmatch(r"[A-Za-zА-Яа-яЁё\s-]{2,30}", name):
        await message.answer(
            "❌ Некорректное имя.\n\n"
            "Введите имя от 2 до 30 символов.\n"
            "Например: Дмитрий"
        )
        return

    await state.update_data(name=name)

    await state.set_state(BookingForm.entering_phone)

    await message.answer(
        f"✅ Имя: {name}\n\n"
        "📞 Теперь напишите ваш номер телефона."
    )


@router.message(BookingForm.entering_phone)
async def phone_handler(
    message: Message,
    state: FSMContext
):
    phone = message.text.strip()

    if not re.fullmatch(r"(?:\+7|8)\d{10}", phone):
        await message.answer(
            "❌ Некорректный номер телефона.\n\n"
            "Введите номер в формате:\n"
            "+79991234567\n"
            "или\n"
            "89991234567"
        )
        return

    await state.update_data(phone=phone)

    await state.set_state(BookingForm.confirmation)

    data = await state.get_data()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить",
                    callback_data="confirm_booking",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_name",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_booking",
                ),
            ],
        ]
    )

    await message.answer(
        "📋 Проверьте запись:\n\n"
        f"✂️ Услуга: {data['service']}\n"
        f"💈 Мастер: {data['master']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}",
        reply_markup=keyboard,
    )
@router.callback_query(F.data == "cancel_booking")
async def cancel_booking_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.clear()

    await callback.message.answer(
        "❌ Запись отменена.\n\n"
        "Вы вернулись в главное меню.",
        reply_markup=main_menu_keyboard(),
    )

    await callback.answer()


@router.callback_query(F.data == "back_main")
async def back_main_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.clear()

    await callback.message.answer(
        "🏠 Главное меню:",
        reply_markup=main_menu_keyboard(),
    )

    await callback.answer()


@router.callback_query(
    BookingForm.choosing_master,
    F.data == "back_service"
)
async def back_service_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(BookingForm.choosing_service)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💈 Мужская стрижка",
                    callback_data="booking_haircut",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🧔 Стрижка + борода",
                    callback_data="booking_beard",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💇‍♂️ Моделирование бороды",
                    callback_data="booking_model",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👦 Детская стрижка",
                    callback_data="booking_kids",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_main",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_booking",
                ),
            ],
        ]
    )

    await callback.message.answer(
        "📅 Выберите услугу:",
        reply_markup=keyboard,
    )

    await callback.answer()
@router.callback_query(
    BookingForm.choosing_date,
    F.data == "back_master"
)
async def back_master_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(BookingForm.choosing_master)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💈 Алексей",
                    callback_data="master_alex",
                )
            ],
            [
                InlineKeyboardButton(
                    text="✂️ Максим",
                    callback_data="master_max",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Дмитрий",
                    callback_data="master_dmitry",
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="back_service",
                ),
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_booking",
                ),
            ],
        ]
    )

    await callback.message.answer(
        "👤 Выберите мастера:",
        reply_markup=keyboard,
    )

    await callback.answer()
@router.callback_query(
    BookingForm.confirmation,
    F.data == "confirm_booking"
)
@router.callback_query(
    BookingForm.confirmation,
    F.data == "confirm_booking"
)
@router.callback_query(
    BookingForm.confirmation,
    F.data == "confirm_booking"
)
async def confirm_booking_handler(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot
):
    data = await state.get_data()

    save_booking(
        service=data["service"],
        master=data["master"],
        date=data["date"],
        time=data["time"],
        name=data["name"],
        phone=data["phone"],
    )

    admin_message = (
        "🔔 Новая запись!\n\n"
        f"✂️ Услуга: {data['service']}\n"
        f"💈 Мастер: {data['master']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}"
    )

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message,
    )

    await state.clear()

    await callback.message.answer(
        "✅ Запись подтверждена!\n\n"
        f"✂️ Услуга: {data['service']}\n"
        f"💈 Мастер: {data['master']}\n"
        f"📅 Дата: {data['date']}\n"
        f"🕐 Время: {data['time']}\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n\n"
        "Ждём вас! ✂️"
    )

    await callback.answer()
@router.callback_query(
    BookingForm.confirmation,
    F.data == "back_name"
)
async def back_name_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(BookingForm.entering_name)

    await callback.message.answer(
        "👤 Введите имя ещё раз."
    )

    await callback.answer()
@router.callback_query(F.data == "cancel_booking")
async def cancel_booking_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.clear()

    await callback.message.answer(
        "❌ Запись отменена.\n\n"
        "Вы вернулись в главное меню.",
        reply_markup=main_menu_keyboard(),
    )

    await callback.answer()
@router.callback_query(F.data == "contact")
async def contact_handler(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Главное меню",
                    callback_data="back_main",
                )
            ]
        ]
    )

    await callback.message.answer(
        "📞 Контакты\n\n"
        "📱 Телефон: +7 999 123-45-67\n"
        "💬 Telegram: @barbergo\n"
        "📍 Адрес: ул. Примерная, 10\n\n"
        "🕐 Работаем ежедневно: 09:00–20:00",
        reply_markup=keyboard,
    )

    await callback.answer()

@router.callback_query(
    BookingForm.entering_name,
    F.data == "back_time"
)
async def back_time_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()

    master = data["master"]
    date = data["date"]

    booked_times = get_booked_times(
        master,
        date
    )

    start_time = datetime.strptime(
        "09:00",
        "%H:%M"
    )

    keyboard_rows = []

    for i in range(22):
        current_time = start_time + timedelta(
            minutes=30 * i
        )

        time_text = current_time.strftime("%H:%M")

        if time_text in booked_times:
            continue

        keyboard_rows.append(
            [
                InlineKeyboardButton(
                    text=time_text,
                    callback_data=f"time_{time_text}"
                )
            ]
        )

    keyboard_rows.append(
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="back_date"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel_booking"
            ),
        ]
    )

    await state.set_state(
        BookingForm.choosing_time
    )

    await callback.message.answer(
        "🕐 Выберите свободное время:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard_rows
        )
    )

    await callback.answer()