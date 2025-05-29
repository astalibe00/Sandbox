# handlers/common.py
# Bu fayl botning umumiy funksiyalari (ro'yxatdan o'tish, kirish, tilni o'zgartirish, parolni tiklash) uchun handlerlarni o'z ichiga oladi.

import logging
import asyncio # Asinxron kutish uchun import qilish kerak
from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot # Bot klassini import qilish kerak

from translations import get_text, get_all_translations_for_key
from utils.database import (
    foydalanuvchini_id_bilan_olish, foydalanuvchi_qoshish, hisob_malukmotlarini_yaratish,
    telefon_raqam_togrimi, foydalanuvchini_login_bilan_olish, foydalanuvchi_kirish_holatini_ornatish,
    login_togrimi, parol_togrimi, foydalanuvchini_telefon_va_login_bilan_olish,
    foydalanuvchi_parolini_yangilash, foydalanuvchi_tilini_yangilash
)

# Loglash sozlamalari
logging.basicConfig(level=logging.INFO, filename=r'c:\Users\Asus\Desktop\bot\bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==============================================================================
# FSM HOLATLARI (UMUMIY)
# ==============================================================================
class RoyxatdanOtish(StatesGroup):
    telefon = State()
    ism = State()
    familiya = State()

class Kirish(StatesGroup):
    login = State()
    parol = State()

class ParolTiklash(StatesGroup):
    telefon = State()
    login = State()
    tasdiqlash = State()
    yangi_parol = State()
    yangi_parolni_tasdiqlash = State()
    tasdiqlash_amali = State() # Holatni to'g'ri belgilash

# ==============================================================================
# ASOSIY BOT BUYRUQLARI VA HANDLERLARI (Dastlabki va umumiy handlerlar)
# ==============================================================================

# Bu funksiya main.py dan o'tkaziladi. Handlerlar ichida ishlatiladi.
_show_control_panel_func = None

def set_show_control_panel_func(func):
    """
    _show_control_panel_func ni tashqi funksiya bilan o'rnatadi.
    """
    global _show_control_panel_func
    _show_control_panel_func = func

async def cmd_start(message: types.Message, state: FSMContext):
    logger.info(f"/start buyrug'i qabul qilindi: user_id={message.from_user.id}")
    await state.clear()
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'

    if user and user.get('is_logged_in', 0):
        logger.info(f"Foydalanuvchi allaqachon tizimga kirgan, boshqaruv panelini ko'rsatish: user_id={message.from_user.id}")
        if _show_control_panel_func:
            await _show_control_panel_func(message, user)
        else:
            await message.answer(get_text(lang, 'welcome'), reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=get_text(lang, 'login'))],
                    [KeyboardButton(text=get_text(lang, 'reset_password'))],
                    [KeyboardButton(text=get_text(lang, 'change_language'))]
                ],
                resize_keyboard=True
            ))
        logger.info(f"Avtomatik kirish: user_id={message.from_user.id}, role={user['role']}, language={lang}")
        return

    if user:
        logger.info(f"Foydalanuvchi ro'yxatdan o'tgan, lekin kirmagan: user_id={message.from_user.id}")
        await message.answer(
            get_text(lang, 'already_registered').format(login=user['login'], role=user['role']),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=get_text(lang, 'login'))],
                    [KeyboardButton(text=get_text(lang, 'reset_password'))],
                    [KeyboardButton(text=get_text(lang, 'change_language'))]
                ],
                resize_keyboard=True
            )
        )
        logger.info(f"Kirish talab qilinadi: user_id={message.from_user.id}, login={user['login']}, role={user['role']}, language={lang}")
    else:
        logger.info(f"Yangi foydalanuvchi, /start buyrug'i: user_id={message.from_user.id}")
        await message.answer(
            get_text(lang, 'welcome'),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=get_text(lang, 'register'))],
                    [KeyboardButton(text=get_text(lang, 'login'))],
                    [KeyboardButton(text=get_text(lang, 'reset_password'))],
                    [KeyboardButton(text=get_text(lang, 'change_language'))]
                ],
                resize_keyboard=True
            )
        )
        logger.info(f"/start buyrugʻi: yangi foydalanuvchi, user_id={message.from_user.id}, language={lang}")

async def cmd_logout(message: types.Message, state: FSMContext):
    logger.info(f"Logout buyrug'i qabul qilindi: user_id={message.from_user.id}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = 'uz' # Default til
    if user:
        lang = user.get('language', 'uz') # Foydalanuvchi tilini olish

    # Xabarlarni o'chirish uchun saqlashni boshlash
    # Har doim foydalanuvchining buyrug'ini o'chirishga harakat qilamiz
    messages_to_delete_ids = [message.message_id]
    await state.update_data(messages_to_delete=messages_to_delete_ids)

    if user and user.get('is_logged_in', 0):
        logger.info(f"Foydalanuvchi tizimdan chiqmoqda: user_id={message.from_user.id}")
        foydalanuvchi_kirish_holatini_ornatish(message.from_user.id, 0) # is_logged_in ni 0 ga o'rnatish
        await state.clear() # FSM holatini tozalash

        sent_message = await message.answer(
            get_text(lang, 'logout_success'),
            reply_markup=ReplyKeyboardRemove()
        )
        # Bot yuborgan logout xabarini ham o'chirish uchun saqlash
        current_messages_after_send = (await state.get_data()).get('messages_to_delete', [])
        current_messages_after_send.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages_after_send)

        logger.info(f"Foydalanuvchi chiqdi va xabarlar o'chirilish uchun belgilandi: user_id={message.from_user.id}, language={lang}")
    else:
        logger.info(f"Chiqish rad etildi, foydalanuvchi kirmagan: user_id={message.from_user.id}, is_logged_in={user.get('is_logged_in', 0) if user else 'yoʻq'}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'not_logged_in'))
        current_messages_after_send = (await state.get_data()).get('messages_to_delete', [])
        current_messages_after_send.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages_after_send)
        logger.info(f"Foydalanuvchi kirmaganligi sababli 'not_logged_in' xabari yuborildi: user_id={message.from_user.id}")

    # Logout jarayoni tugagandan so'ng xabarlarni o'chirish
    chat_id = message.chat.id
    messages_to_delete_final = (await state.get_data()).get('messages_to_delete', [])
    await delete_messages_from_chat(message.bot, chat_id, messages_to_delete_final)
    logger.info(f"Logout jarayoni yakunlandi, xabarlar o'chirildi: user_id={message.from_user.id}")


async def cmd_stop(message: types.Message, state: FSMContext):
    logger.info(f"Stop buyrug'i qabul qilindi: user_id={message.from_user.id}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = 'uz' # Default til
    if user:
        lang = user.get('language', 'uz') # Foydalanuvchi tilini olish

    # Xabarlarni o'chirish uchun saqlashni boshlash
    messages_to_delete_ids = [message.message_id]
    await state.update_data(messages_to_delete=messages_to_delete_ids)

    if user and user.get('is_logged_in', 0):
        foydalanuvchi_kirish_holatini_ornatish(message.from_user.id, 0)
        logger.info(f"Foydalanuvchi kirish holati oʻchirildi: user_id={message.from_user.id}, language={lang}")
    
    await state.clear()
    
    sent_message = await message.answer(
        get_text(lang, 'stop_success'),
        reply_markup=ReplyKeyboardRemove()
    )
    # Bot yuborgan stop xabarini ham o'chirish uchun saqlash
    current_messages_after_send = (await state.get_data()).get('messages_to_delete', [])
    current_messages_after_send.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages_after_send)

    # Stop jarayoni tugagandan so'ng xabarlarni o'chirish
    chat_id = message.chat.id
    messages_to_delete_final = (await state.get_data()).get('messages_to_delete', [])
    await delete_messages_from_chat(message.bot, chat_id, messages_to_delete_final)

    logger.info(f"/stop buyrugʻi: jarayonlar toʻxtatildi va xabarlar o'chirildi, user_id={message.from_user.id}, language={lang}")


# Helper function to delete messages (already updated with 0.5s delay)
async def delete_messages_from_chat(bot_instance: Bot, chat_id: int, message_ids: list):
    for msg_id in message_ids:
        try:
            await asyncio.sleep(0.5) # 0.5 soniya kutish
            await bot_instance.delete_message(chat_id, msg_id)
        except Exception as e:
            logger.warning(f"Xabar o'chirishda xato: chat_id={chat_id}, message_id={msg_id}, error={e}")

# ==============================================================================
# RO'YXATDAN O'TISH HANDLERLARI
# ==============================================================================
async def cmd_register(message: types.Message, state: FSMContext):
    logger.info(f"Ro'yxatdan o'tish buyrug'i qabul qilindi: user_id={message.from_user.id}")
    await state.clear() # Oldingi holatlarni tozalash
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    if user:
        logger.info(f"Foydalanuvchi allaqachon ro'yxatdan o'tgan: user_id={message.from_user.id}")
        await message.answer(get_text(lang, 'already_registered').format(login=user['login'], role=user['role']), reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=get_text(lang, 'login'))],
                    [KeyboardButton(text=get_text(lang, 'reset_password'))],
                    [KeyboardButton(text=get_text(lang, 'change_language'))]
                ],
                resize_keyboard=True
            ))
        return
    
    # Xabarlarni o'chirish uchun saqlash
    await state.update_data(messages_to_delete=[message.message_id]) # Foydalanuvchi xabarini saqlash
    
    sent_message = await message.answer(get_text(lang, 'enter_phone_share_button'), reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=get_text(lang, 'share_phone'), request_contact=True)]],
        resize_keyboard=True
    ))
    # Bot xabarini saqlash
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)

    await state.set_state(RoyxatdanOtish.telefon)
    logger.info(f"Ro'yxatdan o'tish boshlandi: user_id={message.from_user.id}, language={lang}")

async def process_phone(message: types.Message, state: FSMContext):
    logger.info(f"Telefon raqamini qayta ishlash: user_id={message.from_user.id}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'

    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    if not message.contact: # Faqat kontakt orqali kelgan telefon raqamini qabul qilish
        logger.warning(f"Telefon raqami qo'lda kiritildi, tugma orqali so'raldi: user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'use_share_phone_button'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)
        return
    
    phone_number = message.contact.phone_number

    if not telefon_raqam_togrimi(phone_number):
        logger.warning(f"Noto'g'ri telefon raqami formati: {phone_number}, user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'invalid_phone'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)
        return
    
    await state.update_data(phone=phone_number)
    sent_message = await message.answer(get_text(lang, 'enter_first_name'), reply_markup=ReplyKeyboardRemove())
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)
    await state.set_state(RoyxatdanOtish.ism)
    logger.info(f"Telefon raqami qabul qilindi: {phone_number}, user_id={message.from_user.id}, language={lang}")

async def process_first_name(message: types.Message, state: FSMContext):
    logger.info(f"Ism qabul qilindi: user_id={message.from_user.id}, text={message.text}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    await state.update_data(full_name=message.text.strip())
    sent_message = await message.answer(get_text(lang, 'enter_last_name'))
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)
    await state.set_state(RoyxatdanOtish.familiya)
    logger.info(f"Ism qabul qilindi: {message.text}, user_id={message.from_user.id}, language={lang}")

async def process_last_name(message: types.Message, state: FSMContext):
    logger.info(f"Familiya qabul qilindi: user_id={message.from_user.id}, text={message.text}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    await state.update_data(last_name=message.text.strip())
    data = await state.get_data()

    login, password = hisob_malukmotlarini_yaratish()
    user_data = {
        'user_id': message.from_user.id,
        'phone': data['phone'],
        'login': login,
        'password': password,
        'role': 'pending', # Default rol
        'group_name': None,
        'full_name': data['full_name'],
        'last_name': data['last_name'],
        'child_id': None,
        'status': 'active',
        'language': lang # Foydalanuvchi tilini saqlash
    }
    foydalanuvchi_qoshish(user_data)

    # Generatsiya qilingan login va parolni yuborish (o'chirilmaydi)
    final_message_text = get_text(lang, 'registration_success_generated_credentials').format(
        login=f"||`{login}`||", # Monospaced va Hidden
        password=f"||`{password}`||" # Monospaced va Hidden
    )
    await message.answer(final_message_text, reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=get_text(lang, 'login'))]],
            resize_keyboard=True
        ))
    
    # Ro'yxatdan o'tish jarayoni tugagandan so'ng (login/parol xabaridan tashqari) xabarlarni o'chirish
    chat_id = message.chat.id
    messages_to_delete_ids = (await state.get_data()).get('messages_to_delete', [])
    await delete_messages_from_chat(message.bot, chat_id, messages_to_delete_ids)

    await state.clear()
    logger.info(f"Ro'yxatdan o'tish yakunlandi: user_id={message.from_user.id}, login={login}, language={lang}")

# ==============================================================================
# KIRISH HANDLERLARI
# ==============================================================================
async def cmd_login(message: types.Message, state: FSMContext):
    logger.info(f"Login buyrug'i qabul qilindi: user_id={message.from_user.id}")
    await state.clear() # Oldingi holatlarni tozalash
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    if user and user.get('is_logged_in', 0):
        logger.info(f"Foydalanuvchi allaqachon tizimga kirgan: user_id={message.from_user.id}")
        await message.answer(get_text(lang, 'already_logged_in'), reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=get_text(lang, 'login'))],
                [KeyboardButton(text=get_text(lang, 'reset_password'))],
                [KeyboardButton(text=get_text(lang, 'change_language'))]
                ],
                resize_keyboard=True
            ))
        return
    
    # Xabarlarni o'chirish uchun saqlash
    await state.update_data(messages_to_delete=[message.message_id]) # Foydalanuvchi xabarini saqlash

    sent_message = await message.answer(get_text(lang, 'enter_login'), reply_markup=ReplyKeyboardRemove())
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)

    await state.set_state(Kirish.login)
    logger.info(f"Kirish boshlandi: user_id={message.from_user.id}, language={lang}")

async def process_login_input(message: types.Message, state: FSMContext):
    logger.info(f"Login kiritildi: user_id={message.from_user.id}, text={message.text}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'

    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    if not login_togrimi(message.text):
        logger.warning(f"Noto'g'ri login formati: {message.text}, user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'invalid_login'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)
        return
    await state.update_data(login=message.text.strip())
    sent_message = await message.answer(get_text(lang, 'enter_password'))
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)
    await state.set_state(Kirish.parol)
    logger.info(f"Login qabul qilindi: {message.text}, user_id={message.from_user.id}, language={lang}")

async def process_password_input(message: types.Message, state: FSMContext):
    logger.info(f"Parol kiritildi: user_id={message.from_user.id}")
    user_data = await state.get_data()
    login = user_data['login']
    password = message.text.strip()
    
    user = foydalanuvchini_login_bilan_olish(login)
    lang = user['language'] if user else 'uz'

    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    if user and user['password'] == password:
        foydalanuvchi_kirish_holatini_ornatish(user['user_id'], 1)
        sent_message = await message.answer(get_text(lang, 'login_success').format(role=user['role']))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)

        # Kirish jarayoni tugagandan so'ng xabarlarni o'chirish
        chat_id = message.chat.id
        messages_to_delete_ids = (await state.get_data()).get('messages_to_delete', [])
        await delete_messages_from_chat(message.bot, chat_id, messages_to_delete_ids)

        if _show_control_panel_func:
            await _show_control_panel_func(message, user)
        else:
            await message.answer(get_text(lang, 'welcome'), reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=get_text(lang, 'login'))],
                    [KeyboardButton(text=get_text(lang, 'reset_password'))],
                    [KeyboardButton(text=get_text(lang, 'change_language'))]
                ],
                resize_keyboard=True
            ))
        logger.info(f"Kirish muvaffaqiyatli: user_id={user['user_id']}, role={user['role']}, language={lang}")
    else:
        logger.warning(f"Kirish muvaffaqiyatsiz: login={login}, user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'login_failed'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)
        
        # Kirish jarayoni tugagandan so'ng xabarlarni o'chirish (agar muvaffaqiyatsiz bo'lsa ham)
        chat_id = message.chat.id
        messages_to_delete_ids = (await state.get_data()).get('messages_to_delete', [])
        await delete_messages_from_chat(message.bot, chat_id, messages_to_delete_ids)

    await state.clear()

# ==============================================================================
# PAROLNI TIKLASH HANDLERLARI
# ==============================================================================
async def cmd_reset_password(message: types.Message, state: FSMContext):
    logger.info(f"Parolni tiklash buyrug'i qabul qilindi: user_id={message.from_user.id}")
    await state.clear() # Oldingi holatlarni tozalash
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    
    # Xabarlarni o'chirish uchun saqlash
    await state.update_data(messages_to_delete=[message.message_id]) # Foydalanuvchi xabarini saqlash

    sent_message = await message.answer(get_text(lang, 'enter_phone'), reply_markup=ReplyKeyboardRemove())
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)

    await state.set_state(ParolTiklash.telefon)
    logger.info(f"Parolni tiklash boshlandi: user_id={message.from_user.id}, language={lang}")

async def process_reset_phone(message: types.Message, state: FSMContext):
    logger.info(f"Parolni tiklash uchun telefon raqami kiritildi: user_id={message.from_user.id}, text={message.text}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    phone_number = message.text.strip()

    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    if not telefon_raqam_togrimi(phone_number):
        logger.warning(f"Parolni tiklashda noto'g'ri telefon raqami: {phone_number}, user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'invalid_phone'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)
        return
    await state.update_data(phone=phone_number)
    sent_message = await message.answer(get_text(lang, 'enter_login'))
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)
    await state.set_state(ParolTiklash.login)
    logger.info(f"Parolni tiklash uchun telefon qabul qilindi: {phone_number}, user_id={message.from_user.id}, language={lang}")

async def process_reset_login(message: types.Message, state: FSMContext):
    logger.info(f"Parolni tiklash uchun login kiritildi: user_id={message.from_user.id}, text={message.text}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    login = message.text.strip()

    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    if not login_togrimi(login):
        logger.warning(f"Parolni tiklashda noto'g'ri login: {login}, user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'invalid_login'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)
        return
    
    data = await state.get_data()
    phone = data['phone']
    
    user_to_reset = foydalanuvchini_telefon_va_login_bilan_olish(phone, login)
    if not user_to_reset:
        logger.warning(f"Parolni tiklash uchun foydalanuvchi topilmadi: phone={phone}, login={login}, user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'user_not_found'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)

        # Xabarlarni o'chirish
        chat_id = message.chat.id
        messages_to_delete_ids = (await state.get_data()).get('messages_to_delete', [])
        await delete_messages_from_chat(message.bot, chat_id, messages_to_delete_ids)

        await state.clear()
        return
    
    await state.update_data(user_id_to_reset=user_to_reset['user_id'])
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text(lang, 'confirm'), callback_data="confirm_yes")],
        [InlineKeyboardButton(text=get_text(lang, 'cancel'), callback_data="confirm_no")]
    ])
    sent_message = await message.answer(get_text(lang, 'confirm_reset'), reply_markup=confirm_keyboard)
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)

    await state.set_state(ParolTiklash.tasdiqlash_amali) # Holatni to'g'ri belgilash
    logger.info(f"Parolni tiklash tasdiqlash bosqichi: user_id={message.from_user.id}, language={lang}")

async def confirm_reset_password(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Parolni tiklash tasdiqlash callback_query: user_id={callback_query.from_user.id}, data={callback_query.data}")
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    lang = user['language'] if user else 'uz'
    await callback_query.bot.answer_callback_query(callback_query.id)

    current_messages = (await state.get_data()).get('messages_to_delete', [])
    # Inline keyboard xabari edit qilingani uchun, uning message_id sini saqlashimiz kerak.
    # Agar bu xabar o'chirilishi kerak bo'lsa, uni ham listga qo'shamiz.
    # Lekin edit_text ishlatilganligi sababli, bu message_id allaqachon listda bo'lishi kerak.
    # Agar callback_query.message.message_id listda bo'lmasa, qo'shamiz.
    if callback_query.message.message_id not in current_messages:
        current_messages.append(callback_query.message.message_id)
        await state.update_data(messages_to_delete=current_messages)

    if callback_query.data == 'confirm_yes':
        logger.info(f"Parolni tiklash tasdiqlandi: user_id={callback_query.from_user.id}, language={lang}")
        # edit_text yangi message_id qaytarmaydi, shuning uchun oldingi xabarni saqlashda davom etamiz.
        await callback_query.message.edit_text(get_text(lang, 'enter_new_password'))
        await state.set_state(ParolTiklash.yangi_parol)
    else:
        logger.info(f"Parolni tiklash bekor qilindi: user_id={callback_query.from_user.id}, language={lang}")
        await callback_query.message.edit_text(get_text(lang, 'password_reset_failed'))
        # Xabarlarni o'chirish
        chat_id = callback_query.message.chat.id
        messages_to_delete_ids = (await state.get_data()).get('messages_to_delete', [])
        await delete_messages_from_chat(callback_query.bot, chat_id, messages_to_delete_ids)
        
        await state.clear()

async def process_new_password(message: types.Message, state: FSMContext):
    logger.info(f"Yangi parol kiritildi: user_id={message.from_user.id}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    new_password = message.text.strip()

    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    if not parol_togrimi(new_password):
        logger.warning(f"Yangi parol formati noto'g'ri: user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'invalid_password'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)
        return
    await state.update_data(new_password=new_password)
    sent_message = await message.answer(get_text(lang, 'confirm_new_password'))
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)
    await state.set_state(ParolTiklash.yangi_parol_tasdiqlash)
    logger.info(f"Yangi parol qabul qilindi: user_id={message.from_user.id}, language={lang}")

async def confirm_new_password_input(message: types.Message, state: FSMContext):
    logger.info(f"Yangi parol tasdiqlandi: user_id={message.from_user.id}")
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    confirmed_password = message.text.strip()
    data = await state.get_data()
    new_password = data['new_password']
    user_id_to_reset = data['user_id_to_reset']

    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(message.message_id) # Foydalanuvchi xabarini saqlash
    await state.update_data(messages_to_delete=current_messages)

    if new_password == confirmed_password:
        if foydalanuvchi_parolini_yangilash(user_id_to_reset, new_password):
            sent_message = await message.answer(get_text(lang, 'password_reset_success'))
            current_messages = (await state.get_data()).get('messages_to_delete', [])
            current_messages.append(sent_message.message_id)
            await state.update_data(messages_to_delete=current_messages)
            logger.info(f"Parol muvaffaqiyatli tiklandi: user_id={user_id_to_reset}, language={lang}")
        else:
            logger.error(f"Parolni tiklashda DB xatosi: user_id={user_id_to_reset}, language={lang}")
            sent_message = await message.answer(get_text(lang, 'password_reset_failed'))
            current_messages = (await state.get_data()).get('messages_to_delete', [])
            current_messages.append(sent_message.message_id)
            await state.update_data(messages_to_delete=current_messages)
    else:
        logger.warning(f"Parollar mos kelmadi: user_id={message.from_user.id}, language={lang}")
        sent_message = await message.answer(get_text(lang, 'passwords_not_match'))
        current_messages = (await state.get_data()).get('messages_to_delete', [])
        current_messages.append(sent_message.message_id)
        await state.update_data(messages_to_delete=current_messages)
    
    # Parolni tiklash jarayoni tugagandan so'ng xabarlarni o'chirish
    chat_id = message.chat.id
    messages_to_delete_ids = (await state.get_data()).get('messages_to_delete', [])
    await delete_messages_from_chat(message.bot, chat_id, messages_to_delete_ids)

    await state.clear()

# ==============================================================================
# TILNI O'ZGARTIRISH HANDLERLARI
# ==============================================================================
async def cmd_change_language(message: types.Message, state: FSMContext):
    logger.info(f"Tilni o'zgartirish buyrug'i qabul qilindi: user_id={message.from_user.id}")
    await state.clear() # Oldingi holatlarni tozalash
    user = foydalanuvchini_id_bilan_olish(message.from_user.id)
    lang = user['language'] if user else 'uz'
    
    # Foydalanuvchi xabarini o'chirish uchun saqlash
    await state.update_data(messages_to_delete=[message.message_id])

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="O‘zbek", callback_data="lang_uz")],
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="English", callback_data="lang_en")]
    ])
    sent_message = await message.answer(get_text(lang, 'select_language'), reply_markup=keyboard)
    
    # Bot xabarini o'chirish uchun saqlash
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    current_messages.append(sent_message.message_id)
    await state.update_data(messages_to_delete=current_messages)

    logger.info(f"Tilni o'zgartirish so'raldi: user_id={message.from_user.id}, language={lang}")

async def process_language_selection(callback_query: types.CallbackQuery, state: FSMContext):
    logger.info(f"Til tanlovi callback_query: user_id={callback_query.from_user.id}, data={callback_query.data}")
    user = foydalanuvchini_id_bilan_olish(callback_query.from_user.id)
    old_lang = user['language'] if user else 'uz'
    await callback_query.bot.answer_callback_query(callback_query.id)
    new_lang = callback_query.data.split('_')[1]
    
    # Botning inline keyboard xabarini o'chirish uchun saqlash
    current_messages = (await state.get_data()).get('messages_to_delete', [])
    # Agar callback_query.message.message_id listda bo'lmasa, qo'shamiz.
    if callback_query.message.message_id not in current_messages:
        current_messages.append(callback_query.message.message_id)
        await state.update_data(messages_to_delete=current_messages)

    if foydalanuvchi_tilini_yangilash(callback_query.from_user.id, new_lang):
        # edit_text yangi message_id qaytarmaydi, shuning uchun bu yerda qo'shimcha saqlash shart emas.
        # Asosiy xabar allaqachon current_messages ichida.
        await callback_query.message.edit_text(get_text(new_lang, 'language_updated').format(lang=new_lang.upper()))
        logger.info(f"Til o'zgartirildi: user_id={callback_query.from_user.id}, old_lang={old_lang}, new_lang={new_lang}")
    else:
        logger.error(f"Tilni o'zgartirishda xato: user_id={callback_query.from_user.id}, language={old_lang}")
        await callback_query.message.edit_text(get_text(old_lang, 'db_error'))
    
    # Tilni o'zgartirish jarayoni tugagandan so'ng xabarlarni o'chirish
    chat_id = callback_query.message.chat.id
    messages_to_delete_ids = (await state.get_data()).get('messages_to_delete', [])
    await delete_messages_from_chat(callback_query.bot, chat_id, messages_to_delete_ids)

    await state.clear()

# ==============================================================================
# HANDLERLARNI RO'YXATDAN O'TKAZISH FUNKSIYASI
# ==============================================================================
def register_common_handlers(dp: Dispatcher):
    """
    Umumiy handlerlarni ro'yxatdan o'tkazadi.
    """
    dp.message.register(cmd_start, Command("start"))

    # Logout buyrug'i va tugmasi
    # Filtrlar alohida argumentlar sifatida uzatildi
    dp.message.register(cmd_logout, F.text.in_(get_all_translations_for_key('logout')), Command("logout"))

    # Stop buyrug'i
    # Filtrlar alohida argumentlar sifatida uzatildi
    dp.message.register(cmd_stop, F.text.in_(get_all_translations_for_key('stop')), Command("stop"))

    # Ro'yxatdan o'tish
    dp.message.register(cmd_register, F.text.in_(get_all_translations_for_key('register')))
    # Faqat F.contact orqali telefon raqamini qabul qilish
    dp.message.register(process_phone, F.contact, RoyxatdanOtish.telefon)
    # F.text orqali kelgan telefon raqamini rad etish
    dp.message.register(process_phone, F.text, RoyxatdanOtish.telefon) # Bu qator yuqoridagi F.contact dan keyin bo'lishi kerak
    dp.message.register(process_first_name, RoyxatdanOtish.ism)
    dp.message.register(process_last_name, RoyxatdanOtish.familiya)

    # Kirish
    dp.message.register(cmd_login, F.text.in_(get_all_translations_for_key('login')))
    dp.message.register(process_login_input, Kirish.login)
    dp.message.register(process_password_input, Kirish.parol)

    # Parolni tiklash
    dp.message.register(cmd_reset_password, F.text.in_(get_all_translations_for_key('reset_password')))
    dp.message.register(process_reset_phone, ParolTiklash.telefon)
    dp.message.register(process_reset_login, ParolTiklash.login)
    dp.callback_query.register(confirm_reset_password, F.data.startswith('confirm_'), F.state == ParolTiklash.tasdiqlash_amali)
    dp.message.register(process_new_password, ParolTiklash.yangi_parol)
    dp.message.register(confirm_new_password_input, ParolTiklash.yangi_parolni_tasdiqlash)

    # Tilni o'zgartirish
    dp.message.register(cmd_change_language, F.text.in_(get_all_translations_for_key('change_language')))
    dp.callback_query.register(process_language_selection, F.data.startswith('lang_'))

    logger.info("Common handlers registered.")
