from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQuer'
OWNER_USER_ID = 
CHANNEL_ID = '@Tc689mSqPbQ4MGEy'

manga_chapters = {}
next_chapter_number = 1
user_upload_state = {}

async def upload_manga(update: Update, context: CallbackContext):
    global next_chapter_number
    user_id = update.message.from_user.id

    if user_id != OWNER_USER_ID:
        await update.message.reply_text("🔒 عذراً، فقط مالك البوت يمكنه رفع الفصول.")
        return

    if user_id in user_upload_state:
        chapter_number = user_upload_state[user_id]['chapter_number']
        
        if update.message.document:
            file = update.message.document
            sent_message = await context.bot.send_document(CHANNEL_ID, document=file.file_id)
            file_id = sent_message.document.file_id
        elif update.message.photo:
            photo = update.message.photo[-1]
            sent_message = await context.bot.send_photo(CHANNEL_ID, photo=photo.file_id)
            file_id = sent_message.photo[-1].file_id
        else:
            await update.message.reply_text("⚠️ الرجاء إرسال الفصل كصورة أو PDF.")
            return
        
        manga_chapters[chapter_number] = [file_id, f"فصل رقم {chapter_number}"]
        del user_upload_state[user_id]
        next_chapter_number += 1
        
        keyboard = [[InlineKeyboardButton("✅ تأكيد الرفع", callback_data=f'confirm_{chapter_number}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(f"✅ تم رفع الفصل {chapter_number} بنجاح!", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❗ الرجاء اختيار رقم الفصل من القائمة أولاً.")

async def confirm_upload(update: Update, context: CallbackContext):
    query = update.callback_query
    chapter_number = int(query.data.split('_')[1])
    await query.answer()
    await query.edit_message_text(f"✅ تم تأكيد رفع الفصل {chapter_number} بنجاح!")
    await context.bot.send_message(OWNER_USER_ID, f"📢 الفصل {chapter_number} تم رفعه بنجاح في القناة!")

async def show_chapters(update: Update, context: CallbackContext):
    if not manga_chapters:
        await update.message.reply_text("📭 لا توجد فصول متاحة حاليًا.")
    else:
        keyboard = [[InlineKeyboardButton(f"📘 الفصل {num}", callback_data=str(num))] for num in sorted(manga_chapters)]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("📚 الفصول المتاحة:", reply_markup=reply_markup)

async def send_chapter_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chapter_number = int(query.data)
    await query.answer()
    
    if chapter_number in manga_chapters:
        file_id = manga_chapters[chapter_number][0]
        await context.bot.send_document(query.message.chat_id, file_id)
        await query.edit_message_text(f"✅ تم إرسال الفصل {chapter_number} بنجاح!")
    else:
        await query.edit_message_text("⚠️ رقم الفصل غير موجود. تأكد من اختيار رقم صحيح.")

async def start(update: Update, context: CallbackContext):
    welcome_message = "👋 مرحبًا بك في Secret Class بوت! 🚀\n✨ استمتع بتصفح فصول المانجا بسهولة وسرعة.\n🛠️ الأوامر المتاحة:"
    if update.message.from_user.id == OWNER_USER_ID:
        await update.message.reply_text(
            welcome_message +
            "\n📂 /upload - رفع فصل جديد\n📚 /show_chapters - عرض الفصول المتاحة"
        )
    else:
        await update.message.reply_text(
            welcome_message +
            "\n📚 /show_chapters - عرض الفصول"
        )

async def upload_command(update: Update, context: CallbackContext):
    global next_chapter_number
    if update.message.from_user.id == OWNER_USER_ID:
        user_upload_state[OWNER_USER_ID] = {'chapter_number': next_chapter_number}
        await update.message.reply_text(f"📤 أرسل الفصل (صورة أو PDF) لرفعه كفصل {next_chapter_number}.")
    else:
        await update.message.reply_text("🔒 عذراً، فقط مالك البوت يمكنه رفع الفصول.")

def main():
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("show_chapters", show_chapters))
    application.add_handler(CommandHandler("upload", upload_command))
    application.add_handler(CallbackQueryHandler(confirm_upload, pattern='confirm_.*'))
    application.add_handler(CallbackQueryHandler(send_chapter_callback))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, upload_manga))
    application.run_polling()

if __name__ == "__main__":
    main()
