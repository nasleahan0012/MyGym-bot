import os
import sqlite3
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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
            job TEXT,
            goal TEXT,
            training_history TEXT,
            weight TEXT,
            height TEXT,
            neck_cm TEXT,
            waist_cm TEXT,
            gender TEXT,
            hip_cm TEXT,
            weekly_sessions_limit TEXT,
            meal_times TEXT,
            training_time TEXT,
            joint_issues TEXT,
            digestive_issues TEXT,
            egg_capacity TEXT,
            chicken_preference TEXT,
            prev_program TEXT,
            sleep_status TEXT,
            diet_adherence_percent TEXT,
            photo_front_id TEXT,
            photo_side_id TEXT,
            photo_back_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# ---------- وضعیت‌های فرم (State Machine) ----------
(
    PACKAGE,
    FULL_NAME,
    TG_CONTACT,
    AGE,
    JOB,
    GOAL,
    TRAINING_HISTORY,
    WEIGHT,
    HEIGHT,
    NECK,
    WAIST,
    GENDER,
    HIP_OPT,
    WEEKLY_LIMIT,
    MEAL_TIMES,
    TRAINING_TIME,
    JOINT_ISSUES,
    DIGESTIVE_ISSUES,
    EGG_CAPACITY,
    CHICKEN_PREF,
    PREV_PROGRAM,
    SLEEP_STATUS,
    DIET_ADHERENCE,
    PHOTO_FRONT,
    PHOTO_SIDE,
    PHOTO_BACK,
) = range(26)

def kb(rows):
    return ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True)

# ---------- شروع ربات ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "سلام و درود! به سیستم هوشمند دریافت برنامه ورزشی و تغذیه خوش آمدید 💪\n\n"
        "لطفاً پکیج مدنظر خود را انتخاب فرمایید:",
        reply_markup=kb([
            ["پکیج کامل (برنامه تمرینی + غذایی)"],
            ["برنامه تمرینی", "برنامه غذایی"],
        ]),
    )
    return PACKAGE

async def pick_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pkg = update.message.text.strip()
    valid_packages = [
        "پکیج کامل (برنامه تمرینی + غذایی)",
        "برنامه تمرینی",
        "برنامه غذایی"
    ]
    if pkg not in valid_packages:
        await update.message.reply_text(
            "لطفاً فقط یکی از گزینه‌های موجود در کیبورد پایین را انتخاب کنید:",
            reply_markup=kb([
                ["پکیج کامل (برنامه تمرینی + غذایی)"],
                ["برنامه تمرینی", "برنامه غذایی"],
            ])
        )
        return PACKAGE

    context.user_data["package"] = pkg
    await update.message.reply_text(
        f"✅ {pkg} انتخاب شد.\n\n"
        "لطفاً **نام و نام خانوادگی** خود را وارد فرمایید:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return FULL_NAME

async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text.strip()
    await update.message.reply_text(
        "لطفاً **شماره تماس یا آیدی تلگرام به لاتین** خود را ارسال کنید (مثال: 09123456789 یا @username):",
        parse_mode="Markdown"
    )
    return TG_CONTACT

async def tg_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["telegram_contact"] = update.message.text.strip()
    await update.message.reply_text("لطفاً **سن** خود را وارد کنید (به عدد):", parse_mode="Markdown")
    return AGE

async def age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["age"] = update.message.text.strip()
    
    pkg = context.user_data.get("package")
    # برای برنامه غذایی، سوال بعدی شغل است؛ برای بقیه هم در ادامه شغل می‌آید
    await update.message.reply_text("لطفاً **شغل** خود را بنویسید:", parse_mode="Markdown")
    return JOB

async def job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["job"] = update.message.text.strip()
    
    pkg = context.user_data.get("package")
    if pkg == "برنامه غذایی":
        # در برنامه غذایی، بعد از شغل می‌رود سراغ هدف (اگر کاربر بخواهد) یا مستقیم سابقه تمرین
        await update.message.reply_text("لطفاً **هدف اصلی** خود را بنویسید:", parse_mode="Markdown")
        return GOAL
    
    await update.message.reply_text("لطفاً **هدف اصلی** خود را بنویسید (مثال: چربی‌سوزی، عضله‌سازی):", parse_mode="Markdown")
    return GOAL

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text.strip()
    await update.message.reply_text(
        "آیا **سابقه تمرینی منظم** دارید؟ (مثال: ۲ سال سابقه پیوسته یا خیر تازه‌کارم):",
        parse_mode="Markdown"
    )
    return TRAINING_HISTORY

async def training_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["training_history"] = update.message.text.strip()
    await update.message.reply_text("لطفاً **وزن فعلی** خود را وارد کنید (کیلوگرم):", parse_mode="Markdown")
    return WEIGHT

async def weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weight"] = update.message.text.strip()
    await update.message.reply_text("لطفاً **قد** خود را وارد کنید (سانتی‌متر):", parse_mode="Markdown")
    return HEIGHT

async def height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["height"] = update.message.text.strip()
    await update.message.reply_text("اندازه **دور گردن (زیر حنجره)** را وارد کنید (سانتی‌متر):", parse_mode="Markdown")
    return NECK

async def neck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["neck_cm"] = update.message.text.strip()
    await update.message.reply_text("اندازه **دور کمر (روی ناف)** را وارد کنید (سانتی‌متر):", parse_mode="Markdown")
    return WAIST

async def waist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waist_cm"] = update.message.text.strip()
    await update.message.reply_text(
        "لطفاً **جنسیت** خود را مشخص کنید:",
        reply_markup=kb([["آقا", "خانم"]]),
        parse_mode="Markdown"
    )
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    g = update.message.text.strip()
    if g not in ["آقا", "خانم"]:
        await update.message.reply_text("لطفاً یکی از دو گزینه زیر را انتخاب کنید:", reply_markup=kb([["آقا", "خانم"]]))
        return GENDER

    context.user_data["gender"] = g
    if g == "خانم":
        await update.message.reply_text(
            "اندازه **دور باسن** را وارد کنید (سانتی‌متر):",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return HIP_OPT

    context.user_data["hip_cm"] = "ندارد (آقا)"
    return await route_after_hip(update, context)

async def hip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hip_cm"] = update.message.text.strip()
    return await route_after_hip(update, context)

async def route_after_hip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pkg = context.user_data.get("package")
    
    if pkg == "برنامه تمرینی":
        await update.message.reply_text(
            "چه **محدودیتی در تعداد جلسات هفتگی** دارید؟ (مثال: حداکثر ۴ جلسه در هفته):",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return WEEKLY_LIMIT
    
    elif pkg == "برنامه غذایی":
        await update.message.reply_text(
            "تعداد جلسات تمرین در هفته در برنامه تمرینی شما چند جلسه است؟",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return WEEKLY_LIMIT
        
    else: # پکیج کامل
        await update.message.reply_text(
            "چه **محدودیتی در تعداد جلسات هفتگی** دارید؟",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return WEEKLY_LIMIT

async def weekly_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weekly_sessions_limit"] = update.message.text.strip()
    pkg = context.user_data.get("package")

    if pkg == "برنامه تمرینی":
        await update.message.reply_text(
            "آیا **مشکلات یا آسیب‌های مفصلی** دارید؟ (در صورت نداشتن، دکمه «ندارم» را بزنید):",
            reply_markup=kb([["ندارم"]]),
            parse_mode="Markdown"
        )
        return JOINT_ISSUES

    elif pkg == "برنامه غذایی":
        await update.message.reply_text(
            "تایم و ساعت **وعده‌های غذایی و تمرین** خود را بنویسید:",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return MEAL_TIMES

    else: # پکیج کامل
        await update.message.reply_text(
            "تایم و ساعت **وعده‌های غذایی** روزمره شما چگونه است؟",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return MEAL_TIMES

# ---------- شاخه‌های اختصاصی ادامه مسیر ----------
async def meal_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["meal_times"] = update.message.text.strip()
    pkg = context.user_data.get("package")

    if pkg == "برنامه غذایی":
        await update.message.reply_text(
            "آیا **مشکلات گوارشی** دارید؟ (مثل نفخ، سوزش معده، یا دکمه «ندارم»):",
            reply_markup=kb([["ندارم"]]),
            parse_mode="Markdown"
        )
        return DIGESTIVE_ISSUES

    # برای پکیج کامل
    await update.message.reply_text(
        "تایم **تمرین** شما چه ساعتی است؟",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return TRAINING_TIME

async def training_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["training_time"] = update.message.text.strip()
    await update.message.reply_text(
        "آیا **مشکلات مفصلی و گوارشی** دارید؟ (در صورت نداشتن، «ندارم» بزنید):",
        reply_markup=kb([["ندارم"]]),
        parse_mode="Markdown"
    )
    return JOINT_ISSUES

async def joint_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["joint_issues"] = update.message.text.strip()
    pkg = context.user_data.get("package")

    if pkg == "برنامه تمرینی":
        # در برنامه تمرینی بعد از مشکلات مفصلی می‌رود سراغ عکس‌ها
        await update.message.reply_text(
            "📸 **مرحله ارسال تصاویر بدنی**\n\nلطفاً **عکس بدن از روبرو (Front)** را ارسال فرمایید:",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return PHOTO_FRONT

    # برای پکیج کامل می‌رود سراغ تغذیه و عادات
    await update.message.reply_text(
        "تعداد سفیده و زرده تخم‌مرغ مصرفی در یک وعده چقدر است؟",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return EGG_CAPACITY

async def digestive_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["digestive_issues"] = update.message.text.strip()
    await update.message.reply_text(
        "تعداد سفیده و زرده تخم‌مرغ مصرفی در یک وعده چقدر است؟",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return EGG_CAPACITY

async def egg_capacity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["egg_capacity"] = update.message.text.strip()
    await update.message.reply_text(
        "ترجیح شما بین **سینه یا ران مرغ** کدام است؟",
        reply_markup=kb([["سینه", "ران", "فرقی ندارد"]]),
        parse_mode="Markdown"
    )
    return CHICKEN_PREF

async def chicken_pref(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pref = update.message.text.strip()
    context.user_data["chicken_preference"] = pref
    
    pkg = context.user_data.get("package")
    if pkg == "برنامه غذایی":
        await update.message.reply_text(
            "برنامه غذایی دوره قبل خود را بنویسید (یا بنویسید نداشته‌ام):",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return PREV_PROGRAM
        
    # پکیج کامل
    await update.message.reply_text(
        "برنامه تمرینی و غذایی دوره قبل خود را بنویسید:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return PREV_PROGRAM

async def prev_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["prev_program"] = update.message.text.strip()
    pkg = context.user_data.get("package")

    if pkg == "برنامه غذایی":
        # برنامه غذایی عکس بدن ندارد، کار تمام است!
        return await save_and_finish(update, context)

    # پکیج کامل ادامه می‌دهد به خواب و رعایت رژیم و سپس عکس‌ها
    await update.message.reply_text(
        "وضعیت خواب شما چگونه است؟",
        parse_mode="Markdown"
    )
    return SLEEP_STATUS

async def sleep_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sleep_status"] = update.message.text.strip()
    await update.message.reply_text(
        "درصد رعایت رژیم غذایی در دوره قبل چقدر بوده است؟ (از ۰ تا ۱۰۰):",
        parse_mode="Markdown"
    )
    return DIET_ADHERENCE

async def diet_adherence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["diet_adherence_percent"] = update.message.text.strip()
    await update.message.reply_text(
        "📸 **مرحله ارسال تصاویر بدنی**\n\nلطفاً **عکس بدن از روبرو (Front)** را ارسال فرمایید:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return PHOTO_FRONT

# ---------- دریافت عکس‌ها ----------
async def photo_front(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً حتماً عکس ارسال فرمایید:")
        return PHOTO_FRONT
    context.user_data["photo_front_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("عکس اول دریافت شد! لطفاً **عکس بدن از نیم‌رخ (Side)** را بفرستید:", parse_mode="Markdown")
    return PHOTO_SIDE

async def photo_side(update: Update, context: ContextTypes
