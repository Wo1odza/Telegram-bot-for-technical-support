import logging
import os
import sqlite3
from config import TELEGRAM_TOKEN
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler

# 1. Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# 3. База данных (SQLite in-memory)
DATABASE_NAME = ":memory:"  # Use in-memory database
conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False) # Disable thread checking
cursor = conn.cursor()

# Create table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS support_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    request_text TEXT,
    department TEXT,
    timestamp TEXT
)
""")
conn.commit()


# 4. Часто задаваемые вопросы (FAQ) - ЗАМЕНИТЬ НА СВОИ!
FAQ = {
    "Как оформить заказ?": "Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку 'Добавить в корзину', затем перейдите в корзину и следуйте инструкциям для завершения покупки.",
    "Как узнать статус моего заказа?": "Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел 'Мои заказы'. Там будет указан текущий статус вашего заказа.",
    "Как отменить заказ?": "Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки.",
    "Что делать, если товар пришел поврежденным?": "При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара.",
    "Как связаться с вашей технической поддержкой?": "Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота.",
    "Как узнать информацию о доставке?": "Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки."
}

# 5. Состояния для ConversationHandler
ASK_DEPARTMENT, GET_REQUEST = range(2)

# 6. Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я бот тех.поддержки магазина 'Продаем все на свете'. Чем могу помочь?",
        reply_markup=ReplyKeyboardRemove(),
    )
    # Кнопки с ЧАВО
    keyboard = [[key] for key in FAQ.keys()]
    keyboard.append(["Связаться со специалистом"])  # Добавляем кнопку для связи
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text("Выберите вопрос из списка или свяжитесь со специалистом:", reply_markup=reply_markup)


async def faq_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    if question in FAQ:
        await update.message.reply_text(FAQ[question])
    else:
        await update.message.reply_text("К сожалению, я не знаю ответа на этот вопрос. Попробуйте связаться со специалистом.")

async def contact_specialist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Программисты", "Отдел продаж"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("В какой отдел вы хотите обратиться?", reply_markup=reply_markup)
    return ASK_DEPARTMENT

async def get_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    department = update.message.text
    if department not in ("Программисты", "Отдел продаж"):
        await update.message.reply_text("Пожалуйста, выберите один из предложенных отделов: Программисты или Отдел продаж.")
        return ASK_DEPARTMENT

    context.user_data['department'] = department
    await update.message.reply_text(f"Опишите, пожалуйста, вашу проблему для отдела {department}:", reply_markup=ReplyKeyboardRemove())
    return GET_REQUEST

async def get_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request_text = update.message.text
    department = context.user_data['department']

    # Сохраняем запрос в базу данных
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    timestamp = datetime.utcnow().isoformat()  # Format timestamp as string

    cursor.execute("""
    INSERT INTO support_requests (user_id, username, request_text, department, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, request_text, department, timestamp))
    conn.commit()

    await update.message.reply_text("Ваш запрос принят и будет обработан специалистами. Ожидайте, пожалуйста.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# 7. Функция для обработки голосовых сообщений
async def voice_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    await update.message.reply_text("К сожалению, я пока не умею обрабатывать голосовые сообщения. Пожалуйста, опишите вашу проблему текстом.")

# 8. Обработчик неизвестных команд
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Извините, я не понимаю эту команду. Пожалуйста, используйте /start для начала."
    )

# 9. Main function
def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # ConversationHandler для обработки запросов к специалистам
    conversation_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Связаться со специалистом$"), contact_specialist)],
        states={
            ASK_DEPARTMENT: [MessageHandler(filters.Regex("^(Программисты|Отдел продаж)$"), get_department)],
            GET_REQUEST: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_request)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conversation_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, faq_answer))
    application.add_handler(MessageHandler(filters.VOICE, voice_message_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))  # Обработчик неизвестных команд
    application.add_handler(MessageHandler(filters.TEXT, unknown)) # Обработчик любого текста, если ничего не подошло


    application.run_polling()

if __name__ == '__main__':
    main()