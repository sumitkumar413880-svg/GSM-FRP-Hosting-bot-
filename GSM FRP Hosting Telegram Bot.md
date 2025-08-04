# GSM FRP Hosting Telegram Bot

This is a Telegram bot designed to provide GSM FRP (Factory Reset Protection) bypass services. It includes user management, service listing, a mock payment system, and an administrative panel for managing users, services, and orders.

## Features

*   **User Management:** Registration, login, and profile viewing.
*   **Service Catalog:** Browse available FRP bypass services.
*   **Credit System:** Users can add credits (mock payment) and use them to purchase services.
*   **Order Management:** Users can view their order history; Admins can list and fulfill pending orders.
*   **Admin Panel:** Comprehensive tools for administrators to manage users, services, and broadcast messages.

## Setup Instructions

### Prerequisites

*   Python 3.8+
*   A Telegram Bot Token (obtain from BotFather on Telegram)
*   Basic understanding of Python and Telegram bots

### Installation

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <repository_url>
    cd gsm_frp_bot
    ```
    (Note: Since this is a sandbox environment, you would typically download the files directly or copy them.)

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Create a `config.py` file in the root directory of the project (if it doesn't exist) or modify the existing one. This file will hold your bot's token and other settings.

```python
import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE") # Replace with your actual bot token or set as environment variable

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///gsm_frp_bot.db") # SQLite database file

# Admin configuration
# Add Telegram User IDs of administrators, comma-separated. Example: "123456789,987654321"
ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]

# Service configuration
DEFAULT_CREDIT_PRICE = 1.0  # Price per credit in USD (for mock payment)
```

**Important:** For security, it is highly recommended to set `BOT_TOKEN` and `ADMIN_USER_IDS` as environment variables rather than hardcoding them directly in `config.py`.

### Running the Bot

1.  **Ensure your environment variables are set (if you chose that method for configuration):**
    ```bash
    export BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    export ADMIN_USER_IDS="YOUR_ADMIN_TELEGRAM_ID_1,YOUR_ADMIN_TELEGRAM_ID_2"
    ```
    (Replace `YOUR_TELEGRAM_BOT_TOKEN` and `YOUR_ADMIN_TELEGRAM_ID_X` with your actual values.)

2.  **Run the main bot script:**
    ```bash
    python3 main.py
    ```

The bot should now be running and accessible via Telegram.

## Usage

### User Commands
*   `/start`: Start interaction with the bot.
*   `/help`: Get a list of commands and help information.
*   `/register`: Register a new account with the bot.
*   `/login`: Log in to your existing account.
*   `/profile`: View your account details and credit balance.
*   `/services`: Browse available FRP bypass services.
*   `/buy <service_id>`: Purchase a specific service (e.g., `/buy 1`).
*   `/myorders`: View your past service orders.
*   `/balance`: Check your current credit balance.
*   `/addcredits`: Initiate the process to add credits to your account (mock payment).

### Admin Commands (Requires Admin Privileges)
*   `/admin`: Access the administrative panel.
    *   **Manage Users:** List all registered users.
    *   **Manage Services:** Add, edit, delete, and list services.
    *   **Manage Orders:** List pending orders and fulfill them.
    *   **Broadcast Message:** Send a message to all registered users.

## Database

The bot uses an SQLite database (`gsm_frp_bot.db`) by default. The database schema includes tables for `users`, `services`, `orders`, and `transactions`.

## Extending Functionality

*   **Payment Gateway Integration:** Replace the mock payment system in `handlers/payment.py` with a real payment gateway (e.g., Stripe, PayPal, or a cryptocurrency payment processor).
*   **FRP Fulfillment Automation:** Implement actual logic in `handlers/fulfillment.py` to interact with external FRP bypass APIs or systems.
*   **Advanced Admin Features:** Add more detailed user management (e.g., edit user balance, ban users), service statistics, etc.
*   **Error Handling and Logging:** Enhance error handling and logging for production environments.

## Contributing

Feel free to fork the repository, make improvements, and submit pull requests.

## License

This project is open-source and available under the MIT License. (You might want to choose a specific license for your project.)


