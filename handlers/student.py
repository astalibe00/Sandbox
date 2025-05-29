# handlers/student.py
# Bu fayl talaba paneli funksiyalari uchun handlerlarni o'z ichiga oladi.

import logging
import sqlite3 # Faqat to'g'ridan-to'g'ri DB_PATH dan foydalanish uchun
from datetime import datetime
from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from translations import get_text, get_all_translations_for_key
from keyboards import get_student_panel_keyboard # Talaba paneli klaviaturasini import qilish

# utils.database.py dan kerakli funksiyalarni import qilish
from utils.database import (
    foydalanuvchini_id_bilan_olish,
    DB_PATH, # DB_PATH ni utils.database dan import qilish
    create_calendar_keyboard, # utils.database dan import qilish
    get_missed_classes_in_month, # utils.database dan import qilish
    get_student_group_and_teacher_id, # utils.database dan import qilish
    save_student_feedback, # utils.database dan import qilish
    save_teacher_evaluation # utils.database dan import qilish
)

logger = logging.getLogger(__name__)

# ==============================================================================
# FSM Holatlari
# ==============================================================================

class StudentEvaluation(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    confirm_evaluation = State() # Yakuniy baholash holati

class StudentFeedback(StatesGroup):
    enter_feedback_text = State()

# ==============================================================================
# Talaba paneli funksiyalari
# ==============================================================================
async def talaba_paneli(message: types.Message, lang: str):
    """
    Talaba paneli klaviaturasini ko'rsatadi.
    Bu funksiya main.py dagi _show_control_panel funksiyasi tomonidan chaqiriladi.
    """
    await message.answer(get_text(lang, 'student_panel'), reply_markup=get_student_panel_keyboard(lang))
    logger.info(f"Talaba paneli ochildi: user_id={message.from_user.id}, language={lang}")

# ==============================================================================
# DARS JADVALINI KO'RISH HANDLERLARI (Talaba uchun)
# ==============================================================================
async def dars_jadvalini_korsatish(message: types.Message):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Student':
        await message.answer(get_text(lang, 'only_for_students'))
        logger.warning(f"Faqat talabalar uchun: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return
    
    if not user['group_name']:
        await message.answer(get_text(lang, 'no_group_assigned'))
        logger.info(f"Guruh tayinlanmagan: user_id={message.from_user.id}, language={lang}")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT class_times FROM groups WHERE group_name = ?", (user['group_name'],))
        class_times = c.fetchone()
        conn.close()
        if not class_times or not class_times[0]:
            await message.answer(get_text(lang, 'no_schedule'))
            logger.info(f"Dars jadvali topilmadi: guruh_nomi={user['group_name']}, user_id={message.from_user.id}, language={lang}")
            return
        await message.answer(get_text(lang, 'schedule_info').format(group_name=user['group_name'], class_times=class_times[0]))
        logger.info(f"Dars jadvali ko'rsatildi: guruh_nomi={user['group_name']}, user_id={message.from_user.id}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (dars_jadvalini_korsatish): {e}, user_id={message.from_user.id}, language={lang}")

# ==============================================================================
# DAVOMAT TARIXINI KO'RISH HANDLERLARI (Talaba uchun)
# ==============================================================================
async def davomat_tarixini_korsatish(message: types.Message):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Student': # Faqat talabalar uchun
        await message.answer(get_text(lang, 'only_for_students'))
        logger.warning(f"Faqat talabalar uchun: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        target_user_id = user['user_id'] # Talabaning o'z ID'si
        c.execute("SELECT date, status, comment FROM attendance WHERE student_id = ? ORDER BY date DESC", (target_user_id,))
        records = c.fetchall()
        conn.close()
        if not records:
            await message.answer(get_text(lang, 'no_attendance_history'))
            logger.info(f"Davomat tarixi topilmadi: user_id={target_user_id}, language={lang}")
            return
        history_text = get_text(lang, 'attendance_history_text')
        for record in records:
            date, status, comment = record
            comment_text = f"({comment})" if comment else ''
            history_text += get_text(lang, 'attendance_record').format(date=date, status=status, comment=comment_text)
        await message.answer(history_text)
        logger.info(f"Davomat tarixi ko'rsatildi: user_id={target_user_id}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (davomat_tarixini_korsatish): {e}, user_id={message.from_user.id}, language={lang}")

# ==============================================================================
# MENING MA'LUMOTLARIM HANDLERLARI
# ==============================================================================
async def my_info_korsatish(message: types.Message):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if not user:
        await message.answer(get_text(lang, 'not_logged_in'))
        logger.error(f"Foydalanuvchi topilmadi: user_id={message.from_user.id}, language={lang}")
        return

    info_text = get_text(lang, 'my_info_details').format(
        full_name=f"{user.get('full_name', '')} {user.get('last_name', '')}".strip(),
        login=user.get('login', get_text(lang, 'not_set')),
        phone=user.get('phone', get_text(lang, 'not_set')),
        role=user.get('role', get_text(lang, 'not_set')),
        group_name=user.get('group_name', get_text(lang, 'not_set')),
        tariff_plan=user.get('tariff_plan', get_text(lang, 'not_set')),
        tariff_price=user.get('tariff_price', get_text(lang, 'not_set')),
        debt_amount=user.get('debt_amount', 0),
        payment_status=user.get('payment_status', get_text(lang, 'not_set'))
    )
    await message.answer(info_text)
    logger.info(f"Mening ma'lumotlarim ko'rsatildi: user_id={message.from_user.id}, language={lang}")

# ==============================================================================
# O'QITUVCHINI BAHOLASH HANDLERLARI
# ==============================================================================
async def evaluate_teacher_start(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Student':
        await message.answer(get_text(lang, 'only_for_students'))
        logger.warning(f"O'qituvchini baholash rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return

    if not user['group_name']:
        await message.answer(get_text(lang, 'no_group_assigned_for_evaluation'))
        logger.info(f"Guruh tayinlanmagan (baholash uchun): user_id={message.from_user.id}, language={lang}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT teacher_id FROM groups WHERE group_name = ?", (user['group_name'],))
        teacher_id_result = c.fetchone()
        conn.close()

        if not teacher_id_result or not teacher_id_result[0]:
            await message.answer(get_text(lang, 'no_teacher_for_group'))
            logger.info(f"Guruhga o'qituvchi tayinlanmagan: group_name={user['group_name']}, user_id={message.from_user.id}, language={lang}")
            return
        
        teacher_id = teacher_id_result[0]
        teacher_info = foydalanuvchini_id_bilan_olish(teacher_id)
        if not teacher_info:
            await message.answer(get_text(lang, 'teacher_not_found_db'))
            logger.error(f"O'qituvchi topilmadi (DB): teacher_id={teacher_id}, user_id={message.from_user.id}, language={lang}")
            return

        await state.update_data(teacher_id_to_evaluate=teacher_id)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="1", callback_data="eval_rating_1"),
             InlineKeyboardButton(text="2", callback_data="eval_rating_2"),
             InlineKeyboardButton(text="3", callback_data="eval_rating_3"),
             InlineKeyboardButton(text="4", callback_data="eval_rating_4"),
             InlineKeyboardButton(text="5", callback_data="eval_rating_5")]
        ])
        await message.answer(get_text(lang, 'eval_q1'), reply_markup=keyboard)
        await state.set_state(StudentEvaluation.q1)
        logger.info(f"O'qituvchini baholash boshlandi: student_id={message.from_user.id}, teacher_id={teacher_id}, language={lang}")

    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (evaluate_teacher_start): {e}, user_id={message.from_user.id}, language={lang}")

async def evaluate_teacher_q1(callback_query: types.CallbackQuery, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    await callback_query.bot.answer_callback_query(callback_query.id, text=get_text(lang, 'rating_accepted'))
    rating = int(callback_query.data.split('_')[2])
    await state.update_data(q1_rating=rating)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="eval_rating_1"),
         InlineKeyboardButton(text="2", callback_data="eval_rating_2"),
         InlineKeyboardButton(text="3", callback_data="eval_rating_3"),
         InlineKeyboardButton(text="4", callback_data="eval_rating_4"),
         InlineKeyboardButton(text="5", callback_data="eval_rating_5")]
    ])
    await callback_query.message.edit_text(get_text(lang, 'eval_q2'), reply_markup=keyboard)
    await state.set_state(StudentEvaluation.q2)
    logger.info(f"1-savol baholandi: rating={rating}, user_id={callback_query.from_user.id}")

async def evaluate_teacher_q2(callback_query: types.CallbackQuery, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    await callback_query.bot.answer_callback_query(callback_query.id, text=get_text(lang, 'rating_accepted'))
    rating = int(callback_query.data.split('_')[2])
    await state.update_data(q2_rating=rating)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1", callback_data="eval_rating_1"),
         InlineKeyboardButton(text="2", callback_data="eval_rating_2"),
         InlineKeyboardButton(text="3", callback_data="eval_rating_3"),
         InlineKeyboardButton(text="4", callback_data="eval_rating_4"),
         InlineKeyboardButton(text="5", callback_data="eval_rating_5")]
    ])
    await callback_query.message.edit_text(get_text(lang, 'eval_q3'), reply_markup=keyboard)
    await state.set_state(StudentEvaluation.q3)
    logger.info(f"2-savol baholandi: rating={rating}, user_id={callback_query.from_user.id}")

async def evaluate_teacher_q3(callback_query: types.CallbackQuery, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language']
    await callback_query.bot.answer_callback_query(callback_query.id, text=get_text(lang, 'thank_you_for_rating'))
    rating = int(callback_query.data.split('_')[2])
    await state.update_data(q3_rating=rating)
    
    data = await state.get_data()
    teacher_id = data['teacher_id_to_evaluate']
    q1_rating = data['q1_rating']
    q2_rating = data['q2_rating']
    q3_rating = data['q3_rating']
    student_id = callback_query.from_user.id
    rating_date = datetime.now().strftime('%Y-%m-%d')

    try:
        save_teacher_evaluation(teacher_id, student_id, q1_rating, q2_rating, q3_rating, rating_date)
        await callback_query.message.answer(get_text(lang, 'evaluation_saved'), reply_markup=get_student_panel_keyboard(lang)) # Baholashdan keyin student panelga qaytarish
        logger.info(f"O'qituvchi baholandi va saqlandi: student_id={student_id}, teacher_id={teacher_id}, ratings={q1_rating, q2_rating, q3_rating}")
    except sqlite3.Error as e:
        await callback_query.message.answer(get_text(lang, 'db_error'), reply_markup=get_student_panel_keyboard(lang)) # Xato bo'lsa ham panelga qaytarish
        logger.error(f"Ma'lumotlar ombori xatosi (evaluate_teacher_q3): {e}, user_id={callback_query.from_user.id}")
    
    await state.clear()

# ==============================================================================
# FIKR QOLDIRISH HANDLERLARI
# ==============================================================================
async def leave_feedback_start(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    if user['role'] != 'Student':
        await message.answer(get_text(lang, 'only_for_students'))
        logger.warning(f"Fikr qoldirish rad etildi: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return

    if not user['group_name']:
        await message.answer(get_text(lang, 'no_group_assigned_for_feedback'))
        logger.info(f"Guruh tayinlanmagan (fikr uchun): user_id={message.from_user.id}, language={lang}")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT teacher_id FROM groups WHERE group_name = ?", (user['group_name'],))
        teacher_id_result = c.fetchone()
        conn.close()

        if not teacher_id_result or not teacher_id_result[0]:
            await message.answer(get_text(lang, 'no_teacher_for_group_feedback'))
            logger.info(f"Guruhga o'qituvchi tayinlanmagan (fikr uchun): group_name={user['group_name']}, user_id={message.from_user.id}, language={lang}")
            return
        
        teacher_id = teacher_id_result[0]
        await state.update_data(feedback_teacher_id=teacher_id)

        await message.answer(get_text(lang, 'enter_feedback_text'), reply_markup=ReplyKeyboardRemove())
        await state.set_state(StudentFeedback.enter_feedback_text)
        logger.info(f"Fikr qoldirish boshlandi: student_id={message.from_user.id}, teacher_id={teacher_id}, language={lang}")

    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'))
        logger.error(f"Ma'lumotlar ombori xatosi (leave_feedback_start): {e}, user_id={message.from_user.id}, language={lang}")

async def process_feedback_text(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language']
    feedback_text = message.text.strip()

    if not feedback_text:
        await message.answer(get_text(lang, 'feedback_empty'))
        logger.warning(f"Bo'sh fikr: user_id={message.from_user.id}, language={lang}")
        return

    data = await state.get_data()
    teacher_id = data['feedback_teacher_id']
    student_id = message.from_user.id
    feedback_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        save_student_feedback(teacher_id, student_id, feedback_text, feedback_date)
        await message.answer(get_text(lang, 'feedback_saved'), reply_markup=get_student_panel_keyboard(lang)) # Fikr saqlangandan keyin student panelga qaytarish
        logger.info(f"Fikr saqlandi: student_id={student_id}, teacher_id={teacher_id}, feedback_text={feedback_text}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'), reply_markup=get_student_panel_keyboard(lang)) # Xato bo'lsa ham panelga qaytarish
        logger.error(f"Ma'lumotlar ombori xatosi (process_feedback_text): {e}, user_id={message.from_user.id}")
    
    await state.clear()

# ==============================================================================
# HANDLERLARNI RO'YXATDAN O'TKAZISH FUNKSIYASI
#    Bu funksiya barcha talaba handlerlarini Dispatcherga qo'shadi.
# ==============================================================================
def register_student_handlers(dp: Dispatcher):
    # Dars jadvalini ko'rish
    dp.message.register(dars_jadvalini_korsatish, F.text.in_(get_all_translations_for_key('class_schedule')))

    # Davomat tarixini ko'rish
    dp.message.register(davomat_tarixini_korsatish, F.text.in_(get_all_translations_for_key('attendance_history')))

    # Mening ma'lumotlarim
    dp.message.register(my_info_korsatish, F.text.in_(get_all_translations_for_key('my_info')))

    # O'qituvchini baholash
    dp.message.register(evaluate_teacher_start, F.text.in_(get_all_translations_for_key('evaluate_teacher')))
    dp.callback_query.register(evaluate_teacher_q1, F.data.startswith('eval_rating_'), F.state == StudentEvaluation.q1)
    dp.callback_query.register(evaluate_teacher_q2, F.data.startswith('eval_rating_'), F.state == StudentEvaluation.q2)
    dp.callback_query.register(evaluate_teacher_q3, F.data.startswith('eval_rating_'), F.state == StudentEvaluation.q3)

    # Fikr qoldirish
    dp.message.register(leave_feedback_start, F.text.in_(get_all_translations_for_key('leave_feedback')))
    dp.message.register(process_feedback_text, StudentFeedback.enter_feedback_text)
    logger.info("Student handlers registered.")
