import os

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///gsm_frp_bot.db")

# Admin configuration
ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]

# Service configuration
DEFAULT_CREDIT_PRICE = 1.0  # Price per credit in USD

