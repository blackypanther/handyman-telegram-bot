import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---- Google GenAI ----
# Make sure you installed: pip install google-genai
import google.genai as genai

# ---- Logging ----
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---- Environment Variables ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEN_API_KEY = os.environ.get("GEN_API_KEY")

# Initialize Google GenAI client
genai.configure(api_key=GEN_API_KEY)

# ---- Command Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Handyman bot is online and ready.")

async def handyman(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Example: simple AI response
    user_text = " ".join(context.args)
    if not user_text:
        await update.message.reply_text("Send me something to generate a response.")
        return

    response = genai.chat.create(
        model="chat-bison-001",
        messages=[{"role": "user", "content": user_text}]
    )

    await update.message.reply_text(response.last.message.content)

# ---- Main Function ----
def main():
    # Build the bot
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("handyman", handyman))

    # Run the bot
    app.run_polling()

# ---- Entry Point ----
if __name__ == "__main__":
    main()
