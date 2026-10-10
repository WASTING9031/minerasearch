import asyncio
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = os.getenv("BOT_TOKEN")

router = Router()
bot = Bot(token=TOKEN)
dp = Dispatcher()

@router.message(Command("start"))
async def cmd_start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="⚡ minerasearch - канал", url="https://t.me/minerasearch")
    await message.answer("👋 Привет!", reply_markup=kb.as_markup())

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
