from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.admin_storage import is_admin


def admin_menu_kb(user_id: int):

    base_buttons = [
        [InlineKeyboardButton(text="👑 Become Admin", callback_data="become_admin")],
    ]

    if is_admin(user_id):
        admin_buttons = [
            [InlineKeyboardButton(text="📄 Add Document", callback_data="add_doc")],
            [InlineKeyboardButton(text="❌ Remove Document", callback_data="delete_doc")],
            [InlineKeyboardButton(text="📚 List Documents", callback_data="list_docs")],
            [InlineKeyboardButton(text="🔄 Rebuild Index", callback_data="rebuild_index")],
            [InlineKeyboardButton(text="➖ Remove Admin Rights", callback_data="remove_my_admin")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=admin_buttons + base_buttons)
    else:
        # Показываем только кнопку для становления админом
        return InlineKeyboardMarkup(inline_keyboard=base_buttons)