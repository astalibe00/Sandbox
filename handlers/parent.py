# handlers/parent.py
# Bu fayl ota-ona paneli funksiyalari uchun handlerlarni o'z ichiga oladi.

import logging
import sqlite3
import calendar
from datetime import datetime
from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from translations import get_text, get_all_translations_for_key
from keyboards import get_parent_panel_keyboard # Ota-ona paneli klaviaturasini import qilish

# utils.database.py dan kerakli funksiyalarni import qilish
from utils.database import (
    foydalanuvchini_id_bilan_olish,
    DB_PATH,
    create_calendar_keyboard,
    get_missed_classes_in_month,
    get_student_group_and_teacher_id,
    get_student_attendance_records_for_month, # Bu funksiya ham kerak
    save_student_feedback
)

logger = logging.getLogger(__name__)

# ==============================================================================
# FSM Holatlari
# ==============================================================================
class ParentActions(StatesGroup):
    view_child_info_select_month = State() # Farzand davomatini ko'rish uchun oy tanlash
    enter_comment_text = State() # Izoh kiritish

# ==============================================================================
# Ota-ona paneli handlerlari
# ==============================================================================
async def ota_ona_paneli(message: types.Message, lang: str):
    """
    Ota-ona panelini ko'rsatadi.
    """
    await message.answer(get_text(lang, 'parent_panel'), reply_markup=get_parent_panel_keyboard(lang))
    logger.info(f"Ota-ona paneli ochildi: user_id={message.from_user.id}, language={lang}")

async def view_child_info_start(message: types.Message, state: FSMContext):
    """
    Farzand ma'lumotlarini ko'rish jarayonini boshlaydi.
    """
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'

    if not user or user['role'] != 'Parent':
        await message.answer(get_text(lang, 'not_authorized_parent'))
        logger.warning(f"Farzand ma'lumotlarini ko'rish rad etildi: user_id={message.from_user.id}, role={user['role'] if user else 'yoʻq'}, language={lang}")
        return

    child_id = user.get('child_id')
    if not child_id:
        await message.answer(get_text(lang, 'no_child_linked'))
        logger.info(f"Farzand biriktirilmagan: user_id={message.from_user.id}, language={lang}")
        return

    child_info = foydalanuvchini_id_bilan_olish(child_id)
    if not child_info:
        await message.answer(get_text(lang, 'child_not_found_db'))
        logger.error(f"Farzand ma'lumotlar bazasida topilmadi: child_id={child_id}, user_id={message.from_user.id}, language={lang}")
        return

    # Farzandning asosiy ma'lumotlarini ko'rsatish
    child_details_text = get_text(lang, 'child_details_title').format(
        child_name=f"{child_info.get('full_name', '')} {child_info.get('last_name', '')}".strip()
    )
    child_details_text += get_text(lang, 'child_details_info').format(
        login=child_info.get('login', get_text(lang, 'not_set')),
        group_name=child_info.get('group_name', get_text(lang, 'not_set')),
        tariff_plan=child_info.get('tariff_plan', get_text(lang, 'not_set')),
        tariff_price=child_info.get('tariff_price', get_text(lang, 'not_set')),
        debt_amount=child_info.get('debt_amount', 0),
        payment_status=child_info.get('payment_status', get_text(lang, 'not_set'))
    )
    await message.answer(child_details_text)

    # Davomat tarixini ko'rish uchun kalendarni ko'rsatish
    now = datetime.now()
    keyboard = create_calendar_keyboard(now.year, now.month, lang)
    await message.answer(get_text(lang, 'select_month_for_attendance_history'), reply_markup=keyboard)
    await state.update_data(child_id_for_attendance=child_id)
    await state.set_state(ParentActions.view_child_info_select_month)
    logger.info(f"Farzand ma'lumotlari ko'rsatildi, davomat uchun oy tanlash boshlandi: parent_id={message.from_user.id}, child_id={child_id}, language={lang}")

async def davomat_tarixini_korsatish_parent_panel(message: types.Message, state: FSMContext):
    """
    Ota-ona panelidan davomat tarixini ko'rishni boshlaydi.
    """
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'

    if not user or user['role'] != 'Parent':
        await message.answer(get_text(lang, 'not_authorized_parent'))
        logger.warning(f"Davomat tarixini ko'rish rad etildi (ota-ona): user_id={message.from_user.id}, role={user['role'] if user else 'yoʻq'}, language={lang}")
        return

    child_id = user.get('child_id')
    if not child_id:
        await message.answer(get_text(lang, 'no_child_linked'))
        logger.info(f"Davomat tarixini ko'rish uchun farzand biriktirilmagan: user_id={message.from_user.id}, language={lang}")
        return
    
    await state.update_data(child_id_for_attendance=child_id)
    now = datetime.now()
    keyboard = create_calendar_keyboard(now.year, now.month, lang)
    await message.answer(get_text(lang, 'select_month_for_attendance_history'), reply_markup=keyboard)
    await state.set_state(ParentActions.view_child_info_select_month)
    logger.info(f"Davomat tarixini ko'rish (ota-ona): oy tanlash boshlandi: parent_id={message.from_user.id}, child_id={child_id}, language={lang}")


async def process_child_attendance_calendar_selection(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Farzand davomatini ko'rish uchun kalendar navigatsiyasini va sana tanlashni boshqaradi.
    """
    await callback_query.answer()
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language'] if user else 'uz'
    
    data_from_state = await state.get_data()
    child_id = data_from_state.get('child_id_for_attendance')
    if not child_id:
        await callback_query.message.edit_text(get_text(lang, 'child_id_missing_error'))
        logger.error(f"Farzand ID si FSM kontekstida topilmadi: user_id={callback_query.from_user.id}, language={lang}")
        await state.clear()
        return

    data = callback_query.data.split('|')
    action = data[0]

    if action == "cal_nav":
        year, month = map(int, data[1].split('-'))
        new_keyboard = create_calendar_keyboard(year, month, lang)
        await callback_query.message.edit_reply_markup(reply_markup=new_keyboard)
        logger.info(f"Farzand davomati kalendar navigatsiyasi: {year}-{month}, parent_id={callback_query.from_user.id}, child_id={child_id}")
    elif action == "cal_date":
        selected_date_str = data[1] # YYYY-MM-DD
        year, month, day = map(int, selected_date_str.split('-'))
        
        await show_child_attendance_for_month(callback_query.message, child_id, year, month, lang)
        await state.clear() # Davomat ko'rsatilgandan so'ng holatni tozalash
        logger.info(f"Farzand davomati sanasi tanlandi ({selected_date_str}), davomat ko'rsatildi: parent_id={callback_query.from_user.id}, child_id={child_id}, language={lang}")
    elif action == "cal_today":
        today = datetime.now()
        await show_child_attendance_for_month(callback_query.message, child_id, today.year, today.month, lang)
        await state.clear() # Davomat ko'rsatilgandan so'ng holatni tozalash
        logger.info(f"Farzand davomati bugungi sana tanlandi, davomat ko'rsatildi: parent_id={callback_query.from_user.id}, child_id={child_id}, language={lang}")
    elif action == "ignore":
        pass # Ignore button clicks on month/day names or empty cells

async def show_child_attendance_for_month(message: types.Message, child_id: int, year: int, month: int, lang: str):
    """
    Farzandning berilgan oy uchun davomat tarixini ko'rsatadi.
    """
    child_info = foydalanuvchini_id_bilan_olish(child_id)
    child_name = f"{child_info.get('full_name', '')} {child_info.get('last_name', '')}".strip() if child_info else f"ID: {child_id}"
    
    attendance_records = get_student_attendance_records_for_month(child_id, year, month)
    missed_count = get_missed_classes_in_month(child_id, year, month)

    if not attendance_records:
        await message.edit_text(get_text(lang, 'no_attendance_history_for_month').format(child_name=child_name, month=month, year=year))
        logger.info(f"Farzand davomat tarixi topilmadi: child_id={child_id}, month={month}, year={year}, language={lang}")
        return

    history_text = get_text(lang, 'child_attendance_history_title').format(child_name=child_name, month=month, year=year)
    for record in attendance_records:
        date, status, comment = record
        comment_text = f"({comment})" if comment else ''
        history_text += get_text(lang, 'attendance_record').format(date=date, status=status, comment=comment_text)
    
    history_text += get_text(lang, 'total_missed_classes_month').format(missed_count=missed_count)

    await message.edit_text(history_text)
    logger.info(f"Farzand davomat tarixi ko'rsatildi: child_id={child_id}, month={month}, year={year}, language={lang}")


async def leave_comment_start(message: types.Message, state: FSMContext):
    """
    Ota-onaning izoh qoldirish jarayonini boshlaydi.
    """
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'

    if not user or user['role'] != 'Parent':
        await message.answer(get_text(lang, 'not_authorized_parent'))
        logger.warning(f"Izoh qoldirish rad etildi: user_id={message.from_user.id}, role={user['role'] if user else 'yoʻq'}, language={lang}")
        return
    
    child_id = user.get('child_id')
    if not child_id:
        await message.answer(get_text(lang, 'no_child_linked_for_comment'))
        logger.info(f"Izoh qoldirish uchun farzand biriktirilmagan: user_id={message.from_user.id}, language={lang}")
        return

    child_group_info = get_student_group_and_teacher_id(child_id)
    if not child_group_info or not child_group_info.get('teacher_id'):
        await message.answer(get_text(lang, 'no_teacher_for_child_group'))
        logger.info(f"Farzand guruhi uchun o'qituvchi topilmadi: child_id={child_id}, user_id={message.from_user.id}, language={lang}")
        return
    
    teacher_id = child_group_info['teacher_id']
    await state.update_data(parent_comment_child_id=child_id, parent_comment_teacher_id=teacher_id)

    await message.answer(get_text(lang, 'enter_parent_comment_text'), reply_markup=ReplyKeyboardRemove())
    await state.set_state(ParentActions.enter_comment_text)
    logger.info(f"Ota-ona izoh qoldirish boshlandi: parent_id={message.from_user.id}, child_id={child_id}, teacher_id={teacher_id}, language={lang}")

async def process_parent_comment_text(message: types.Message, state: FSMContext):
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    comment_text = message.text.strip()

    if not comment_text:
        await message.answer(get_text(lang, 'comment_empty'))
        logger.warning(f"Bo'sh izoh: user_id={message.from_user.id}, language={lang}")
        return

    data = await state.get_data()
    child_id = data.get('parent_comment_child_id')
    teacher_id = data.get('parent_comment_teacher_id')
    
    if not child_id or not teacher_id:
        await message.answer(get_text(lang, 'comment_save_error'))
        logger.error(f"Izohni saqlashda xato: child_id yoki teacher_id topilmadi. parent_id={message.from_user.id}, language={lang}")
        await state.clear()
        return

    feedback_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        save_student_feedback(teacher_id, child_id, comment_text, feedback_date)
        await message.answer(get_text(lang, 'parent_comment_saved'), reply_markup=get_parent_panel_keyboard(lang))
        logger.info(f"Ota-ona izohi saqlandi: parent_id={message.from_user.id}, child_id={child_id}, teacher_id={teacher_id}, comment_text={comment_text}, language={lang}")
    except sqlite3.Error as e:
        await message.answer(get_text(lang, 'db_error'), reply_markup=get_parent_panel_keyboard(lang))
        logger.error(f"Ma'lumotlar ombori xatosi (process_parent_comment_text): {e}, parent_id={message.from_user.id}, language={lang}")
    
    await state.clear()


# ==============================================================================
# Handlerlarni ro'yxatdan o'tkazish funksiyasi
# ==============================================================================
def register_parent_handlers(dp: Dispatcher):
    """
    Ota-ona paneli uchun handlerlarni ro'yxatdan o'tkazadi.
    """
    # F.text.in_() filtrlari ro'yxatga o'ralgan
    dp.message.register(view_child_info_start, F.text.in_(get_all_translations_for_key('child_info')))
    dp.message.register(davomat_tarixini_korsatish_parent_panel, F.text.in_(get_all_translations_for_key('attendance_history')))
    dp.message.register(leave_comment_start, F.text.in_(get_all_translations_for_key('leave_comment')))
    
    dp.callback_query.register(process_child_attendance_calendar_selection, F.data.startswith('cal_'), F.state == ParentActions.view_child_info_select_month)
    dp.message.register(process_parent_comment_text, ParentActions.enter_comment_text)

    logger.info("Parent handlers registered.")
