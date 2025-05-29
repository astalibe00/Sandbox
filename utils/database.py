# utils/database.py
# Bu fayl ma'lumotlar bazasi bilan ishlash uchun barcha funksiyalarni o'z ichiga oladi.

import sqlite3
import os
import logging
import random
import string
import calendar
from datetime import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Loglash sozlamalari
logger = logging.getLogger(__name__)

# Ma'lumotlar bazasi fayli yo'li
DB_PATH = r'c:\Users\Asus\Desktop\bot\bot.db'

def initialize_db():
    """
    Ma'lumotlar bazasini boshlash va jadvallarni yaratish funksiyasi.
    Agar ma'lumotlar bazasi fayli mavjud bo'lmasa, uni yaratadi.
    Mavjud bo'lsa, ustunlarni qo'shish (ALTER TABLE) orqali yangilaydi.
    """
    try:
        db_directory = os.path.dirname(DB_PATH)
        if db_directory and not os.path.exists(db_directory):
            os.makedirs(db_directory)
            logger.info(f"Ma'lumotlar bazasi papkasi yaratildi: {db_directory}")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # 1. users jadvalini yaratish
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (user_id INTEGER PRIMARY KEY,
                      phone TEXT,
                      login TEXT,
                      password TEXT,
                      role TEXT,
                      group_name TEXT,
                      full_name TEXT,
                      last_name TEXT,
                      child_id INTEGER, -- Ota-ona uchun biriktirilgan talabaning ID'si
                      status TEXT,
                      is_logged_in INTEGER DEFAULT 0,
                      debt_amount REAL DEFAULT 0,
                      payment_status TEXT DEFAULT 'tolanmagan',
                      tariff_plan TEXT,
                      tariff_price REAL,
                      language TEXT DEFAULT 'uz')''')
        logger.info("users jadvali yaratildi yoki mavjudligi tekshirildi.")

        # 2. groups jadvalini yaratish
        c.execute('''CREATE TABLE IF NOT EXISTS groups
                     (group_name TEXT PRIMARY KEY,
                      teacher_id INTEGER,
                      class_times TEXT)''')
        logger.info("groups jadvali yaratildi yoki mavjudligi tekshirildi.")

        # 3. group_assignments jadvalini yaratish
        c.execute('''CREATE TABLE IF NOT EXISTS group_assignments
                     (student_id INTEGER,
                      group_name TEXT,
                      PRIMARY KEY (student_id, group_name))''')
        logger.info("group_assignments jadvali yaratildi yoki mavjudligi tekshirildi.")

        # 4. attendance jadvalini yaratish
        c.execute('''CREATE TABLE IF NOT EXISTS attendance
                     (student_id INTEGER,
                      group_name TEXT,
                      date TEXT,
                      status TEXT,
                      comment TEXT)''')
        logger.info("attendance jadvali yaratildi yoki mavjudligi tekshirildi.")

        # 5. teacher_ratings jadvalini yaratish
        c.execute('''CREATE TABLE IF NOT EXISTS teacher_ratings
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      teacher_id INTEGER,
                      student_id INTEGER,
                      q1_rating INTEGER,
                      q2_rating INTEGER,
                      q3_rating INTEGER,
                      rating_date TEXT)''')
        logger.info("teacher_ratings jadvali yaratildi yoki mavjudligi tekshirildi.")

        # 6. student_feedback jadvalini yaratish
        c.execute('''CREATE TABLE IF NOT EXISTS student_feedback
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      teacher_id INTEGER,
                      student_id INTEGER,
                      feedback_text TEXT,
                      feedback_date TEXT)''')
        logger.info("student_feedback jadvali yaratildi yoki mavjudligi tekshirildi.")

        # Mavjud users jadvaliga yangi ustunlar qo'shish (agar ular hali mavjud bo'lmasa)
        columns_to_add = [
            ('is_logged_in', 'INTEGER', '0'),
            ('debt_amount', 'REAL', '0'),
            ('payment_status', 'TEXT', "'tolanmagan'"),
            ('last_name', 'TEXT', None),
            ('tariff_plan', 'TEXT', None),
            ('tariff_price', 'REAL', None),
            ('language', 'TEXT', "'uz'"),
            ('child_id', 'INTEGER', None) # child_id ustunini qo'shish
        ]

        for column, column_type, default in columns_to_add:
            try:
                add_column_sql = f"ALTER TABLE users ADD COLUMN {column} {column_type}"
                if default is not None:
                    add_column_sql += f" DEFAULT {default}"
                c.execute(add_column_sql)
                logger.info(f"users jadvaliga '{column}' ustuni qo'shildi.")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    logger.info(f"users jadvalida '{column}' ustuni allaqachon mavjud.")
                else:
                    logger.error(f"users jadvaliga '{column}' ustunini qo'shishda xato: {e}")

        # Super adminni qo'shish/yangilash
        super_admin_user_id = 6642598607
        super_admin_phone = '+998990197548'
        super_admin_login = 'Saidabdulloh'
        super_admin_password = 'said'

        c.execute("SELECT * FROM users WHERE user_id = ?", (super_admin_user_id,))
        if c.fetchone():
            c.execute("""UPDATE users SET phone = ?, login = ?, password = ?, role = ?, group_name = ?,
                         full_name = ?, last_name = ?, child_id = ?, status = ?, is_logged_in = ?,
                         debt_amount = ?, payment_status = ?, tariff_plan = ?, tariff_price = ?, language = ?
                         WHERE user_id = ?""",
                      (super_admin_phone, super_admin_login, super_admin_password, 'super_admin', None,
                       'Saidabdulloh', None, None, 'active', 0, 0, 'tolanmagan', None, None, 'uz', super_admin_user_id))
            logger.info(f"Super admin hisobi yangilandi: user_id={super_admin_user_id}")
        else:
            # `group_name` ni None qilib qo'shish, chunki super admin guruhga biriktirilmaydi
            c.execute("""INSERT INTO users (user_id, phone, login, password, role, group_name, full_name,
                         last_name, child_id, status, is_logged_in, debt_amount, payment_status,
                         tariff_plan, tariff_price, language)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (super_admin_user_id, super_admin_phone, super_admin_login, super_admin_password,
                       'super_admin', None, 'Saidabdulloh', None, None, 'active', 0, 0, 'tolanmagan', None, None, 'uz'))
            logger.info(f"Super admin hisobi yaratildi: user_id={super_admin_user_id}")

        conn.commit()
        logger.info("Ma'lumotlar bazasi muvaffaqiyatli boshlandi va yangilandi.")

    except sqlite3.Error as e:
        logger.error(f"Ma'lumotlar omborini boshlashda xato: {e}")
    finally:
        if conn:
            conn.close()

# Yordamchi funksiyalar
def hisob_malukmotlarini_yaratish():
    """
    Tushunarliroq login va parolni generatsiya qiladi.
    Login: 'user' prefiksi + 4 ta tasodifiy harf/raqam (masalan, userA1b2)
    Parol: 8 ta tasodifiy harf/raqam (masalan, XyZ123aB)
    """
    # Login uchun faqat kichik harflar va raqamlar
    login_chars = string.ascii_lowercase + string.digits
    login_suffix = ''.join(random.choices(login_chars, k=4))
    login = f"user{login_suffix}"

    # Parol uchun katta-kichik harflar va raqamlar
    password_chars = string.ascii_letters + string.digits
    parol = ''.join(random.choices(password_chars, k=8))
    
    logger.info(f"Yangi login generatsiya qilindi: {login}")
    return login, parol

def foydalanuvchini_id_bilan_olish(user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            columns = ['user_id', 'phone', 'login', 'password', 'role', 'group_name', 'full_name', 'last_name', 'child_id', 'status', 'is_logged_in', 'debt_amount', 'payment_status', 'tariff_plan', 'tariff_price', 'language']
            user = dict(zip(columns[:len(row)], row))
            # Qo'shimcha ustunlar mavjudligini tekshirish va ularga standart qiymat berish
            if 'is_logged_in' not in user:
                user['is_logged_in'] = 0
            if 'tariff_plan' not in user:
                user['tariff_plan'] = None
            if 'tariff_price' not in user:
                user['tariff_price'] = None
            if 'language' not in user:
                user['language'] = 'uz'
            if 'child_id' not in user: # child_id ni tekshirish
                user['child_id'] = None
            logger.info(f"Foydalanuvchi topildi: user_id={user_id}, login={user['login']}, role={user['role']}, language={user['language']}")
            return user
        logger.info(f"Foydalanuvchi topilmadi: user_id={user_id}")
        return None
    except sqlite3.Error as e:
        logger.error(f"Ma'lumotlar ombori xatosi (foydalanuvchini_id_bilan_olish): {e}")
        return None

def foydalanuvchini_login_bilan_olish(login):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE login = ?", (login,))
        row = c.fetchone()
        conn.close()
        if row:
            columns = ['user_id', 'phone', 'login', 'password', 'role', 'group_name', 'full_name', 'last_name', 'child_id', 'status', 'is_logged_in', 'debt_amount', 'payment_status', 'tariff_plan', 'tariff_price', 'language']
            user = dict(zip(columns[:len(row)], row))
            if 'is_logged_in' not in user:
                user['is_logged_in'] = 0
            if 'tariff_plan' not in user:
                user['tariff_plan'] = None
            if 'tariff_price' not in user:
                user['tariff_price'] = None
            if 'language' not in user:
                user['language'] = 'uz'
            if 'child_id' not in user: # child_id ni tekshirish
                user['child_id'] = None
            logger.info(f"Foydalanuvchi topildi: login={login}, role={user['role']}")
            return user
        logger.warning(f"Foydalanuvchi topilmadi: login={login}")
        return None
    except sqlite3.Error as e:
        logger.error(f"Ma'lumotlar ombori xatosi (foydalanuvchini_login_bilan_olish): {e}")
        return None

def foydalanuvchini_telefon_va_login_bilan_olish(phone, login):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE phone = ? AND login = ?", (phone, login))
        row = c.fetchone()
        conn.close()
        if row:
            columns = ['user_id', 'phone', 'login', 'password', 'role', 'group_name', 'full_name', 'last_name', 'child_id', 'status', 'is_logged_in', 'debt_amount', 'payment_status', 'tariff_plan', 'tariff_price', 'language']
            user = dict(zip(columns[:len(row)], row))
            if 'is_logged_in' not in user:
                user['is_logged_in'] = 0
            if 'tariff_plan' not in user:
                user['tariff_plan'] = None
            if 'tariff_price' not in user:
                user['tariff_price'] = None
            if 'language' not in user:
                user['language'] = 'uz'
            if 'child_id' not in user: # child_id ni tekshirish
                user['child_id'] = None
            logger.info(f"Foydalanuvchi topildi: phone={phone}, login={login}, user_id={user['user_id']}")
            return user
        logger.warning(f"Foydalanuvchi topilmadi: phone={phone}, login={login}")
        return None
    except sqlite3.Error as e:
        logger.error(f"Ma'lumotlar ombori xatosi (foydalanuvchini_telefon_va_login_bilan_olish): {e}")
        return None

def foydalanuvchi_parolini_yangilash(user_id, yangi_parol):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET password = ? WHERE user_id = ?", (yangi_parol, user_id))
        conn.commit()
        conn.close()
        logger.info(f"Parol yangilandi: user_id={user_id}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Ma'lumotlar ombori xatosi (foydalanuvchi_parolini_yangilash): {e}")
        return False

def foydalanuvchi_kirish_holatini_ornatish(user_id, is_logged_in):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET is_logged_in = ? WHERE user_id = ?", (is_logged_in, user_id))
        conn.commit()
        conn.close()
        logger.info(f"Foydalanuvchi kirish holati yangilandi: user_id={user_id}, is_logged_in={is_logged_in}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Ma'lumotlar ombori xatosi (foydalanuvchi_kirish_holatini_ornatish): {e}")
        return False

def foydalanuvchi_tilini_yangilash(user_id, language):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        conn.commit()
        conn.close()
        logger.info(f"Foydalanuvchi tili yangilandi: user_id={user_id}, language={language}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Ma'lumotlar ombori xatosi (foydalanuvchi_tilini_yangilash): {e}")
        return False

def foydalanuvchi_qoshish(user_data):
    """
    Yangi foydalanuvchini ma'lumotlar bazasiga qo'shadi.
    `user_data` lug'atida `group_name` maydoni bo'lmasa, None bo'lib qoladi.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # `group_name` ni `user_data` dan olamiz, agar mavjud bo'lmasa None
        group_name_val = user_data.get('group_name')
        c.execute("INSERT OR IGNORE INTO users (user_id, phone, login, password, role, group_name, full_name, last_name, child_id, status, is_logged_in, debt_amount, payment_status, tariff_plan, tariff_price, language) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (user_data['user_id'], user_data['phone'], user_data['login'], user_data['password'], user_data['role'],
                   group_name_val, user_data['full_name'], user_data['last_name'], user_data['child_id'], user_data['status'], 0, 0, 'tolanmagan', user_data.get('tariff_plan'), user_data.get('tariff_price'), user_data.get('language', 'uz')))
        conn.commit()
        logger.info(f"Yangi foydalanuvchi qo'shildi: user_id={user_data['user_id']}, login={user_data['login']}, tariff_plan={user_data.get('tariff_plan')}, language={user_data.get('language')}")
    except sqlite3.Error as e:
        logger.error(f"Ma'lumotlar ombori xatosi (foydalanuvchi_qoshish): {e}")
    finally:
        conn.close()

def update_user_group_name(user_id, group_name):
    """
    Foydalanuvchining `users` jadvalidagi `group_name` ustunini yangilaydi.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET group_name = ? WHERE user_id = ?", (group_name, user_id))
        conn.commit()
        logger.info(f"Foydalanuvchi {user_id} uchun group_name '{group_name}' ga yangilandi.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Foydalanuvchi group_name'ini yangilashda xato: {e}")
        return False
    finally:
        conn.close()

def update_parent_child_link(parent_user_id, child_user_id):
    """
    Ota-ona foydalanuvchining `child_id` ustunini yangilaydi.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET child_id = ? WHERE user_id = ?", (child_user_id, parent_user_id))
        conn.commit()
        logger.info(f"Ota-ona {parent_user_id} talaba {child_user_id} ga biriktirildi.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Ota-ona-talaba bog'lanishini yangilashda xato: {e}")
        return False
    finally:
        conn.close()

def telefon_raqam_togrimi(phone):
    # Telefon raqami + bilan boshlanishi va 13 ta raqamdan iborat bo'lishi kerak.
    # Bu yerda faqat raqamlar va '+' belgisidan iboratligini tekshiramiz.
    return phone.startswith('+') and len(phone) == 13 and phone[1:].isdigit()

def login_togrimi(login):
    # Login faqat harf va raqamlardan iborat bo'lishi kerak.
    return len(login) >= 3 and login.isalnum()

def parol_togrimi(password):
    # Parol kamida 6 ta belgidan iborat bo'lishi kerak.
    return len(password) >= 6

def create_calendar_keyboard(year, month, lang='uz'):
    """Inline kalendarni yaratadi."""
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    
    # Oy va yil sarlavhasi
    month_names = {
        'uz': ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"],
        'ru': ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
        'en': ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    }
    
    today_button_text = {
        'uz': "Bugun",
        'ru': "Сегодня",
        'en': "Today"
    }

    header_text = f"{month_names[lang][month - 1]} {year}"
    kb.inline_keyboard.append([InlineKeyboardButton(text=header_text, callback_data="ignore")])

    # Kunlar nomlari
    day_names = {
        'uz': ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"],
        'ru': ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
        'en': ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
    }
    kb.inline_keyboard.append([InlineKeyboardButton(text=day, callback_data="ignore") for day in day_names[lang]])

    # Kalendar kunlari
    cal = calendar.Calendar(firstweekday=0) # Dushanba haftaning birinchi kuni
    for week in cal.monthdayscalendar(year, month):
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(text=str(day), callback_data=f"cal_date|{year}-{month}-{day}"))
        kb.inline_keyboard.append(row)

    # Navigatsiya tugmalari
    prev_month_year = month - 1 if month > 1 else 12
    prev_year_val = year if month > 1 else year - 1
    next_month_year = month + 1 if month < 12 else 1
    next_year_val = year if month < 12 else year + 1

    kb.inline_keyboard.append([
        InlineKeyboardButton(text="<", callback_data=f"cal_nav|{prev_year_val}-{prev_month_year}"),
        InlineKeyboardButton(text=today_button_text[lang], callback_data="cal_today"),
        InlineKeyboardButton(text=">", callback_data=f"cal_nav|{next_year_val}-{next_month_year}")
    ])
    return kb

def get_parent_of_student(student_id):
    """Talabaning ota-onasini (agar mavjud bo'lsa) topadi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Ota-ona rolidagi foydalanuvchining child_id si talabaning user_id siga teng bo'lsa
    c.execute("SELECT user_id, phone, language FROM users WHERE role = 'Parent' AND child_id = ?", (student_id,))
    parent = c.fetchone()
    conn.close()
    if parent:
        columns = ['user_id', 'phone', 'language'] # Faqat kerakli ustunlar
        return dict(zip(columns, parent))
    return None

def get_missed_classes_in_month(student_id, year, month):
    """Talabaning berilgan oyda qoldirgan darslari sonini hisoblaydi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Oyning boshlanishi va oxirgi kunini aniqlash
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"

    c.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE student_id = ? AND status = 'missed' AND date BETWEEN ? AND ?
    """, (student_id, start_date, end_date))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_teacher_average_rating(teacher_id, period='all_time'):
    """O'qituvchining o'rtacha reytingini hisoblaydi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    query = "SELECT AVG(q1_rating), AVG(q2_rating), AVG(q3_rating) FROM teacher_ratings WHERE teacher_id = ?"
    params = [teacher_id]

    if period == 'last_month':
        today = datetime.now()
        month_start = today.replace(day=1).strftime('%Y-%m-%d')
        month_end = today.strftime('%Y-%m-%d') # Bugungi kungacha
        query += " AND rating_date BETWEEN ? AND ?"
        params.extend([month_start, month_end])
    elif period == 'last_3_months':
        today = datetime.now()
        three_months_ago = today.replace(day=1) # Joriy oyning birinchi kuni
        # Orqaga 2 oy o'tib, o'sha oyning birinchi kunini topish
        for _ in range(2):
            if three_months_ago.month == 1:
                three_months_ago = three_months_ago.replace(year=three_months_ago.year - 1, month=12)
            else:
                three_months_ago = three_months_ago.replace(month=three_months_ago.month - 1)
        three_months_ago_start = three_months_ago.replace(day=1).strftime('%Y-%m-%d')
        query += " AND rating_date BETWEEN ? AND ?"
        params.extend([three_months_ago_start, today.strftime('%Y-%m-%d')])

    c.execute(query, params)
    avg_q1, avg_q2, avg_q3 = c.fetchone()
    conn.close()

    total_avg = 0
    count = 0
    if avg_q1 is not None:
        total_avg += avg_q1
        count += 1
    if avg_q2 is not None:
        total_avg += avg_q2
        count += 1
    if avg_q3 is not None:
        total_avg += avg_q3
        count += 1
    
    return total_avg / count if count > 0 else 0

def get_teacher_rating_count(teacher_id):
    """O'qituvchini baholagan talabalar sonini hisoblaydi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(DISTINCT student_id) FROM teacher_ratings WHERE teacher_id = ?", (teacher_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_all_users_by_role(role=None):
    """Barcha foydalanuvchilarni yoki rol bo'yicha foydalanuvchilarni qaytaradi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if role:
        c.execute("SELECT user_id, full_name, last_name, login, phone FROM users WHERE role = ?", (role,))
    else:
        c.execute("SELECT user_id, full_name, last_name, login, phone FROM users")
    users_data = c.fetchall()
    conn.close()
    users_list = []
    for u in users_data:
        users_list.append({
            'user_id': u[0],
            'full_name': u[1],
            'last_name': u[2],
            'login': u[3],
            'phone': u[4]
        })
    return users_list

def get_student_group_and_teacher_id(student_id):
    """Talabaning guruhini va o'qituvchisini (agar mavjud bo'lsa) qaytaradi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT g.group_name, g.teacher_id
        FROM group_assignments ga
        JOIN groups g ON ga.group_name = g.group_name
        WHERE ga.student_id = ?
    """, (student_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {'group_name': result[0], 'teacher_id': result[1]}
    return None

def get_student_attendance_records_for_month(student_id, year, month):
    """Talabaning berilgan oy uchun davomat yozuvlarini qaytaradi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{calendar.monthrange(year, month)[1]}"
    c.execute("""
        SELECT date, status, comment FROM attendance
        WHERE student_id = ? AND date BETWEEN ? AND ? ORDER BY date ASC
    """, (student_id, start_date, end_date))
    records = c.fetchall()
    conn.close()
    return records

def save_student_feedback(teacher_id, student_id, feedback_text, feedback_date):
    """Talaba (yoki ota-ona) tomonidan qoldirilgan fikrni saqlaydi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO student_feedback (teacher_id, student_id, feedback_text, feedback_date) VALUES (?, ?, ?, ?)",
              (teacher_id, student_id, feedback_text, feedback_date))
    conn.commit()
    conn.close()
    return True

def save_teacher_evaluation(teacher_id, student_id, q1_rating, q2_rating, q3_rating, rating_date):
    """O'qituvchi baholashini saqlaydi."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO teacher_ratings (teacher_id, student_id, q1_rating, q2_rating, q3_rating, rating_date) VALUES (?, ?, ?, ?, ?, ?)",
              (teacher_id, student_id, q1_rating, q2_rating, q3_rating, rating_date))
    conn.commit()
    conn.close()
    return True

