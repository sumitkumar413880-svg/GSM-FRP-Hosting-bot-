import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from models.database import create_tables

from config import BOT_TOKEN
from handlers.start import start
from handlers.help import help_command
from handlers.user_management import register_start, register_email, register_password, login_start, login_password, profile, cancel, REGISTER_EMAIL, REGISTER_PASSWORD, LOGIN_EMAIL, LOGIN_PASSWORD
from handlers.service_management import services, buy_service_callback, my_orders, balance
from handlers.payment import add_credits_start, add_credits_amount, cancel_payment, ADD_CREDITS_AMOUNT
from handlers.admin_commands import admin_start, admin_menu_selection, manage_users_selection, manage_services_selection, add_service_name, add_service_desc, add_service_price, edit_service_select, edit_service_field, edit_service_value, delete_service_select, broadcast_message, admin_cancel, ADMIN_MENU, MANAGE_USERS, MANAGE_SERVICES, ADD_SERVICE_NAME, ADD_SERVICE_DESC, ADD_SERVICE_PRICE, EDIT_SERVICE_SELECT, EDIT_SERVICE_FIELD, EDIT_SERVICE_VALUE, DELETE_SERVICE_SELECT, BROADCAST_MESSAGE

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot\\'s token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile))

    # Conversation handler for registration
    reg_handler = ConversationHandler(
        entry_points=[CommandHandler("register", register_start)],
        states={
            REGISTER_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(reg_handler)

    # Conversation handler for login
    login_handler = ConversationHandler(
        entry_points=[CommandHandler("login", login_start)],
        states={
            LOGIN_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
            LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, login_password)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(login_handler)

    # Service management handlers
    application.add_handler(CommandHandler("services", services))
    application.add_handler(CommandHandler("myorders", my_orders))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CallbackQueryHandler(buy_service_callback, pattern=\"^buy_service_\"))

    # Conversation handler for adding credits
    add_credits_handler = ConversationHandler(
        entry_points=[CommandHandler("addcredits", add_credits_start)],
        states={
            ADD_CREDITS_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_credits_amount)],
        },
        fallbacks=[CommandHandler("cancel", cancel_payment)],
    )
    application.add_handler(add_credits_handler)

    # Admin conversation handler
    admin_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_start)],
        states={
            ADMIN_MENU: [
                MessageHandler(filters.Regex("^(Manage Users|Manage Services|Broadcast Message|Cancel)$"), admin_menu_selection)
            ],
            MANAGE_USERS: [
                MessageHandler(filters.Regex("^(List Users|Back to Admin Menu)$"), manage_users_selection)
            ],
            MANAGE_SERVICES: [
                MessageHandler(filters.Regex("^(Add Service|Edit Service|Delete Service|List Services|Back to Admin Menu)$"), manage_services_selection)
            ],
            ADD_SERVICE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_service_name)],
            ADD_SERVICE_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_service_desc)],
            ADD_SERVICE_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_service_price)],
            EDIT_SERVICE_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_service_select)],
            EDIT_SERVICE_FIELD: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_service_field)],
            EDIT_SERVICE_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_service_value)],
            DELETE_SERVICE_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, delete_service_select)],
            BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message)],
        },
        fallbacks=[CommandHandler("cancel", admin_cancel), MessageHandler(filters.Regex("^(Cancel)$"), admin_cancel)],
    )
    application.add_handler(admin_handler)

    # Run the bot until the user presses Ctrl-C
    create_tables()
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()


