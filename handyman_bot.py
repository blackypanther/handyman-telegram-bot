import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError

# ---- Google Gemini (current SDK in 2026) ----
import google.generativeai as genai

# ---- Logging ----
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---- Environment Variables ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEN_API_KEY    = os.environ.get("GEN_API_KEY")

if not TELEGRAM_TOKEN or not GEN_API_KEY:
    logger.critical("Environment variables TELEGRAM_TOKEN or GEN_API_KEY not set!")
    exit(1)

# ---- Configure Gemini ----
genai.configure(api_key=GEN_API_KEY)

# Recommended lightweight & fast model in 2026 (good balance of speed & quality)
MODEL_NAME = "gemini-2.5-flash"           # or "gemini-3-pro" for maximum quality
model = genai.GenerativeModel(MODEL_NAME)

# ---- Command Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("Hello! Handyman bot is online and ready 🚀")
    except TelegramError as e:
        logger.error(f"Telegram error in /start: {e}")

async def handyman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)
    if not user_text:
        await update.message.reply_text("Please provide a question or task after /handyman")
        return

    try:
        # Modern way — simple generate_content call
        response = model.generate_content(user_text)
        reply_text = response.text

        # Optional: clean up if you want to remove markdown artifacts etc.
        # reply_text = reply_text.replace("**", "*").replace("__", "_")

        await update.message.reply_text(reply_text)
    except Exception as e:
        logger.error(f"Gemini error: {e}", exc_info=True)
        await update.message.reply_text("Sorry, something went wrong with the AI. Try again later.")

# ---- Error Handler ----
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(msg="Exception while handling update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text("An unexpected error occurred 😓")
        except Exception as send_err:
            logger.error(f"Failed to send error message: {send_err}")

# ---- Main ----
def main():
    try:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("handyman", handyman))

        app.add_error_handler(error_handler)

        print("Bot is starting... (using polling)")
        app.run_polling(
            drop_pending_updates=True,   # Recommended in production
            poll_interval=0.8,
            timeout=15
        )
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}", exc_info=True)

if __name__ == "__main__":
    main()
