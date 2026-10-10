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
        "btn_fio": "🔍 Поиск по ФИО и соцсетям",
        "enter_fio": "Введите ФИО и возраст (например: Иванов Иван 25):",
        "searching": "[*] Сканирование соцсетей (VK, Facebook, OK, Telegram)...",
        "not_found": "[-] Ничего не найдено."
    },
    "en": {
        "start": "👋 Hello!",
        "menu_title": "📂 Main menu:",
        "btn_fio": "🔍 Full Name & Socials Search",
        "enter_fio": "Enter full name and age (e.g., John Smith 25):",
        "searching": "[*] Scanning social networks...",
        "not_found": "[-] Nothing found."
    }
}

async def search_socials(query: str) -> str:
    encoded_q = query.replace(" ", "+")
    
    vk_link = f"https://vk.com/search?c[section]=people&c[q]={encoded_q}"
    ok_link = f"https://ok.ru/search?st.query={encoded_q}"
    fb_link = f"https://www.facebook.com/public/{encoded_q}"
    
    parts = query.split()
    first_name = parts[0] if parts else query

    results = (
        f"🔍 <b>Результаты поиска для:</b> {query}\n\n"
        f"🌐 <b>VKontakte:</b>\n"
        f"• <a href='{vk_link}'>Открыть профили и фильтр по возрасту в VK</a>\n\n"
        f"🟢 <b>Одноклассники:</b>\n"
        f"• <a href='{ok_link}'>Открыть поиск в Одноклассниках</a>\n\n"
        f"📘 <b>Facebook:</b>\n"
        f"• <a href='{fb_link}'>Открыть публичный поиск Facebook</a>\n\n"
        f"💬 <b>Telegram:</b>\n"
        f"• <a href='https://t.me/{first_name}'>@{first_name}</a>"
    )
    return results

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
        
        msg = await message.answer(TRANSLATIONS[lang]["searching"])
        await asyncio.sleep(0.5)
        
        result = await search_socials(query)
        await msg.edit_text(result, parse_mode="HTML", disable_web_page_preview=True)

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
