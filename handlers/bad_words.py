from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from config import BAD_WORDS, ADD_BAD_WORD, BANNED_USERS, REMOVE_BAD_WORD, WARNINGS

def initialize_bad_words(chat_id):
    if chat_id not in BAD_WORDS:
        BAD_WORDS[chat_id] = []

# Define handle_message if it is related to bad words
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("handle_message called")
    chat_id = update.message.chat_id
    user = update.message.from_user
    text = update.message.text

    print(f"Mensaje recibido en el grupo {chat_id} de {user.username}: {text}")
    print(f"Estado actual: {context.user_data.get('state')}")

    # Diccionario para mapear estados a funciones
    state_functions = {
        ADD_BAD_WORD: save_bad_word,
        REMOVE_BAD_WORD: confirm_remove_bad_words
    }

    # Verificar si el estado de la conversación está en el diccionario y llamar a la función correspondiente
    state = context.user_data.get('state')
    if state in state_functions:
        print(f"Llamando a la función para el estado: {state}")
        await state_functions[state](update, context)
        return

    # Comprobar si el grupo tiene una lista de palabras no aceptadas
    if chat_id in BAD_WORDS:
        print(f"Palabras no aceptadas en el grupo {chat_id}: {BAD_WORDS[chat_id]}")
        if any(bad_word.lower() in text.lower() for bad_word in BAD_WORDS[chat_id]):
            user_id = user.id
            username = user.username

            # Incrementar el conteo de advertencias
            if user_id in WARNINGS:
                WARNINGS[user_id] += 1
            else:
                WARNINGS[user_id] = 1

            # Enviar advertencia
            await update.message.reply_text(f"Advertencia {WARNINGS[user_id]} para @{username}. No uses palabras no aceptadas.")

            # Si el usuario tiene 2 advertencias, eliminarlo del grupo
            if WARNINGS[user_id] >= 2:
                BANNED_USERS.append(user_id)
                await context.bot.kick_chat_member(chat_id, user_id)
                await update.message.reply_text(f"@{username} ha sido eliminado del grupo por usar palabras no aceptadas.")
        else:
            print("No se encontraron palabras no aceptadas en el mensaje.")
    else:
        print(f"No hay palabras no aceptadas configuradas para el grupo {chat_id}.")

async def show_bad_words_options(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("show_bad_words_options called")
    keyboard = [
        [InlineKeyboardButton("Añadir palabra", callback_data='bad_word_option_add')],
        [InlineKeyboardButton("Eliminar palabra", callback_data='bad_word_option_remove')],
        [InlineKeyboardButton("Ver lista de palabras", callback_data='bad_word_option_list')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Seleccione una opción para administrar palabras prohibidas:", reply_markup=reply_markup)

async def handle_bad_word_option(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("handle_bad_word_option called")
    if query.data == 'bad_word_option_add':
        await query.edit_message_text(text="Añadir palabra seleccionado.")
        await add_bad_words(query, context)
    elif query.data == 'bad_word_option_remove':
        await query.edit_message_text(text="Eliminar palabra seleccionado.")
        await remove_bad_words(query, context)
    elif query.data == 'bad_word_option_list':
        await query.edit_message_text(text="Ver lista de palabras seleccionado.")
        await get_bad_words_list(query, context)

async def add_bad_words(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("add_bad_words called")
    chat_id = context.user_data.get('chat_id')
    initialize_bad_words(chat_id)
    await query.message.reply_text("Ingrese las palabras que desea añadir a la lista de palabras no aceptadas, separadas por comas.")
    context.user_data['state'] = ADD_BAD_WORD
    return ADD_BAD_WORD

async def save_bad_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("save_bad_word called")
    chat_id = context.user_data.get('chat_id')
    initialize_bad_words(chat_id)
    new_words = [word.strip() for word in update.message.text.split(',') if word.strip()]
    added_words = []
    existing_words = []
    for word in new_words:
        if word not in BAD_WORDS[chat_id]:
            BAD_WORDS[chat_id].append(word)
            added_words.append(word)
        else:
            existing_words.append(word)
    if added_words:
        await update.message.reply_text(f"Las palabras '{', '.join(added_words)}' han sido añadidas a la lista de palabras no aceptadas.")
    if existing_words:
        await update.message.reply_text(f"Las palabras '{', '.join(existing_words)}' ya están en la lista de palabras no aceptadas.")
    context.user_data['state'] = None
    return ConversationHandler.END

async def remove_bad_words(query, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("remove_bad_words called")
    chat_id = context.user_data.get('chat_id')
    initialize_bad_words(chat_id)
    if BAD_WORDS[chat_id]:
        await query.message.reply_text("Ingrese las palabras que desea eliminar de la lista de palabras no aceptadas, separadas por comas.")
        context.user_data['state'] = REMOVE_BAD_WORD
        return REMOVE_BAD_WORD
    else:
        await query.message.reply_text("No hay palabras no aceptadas en este grupo.")
        return ConversationHandler.END

async def confirm_remove_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    print("confirm_remove_bad_words called")
    chat_id = context.user_data.get('chat_id')
    initialize_bad_words(chat_id)
    words_to_remove = [word.strip() for word in update.message.text.split(',') if word.strip()]
    removed_words = []
    not_found_words = []
    for word in words_to_remove:
        if word in BAD_WORDS[chat_id]:
            BAD_WORDS[chat_id].remove(word)
            removed_words.append(word)
        else:
            not_found_words.append(word)
    if removed_words:
        await update.message.reply_text(f"Las palabras '{', '.join(removed_words)}' han sido eliminadas de la lista de palabras no aceptadas.")
    if not_found_words:
        await update.message.reply_text(f"Las palabras '{', '.join(not_found_words)}' no se encontraron en la lista de palabras no aceptadas.")
    context.user_data['state'] = None
    return ConversationHandler.END

async def get_bad_words_list(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("get_bad_words_list called")
    chat_id = context.user_data.get('chat_id')
    initialize_bad_words(chat_id)
    if BAD_WORDS[chat_id]:
        await query.message.reply_text(f"Lista de palabras no aceptadas: {', '.join(BAD_WORDS[chat_id])}")
    else:
        await query.message.reply_text("No hay palabras no aceptadas en este grupo.")