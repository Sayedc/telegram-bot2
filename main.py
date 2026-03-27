import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

DATA_FILE = "products.json"
ADMIN_ID = 5671168695  # 🔥 حط الايدي بتاعك هنا

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

# حالة التعديل
editing_product = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 أهلاً بيك في المتجر\n\n"
        "📦 /products لعرض المنتجات\n"
        "➕ /add لإضافة منتج نصي\n"
        "📸 ابعت صورة + كابشن لإضافة منتج"
    )

# إضافة نص
async def add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("❌ اكتب المنتج بعد الأمر")
        return

    products.append({"name": text, "photo": None})
    save_products(products)

    await update.message.reply_text("✅ تم إضافة المنتج")

# إضافة صورة
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.caption:
        await update.message.reply_text("❌ اكتب الاسم والسعر في الكابشن")
        return

    products.append({
        "name": update.message.caption,
        "photo": update.message.photo[-1].file_id
    })

    save_products(products)
    await update.message.reply_text("✅ تم إضافة المنتج بالصورة")

# عرض المنتجات
async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not products:
        await update.message.reply_text("❌ مفيش منتجات")
        return

    user_id = update.effective_user.id

    for i, p in enumerate(products):
        keyboard = None

        if user_id == ADMIN_ID:
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("❌ حذف", callback_data=f"del_{i}"),
                    InlineKeyboardButton("✏️ تعديل", callback_data=f"edit_{i}")
                ]
            ])

        if p["photo"]:
            await update.message.reply_photo(
                photo=p["photo"],
                caption=p["name"],
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                p["name"],
                reply_markup=keyboard
            )

# الأزرار
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id != ADMIN_ID:
        await query.edit_message_text("❌ مش مسموح")
        return

    data = query.data

    # حذف
    if data.startswith("del_"):
        i = int(data.split("_")[1])
        if i < len(products):
            products.pop(i)
            save_products(products)
            await query.edit_message_text("✅ تم الحذف")

    # تعديل
    elif data.startswith("edit_"):
        i = int(data.split("_")[1])
        editing_product[user_id] = i

        await query.message.reply_text(
            "✏️ ابعت الاسم الجديد + السعر"
        )

# استقبال التعديل
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in editing_product:
        i = editing_product[user_id]

        if i < len(products):
            products[i]["name"] = update.message.text
            save_products(products)

            await update.message.reply_text("✅ تم التعديل")

        del editing_product[user_id]

# تشغيل
app = ApplicationBuilder().token("8715838256:AAFb2PCSuiFTnROY5_ZdJ_KRI9BG9xEVRpw").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_product))
app.add_handler(CommandHandler("products", show_products))

app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

app.add_handler(CallbackQueryHandler(handle_buttons))

print("Bot running...")
app.run_polling()
