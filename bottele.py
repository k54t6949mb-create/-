from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# توكن البوت
TOKEN = "8405152258:AAGkmhSzO3VQHWYkRF-CbyfVRC1_lxhGXPI"

# إدمن البوت
ADMIN_ID = 7363344550

# قناة الاشتراك الإجباري
CHANNEL_USERNAME = "nncnnz"

# لتخزين الكلمات → الفيديو
videos = {}

# ----------- فحص الاشتراك -----------
def check_subscription(user_id, context: CallbackContext):
    try:
        member = context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ----------- /start -----------
def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_subscription(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 اشترك بالقناة أولاً", url=f"https://t.me/{CHANNEL_USERNAME}")]]
        update.message.reply_text(
            "⚠️ يجب عليك الاشتراك في قناة البوت أولاً حتى تستخدمه.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    keyboard = [[InlineKeyboardButton("📢 رابط القناة", url=f"https://t.me/{CHANNEL_USERNAME}")]]
    update.message.reply_text(
        "اهلا بك ببوت الرياكشنات\n"
        "اذا تريد تاخذ رياكشن من البوت اكتب مثلا (رياكشن)\n"
        "ويرسل لك الرياكشن الخاص بهذه الكلمة\n"
        f"( رابط قناة البوت : https://t.me/{CHANNEL_USERNAME} )",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ----------- /upload -----------
def upload(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id != ADMIN_ID:
        update.message.reply_text("❌ هذا الأمر مخصص للإدمن فقط.")
        return

    if not context.args:
        update.message.reply_text("استخدم الأمر هكذا:\n/upload كلمة_المقطع")
        return

    keyword = context.args[0]
    update.message.reply_text(f"✔️ أرسل الفيديو الآن المرتبط بكلمة: {keyword}")
    context.user_data["awaiting_video"] = keyword

# ----------- استقبال الفيديو من الإدمن -----------
def receive_video(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id == ADMIN_ID and "awaiting_video" in context.user_data:
        keyword = context.user_data["awaiting_video"]
        file_id = update.message.video.file_id

        videos[keyword] = file_id
        del context.user_data["awaiting_video"]

        update.message.reply_text(f"✔️ تم حفظ الفيديو لكلمة: {keyword}")
    else:
        update.message.reply_text("❌ هذا الفيديو غير متوقع.")

# ----------- المستخدم يكتب كلمة -----------
def handle_text(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if not check_subscription(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 اشترك بالقناة أولاً", url=f"https://t.me/{CHANNEL_USERNAME}")]]
        update.message.reply_text(
            "⚠️ يجب عليك الاشتراك في قناة البوت أولاً حتى تستخدمه.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    text = update.message.text.strip()
    if text in videos:
        update.message.reply_video(videos[text])
    else:
        update.message.reply_text("❌ لا يوجد فيديو مرتبط بهذه الكلمة.")

# ----------- إشعار للأدمن عند عضو جديد -----------
def new_member(update: Update, context: CallbackContext):
    new_members = update.message.new_chat_members
    chat = update.effective_chat

    # إرسال رسالة ترحيب في المجموعة لكل عضو جديد
    for member in new_members:
        update.message.reply_text(f"🎉 أهلاً بالعضو الجديد: {member.full_name}!")

    # الحصول على عدد الأعضاء الكلي
    total_members = chat.get_members_count()

    # إشعار للإدمن
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🔔 عضو جديد دخل: {', '.join([m.full_name for m in new_members])}\n"
             f"👥 إجمالي الأعضاء: {total_members}"
    )

# ----------- تشغيل البوت -----------
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("upload", upload))
    dp.add_handler(MessageHandler(Filters.video, receive_video))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))

    # متابعة الأعضاء الجدد
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()