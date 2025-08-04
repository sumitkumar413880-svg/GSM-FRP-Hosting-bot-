from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.database import Service, User, Order, Transaction, get_db
import json

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays a list of available FRP services."""
    with next(get_db()) as db:
        active_services = db.query(Service).filter(Service.is_active == True).all()

        if not active_services:
            await update.message.reply_text("No services are currently available. Please check back later.")
            return

        message_text = "Available FRP Services:\n\n"
        keyboard = []

        for service in active_services:
            message_text += f"ID: {service.service_id}\n"
            message_text += f"Name: {service.name}\n"
            message_text += f"Description: {service.description}\n"
            message_text += f"Price: {service.price:.2f} credits\n\n"
            keyboard.append([InlineKeyboardButton(f"Buy {service.name} ({service.price:.2f} credits)", callback_data=f"buy_service_{service.service_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message_text, reply_markup=reply_markup)

async def buy_service_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the callback query for buying a service."""
    query = update.callback_query
    await query.answer()

    service_id = int(query.data.split("_")[-1])
    user_id = query.from_user.id

    with next(get_db()) as db:
        service = db.query(Service).filter(Service.service_id == service_id).first()
        user = db.query(User).filter(User.user_id == user_id).first()

        if not service:
            await query.edit_message_text("Service not found.")
            return
        if not user:
            await query.edit_message_text("You are not registered. Please use /register to create an account.")
            return
        if user.balance < service.price:
            await query.edit_message_text(
                f"Insufficient credits. You need {service.price:.2f} credits, but you only have {user.balance:.2f}. "
                "Please add credits using /addcredits."
            )
            return
        
        # Deduct credits and create order
        user.balance -= service.price
        
        new_order = Order(
            user_id=user.user_id,
            service_id=service.service_id,
            status="pending",
            device_info=json.dumps({"note": "Device info to be collected"}),
            fulfillment_details=None
        )
        
        new_transaction = Transaction(
            user_id=user.user_id,
            amount=-service.price,
            transaction_type="service_purchase",
            payment_gateway_ref=f"ORDER_{new_order.order_id}"
        )
        
        db.add(user)
        db.add(new_order)
        db.add(new_transaction)
        db.commit()
        
        await query.edit_message_text(
            f"Successfully purchased {service.name} for {service.price:.2f} credits.\n"
            f"Order ID: {new_order.order_id}\n"
            f"Your new balance is {user.balance:.2f} credits.\n"
            "Your order is being processed. You will be notified when it's completed."
        )


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's order history."""
    user_id = update.effective_user.id
    with next(get_db()) as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            await update.message.reply_text("You are not registered. Please use /register to create an account.")
            return
        
        orders = user.orders
        if not orders:
            await update.message.reply_text("You have no orders yet.")
            return
        
        message_text = "Your Order History:\n\n"
        for order in orders:
            message_text += f"Order ID: {order.order_id}\n"
            message_text += f"Service: {order.service.name}\n"
            message_text += f"Status: {order.status}\n"
            message_text += f"Date: {order.order_date.strftime("%Y-%m-%d %H:%M:%S")}\n"
            if order.device_info:
                message_text += f"Device Info: {order.device_info}\n"
            if order.fulfillment_details:
                message_text += f"Fulfillment: {order.fulfillment_details}\n"
            message_text += "\n"
        await update.message.reply_text(message_text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the user's current credit balance."""
    user_id = update.effective_user.id
    with next(get_db()) as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            await update.message.reply_text(f"Your current balance is: {user.balance:.2f} credits.")
        else:
            await update.message.reply_text("You are not registered. Please use /register to create an account.")


