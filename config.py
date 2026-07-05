import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
PORT = int(os.getenv("PORT", "10000"))

# Free Render plan me RAM/CPU limited hoti hai, isliye bade files reject karenge
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "20"))

# Tumhara Telegram user ID - /stats command sirf isi ID wale ko dikhega
ADMIN_ID = int(os.getenv("ADMIN_ID", "0")) or None

# Rate limiting - spam/abuse rokne ke liye (free plan ke resources bachane ke liye)
RATE_LIMIT_COUNT = int(os.getenv("RATE_LIMIT_COUNT", "5"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# Optional: Premium animated emoji ki ID welcome message me dikhane ke liye.
# Sirf tabhi kaam karega jab bot owner (BotFather wala account) ke paas Telegram Premium ho.
# Khaali chhod do agar nahi chahiye - bot bilkul normal chalega.
WELCOME_EMOJI_ID = os.getenv("WELCOME_EMOJI_ID", "").strip() or None

TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN environment variable set nahi hai. "
        ".env file me ya Render dashboard me BOT_TOKEN add karo."
    )
