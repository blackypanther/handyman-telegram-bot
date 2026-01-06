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
TELEGRAM_TOKEN = "8587188130:AAFtzw5ig_V9wzunCpUk8HiZBaMcSDQ6yAo"
GEN_API_KEY = "gen-lang-client-0404387219"

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

    data = user_state[user_id]

    # Save answer
    for key, _ in QUESTIONS:
        if key not in data:
            data[key] = update.message.text
            break

    # Ask next question
    if len(data) < len(QUESTIONS):
        await update.message.reply_text(
            QUESTIONS[len(data)][1]
        )
        return

    # ------------------------------
    # AI BRAIN (GEMINI)
    # ------------------------------
    prompt = f"""
You are a professional handyman dispatcher.

Customer request:
Issue: {data['issue']}
Location: {data['location']}
Preferred time: {data['time']}
Budget: {data['budget']}
Extra details: {data['details']}

Return:
- Service category
- Urgency (Low / Medium / High)
- One-line job summary
"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        await update.message.reply_text(
            "✅ Request logged successfully.\n\n"
            f"{response.text}\n\n"
            "Our team will contact you shortly."
        )

    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        await update.message.reply_text(
            "❌ Sorry, there was a system issue, but your request has been recorded."
        )

    # Reset memory after completion
    user_state.pop(user_id, None)

# ------------------------------
# MAIN
# ------------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Handyman bot running...")
    app.run_polling()
