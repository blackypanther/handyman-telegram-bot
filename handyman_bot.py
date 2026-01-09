import os

# handyman_bot.py
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import google.generativeai as genai


# ------------------------------
# CONFIG
# ------------------------------
TELEGRAM_TOKEN = "your Telegram bot token"
GEN_API_KEY = "your Gemini API key"

genai.configure(api_key=GEN_API_KEY)
model = genai.GenerativeModel("gemini-pro")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------------
# MEMORY (BOT BRAIN)
# ------------------------------
user_state = {}

QUESTIONS = [
    ("issue", "Please describe the issue you need help with."),
    ("location", "Thanks. What is the **location** of the issue?"),
    ("time", "What is your **preferred time** for the handyman to arrive?"),
    ("budget", "What is your **budget** for this job?"),
    ("details", "Any **additional details** we should know?")
]

GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

# ------------------------------
# START
# ------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_state[update.effective_user.id] = {}
    await update.message.reply_text(
        "Welcome to Handyman Company Services.\n"
        "I’ll help you log a service request."
    )
    await update.message.reply_text(QUESTIONS[0][1])

# ------------------------------
# MESSAGE HANDLER
# ------------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    # Greeting handling
    if text in GREETINGS:
        await update.message.reply_text(
            "Hello! 👋 I can help you with handyman services.\n"
            "Please tell me what issue you need help with."
        )
        return

    if user_id not in user_state:
        user_state[user_id] = {}
import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import google.generativeai as genai  # Deprecated package, works for now

# -------------------------------
# CONFIGURATION
# -------------------------------

# Load tokens from environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEN_API_KEY = os.environ.get("GEN_API_KEY")

# Configure Google Generative AI
genai.configure(api_key=GEN_API_KEY)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------------------
# COMMAND HANDLERS
# -------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Handyman bot is online! Send /help for commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    help_text = (
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/generate <prompt> - Generate AI response\n"
    )
    await update.message.reply_text(help_text)

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a response from Google Generative AI."""
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Please provide a prompt after /generate!")
        return

    try:
        # Example using text-bison-001 (adjust model if needed)
        response = genai.text.generate(
            model="models/text-bison-001",
            prompt=prompt
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Error generating AI response: {e}")
        await update.message.reply_text("Failed to generate response. Try again later.")

# -------------------------------
# MAIN
# -------------------------------

def main():
    """Start the bot."""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("generate", generate))

    # Run the bot
    app.run_polling()

# -------------------------------
# ENTRY POINT
# -------------------------------

if __name__ == "__main__":
    main()
