import os

# Bot configuration
BOT_TOKEN = os.getenv("BOt Toke", "8071167662:AAH2taJuwpYfGdV_cwuj16AwX_gOV_im1O4")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///gsm_frp_bot.db")

# Admin configuration
ADMIN_USER_IDS = [int(x) for x in os.getenv("ADMIN_USER_IDS", "").split(",") if x.strip()]

# Service configuration
DEFAULT_CREDIT_PRICE = 1.0  # Price per credit in USD

