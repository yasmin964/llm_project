import os
from aiogram import Router, types, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from bot.keyboards import admin_menu_kb
from rag.global_rag import rag
from bot.admin_storage import add_admin, remove_admin, get_admins, is_admin
from rag.config import DOCS_DIR

router = Router()

waiting_for_password = set()


def register_admin_handlers(dp, ADMIN_ID):
    dp.include_router(router)

    @router.message(Command("admin"))
    async def admin_panel(message: Message):
        await message.answer(
            "🛠 <b>Admin Panel</b>",
            reply_markup=admin_menu_kb(message.from_user.id)
        )

    # ADD DOCUMENT
    @router.callback_query(F.data == "add_doc")
    async def wait_for_doc(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            return await callback.answer("⛔ No access")
        await callback.message.answer("📄 Send PDF document.")
        await callback.answer()

    @router.message(F.document)
    async def handle_doc_upload(message: Message):
        if not is_admin(message.from_user.id):
            return

        file = await message.bot.get_file(message.document.file_id)
        file_path = f"{DOCS_DIR}/{message.document.file_name}"
        await message.bot.download_file(file.file_path, file_path)

        await message.answer("📥 Document uploaded. Processing and building index...")

        success = rag.add_document(file_path)

        if success:
            await message.answer("✅ Document added and index rebuilt! You can now ask questions about this document.")
        else:
            await message.answer("❌ Error processing document. Please try again.")

    #  DELETE DOCUMENT
    @router.callback_query(F.data == "delete_doc")
    async def delete_doc_menu(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            return await callback.answer("⛔ No access")

        files = os.listdir(DOCS_DIR)
        if not files:
            return await callback.message.answer("No documents.")

        kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=f, callback_data=f"del:{f}")]
                for f in files
            ]
        )
        await callback.message.answer("Select document:", reply_markup=kb)
        await callback.answer()

    @router.callback_query(F.data.startswith("del:"))
    async def confirm_delete(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            return await callback.answer("⛔ No access")

        filename = callback.data.split("del:")[1]
        os.remove(f"{DOCS_DIR}/{filename}")
        await callback.message.answer(f"❌ Deleted: {filename}")
        await callback.answer()

    #  LIST DOCS
    @router.callback_query(F.data == "list_docs")
    async def list_docs(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            return await callback.answer("⛔ No access")

        files = os.listdir(DOCS_DIR)
        msg = "\n".join([f"📄 {f}" for f in files]) or "No documents"
        await callback.message.answer(msg)
        await callback.answer()

    #  REBUILD INDEX
    @router.callback_query(F.data == "rebuild_index")
    async def rebuild(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            return await callback.answer("⛔ No access")

        await callback.message.answer("🔄 Rebuilding index...")
        rag.rebuild_index()
        await callback.message.answer("✅ Done!")
        await callback.answer()

    #  BECOME ADMIN
    @router.callback_query(F.data == "become_admin")
    async def process_become_admin(callback: CallbackQuery):
        await callback.message.answer("Enter administrator password:")
        waiting_for_password.add(callback.from_user.id)
        await callback.answer()

    @router.message(F.text, lambda message: message.from_user.id in waiting_for_password)
    async def check_password(message: Message):
        if message.text == "secret":
            add_admin(message.from_user.id)
            await message.answer("🎉 You are now an administrator!")

            await message.answer(
                "🛠 <b>Admin Panel Updated</b>",
                reply_markup=admin_menu_kb(message.from_user.id)
            )
        else:
            await message.answer("❌ Wrong password.")
        waiting_for_password.remove(message.from_user.id)

    #  REMOVE MY ADMIN RIGHTS
    @router.callback_query(F.data == "remove_my_admin")
    async def remove_my_admin(callback: CallbackQuery):
        if not is_admin(callback.from_user.id):
            return await callback.answer("⛔ You are not an admin")

        remove_admin(callback.from_user.id)
        await callback.message.answer("🔓 Your admin rights have been removed!")

        await callback.message.edit_reply_markup(
            reply_markup=admin_menu_kb(callback.from_user.id)
        )
        await callback.answer()