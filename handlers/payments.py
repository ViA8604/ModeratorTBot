from telegram import Update
from telegram.ext import ContextTypes

async def handle_payment(query, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("handle_payment called")
    pass