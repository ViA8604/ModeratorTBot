from telegram import Update
from telegram.ext import ContextTypes

async def show_user_permissions_options(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("show_user_permissions_options called")
    await query.message.reply_text("Opciones de permisos de usuario.")

async def handle_user_permission_option(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("handle_user_permission_option called")
    pass