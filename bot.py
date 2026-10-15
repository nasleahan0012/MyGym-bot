import os
import re
import sqlite3
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

DB_PATH = "gym_athletes.db"

# ---------- پایگاه داده ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS athletes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            package TEXT,
            full_name TEXT,
            telegram_contact TEXT,
            age TEXT,
            weight TEXT,
            height TEXT,
            job TEXT,
            goal TEXT,
            neck_cm TEXT,
            waist_cm TEXT,
            gender TEXT,
            hip_cm TEXT,
            training_history TEXT,
            weekly_sessions_limit TEXT,
            meal_times TEXT,
            training_time TEXT,
            joint_issues TEXT,
            digestive_issues TEXT,
            sleep_status TEXT,
            diet_adherence_percent TEXT,
            egg_capacity TEXT,
            chicken_preference TEXT,
            photo_front_id TEXT,
            photo_side_id TEXT,
            photo_back_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# ---------- وضعیت‌های فرم (States) ----------
(
    PACKAGE,
    FULL_NAME,
    TG_CONTACT,
    AGE,
    WEIGHT,
    HEIGHT,
    NECK,
    WAIST,
    GENDER,
    HIP_OPT,
    JOB,
    GOAL,
    TRAINING_HISTORY,
    WEEKLY_LIMIT,
    MEAL_TIMES,
    TRAINING_TIME,
    JOINT_ISSUES,
    DIGESTIVE_ISSUES,
    SLEEP_STATUS,
    DIET_ADHERENCE,
    EGG_CAPACITY,
    CHICKEN_PREF,
    PHOTO_FRONT,
    PHOTO_SIDE,
    PHOTO_BACK,
) = range(25)

def kb(rows):
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)

# ---------- مراحل گفتگو ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام و درود! به سیستم ثبت اطلاعات ورزشی خوش آمدید 💪\n\n"
        "لطفاً پکیج مورد نظر خود را انتخاب کنید:",
        reply_markup=kb([
            ["پکیج کامل (برنامه تمرینی + غذایی)"],
            ["برنامه تمرینی", "برنامه غذایی"],
        ]),
    )
    return PACKAGE

async def pick_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    p = update.message.text.strip()
    context.user_data.clear()
    context.user_data["package"] = p

    if p == "پکیج کامل (برنامه تمرینی + غذایی)":
        await update.message.reply_text(
            "✅ پکیج کامل انتخاب شد.\n\n"
            "مرحله ۱: لطفاً **نام و نام خانوادگی** خود را وارد کنید:",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove(),
        )
        return FULL_NAME

    await update.message.reply_text(
        "این بخش به زودی فعال می‌شود. لطفاً فعلاً «پکیج کامل» را انتخاب کنید یا مجدداً /start را بزنید.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text.strip()
    await update.message.reply_text(
        "مرحله ۲: لطفاً **شماره تماس** (به انگلیسی مانند 09123456789) یا **آیدی تلگرام** خود را ارسال کنید:",
        parse_mode="Markdown"
    )
    return TG_CONTACT

async def tg_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["telegram_contact"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۳: **سن** خود را وارد کنید (به عدد):", parse_mode="Markdown")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۴: **وزن** فعلی خود را وارد کنید (کیلوگرم):", parse_mode="Markdown")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weight"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۵: **قد** خود را وارد کنید (سانتی‌متر):", parse_mode="Markdown")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["height"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۶: اندازه **دور گردن (زیر حنجره)** را وارد کنید (سانتی‌متر):", parse_mode="Markdown")
    return NECK

async def neck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["neck_cm"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۷: اندازه **دور کمر (روی ناف)** را وارد کنید (سانتی‌متر):", parse_mode="Markdown")
    return WAIST

async def waist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waist_cm"] = update.message.text.strip()
    await update.message.reply_text(
        "مرحله ۸: لطفاً **جنسیت** را انتخاب کنید:",
        reply_markup=kb([["آقا", "خانم"]]),
        parse_mode="Markdown"
    )
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g = update.message.text.strip()
    if g not in ["آقا", "خانم"]:
        await update.message.reply_text("لطفاً فقط یکی از دو گزینه زیر را لمس کنید:", reply_markup=kb([["آقا", "خانم"]]))
        return GENDER

    context.user_data["gender"] = g

    if g == "خانم":
        await update.message.reply_text(
            "مرحله ۹: اندازه **دور باسن** را وارد کنید (سانتی‌متر):",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return HIP_OPT

    context.user_data["hip_cm"] = "ندارد (آقا)"
    await update.message.reply_text("مرحله ۹: **شغل** خود را بنویسید:", reply_markup=ReplyKeyboardRemove(), parse_mode="Markdown")
    return JOB

async def hip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hip_cm"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۱۰: **شغل** خود را بنویسید:", parse_mode="Markdown")
    return JOB

async def job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["job"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۱۱: **هدف** اصلی شما چیست؟ (مثال: چربی‌سوزی، حجم عضلانی، بهبود آسیب‌دیدگی):", parse_mode="Markdown")
    return GOAL

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۱۲: **سابقه تمرینی منظم** دارید؟ (مثال: ۲ سال سابقه پیوسته یا خیر تازه کارم):", parse_mode="Markdown")
    return TRAINING_HISTORY

async def training_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["training_history"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۱۳: **محدودیت تعداد جلسات هفتگی** دارید؟ (مثال: حداکثر ۳ جلسه در هفته):", parse_mode="Markdown")
    return WEEKLY_LIMIT

async def weekly_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weekly_sessions_limit"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۱۴: **تایم و ساعت وعده‌های غذایی** روزمره شما چگونه است؟ (مثال: صبحانه ۹، ناهار ۱۴، شام ۲۱):", parse_mode="Markdown")
    return MEAL_TIMES

async def meal_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["meal_times"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۱۵: معمولاً چه **ساعتی از روز تمرین** می‌کنید؟ (مثال: ۱۸ تا ۱۹:۳۰):", parse_mode="Markdown")
    return TRAINING_TIME

async def training_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["training_time"] = update.message.text.strip()
    reply_keyboard = [["ندارم"]]
    await update.message.reply_text(
        "مرحله ۱۶: آیا **مشکلات یا آسیب‌های مفصلی** دارید؟ (مثل شانه، زانو، دیسک کمر یا دکمه «ندارم»):",
        reply_markup=kb(reply_keyboard),
        parse_mode="Markdown"
    )
    return JOINT_ISSUES

async def joint_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["joint_issues"] = update.message.text.strip()
    reply_keyboard = [["ندارم"]]
    await update.message.reply_text(
        "مرحله ۱۷: آیا **مشکلات گوارشی** دارید؟ (مثل نفخ، رفلاکس، یبوست، حساسیت به لاکتوز یا دکمه «ندارم»):",
        reply_markup=kb(reply_keyboard),
        parse_mode="Markdown"
    )
    return DIGESTIVE_ISSUES

async def digestive_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["digestive_issues"] = update.message.text.strip()
    await update.message.reply_text(
        "مرحله ۱۸: **وضعیت خواب** شما چطور است؟ (ساعت خواب و بیداری، کیفیت خواب و عمق آن):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return SLEEP_STATUS

async def sleep_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sleep_status"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۱۹: **درصد رعایت رژیم غذایی** در دوره یا رژیم‌های قبلی شما چقدر بوده است؟ (از ۰ تا ۱۰۰):", parse_mode="Markdown")
    return DIET_ADHERENCE

async def diet_adherence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["diet_adherence_percent"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۲۰: در یک وعده توانایی مصرف چه تعداد **سفیده و زرده تخم‌مرغ** را دارید؟ (مثال: ۴ سفیده + ۱ زرده):", parse_mode="Markdown")
    return EGG_CAPACITY

async def egg_capacity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["egg_capacity"] = update.message.text.strip()
    await update.message.reply_text(
        "مرحله ۲۱: ترجیح و انتخاب شما بین **سینه یا ران مرغ** کدام است؟",
        reply_markup=kb([["سینه", "ران", "فرقی ندارد"]]),
        parse_mode="Markdown"
    )
    return CHICKEN_PREF

async def chicken_pref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pref = update.message.text.strip()
    if pref not in ["سینه", "ران", "فرقی ندارد"]:
        await update.message.reply_text("لطفاً یکی از گزینه‌های کیبورد را انتخاب کنید:", reply_markup=kb([["سینه", "ران", "فرقی ندارد"]]))
        return CHICKEN_PREF

    context.user_data["chicken_preference"] = pref

    await update.message.reply_text(
        "📸 **مرحله ارسال عکس‌ها**\n\n"
        "مرحله ۲۲: لطفاً **عکس بدن از روبرو (Front)** را ارسال فرمایید:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return PHOTO_FRONT

async def photo_front(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً حتماً یک عکس ارسال نمایید:")
        return PHOTO_FRONT
    context.user_data["photo_front_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("عالی! مرحله ۲۳: لطفاً **عکس بدن از نیم‌رخ (Side)** را بفرستید:", parse_mode="Markdown")
    return PHOTO_SIDE

async def photo_side(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً حتماً یک عکس ارسال نمایید:")
        return PHOTO_SIDE
    context.user_data["photo_side_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("دریافت شد! مرحله ۲۴: در نهایت **عکس بدن از پشت (Back)** را ارسال کنید:", parse_mode="Markdown")
    return PHOTO_BACK

async def photo_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً حتماً یک عکس ارسال نمایید:")
        return PHOTO_BACK
    context.user_data["photo_back_id"] = update.message.photo[-1].file_id

    u = context.user_data
    user = update.effective_user

    # ذخیره در پایگاه داده
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO athletes (
                user_id, username, package,
                full_name, telegram_contact, age, weight, height, job, goal,
                neck_cm, waist_cm, gender, hip_cm,
                training_history, weekly_sessions_limit, meal_times, training_time,
                joint_issues, digestive_issues, sleep_status,
                diet_adherence_percent, egg_capacity, chicken_preference,
                photo_front_id, photo_side_id, photo_back_id
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            user.id,
            user.username or "ندارد",
            u.get("package"),
            u.get("full_name"),
            u.get("telegram_contact"),
            u.get("age"),
            u.get("weight"),
            u.get("height"),
            u.get("job"),
            u.get("goal"),
            u.get("neck_cm"),
            u.get("waist_cm"),
            u.get("gender"),
            u.get("hip_cm"),
            u.get("training_history"),
            u.get("weekly_sessions_limit"),
            u.get("meal_times"),
            u.get("training_time"),
            u.get("joint_issues"),
            u.get("digestive_issues"),
            u.get("sleep_status"),
            u.get("diet_adherence_percent"),
            u.get("egg_capacity"),
            u.get("chicken_preference"),
            u.get("photo_front_id"),
            u.get("photo_side_id"),
            u.get("photo_back_id"),
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"خطا در ثبت دیتابیس: {e}")

    await update.message.reply_text(
        "✅ **اطلاعات و تصاویر شما با موفقیت ثبت شد!**\n\n"
        "اطلاعات شما در اختیار مربی قرار گرفت و به زودی پرونده شما بررسی خواهد شد. ممنون از اعتماد و شکیبایی شما 💪",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

    # ارسال گزارش جامع به ادمین
    if ADMIN_ID:
        hip_text = f"🍑 **دور باسن:** {u.get('hip_cm')} cm\n" if u.get("gender") == "خانم" else ""
        report = (
            "🔔 **پرونده جدید ورزشکار (پکیج کامل)**\n\n"
            f"👤 **نام:** {u.get('full_name')}\n"
            f"📞 **ارتباط/آیدی:** {u.get('telegram_contact')}\n"
            f"🎂 **سن:** {u.get('age')}\n"
            f"⚖️ **وزن:** {u.get('weight')} kg\n"
            f"📏 **قد:** {u.get('height')} cm\n"
            f"👔 **شغل:** {u.get('job')}\n"
            f"🎯 **هدف:** {u.get('goal')}\n\n"
            f"📐 **سایزها:**\n"
            f"• دور گردن: {u.get('neck_cm')} cm\n"
            f"• دور کمر روی ناف: {u.get('waist_cm')} cm\n"
            f"• جنسیت: {u.get('gender')}\n"
            f"{hip_text}\n"
            f"🏋️‍♂️ **تمرین:**\n"
            f"• سابقه: {u.get('training_history')}\n"
            f"• جلسات در هفته: {u.get('weekly_sessions_limit')}\n"
            f"• تایم تمرین: {u.get('training_time')}\n\n"
            f"🥗 **تغذیه و عادات:**\n"
            f"• تایم وعده‌ها: {u.get('meal_times')}\n"
            f"• رعایت رژیم قبلی: {u.get('diet_adherence_percent')}%\n"
            f"• تخم‌مرغ در هر وعده: {u.get('egg_capacity')}\n"
            f"• سلیقه پروتئینی: {u.get('chicken_preference')}\n\n"
            f"🩺 **سلامت:**\n"
            f"• مفصلی: {u.get('joint_issues')}\n"
            f"• گوارشی: {u.get('digestive_issues')}\n"
            f"• خواب: {u.get('sleep_status')}\n\n"
            f"🆔 **اکانت تلگرام:** @{user.username or 'ندارد'} (`{user.id}`)"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=report, parse_mode="Markdown")
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=u.get("photo_front_id"), caption="عکس از روبرو (Front)")
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=u.get("photo_side_id"), caption="عکس از نیم‌رخ (Side)")
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=u.get("photo_back_id"), caption="عکس از پشت (Back)")
        except Exception as e:
            logger.error(f"خطا در ارسال به ادمین: {e}")

    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("عملیات لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    if not BOT_TOKEN:
        raise ValueError("متغیر BOT_TOKEN تنظیم نشده است!")

    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PACKAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pick_package)],
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            TG_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, tg_contact)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weight)],
            HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, height)],
            NECK: [MessageHandler(filters.TEXT & ~filters.COMMAND, neck)],
            WAIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, waist)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            HIP_OPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, hip)],
            JOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, job)],
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, goal)],
            TRAINING_HISTORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, training_history)],
            WEEKLY_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, weekly_limit)],
            MEAL_TIMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, meal_times)],
            TRAINING_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, training_time)],
            JOINT_ISSUES: [MessageHandler(filters.TEXT & ~filters.COMMAND, joint_issues)],
            DIGESTIVE_ISSUES: [MessageHandler(filters.TEXT & ~filters.COMMAND, digestive_issues)],
            SLEEP_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, sleep_status)],
            DIET_ADHERENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, diet_adherence)],
            EGG_CAPACITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, egg_capacity)],
            CHICKEN_PREF: [MessageHandler(filters.TEXT & ~filters.COMMAND, chicken_pref)],
            PHOTO_FRONT: [MessageHandler(filters.PHOTO, photo_front)],
            PHOTO_SIDE: [MessageHandler(filters.PHOTO, photo_side)],
            PHOTO_BACK: [MessageHandler(filters.PHOTO, photo_back)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
