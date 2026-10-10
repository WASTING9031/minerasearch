import asyncio
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")

router = Router()
bot = Bot(token=TOKEN)
dp = Dispatcher()

user_langs = {}
user_states = {}

TRANSLATIONS = {
    "ru": {
        "start": "👋 Привет!",
        "menu_title": "📂 Главное меню:",
        "btn_fio": "🔍 Поиск по ФИО",
        "enter_fio": "Введите ФИО для поиска:",
        "searching": "[*] Выполняется кросс-платформенный поиск..."
    },
    "en": {
        "start": "👋 Hello!",
        "menu_title": "📂 Main menu:",
        "btn_fio": "🔍 Full Name Search",
        "enter_fio": "Enter full name to search:",
        "searching": "[*] Running cross-platform search..."
    }
}

@router.message(Command("start"))
async def cmd_start(message: Message):
    lang = user_langs.get(message.from_user.id, "ru")
    kb = InlineKeyboardBuilder()
    kb.button(text="⚡ minerasearch - канал", url="https://t.me/minerasearch")
    await message.answer(TRANSLATIONS[lang]["start"], reply_markup=kb.as_markup())

@router.message(Command("menu"))
async def cmd_menu(message: Message):
    lang = user_langs.get(message.from_user.id, "ru")
    kb = InlineKeyboardBuilder()
    kb.button(text=TRANSLATIONS[lang]["btn_fio"], callback_data="menu_fio")
    kb.adjust(1)
    await message.answer(TRANSLATIONS[lang]["menu_title"], reply_markup=kb.as_markup())

@router.callback_query(F.data == "menu_fio")
async def callback_menu_fio(call: CallbackQuery):
    lang = user_langs.get(call.from_user.id, "ru")
    user_states[call.from_user.id] = "waiting_fio"
    await call.message.answer(TRANSLATIONS[lang]["enter_fio"])
    await call.answer()

@router.message(Command("lang"))
async def cmd_lang(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Русский", callback_data="lang_ru")
    kb.button(text="English", callback_data="lang_en")
    kb.adjust(2)
    custom_emoji = '<tg-emoji id="5447410659077661506">🌐</tg-emoji>'
    await message.answer(f"{custom_emoji} Выберите язык / Choose language:", reply_markup=kb.as_markup(), parse_mode="HTML")

@router.callback_query(F.data.startswith("lang_"))
async def callback_lang(call: CallbackQuery):
    lang = call.data.split("_")[1]
    user_langs[call.from_user.id] = lang
    user_states.pop(call.from_user.id, None)
    await call.answer()

@router.message(F.text)
async def handle_text(message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)
    lang = user_langs.get(user_id, "ru")

    if state == "waiting_fio":
        user_states.pop(user_id, None)
        query = message.text.strip()
        await message.answer(TRANSLATIONS[lang]["searching"])
        
        result = (
            f"🔍 Результаты поиска для: {query}\n\n"
            f"📱 Телефон: +7 (999) ***-**-42\n"
            f"💬 Telegram: @sample_user\n"
            f"🆔 Telegram ID: 5837405541\n"
            f"🌐 VK: vk.com/id00000000\n"
            f"📘 Facebook: facebook.com/sample\n"
            f"🟢 Одноклассники: ok.ru/profile/000000\n"
            f"💬 MAX: найдено совпадение"
        )
        await message.answer(result)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
