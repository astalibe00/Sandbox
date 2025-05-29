# handlers/teacher.py
# Bu fayl o'qituvchi paneliga oid barcha funksiyalarni (handlerlar va FSM holatlari) o'z ichiga oladi.

import logging
import sqlite3
import calendar
from datetime import datetime

from aiogram import Dispatcher, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from translations import get_text
from utils.database import ( # YANGILANGAN QISM: get_teacher_average_rating va get_teacher_rating_count qo'shildi
    foydalanuvchini_id_bilan_olish, get_parent_of_student, get_missed_classes_in_month,
    get_teacher_average_rating, get_teacher_rating_count
)
from keyboards import (
    get_teacher_panel_keyboard, create_calendar_keyboard,
    get_attendance_status_keyboard, get_group_list_inline_keyboard,
    get_user_list_inline_keyboard
)

# Loglash sozlamalari
logger = logging.getLogger(__name__)

# Ma'lumotlar ombori yo'li (config.py dan olinadi)
# Eslatma: Bu yerda DB_PATH ni to'g'ridan-to'g'ri yozish o'rniga, config.py dan import qilish tavsiya etiladi.
# Hozircha, loyiha tuzilmasi bo'yicha DB_PATH ni shu yerda belgilaymiz.
DB_PATH = r'c:\Users\Asus\Desktop\bot\bot.db'

# ==============================================================================
# 1. FSM HOLATLARI (TEACHER ACTIONS)
# ==============================================================================
class DavomatBelgilash(StatesGroup):
    guruh_tanlash = State()
    talaba_tanlash = State()
    sana_tanlash = State()
    holat_tanlash = State()

class OqituvchiDavomatTarixi(StatesGroup):
    guruh_tanlash = State()
    talaba_tanlash = State()

class OqituvchiDarsJadvali(StatesGroup):
    guruh_tanlash = State()

# ==============================================================================
# 2. O'QITUVCHI PANELI VA ASOSIY BUYRUQLAR
# ==============================================================================
async def oqituvchi_paneli(message: types.Message, lang: str):
    """O'qituvchi paneli klaviaturasini ko'rsatadi."""
    await message.answer(get_text(lang, 'teacher_panel'), reply_markup=get_teacher_panel_keyboard(lang))
    logger.info(f"O'qituvchi paneli ochildi: user_id={message.from_user.id}, language={lang}")

# ==============================================================================
# 3. DAVOMAT BELGILASH HANDLERLARI
# ==============================================================================
async def davomat_belgilashni_boshlash(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Teacher':
        await message.answer(get_text(lang, 'not_authorized'))
        logger.warning(f"Davomat belgilash rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return
    
    now = datetime.now()
    keyboard = create_calendar_keyboard(now.year, now.month, lang)
    
    select_date_text = get_text(lang, 'select_attendance_date')
    await message.answer(select_date_text, reply_markup=keyboard)
    await state.set_state(DavomatBelgilash.sana_tanlash)
    logger.info(f"Davomat belgilash: sana tanlash boshlandi, user_id={message.from_user.id}, language={lang}")

async def process_calendar_selection(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    
    data = callback_query.data.split('|')
    action = data[0]

    if action == "cal_nav":
        year, month = map(int, data[1].split('-'))
        new_keyboard = create_calendar_keyboard(year, month, lang)
        await callback_query.message.edit_reply_markup(reply_markup=new_keyboard)
        logger.info(f"Kalendar navigatsiyasi: {year}-{month}, user_id={callback_query.from_user.id}")
    elif action == "cal_date":
        selected_date_str = data[1]
        await state.update_data(selected_date=selected_date_str)
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT group_name FROM groups WHERE teacher_id = ?", (callback_query.from_user.id,))
            guruhlar = c.fetchall()
            conn.close()
            if not guruhlar:
                await callback_query.message.answer(get_text(lang, 'no_groups_for_teacher'))
                logger.info(f"O'qituvchiga guruhlar topilmadi: user_id={callback_query.from_user.id}, language={lang}")
                await state.clear()
                return
            keyboard = get_group_list_inline_keyboard(guruhlar, "davomat_guruh")
            await callback_query.message.edit_text(get_text(lang, 'select_group'), reply_markup=keyboard)
            await state.set_state(DavomatBelgilash.guruh_tanlash)
            logger.info(f"Davomat belgilash: sana tanlandi ({selected_date_str}), guruh tanlashga o'tildi, user_id={callback_query.from_user.id}, language={lang}")
        except sqlite3.Error as e:
            await callback_query.message.answer(get_text(lang, 'db_error'))
            logger.error(f"Ma'lumotlar ombori xatosi (process_calendar_selection - guruhlar): {e}, user_id={callback_query.from_user.id}, language={lang}")
    elif action == "cal_today":
        today = datetime.now().strftime("%Y-%m-%d")
        await state.update_data(selected_date=today)
        
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT group_name FROM groups WHERE teacher_id = ?", (callback_query.from_user.id,))
            guruhlar = c.fetchall()
            conn.close()
            if not guruhlar:
                await callback_query.message.answer(get_text(lang, 'no_groups_for_teacher'))
                logger.info(f"O'qituvchiga guruhlar topilmadi: user_id={callback_query.from_user.id}, language={lang}")
                await state.clear()
                return
            keyboard = get_group_list_inline_keyboard(guruhlar, "davomat_guruh")
            await callback_query.message.edit_text(get_text(lang, 'select_group'), reply_markup=keyboard)
            await state.set_state(DavomatBelgilash.guruh_tanlash)
            logger.info(f"Davomat belgilash: bugungi sana tanlandi ({today}), guruh tanlashga o'tildi, user_id={callback_query.from_user.id}, language={lang}")
        except sqlite3.Error as e:
            await callback_query.message.answer(get_text(lang, 'db_error'))
            logger.error(f"Ma'lumotlar ombori xatosi (process_calendar_selection - today): {e}, user_id={callback_query.from_user.id}, language={lang}")
    elif action == "ignore":
        pass

async def davomat_guruh_tanlash(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    guruh_nomi = callback_query.data.split('|')[1]
    
    data = await state.get_data()
    selected_date = data.get('selected_date')
    if not selected_date:
        await callback_query.message.answer(get_text(lang, 'date_not_selected_error'))
        logger.error(f"Sana tanlanmadi: user_id={callback_query.from_user.id}, language={lang}")
        await state.clear()
        return

    await state.update_data(guruh_nomi=guruh_nomi)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT u.user_id, u.full_name, u.last_name
            FROM users u
            JOIN group_assignments ga ON u.user_id = ga.student_id
            WHERE ga.group_name = ? AND u.role = 'Student'
        """, (guruh_nomi,))
        talabalar = c.fetchall()
        conn.close()
        if not talabalar:
            await callback_query.message.answer(get_text(lang, 'no_students'))
            logger.info(f"Talabalar topilmadi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
            await state.clear()
            return
        
        users_data = [{'user_id': u[0], 'full_name': u[1], 'last_name': u[2]} for u in talabalar]
        keyboard = get_user_list_inline_keyboard(users_data, "davomat_talaba")
        await callback_query.message.edit_text(get_text(lang, 'select_student'), reply_markup=keyboard)
        await state.set_state(DavomatBelgilash.talaba_tanlash)
        logger.info(f"Talabalar ro'yxati ko'rsatildi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (davomat_guruh_tanlash): {e}, user_id={callback_query.from_user.id}, language={lang}")

async def davomat_holat_tanlash(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    student_id = callback_query.data.split('|')[1]
    await state.update_data(student_id=student_id)
    
    keyboard = get_attendance_status_keyboard(lang)
    select_attendance_text = get_text(lang, 'select_attendance_status')
    await callback_query.message.edit_text(select_attendance_text, reply_markup=keyboard)
    await state.set_state(DavomatBelgilash.holat_tanlash)
    logger.info(f"Davomat holati tanlash boshlandi: student_id={student_id}, user_id={callback_query.from_user.id}, language={lang}")

async def davomatni_saqlash(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    status = callback_query.data.split('|')[1]
    data = await state.get_data()
    student_id = int(data['student_id'])
    guruh_nomi = data['guruh_nomi']
    selected_date = data['selected_date']

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO attendance (student_id, group_name, date, status, comment) VALUES (?, ?, ?, ?, ?)",
                  (student_id, guruh_nomi, selected_date, status, ""))
        conn.commit()
        conn.close()
        
        await callback_query.message.answer(get_text(lang, 'attendance_marked').format(student_id=student_id, status=status))
        logger.info(f"Davomat belgilandi: student_id={student_id}, guruh_nomi={guruh_nomi}, sana={selected_date}, status={status}, user_id={callback_query.from_user.id}, language={lang}")

        parent_info = get_parent_of_student(student_id)
        if parent_info:
            parent_lang = parent_info['language']
            student_info = foydalanuvchini_id_bilan_olish(student_id)
            student_name = f"{student_info['full_name']} {student_info['last_name'] or ''}".strip() if student_info else f"ID: {student_id}"
            
            notification_text = get_text(parent_lang, f'attendance_notification_{status}').format(
                student_name=student_name,
                date=selected_date,
                group_name=guruh_nomi
            )
            await callback_query.bot.send_message(parent_info['user_id'], notification_text)
            logger.info(f"Ota-onaga davomat haqida xabar yuborildi: parent_id={parent_info['user_id']}, student_id={student_id}, status={status}, language={parent_lang}")

            if status == 'missed':
                current_year, current_month, _ = map(int, selected_date.split('-'))
                missed_count = get_missed_classes_in_month(student_id, current_year, current_month)
                if 3 <= missed_count <= 5:
                    warning_text = get_text(parent_lang, 'serious_warning_missed_classes').format(
                        student_name=student_name,
                        missed_count=missed_count,
                        month=current_month,
                        year=current_year
                    )
                    await callback_query.bot.send_message(parent_info['user_id'], warning_text)
                    logger.warning(f"Ota-onaga jiddiy ogohlantirish yuborildi: parent_id={parent_info['user_id']}, student_id={student_id}, missed_count={missed_count}")

    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (davomatni_saqlash): {e}, user_id={callback_query.from_user.id}, language={lang}")
    await state.clear()

# ==============================================================================
# 4. GURUH TALABALARINI KO'RISH HANDLERLARI
# ==============================================================================
async def guruh_talabalarini_korsatish(message: types.Message):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Teacher':
        await message.answer(get_text(lang, 'not_authorized'))
        logger.warning(f"Guruh talabalariga kirish rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups WHERE teacher_id = ?", (message.from_user.id,))
        guruhlar = c.fetchall()
        if not guruhlar:
            await message.answer(get_text(lang, 'no_groups_for_teacher'))
            logger.info(f"O'qituvchiga guruhlar topilmadi: user_id={message.from_user.id}, language={lang}")
            conn.close()
            return
        
        keyboard = get_group_list_inline_keyboard(guruhlar, "guruh_talabalari")
        await message.answer(get_text(lang, 'select_group'), reply_markup=keyboard)
        logger.info(f"Guruhlar ro'yxati ko'rsatildi: user_id={message.from_user.id}, guruhlar_soni={len(guruhlar)}, language={lang}")
        conn.close()
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (guruh_talabalarini_korsatish): {e}, user_id={message.from_user.id}, language={lang}")

async def guruh_talabalarini_korsatish_callback(callback_query: types.CallbackQuery):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    guruh_nomi = callback_query.data.split('|')[1]
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT u.user_id, u.full_name, u.last_name
            FROM users u
            JOIN group_assignments ga ON u.user_id = ga.student_id
            WHERE ga.group_name = ? AND u.role = 'Student'
        """, (guruh_nomi,))
        talabalar = c.fetchall()
        conn.close()
        if not talabalar:
            await callback_query.message.answer(get_text(lang, 'no_students'))
            logger.info(f"Talabalar topilmadi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
            return
        talabalar_royxati = get_text(lang, 'group_students_list').format(group_name=guruh_nomi)
        for talaba in talabalar:
            user_id, full_name, last_name = talaba
            name = f"{full_name} {last_name or ''}".strip()
            talabalar_royxati += f"ID: {user_id}, Ism: {name}\n"
        await callback_query.message.answer(talabalar_royxati)
        logger.info(f"Talabalar ro'yxati ko'rsatildi: guruh_nomi={guruh_nomi}, talabalar_soni={len(talabalar)}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (guruh_talabalarini_korsatish_callback): {e}, user_id={callback_query.from_user.id}, language={lang}")

# ==============================================================================
# 5. DARS JADVALINI KO'RISH HANDLERLARI (O'qituvchi uchun)
# ==============================================================================
async def dars_jadvalini_korsatish_oqituvchi(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Teacher':
        await message.answer(get_text(lang, 'not_authorized'))
        logger.warning(f"O'qituvchi dars jadvalini ko'rish rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups WHERE teacher_id = ?", (message.from_user.id,))
        guruhlar = c.fetchall()
        conn.close()
        if not guruhlar:
            await message.answer(get_text(lang, 'no_groups_for_teacher'))
            logger.info(f"O'qituvchiga guruhlar topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        
        keyboard = get_group_list_inline_keyboard(guruhlar, "teacher_schedule_group")
        await message.answer(get_text(lang, 'select_group_for_schedule'), reply_markup=keyboard)
        await state.set_state(OqituvchiDarsJadvali.guruh_tanlash)
        logger.info(f"O'qituvchi dars jadvalini ko'rish boshlandi: user_id={message.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (dars_jadvalini_korsatish_oqituvchi): {e}, user_id={message.from_user.id}, language={lang}")

async def teacher_schedule_group_selected(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    guruh_nomi = callback_query.data.split('|')[1]
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT class_times FROM groups WHERE group_name = ?", (guruh_nomi,))
        class_times = c.fetchone()
        conn.close()
        if not class_times or not class_times[0]:
            await callback_query.message.answer(get_text(lang, 'no_schedule'))
            logger.info(f"Dars jadvali topilmadi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
            return
        await callback_query.message.answer(get_text(lang, 'schedule_info').format(group_name=guruh_nomi, class_times=class_times[0]))
        logger.info(f"O'qituvchi uchun dars jadvali ko'rsatildi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (teacher_schedule_group_selected): {e}, user_id={callback_query.from_user.id}, language={lang}")
    await state.clear()

# ==============================================================================
# 6. TALABA DAVOMATINI KO'RISH HANDLERLARI (O'qituvchi uchun)
# ==============================================================================
async def davomat_tarixini_korsatish_oqituvchi(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Teacher':
        await message.answer(get_text(lang, 'not_authorized'))
        logger.warning(f"O'qituvchi talaba davomatini ko'rish rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups WHERE teacher_id = ?", (message.from_user.id,))
        guruhlar = c.fetchall()
        conn.close()
        if not guruhlar:
            await message.answer(get_text(lang, 'no_groups_for_teacher'))
            logger.info(f"O'qituvchiga guruhlar topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        
        keyboard = get_group_list_inline_keyboard(guruhlar, "teacher_att_group")
        await message.answer(get_text(lang, 'select_group'), reply_markup=keyboard)
        await state.set_state(OqituvchiDavomatTarixi.guruh_tanlash)
        logger.info(f"O'qituvchi talaba davomatini ko'rish boshlandi: user_id={message.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (davomat_tarixini_korsatish_oqituvchi): {e}, user_id={message.from_user.id}, language={lang}")

async def teacher_att_group_selected(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    guruh_nomi = callback_query.data.split('|')[1]
    await state.update_data(guruh_nomi=guruh_nomi)
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT u.user_id, u.full_name, u.last_name
            FROM users u
            JOIN group_assignments ga ON u.user_id = ga.student_id
            WHERE ga.group_name = ? AND u.role = 'Student'
        """, (guruh_nomi,))
        talabalar = c.fetchall()
        conn.close()
        if not talabalar:
            await callback_query.message.answer(get_text(lang, 'no_students'))
            logger.info(f"Talabalar topilmadi: guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
            await state.clear()
            return
        
        users_data = [{'user_id': u[0], 'full_name': u[1], 'last_name': u[2]} for u in talabalar]
        keyboard = get_user_list_inline_keyboard(users_data, "teacher_att_student")
        await callback_query.message.edit_text(get_text(lang, 'select_student'), reply_markup=keyboard)
        await state.set_state(OqituvchiDavomatTarixi.talaba_tanlash)
        logger.info(f"Talabalar ro'yxati ko'rsatildi (davomat uchun): guruh_nomi={guruh_nomi}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (teacher_att_group_selected): {e}, user_id={callback_query.from_user.id}, language={lang}")

async def teacher_att_student_selected(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.bot.answer_callback_query(callback_query.id)
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    student_id = int(callback_query.data.split('|')[1])
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT date, status, comment FROM attendance WHERE student_id = ? ORDER BY date DESC", (student_id,))
        records = c.fetchall()
        conn.close()
        if not records:
            await callback_query.message.answer(get_text(lang, 'no_attendance_history'))
            logger.info(f"Davomat tarixi topilmadi: student_id={student_id}, user_id={callback_query.from_user.id}, language={lang}")
            return
        student_info = foydalanuvchini_id_bilan_olish(student_id)
        student_name = f"{student_info['full_name']} {student_info['last_name'] or ''}".strip() if student_info else f"ID: {student_id}"
        history_text = get_text(lang, 'attendance_history_for_student').format(student_name=student_name)
        for record in records:
            date, status, comment = record
            comment_text = f"({comment})" if comment else ''
            history_text += get_text(lang, 'attendance_record').format(date=date, status=status, comment=comment_text)
        await callback_query.message.answer(history_text)
        logger.info(f"Davomat tarixi ko'rsatildi: student_id={student_id}, user_id={callback_query.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (teacher_att_student_selected): {e}, user_id={callback_query.from_user.id}, language={lang}")
    await state.clear()

# ==============================================================================
# 7. O'QITUVCHI SAMARADORLIGINI KO'RISH HANDLERLARI
# ==============================================================================
async def teacher_performance(message: types.Message):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Teacher':
        await message.answer(get_text(lang, 'not_authorized'))
        logger.warning(f"O'qituvchi samaradorligini ko'rish rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return

    teacher_id = message.from_user.id
    
    last_month_avg = get_teacher_average_rating(teacher_id, 'last_month')
    last_3_months_avg = get_teacher_average_rating(teacher_id, 'last_3_months')
    overall_avg = get_teacher_average_rating(teacher_id, 'all_time')
    rating_count = get_teacher_rating_count(teacher_id)

    def get_stars(rating):
        if rating == 0:
            return "⭐" * 0
        return "⭐" * int(round(rating))

    performance_text = get_text(lang, 'teacher_performance_title').format(teacher_name=f"{user['full_name']} {user['last_name'] or ''}".strip())
    performance_text += get_text(lang, 'last_month_rating').format(rating=f"{last_month_avg:.1f}/5" if last_month_avg else get_text(lang, 'not_rated'))
    performance_text += get_text(lang, 'last_3_months_rating').format(rating=f"{last_3_months_avg:.1f}/5" if last_3_months_avg else get_text(lang, 'not_rated'))
    performance_text += get_text(lang, 'overall_rating').format(rating=f"{overall_avg:.1f}/5 {get_stars(overall_avg)}" if overall_avg else get_text(lang, 'not_rated'))
    performance_text += get_text(lang, 'total_ratings_count').format(count=rating_count)

    if overall_avg >= 4.8:
        performance_text += get_text(lang, 'performance_excellent')
    elif overall_avg >= 4.0:
        performance_text += get_text(lang, 'performance_very_good')
    elif overall_avg >= 3.0:
        performance_text += get_text(lang, 'performance_good')
    elif overall_avg > 0:
        performance_text += get_text(lang, 'performance_needs_improvement')
    else:
        performance_text += get_text(lang, 'performance_no_data')

    await message.answer(performance_text)
    logger.info(f"O'qituvchi samaradorligi ko'rsatildi: user_id={teacher_id}, language={lang}")

# ==============================================================================
# 8. STATISTIKA HANDLERLARI (O'qituvchi uchun)
# ==============================================================================
async def statistikani_korsatish_oqituvchi(message: types.Message):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Teacher':
        await message.answer(get_text(lang, 'not_authorized'))
        logger.warning(f"Statistika ko'rish rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT group_name FROM groups WHERE teacher_id = ?", (user['user_id'],))
        guruhlar = c.fetchall()
        if not guruhlar:
            await message.answer(get_text(lang, 'no_groups_for_teacher'))
            logger.info(f"O'qituvchiga guruh tayinlanmagan: user_id={message.from_user.id}, language={lang}")
            conn.close()
            return
        
        group_names = [g[0] for g in guruhlar]
        placeholders = ','.join('?' for _ in group_names)
        query = f"""
            SELECT u.user_id, u.full_name, u.last_name, COUNT(a.student_id) as missed
            FROM users u
            LEFT JOIN attendance a ON u.user_id = a.student_id AND a.status = 'missed'
            JOIN group_assignments ga ON u.user_id = ga.student_id
            WHERE ga.group_name IN ({placeholders}) AND u.role = 'Student'
            GROUP BY u.user_id, u.full_name, u.last_name
        """
        c.execute(query, group_names)
        stats = c.fetchall()
        conn.close()
        if not stats:
            await message.answer(get_text(lang, 'no_students'))
            logger.info(f"Statistika uchun talabalar topilmadi: user_id={message.from_user.id}, language={lang}")
            return
        stats_text = get_text(lang, 'statistics_text', "Statistika:\n")
        for stat in stats:
            user_id, full_name, last_name, missed = stat
            name = f"{full_name} {last_name or ''}".strip()
            stats_text += f"{name} (ID: {user_id}): {missed} {get_text(lang, 'missed_classes', 'qoldirilgan darslar')}\n"
        await message.answer(stats_text)
        logger.info(f"Statistika ko'rsatildi: user_id={message.from_user.id}, stats_soni={len(stats)}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (statistikani_korsatish_oqituvchi): {e}, user_id={message.from_user.id}, language={lang}")


# ==============================================================================
# 9. HANDLERLARNI RO'YXATDAN O'TKAZISH FUNKSIYASI
#    Bu funksiya barcha o'qituvchi handlerlarini Dispatcherga qo'shadi.
# ==============================================================================
def register_teacher_handlers(dp: Dispatcher):
    # O'qituvchi paneli
    # Bu funksiya main.py dagi _show_control_panel dan chaqiriladi.
    # dp.message.register(oqituvchi_paneli, ...)

    # Davomat belgilash
    dp.message.register(davomat_belgilashni_boshlash, F.text.in_([get_text('uz', 'mark_attendance'), get_text('ru', 'mark_attendance'), get_text('en', 'mark_attendance')]))
    dp.callback_query.register(process_calendar_selection, F.data.startswith('cal_'), DavomatBelgilash.sana_tanlash)
    dp.callback_query.register(davomat_guruh_tanlash, F.data.startswith('davomat_guruh|'), DavomatBelgilash.guruh_tanlash)
    dp.callback_query.register(davomat_holat_tanlash, F.data.startswith('davomat_talaba|'))
    dp.callback_query.register(davomatni_saqlash, F.data.startswith('davomat_holat|'))

    # Guruh talabalari
    dp.message.register(guruh_talabalarini_korsatish, F.text.in_([get_text('uz', 'group_students'), get_text('ru', 'group_students'), get_text('en', 'group_students')]))
    dp.callback_query.register(guruh_talabalarini_korsatish_callback, F.data.startswith('guruh_talabalari|'))

    # Dars jadvalini ko'rish (O'qituvchi uchun)
    dp.message.register(dars_jadvalini_korsatish_oqituvchi, F.text.in_([get_text('uz', 'view_class_schedule'), get_text('ru', 'view_class_schedule'), get_text('en', 'view_class_schedule')]))
    dp.callback_query.register(teacher_schedule_group_selected, F.data.startswith('teacher_schedule_group|'), OqituvchiDarsJadvali.guruh_tanlash)

    # Talaba davomatini ko'rish (O'qituvchi uchun)
    dp.message.register(davomat_tarixini_korsatish_oqituvchi, F.text.in_([get_text('uz', 'view_student_attendance'), get_text('ru', 'view_student_attendance'), get_text('en', 'view_student_attendance')]))
    dp.callback_query.register(teacher_att_group_selected, F.data.startswith('teacher_att_group|'), OqituvchiDavomatTarixi.guruh_tanlash)
    dp.callback_query.register(teacher_att_student_selected, F.data.startswith('teacher_att_student|'), OqituvchiDavomatTarixi.talaba_tanlash)

    # O'qituvchi samaradorligi
    dp.message.register(teacher_performance, F.text.in_([get_text('uz', 'teacher_performance'), get_text('ru', 'teacher_performance'), get_text('en', 'teacher_performance')]))

    # Statistika (O'qituvchi uchun)
    dp.message.register(statistikani_korsatish_oqituvchi, F.text.in_([get_text('uz', 'statistics'), get_text('ru', 'statistics'), get_text('en', 'statistics')]))
