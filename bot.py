"""
Main bot – handles commands and starts monitor thread
Developer: @gotweeds | Owner: Syed Rehan
"""

import asyncio
import threading
from telebot import TeleBot, types
import config
import database as db
from claimer import UsernameClaimer

# Initialize bot and claimer
bot = TeleBot(config.BOT_TOKEN)
claimer = UsernameClaimer()

# Background monitor thread reference
monitor_thread = None
loop = None

# Branding
SEPARATOR = "━━━━━━━━━━━━━━━━━━"
FOOTER = f"\n{SEPARATOR}\n⚡ Powered by {config.DEV_NAME}"

def format_response(text):
    return f"{text}\n{FOOTER}"

# === Commands ===
@bot.message_handler(commands=['start'])
def start_cmd(message: types.Message):
    welcome = f"""
{SEPARATOR}
🤖 {config.BOT_NAME} v2.0

Monitor and claim Telegram usernames automatically.

📌 Commands:
/add @username1 @username2  - Add usernames
/remove @username           - Remove username
/list                       - Show all usernames
/status                     - Show statistics
/clear                      - Clear pending
/start                      - This message
/help                       - Help

👨‍💻 Developer: {config.DEV_NAME}
👤 Owner: {config.OWNER_NAME}

⚠️ Educational purpose only
{SEPARATOR}
"""
    bot.reply_to(message, format_response(welcome))

@bot.message_handler(commands=['help'])
def help_cmd(message: types.Message):
    help_text = f"""
{SEPARATOR}
📚 Help

/add @username1 @username2 - Add usernames to monitor
/remove @username           - Remove from monitoring
/list                       - Show all usernames with status
/status                     - Bot statistics
/clear                      - Clear all pending
/start                      - Welcome
/help                       - This message

📌 How it works:
1. Add usernames with /add
2. Bot checks every {config.CHECK_INTERVAL}s
3. When available, claims to {'channel' if config.CLAIM_TO=='channel' else 'your account'}
4. You get notification! 🎉

⚠️ Max 5 usernames recommended.
{SEPARATOR}
"""
    bot.reply_to(message, format_response(help_text))

@bot.message_handler(commands=['add'])
def add_cmd(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.split()[1:]
    if not parts:
        bot.reply_to(message, format_response("❌ Provide usernames: /add @cool @awesome"))
        return

    added = []
    failed = []
    for p in parts:
        username = p.replace('@', '').strip().lower()
        if len(username) < 5:
            failed.append(f"@{username} (too short)")
            continue
        if not username.isalnum() and '_' not in username:
            failed.append(f"@{username} (invalid chars)")
            continue
        if username[0].isdigit():
            failed.append(f"@{username} (starts with number)")
            continue
        if db.add_username(username, user_id):
            added.append(f"@{username}")
        else:
            failed.append(f"@{username} (already in list)")

    response = ""
    if added:
        response += "✅ Added:\n" + "\n".join(f"• {u}" for u in added)
    if failed:
        response += "\n\n❌ Failed:\n" + "\n".join(f"• {f}" for f in failed)
    if not response:
        response = "❌ No valid usernames provided."
    bot.reply_to(message, format_response(response))

@bot.message_handler(commands=['remove'])
def remove_cmd(message: types.Message):
    user_id = message.from_user.id
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, format_response("❌ Provide username: /remove @cool"))
        return
    username = parts[1].replace('@', '').strip().lower()
    if db.remove_username(username, user_id):
        bot.reply_to(message, format_response(f"✅ Removed @{username}"))
    else:
        bot.reply_to(message, format_response(f"❌ @{username} not found or already claimed"))

@bot.message_handler(commands=['list'])
def list_cmd(message: types.Message):
    user_id = message.from_user.id
    usernames = db.get_all_usernames(user_id)
    if not usernames:
        bot.reply_to(message, format_response("📋 No usernames in database."))
        return

    pending = [u for u in usernames if u['status'] == 'pending']
    claimed = [u for u in usernames if u['status'] == 'claimed']
    response = "📋 Usernames:\n\n"
    if pending:
        response += "⏳ Pending:\n" + "\n".join(f"  • @{u['username']} (added: {u['added_at'][:16]})" for u in pending) + "\n\n"
    if claimed:
        response += "✅ Claimed:\n" + "\n".join(f"  • @{u['username']} (claimed: {u['claimed_at'][:16]})" for u in claimed)
    response += f"\n\n📊 Total: {len(usernames)}"
    bot.reply_to(message, format_response(response))

@bot.message_handler(commands=['status'])
def status_cmd(message: types.Message):
    user_id = message.from_user.id
    stats = db.get_stats(user_id)
    response = f"""
📊 Bot Statistics

📈 Usernames:
• Total: {stats['total']}
• Pending: {stats['pending']}
• Claimed: {stats['claimed']}

⚙️ Settings:
• Check Interval: {config.CHECK_INTERVAL}s
• Claim To: {config.CLAIM_TO}

👨‍💻 {config.DEV_NAME}
"""
    bot.reply_to(message, format_response(response))

@bot.message_handler(commands=['clear'])
def clear_cmd(message: types.Message):
    user_id = message.from_user.id
    count = db.clear_pending(user_id)
    if count == 0:
        bot.reply_to(message, format_response("📋 No pending usernames to clear."))
    else:
        bot.reply_to(message, format_response(f"✅ Cleared {count} pending usernames."))

# === Background monitor runner ===
def start_monitor():
    global loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run():
        if await claimer.start():
            await claimer.monitor_loop(bot)
        else:
            print("❌ Failed to login. Exiting monitor.")

    loop.run_until_complete(run())

# === Start everything ===
if __name__ == '__main__':
    db.init_db()
    print(f"✅ Database initialized. Pending: {len(db.get_pending_usernames())}")

    # Start monitor in background thread
    monitor_thread = threading.Thread(target=start_monitor, daemon=True)
    monitor_thread.start()

    print(f"""
{SEPARATOR}
🤖 {config.BOT_NAME} started
👨‍💻 {config.DEV_NAME}
✅ Monitoring with user account
📱 Bot listening for commands...
{SEPARATOR}
""")

    try:
        bot.infinity_polling(timeout=60)
    except KeyboardInterrupt:
        print("\n⚠️ Stopping...")
        claimer.is_running = False
        if loop:
            loop.run_until_complete(claimer.stop())
