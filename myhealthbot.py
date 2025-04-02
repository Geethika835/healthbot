import os
import google.generativeai as genai
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate API keys
if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or GEMINI_API_KEY! Check your .env file.")

# Initialize Gemini client
genai.configure(api_key=GEMINI_API_KEY)
# Set the default Gemini model here. You can choose a model known for free tier,
# like one containing "flash" in its name, or a generally capable model.
# Check the output of `genai.list_models()` to see available options.
DEFAULT_GEMINI_MODEL = 'gemini-2.0-flash-lite'  # Or try 'gemini-pro-vision' if you want multimodal
try:
    gemini_model = genai.GenerativeModel(DEFAULT_GEMINI_MODEL)
except Exception as e:
    print(f"Error initializing model {DEFAULT_GEMINI_MODEL}: {e}")
    gemini_model = None

async def get_health_response(question):
    """Fetch health-related answers using Gemini API"""
    if gemini_model is None:
        return f"Error: Could not initialize the Gemini model ({DEFAULT_GEMINI_MODEL}). Please check the logs."
    try:
        response = gemini_model.generate_content(
            [{"role": "user", "parts": [question]}],
            stream=False  # Set to True for streaming responses
        )
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

async def send_long_message(update: Update, text: str, chunk_size: int = 4000) -> None:
    """Sends a long message by splitting it into chunks."""
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        await update.message.reply_text(chunk)

async def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command"""
    await update.message.reply_text(f"Hello! I am your AI Health Assistant powered by Gemini ({DEFAULT_GEMINI_MODEL}). Ask me anything about health.")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle user messages"""
    user_text = update.message.text
    response = await get_health_response(user_text)
    await send_long_message(update, response)

def main():
    """Start the bot"""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start))

    # Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
    