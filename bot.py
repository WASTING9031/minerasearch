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

TRANSLATIONS = {
    "ru": {
        "start": "👋 Привет!"
    },
    "en": {
        "start": "👋 Hello!"
    }
}

@router.message(Command("start"))
async def cmd_start(message: Message):
    lang = user_langs.get(message.from_user.id, "ru")
    kb = InlineKeyboardBuilder()
    kb.button(text="⚡ minerasearch - канал", url="https://t.me/minerasearch")
    await message.answer(TRANSLATIONS[lang]["start"], reply_markup=kb.as_markup())

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
    await call.answer()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
