from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from models.database import User, Transaction, get_db
from config import DEFAULT_CREDIT_PRICE

ADD_CREDITS_AMOUNT = range(1)

async def add_credits_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Initiates the process to add credits."""
    await update.message.reply_text(
        "To add credits, please specify the amount you wish to purchase (e.g., 10, 25, 50)."
    )
    return ADD_CREDITS_AMOUNT

async def add_credits_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Processes the credit addition (mock payment)."""
    try:
        amount = float(update.message.text)
        if amount <= 0:
            await update.message.reply_text("Please enter a positive amount.")
            return ADD_CREDITS_AMOUNT
    except ValueError:
        await update.message.reply_text("Invalid amount. Please enter a number.")
        return ADD_CREDITS_AMOUNT

    user_id = update.effective_user.id
    with next(get_db()) as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            await update.message.reply_text("You are not registered. Please use /register to create an account.")
            return ConversationHandler.END
        
        # Mock payment processing
        # In a real application, this would involve interaction with a payment gateway (e.g., Stripe, PayPal)
        # and verification of successful payment before updating user balance.
        
        user.balance += amount
        
        new_transaction = Transaction(
            user_id=user.user_id,
            amount=amount,
            transaction_type="credit_purchase",
            payment_gateway_ref="MOCK_PAYMENT_REF_" + str(user_id) + "_" + str(int(amount))
        )
        db.add(user)
        db.add(new_transaction)
        db.commit()

        await update.message.reply_text(
            f"Successfully added {amount:.2f} credits to your account. Your new balance is {user.balance:.2f} credits."
        )
        return ConversationHandler.END

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Adding credits operation cancelled."
    )
    return ConversationHandler.END


