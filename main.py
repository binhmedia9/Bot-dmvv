# -*- coding: utf-8 -*-

import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================= CẤU HÌNH =================

TOKEN = os.environ.get("8372007730:AAHxqCih6FibR9lBZ6WZxC26Ix4ehEk7ixM")        # set trong Render
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # https://tenapp.onrender.com/webhook

ADMIN_IDS = [5030427601]

# ================= DANH SÁCH DỊCH VỤ =================

SUPPORT_LIST = {
    "chứng chỉ giá rẻ": """💰 GÓI GIÁ RẺ ĐMVV – CHỨNG CHỈ APPLE ỔN ĐỊNH
💵 Giá: 80k / năm
⏳ Thời hạn: 11 tháng
🔹 Quyền lợi: cài IPA, nhân bản app không giới hạn, hỗ trợ VPN, App Group, iCloud bypass…
🔹 Bảo hành: 280 ngày""",

    "chứng chỉ lấy ngay": """⚡ GÓI LẤY NGAY iPHONE – CAO CẤP
💵 Giá: 219k / năm
⏳ Thời hạn: 11 tháng
🔹 Quyền lợi: Lấy ngay 3–5 phút, không lỗi xác minh internet, hỗ trợ App Group + VPN + iCloud bypass
🔹 Bảo hành: 100 ngày""",

    "chứng chỉ ipad": """📱 GÓI iPAD – LẤY NGAY
💵 Giá: 30k / năm
⏳ Thời hạn: 12 tháng
🔹 Quyền lợi: Chỉ dành cho iPad, lấy ngay, cài IPA, nhân bản app không giới hạn
🔹 Bảo hành: 365 ngày (1 đổi 1)""",

    "unban": """🔓 DỊCH VỤ UNBAN – XOÁ BLACKLIST iPHONE
💵 Giá: 189k / năm
⏳ Thời hạn: 11 tháng
🔹 Tính năng: Loại bỏ blacklist, dùng ngay, cài IPA, nhân bản app không giới hạn
🔹 Bảo hành: 300 ngày""",

    "thanh toán": """💳 THANH TOÁN
STK: 4721844336684
CTK: HỒ QUỐC BÌNH
❌ Bank xong nhớ gửi bill và nhắn "đã bank" nhé."""
}

# ================= BOT HANDLER =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xin chào!\n"
        "📌 Gõ /help để xem danh sách dịch vụ.\n"
        "👉 Gõ đúng tên dịch vụ (có dấu) để xem chi tiết."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 DANH SÁCH DỊCH VỤ\n\n"
        "• Chứng chỉ giá rẻ\n"
        "• Chứng chỉ lấy ngay\n"
        "• Chứng chỉ iPad\n"
        "• Unban\n"
        "• Thanh toán\n\n"
        "👉 Gõ đúng tên dịch vụ để xem chi tiết."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text.strip().lower()

    # Trả lời dịch vụ
    if text in SUPPORT_LIST:
        await update.message.reply_text(SUPPORT_LIST[text])
        return

    # Admin trả lời user
    if user.id in ADMIN_IDS and update.message.reply_to_message:
        replied_text = update.message.reply_to_message.text or ""
        if "🆔 ID:" in replied_text:
            try:
                user_id = int(replied_text.split("🆔 ID:")[1].split("\n")[0])
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📩 Quản lý:\n{text}"
                )
                await update.message.reply_text("✅ Đã gửi cho người dùng")
            except:
                await update.message.reply_text("❌ Lỗi gửi tin")
        return

    # User gửi admin
    if user.id not in ADMIN_IDS:
        msg = (
            f"📨 TIN NHẮN MỚI\n"
            f"👤 {user.full_name}\n"
            f"🆔 ID: {user.id}\n"
            f"💬 Nội dung:\n{text}"
        )
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(chat_id=admin_id, text=msg)
        await update.message.reply_text("✅ Tin nhắn đã gửi tới quản lý.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_id = update.message.photo[-1].file_id

    await update.message.reply_text("✅ Mình đã nhận được ảnh của bạn!")

    for admin_id in ADMIN_IDS:
        await context.bot.send_photo(
            chat_id=admin_id,
            photo=photo_id,
            caption=f"👤 {user.full_name} gửi ảnh"
        )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    doc_id = update.message.document.file_id

    await update.message.reply_text("✅ Mình đã nhận được file của bạn!")

    for admin_id in ADMIN_IDS:
        await context.bot.send_document(
            chat_id=admin_id,
            document=doc_id,
            caption=f"👤 {user.full_name} gửi file: {update.message.document.file_name}"
        )

# ================= FLASK + WEBHOOK =================

flask_app = Flask(__name__)

application = ApplicationBuilder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.Document.ALL, handle_document))

@flask_app.route("/", methods=["GET"])
def index():
    return "Bot is running", 200

@flask_app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok", 200

# ================= MAIN =================

if __name__ == "__main__":
    application.bot.set_webhook(url=WEBHOOK_URL)
    flask_app.run(host="0.0.0.0", port=10000)