import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN = "8771668793:AAEO-LTLHltwU8amrRcSHu2YzQBp9UE_7uo"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Хранилище в памяти (быстро и без ошибок)
users = {}  # {user_id: {"first_name": ..., "username": ...}}
dialogs = {}  # {user_id: reply_to_user_id}

# КОМАНДА /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Сохраняем пользователя в память
    users[user.id] = {
        "first_name": user.first_name,
        "username": user.username,
        "last_name": user.last_name
    }
    
    args = context.args
    
    # Если перешли по ссылке (чтобы написать кому-то)
    if args and args[0].startswith('id'):
        try:
            target_id = int(args[0][2:])
            dialogs[user.id] = target_id  # Запоминаем кому писать
            
            target_name = users.get(target_id, {}).get("first_name", str(target_id))
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]])
            await update.message.reply_text(
                f"📨 Ты пишешь {target_name}\n\n✏️ Отправь сообщение:",
                reply_markup=keyboard
            )
        except:
            await update.message.reply_text("❌ Неверная ссылка")
    else:
        # Показываем свою ссылку
        link = f"https://t.me/anons_my_bot?start=id{user.id}"
        await update.message.reply_text(
            f"🔗 Твоя ссылка:\n`{link}`\n\nОтправь её другу!",
            parse_mode='Markdown'
        )

# ОТПРАВКА СООБЩЕНИЯ
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    
    # Есть ли кому писать?
    if user.id in dialogs:
        to_id = dialogs[user.id]
        
        try:
            # Кнопка для ответа
            keyboard = InlineKeyboardMarkup([[
                InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{user.id}")
            ]])
            
            # Имя отправителя
            sender_name = users[user.id]["first_name"]
            if users[user.id].get("username"):
                sender_name += f" (@{users[user.id]['username']})"
            
            # Отправляем получателю
            await context.bot.send_message(
                chat_id=to_id,
                text=f"📩 От {sender_name}:\n\n{text}",
                reply_markup=keyboard
            )
            await update.message.reply_text("✅ Отправлено!")
            
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            await update.message.reply_text("❌ Не удалось отправить. Попроси человека запустить бота.")
    else:
        link = f"https://t.me/anons_my_bot?start=id{user.id}"
        await update.message.reply_text(
            f"❌ Сначала перейди по ссылке друга\n\nТвоя ссылка: `{link}`",
            parse_mode='Markdown'
        )

# КНОПКИ
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    
    if query.data == "cancel":
        if user.id in dialogs:
            del dialogs[user.id]
        await query.edit_message_text("❌ Отменено")
    
    elif query.data.startswith("reply_"):
        to_id = int(query.data.split("_")[1])
        dialogs[user.id] = to_id
        
        target_name = users.get(to_id, {}).get("first_name", str(to_id))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Отмена", callback_data="cancel")]])
        
        await query.edit_message_text(
            f"✏️ Отвечаешь {target_name}\n\nНапиши сообщение:",
            reply_markup=keyboard
        )

# ЗАПУСК
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()