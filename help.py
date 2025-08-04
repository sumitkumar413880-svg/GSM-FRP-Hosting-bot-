from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
🔧 GSM FRP Hosting Bot Commands:

📋 General Commands:
/start - Start the bot
/help - Show this help message
/register - Register a new account
/login - Login to your account
/profile - View your profile

🛒 Services:
/services - View available FRP services
/buy <service_id> - Purchase a service
/myorders - View your order history
/balance - Check your credit balance
/addcredits - Add credits to your account

👨‍💼 Admin Commands (Admin only):
/admin - Access admin panel

Need help? Contact support!
    """
    await update.message.reply_text(help_text)

