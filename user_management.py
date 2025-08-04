from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from models.database import User, get_db
from sqlalchemy.exc import IntegrityError
import bcrypt

# States for conversation handler
REGISTER_EMAIL, REGISTER_PASSWORD, LOGIN_EMAIL, LOGIN_PASSWORD = range(4)

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the registration conversation."""
    await update.message.reply_text(
        "To register, please send me your email address."
    )
    return REGISTER_EMAIL

async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the email and asks for a password."""
    user_email = update.message.text
    context.user_data["register_email"] = user_email
    await update.message.reply_text(
        "Now, please choose a password."
    )
    return REGISTER_PASSWORD

async def register_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the password, hashes it, and creates the user."""
    user_password = update.message.text
    email = context.user_data["register_email"]
    
    hashed_password = bcrypt.hashpw(user_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with next(get_db()) as db:
        try:
            new_user = User(
                user_id=update.effective_user.id,
                username=update.effective_user.username,
                email=email,
                password_hash=hashed_password,
                balance=0.0,
                is_admin=False
            )
            db.add(new_user)
            db.commit()
            await update.message.reply_text(
                "Registration successful! You can now use /login to access your account.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END
        except IntegrityError:
            db.rollback()
            await update.message.reply_text(
                "An account with this Telegram ID or email already exists. Please use /login or /start if you are already registered.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END
        except Exception as e:
            db.rollback()
            await update.message.reply_text(
                f"An error occurred during registration: {e}. Please try again.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the login conversation."""
    await update.message.reply_text(
        "To log in, please send me your registered email address."
    )
    return LOGIN_EMAIL

async def login_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the email for login and asks for password."""
    user_email = update.message.text
    context.user_data["login_email"] = user_email
    await update.message.reply_text(
        "Please send your password."
    )
    return LOGIN_PASSWORD

async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Authenticates the user with provided email and password."""
    user_password = update.message.text
    email = context.user_data["login_email"]

    with next(get_db()) as db:
        user = db.query(User).filter(User.email == email).first()

        if user and bcrypt.checkpw(user_password.encode("utf-8"), user.password_hash.encode("utf-8")):
            # For simplicity, we\'ll just store user_id in context.user_data for session management
            # In a real application, you might use more robust session management.
            context.user_data["logged_in_user_id"] = user.user_id
            await update.message.reply_text(
                f"Welcome back, {user.username or user.email}! You are now logged in.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "Invalid email or password. Please try again or /register if you don\'t have an account.",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Operation cancelled.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays user profile information."""
    user_id = update.effective_user.id
    with next(get_db()) as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            await update.message.reply_text(
                f"""
                👤 Your Profile:
                Telegram ID: {user.user_id}
                Username: {user.username or 'N/A'}
                Email: {user.email}
                Balance: {user.balance:.2f} credits
                Admin: {'Yes' if user.is_admin else 'No'}
                Registered: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                """
            )
        else:
            await update.message.reply_text(
                "You are not registered. Please use /register to create an account."
            )


