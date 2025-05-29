# keyboards.py
# Bu fayl botning turli panellari va harakatlari uchun klaviaturalarni yaratadi.

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from translations import get_text, get_all_translations_for_key # get_all_translations_for_key import qilindi
import calendar
from datetime import datetime

# ==============================================================================
# 1. ASOSIY KLAVIATURALAR
# ==============================================================================

def get_initial_keyboard(lang: str, logged_in: bool = False) -> ReplyKeyboardMarkup:
    """
    Botning boshlang'ich klaviaturasini qaytaradi (ro'yxatdan o'tish/kirish/tilni o'zgartirish).
    Foydalanuvchi tizimga kirganligiga qarab tugmalarni o'zgartiradi.
    """
    builder = ReplyKeyboardBuilder()
    if not logged_in:
        builder.row(
            KeyboardButton(text=get_text(lang, 'register')),
            KeyboardButton(text=get_text(lang, 'login'))
        )
    else:
        # Tizimga kirgan foydalanuvchi uchun asosiy menyu tugmalari
        # Bu yerda foydalanuvchi rolini tekshirish kerak bo'lishi mumkin
        # Hozircha umumiy tugmalar
        builder.row(
            KeyboardButton(text=get_text(lang, 'my_info')),
            KeyboardButton(text=get_text(lang, 'class_schedule'))
        )
        builder.row(
            KeyboardButton(text=get_text(lang, 'logout')) # Agar logout tugmasi bo'lsa
        )

    builder.row(KeyboardButton(text=get_text(lang, 'change_language')))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

def get_share_phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """
    Telefon raqamini ulashish tugmasi bilan klaviaturani qaytaradi.
    """
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=get_text(lang, 'share_phone'), request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Tilni tanlash uchun inline klaviaturani qaytaradi.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇿 O'zbek", callback_data="lang_uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")
    )
    return builder.as_markup()

def get_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Tasdiqlash/Bekor qilish tugmalari bilan inline klaviaturani qaytaradi.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text(lang, 'confirm'), callback_data="confirm_yes"),
        InlineKeyboardButton(text=get_text(lang, 'cancel'), callback_data="confirm_no")
    )
    return builder.as_markup()

# ==============================================================================
# 2. ROLGA ASOSLANGAN PANELLAR KLAVIATURALARI
# ==============================================================================

def get_student_panel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """
    Talaba paneli klaviaturasini qaytaradi.
    """
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text(lang, 'class_schedule')),
        KeyboardButton(text=get_text(lang, 'attendance_history'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'my_info')),
        KeyboardButton(text=get_text(lang, 'evaluate_teacher')) # Yangi tugma
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'leave_feedback')) # Yangi tugma
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'change_language')),
        KeyboardButton(text=get_text(lang, 'logout'))
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

def get_parent_panel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """
    Ota-ona paneli klaviaturasini qaytaradi.
    """
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text(lang, 'child_info')),
        KeyboardButton(text=get_text(lang, 'attendance_history'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'leave_comment'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'change_language')),
        KeyboardButton(text=get_text(lang, 'logout'))
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

def get_teacher_panel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """
    O'qituvchi paneli klaviaturasini qaytaradi.
    """
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text(lang, 'mark_attendance')),
        KeyboardButton(text=get_text(lang, 'group_students'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'view_class_schedule')),
        KeyboardButton(text=get_text(lang, 'view_student_attendance'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'teacher_performance')), # Yangi tugma
        KeyboardButton(text=get_text(lang, 'statistics'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'change_language')),
        KeyboardButton(text=get_text(lang, 'logout'))
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

def get_super_admin_panel_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """
    Super Admin paneli klaviaturasini qaytaradi.
    """
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=get_text(lang, 'create_group')),
        KeyboardButton(text=get_text(lang, 'show_groups'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'assign_students_to_groups')),
        KeyboardButton(text=get_text(lang, 'assign_teachers_to_groups'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'assign_schedule')),
        KeyboardButton(text=get_text(lang, 'users'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'assign_roles')),
        KeyboardButton(text=get_text(lang, 'send_mass_message')) # Yangi tugma
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'send_individual_message')), # Yangi tugma
        KeyboardButton(text=get_text(lang, 'view_feedback')) # Yangi tugma
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'statistics')),
        KeyboardButton(text=get_text(lang, 'change_language'))
    )
    builder.row(
        KeyboardButton(text=get_text(lang, 'logout'))
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=False)

# ==============================================================================
# 3. YORDAMCHI INLINE KLAVIATURALAR
# ==============================================================================

def create_calendar_keyboard(year: int, month: int, lang: str) -> InlineKeyboardMarkup:
    """
    Berilgan oy va yil uchun kalendar inline klaviaturasini yaratadi.
    """
    builder = InlineKeyboardBuilder()
    
    # Oy va yil navigatsiyasi
    builder.row(
        InlineKeyboardButton(text="<", callback_data=f"cal_nav|{year}-{month-1 if month > 1 else year-1}-12"),
        InlineKeyboardButton(text=f"{calendar.month_name[month]} {year}", callback_data="cal_ignore"),
        InlineKeyboardButton(text=">", callback_data=f"cal_nav|{year}-{month+1 if month < 12 else year+1}-1")
    )

    # Haftaning kunlari
    week_days = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]
    builder.row(*[InlineKeyboardButton(text=day, callback_data="cal_ignore") for day in week_days])

    # Kunlar
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row_buttons = []
        for day in week:
            if day == 0:
                row_buttons.append(InlineKeyboardButton(text=" ", callback_data="cal_ignore"))
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                row_buttons.append(InlineKeyboardButton(text=str(day), callback_data=f"cal_date|{date_str}"))
        builder.row(*row_buttons)
    
    # "Bugun" tugmasi
    builder.row(InlineKeyboardButton(text=get_text(lang, 'today_button'), callback_data="cal_today"))
    
    return builder.as_markup()

def get_confirm_save_schedule_keyboard(lang: str, group_name: str, date: str) -> InlineKeyboardMarkup:
    """
    Dars jadvalini saqlashni tasdiqlash uchun inline klaviaturani qaytaradi.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text(lang, 'confirm_save_schedule_yes'), callback_data=f"djs_save:{group_name}|{date}"),
        InlineKeyboardButton(text=get_text(lang, 'confirm_save_schedule_no'), callback_data="djs_retry")
    )
    return builder.as_markup()

def get_group_list_inline_keyboard(groups: list, callback_prefix: str) -> InlineKeyboardMarkup:
    """
    Guruhlar ro'yxati uchun inline klaviaturani qaytaradi.
    """
    builder = InlineKeyboardBuilder()
    for group in groups:
        group_name = group[0] if isinstance(group, tuple) else group # Guruh nomi tuple ichida bo'lishi mumkin
        builder.row(InlineKeyboardButton(text=group_name, callback_data=f"{callback_prefix}|{group_name}"))
    builder.adjust(2) # Ikki ustunli tartib
    return builder.as_markup()

def get_user_list_inline_keyboard(users: list, callback_prefix: str) -> InlineKeyboardMarkup:
    """
    Foydalanuvchilar ro'yxati uchun inline klaviaturani qaytaradi.
    users listi dict yoki tuple bo'lishi mumkin: [{'user_id': ..., 'full_name': ..., 'last_name': ...}]
    yoki [(user_id, full_name, last_name), ...]
    """
    builder = InlineKeyboardBuilder()
    for user_data in users:
        user_id = user_data.get('user_id') if isinstance(user_data, dict) else user_data[0]
        full_name = user_data.get('full_name') if isinstance(user_data, dict) else user_data[1]
        last_name = user_data.get('last_name') if isinstance(user_data, dict) else user_data[2] if len(user_data) > 2 else ''
        
        display_name = f"{full_name} {last_name}".strip()
        if not display_name: # Agar ism va familiya bo'sh bo'lsa, IDni ko'rsatamiz
            display_name = f"ID: {user_id}"
        
        builder.row(InlineKeyboardButton(text=display_name, callback_data=f"{callback_prefix}|{user_id}"))
    builder.adjust(2)
    return builder.as_markup()

def get_user_type_for_message_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Xabar yuborish uchun foydalanuvchi turini tanlash klaviaturasini qaytaradi.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text(lang, 'student_role'), callback_data="ind_msg_role|Student"),
        InlineKeyboardButton(text=get_text(lang, 'parent_role'), callback_data="ind_msg_role|Parent")
    )
    builder.row(
        InlineKeyboardButton(text=get_text(lang, 'teacher_role'), callback_data="ind_msg_role|Teacher"),
        InlineKeyboardButton(text=get_text(lang, 'all_users'), callback_data="ind_msg_role|all")
    )
    return builder.as_markup()

def get_user_role_select_keyboard(lang: str) -> InlineKeyboardMarkup:
    """
    Foydalanuvchi rolini tanlash uchun inline klaviaturani qaytaradi.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text(lang, 'student_role'), callback_data="role_Student"),
        InlineKeyboardButton(text=get_text(lang, 'parent_role'), callback_data="role_Parent"),
        InlineKeyboardButton(text=get_text(lang, 'teacher_role'), callback_data="role_Teacher")
    )
    return builder.as_markup()

def get_teacher_evaluation_keyboard() -> InlineKeyboardMarkup:
    """
    O'qituvchini baholash uchun 1-5 gacha raqamli inline klaviaturani qaytaradi.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="1", callback_data="eval_rating_1"),
        InlineKeyboardButton(text="2", callback_data="eval_rating_2"),
        InlineKeyboardButton(text="3", callback_data="eval_rating_3"),
        InlineKeyboardButton(text="4", callback_data="eval_rating_4"),
        InlineKeyboardButton(text="5", callback_data="eval_rating_5")
    )
    return builder.as_markup()

def get_attendance_status_keyboard(lang: str, student_id: int, date: str) -> InlineKeyboardMarkup:
    """
    Davomat holatini belgilash uchun inline klaviaturani qaytaradi.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=get_text(lang, 'attended'), callback_data=f"att_status|{student_id}|{date}|attended"),
        InlineKeyboardButton(text=get_text(lang, 'missed'), callback_data=f"att_status|{student_id}|{date}|missed"),
        InlineKeyboardButton(text=get_text(lang, 'excused'), callback_data=f"att_status|{student_id}|{date}|excused")
    )
    return builder.as_markup()
