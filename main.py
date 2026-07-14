import os
import asyncio
import time
from datetime import datetime
import random
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import urllib.request
import json
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ১. Render এনভায়রনমেন্ট ভ্যারিয়েবল থেকে টোকেন ও অ্যাডমিন আইডি নেওয়া
TOKEN = os.environ.get("BOT_TOKEN")
# [নিরাপত্তা টিপস]: Render-এর Environment Variable-এ ADMIN_ID কী-তে আপনার নিজের Telegram Chat ID (যেমন: 8027584152) বসিয়ে দেবেন।
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

BOT_VERSION = "4.0 (Ultra Pro + Database)"

# সাইবার সিকিউরিটি টিপস পুল
SECURITY_TIPS = [
    "Always use a strong VPN when performing network reconnaissance or penetration testing.",
    "Enable 2-Step Verification (2FA) on your Telegram account to block unauthorized session hijacking.",
    "Do not click on unsolicited links or download unrecognized `.apk` or `.exe` files in public groups.",
    "Regularly audit active sessions in your Telegram Settings > Devices to terminate suspicious clones.",
    "Keep your automated lab environments isolated from your primary host network using proper VLANs."
]

# ----------------- SQLite ডেটাবেস মডিউল -----------------
DB_FILE = "bot_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            language TEXT,
            premium TEXT,
            first_seen TEXT,
            last_seen TEXT,
            msg_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def db_track_user(user_id, chat_id, first_name, last_name, username, language, premium):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("SELECT first_seen, msg_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        # নতুন ইউজার রেজিস্টার্ড হচ্ছে
        cursor.execute('''
            INSERT INTO users (user_id, chat_id, first_name, last_name, username, language, premium, first_seen, last_seen, msg_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (user_id, chat_id, first_name, last_name, username, language, premium, current_time, current_time))
    else:
        # পুরাতন ইউজারের ডেটা ও মেসেজ কাউন্ট আপডেট হচ্ছে
        new_count = row[1] + 1
        cursor.execute('''
            UPDATE users 
            SET last_seen = ?, msg_count = ?, first_name = ?, last_name = ?, username = ?, premium = ?
            WHERE user_id = ?
        ''', (current_time, new_count, first_name, last_name, username, premium, user_id))
        
    conn.commit()
    conn.close()

def get_user_profile(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT first_seen, last_seen, msg_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None, 0)
# --------------------------------------------------

# --- রেন্ডার ২৪ ঘণ্টা লাইভ রাখার জন্য ফেইক ওয়েব সার্ভার ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Ultra Bot Engine Running 24/7 with DB!")

def run_health_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()
# --------------------------------------------------

# ইউজারের মেসেজ ইন্টারসেপ্ট করে ট্র্যাকিং মডিউলে পাঠানো
def log_user_activity(update: Update):
    user = update.effective_user
    if not user:
        return
    is_premium = "Yes 🌟" if user.is_premium else "No"
    db_track_user(
        user_id=user.id,
        chat_id=update.effective_chat.id,
        first_name=user.first_name,
        last_name=user.last_name or "",
        username=user.username or "Not set",
        language=user.language_code or "Unknown",
        premium=is_premium
    )

# /start কমান্ড (আলাদা ৩টি মেসেজ বাবল)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    
    msg1 = (
        f"👋 *Welcome to the Advanced Hub, {first_name}!*\n\n"
        f"🤖 *RS5_ARIF Pro Core Engine* v{BOT_VERSION}\n"
        f"• Secure SQLite Database Cluster Connected\n"
        f"• Crypto Hash & IP Intel Subsystems Loaded\n"
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
    log_user_activity(update)
    help_text = (
        f"🛠️ *Advanced Bot Core Menu*\n\n"
        f"📋 *Core Commands:*\n"
        f"• /start - Activate session & pull Chat ID\n"
        f"• /help - Display this advanced controller schema\n"
        f"• /info - Generate deep profile analytics payload\n"
        f"• /netinfo - Query bot infrastructure network state\n"
        f"• /sectip - Fetch a random cybersecurity/hardening tip\n"
        f"• /hash `<text>` - Generate MD5, SHA1, SHA256 integrity check\n"
        f"• /ip `<address>` - Query Deep IP OSINT Intelligence data\n"
        f"• /ping - Measure exact core response latency\n"
        f"• /stats - Broadcast total operational database stats\n\n"
        f"⚡ *System Architecture:*\n"
        f"• Database Engine: SQLite3 (Persistent Layer)\n"
        f"• Native Markdown Auto-Copy Hooks Enabled\n\n"
        f"📡 *Network Operations:* @RS5ARIF"
    )
    await update.message.reply_text(text=help_text, parse_mode="Markdown")

# /info কমান্ড (অ্যাডভান্সড ডাটাবেস ভ্যারিয়েন্ট)
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    first_seen, last_seen, msg_count = get_user_profile(user.id)
    username_display = f"@{user.username}" if user.username else "Not set"
    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    is_premium = "Yes 🌟" if user.is_premium else "No"
    
    info_text = (
        f"🕵️‍♂️ *Deep Profile Analytics Generated*\n\n"
        f"🆔 *User ID:* `{user.id}`\n"
        f"💬 *Chat ID:* `{chat_id}`\n"
        f"👤 *Full Name:* `{full_name}`\n"
        f"📝 *Username:* {username_display}\n"
        f"🌐 *Client Language:* `{user.language_code or 'Unknown'}`\n"
        f"🌟 *Telegram Premium:* `{is_premium}`\n"
        f"📅 *Session Established:* `{first_seen}`\n"
        f"🕒 *Last Activity Frame:* `{last_seen}`\n"
        f"📊 *Total Intercepted Packets:* `{msg_count} msgs`\n"
        f"🤖 *Core Engine Build:* `v{BOT_VERSION}`"
    )
    await update.message.reply_text(text=info_text, parse_mode="Markdown")

# /netinfo কমান্ড
async def netinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    try:
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

# /sectip কমান্ড
async def sectip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    selected_tip = random.choice(SECURITY_TIPS)
    tip_text = (
        f"🛡️ *CyberSecurity Hardening Tip:*\n\n"
        f"`{selected_tip}`"
    )
    await update.message.reply_text(text=tip_text, parse_mode="Markdown")

# /hash কমান্ড (নতুন অ্যাডভান্সড ফিচার)
async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/hash your_text_here`", parse_mode="Markdown")
        return
    
    target_text = " ".join(context.args)
    md5_res = hashlib.md5(target_text.encode()).hexdigest()
    sha1_res = hashlib.sha1(target_text.encode()).hexdigest()
    sha256_res = hashlib.sha256(target_text.encode()).hexdigest()
    
    hash_text = (
        f"🔑 *Cryptographic Hash Payload Generated*\n\n"
        f"📝 *Plain Text:* `{target_text}`\n\n"
        f"🔹 *MD5:* `{md5_res}`\n\n"
        f"🔹 *SHA-1:* `{sha1_res}`\n\n"
        f"🔹 *SHA-256:* `{sha256_res}`"
    )
    await update.message.reply_text(text=hash_text, parse_mode="Markdown")

# /ip কমান্ড (নতুন অ্যাডভান্সড OSINT ফিচার)
async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/ip 8.8.8.8`", parse_mode="Markdown")
        return
    
    target_ip = context.args[0]
    await update.message.reply_text("🔍 *Running Threat Intelligence Scan...*")
    
    try:
        with urllib.request.urlopen(f"http://ip-api.com/json/{target_ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query", timeout=4) as url:
            data = json.loads(url.read().decode())
            if data.get("status") == "fail":
                await update.message.reply_text(f"❌ *Scan Failed:* {data.get('message', 'Invalid IP')}", parse_mode="Markdown")
                return
            
            ip_scan_result = (
                f"🛰️ *OSINT Target Scan Report:*\n\n"
                f"📌 *Target IP:* `{data.get('query')}`\n"
                f"🌍 *Country/City:* `{data.get('country')}, {data.get('city')} ({data.get('regionName')})`\n"
                f"📮 *ZIP Code:* `{data.get('zip')}`\n"
                f"⏰ *Timezone:* `{data.get('timezone')}`\n"
                f"🏢 *ISP NetName:* `{data.get('isp')}`\n"
                f"💼 *Organization:* `{data.get('org')}`\n"
                f"📡 *ASN Matrix:* `{data.get('as')}`\n"
                f"📍 *Geo Coordinates:* `{data.get('lat')}, {data.get('lon')}`"
            )
            await update.message.reply_text(text=ip_scan_result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ *Network Error:* Timeout or API Rate-limited.", parse_mode="Markdown")

# /ping কমান্ড
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    start_time = time.time()
    message = await update.message.reply_text(text="⚡ *Pinging Core Matrix...*", parse_mode="Markdown")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000)
    await message.edit_text(text=f"🏓 *Pong!*\n⏱️ *Latency:* `{latency}ms`\n🟢 *Status:* `Operational`", parse_mode="Markdown")

# /stats কমান্ড (গ্লোবাল ডাটাবেস পরিসংখ্যান)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # মোট রেজিস্টার্ড ইউনিক ইউজার সংখ্যা
    cursor.execute("SELECT COUNT(*) FROM users")
    total_db_users = cursor.fetchone()[0]
    
    # বটের ইতিহাসে সর্বমোট চালা চালি হওয়া মেসেজ সংখ্যা
    cursor.execute("SELECT SUM(msg_count) FROM users")
    total_db_msgs = cursor.fetchone()[0] or 0
    
    # আজকের তারিখে নতুন কতজন ইউজার এসেছে
    today_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM users WHERE first_seen LIKE ?", (f"{today_date}%",))
    today_new_users = cursor.fetchone()[0]
    
    conn.close()
    
    stats_text = (
        f"📊 *Global Operational Metrics (Persistent)*\n\n"
        f"👥 *Total Unique Database Nodes:* `{total_db_users}`\n"
        f"📈 *Today's New Registered Nodes:* `{today_new_users}`\n"
        f"📥 *Total Intercepted Bot Signals:* `{total_db_msgs} interactions`\n"
        f"⏳ *Database System Uptime:* `Continuous (24/7 File Protected)`\n"
        f"🤖 *Core Version:* `{BOT_VERSION}`"
    )
    await update.message.reply_text(text=stats_text, parse_mode="Markdown")

# ----------------- অ্যাডমিন ও ব্রডকাস্ট কমান্ডস -----------------
# /admin_stats কমান্ড (শুধুমাত্র অ্যাডমিন দেখতে পারবে)
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ *Access Denied:* Unauthorized Security Clearance Level.", parse_mode="Markdown")
        return
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, username, msg_count FROM users ORDER BY msg_count DESC LIMIT 10")
    top_users = cursor.fetchall()
    conn.close()
    
    adm_text = "👑 *Top 10 Most Active Bot Users:*\n\n"
    for idx, row in enumerate(top_users, 1):
        uname = f"@{row[2]}" if row[2] != "Not set" else "No Username"
        adm_text += f"{idx}. `{row[0]}` - *{row[1]}* ({uname}) -> `{row[3]} msgs`\n"
        
    await update.message.reply_text(text=adm_text, parse_mode="Markdown")

# /broadcast কমান্ড (সব ইউজারকে একবারে মেসেজ পাঠানোর প্যানেল)
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ *Access Denied:* Admin credentials verification failed.", parse_mode="Markdown")
        return
        
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/broadcast Your global message here`", parse_mode="Markdown")
        return
        
    broadcast_msg = "📢 *Global Broadcast from Admin:*\n\n" + " ".join(context.args)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    all_chats = cursor.fetchall()
    conn.close()
    
    success_count = 0
    fail_count = 0
    
    status_message = await update.message.reply_text(f"🚀 *Initiating global broadcast transmission to {len(all_chats)} nodes...*")
    
    for chat in all_chats:
        try:
            await context.bot.send_message(chat_id=chat[0], text=broadcast_msg, parse_mode="Markdown")
            success_count += 1
            await asyncio.sleep(0.05) # রেট লিমিট এড়ানোর জন্য ক্ষুদ্র বিরতি
        except Exception:
            fail_count += 1
            
    await status_message.edit_text(
        f"✅ *Broadcast Transmission Complete!*\n\n"
        f"🟢 Success Deliveries: `{success_count}`\n"
        f"🔴 Failed/Blocked Connections: `{fail_count}`"
    )

# সাধারণ টেক্সট মেসেজ হ্যান্ডলার
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)

def main():
    init_db() # ডাটাবেস ইনিশিয়েট করা
    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    
    # হ্যান্ডলার বাইন্ডিং
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("netinfo", netinfo_command))
    app.add_handler(CommandHandler("sectip", sectip_command))
    app.add_handler(CommandHandler("hash", hash_command))
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("stats", stats_command))
    
    # অ্যাডমিন কমান্ডস
    app.add_handler(CommandHandler("admin_stats", admin_stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Ultra Advanced Persistent DB Bot is deployed and online...")
    app.run_polling()

if __name__ == "__main__":
    main()
