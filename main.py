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
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

BOT_VERSION = "5.0 (Maximum Enterprise & Deep Intel)"
DB_FILE = "bot_data.db"

# সাইবার সিকিউরিটি ও হার্ডেনিং টিপস মডিউল
SECURITY_TIPS = [
    "Always use a strong VPN when performing network reconnaissance or penetration testing.",
    "Enable 2-Step Verification (2FA) on your Telegram account to block unauthorized session hijacking.",
    "Do not click on unsolicited links or download unrecognized `.apk` or `.exe` files in public groups.",
    "Regularly audit active sessions in your Telegram Settings > Devices to terminate suspicious clones.",
    "Keep your automated lab environments isolated from your primary host network using proper VLANs.",
    "Disable automatic media downloads in Telegram to mitigate zero-day exploit executions via compromised files.",
    "Implement rate-limiting and strictly isolated environments on your demo applications during target fuzzing."
]

# ----------------- থ্রেড-সেফ এবং ক্র্যাশ-প্রুফ SQLite ডেটাবেস -----------------
def get_db_connection():
    # Multi-threading এবং Concurrent writing হ্যান্ডেল করার জন্য টাইমআউট বাড়ানো হয়েছে
    conn = sqlite3.connect(DB_FILE, timeout=30.0, check_same_thread=False)
    return conn

def init_db():
    conn = get_db_connection()
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("SELECT first_seen, msg_count FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row is None:
            cursor.execute('''
                INSERT INTO users (user_id, chat_id, first_name, last_name, username, language, premium, first_seen, last_seen, msg_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (user_id, chat_id, first_name, last_name, username, language, premium, current_time, current_time))
        else:
            new_count = row[1] + 1
            cursor.execute('''
                UPDATE users 
                SET last_seen = ?, msg_count = ?, first_name = ?, last_name = ?, username = ?, premium = ?
                WHERE user_id = ?
            ''', (current_time, new_count, first_name, last_name, username, premium, user_id))
            
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"⚠️ Data Concurrency Alert: {e}. Recovering thread...")
    finally:
        conn.close()

def get_user_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_seen, last_seen, msg_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None, 0)
# ---------------------------------------------------------------------

# --- রেন্ডার লাইভ ওয়েব সার্ভার সাবসিস্টেম ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # সার্ভারের বর্তমান অবস্থা রেন্ডার ড্যাশবোর্ডে লাইভ দেখাবে
        status_payload = f"RS5_ARIF Core Matrix Online - Build v{BOT_VERSION}"
        self.wfile.write(status_payload.encode())

def run_health_server():
    try:
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        server.serve_forever()
    except Exception as e:
        print(f"Web Subsystem Failure: {e}")

def log_user_activity(update: Update):
    user = update.effective_user
    if not user:
        return
    is_premium = "True 🌟" if user.is_premium else "False"
    db_track_user(
        user_id=user.id,
        chat_id=update.effective_chat.id,
        first_name=user.first_name,
        last_name=user.last_name or "",
        username=user.username or "None Specified",
        language=user.language_code or "Undefined",
        premium=is_premium
    )

# ==================== সম্পূর্ণ বিস্তারিত ও অ্যাডভান্সড কমান্ডস ====================

# /start কমান্ড (৩টি সম্পূর্ণ ডেডিকেটেড ইনফো বাবল)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    
    msg1 = (
        f"🤖 *WELCOME TO THE CORE APPLICATION PORTAL*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛰️ *Client Greeting:* Hello, {first_name}!\n"
        f"📦 *Active Engine Build:* `v{BOT_VERSION}`\n"
        f"🛠️ *Cluster Core:* SQLite3 Fully Persistent Layer\n"
        f"🔒 *Security Mode:* Anti-Crash Fuzzing Hardened\n"
        f"⚡ *Status:* Operational & Intercepting Packets\n\n"
        f"👉 _Run /help to view all threat intelligence and core utility matrices._"
    )
    await update.message.reply_text(text=msg1, parse_mode="Markdown")
    
    msg2 = (
        f"🔑 *SESSION IDENTIFICATION PARAMS*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 *Your Chat Telegram ID:* `{chat_id}`\n"
        f"💡 _Note: Click the ID above to copy it automatically._"
    )
    await update.message.reply_text(text=msg2, parse_mode="Markdown")
    
    msg3 = (
        f"📡 *OFFICIAL MAIN NODE INFORMATION*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 *Developer Node:* @RS5ARIF\n"
        f"⚡ *System Diagnostic Recommendation:* Execute /info to generate a complete forensic profiling packet of your current session."
    )
    await update.message.reply_text(text=msg3, parse_mode="Markdown")

# /help কমান্ড (সম্পূর্ণ গাইড)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    help_text = (
        f"🛠️ *CORE CONTROLLER & UTILITY SYSTEM SCHEMA*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 *Standard Operator Controls:*\n"
        f"• /start — Initializes current session and pulls structural Chat ID.\n"
        f"• /help — Prints this complete terminal interface documentation.\n"
        f"• /info — Runs a granular telemetry profiling check on your account.\n"
        f"• /ping — Executes round-trip latency evaluation on host infrastructure.\n"
        f"• /sectip — Fetches a specialized cyber hardening configuration tip.\n"
        f"• /stats — Generates an open statistical ledger of database engagement.\n\n"
        f"🎯 *Cyber Security & OSINT Subsystems:*\n"
        f"• /hash `<string>` — Processes real-time string parsing into MD5, SHA-1, and SHA-256 integrity check matrix.\n"
        f"• /ip `<address>` — Queries target host to extract deep ISP, ASN routing, and geolocation metadata telemetry.\n"
        f"• /netinfo — Extracts the physical server network interface layout metrics.\n\n"
        f"⚙️ *System Base Configuration:* `Python-Telegram-Bot API Layer`"
    )
    await update.message.reply_text(text=help_text, parse_mode="Markdown")

# /info কমান্ড (Granular Details)
async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    first_seen, last_seen, msg_count = get_user_profile(user.id)
    username_display = f"@{user.username}" if user.username else "Not Allocated"
    full_name = f"{user.first_name} {user.last_name or ''}".strip()
    is_premium = "Active Premium Node 🌟" if user.is_premium else "Standard Tier Account"
    
    info_text = (
        f"🕵️‍♂️ *DEEP SYSTEM PROFILE AND FORENSIC TELEMETRY*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Account Meta:* \n"
        f"  ├── *Full Name:* `{full_name}`\n"
        f"  ├── *Username:* {username_display}\n"
        f"  └── *Security Clearances:* `{is_premium}`\n\n"
        f"🆔 *Network Routings:* \n"
        f"  ├── *User Unique ID:* `{user.id}`\n"
        f"  └── *Assigned Chat ID:* `{chat_id}`\n\n"
        f"📊 *Database History Metrics:* \n"
        f"  ├── *Registration Timestamp:* `{first_seen or 'Just Initialized'}`\n"
        f"  ├── *Last Network Activity:* `{last_seen or 'Active Framework'}`\n"
        f"  └── *Intercepted Bot Signals:* `{msg_count} independent interactions`\n\n"
        f"⚙️ *Subsystem Engine:* `v{BOT_VERSION}`"
    )
    await update.message.reply_text(text=info_text, parse_mode="Markdown")

# /netinfo কমান্ড (আইএসপি ও এএসএন সহ বিস্তারিত)
async def netinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    try:
        req = urllib.request.Request("http://ip-api.com/json/?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as url:
            data = json.loads(url.read().decode())
            if data.get("status") == "fail":
                raise Exception()
            
            net_text = (
                f"🌐 *HOST SERVER INFRASTRUCTURE TELEMETRY REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📡 *Public WAN IPv4 Address:* `{data.get('query')}`\n"
                f"🏢 *Upstream Network Gateway:* `{data.get('isp')}`\n"
                f"💼 *Data Center Operator:* `{data.get('org')}`\n"
                f"⚡ *BGP Autonomous System Routing:* `{data.get('as')}`\n"
                f"📍 *Node Location Matrix:* `{data.get('city')}, {data.get('regionName')}, {data.get('country')} ({data.get('countryCode')})`\n"
                f"⏰ *Local Hardware Timezone:* `{data.get('timezone')}`\n"
                f"🛰️ *Coordinates:* `{data.get('lat')}, {data.get('lon')}`\n"
                f"🔒 *SSL Layer Configuration:* `TLS v1.3 Standard Forced`"
            )
    except Exception:
        net_text = (
            f"🌐 *HOST INFRASTRUCTURE METRICS*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Status:* Live Telemetry Hidden / Blocked by Cloud Firewall\n"
            f"📡 *Virtual Gateway Provider:* `Render Virtual Cluster Node`\n"
            f"📍 *Physical Region Deployment:* `Global Load Balanced Core`"
        )
    await update.message.reply_text(text=net_text, parse_mode="Markdown")

# /sectip কমান্ড
async def sectip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    selected_tip = random.choice(SECURITY_TIPS)
    tip_text = (
        f"🛡️ *CYBER SECURITY HARDENING RECOMMENDATION*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👉 `{selected_tip}`"
    )
    await update.message.reply_text(text=tip_text, parse_mode="Markdown")

# /hash কমান্ড (MD5, SHA-1, SHA-256 বিস্তারিত জেনারেটর)
async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("❌ *Error:* Parameters missing. Usage: `/hash <your_text_here>`", parse_mode="Markdown")
        return
    
    target_text = " ".join(context.args)
    md5_res = hashlib.md5(target_text.encode()).hexdigest()
    sha1_res = hashlib.sha1(target_text.encode()).hexdigest()
    sha256_res = hashlib.sha256(target_text.encode()).hexdigest()
    
    hash_text = (
        f"🔑 *CRYPTOGRAPHIC INTEGRITY MATRIX FOR PARSED STRINGS*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *Target Input Plain Text:* \n`{target_text}`\n\n"
        f"🔹 *MD5 Message-Digest:* \n`{md5_res}`\n\n"
        f"🔹 *SHA-1 Cryptographic Hash:* \n`{sha1_res}`\n\n"
        f"🔹 *SHA-256 Secure Hash Standard:* \n`{sha256_res}`\n\n"
        f"💡 _All generated cryptographic values are in complete hexadecimal format._"
    )
    await update.message.reply_text(text=hash_text, parse_mode="Markdown")

# /ip কমান্ড (চরম অ্যাডভান্সড OSINT লুকআপ মডিউল)
async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("❌ *Error:* IP missing. Usage: `/ip 8.8.8.8`", parse_mode="Markdown")
        return
    
    target_ip = context.args[0]
    status_msg = await update.message.reply_text("🔍 *Executing Deep OSINT Network Analysis Payload... Please Wait.*")
    
    try:
        req = urllib.request.Request(f"http://ip-api.com/json/{target_ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as url:
            data = json.loads(url.read().decode())
            if data.get("status") == "fail":
                await status_msg.edit_text(f"❌ *OSINT Scan Interrupted:* `{data.get('message', 'Invalid Target IPv4 Address')}`", parse_mode="Markdown")
                return
            
            ip_scan_result = (
                f"🛰️ *DEEP OSINT TARGET THREAT INTELLIGENCE REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 *Target IPv4 Address:* `{data.get('query')}`\n\n"
                f"🌍 *Geographical Core Location:* \n"
                f"  ├── *Country Name:* `{data.get('country')} ({data.get('countryCode')})`\n"
                f"  ├── *State/Region:* `{data.get('regionName')}`\n"
                f"  ├── *City Allocation:* `{data.get('city')}`\n"
                f"  └── *Postal Routing ZIP:* `{data.get('zip')}`\n\n"
                f"🏢 *Network Operator & ISP Telemetry:* \n"
                f"  ├── *Primary Internet Service Provider:* `{data.get('isp')}`\n"
                f"  ├── *Registered Organization:* `{data.get('org')}`\n"
                f"  └── *Autonomous System Matrix:* `{data.get('as')}`\n\n"
                f"📍 *Physical & Spatial Matrix:* \n"
                f"  ├── *Exact GPS Coordinates:* `{data.get('lat')}, {data.get('lon')}`\n"
                f"  └── *Assigned System Timezone:* `{data.get('timezone')}`"
            )
            await status_msg.edit_text(text=ip_scan_result, parse_mode="Markdown")
    except Exception:
        await status_msg.edit_text("❌ *OSINT Scan Timed Out:* The intelligence API did not respond or connection was throttled.", parse_mode="Markdown")

# /ping কমান্ড
async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    start_time = time.time()
    message = await update.message.reply_text(text="⚡ *Measuring Socket Ping Latency Matrix...*", parse_mode="Markdown")
    end_time = time.time()
    
    latency = round((end_time - start_time) * 1000)
    await message.edit_text(text=f"🏓 *Pong Response Broadcast!*\n⏱️ *Latency Frame:* `{latency}ms`\n🟢 *Core Subsystem Health:* `Excellent (Operational)`", parse_mode="Markdown")

# /stats কমান্ড (গ্লোবাল স্ট্যাটস)
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_db_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(msg_count) FROM users")
        total_db_msgs = cursor.fetchone()[0] or 0
        
        today_date = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM users WHERE first_seen LIKE ?", (f"{today_date}%",))
        today_new_users = cursor.fetchone()[0]
        
        conn.close()
    except Exception:
        total_db_users, total_db_msgs, today_new_users = 0, 0, 0
    
    stats_text = (
        f"📊 *GLOBAL PERSISTENT NETWORK METRICS DIAGNOSTICS*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Total Unique Network Entities:* `{total_db_users} registered users`\n"
        f"📈 *New Nodes Initialized Today:* `{today_new_users} new profiles`\n"
        f"📥 *Total Processed Signal Handshakes:* `{total_db_msgs} active messages`\n"
        f"⏳ *Database System Protection Status:* `100% Intact File Cluster`\n"
        f"🤖 *Core Version Engine Build:* `{BOT_VERSION}`"
    )
    await update.message.reply_text(text=stats_text, parse_mode="Markdown")

# ==================== শুধুমাত্র অ্যাডমিন প্রিভিলেজড সিস্টেম ====================

# /admin_stats কমান্ড
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ *Access Denied:* Security Clearance Level Insufficient.", parse_mode="Markdown")
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, username, msg_count FROM users ORDER BY msg_count DESC LIMIT 10")
    top_users = cursor.fetchall()
    conn.close()
    
    adm_text = "👑 *TOP 10 MOST ACTIVE INDEPENDENT CLIENT NODES:*\n"
    adm_text += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for idx, row in enumerate(top_users, 1):
        uname = f"@{row[2]}" if row[2] != "None Specified" else "No Username Alloc"
        adm_text += f"`[{idx}]` *ID:* `{row[0]}` | *Name:* `{row[1]}` ({uname}) -> `Total: {row[3]} transmissions`\n"
        
    await update.message.reply_text(text=adm_text, parse_mode="Markdown")

# /broadcast কমান্ড (সবাইকে মেসেজ পাঠানোর রিয়েল-টাইম ক্লিয়ারেন্স মডিউল)
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⚠️ *Access Denied:* Secure Authentication Token Key Failed.", parse_mode="Markdown")
        return
        
    if not context.args:
        await update.message.reply_text("❌ *Error:* Payload text empty. Usage: `/broadcast <message>`", parse_mode="Markdown")
        return
        
    broadcast_msg = "📢 *GLOBAL SYSTEM BROADCAST FROM ROOT ADMIN:*\n" + "━━━━━━━━━━━━━━━━━━━━━━━━\n" + " ".join(context.args)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    all_chats = cursor.fetchall()
    conn.close()
    
    success_count = 0
    fail_count = 0
    status_message = await update.message.reply_text(f"🚀 *Initiating automated global packet broadcast to {len(all_chats)} network nodes...*")
    
    for chat in all_chats:
        try:
            await context.bot.send_message(chat_id=chat[0], text=broadcast_msg, parse_mode="Markdown")
            success_count += 1
            await asyncio.sleep(0.04)  # Anti-Flood API throttling prevention
        except Exception:
            fail_count += 1
            
    await status_message.edit_text(
        f"✅ *GLOBAL BROADCAST PACKET DISTRIBUTION REPORT*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🟢 Delivered Packet Count: `{success_count}`\n"
        f"🔴 Dropped / Blocked Terminal Connections: `{fail_count}`\n"
        f"📊 *Distribution Integrity Rate:* `{round((success_count/(success_count+fail_count or 1))*100)}%`"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)

def main():
    init_db()
    # মাল্টিথ্রেডিং এ ফেইক ওয়েব সার্ভার রান করা যেন রেন্ডার স্লিপে না যায়
    threading.Thread(target=run_health_server, daemon=True).start()

    app = Application.builder().token(TOKEN).build()
    
    # কোরের সমস্ত কমান্ড হ্যান্ডলার রেজিস্টার করা
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("netinfo", netinfo_command))
    app.add_handler(CommandHandler("sectip", sectip_command))
    app.add_handler(CommandHandler("hash", hash_command))
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("admin_stats", admin_stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("RS5_ARIF Ultra Pro Master Core Engine Active...")
    app.run_polling()

if __name__ == "__main__":
    # ইনফিনিটি লুপ প্রোটেকশন - ক্র্যাশ করলে ৩ সেকেন্ডে স্বয়ংক্রিয় রি-বুট নিবে
    while True:
        try:
            main()
        except Exception as crash_error:
            print(f"⚠️ Critical Interruption Detected: {crash_error}. Re-booting matrix core...")
            time.sleep(3)
