import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 5671168695

PRODUCTS_FILE = "products.json"
ORDERS_FILE = "orders.json"

user_state = {}

def load_data(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

products = load_data(PRODUCTS_FILE)
orders = load_data(ORDERS_FILE)

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🛒 عرض المنتجات", callback_data="show")]]
    await update.message.reply_text("🔥 أهلاً بيك في المتجر", reply_markup=InlineKeyboardMarkup(keyboard))

# عرض منتج
async def show_product(query, i):
    if not products:
        await query.message.reply_text("❌ مفيش منتجات")
        return

    p = products[i]

    keyboard = [
        [InlineKeyboardButton("⬅️", callback_data=f"prev_{i}"),
         InlineKeyboardButton("➡️", callback_data=f"next_{i}")],
        [InlineKeyboardButton("🛍️ اطلب", callback_data=f"order_{i}")],
        [InlineKeyboardButton("⭐ تقييم", callback_data=f"rate_{i}")]
    ]

    await query.message.delete()
    await query.message.reply_photo(
        photo=p["image"],
        caption=f"{p['name']}\n💰 {p['price']}\n📄 {p['desc']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# الأزرار
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "show":
        await show_product(query, 0)

    elif data.startswith("next_"):
        i = (int(data.split("_")[1]) + 1) % len(products)
        await show_product(query, i)

    elif data.startswith("prev_"):
        i = (int(data.split("_")[1]) - 1) % len(products)
        await show_product(query, i)

    elif data.startswith("order_"):
        i = int(data.split("_")[1])
        user_state[query.message.chat_id] = {"product": products[i]["name"], "status": "جديد"}
        await query.message.reply_text("📲 ابعت اسمك + رقمك + عنوانك")

    elif data.startswith("rate_"):
        i = int(data.split("_")[1])
        user_state[query.message.chat_id] = {"rate_product": products[i]["name"]}
        await query.message.reply_text("⭐ قيم من 1 لـ 5")

# الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text

    # تقييم
    if chat_id in user_state and "rate_product" in user_state[chat_id]:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⭐ تقييم جديد\n📦 {user_state[chat_id]['rate_product']}\n⭐ {text}"
        )
        await update.message.reply_text("✅ شكراً على التقييم")
        user_state.pop(chat_id)
        return

    # طلب
    if chat_id in user_state and "product" in user_state[chat_id]:
        order = user_state[chat_id]
        order["info"] = text
        order["id"] = len(orders)

        orders.append(order)
        save_data(ORDERS_FILE, orders)

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔥 طلب #{order['id']}\n📦 {order['product']}\n👤 {text}\n📊 الحالة: {order['status']}"
        )

        await update.message.reply_text("💰 حول على الرقم: 010XXXXXXXX\nوابعت صورة التحويل")
        user_state.pop(chat_id)
        return

# الأدمن
async def orders_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    if not orders:
        await update.message.reply_text("❌ مفيش طلبات")
        return

    text = "📦 الطلبات:\n"
    for o in orders:
        text += f"#{o['id']} - {o['product']} ({o['status']})\n"

    await update.message.reply_text(text)

async def change_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != ADMIN_ID:
        return

    try:
        oid = int(context.args[0])
        status = context.args[1]

        orders[oid]["status"] = status
        save_data(ORDERS_FILE, orders)

        await update.message.reply_text("✅ تم التحديث")
    except:
        await update.message.reply_text("❌ خطأ")

# تشغيل
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("orders", orders_list))
app.add_handler(CommandHandler("set", change_status))

app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
