# 🤖 iramXtele-sniper

**Telegram Username Sniper Bot** – Monitor and automatically claim Telegram usernames using your personal account.

> ⚠️ **Educational Purpose Only** – Use responsibly. It is recommended to inform Telegram at `recover@telegram.org` before deploying.

---

## ✨ Features

- ✅ **Add multiple usernames** via Telegram bot commands (`/add @cool @awesome`)
- ✅ **Continuous monitoring** every 0.5–1 second (configurable)
- ✅ **Auto‑claim** when a username becomes available (to a **new channel** or your account)
- ✅ **Instant notification** when a username is claimed
- ✅ **SQLite database** for persistent tracking
- ✅ **Flask health‑check endpoint** for Render free tier
- ✅ **Session string persistence** – no repeated logins

---

## 🛠️ Prerequisites

- Python 3.10+
- **API ID & Hash** from [my.telegram.org](https://my.telegram.org)
- **Bot Token** from [@BotFather](https://t.me/botfather)
- Your **personal Telegram account** (used for claiming)

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/iramXtele-snipt.git
cd iramXtele-snipt

# Install dependencies
pip install -r requirements.txt

# Copy environment variables template
cp .env.example .env

# Edit .env with your credentials
```

Environment Variables (.env)

```env
# User account (for claiming)
API_ID=12345678
API_HASH=your_api_hash_here
PHONE_NUMBER=+919876543210

# Bot token (for commands & notifications)
BOT_TOKEN=your_bot_token_here

# Session string (optional, will be generated after first run)
SESSION_STRING=

# Settings
CHECK_INTERVAL=0.5
CLAIM_TO=channel

# Render port
PORT=10000
```

---

🚀 Running Locally

```bash
python bot.py
```

The Flask health‑check server can be run separately (optional):

```bash
python main.py
```

---

📱 Bot Commands

Command Description
/start Welcome message
/add @username1 @username2 Add usernames to monitor
/remove @username Remove a username
/list Show all usernames with status
/status Show bot statistics
/clear Clear all pending usernames
/help Help message

---

⚙️ How It Works

1. You add usernames via /add.
2. The bot saves them in the SQLite database with status pending.
3. A background process continuously checks the availability of each username using your user account.
4. When a username becomes available:
   · The bot creates a new channel (or claims to your account if CLAIM_TO=user).
   · Assigns the username to that channel via channels.UpdateUsername.
   · Marks it as claimed in the database.
   · Sends you a Telegram notification 🎉.

---

🧠 Why User Account? Why Not Bot Token?

· Bots cannot claim usernames – Telegram’s API restricts account.updateUsername and channels.createChannel to user accounts only.
· Your user account (logged in via Telethon) is used for checking and claiming.
· The bot token is used only for receiving commands and sending notifications.

---

☁️ Deploy to Render (Free Tier)

1. Push your code to GitHub.
2. On render.com, create a new Web Service.
3. Connect your GitHub repository.
4. Build Command: pip install -r requirements.txt
5. Start Command: python bot.py & python main.py
6. Add all environment variables from your .env.
7. Health Check Path: /health
8. Choose Free instance type and deploy.

💡 The Flask server keeps your service alive on Render; the bot.py process runs continuously in the background.

---

⚠️ Important Notes

· Minimum check interval – Do not set below 0.1 seconds to avoid flood waits.
· Maximum usernames – Monitoring more than 5 usernames reduces success rate and increases rate‑limit risk.
· Session string – After first successful login, a session string will be printed. Save it in .env to avoid re‑login on restart.
· Channel claiming is recommended – It has fewer rate limits and allows you to auction usernames on Fragment later.

---

👨‍💻 Credits

· Developer: @rehuux
· Owner: Syed Rehan

---

📄 License

This project is for educational purposes only. Use at your own risk.
Please respect Telegram’s Terms of Service.

---

⚡ Powered by @rehuux
