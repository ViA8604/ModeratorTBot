from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from conversation_handlers import conv_handler
from button_handlers import button
from handlers import handle_message, administrate
from config import TOKEN

def main():
    print("Bot iniciado")
    application = Application.builder().token(TOKEN).build()

    # Agrega el manejador de conversación primero
    application.add_handler(conv_handler)

    # Agrega el manejador para el comando /administrate
    application.add_handler(CommandHandler('administrate', administrate))
    
    # Maneja los callbacks de los botones
    application.add_handler(CallbackQueryHandler(button))

    # Maneja todos los mensajes del grupo
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Inicia el bot
    application.run_polling()

if __name__ == '__main__':
    main()