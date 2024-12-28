from telegram import Update
from telegram.ext import ContextTypes
from bad_words import confirm_remove_bad_words, save_bad_word
from config import ADD_BAD_WORD, BAD_WORDS, REMOVE_BAD_WORD, WARNINGS, BANNED_USERS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('¡Hola! Soy tu bot de moderación.')

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
        if any(bad_word in text.lower() for bad_word in BAD_WORDS[chat_id]):
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