import json
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

DATA_FILE = "products.json"

# تحميل المنتجات
def load_products():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# حفظ المنتجات
def save_products(products):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

products = load_products()

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 أهلاً بيك في المتجر\n\n"
        "📦 /products لعرض المنتجات\n"
        "➕ /add لإضافة منتج نصي\n"
        "📸 ابعت صورة مع كابشن لإضافة منتج بصورة"
    )

# إضافة منتج نصي
async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("❌ اكتب المنتج بعد الأمر\nمثال:\n/add موبايل 5000ج")
        return

    product = {
        "name": text,
        "photo": None
    }

    products.append(product)
    save_products(products)

    await update.message.reply_text("✅ تم إضافة المنتج")

# استقبال الصور
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.caption:
        await update.message.reply_text("❌ حط اسم المنتج والسعر في الكابشن")
        return

    photo = update.message.photo[-1].file_id
    caption = update.message.caption

    product = {
        "name": caption,
        "photo": photo
    }

    products.append(product)
    save_products(products)

    await update.message.reply_text("✅ تم إضافة المنتج بالصورة")

# عرض المنتجات
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not products:
        await update.message.reply_text("❌ مفيش منتجات")
        return

    for p in products:
        if p["photo"]:
            await update.message.reply_photo(
                photo=p["photo"],
                caption=p["name"]
            )
        else:
            await update.message.reply_text(p["name"])

# تشغيل البوت
app = ApplicationBuilder().token("8715838256:AAFb2PCSuiFTnROY5_ZdJ_KRI9BG9xEVRpw").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_product))
app.add_handler(CommandHandler("products", show_products))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot is running...")
app.run_polling()
