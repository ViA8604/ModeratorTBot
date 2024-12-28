from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from config import ADMINS, ASK_CHANNEL_LINK, ADD_BAD_WORD, REMOVE_BAD_WORD
from handlers.bad_words import save_bad_word, confirm_remove_bad_words
from button_handlers import show_administration_menu

async def config_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("config_channel called")
    await update.message.reply_text("Ingrese el link del canal o @ del grupo.")
    return ASK_CHANNEL_LINK

async def ask_channel_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("ask_channel_link called")
    user = update.message.from_user
    group_link = update.message.text

    if group_link.startswith("https://t.me/"):
        group_link = group_link.replace("https://t.me/", "@")

    try:
        chat = await context.bot.get_chat(group_link)
        chat_id = chat.id
        context.user_data['chat_id'] = chat_id

        chat_administrators = await context.bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in chat_administrators]

        if user.id in admin_ids:
            if chat_id not in ADMINS:
                ADMINS[chat_id] = []
            if user.id not in ADMINS[chat_id]:
                ADMINS[chat_id].append(user.id)

            await update.message.reply_text("El canal ha sido configurado correctamente. Ahora puedes administrar este grupo.")
            return ConversationHandler.END
        else:
            await update.message.reply_text("No tienes permisos de administrador en este grupo.")
            return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(f"Error al obtener información del grupo: {e}")
        return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('config_channel', config_channel)],
    states={
        ASK_CHANNEL_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_channel_link)],
        ADD_BAD_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_bad_word)],
        REMOVE_BAD_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_remove_bad_words)],
    },
    fallbacks=[],
    allow_reentry=True
)