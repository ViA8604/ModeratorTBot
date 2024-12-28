import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from handlers.bad_words import show_bad_words_options, handle_bad_word_option
from handlers.user_permissions import show_user_permissions_options, handle_user_permission_option
from handlers.payments import handle_payment

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("button llamado")
    query = update.callback_query
    await query.answer()

    callback_actions = {
        'manage_bad_words': show_bad_words_options,
        'manage_user_permissions': show_user_permissions_options,
        'payment': handle_payment,
    }

    if query.data in callback_actions:
        await query.edit_message_text(text=f"{query.data.replace('_', ' ').capitalize()} seleccionado.")
        await callback_actions[query.data](query, context)
    elif query.data.startswith('bad_word_option'):
        await handle_bad_word_option(query, context)
    elif query.data.startswith('user_permission_option'):
        await handle_user_permission_option(query, context)

async def show_administration_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("show_administration_menu called")
    keyboard = [
        [InlineKeyboardButton("Administrar palabras prohibidas", callback_data='manage_bad_words')],
        [InlineKeyboardButton("Administrar permisos de usuarios", callback_data='manage_user_permissions')],
        [InlineKeyboardButton("Pago", callback_data='payment')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Seleccione una opción para administrar:", reply_markup=reply_markup)