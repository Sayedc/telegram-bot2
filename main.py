from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8715838256:AAEQ-e_RV4iv4-H5hQ-pNPsw80CJRizsYy4"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("البوت شغال 🔥")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ابعتلي لينك فيديو وأنا أحمله لك 🔥")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))

app.run_polling()
