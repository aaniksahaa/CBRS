import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from utils import * 

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define a command handler function
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! I am monitoring this group. Say "hello" and I will reply with "hi".')

# Define a message handler function to respond to "hello"
async def respond_hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text.lower()
    if 'hello' in user_text:
        await update.message.reply_text('hi')

def main():
    # Replace 'YOUR TOKEN HERE' with your bot's API token
    application = ApplicationBuilder().token(TG_TOKEN).build()

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Register the message handler for responding to "hello"
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond_hello))

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
