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

# ---------- ساخت پایگاه داده ----------
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
            neck_cm TEXT,
            waist_cm TEXT,
            gender TEXT,
            hip_cm TEXT,
            job TEXT,
            goal TEXT,
            training_history TEXT,
            weekly_sessions_limit TEXT,
            training_time TEXT,
            joint_issues TEXT,
            meal_times TEXT,
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

# ---------- وضعیت‌های فرم ----------
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
    TRAINING_TIME,
    JOINT_ISSUES,
    MEAL_TIMES,
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

# ---------- نقطه شروع ----------
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
    context.user_data["step"] = 1

    await update.message.reply_text(
        f"✅ {pkg} انتخاب شد.\n\n"
        "مرحله ۱: لطفاً **نام و نام خانوادگی** خود را وارد فرمایید:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return FULL_NAME

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
    await update.message.reply_text("مرحله ۴: **وزن فعلی** خود را وارد کنید (کیلوگرم):", parse_mode="Markdown")
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
        "مرحله ۸: لطفاً **جنسیت** را مشخص کنید:",
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
            "مرحله ۹: اندازه **دور باسن** را وارد کنید (سانتی‌متر):",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return HIP_OPT

    context.user_data["hip_cm"] = "ندارد (آقا)"
    await update.message.reply_text(
        "مرحله ۹: لطفاً **شغل** خود را بنویسید:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return JOB

async def hip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hip_cm"] = update.message.text.strip()
    await update.message.reply_text("مرحله ۱۰: لطفاً **شغل** خود را بنویسید:", parse_mode="Markdown")
    return JOB

async def job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["job"] = update.message.text.strip()
    step_num = 11 if context.user_data.get("gender") == "خانم" else 10
    await update.message.reply_text(f"مرحله {step_num}: لطفاً **هدف اصلی** خود را بنویسید (مثال: چربی‌سوزی، عضله‌سازی، تناسب اندام):", parse_mode="Markdown")
    return GOAL

async def goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text.strip()
    pkg = context.user_data.get("package")

    # مسیر مستقیم برای پکیج غذایی (رد کردن تمرین)
    if pkg == "برنامه غذایی":
        step_num = 12 if context.user_data.get("gender") == "خانم" else 11
        await update.message.reply_text(
            f"مرحله {step_num}: تایم و ساعت **وعده‌های غذایی** روزمره شما چگونه است؟ (مثال: صبحانه ۹، ناهار ۱۴، شام ۲۱):",
            parse_mode="Markdown"
        )
        return MEAL_TIMES

    # مسیر پکیج تمرینی و پکیج کامل
    step_num = 12 if context.user_data.get("gender") == "خانم" else 11
    await update.message.reply_text(
        f"مرحله {step_num}: آیا **سابقه تمرینی منظم** دارید؟ (مثال: ۲ سال سابقه پیوسته یا خیر تازه‌کارم):",
        parse_mode="Markdown"
    )
    return TRAINING_HISTORY

# ---------- مراحل تمرین ----------
async def training_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["training_history"] = update.message.text.strip()
    step_num = 13 if context.user_data.get("gender") == "خانم" else 12
    await update.message.reply_text(
        f"مرحله {step_num}: چه **محدودیتی در تعداد جلسات هفتگی** دارید؟ (مثال: حداکثر ۴ جلسه در هفته):",
        parse_mode="Markdown"
    )
    return WEEKLY_LIMIT

async def weekly_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weekly_sessions_limit"] = update.message.text.strip()
    step_num = 14 if context.user_data.get("gender") == "خانم" else 13
    await update.message.reply_text(
        f"مرحله {step_num}: معمولاً چه **ساعتی از روز تمرین** می‌کنید؟ (مثال: ۱۸ تا ۲۰ شب):",
        parse_mode="Markdown"
    )
    return TRAINING_TIME

async def training_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["training_time"] = update.message.text.strip()
    step_num = 15 if context.user_data.get("gender") == "خانم" else 14
    await update.message.reply_text(
        f"مرحله {step_num}: آیا **مشکلات یا آسیب‌های مفصلی/عضلانی** دارید؟ (در صورت نداشتن، دکمه «ندارم» را بزنید):",
        reply_markup=kb([["ندارم"]]),
        parse_mode="Markdown"
    )
    return JOINT_ISSUES

async def joint_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["joint_issues"] = update.message.text.strip()
    pkg = context.user_data.get("package")

    # اگر فقط پکیج تمرینی بود، سوالات تغذیه رد می‌شود و می‌رود سراغ عکس‌ها
    if pkg == "برنامه تمرینی":
        await update.message.reply_text(
            "📸 **مرحله ارسال تصاویر بدنی**\n\n"
            "لطفاً **عکس بدن از روبرو (Front)** را ارسال فرمایید:",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        return PHOTO_FRONT

    # برای پکیج کامل
    step_num = 16 if context.user_data.get("gender") == "خانم" else 15
    await update.message.reply_text(
        f"مرحله {step_num}: تایم و ساعت **وعده‌های غذایی** روزمره شما چگونه است؟ (مثال: صبحانه ۹، ناهار ۱۴، شام ۲۱):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return MEAL_TIMES

# ---------- مراحل تغذیه ----------
async def meal_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["meal_times"] = update.message.text.strip()
    await update.message.reply_text(
        "آیا **مشکلات گوارشی** دارید؟ (مثل نفخ، سوزش معده، عدم تحمل لاکتوز، یا دکمه «ندارم»):",
        reply_markup=kb([["ندارم"]]),
        parse_mode="Markdown"
    )
    return DIGESTIVE_ISSUES

async def digestive_issues(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["digestive_issues"] = update.message.text.strip()
    await update.message.reply_text(
        "**وضعیت خواب** شما چطور است؟ (ساعت معمول خوابیدن و بیداری و کیفیت خواب):",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return SLEEP_STATUS

async def sleep_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["sleep_status"] = update.message.text.strip()
    await update.message.reply_text(
        "**درصد رعایت رژیم غذایی** در دوره‌های قبلی شما چقدر بوده است؟ (از ۰ تا ۱۰۰ درصد):",
        parse_mode="Markdown"
    )
    return DIET_ADHERENCE

async def diet_adherence(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["diet_adherence_percent"] = update.message.text.strip()
    await update.message.reply_text(
        "در یک وعده توانایی مصرف چه تعداد **سفیده و زرده تخم‌مرغ** را دارید؟ (مثال: ۴ سفیده + ۱ زرده):",
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
    if pref not in ["سینه", "ران", "فرقی ندارد"]:
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های کیبورد را انتخاب کنید:",
            reply_markup=kb([["سینه", "ران", "فرقی ندارد"]])
        )
        return CHICKEN_PREF

    context.user_data["chicken_preference"] = pref
    await update.message.reply_text(
        "📸 **مرحله ارسال تصاویر بدنی**\n\n"
        "لطفاً **عکس بدن از روبرو (Front)** را ارسال فرمایید:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    return PHOTO_FRONT

# ---------- ارسال عکس‌ها و ذخیره در دیتابیس ----------
async def photo_front(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً حتماً عکس ارسال فرمایید:")
        return PHOTO_FRONT
    context.user_data["photo_front_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("عکس اول دریافت شد! لطفاً **عکس بدن از نیم‌رخ (Side)** را بفرستید:", parse_mode="Markdown")
    return PHOTO_SIDE

async def photo_side(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً حتماً عکس ارسال فرمایید:")
        return PHOTO_SIDE
    context.user_data["photo_side_id"] = update.message.photo[-1].file_id
    await update.message.reply_text("عکس دوم دریافت شد! لطفاً **عکس بدن از پشت (Back)** را ارسال فرمایید:", parse_mode="Markdown")
    return PHOTO_BACK

async def photo_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً حتماً عکس ارسال فرمایید:")
        return PHOTO_BACK
    context.user_data["photo_back_id"] = update.message.photo[-1].file_id

    u = context.user_data
    user = update.effective_user

    # ذخیره مشخصات در دیتابیس SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO athletes (
                user_id, username, package,
                full_name, telegram_contact, age, weight, height,
                neck_cm, waist_cm, gender, hip_cm, job, goal,
                training_history, weekly_sessions_limit, training_time, joint_issues,
                meal_times, digestive_issues, sleep_status, diet_adherence_percent,
                egg_capacity, chicken_preference,
                photo_front_id, photo_side_id, photo_back_id
            ) 
