import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# اسم ملف التخزين
DATA_FILE = "products.json"

# تحميل المنتجات من الملف
def load_products():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# حفظ المنتجات في الملف
def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

# لود أول مرة
products = load_products()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 أهلاً بيك في المتجر\n\nاكتب /products لعرض المنتجات")

# إضافة منتج
async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("❌ اكتب المنتج بعد الأمر\nمثال:\n/add سماعة 200ج")
        return

    products.append(text)
    save_products(products)

    await update.message.reply_text("✅ تم إضافة المنتج")

# عرض المنتجات
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not products:
        await update.message.reply_text("❌ مفيش منتجات")
        return

    msg = "🛒 المنتجات:\n\n"
    for i, p in enumerate(products, 1):
        msg += f"{i}- {p}\n"

    await update.message.reply_text(msg)

# تشغيل البوت
app = ApplicationBuilder().token("8715838256:AAFb2PCSuiFTnROY5_ZdJ_KRI9BG9xEVRpw").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_product))
app.add_handler(CommandHandler("products", show_products))

print("Bot is running...")
app.run_polling()
