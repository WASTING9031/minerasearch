import asyncio
import os
import sqlite3
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = "osint.db"

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
        "not_found": "[-] Ничего не найдено."
    },
    "en": {
        "start": "👋 Hello!",
        "menu_title": "📂 Main menu:",
        "btn_fio": "🔍 Full Name Search",
        "enter_fio": "Enter full name to search:",
        "not_found": "[-] Nothing found."
    }
}

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT,
                phone TEXT,
                telegram TEXT,
                tg_id TEXT,
                vk TEXT,
                facebook TEXT,
                ok TEXT,
                max TEXT
            )
        """)
        conn.commit()

def search_db(query: str) -> str:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT phone, telegram, tg_id, vk, facebook, ok, max 
            FROM targets 
            WHERE fio LIKE ? OR phone LIKE ? OR telegram LIKE ?
        """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        
        if not rows:
            return ""
        
        output = []
        for r in rows:
            output.append(
                f"🔍 Найдено совпадение:\n"
                f"📱 Телефон: {r[0] or 'нет'}\n"
                f"💬 Telegram: @{r[1] or 'нет'}\n"
                f"🆔 Telegram ID: {r[2] or 'нет'}\n"
                f"🌐 VK: {r[3] or 'нет'}\n"
                f"📘 Facebook: {r[4] or 'нет'}\n"
                f"🟢 Одноклассники: {r[5] or 'нет'}\n"
                f"💬 MAX: {r[6] or 'нет'}"
            )
        return "\n\n".join(output)

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
        
        result = search_db(query)
        if not result:
            result = TRANSLATIONS[lang]["not_found"]
            
        await message.answer(result)

async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
