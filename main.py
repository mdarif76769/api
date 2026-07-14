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
import re
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

BOT_VERSION = "6.0 (Ultimate Security & Extended OSINT Build)"
DB_FILE = "bot_data.db"

SECURITY_TIPS = [
    "Always use a strong VPN when performing network reconnaissance or penetration testing.",
    "Enable 2-Step Verification (2FA) on your Telegram account to block unauthorized session hijacking.",
    "Do not click on unsolicited links or download unrecognized `.apk` or `.exe` files in public groups.",
    "Regularly audit active sessions in your Telegram Settings > Devices to terminate suspicious clones.",
    "Keep your automated lab environments isolated from your primary host network using proper VLANs."
]

# ----------------- SQLite ডেটাবেস -----------------
def get_db_connection():
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
                UPDATE users SET last_seen = ?, msg_count = ?, first_name = ?, last_name = ?, username = ?, premium = ? WHERE user_id = ?
            ''', (current_time, new_count, first_name, last_name, username, premium, user_id))
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()

def get_user_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_seen, last_seen, msg_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row if row else (None, None, 0)

# --- রেন্ডার ওয়েব সার্ভার ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f"RS5_ARIF Matrix Core Build v{BOT_VERSION} Online".encode())

def run_health_server():
    try:
        port = int(os.environ.get("PORT", 8080))
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        server.serve_forever()
    except Exception:
        pass

def log_user_activity(update: Update):
    user = update.effective_user
    if not user: return
    is_premium = "True 🌟" if user.is_premium else "False"
    db_track_user(user.id, update.effective_chat.id, user.first_name, user.last_name or "", user.username or "None", user.language_code or "Undefined", is_premium)

# ==================== কমান্ডস ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🤖 *WELCOME TO THE CORE APPLICATION PORTAL*\n━━━━━━━━━━━━━━━━━━━━━━━━\n🛰️ *Client:* Hello, {first_name}!\n📦 *Engine Build:* `v{BOT_VERSION}`\n🔒 *Security Mode:* Anti-Crash Fuzzing Hardened\n\n👉 _Run /help to view all threat intelligence modules._", parse_mode="Markdown")
    await update.message.reply_text(f"🔑 *SESSION IDENTIFICATION PARAMS*\n━━━━━━━━━━━━━━━━━━━━━━━━\n🆔 *Your Chat Telegram ID:* `{chat_id}`", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    help_text = (
        f"🛠️ *CORE CONTROLLER & UTILITY SYSTEM SCHEMA*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📋 *Standard Controls:*\n"
        f"• /start — Initializes session and pulls Chat ID.\n"
        f"• /help — Prints this system documentation.\n"
        f"• /info — Runs a granular telemetry profiling check.\n"
        f"• /ping — Latency evaluation on host infrastructure.\n"
        f"• /stats — Generates database engagement stats.\n"
        f"• /sectip — Fetches a cyber hardening configuration tip.\n\n"
        f"🎯 *Crypto & OSINT Subsystems:*\n"
        f"• /hash `<string>` — Generates MD5, SHA-1, and SHA-256 hashes.\n"
        f"• /dehash `<hash>` — Refers to Cloud OSINT DB to reverse/decrypt MD5 hashes.\n"
        f"• /ip `<address>` — Extracts deep ISP, ASN, and geo-metadata.\n"
        f"• /netinfo — Server network interface layout metrics."
    )
    await update.message.reply_text(text=help_text, parse_mode="Markdown")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    user = update.effective_user
    first_seen, last_seen, msg_count = get_user_profile(user.id)
    info_text = (
        f"🕵️‍♂️ *DEEP SYSTEM PROFILE AND FORENSIC TELEMETRY*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Account Meta:* \n"
        f"  ├── *Full Name:* `{user.first_name} {user.last_name or ''}`\n"
        f"  └── *Clearance:* `{'Premium 🌟' if user.is_premium else 'Standard'}`\n"
        f"🆔 *Routings:* \n"
        f"  ├── *User ID:* `{user.id}`\n"
        f"  └── *Chat ID:* `{update.effective_chat.id}`\n"
        f"📊 *Metrics:* \n"
        f"  ├── *First Seen:* `{first_seen or 'Just Now'}`\n"
        f"  └── *Total Transmissions:* `{msg_count} msgs`"
    )
    await update.message.reply_text(text=info_text, parse_mode="Markdown")

async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("❌ *Error:* Usage: `/hash <text>`", parse_mode="Markdown")
        return
    target_text = " ".join(context.args)
    hash_text = (
        f"🔑 *CRYPTOGRAPHIC INTEGRITY MATRIX*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *Plain Text:* `{target_text}`\n\n"
        f"🔹 *MD5:* `{hashlib.md5(target_text.encode()).hexdigest()}`\n\n"
        f"🔹 *SHA-1:* `{hashlib.sha1(target_text.encode()).hexdigest()}`\n\n"
        f"🔹 *SHA-256:* `{hashlib.sha256(target_text.encode()).hexdigest()}`"
    )
    await update.message.reply_text(text=hash_text, parse_mode="Markdown")

# 🔍 /dehash কমান্ড (নতুন ক্লাউড OSINT ডিক্রিপশন ফিচার)
async def dehash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("❌ *Error:* Usage: `/dehash <hash_value>`", parse_mode="Markdown")
        return
    
    input_hash = context.args[0].strip().lower()
    
    # ইনপুট ভ্যালিডেশন (MD5 সাধারণত ৩২ অক্ষরের হেক্স স্পেসিফিকেশন হয়)
    if not re.match(r"^[a-f0-9]{32}$", input_hash):
        await update.message.reply_text("❌ *Error:* Only **MD5** hashes (32 hex characters) are currently supported for OSINT lookup.", parse_mode="Markdown")
        return
        
    status_msg = await update.message.reply_text("⚡ *Querying Global Cyber Intelligence Databases...*")
    
    try:
        # Nitrxgen MD5 OSINT API ডেটাবেস কোয়েরি
        api_url = f"http://md5.nitrxgen.net/fetch.php?hash={input_hash}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=6) as response:
            decrypted_text = response.read().decode('utf-8').strip()
            
            if decrypted_text and not decrypted_text.startswith("ERROR"):
                result_text = (
                    f"🔓 *HASH DECRYPTION SUCCESSFUL (OSINT)*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧱 *Target MD5 Hash:* `{input_hash}`\n"
                    f"🔑 *Decrypted Plain Text:* `{decrypted_text}`\n\n"
                    f"🟢 *Status:* Match Found in Cloud Rainbow Tables."
                )
                await status_msg.edit_text(text=result_text, parse_mode="Markdown")
            else:
                # ১ম ডাটাবেসে না পাওয়া গেলে ২য় অল্টারনেティブ API ট্রাই করবে
                api_url_2 = f"https://md5online.org/api.php?d=1&h={input_hash}"
                req2 = urllib.request.Request(api_url_2, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req2, timeout=5) as resp2:
                    decrypted_text_2 = resp2.read().decode('utf-8').strip()
                    if decrypted_text_2 and "not found" not in decrypted_text_2.lower():
                        result_text = (
                            f"🔓 *HASH DECRYPTION SUCCESSFUL (OSINT Tier-2)*\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🧱 *Target MD5 Hash:* `{input_hash}`\n"
                            f"🔑 *Decrypted Plain Text:* `{decrypted_text_2}`\n"
                        )
                        await status_msg.edit_text(text=result_text, parse_mode="Markdown")
                        return
                        
                await status_msg.edit_text(f"❌ *OSINT Dehash Failed:* Hash not found in global rainbow tables. (It might be a highly complex custom password).", parse_mode="Markdown")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ *Subsystem Timeout:* API Network interface throttled. Error: {str(e)[:30]}")

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("❌ *Usage:* `/ip 8.8.8.8`", parse_mode="Markdown")
        return
    target_ip = context.args[0]
    status_msg = await update.message.reply_text("🔍 *Executing Deep OSINT Network Analysis...*")
    try:
        req = urllib.request.Request(f"http://ip-api.com/json/{target_ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as url:
            data = json.loads(url.read().decode())
            if data.get("status") == "fail":
                await status_msg.edit_text(f"❌ *Scan Failed:* `{data.get('message')}`")
                return
            ip_scan_result = (
                f"🛰️ *DEEP OSINT TARGET REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 *Target IPv4:* `{data.get('query')}`\n"
                f"🌍 *Geo Core:* `{data.get('city')}, {data.get('country')}`\n"
                f"🏢 *ISP NetName:* `{data.get('isp')}`\n"
                f"📡 *ASN Matrix:* `{data.get('as')}`\n"
                f"📍 *GPS Matrix:* `{data.get('lat')}, {data.get('lon')}`"
            )
            await status_msg.edit_text(text=ip_scan_result, parse_mode="Markdown")
    except Exception:
        await status_msg.edit_text("❌ *OSINT Scan Timed Out.*")

async def netinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    try:
        req = urllib.request.Request("http://ip-api.com/json/", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as url:
            data = json.loads(url.read().decode())
            await update.message.reply_text(f"🌐 *SERVER INFRASTRUCTURE METRICS*\n━━━━━━━━━━━━━━━━━━━━━━━━\n📡 *WAN IPv4:* `{data.get('query')}`\n🏢 *Gateway ISP:* `{data.get('isp')}`\n📍 *Location:* `{data.get('country')}`", parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("🌐 *Render Cluster Layer Node Protected.*")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    start_time = time.time()
    message = await update.message.reply_text("⚡ *Measuring Latency...*")
    await message.edit_text(f"🏓 *Pong!*\n⏱️ *Latency Frame:* `{round((time.time() - start_time) * 1000)}ms`\n🟢 *Status:* `Operational`", parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(msg_count) FROM users")
        total_msgs = cursor.fetchone()[0] or 0
        conn.close()
    except Exception:
        total_users, total_msgs = 0, 0
    await update.message.reply_text(f"📊 *GLOBAL PERSISTENT METRICS*\n━━━━━━━━━━━━━━━━━━━━━━━━\n👥 *Total Entities:* `{total_users} nodes`\n📥 *Total Handshakes:* `{total_msgs} messages`", parse_mode="Markdown")

async def sectip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    await update.message.reply_text(f"🛡️ *HARDENING RECOMMENDATION*\n━━━━━━━━━━━━━━━━━━━━━━━━\n👉 `{random.choice(SECURITY_TIPS)}`", parse_mode="Markdown")

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, msg_count FROM users ORDER BY msg_count DESC LIMIT 10")
    top_users = cursor.fetchall()
    conn.close()
    adm_text = "👑 *TOP ACTIVE CLIENT NODES:*\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for idx, row in enumerate(top_users, 1):
        adm_text += f"`[{idx}]` *ID:* `{row[0]}` | *Name:* `{row[1]}` -> `{row[2]} msgs`\n"
    await update.message.reply_text(text=adm_text, parse_mode="Markdown")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or not context.args: return
    broadcast_msg = "📢 *GLOBAL SYSTEM BROADCAST FROM ROOT ADMIN:*\n━━━━━━━━━━━━━━━━━━━━━━━━\n" + " ".join(context.args)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    all_chats = cursor.fetchall()
    conn.close()
    status_message = await update.message.reply_text("🚀 *Broadcasting payload...*")
    success = 0
    for chat in all_chats:
        try:
            await context.bot.send_message(chat_id=chat[0], text=broadcast_msg, parse_mode="Markdown")
            success += 1
            await asyncio.sleep(0.04)
        except Exception: pass
    await status_message.edit_text(f"✅ *BROADCAST COMPLETE*\n━━━━━━━━━━━━━━━━━━━━━━━━\n🟢 Success Nodes: `{success}`\n🔴 Dropped Nodes: `{len(all_chats)-success}`")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)

def main():
    init_db()
    threading.Thread(target=run_health_server, daemon=True).start()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("netinfo", netinfo_command))
    app.add_handler(CommandHandler("sectip", sectip_command))
    app.add_handler(CommandHandler("hash", hash_command))
    app.add_handler(CommandHandler("dehash", dehash_command))
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("admin_stats", admin_stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    app.run_polling()

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception:
            time.sleep(3)
