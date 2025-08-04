from telegram import Update
from telegram.ext import ContextTypes
from models.database import Order, get_db
import json

async def fulfill_order(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: int, fulfillment_data: dict) -> None:
    """Fulfills an order and updates its status and fulfillment details."""
    with next(get_db()) as db:
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if order:
            order.status = "completed"
            order.fulfillment_details = json.dumps(fulfillment_data)
            db.add(order)
            db.commit()
            await context.bot.send_message(
                chat_id=order.user_id,
                text=f"Your order (ID: {order.order_id}) for {order.service.name} has been completed!\n\nFulfillment Details:\n{json.dumps(fulfillment_data, indent=2)}"
            )
        else:
            await update.message.reply_text(f"Order ID {order_id} not found for fulfillment.")

async def provide_frp_link(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: int, frp_link: str) -> None:
    """Provides an FRP bypass link as fulfillment."""
    fulfillment_data = {"type": "link", "link": frp_link}
    await fulfill_order(update, context, order_id, fulfillment_data)

async def provide_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: int, username: str, password: str) -> None:
    """Provides credentials as fulfillment."""
    fulfillment_data = {"type": "credentials", "username": username, "password": password}
    await fulfill_order(update, context, order_id, fulfillment_data)

async def provide_custom_message(update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: int, message: str) -> None:
    """Provides a custom message as fulfillment."""
    fulfillment_data = {"type": "custom_message", "message": message}
    await fulfill_order(update, context, order_id, fulfillment_data)


