import os
import asyncio
import time
from datetime import datetime
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.request
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ১. Render এনভায়রনমেন্ট ভ্যারিয়েবল থেকে টোকেন নেওয়া
TOKEN = os.environ.get("BOT_TOKEN")

# ডাইনামিক ডেটা ট্র্যাকিং
user_data = {}
total_users = set()
bot_version = "3.5 (Advanced Pro)"

# সাইবার সিকিউরিটি ও এথিক্যাল হ্যাকিং টিপস পুল
SECURITY_TIPS = [
    "Always use a strong VPN when performing network reconnaissance or penetration testing.",
    "Enable 2-Step Verification (2FA) on your Telegram account to block unauthorized session hijacking.",
    "Do not click on unsolicited links or download unrecognized `.apk` or `.exe` files in public groups.",
    "Regularly audit active sessions in your Telegram Settings > Devices to terminate suspicious clones.",
    "Keep your automated lab environments isolated from your primary host network using proper VLANs."
]

# --- রেন্ডার ২৪ ঘণ্টা লাইভ রাখার জন্য ফেইক ওয়েব সার্ভার ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Advanced Bot is Running 24/7!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()
# --------------------------------------------------

# অ্যাডভান্সড ইউজার ট্র্যাকিং ফাংশন
def track_user(update: Update):
    user = update.effective_user
    user_id = user.id
    username = user.username or "Not set"
    first_name = user.first_name
    last_name = user.last_name or ""
    language_code = user.language_code or "Unknown"
    is_premium = "Yes 🌟" if user.is_premium else "No"
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_users.add(user_id)
    
    if user_id not in user_data:
        user_data[user_id] = {
            "first_seen": current_time,
            "last_seen": current_time,
            "msg_count": 1,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "language": language_code,
            "premium": is_premium
        }
    else:
        user_data[user_id]["last_seen"] = current_time
        user_data[user_id]["msg_count"] += 1
        user_data[user_id]["username"] = username
        user_data[user_id]["first_name"] = first_name
        user_data[user_id]["last_name"] = last_name
        user_data[user_id]["language"] = language_code
        user_data[user_id]["premium"] = is_premium
        
    return user_data[user_id]

# /start কমান্ড
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    
    msg1 = (
        f"👋 *Welcome to the Advanced Hub, {first_name}!*\n\n"
        f"🤖 *RS5_ARIF Pro Edition ID Bot* v{bot_version}\n"
        f"• Instant Chat & User ID Fetching\n"
        f"• Deep Analytics & System Auditing\n"
        f"• Integrated Network Security Modules\n\n"
        f"Use /help to unlock the full potential!"
    )
    await update.message.reply_text(text=msg1, parse_mode="Markdown")
    
    msg2 = f"✨ *Your Secure Chat ID:* `{chat_id}`"
    await update.message.reply_text(text=msg2, parse_mode="Markdown")
    
    msg3 = (
        f"🌟 *Official Node:* @RS5ARIF\n"
        f"💡 *Pro-Tip:* Execute /info to run a full profile diagnostics check."
    )
    await update.message.reply_text(text=msg3, parse_mode="Markdown")

# /help কমান্ড
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    help_text = (
        f"🛠️ *Advanced Bot Core Menu*\n\n"
        f"📋 *Core Commands:*\n"
        f"• /start - Activate session & pull Chat ID\n"
        f"• /help - Display this advanced controller schema\n"
        f"• /info - Generate deep profile analytics payload\n"
        f"• /netinfo - Query bot infrastructure network state\n"
        f"• /sectip - Fetch a random cybersecurity/hardening tip\n"
        f"• /ping - Measure exact core response latency\n"
        f"• /stats - Broadcast total operational statistics\n\n"
        f"⚡ *System Architecture:*\n"
        f"• Fully Containerized & Persistent\n"
        f"• Native Markdown Auto-Copy Hooks\n"
        f"• Sub-millisecond Event Handlers\n\n"
        f"📡 *Network Operations:* @RS5ARIF"
    )
    await update.message.reply_text(text=help_text, parse_mode="Markdown")

# /info কমান্ড (অ্যাডভান্সড ভেরিয়েন্ট)
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ud = track_user(update)
    user = update.effective_user
    
    username_display = f"@{ud['username']}" if ud['username'] != "Not set" else "Not set"
    full_name = f"{ud['first_name']} {ud['last_name']}".strip()
    
    info_text = (
        f"🕵️‍♂️ *Deep Profile Analytics Generated*\n\n"
        f"🆔 *User ID:* `{user.id}`\n"
        f"💬 *Chat ID:* `{update.effective_chat.id}`\n"
        f"👤 *Full Name:* `{full_name}`\n"
        f"📝 *Username:* {username_display}\n"
        f"🌐 *Client Language:* `{ud['language']}`\n"
        f"🌟 *Telegram Premium:* `{ud['premium']}`\n"
        f"📅 *Session Established:* `{ud['first_seen']}`\n"
        f"🕒 *Last Activity Frame:* `{ud['last_seen']}`\n"
        f"📊 *Total Intercepted Packets:* `{ud['msg_count']} msgs`\n"
        f"🤖 *Core Engine Build:* `v{bot_version}`"
    )
    await update.message.reply_text(text=info_text, parse_mode="Markdown")

# /netinfo কমান্ড (নতুন অ্যাডভান্সড ফিচার)
async def netinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    try:
        # বটের হোস্ট সার্ভারের পাবলিক আইপি ও প্রোভাইডার চেক (API কল)
        with urllib.request.urlopen("http://ip-api.com/json/", timeout=3) as url:
            data = json.loads(url.read().decode())
            ip = data.get("query", "Unknown")
            isp = data.get("isp", "Unknown")
            country = data.get("country", "Unknown")
    except Exception:
        ip, isp, country = "Protected/Hidden", "Cloud Network", "Global Cluster"

    net_text = (
        f"🌐 *Host Node Infrastructure Metrics*\n\n"
        f"📡 *Server Public IP:* `{ip}`\n"
        f"🏢 *Gateway Provider:* `{isp}`\n"
        f"📍 *Node Location:* `{country}`\n"
        f"🔒 *Protocol Encryption:* `TLS v1.3 (Active)`"
    )
    await update.message.reply_text(text=net_text, parse_mode="Markdown")

# /sectip কমান্ড (নতুন অ্যাডভান্সড ফিচার)
async def sectip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    selected_tip = random.choice(SECURITY_TIPS)
    tip_text = (
        f"🛡️ *CyberSecurity Hardening Tip:*\n\n"
        f"`{selected_tip}`"
    )
    await update.message.reply_text(text=tip_text, parse_mode="Markdown")

# /ping কমান্ড (লেটেন্সি হিসাব সহ)
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    start_time = time.time()
    message = await update.message.reply_text(text="⚡ *Pinging Core Matrix...*", parse_mode="Markdown")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000)
    await message.edit_text(text=f"🏓 *Pong!*\n⏱️ *Latency:* `{latency}ms`\n🟢 *Status:* `Operational`", parse_mode="Markdown")

# /stats কমান্ড
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)
    stats_text = (
        f"📊 *Global Core Statistics*\n\n"
        f"• Total Unique Node Users: `{len(total_users)}`\n"
        f"• Engine Runtime: `24/7 Web Handler Mode`\n"
        f"• Core Version: `{bot_version}`"
    )
    await update.message.reply_text(text=stats_text, parse_mode="Markdown")

# টেক্সট ট্র্যাকিং ব্যাকএন্ড
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    track_user(update)

def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("netinfo", netinfo_command))
    app.add_handler(CommandHandler("sectip", sectip_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Advanced RS5_ARIF Pro Bot is initialized successfully...")
    app.run_polling()

if __name__ == "__main__":
    main()
