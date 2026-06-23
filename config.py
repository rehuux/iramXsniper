"""
Configuration loader for Username Sniper Bot
Developer: @gotweeds | Owner: Syed Rehan
"""

import os
from dotenv import load_dotenv

load_dotenv()

# === User account credentials (for claiming) ===
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
PHONE_NUMBER = os.getenv('PHONE_NUMBER', '')

# === Bot token (for commands & notifications) ===
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# === Optional session string (saves login) ===
SESSION_STRING = os.getenv('SESSION_STRING', '')

# === Settings ===
CHECK_INTERVAL = float(os.getenv('CHECK_INTERVAL', '0.5'))   # seconds
CLAIM_TO = os.getenv('CLAIM_TO', 'channel')   # 'channel' or 'user'

# === Render ===
PORT = int(os.getenv('PORT', 10000))

# === Branding ===
DEV_NAME = "@gotweeds"
OWNER_NAME = "Syed Rehan"
BOT_NAME = "Username Sniper Bot"
