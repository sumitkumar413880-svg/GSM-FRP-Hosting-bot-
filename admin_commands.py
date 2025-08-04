from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from models.database import User, Service, Order, get_db
from config import ADMIN_USER_IDS
import json

# States for admin conversation handler
ADMIN_MENU, MANAGE_USERS, MANAGE_SERVICES, ADD_SERVICE_NAME, ADD_SERVICE_DESC, ADD_SERVICE_PRICE, EDIT_SERVICE_SELECT, EDIT_SERVICE_FIELD, EDIT_SERVICE_VALUE, DELETE_SERVICE_SELECT, BROADCAST_MESSAGE, MANAGE_ORDERS, FULFILL_ORDER_SELECT, FULFILL_ORDER_DETAILS = range(14)

def is_admin(user_id: int) -> bool:
    """Checks if a user is an admin."""
    return user_id in ADMIN_USER_IDS

async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the admin conversation and displays the admin menu."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("You are not authorized to access the admin panel.")
        return ConversationHandler.END

    keyboard = [
        [KeyboardButton("Manage Users")],
        [KeyboardButton("Manage Services")],
        [KeyboardButton("Manage Orders")],
        [KeyboardButton("Broadcast Message")],
        [KeyboardButton("Cancel")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Welcome to the Admin Panel!", reply_markup=reply_markup)
    return ADMIN_MENU

async def admin_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles selection from the admin menu."""
    text = update.message.text

    if text == "Manage Users":
        keyboard = [
            [KeyboardButton("List Users")],
            [KeyboardButton("Back to Admin Menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("User Management:", reply_markup=reply_markup)
        return MANAGE_USERS
    elif text == "Manage Services":
        keyboard = [
            [KeyboardButton("Add Service")],
            [KeyboardButton("Edit Service")],
            [KeyboardButton("Delete Service")],
            [KeyboardButton("List Services")],
            [KeyboardButton("Back to Admin Menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Service Management:", reply_markup=reply_markup)
        return MANAGE_SERVICES
    elif text == "Manage Orders":
        keyboard = [
            [KeyboardButton("List Pending Orders")],
            [KeyboardButton("Fulfill Order")],
            [KeyboardButton("Back to Admin Menu")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Order Management:", reply_markup=reply_markup)
        return MANAGE_ORDERS
    elif text == "Broadcast Message":
        await update.message.reply_text("Please enter the message you want to broadcast to all users:", reply_markup=ReplyKeyboardRemove())
        return BROADCAST_MESSAGE
    elif text == "Cancel":
        await update.message.reply_text("Admin operation cancelled.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Invalid option. Please choose from the menu.")
        return ADMIN_MENU

async def manage_users_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles selection from the manage users menu."""
    text = update.message.text

    if text == "List Users":
        with next(get_db()) as db:
            users = db.query(User).all()
            if not users:
                await update.message.reply_text("No users registered yet.")
            else:
                message_text = "Registered Users:\n\n"
                for user in users:
                    message_text += f"ID: {user.user_id}, Username: {user.username or 'N/A'}, Email: {user.email}, Balance: {user.balance:.2f}, Admin: {user.is_admin}\n"
                await update.message.reply_text(message_text)
        return MANAGE_USERS # Stay in user management
    elif text == "Back to Admin Menu":
        return await admin_start(update, context) # Go back to admin menu
    else:
        await update.message.reply_text("Invalid option. Please choose from the menu.")
        return MANAGE_USERS

async def manage_services_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles selection from the manage services menu."""
    text = update.message.text

    if text == "Add Service":
        await update.message.reply_text("Please enter the name of the new service:", reply_markup=ReplyKeyboardRemove())
        return ADD_SERVICE_NAME
    elif text == "Edit Service":
        await update.message.reply_text("Please enter the ID of the service you want to edit:", reply_markup=ReplyKeyboardRemove())
        return EDIT_SERVICE_SELECT
    elif text == "Delete Service":
        await update.message.reply_text("Please enter the ID of the service you want to delete:", reply_markup=ReplyKeyboardRemove())
        return DELETE_SERVICE_SELECT
    elif text == "List Services":
        from handlers.service_management import services as list_services # Avoid circular import
        await list_services(update, context) # Reuse existing services function
        return MANAGE_SERVICES # Stay in service management
    elif text == "Back to Admin Menu":
        return await admin_start(update, context) # Go back to admin menu
    else:
        await update.message.reply_text("Invalid option. Please choose from the menu.")
        return MANAGE_SERVICES

async def add_service_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets service name and asks for description."""
    context.user_data["new_service_name"] = update.message.text
    await update.message.reply_text("Please enter the description for the service:")
    return ADD_SERVICE_DESC

async def add_service_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets service description and asks for price."""
    context.user_data["new_service_desc"] = update.message.text
    await update.message.reply_text("Please enter the price (in credits) for the service:")
    return ADD_SERVICE_PRICE

async def add_service_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets service price and adds the service to the database."""
    try:
        price = float(update.message.text)
        if price <= 0:
            await update.message.reply_text("Price must be a positive number. Please try again.")
            return ADD_SERVICE_PRICE
    except ValueError:
        await update.message.reply_text("Invalid price. Please enter a number.")
        return ADD_SERVICE_PRICE

    name = context.user_data["new_service_name"]
    description = context.user_data["new_service_desc"]

    with next(get_db()) as db:
        new_service = Service(
            name=name,
            description=description,
            price=price,
            is_active=True
        )
        db.add(new_service)
        db.commit()
        await update.message.reply_text(f"Service \'{name}\' added successfully with ID {new_service.service_id}.")
    return await admin_start(update, context) # Go back to admin menu

async def edit_service_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Selects service to edit and asks for field."""
    try:
        service_id = int(update.message.text)
        with next(get_db()) as db:
            service = db.query(Service).filter(Service.service_id == service_id).first()
            if not service:
                await update.message.reply_text("Service not found. Please enter a valid service ID.")
                return EDIT_SERVICE_SELECT
            context.user_data["edit_service_id"] = service_id
            keyboard = [
                [KeyboardButton("name"), KeyboardButton("description")],
                [KeyboardButton("price"), KeyboardButton("is_active")],
                [KeyboardButton("Cancel")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(f"Which field of service ID {service_id} do you want to edit?", reply_markup=reply_markup)
            return EDIT_SERVICE_FIELD
    except ValueError:
        await update.message.reply_text("Invalid service ID. Please enter a number.")
        return EDIT_SERVICE_SELECT

async def edit_service_field(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Gets field to edit and asks for new value."""
    field = update.message.text.lower()
    if field not in ["name", "description", "price", "is_active", "cancel"]:
        await update.message.reply_text("Invalid field. Please choose from name, description, price, or is_active.")
        return EDIT_SERVICE_FIELD
    
    if field == "cancel":
        await update.message.reply_text("Service edit cancelled.", reply_markup=ReplyKeyboardRemove())
        return await admin_start(update, context)

    context.user_data["edit_service_field"] = field
    await update.message.reply_text(f"Please enter the new value for \'{field}\':", reply_markup=ReplyKeyboardRemove())
    return EDIT_SERVICE_VALUE

async def edit_service_value(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Updates the service with the new value."""
    service_id = context.user_data["edit_service_id"]
    field = context.user_data["edit_service_field"]
    value = update.message.text

    with next(get_db()) as db:
        service = db.query(Service).filter(Service.service_id == service_id).first()
        if not service:
            await update.message.reply_text("Service not found. This should not happen.")
            return await admin_start(update, context)

        if field == "price":
            try:
                value = float(value)
                if value <= 0:
                    await update.message.reply_text("Price must be a positive number. Please try again.")
                    return EDIT_SERVICE_VALUE
            except ValueError:
                await update.message.reply_text("Invalid price. Please enter a number.")
                return EDIT_SERVICE_VALUE
        elif field == "is_active":
            value = value.lower() == "true"
        
        setattr(service, field, value)
        db.add(service)
        db.commit()
        await update.message.reply_text(f"Service ID {service_id} \'{field}\' updated to \'{value}\'.")
    return await admin_start(update, context) # Go back to admin menu

async def delete_service_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Deletes a service."""
    try:
        service_id = int(update.message.text)
        with next(get_db()) as db:
            service = db.query(Service).filter(Service.service_id == service_id).first()
            if not service:
                await update.message.reply_text("Service not found. Please enter a valid service ID.")
                return DELETE_SERVICE_SELECT
            
            db.delete(service)
            db.commit()
            await update.message.reply_text(f"Service ID {service_id} (\'{service.name}\') deleted successfully.")
        return await admin_start(update, context) # Go back to admin menu
    except ValueError:
        await update.message.reply_text("Invalid service ID. Please enter a number.")
        return DELETE_SERVICE_SELECT

async def manage_orders_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handles selection from the manage orders menu."""
    text = update.message.text

    if text == "List Pending Orders":
        with next(get_db()) as db:
            pending_orders = db.query(Order).filter(Order.status == "pending").all()
            if not pending_orders:
                await update.message.reply_text("No pending orders.")
            else:
                message_text = "Pending Orders:\n\n"
                for order in pending_orders:
                    message_text += f"Order ID: {order.order_id}\n"
                    message_text += f"User ID: {order.user_id}\n"
                    message_text += f"Service: {order.service.name}\n"
                    message_text += f"Order Date: {order.order_date.strftime(\"%Y-%m-%d %H:%M:%S\")}\n"
                    if order.device_info:
                        message_text += f"Device Info: {order.device_info}\n"
                    message_text += "\n"
                await update.message.reply_text(message_text)
        return MANAGE_ORDERS # Stay in order management
    elif text == "Fulfill Order":
        await update.message.reply_text("Please enter the Order ID to fulfill:", reply_markup=ReplyKeyboardRemove())
        return FULFILL_ORDER_SELECT
    elif text == "Back to Admin Menu":
        return await admin_start(update, context) # Go back to admin menu
    else:
        await update.message.reply_text("Invalid option. Please choose from the menu.")
        return MANAGE_ORDERS

async def fulfill_order_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Selects an order to fulfill and asks for fulfillment details."""
    try:
        order_id = int(update.message.text)
        with next(get_db()) as db:
            order = db.query(Order).filter(Order.order_id == order_id, Order.status == "pending").first()
            if not order:
                await update.message.reply_text("Pending order not found. Please enter a valid pending Order ID.")
                return FULFILL_ORDER_SELECT
            context.user_data["fulfill_order_id"] = order_id
            await update.message.reply_text(
                f"Enter fulfillment details for Order ID {order_id}. "
                "Example: {\\\"type\\\": \\\"link\\\", \\\"link\\\": \\\"https://example.com/frp\\\"} or {\\\"type\\\": \\\"message\\\", \\\"message\\\": \\\"Your FRP is done!\\\"}"
            )
            return FULFILL_ORDER_DETAILS
    except ValueError:
        await update.message.reply_text("Invalid Order ID. Please enter a number.")
        return FULFILL_ORDER_SELECT

async def fulfill_order_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives fulfillment details and calls the fulfillment function."""
    order_id = context.user_data["fulfill_order_id"]
    try:
        fulfillment_data = json.loads(update.message.text)
        if not isinstance(fulfillment_data, dict):
            raise ValueError("Invalid JSON format.")
    except json.JSONDecodeError:
        await update.message.reply_text("Invalid JSON format. Please provide valid JSON.")
        return FULFILL_ORDER_DETAILS
    except ValueError as e:
        await update.message.reply_text(f"Error: {e}. Please provide valid JSON.")
        return FULFILL_ORDER_DETAILS

    # Call the fulfillment function (from handlers.fulfillment)
    from handlers.fulfillment import fulfill_order
    await fulfill_order(update, context, order_id, fulfillment_data)
    await update.message.reply_text(f"Order ID {order_id} marked as fulfilled.")
    return await admin_start(update, context) # Go back to admin menu

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Broadcasts a message to all users."""
    message_to_send = update.message.text
    with next(get_db()) as db:
        users = db.query(User).all()
        for user in users:
            try:
                await context.bot.send_message(chat_id=user.user_id, text=message_to_send)
            except Exception as e:
                print(f"Could not send message to user {user.user_id}: {e}")
        await update.message.reply_text("Message broadcasted to all users.")
    return await admin_start(update, context) # Go back to admin menu

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the admin conversation."""
    await update.message.reply_text("Admin operation cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


