import os

# config.py
# Botning asosiy konfiguratsiya sozlamalari

# Bot tokeni muhit o'zgaruvchisidan olinadi
API_TOKEN = os.environ.get('API_TOKEN', 'YOUR_DEFAULT_TOKEN_IF_NOT_SET') # Default qiymatni o'zgartiring yoki o'chiring

# Ma'lumotlar bazasi fayli yo'li
# Renderda bot.db faylini loyiha papkasida saqlash tavsiya etiladi
DB_PATH = 'bot.db' # Yoki to'liq yo'l: '/opt/my_telegram_bot/bot.db'