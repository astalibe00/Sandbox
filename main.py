# main.py
# Bu fayl botni ishga tushirish uchun asosiy kirish nuqtasi hisoblanadi.
# U Dispatcher va Bot ob'ektlarini sozlaydi, ma'lumotlar bazasini ishga tushiradi
# va barcha handler modullaridan handlerlarni ro'yxatdan o'tkazadi.

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Loyihaning boshqa qismlaridan importlar
# config.py dan API_TOKEN import qilish
from config import API_TOKEN

# utils/database.py dan kerakli funksiyalarni import qilish
from utils.database import initialize_db, foydalanuvchini_id_bilan_olish, foydalanuvchi_kirish_holatini_ornatish

# translations.py dan kerakli funksiyalarni import qilish
from translations import get_text, get_all_translations_for_key

# keyboards.py dan kerakli klaviatura funksiyalarini import qilish
from keyboards import (
    get_initial_keyboard, get_student_panel_keyboard, get_parent_panel_keyboard,
    get_teacher_panel_keyboard, get_super_admin_panel_keyboard
)

# Handler modullarini import qilish
from handlers.common import register_common_handlers, set_show_control_panel_func # set_show_control_panel_func import qilindi
from handlers.admin import register_admin_handlers, super_admin_paneli # super_admin_paneli ni ham import qilish
from handlers.student import register_student_handlers, talaba_paneli # talaba_paneli handlerini import qilish
from handlers.teacher import register_teacher_handlers, oqituvchi_paneli # oqituvchi_paneli handlerini import qilish
from handlers.parent import register_parent_handlers, ota_ona_paneli # ota_ona_paneli handlerini import qilish

# Loglash sozlamalari
logging.basicConfig(level=logging.INFO, filename=r'c:\Users\Asus\Desktop\bot\bot.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bot va Dispatcher ob'ektlari (main() funksiyasi ichida yaratiladi)
bot: Bot = None
dp: Dispatcher = None


# ==============================================================================
# YORDAMCHI FUNKSIYALAR
# ==============================================================================
async def _show_control_panel(message: types.Message, user):
    """
    Foydalanuvchi rolini tekshirib, tegishli panelni ko'rsatadi.
    Bu funksiya handlerlar ichida chaqiriladi.
    """
    lang = user.get('language', 'uz') # Foydalanuvchi tili topilmasa 'uz'
    role = user.get('role')

    if role == 'Student':
        await talaba_paneli(message, lang)
    elif role == 'Parent':
        await ota_ona_paneli(message, lang)
    elif role == 'Teacher':
        await oqituvchi_paneli(message, lang)
    elif role == 'super_admin':
        await super_admin_paneli(message, lang) # super_admin_paneli ni chaqirish
    else:
        await message.answer(get_text(lang, 'no_role', "Sizga hali rol berilmagan. Iltimos, kuting."), reply_markup=get_initial_keyboard(lang, logged_in=False))
    logger.info(f"Boshqaruv paneli ko'rsatildi: user_id={user['user_id']}, role={user['role']}, language={lang}")


# ==============================================================================
# BOTNI ISHGA TUSHIRISH
# ==============================================================================
async def main():
    global bot, dp # Global o'zgaruvchilarni ishlatish uchun

    # Bot tokenini config.py faylidan olamiz.
    # Agar config.py da API_TOKEN bo'sh bo'lsa, xato beradi.
    if not API_TOKEN:
        logger.error("Bot tokeni 'config.py' faylida aniqlanmagan. Iltimos, 'API_TOKEN' o'zgaruvchisini to'g'ri qiymat bilan to'ldiring.")
        exit(1)

    # Bot ob'ektini TOKEN aniqlangandan so'ng yaratamiz
    bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher(storage=MemoryStorage()) # Dispatcher ham bot bilan birga yaratiladi

    # Ma'lumotlar bazasini ishga tushirish
    initialize_db()
    logger.info("Ma'lumotlar bazasi ishga tushirildi.")

    # Handlerlarni ro'yxatdan o'tkazish
    # _show_control_panel funksiyasini common handlerlariga o'tkazamiz
    set_show_control_panel_func(_show_control_panel) # common.py ga funksiyani uzatish

    register_common_handlers(dp)
    register_admin_handlers(dp)
    register_student_handlers(dp)
    register_teacher_handlers(dp)
    register_parent_handlers(dp)

    logger.info("Bot ishga tushmoqda...")
    # Botni ishga tushirish
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
