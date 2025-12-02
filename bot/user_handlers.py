from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from rag.global_rag import rag

router = Router()


def register_user_handlers(dp):
    dp.include_router(router)

    # /start
    @router.message(Command("start"))
    async def start(message: Message):
        await message.answer(
            "Hi! I'm a RAG-bot. You can ask me questions about Python documentation!"
        )

    #  USER QUERY
    @router.message(F.text & ~F.command)
    async def answer(message: Message):
        query = message.text
        await message.answer("Searching the answer...")

        response = rag.query(query)
        await message.answer(response)
