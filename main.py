import os
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ১. @BotFather থেকে পাওয়া টোকেনটি এখানে বসান
TOKEN = "YOUR_BOT_TOKEN_HERE"

# --- রেন্ডার ২৪ ঘণ্টা লাইভ রাখার জন্য ফেইক ওয়েব সার্ভার ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is Running 24/7!")

def run_health_server():
    # Render সাধারণত একটি PORT এনভায়রনমেন্ট ভ্যারিয়েবল দেয়, না থাকলে default 8080
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Health check server started on port {port}")
    server.serve_forever()
# --------------------------------------------------

# /start কমান্ড হ্যান্ডলার (আপনার স্ক্রিনশটের হুবহু ফরম্যাট)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id
    
    # স্ক্রিনশটের মতো আকর্ষণীয় ইমোজি ও টেক্সট ফরম্যাট
    message = (
        f"👋 *Welcome, {first_name}!*\n\n"
        f"🤖 I'm your Chat ID Bot! I can help you with:\n"
        f"• Getting your Chat ID\n"
        f"• User statistics\n"
        f"• Bot information\n\n"
        f"Type /help for all commands!\n\n"
        f"✨ *Your Chat ID is:* `{chat_id}`\n\n"
        f"🌟 *Join Our Channel:* @RS5ARIF\n"
        f"💡 *Tip:* Use /info to see your detailed information!"
    )
    
    # Markdown parse mode ব্যবহার করা হয়েছে যাতে আইডি টাচ করলেই কপি হয়
    await update.message.reply_text(text=message, parse_mode="Markdown")

def main():
    # ব্যাকগ্রাউন্ডে ওয়েব সার্ভার চালু করা যাতে Render স্লিপে না যায়
    threading.Thread(target=run_health_server, daemon=True).start()

    # টেলিগ্রাম বট অ্যাপ্লিকেশন তৈরি
    app = Application.builder().token(TOKEN).build()
    
    # হ্যান্ডলার যুক্ত করা
    app.add_handler(CommandHandler("start", start_command))
    
    print("বটটি সফলভাবে চালু হয়েছে...")
    app.run_polling()

if __name__ == "__main__":
    main()
