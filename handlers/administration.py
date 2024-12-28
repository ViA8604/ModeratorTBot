from telegram import Update
from telegram.ext import ContextTypes
from config import ADMINS
from button_handlers import show_administration_menu

async def administrate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("administrate called")
    user_id = update.message.from_user.id
    chat_id = context.user_data.get('chat_id')

    if not chat_id:
        await update.message.reply_text("No has configurado ningún grupo para administrar. Usa /config_channel para configurar un grupo.")
        return

    if chat_id not in ADMINS or user_id not in ADMINS[chat_id]:
        await update.message.reply_text("No tienes permisos de administrador en este grupo.")
        return

    await show_administration_menu(update, context)
