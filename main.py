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

BOT_VERSION = "7.5 (Enterprise Intelligence Build)"
DB_FILE = "bot_data.db"

SECURITY_TIPS = [
    "Always use a strong VPN when performing network reconnaissance or penetration testing.",
    "Enable 2-Step Verification (2FA) on your Telegram account to block unauthorized session hijacking.",
    "Do not click on unsolicited links or download unrecognized `.apk` or `.exe` files in public groups.",
    "Regularly audit active sessions in your Telegram Settings > Devices to terminate suspicious clones.",
    "Keep your automated lab environments isolated from your primary host network using proper VLANs."
]

# ----------------- SQLITE DATABASE SUBSYSTEM -----------------
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

# ----------------- WEB WEB-SERVER FOR CLOUD HOSTING -----------------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f"RS5_ARIF System Mainframe Build v{BOT_VERSION} Status: OPERATIONAL".encode())

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

# ==================== MAIN TELEGRAM HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # 🌟 মেসেজ ১: প্রধান গেটওয়ে ওয়েলকাম কার্ড
    msg_1 = (
        f"🌌 ┌─📡 **SYSTEM MAINFRAME ONLINE**\n"
        f"⚡ ├─ **Status:** Authenticated\n"
        f"🎯 ├─ **Welcome User:** `{user.first_name}`\n"
        f"📦 ├─ **Engine Core:** `v{BOT_VERSION}`\n"
        f"🛡️ └─ **Failsafe System:** Hardened & Shielded\n\n"
        f"💡 _Run /help to load available terminal execution units._"
    )
    await update.message.reply_text(text=msg_1, parse_mode="Markdown")
    
    # 🌟 মেসেজ ২: নেটওয়ার্ক রাউটিং আইডেন্টিফিকেশন
    msg_2 = (
        f"🔑 ┌─🌐 **SESSION IDENTITY SCHEMATIC**\n"
        f"🆔 └─ **Your Telegram Chat ID:** `{chat_id}`"
    )
    await update.message.reply_text(text=msg_2, parse_mode="Markdown")
    
    # 🌟 মেসেজ ৩: কমপ্লিট ইউজার ডায়াগনস্টিকস ও মেটাডেটা 
    msg_3 = (
        f"🔮 ┌─🧬 **CORE TELEMETRY DIAGNOSTICS**\n"
        f"👤 ├─ **First Name:** `{user.first_name}`\n"
        f"🔹 ├─ **Last Name:** `{user.last_name or 'Not Configured'}`\n"
        f"🏷️ ├─ **Handshake Identity:** `@{user.username or 'No_Username'}`\n"
        f"🌐 ├─ **Language Node:** `{user.language_code or 'Unknown'}`\n"
        f"🌟 └─ **Premium License:** `{'Active Member 🌟' if user.is_premium else 'Standard Node'}`"
    )
    await update.message.reply_text(text=msg_3, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    help_text = (
        f"🛠️ ┌─🗺️ **SYSTEM CONTROLLER SCHEMA MODULE**\n"
        f"🧬 └─ **Operational Core Framework**\n\n"
        f"📋 **🔹 CORE OPERATIONAL RUNBOOKS:**\n"
        f" ├ /start  — Reinitializes handshakes & active profiles.\n"
        f" ├ /help   — Pulls deep system operational architecture.\n"
        f" ├ /info   — Fetches analytical diagnostics on your profile.\n"
        f" ├ /ping   — Checks core network cluster round-trip time.\n"
        f" ├ /stats  — Queries global active user metrics database.\n"
        f" └ /sectip — Requests real-time server hardening vector tips.\n\n"
        f"🎯 **🛰️ CRYPTO & OSINT THREAT UTILITIES:**\n"
        f" ├ /hash `<str>` — Computes parallel MD5, SHA-1, SHA-256 integrity.\n"
        f" ├ /dehash `<hash>` — Submits queries to Cloud OSINT Reverse Database.\n"
        f" ├ /ip `<host>`  — Executes geolocation, ISP, ASN deep intelligence.\n"
        f" └ /netinfo — Analyzes hosted infrastructure perimeter boundaries."
    )
    await update.message.reply_text(text=help_text, parse_mode="Markdown")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    user = update.effective_user
    first_seen, last_seen, msg_count = get_user_profile(user.id)
    info_text = (
        f"🕵️‍♂️ ┌─📊 **FORENSIC TELEMETRY MATRIX CAPTURE**\n"
        f"👤 ├─ **Entity Name:** `{user.first_name} {user.last_name or ''}`\n"
        f"🔑 ├─ **Clearance Tier:** `{'Premium Level 🌟' if user.is_premium else 'Standard Level'}`\n"
        f"🆔 ├─ **Identity Map:** `{user.id}`\n"
        f"📡 ├─ **Network Path:** `{update.effective_chat.id}`\n"
        f"🗓️ ├─ **First Handshake:** `{first_seen or 'Just Captured'}`\n"
        f"🔄 ├─ **Last Handshake:** `{last_seen or 'Just Captured'}`\n"
        f"📊 └─ **Packet Streams Sent:** `{msg_count} packets`"
    )
    await update.message.reply_text(text=info_text, parse_mode="Markdown")

async def hash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("⚠️ **Syntax Deviation:** Format must be `/hash <string_payload>`", parse_mode="Markdown")
        return
    target_text = " ".join(context.args)
    hash_text = (
        f"🔐 ┌─💎 **INTEGRITY MATRIX GENERATION REPORT**\n"
        f"📝 ├─ **Input Payload:** `{target_text}`\n"
        f"🧬 ├─ **MD5 Variant:** `{hashlib.md5(target_text.encode()).hexdigest()}`\n"
        f"🧬 ├─ **SHA-1 Variant:** `{hashlib.sha1(target_text.encode()).hexdigest()}`\n"
        f"🧬 └─ **SHA-256 Variant:** `{hashlib.sha256(target_text.encode()).hexdigest()}`"
    )
    await update.message.reply_text(text=hash_text, parse_mode="Markdown")

async def dehash_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("⚠️ **Syntax Deviation:** Format must be `/dehash <32_char_md5_hash>`", parse_mode="Markdown")
        return
    
    input_hash = context.args[0].strip().lower()
    
    if not re.match(r"^[a-f0-9]{32}$", input_hash):
        await update.message.reply_text("❌ **Execution Terminated:** Subsystem only maps **MD5 (32 hex elements)** values at this time.", parse_mode="Markdown")
        return
        
    status_msg = await update.message.reply_text("⚡ **Mapping Target against Distributed Cloud Databases...**")
    
    try:
        api_url = f"http://md5.nitrxgen.net/fetch.php?hash={input_hash}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=6) as response:
            decrypted_text = response.read().decode('utf-8').strip()
            
            if decrypted_text and not decrypted_text.startswith("ERROR"):
                result_text = (
                    f"🔓 ┌─💥 **REVERSE HASH CRACK SYSTEM (OSINT SUCCESS)**\n"
                    f"🧱 ├─ **Query Target MD5:** `{input_hash}`\n"
                    f"🔑 ├─ **Recovered String:** `{decrypted_text}`\n"
                    f"🟢 └─ **Confidence:** Match verified via Global Distributed Tables."
                )
                await status_msg.edit_text(text=result_text, parse_mode="Markdown")
                return
            
            # ব্যাকআপ টিয়ার-২ ডাটাবেস লুকআপ
            api_url_2 = f"https://md5online.org/api.php?d=1&h={input_hash}"
            req2 = urllib.request.Request(api_url_2, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2, timeout=5) as resp2:
                decrypted_text_2 = resp2.read().decode('utf-8').strip()
                if decrypted_text_2 and "not found" not in decrypted_text_2.lower():
                    result_text = (
                        f"🔓 ┌─💥 **REVERSE HASH CRACK SYSTEM (OSINT TIER-2 SUCCESS)**\n"
                        f"🧱 ├─ **Query Target MD5:** `{input_hash}`\n"
                        f"🔑 └─ **Recovered String:** `{decrypted_text_2}`\n"
                    )
                    await status_msg.edit_text(text=result_text, parse_mode="Markdown")
                    return
                        
            await status_msg.edit_text(f"❌ **Lookup Concluded:** No plain-text signature found within global threat dictionary definitions.", parse_mode="Markdown")
    except Exception as e:
        await status_msg.edit_text(f"⚠️ **Interface Error:** Communication timed out. Log trace: `{str(e)[:25]}`")

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    if not context.args:
        await update.message.reply_text("⚠️ **Syntax Deviation:** Format must be `/ip <target_ip_node>`", parse_mode="Markdown")
        return
    target_ip = context.args[0]
    status_msg = await update.message.reply_text("🔍 **Broadcasting Reconnaissance Packets to Target Nodes...**")
    try:
        req = urllib.request.Request(f"http://ip-api.com/json/{target_ip}?fields=status,message,country,regionName,city,zip,lat,lon,timezone,isp,org,as,query", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as url:
            data = json.loads(url.read().decode())
            if data.get("status") == "fail":
                await status_msg.edit_text(f"❌ **Analysis Fault:** `{data.get('message')}`")
                return
            ip_scan_result = (
                f"🛰️ ┌─🌐 **OSINT INTEL CORE NET-REPORT**\n"
                f"🎯 ├─ **Target IPv4 Endpoint:** `{data.get('query')}`\n"
                f"🌍 ├─ **Physical Matrix:** `{data.get('city')}, {data.get('country')}`\n"
                f"🏢 ├─ **ISP Carrier Node:** `{data.get('isp')}`\n"
                f"📡 ├─ **Autonomous System (ASN):** `{data.get('as')}`\n"
                f"📍 └─ **Telemetry Coordinates:** `{data.get('lat')}, {data.get('lon')}`"
            )
            await status_msg.edit_text(text=ip_scan_result, parse_mode="Markdown")
    except Exception:
        await status_msg.edit_text("❌ **Scan Failure:** Remote tracking gateway did not acknowledge telemetry packets.")

async def netinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    try:
        req = urllib.request.Request("http://ip-api.com/json/", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as url:
            data = json.loads(url.read().decode())
            await update.message.reply_text(
                f"🌐 ┌─📡 **INFRASTRUCTURE PERIMETER SUMMARY**\n"
                f"📡 ├─ **Main WAN IPv4 Address:** `{data.get('query')}`\n"
                f"🏢 ├─ **Upstream ISP Gateway:** `{data.get('isp')}`\n"
                f"📍 └─ **Cluster Host Location:** `{data.get('country')}`", 
                parse_mode="Markdown"
            )
    except Exception:
        await update.message.reply_text("🌐 **Security Status:** Cloud node internal mapping is isolated from reverse tracing lookup.")

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    start_time = time.time()
    message = await update.message.reply_text("⚡ **Measuring Framework Latency Response...**")
    await message.edit_text(f"🏓 ┌─⚡ **ECHO RESPONSE CAPTURE**\n⏱️ ├─ **Round-Trip Delay:** `{round((time.time() - start_time) * 1000)}ms`\n🟢 └─ **System Health:** Fully Operational Node", parse_mode="Markdown")

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
        f"📊 ┌─📈 **PERSISTENT GLOBAL INTEL DATABASE METRICS**\n"
        f"👥 ├─ **Registered Unique Entities:** `{total_users} active nodes`\n"
        f"📥 └─ **Recorded Session Signals:** `{total_msgs} communications`", 
        parse_mode="Markdown"
    )

async def sectip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_user_activity(update)
    await update.message.reply_text(f"🛡️ ┌─🧬 **INFRASTRUCTURE HARDENING VECTORS**\n👉 └─ `{random.choice(SECURITY_TIPS)}`", parse_mode="Markdown")

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, msg_count FROM users ORDER BY msg_count DESC LIMIT 10")
        top_users = cursor.fetchall()
        conn.close()
        adm_text = "👑 ┌─🛰️ **ROOT EXECUTIVE NODES TELEMETRY MATRIX**\n━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for idx, row in enumerate(top_users, 1):
            adm_text += f" 🔥 ├─ `[{idx}]` *ID:* `{row[0]}` | *Alias:* `{row[1]}` -> `{row[2]} packets`\n"
        adm_text += "⚙️ └─ **Audit Log Complete.**"
        await update.message.reply_text(text=adm_text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Admin query failure: {str(e)}")

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or not context.args: return
    broadcast_msg = "📢 ┌─🛰️ **CRITICAL CORE NETWORK BROADCAST FROM ADMIN**\n━━━━━━━━━━━━━━━━━━━━━━━━\n" + " ".join(context.args)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT chat_id FROM users")
        all_chats = cursor.fetchall()
        conn.close()
        status_message = await update.message.reply_text("🚀 **Deploying payload streams to all infrastructure branches...**")
        success = 0
        for chat in all_chats:
            try:
                await context.bot.send_message(chat_id=chat[0], text=broadcast_msg, parse_mode="Markdown")
                success += 1
                await asyncio.sleep(0.05)
            except Exception: pass
        await status_message.edit_text(f"✅ ┌─🛰️ **BROADCAST ROUTING LOG TERMINATED**\n🟢 ├─ **Target Deliveries Verified:** `{success}`\n🔴 └─ **Unacknowledged Dropouts:** `{len(all_chats)-success}`")
    except Exception as e:
        await update.message.reply_text(f"❌ Broadcast execution failed: {str(e)}")

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
