import asyncio
import os
import aiohttp
import sqlite3
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = "osint.db"

router = Router()
bot = Bot(token=TOKEN)
dp = Dispatcher()

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                user_id INTEGER,
                query_type TEXT,
                target TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

async def fetch_ip_info(ip: str) -> str:
    url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,isp,org,as,query"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return "Failed to query IP provider."
            data = await resp.json()
            if data.get("status") != "success":
                return f"Lookup failed: {data.get('message', 'unknown error')}"
            
            return (
                f"[*] IP Info: {data.get('query')}\n"
                f"Country: {data.get('country')}\n"
                f"Region: {data.get('regionName')}, {data.get('city')}\n"
                f"ISP: {data.get('isp')}\n"
                f"Org: {data.get('org')}\n"
                f"AS: {data.get('as')}"
            )

async def fetch_phone_info(phone: str) -> str:
    return f"[*] Phone lookup parsed for: {phone}\nCarrier: SampleCarrier\nCountry: RU/CIS"

@router.message(Command("start"))
async def cmd_start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="⚡ minerasearch - канал", url="https://t.me/minerasearch")
    await message.answer("👋 Привет!", reply_markup=kb.as_markup())

@router.message(F.text)
async def handle_target(message: Message):
    target = message.text.strip()
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO history (user_id, query_type, target) VALUES (?, ?, ?)", 
                     (message.from_user.id, "generic", target))
        conn.commit()

    if target.replace(".", "").isdigit() and len(target.split(".")) == 4:
        result = await fetch_ip_info(target)
    elif target.startswith("+") or target.isdigit():
        result = await fetch_phone_info(target)
    else:
        result = f"[*] Target registered: {target}\nSearching public sources..."

    await message.answer(result)

async def main():
    init_db()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
