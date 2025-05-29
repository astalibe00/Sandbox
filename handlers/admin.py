# handlers/admin.py
# Bu fayl admin paneli funksiyalari uchun handlerlarni o'z ichiga oladi.

import logging
import sqlite3
from datetime import datetime
from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from translations import get_text, get_all_translations_for_key
from keyboards import get_super_admin_panel_keyboard # Admin paneli klaviaturasini import qilish

# utils.database.py dan kerakli funksiyalarni import qilish
from utils.database import (
    foydalanuvchini_id_bilan_olish,
    foydalanuvchini_login_bilan_olish, # <-- Bu qator qo'shildi
    DB_PATH,
    create_calendar_keyboard,
    get_all_users_by_role,
    update_user_group_name,
    update_parent_child_link,
    get_student_group_and_teacher_id, # Agar kerak bo'lsa
    get_student_attendance_records_for_month, # Agar kerak bo'lsa
    get_missed_classes_in_month, # Agar kerak bo'lsa
    get_teacher_average_rating, # Agar kerak bo'lsa
    get_teacher_rating_count, # Agar kerak bo'lsa
    save_student_feedback # Agar kerak bo'lsa
)

logger = logging.getLogger(__name__)

# ==============================================================================
# FSM Holatlari
# ==============================================================================
class GuruhYaratish(StatesGroup):
    guruh_nomi = State()
    dars_vaqtlari = State()

class GuruhgaTaqsimlash(StatesGroup):
    talaba_tanlash = State()
    guruh_tanlash = State()

class OqituvchiTaqsimlash(StatesGroup):
    guruh_tanlash = State()
    oqituvchi_tanlash = State()

class DarsJadvaliniBelgilash(StatesGroup):
    guruh_tanlash = State()
    dars_vaqtlari = State()
    tasdiqlash_jadval = State()

class AdminActions(StatesGroup):
    assign_role = State()
    assign_parent_child = State()
    select_user_for_details = State()
    mass_message_input = State()
    individual_message_select_type = State()
    individual_message_select_user = State()
    individual_message_input = State()
    view_feedback_select_teacher = State()

# ==============================================================================
# ADMIN PANELI HANDLERLARI
# ==============================================================================
async def super_admin_paneli(message: types.Message, lang: str):
    """
    Super Admin paneliga kirish va asosiy menyuni ko'rsatish.
    """
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    if not user:
        lang = 'uz' # Agar foydalanuvchi topilmasa, default til
        await message.answer(get_text(lang, 'user_not_found'))
        logger.error(f"Foydalanuvchi topilmadi: user_id={message.from_user.id}, language={lang}")
        return
    lang = user['language'] # Foydalanuvchi tilini yangilash
    if user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        logger.warning(f"Super admin paneliga kirish rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return
    
    await message.answer(get_text(lang, 'super_admin_panel'), reply_markup=get_super_admin_panel_keyboard(lang))
    logger.info(f"Super Admin paneli ochildi: user_id={message.from_user.id}, language={lang}")

# Guruh yaratish
async def guruh_yaratishni_boshlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    await message.answer(get_text(lang, 'enter_group_name'), reply_markup=ReplyKeyboardRemove())
    await state.set_state(GuruhYaratish.guruh_nomi)
    logger.info(f"Guruh yaratish jarayoni boshlandi: user_id={message.from_user.id}, language={lang}")

async def guruh_nomini_qayta_ishlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    guruh_nomi = message.text.strip()
    if not guruh_nomi:
        await message.answer(get_text(lang, 'invalid_group_name'))
        logger.warning(f"Noto‘g‘ri guruh nomi: user_id={message.from_user.id}, language={lang}")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups WHERE group_name = ?", (guruh_nomi,))
        if c.fetchone():
            await message.answer(get_text(lang, 'group_exists'))
            logger.warning(f"Guruh allaqachon mavjud: guruh_nomi={guruh_nomi}, user_id={message.from_user.id}, language={lang}")
            conn.close()
            return
        await state.update_data(guruh_nomi=guruh_nomi)
        await message.answer(get_text(lang, 'enter_class_times'))
        await state.set_state(GuruhYaratish.dars_vaqtlari)
        logger.info(f"Guruh nomi kiritildi: guruh_nomi={guruh_nomi}, user_id={message.from_user.id}, language={lang}")
        conn.close()
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (guruh_nomini_qayta_ishlash): {e}, user_id={message.from_user.id}, language={lang}")

async def dars_vaqtlarini_qayta_ishlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    class_times = message.text.strip()
    data = await state.get_data()
    guruh_nomi = data['guruh_nomi']
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO groups (group_name, class_times) VALUES (?, ?)", (guruh_nomi, class_times))
        conn.commit()
        await message.answer(get_text(lang, 'group_created').format(group_name=guruh_nomi))
        logger.info(f"Yangi guruh yaratildi: guruh_nomi={guruh_nomi}, class_times={class_times}, user_id={message.from_user.id}, language={lang}")
        conn.close()
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (dars_vaqtlarini_qayta_ishlash): {e}, user_id={message.from_user.id}, language={lang}")
    await state.clear()

# Guruhlar ro'yxatini ko'rsatish
async def guruhlar_royxatini_korsatish(message: types.Message):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups")
        guruhlar = c.fetchall()
        conn.close()
        if not guruhlar:
            await message.answer(get_text(lang, 'no_groups'))
            logger.info(f"Hech qanday guruh topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=g[0], callback_data=f"guruh_malumot|{g[0]}")] for g in guruhlar
        ])
        await message.answer(get_text(lang, 'select_group'), reply_markup=keyboard)
        logger.info(f"Guruhlar ro‘yxati ko‘rsatildi: user_id={message.from_user.id}, guruhlar_soni={len(guruhlar)}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (guruhlar_royxatini_korsatish): {e}, user_id={message.from_user.id}, language={lang}")

async def guruh_malumotlarini_korsatish(callback_query: types.CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    guruh_nomi = callback_query.data.split('|')[1]
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT teacher_id, class_times FROM groups WHERE group_name = ?", (guruh_nomi,))
        guruh = c.fetchone()
        teacher_id, class_times = guruh if guruh else (None, None)
        teacher_info = get_text(lang, 'no_teacher')
        if teacher_id:
            teacher = foydalanuvchini_id_bilan_olish(teacher_id)
            teacher_info = f"{teacher['full_name']} {teacher['last_name'] or ''}".strip() if teacher else get_text(lang, 'no_teacher')
        c.execute("""
            SELECT u.full_name, u.last_name
            FROM users u
            JOIN group_assignments ga ON u.user_id = ga.student_id
            WHERE ga.group_name = ? AND u.role = 'Student'
        """, (guruh_nomi,))
        talabalar = c.fetchall()
        conn.close()
        talabalar_royxati = get_text(lang, 'no_students')
        if talabalar:
            talabalar_royxati = "\n".join([f"- {full_name} {last_name or ''}".strip() for full_name, last_name in talabalar])
        guruh_malumotlari = get_text(lang, 'group_details').format(
            group_name=guruh_nomi,
            teacher_info=teacher_info,
            class_times=class_times if class_times else get_text(lang, 'not_set'),
            students=talabalar_royxati
        )
        await callback_query.message.answer(guruh_malumotlari)
        logger.info(f"Guruh ma’lumotlari ko‘rsatildi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (guruh_malumotlarini_korsatish): {e}, user_id={callback_query.from_user.id}, language={lang}")

# Talabalarni guruhga taqsimlash
async def talabalarni_guruhlarga_taqsimlashni_boshlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, full_name, last_name FROM users WHERE role = 'Student'")
        talabalar = c.fetchall()
        conn.close()
        if not talabalar:
            await message.answer(get_text(lang, 'no_students'))
            logger.info(f"Talabalar topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{u[1]} {u[2] or ''}".strip(), callback_data=f"assign_student|{u[0]}")] for u in talabalar
        ])
        await message.answer(get_text(lang, 'select_student'), reply_markup=keyboard)
        await state.set_state(GuruhgaTaqsimlash.talaba_tanlash)
        logger.info(f"Talabalar ro‘yxati ko‘rsatildi: user_id={message.from_user.id}, talabalar_soni={len(talabalar)}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (talabalarni_guruhlarga_taqsimlashni_boshlash): {e}, user_id={message.from_user.id}, language={lang}")

async def talaba_tanlash(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    student_id = int(callback_query.data.split('|')[1])
    await state.update_data(student_id=student_id)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups")
        guruhlar = c.fetchall()
        conn.close()
        if not guruhlar:
            await callback_query.message.answer(get_text(lang, 'no_groups'))
            logger.info(f"Guruhlar topilmadi: user_id={callback_query.from_user.id}, language={lang}")
            await state.clear()
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=g[0], callback_data=f"assign_group|{g[0]}")] for g in guruhlar
        ])
        await callback_query.message.answer(get_text(lang, 'select_group'), reply_markup=keyboard)
        await state.set_state(GuruhgaTaqsimlash.guruh_tanlash)
        logger.info(f"Guruhlar ro‘yxati ko‘rsatildi: student_id={student_id}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (talaba_tanlash): {e}, user_id={callback_query.from_user.id}, language={lang}")

async def guruh_tanlash(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    guruh_nomi = callback_query.data.split('|')[1]
    data = await state.get_data()
    student_id = data['student_id']
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO group_assignments (student_id, group_name) VALUES (?, ?)", (student_id, guruh_nomi))
        conn.commit()
        conn.close()

        # Update users.group_name
        update_user_group_name(student_id, guruh_nomi)
        
        await callback_query.message.answer(get_text(lang, 'student_assigned').format(student_id=student_id, group_name=guruh_nomi))
        logger.info(f"Talaba guruhga taqsimlandi va users.group_name yangilandi: student_id={student_id}, guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")

    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (guruh_tanlash): {e}, user_id={callback_query.from_user.id}, language={lang}")
    await state.clear()

# O'qituvchilarni guruhlarga taqsimlash
async def oqituvchi_taqsimlashni_boshlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups")
        guruhlar = c.fetchall()
        conn.close()
        if not guruhlar:
            await message.answer(get_text(lang, 'no_groups'))
            logger.info(f"Guruhlar topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=g[0], callback_data=f"teacher_group|{g[0]}")] for g in guruhlar
        ])
        await message.answer(get_text(lang, 'select_group'), reply_markup=keyboard)
        await state.set_state(OqituvchiTaqsimlash.guruh_tanlash)
        logger.info(f"Guruhlar ro‘yxati ko‘rsatildi: user_id={message.from_user.id}, guruhlar_soni={len(guruhlar)}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (oqituvchi_taqsimlashni_boshlash): {e}, user_id={message.from_user.id}, language={lang}")

async def oqituvchi_guruh_tanlash(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    guruh_nomi = callback_query.data.split('|')[1]
    await state.update_data(guruh_nomi=guruh_nomi)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, full_name, last_name FROM users WHERE role = 'Teacher'")
        oqituvchilar = c.fetchall()
        conn.close()
        if not oqituvchilar:
            await callback_query.message.answer(get_text(lang, 'no_teachers'))
            logger.info(f"O‘qituvchilar topilmadi: user_id={callback_query.from_user.id}, language={lang}")
            await state.clear()
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{u[1]} {u[2] or ''}".strip(), callback_data=f"teacher_assign|{u[0]}")] for u in oqituvchilar
        ])
        await callback_query.message.answer(get_text(lang, 'select_teacher'), reply_markup=keyboard)
        await state.set_state(OqituvchiTaqsimlash.oqituvchi_tanlash)
        logger.info(f"O‘qituvchilar ro‘yxati ko‘rsatildi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (oqituvchi_guruh_tanlash): {e}, user_id={callback_query.from_user.id}, language={lang}")

async def oqituvchi_tanlash(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    teacher_id = int(callback_query.data.split('|')[1])
    data = await state.get_data()
    guruh_nomi = data['guruh_nomi']
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE groups SET teacher_id = ? WHERE group_name = ?", (teacher_id, guruh_nomi))
        conn.commit()
        conn.close()
        await callback_query.message.answer(get_text(lang, 'teacher_assigned').format(teacher_id=teacher_id, group_name=guruh_nomi))
        logger.info(f"O‘qituvchi guruhga taqsimlandi: teacher_id={teacher_id}, guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma‘lumotlar ombori xatosi (oqituvchi_tanlash): {e}, user_id={callback_query.from_user.id}, language={lang}")
    await state.clear()

# Dars jadvalini belgilash
async def dars_jadvalini_belgilashni_boshlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups")
        guruhlar = c.fetchall()
        conn.close()
        if not guruhlar:
            await message.answer(get_text(lang, 'no_groups'))
            logger.info(f"Hech qanday guruh topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=g[0], callback_data=f"jadval_guruh|{g[0]}")] for g in guruhlar
        ])
        await message.answer(get_text(lang, 'select_group_for_schedule'), reply_markup=keyboard)
        await state.set_state(DarsJadvaliniBelgilash.guruh_tanlash)
        logger.info(f"Dars jadvalini belgilash boshlandi: user_id={message.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (dars_jadvalini_boshlash): {e}, user_id={message.from_user.id}, language={lang}")

async def jadval_uchun_guruh_tanlash(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    guruh_nomi = callback_query.data.split('|')[1]
    await state.update_data(guruh_nomi=guruh_nomi)
    
    now = datetime.now()
    keyboard = create_calendar_keyboard(now.year, now.month, lang)
    await callback_query.message.edit_text(get_text(lang, 'select_schedule_date'), reply_markup=keyboard)
    await state.set_state(DarsJadvaliniBelgilash.dars_vaqtlari)
    logger.info(f"Guruh tanlandi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")

async def process_schedule_calendar_selection(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    
    data = callback_query.data.split('|')
    action = data[0]

    if action == "cal_nav":
        year, month = map(int, data[1].split('-'))
        new_keyboard = create_calendar_keyboard(year, month, lang)
        await callback_query.message.edit_reply_markup(reply_markup=new_keyboard)
        logger.info(f"Kalendar navigatsiyasi (jadval): {year}-{month}, user_id={callback_query.from_user.id}")
    elif action == "cal_date":
        selected_date_str = data[1]
        await state.update_data(selected_schedule_date=selected_date_str)
        
        await callback_query.message.edit_text(get_text(lang, 'enter_class_times_for_date').format(date=selected_date_str))
        await state.set_state(DarsJadvaliniBelgilash.tasdiqlash_jadval)
        logger.info(f"Jadval sanasi tanlandi ({selected_date_str}), dars vaqtlarini kiritishga o'tildi, user_id={callback_query.from_user.id}, language={lang}")
    elif action == "cal_today":
        today = datetime.now().strftime("%Y-%m-%d")
        await state.update_data(selected_schedule_date=today)
        
        await callback_query.message.edit_text(get_text(lang, 'enter_class_times_for_date').format(date=today))
        await state.set_state(DarsJadvaliniBelgilash.tasdiqlash_jadval)
        logger.info(f"Jadval bugungi sana tanlandi ({today}), dars vaqtlarini kiritishga o'tildi, user_id={callback_query.from_user.id}, language={lang}")
    elif action == "ignore":
        pass

async def dars_vaqtlarini_tasdiqlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    dars_vaqtlari_text = message.text.strip()

    if not dars_vaqtlari_text:
        await message.answer(get_text(lang, 'class_times_empty'))
        logger.warning(f"Bo'sh dars vaqtlari: user_id={message.from_user.id}, language={lang}")
        return

    data = await state.get_data()
    guruh_nomi = data['guruh_nomi']
    selected_schedule_date = data.get('selected_schedule_date', 'Noma\'lum sana')

    await state.update_data(kiritilgan_dars_vaqtlari=dars_vaqtlari_text)

    confirm_save_schedule_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, 'confirm_save_schedule_yes'), callback_data=f"djs_save:{guruh_nomi}|{selected_schedule_date}")],
        [InlineKeyboardButton(text=get_text(lang, 'confirm_save_schedule_no'), callback_data="djs_retry")]
    ])

    await message.answer(
        get_text(lang, 'confirm_schedule_text_with_date').format(group_name=guruh_nomi, date=selected_schedule_date, class_times=dars_vaqtlari_text),
        reply_markup=confirm_save_schedule_keyboard
    )
    logger.info(f"Dars jadvali tasdiqlash uchun yuborildi: guruh_nomi={guruh_nomi}, sana={selected_schedule_date}, dars_vaqtlari={dars_vaqtlari_text}, user_id={message.from_user.id}")

async def confirm_save_schedule_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']

    data_parts = callback_query.data.split(':')
    guruh_nomi = data_parts[1].split('|')[0]
    selected_schedule_date = data_parts[1].split('|')[1]

    data = await state.get_data()
    dars_vaqtlari = data['kiritilgan_dars_vaqtlari']

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE groups SET class_times = ? WHERE group_name = ?", (f"{selected_schedule_date}: {dars_vaqtlari}", guruh_nomi))
        conn.commit()
        conn.close()
        await callback_query.message.edit_text(get_text(lang, 'schedule_assigned_confirmed').format(group_name=guruh_nomi, class_times=f"{selected_schedule_date}: {dars_vaqtlari}"))
        logger.info(f"Dars jadvali saqlandi: guruh_nomi={guruh_nomi}, dars_vaqtlari={selected_schedule_date}: {dars_vaqtlari}, user_id={callback_query.from_user.id}")
    except sqlite3.Error as e:
        await callback_query.message.edit_text(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (jadvalni saqlash): {e}, user_id={callback_query.from_user.id}")
    await state.clear()

async def retry_schedule_input_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']

    data = await state.get_data()
    selected_schedule_date = data.get('selected_schedule_date', 'Noma\'lum sana')

    await callback_query.message.edit_text(get_text(lang, 'enter_class_times_for_date').format(date=selected_schedule_date))
    await state.set_state(DarsJadvaliniBelgilash.tasdiqlash_jadval)
    logger.info(f"Dars jadvalini qayta kiritish so'raldi, user_id={callback_query.from_user.id}")

# Rollarni belgilash
async def rollarni_belgilashni_boshlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, login, phone, full_name, last_name FROM users WHERE role = 'pending'")
        pending_users = c.fetchall()
        conn.close()
        if not pending_users:
            await message.answer(get_text(lang, 'no_pending_users'))
            logger.info(f"Kutayotgan foydalanuvchilar yo'q: user_id={message.from_user.id}, language={lang}")
            return
        pending_users_list = get_text(lang, 'pending_users')
        for pending_user in pending_users:
            user_id, login, phone, full_name, last_name = pending_user
            name = f"{full_name} {last_name or ''}".strip()
            pending_users_list += get_text(lang, 'pending_user_info').format(id=user_id, login=login, phone=phone, name=name)
        await message.answer(
            pending_users_list + "\n" + get_text(lang, 'role_format'),
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(AdminActions.assign_role)
        logger.info(f"Rollarni belgilash boshlandi: user_id={message.from_user.id}, pending_users={len(pending_users)}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (rollarni_belgilashni_boshlash): {e}, user_id={message.from_user.id}, language={lang}")

async def rolni_qayta_ishlash(message: types.Message, state: FSMContext):
    user_obj = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user_obj['language']

    parts = message.text.split(':', 2)
    login = parts[0].strip()
    role_input = ""
    tariff_plan_input = None

    if len(parts) >= 2:
        role_input = parts[1].strip()
    if len(parts) == 3:
        tariff_plan_input = parts[2].strip()

    valid_roles = ['Student', 'Parent', 'Teacher']
    valid_tariffs = {'Elite': 800000, 'Express': 1600000}

    final_tariff_plan = None
    final_tariff_price = None

    state_data = await state.get_data()
    if 'login_to_change_role' in state_data:
        login = state_data['login_to_change_role']
        if not tariff_plan_input:
            existing_user = foydalanuvchini_login_bilan_olish(login)
            if existing_user:
                tariff_plan_input = existing_user.get('tariff_plan')

    if not login or not role_input:
        await message.answer(get_text(lang, 'role_format'))
        logger.warning(f"Noto'g'ri umumiy format: text={message.text}, user_id={message.from_user.id}")
        return

    if role_input not in valid_roles:
        await message.answer(get_text(lang, 'invalid_role').format(roles=', '.join(valid_roles)))
        logger.warning(f"Noto'g'ri rol: {role_input}, user_id={message.from_user.id}")
        return

    foydalanuvchi_uchun_update = foydalanuvchini_login_bilan_olish(login)
    if not foydalanuvchi_uchun_update:
        await message.answer(get_text(lang, 'user_not_found_login').format(login=login))
        logger.warning(f"Foydalanuvchi topilmadi: login={login}, user_id={message.from_user.id}")
        return

    if role_input == 'Teacher':
        if tariff_plan_input:
            if tariff_plan_input not in valid_tariffs:
                await message.answer(get_text(lang, 'invalid_tariff'))
                logger.warning(f"O'qituvchi uchun noto'g'ri tarif: {tariff_plan_input}, user_id={message.from_user.id}")
                return
            final_tariff_plan = tariff_plan_input
            final_tariff_price = valid_tariffs[final_tariff_plan]
    elif role_input in ['Student', 'Parent']:
        if not tariff_plan_input or tariff_plan_input not in valid_tariffs:
            await message.answer(get_text(lang, 'tariff_required_student_parent'))
            logger.warning(f"Talaba/Ota-ona uchun tarif xatosi: {tariff_plan_input}, user_id={message.from_user.id}")
            return
        final_tariff_plan = tariff_plan_input
        final_tariff_price = valid_tariffs[final_tariff_plan]

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET role = ?, tariff_plan = ?, tariff_price = ? WHERE login = ?",
                  (role_input, final_tariff_plan, final_tariff_price, login))
        conn.commit()
        conn.close()

        if role_input == 'Parent':
            await state.update_data(parent_login_to_link=login)
            await message.answer(get_text(lang, 'enter_child_login'))
            await state.set_state(AdminActions.assign_parent_child)
            logger.info(f"Ota-ona roli berildi, talabani biriktirish so'raldi: login={login}, user_id={message.from_user.id}")
            return
        
        if final_tariff_plan and final_tariff_price:
            await message.answer(get_text(lang, 'role_assigned').format(login=login, role=role_input, tariff=final_tariff_plan, price=final_tariff_price))
            logger.info(f"Rol va tarif berildi: login={login}, role={role_input}, tariff={final_tariff_plan}, price={final_tariff_price}, user_id={message.from_user.id}")
        else:
            await message.answer(get_text(lang, 'role_assigned_no_tariff').format(login=login, role=role_input))
            logger.info(f"Rol berildi (tarifsiz): login={login}, role={role_input}, user_id={message.from_user.id}")

    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (rolni_qayta_ishlash): {e}, user_id={message.from_user.id}")
    
    await state.clear()

async def assign_parent_child_process(message: types.Message, state: FSMContext):
    user_admin = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user_admin['language']
    child_login = message.text.strip()

    data = await state.get_data()
    parent_login = data.get('parent_login_to_link')
    
    parent_user_obj = foydalanuvchini_login_bilan_olish(parent_login)
    child_user_obj = foydalanuvchini_login_bilan_olish(child_login)

    if not child_user_obj or child_user_obj['role'] != 'Student':
        await message.answer(get_text(lang, 'student_not_found_for_parent').format(login=child_login))
        logger.warning(f"Talaba topilmadi yoki 'Student' rolida emas: child_login={child_login}, user_id={message.from_user.id}")
        await state.clear()
        return

    if parent_user_obj and update_parent_child_link(parent_user_obj['user_id'], child_user_obj['user_id']):
        await message.answer(get_text(lang, 'parent_linked_to_student').format(parent_login=parent_login, student_login=child_login))
        logger.info(f"Ota-ona {parent_login} talaba {child_login} ga biriktirildi. user_id={message.from_user.id}")
    else:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ota-onani talabaga biriktirishda xato: parent_login={parent_login}, child_login={child_login}, user_id={message.from_user.id}")
    
    await state.clear()

async def users_list_start(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return
    
    all_users = get_all_users_by_role()
    if not all_users:
        await message.answer(get_text(lang, 'no_users_found_for_role').format(role=get_text(lang, 'all_users')))
        logger.info(f"Foydalanuvchilar topilmadi: user_id={message.from_user.id}, language={lang}")
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{u['full_name']} {u['last_name'] or ''}".strip(), callback_data=f"user_details_view|{u['user_id']}")] for u in all_users
    ])
    await message.answer(get_text(lang, 'select_user_for_details'), reply_markup=keyboard)
    await state.set_state(AdminActions.select_user_for_details)
    logger.info(f"Foydalanuvchilar ro'yxati ko'rsatildi: user_id={message.from_user.id}, language={lang}")

async def show_user_details(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user_admin = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user_admin['language']
    target_user_id = int(callback_query.data.split('|')[1])

    target_user_info = foydalanuvchini_id_bilan_olish(target_user_id)
    if not target_user_info:
        await callback_query.message.answer(get_text(lang, 'user_not_found'))
        logger.warning(f"Ma'lumotlari so'ralgan foydalanuvchi topilmadi: user_id={target_user_id}")
        await state.clear()
        return

    full_name = f"{target_user_info.get('full_name', '')} {target_user_info.get('last_name', '') or ''}".strip()
    group_name = target_user_info.get('group_name', get_text(lang, 'not_set'))
    tariff_plan = target_user_info.get('tariff_plan', get_text(lang, 'not_set'))
    tariff_price = target_user_info.get('tariff_price', 0)
    debt_amount = target_user_info.get('debt_amount', 0)
    payment_status = target_user_info.get('payment_status', get_text(lang, 'not_set'))
    
    user_details_text = get_text(lang, 'user_details_full').format(
        user_id=target_user_info.get('user_id', get_text(lang, 'not_set')),
        full_name=full_name,
        last_name=target_user_info.get('last_name', get_text(lang, 'not_set')),
        login=target_user_info.get('login'),
        phone=target_user_info.get('phone'),
        role=target_user_info.get('role'),
        group_name=group_name,
        tariff_plan=tariff_plan,
        tariff_price=tariff_price,
        debt_amount=debt_amount,
        payment_status=payment_status,
        language=target_user_info.get('language', 'uz')
    )
    await callback_query.message.answer(user_details_text)
    logger.info(f"Foydalanuvchi ma'lumotlari ko'rsatildi: target_user_id={target_user_id}, admin_id={callback_query.from_user.id}")
    await state.clear()

# Ommaviy xabar yuborish
async def send_mass_message_start(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return
    await message.answer(get_text(lang, 'enter_mass_message'), reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminActions.mass_message_input)
    logger.info(f"Ommaviy xabar yuborish boshlandi: user_id={message.from_user.id}, language={lang}")

async def send_mass_message_process(message: types.Message, state: FSMContext):
    user_admin = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user_admin['language']
    message_text = message.text.strip()

    if not message_text:
        await message.answer(get_text(lang, 'message_empty'))
        logger.warning(f"Bo'sh ommaviy xabar: user_id={message.from_user.id}, language={lang}")
        return

    all_users = get_all_users_by_role()
    sent_count = 0
    failed_count = 0

    for user_data in all_users:
        try:
            full_message = f"{message_text}\n\n{get_text(lang, 'message_from_admin')}\nEslatma: {user_data['full_name']} {user_data['last_name'] or ''}".strip()
            await message.bot.send_message(user_data['user_id'], full_message) # message.bot orqali botga murojaat
            sent_count += 1
        except Exception as e:
            logger.error(f"Ommaviy xabar yuborishda xato: user_id={user_data['user_id']}, error={e}")
            failed_count += 1
    
    await message.answer(get_text(lang, 'mass_message_sent_summary').format(sent=sent_count, failed=failed_count))
    logger.info(f"Ommaviy xabar yuborish yakunlandi: sent={sent_count}, failed={failed_count}, user_id={message.from_user.id}, language={lang}")
    await state.clear()

# Shaxsiy xabar yuborish
async def send_individual_message_start(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, 'student_role'), callback_data="ind_msg_role|Student"),
         InlineKeyboardButton(text=get_text(lang, 'parent_role'), callback_data="ind_msg_role|Parent")],
        [InlineKeyboardButton(text=get_text(lang, 'teacher_role'), callback_data="ind_msg_role|Teacher"),
         InlineKeyboardButton(text=get_text(lang, 'all_users'), callback_data="ind_msg_role|all")]
    ])
    await message.answer(get_text(lang, 'select_user_type_for_message'), reply_markup=keyboard)
    await state.set_state(AdminActions.individual_message_select_type)
    logger.info(f"Shaxsiy xabar yuborish boshlandi: user_id={message.from_user.id}, language={lang}")

async def individual_message_select_user_type(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user_admin = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user_admin['language']
    selected_role = callback_query.data.split('|')[1]
    await state.update_data(selected_message_role=selected_role)

    users_to_select = []
    if selected_role == 'all':
        users_to_select = get_all_users_by_role()
    else:
        users_to_select = get_all_users_by_role(selected_role)

    if not users_to_select:
        await callback_query.message.edit_text(get_text(lang, 'no_users_found_for_role').format(role=selected_role))
        logger.info(f"Shaxsiy xabar uchun foydalanuvchilar topilmadi: role={selected_role}, user_id={callback_query.from_user.id}, language={lang}")
        await state.clear()
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{u['full_name']} {u['last_name'] or ''}".strip(), callback_data=f"ind_msg_user|{u['user_id']}")] for u in users_to_select
    ])
    await callback_query.message.edit_text(get_text(lang, 'select_user_to_message'), reply_markup=keyboard)
    await state.set_state(AdminActions.individual_message_select_user)
    logger.info(f"Shaxsiy xabar uchun foydalanuvchi tanlash: role={selected_role}, user_id={callback_query.from_user.id}, language={lang}")

async def individual_message_select_user(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user_admin = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user_admin['language']
    selected_user_id = int(callback_query.data.split('|')[1])
    await state.update_data(target_user_id=selected_user_id)

    target_user_info = foydalanuvchini_id_bilan_olish(selected_user_id)
    target_user_name = f"{target_user_info['full_name']} {target_user_info['last_name'] or ''}".strip() if target_user_info else f"ID: {selected_user_id}"

    await callback_query.message.edit_text(get_text(lang, 'enter_message_for_user').format(user_name=target_user_name))
    await state.set_state(AdminActions.individual_message_input)
    logger.info(f"Shaxsiy xabar kiritish boshlandi: target_user_id={selected_user_id}, user_id={callback_query.from_user.id}, language={lang}")

async def individual_message_send(message: types.Message, state: FSMContext):
    user_admin = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user_admin['language']
    message_text = message.text.strip()
    data = await state.get_data()
    target_user_id = data['target_user_id']

    if not message_text:
        await message.answer(get_text(lang, 'message_empty'))
        logger.warning(f"Bo'sh shaxsiy xabar: user_id={message.from_user.id}, target_user_id={target_user_id}, language={lang}")
        return

    try:
        target_user_info = foydalanuvchini_id_bilan_olish(target_user_id)
        target_user_name = f"{target_user_info['full_name']} {target_user_info['last_name'] or ''}".strip() if target_user_info else f"ID: {target_user_id}"
        
        full_message = f"{message_text}\n\n{get_text(lang, 'message_from_admin_individual')}\nEslatma: {target_user_name} (ID: {target_user_id})"
        
        await message.bot.send_message(target_user_id, full_message) # message.bot orqali botga murojaat
        await message.answer(get_text(lang, 'message_sent_success').format(user_name=target_user_name))
        logger.info(f"Shaxsiy xabar yuborildi: target_user_id={target_user_id}, user_id={message.from_user.id}, language={lang}")
    except Exception as e:
        await message.answer(get_text(lang, 'message_sent_failed').format(user_name=target_user_name))
        logger.error(f"Shaxsiy xabar yuborishda xato: target_user_id={target_user_id}, error={e}, user_id={message.from_user.id}, language={lang}")
    
    await state.clear()

# Fikr-mulohazalarni ko'rish
async def view_feedback_start(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT user_id, full_name, last_name FROM users WHERE role = 'Teacher'")
        teachers = c.fetchall()
        conn.close()

        if not teachers:
            await message.answer(get_text(lang, 'no_teachers_for_feedback_view'))
            logger.info(f"Fikrlar bazasini ko'rish uchun o'qituvchilar topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{t[1]} {t[2] or ''}".strip(), callback_data=f"view_feedback_teacher|{t[0]}")] for t in teachers
        ])
        await message.answer(get_text(lang, 'select_teacher_for_feedback_view'), reply_markup=keyboard)
        await state.set_state(AdminActions.view_feedback_select_teacher)
        logger.info(f"Fikrlar bazasini ko'rish boshlandi: user_id={message.from_user.id}, language={lang}")

    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (view_feedback_start): {e}, user_id={message.from_user.id}")

async def view_feedback_for_teacher(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user_admin = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user_admin['language']
    teacher_id = int(callback_query.data.split('|')[1])

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT student_id, feedback_text, feedback_date FROM student_feedback WHERE teacher_id = ? ORDER BY feedback_date DESC", (teacher_id,))
        feedbacks = c.fetchall()
        conn.close()

        teacher_info = foydalanuvchini_id_bilan_olish(teacher_id)
        teacher_name = f"{teacher_info['full_name']} {teacher_info['last_name'] or ''}".strip() if teacher_info else f"ID: {teacher_id}"

        if not feedbacks:
            await callback_query.message.edit_text(get_text(lang, 'no_feedback_for_teacher').format(teacher_name=teacher_name))
            logger.info(f"O'qituvchi uchun fikrlar topilmadi: teacher_id={teacher_id}, user_id={callback_query.from_user.id}, language={lang}")
            return
        
        feedback_list_text = get_text(lang, 'feedback_list_for_teacher').format(teacher_name=teacher_name)
        for student_id_anon, feedback_text, feedback_date in feedbacks:
            feedback_list_text += get_text(lang, 'feedback_entry').format(
                date=feedback_date,
                feedback=feedback_text
            )
        
        await callback_query.message.edit_text(feedback_list_text)
        logger.info(f"O'qituvchi uchun fikrlar ko'rsatildi: teacher_id={teacher_id}, count={len(feedbacks)}, user_id={callback_query.from_user.id}, language={lang}")

    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (view_feedback_for_teacher): {e}, user_id={callback_query.from_user.id}, language={lang}")
    
    await state.clear()

# Statistika
async def statistikani_korsatish(message: types.Message):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user or user['role'] != 'super_admin':
        await message.answer(get_text(lang, 'not_super_admin'))
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Super admin har doim barcha talabalar statistikasini ko'radi
        c.execute("""
            SELECT u.user_id, u.full_name, u.last_name, COUNT(a.student_id) as missed
            FROM users u
            LEFT JOIN attendance a ON u.user_id = a.student_id AND a.status = 'missed'
            WHERE u.role = 'Student'
            GROUP BY u.user_id, u.full_name, u.last_name
        """)
        stats = c.fetchall()
        conn.close()
        if not stats:
            await message.answer(get_text(lang, 'no_students'))
            logger.info(f"Statistika uchun talabalar topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        stats_text = get_text(lang, 'statistics_text')
        for stat in stats:
            user_id, full_name, last_name, missed = stat
            name = f"{full_name} {last_name or ''}".strip()
            stats_text += f"{name} (ID: {user_id}): {missed} {get_text(lang, 'missed_classes')}\n"
        await message.answer(stats_text)
        logger.info(f"Statistika ko'rsatildi: user_id={message.from_user.id}, stats_soni={len(stats)}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (statistikani_korsatish): {e}, user_id={message.from_user.id}, language={lang}")

# ==============================================================================
# HANDLERLARNI RO'YXATDAN O'TKAZISH FUNKSIYASI
# ==============================================================================
def register_admin_handlers(dp: Dispatcher):
    """
    Admin paneli uchun handlerlarni ro'yxatdan o'tkazadi.
    """
    # Super admin paneli
    # Filtrlar alohida argumentlar sifatida uzatildi
    dp.message.register(super_admin_paneli, F.text.in_(get_all_translations_for_key('super_admin_panel')), Command("admin"))
    
    # Guruh yaratish
    dp.message.register(guruh_yaratishni_boshlash, F.text.in_(get_all_translations_for_key('create_group')))
    dp.message.register(guruh_nomini_qayta_ishlash, GuruhYaratish.guruh_nomi)
    dp.message.register(dars_vaqtlarini_qayta_ishlash, GuruhYaratish.dars_vaqtlari)

    # Guruhlar ro'yxatini ko'rsatish
    dp.message.register(guruhlar_royxatini_korsatish, F.text.in_(get_all_translations_for_key('show_groups')))
    dp.callback_query.register(guruh_malumotlarini_korsatish, F.data.startswith('guruh_malumot|'))

    # Talabalarni guruhga taqsimlash
    dp.message.register(talabalarni_guruhlarga_taqsimlashni_boshlash, F.text.in_(get_all_translations_for_key('assign_students_to_groups')))
    dp.callback_query.register(talaba_tanlash, F.data.startswith('assign_student|'), F.state == GuruhgaTaqsimlash.talaba_tanlash)
    dp.callback_query.register(guruh_tanlash, F.data.startswith('assign_group|'), F.state == GuruhgaTaqsimlash.guruh_tanlash)

    # O'qituvchilarni guruhlarga taqsimlash
    dp.message.register(oqituvchi_taqsimlashni_boshlash, F.text.in_(get_all_translations_for_key('assign_teachers_to_groups')))
    dp.callback_query.register(oqituvchi_guruh_tanlash, F.data.startswith('teacher_group|'), F.state == OqituvchiTaqsimlash.guruh_tanlash)
    dp.callback_query.register(oqituvchi_tanlash, F.data.startswith('teacher_assign|'), F.state == OqituvchiTaqsimlash.oqituvchi_tanlash)

    # Dars jadvalini belgilash
    dp.message.register(dars_jadvalini_belgilashni_boshlash, F.text.in_(get_all_translations_for_key('assign_schedule')))
    dp.callback_query.register(jadval_uchun_guruh_tanlash, F.data.startswith('jadval_guruh|'), F.state == DarsJadvaliniBelgilash.guruh_tanlash)
    dp.callback_query.register(process_schedule_calendar_selection, F.data.startswith('cal_'), F.state == DarsJadvaliniBelgilash.dars_vaqtlari)
    dp.message.register(dars_vaqtlarini_tasdiqlash, DarsJadvaliniBelgilash.tasdiqlash_jadval)
    dp.callback_query.register(confirm_save_schedule_handler, F.data.startswith("djs_save:"), F.state == DarsJadvaliniBelgilash.tasdiqlash_jadval)
    dp.callback_query.register(retry_schedule_input_handler, F.data == "djs_retry", F.state == DarsJadvaliniBelgilash.tasdiqlash_jadval)

    # Rollarni belgilash
    dp.message.register(rollarni_belgilashni_boshlash, F.text.in_(get_all_translations_for_key('assign_roles')))
    dp.message.register(rolni_qayta_ishlash, AdminActions.assign_role)
    dp.message.register(assign_parent_child_process, AdminActions.assign_parent_child)

    # Foydalanuvchilar ro'yxati va ma'lumotlari
    dp.message.register(users_list_start, F.text.in_(get_all_translations_for_key('users')))
    dp.callback_query.register(show_user_details, F.data.startswith('user_details_view|'), F.state == AdminActions.select_user_for_details)

    # Ommaviy xabar yuborish
    dp.message.register(send_mass_message_start, F.text.in_(get_all_translations_for_key('send_mass_message')))
    dp.message.register(send_mass_message_process, AdminActions.mass_message_input)

    # Shaxsiy xabar yuborish
    dp.message.register(send_individual_message_start, F.text.in_(get_all_translations_for_key('send_individual_message')))
    dp.callback_query.register(individual_message_select_user_type, F.data.startswith('ind_msg_role|'), F.state == AdminActions.individual_message_select_type)
    dp.callback_query.register(individual_message_select_user, F.data.startswith('ind_msg_user|'), F.state == AdminActions.individual_message_select_user)
    dp.message.register(individual_message_send, AdminActions.individual_message_input)

    # Fikr-mulohazalarni ko'rish
    dp.message.register(view_feedback_start, F.text.in_(get_all_translations_for_key('view_feedback')))
    dp.callback_query.register(view_feedback_for_teacher, F.data.startswith('view_feedback_teacher|'), F.state == AdminActions.view_feedback_select_teacher)

    # Statistika
    dp.message.register(statistikani_korsatish, F.text.in_(get_all_translations_for_key('statistics')))

    logger.info("Admin handlers registered.")
