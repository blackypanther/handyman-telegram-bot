import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError

# ---- Google GenAI ----
import google.genai as genai

# ---- Logging ----
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---- Environment Variables ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEN_API_KEY = os.environ.get("GEN_API_KEY")

if not TELEGRAM_TOKEN or not GEN_API_KEY:
    logger.error("Environment variables TELEGRAM_TOKEN or GEN_API_KEY not set!")
    exit(1)

# Initialize Google GenAI client
genai.configure(api_key=GEN_API_KEY)

# ---- Command Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Hello! Handyman bot is online and ready.")
    except TelegramError as e:
        logger.error(f"Telegram error in /start: {e}")

async def handyman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)
    if not user_text:
        await update.message.reply_text("Send me something to generate a response.")
        return

    try:
        response = genai.chat.create(
            model="chat-bison-001",
            messages=[{"role": "user", "content": user_text}]
        )
        await update.message.reply_text(response.last.message.content)
    except Exception as e:
        logger.error(f"GenAI error: {e}")
        await update.message.reply_text("Sorry, something went wrong with the AI request.")

# ---- Error Handler ----
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling update:", exc_info=context.error)
    try:
        if isinstance(update, Update) and update.message:
            await update.message.reply_text("An error occurred while processing your request.")
    except Exception as e:
        logger.error(f"Failed to send error message: {e}")

# ---- Main Function ----
def main():
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        # Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("handyman", handyman))
        app.add_error_handler(error_handler)

        # Run
        app.run_polling()
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")

# ---- Entry Point ----
if __name__ == "__main__":
    main()
