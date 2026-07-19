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

TOKEN = os.environ.get("8225542034:AAHa1La3HGN-E9xBqlLYQjAOztX-K7zZst4")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 0))

BOT_VERSION = "9.0 (RS5_ARIF Pro Core Intel Build)"
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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT first_seen, last_seen, msg_count FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row if row else (None, None, 0)
    except Exception:
        return (None, None, 0)

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
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # ✨ মেসেজ ১: প্রধান স্বাগতম কার্ড (আপনার স্ক্রিনশটের হুবহু ক্লিন ও সুন্দর লেআউট)
    welcome_msg = (
        f"👋 Welcome, *{user.first_name}*!\n\n"
        f"🤖 I'm your Chat ID Bot! I can help you with:\n"
        f"• Getting your Chat ID\n"
        f"• User statistics\n"
        f"• Bot information\n\n"
        f"Type /help for all commands!"
    )
    await update.message.reply_text(text=welcome_msg, parse_mode="Markdown")
    
    # ✨ মেসেজ ২: চ্যাট আইডি কার্ড
    id_msg = f"✨ *Your Chat ID is:* `{chat_id}`"
    await update.message.reply_text(text=id_msg, parse_mode="Markdown")
    
    # ✨ মেসেজ ৩: চ্যানেল জয়েন ও ইনফো টিপস (আপনার নিজস্ব RS5ARIF ব্র্যান্ডিং সহ বিস্তারিত তথ্য)
    tip_msg = (
        f"🌟 *Join Our Channel:* @RS5ARIF\n"
        f"💡 *Tip:* Use /info to see your detailed information!\n\n"
        f"📋 *Your Detailed Metadata Profile:*\n"
        f"• First Name: `{user.first_name}`\n"
        f"• Last Name: `{user.last_name or 'None'}`\n"
        f"• Username: `@{user.username or 'None'}`\n"
        f"• Language: `{user.language_code or 'Unknown'}`\n"
        f"• Premium Account: `{'Yes 🌟' if user.is_premium else 'No'}`"
    )
    await update.message.reply_text(text=tip_msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    help_text = (
        f"🛠️ *SYSTEM COMMAND CENTER & MANUAL*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🚀 *Standard System Commands:*\n"
        f"• /start — Reinitializes bot session & pulls ID info.\n"
        f"• /help — Displays this command dashboard guide.\n"
        f"• /info — Fetches analytical database telemetry on your profile.\n"
        f"• /ping — Measures active network latency to the cloud host.\n"
        f"• /stats — Generates total persistent active database metrics.\n"
        f"• /sectip — Requests real-time security & hardening vectors.\n\n"
        f"🛰️ *Advanced OSINT & Forensic Utilities:*\n"
        f"• /hash `<string>` — Generates parallel MD5, SHA-1, SHA-256 integrity hashes.\n"
        f"• /dehash `<hash>` — Submits queries to Cloud OSINT Reverse Database.\n"
        f"• /ip `<address>` — Extracts deep geolocation, ISP carrier, and ASN data.\n"
        f"• /netinfo — Analyzes server network perimeter boundaries."
    )
    await update.message.reply_text(text=help_text, parse_mode="Markdown")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    user = update.effective_user
    first_seen, last_seen, msg_count = get_user_profile(user.id)
    info_text = (
        f"🕵️‍♂️ *DETAILED PROFILE TELEMETRY ANALYTICS*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Account Overview:*\n"
        f"• Full Name: `{user.first_name} {user.last_name or ''}`\n"
        f"• Account Rank: `{'Premium License Node 🌟' if user.is_premium else 'Standard Node'}`\n\n"
        f"🆔 *Session Routings:*\n"
        f"• User ID Number: `{user.id}`\n"
        f"• Chat ID Number: `{update.effective_chat.id}`\n\n"
        f"📊 *Activity Records:*\n"
        f"• Initial Registration: `{first_seen or 'Just Captured'}`\n"
        f"• Last Active Update: `{last_seen or 'Just Captured'}`\n"
        f"• Transmission Streams: `{msg_count} packets/messages`"
    )
    await update.message.reply_text(text=info_text, parse_mode="Markdown")

async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("⚠️ *Syntax Error:* Please use format: `/hash <your_text>`", parse_mode="Markdown")
        return
    target_text = " ".join(context.args)
    hash_text = (
        f"🔐 *CRYPTOGRAPHIC INTEGRITY MATRIX*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 *Input Payload:* `{target_text}`\n\n"
        f"🧬 *MD5 Hash:* \n`{hashlib.md5(target_text.encode()).hexdigest()}`\n\n"
        f"🧬 *SHA-1 Hash:* \n`{hashlib.sha1(target_text.encode()).hexdigest()}`\n\n"
        f"🧬 *SHA-256 Hash:* \n`{hashlib.sha256(target_text.encode()).hexdigest()}`"
    )
    await update.message.reply_text(text=hash_text, parse_mode="Markdown")

async def dehash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("⚠️ *Syntax Error:* Please use format: `/dehash <32_char_md5>`", parse_mode="Markdown")
        return
    
    input_hash = context.args[0].strip().lower()
    
    if not re.match(r"^[a-f0-9]{32}$", input_hash):
        await update.message.reply_text("❌ *Execution Halted:* Only standard **MD5 (32 characters)** is supported.", parse_mode="Markdown")
        return
        
    status_msg = await update.message.reply_text("⚡ *Scanning global distributed threat databases...*")
    
    try:
        api_url = f"http://md5.nitrxgen.net/fetch.php?hash={input_hash}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=6) as response:
            decrypted_text = response.read().decode('utf-8').strip()
            
            if decrypted_text and not decrypted_text.startswith("ERROR"):
                result_text = (
                    f"🔓 *REVERSE HASH CRACK SUCCESSFUL*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🧱 *Target MD5 Hash:* `{input_hash}`\n"
                    f"🔑 *Decrypted Text:* `{decrypted_text}`\n\n"
                    f"🟢 *Database Status:* Match verified via Tier-1 Tables."
                )
                await status_msg.edit_text(text=result_text, parse_mode="Markdown")
                return
            
            # Tier-2 OSINT Database Backup Lookups
            api_url_2 = f"https://md5online.org/api.php?d=1&h={input_hash}"
            req2 = urllib.request.Request(api_url_2, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2, timeout=5) as resp2:
                decrypted_text_2 = resp2.read().decode('utf-8').strip()
                if decrypted_text_2 and "not found" not in decrypted_text_2.lower():
                    result_text = (
                        f"🔓 *REVERSE HASH CRACK SUCCESSFUL (TIER-2)*\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🧱 *Target MD5 Hash:* `{input_hash}`\n"
                        f"🔑 *Decrypted Text:* `{decrypted_text_2}`\n"
                    )
                    await status_msg.edit_text(text=result_text, parse_mode="Markdown")
                    return
                        
            await status_msg.edit_text(f"❌ *OSINT Notice:* No plain-text value was found in the global dictionary architecture.", parse_mode="Markdown")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ *Network Timeout:* Remote gateway busy. Trace: `{str(e)[:30]}`")

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("⚠️ *Syntax Error:* Please use format: `/ip <target_ip>`", parse_mode="Markdown")
        return
    target_ip = context.args[0]
    status_msg = await update.message.reply_text("🔍 *Broadcasting tracking packets to target host...*")
    try:
        req = urllib.request.Request(f"http://ip-api.com/json/{target_ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as url:
            data = json.loads(url.read().decode())
            if data.get("status") == "fail":
                await status_msg.edit_text(f"❌ *Analysis Fault:* `{data.get('message')}`")
                return
            ip_scan_result = (
                f"🛰️ *OSINT ENDPOINT DEEP SUMMARY*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎯 *Target IP Address:* `{data.get('query')}`\n"
                f"🌍 *Location Matrix:* `{data.get('city')}, {data.get('regionName')}, {data.get('country')} ({data.get('zip')})`\n"
                f"🏢 *ISP Net Operator:* `{data.get('isp')}`\n"
                f"📡 *Autonomous System (ASN):* `{data.get('as')}`\n"
                f"📍 *GPS Target Points:* `{data.get('lat')}, {data.get('lon')}`\n"
                f"🕒 *Local Timezone:* `{data.get('timezone')}`"
            )
            await status_msg.edit_text(text=ip_scan_result, parse_mode="Markdown")
    except Exception:
        await status_msg.edit_text("❌ *Scan Failure:* The remote diagnostic gateway rejected tracking headers.")

async def netinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    try:
        req = urllib.request.Request("http://ip-api.com/json/", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as url:
            data = json.loads(url.read().decode())
            await update.message.reply_text(
                f"🌐 *CORE ENVIRONMENT PERIMETER METRICS*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📡 *Server Public WAN IPv4:* `{data.get('query')}`\n"
                f"🏢 *Upstream Hosting Provider:* `{data.get('isp')}`\n"
                f"📍 *Cluster Server Location:* `{data.get('country')}`", 
                parse_mode="Markdown"
            )
    except Exception:
        await update.message.reply_text("🌐 *Security Matrix:* Local environment network data is completely isolated.")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    start_time = time.time()
    message = await update.message.reply_text("⚡ *Evaluating ping intervals...*")
    await message.edit_text(
        f"🏓 *Pong Response Successful!*\n\n"
        f"⏱️ *Host Cluster Latency:* `{round((time.time() - start_time) * 1000)}ms`\n"
        f"🟢 *System Engine Health:* `Stable & Operational`", 
        parse_mode="Markdown"
    )

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
    await update.message.reply_text(
        f"📊 *GLOBAL INTEL ENGINE STATISTICS*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Total Registered Core Nodes:* `{total_users} users`\n"
        f"📥 *Total Processed Packet Inbound:* `{total_msgs} messages`", 
        parse_mode="Markdown"
    )

async def sectip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    await update.message.reply_text(
        f"🛡️ *HARDENING RECOMMENDATION VECTOR*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 `{random.choice(SECURITY_TIPS)}`", 
        parse_mode="Markdown"
    )

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, msg_count FROM users ORDER BY msg_count DESC LIMIT 10")
        top_users = cursor.fetchall()
        conn.close()
        adm_text = "👑 *ROOT DATABASE ACTIVE USER PROFILE TELEMETRY*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for idx, row in enumerate(top_users, 1):
            adm_text += f"⚡ `[{idx}]` *ID:* `{row[0]}` | *Name:* `{row[1]}` ➔ `{row[2]} msgs`\n"
        await update.message.reply_text(text=adm_text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Admin statistics lookup failed: {str(e)}")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or not context.args: return
    broadcast_msg = "📢 *GLOBAL SYSTEM NETWORK BROADCAST FROM ROOT ADMIN*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" + " ".join(context.args)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        all_chats = cursor.fetchall()
        conn.close()
        status_message = await update.message.reply_text("🚀 *Deploying data blocks to all active nodes...*")
        success = 0
        for chat in all_chats:
            try:
                await context.bot.send_message(chat_id=chat[0], text=broadcast_msg, parse_mode="Markdown")
                success += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        await status_message.edit_text(
            f"✅ *BROADCAST TRANSMISSION COMPLETED*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🟢 *Success Nodes:* `{success}`\n"
            f"🔴 *Dropped/Blocked Nodes:* `{len(all_chats)-success}`"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Broadcast process failure: {str(e)}")

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
