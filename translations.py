# translations.py
# Bu fayl botning turli xabarlari va tugmalari uchun o'zbekcha va ruscha tarjimalarni o'z ichiga oladi.
# Eslatma: Stikerlar (emojilar) matnlar ichiga qo'shildi.

translations = {
    'uz': {
        'welcome': "Assalomu alaykum! Botimizga xush kelibsiz! 👋",
        'register': "Ro'yxatdan o'tish 📝",
        'login': "Kirish 🚪",
        'reset_password': "Parolni tiklash 🔑",
        'change_language': "Tilni o'zgartirish 🌐",
        'select_language': "Tilni tanlang: 👇",
        'language_updated': "Til {lang} tiliga o'zgartirildi. ✅",
        'db_error': "Ma'lumotlar bazasida xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring. 🛠️",
        'already_registered': "Siz allaqachon ro'yxatdan o'tgansiz! Kirish ma'lumotlaringiz:\nLogin: `{login}`\nRol: `{role}`\n\nKirish uchun 'Kirish' tugmasini bosing.",
        'enter_phone': "Iltimos, telefon raqamingizni +998XXYYYYZZ formatida kiriting yoki 'Telefon raqamini ulashish' tugmasini bosing: 📞",
        'share_phone': "Telefon raqamini ulashish 📲",
        'invalid_phone': "Noto'g'ri telefon raqami formati. Iltimos, +998XXXXXXXXX formatida kiriting. ❌",
        'enter_first_name': "Ismingizni kiriting: �",
        'enter_last_name': "Familiyangizni kiriting: 👥",
        'registration_success': "Muvaffaqiyatli ro'yxatdan o'tdingiz! 🎉\nSizning login va parolingiz:\nLogin: `{login}`\nParol: `{password}`\n\nIltimos, ushbu ma'lumotlarni saqlab qoling. Kirish uchun 'Kirish' tugmasini bosing.",
        'enter_login': "Loginingizni kiriting: ✍️",
        'invalid_login': "Login kamida 3 ta belgidan iborat bo'lishi va faqat harf va raqamlardan tashkil topishi kerak. 🚫",
        'enter_password': "Parolingizni kiriting: 🔒",
        'login_success': "Muvaffaqiyatli kirdingiz! Sizning rolingiz: {role} ✅",
        'login_failed': "Login yoki parol noto'g'ri. Iltimos, qayta urinib ko'ring. ⚠️",
        'not_logged_in': "Siz tizimga kirmagansiz. Iltimos, /start buyrug'ini yuboring. ⛔",
        'logout_success': "Siz tizimdan chiqdingiz. Qayta kirish uchun /start buyrug'ini yuboring. 👋",
        'stop_success': "Barcha jarayonlar to'xtatildi. Qayta boshlash uchun /start buyrug'ini yuboring. 🛑",
        'enter_new_password': "Yangi parolni kiriting (kamida 6 belgi): 🆕🔑",
        'invalid_password': "Parol kamida 6 ta belgidan iborat bo'lishi kerak. ❌",
        'confirm_new_password': "Yangi parolni tasdiqlang: 🔁🔑",
        'passwords_not_match': "Parollar mos kelmadi. Iltimos, qaytadan kiriting. 🚫",
        'confirm_reset': "Parolni tiklashni tasdiqlaysizmi? 🤔",
        'confirm': "Tasdiqlash ✅",
        'cancel': "Bekor qilish ❌",
        'password_reset_success': "Parolingiz muvaffaqiyatli tiklandi. 🎉",
        'password_reset_failed': "Parolni tiklashda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring. 🛠️",
        'invalid_choice': "Noto'g'ri tanlov. Iltimos, tugmalardan birini bosing. 👆",
        'user_not_found': "Foydalanuvchi topilmadi. 🤷‍♂️",
        'not_super_admin': "Siz super admin emassiz. Bu funksiyadan foydalanishga ruxsatingiz yo'q. 🚫",
        'invalid_action': "Noto'g'ri amal. ⚠️",

        # Panellar
        'student_panel': "Talaba paneli 🎓",
        'parent_panel': "Ota-ona paneli 👨‍👩‍👧‍👦",
        'teacher_panel': "O'qituvchi paneli 🧑‍🏫",
        'super_admin_panel': "Super Admin paneli 👑",

        # Talaba paneli tugmalari
        'class_schedule': "Dars jadvali 🗓️",
        'attendance_history': "Davomat tarixi 📊",
        'my_info': "Mening ma'lumotlarim ℹ️",
        'evaluate_teacher': "Ustozni baholash ⭐",
        'leave_feedback': "Fikr qoldirish 💬",

        # Ota-ona paneli tugmalari
        'child_info': "Farzandim ma'lumotlari 👶",
        'leave_comment': "Izoh qoldirish ✍️",

        # O'qituvchi paneli tugmalari
        'mark_attendance': "Davomat belgilash ✅",
        'group_students': "Guruh talabalari 🧑‍🎓",
        'view_class_schedule': "Dars jadvalini ko'rish 📅",
        'view_student_attendance': "Talaba davomatini ko'rish 📈",
        'teacher_performance': "Samaradorlik 📊",
        'statistics': "Statistika 📈",

        # Super Admin paneli tugmalari
        'show_groups': "Guruhlar ro'yxati 📋",
        'create_group': "Guruh yaratish ➕",
        'assign_students_to_groups': "Talabalarni guruhlarga taqsimlash 🔄",
        'assign_teachers_to_groups': "O'qituvchilarni guruhlarga taqsimlash 🧑‍🏫",
        'assign_schedule': "Dars jadvalini belgilash 🗓️",
        'users': "Foydalanuvchilar 🧑‍💻",
        'assign_roles': "Rollarni belgilash 🏷️",
        'send_mass_message': "Ommaviy xabar yuborish 📢",
        'send_individual_message': "Shaxsiy xabar yuborish ✉️",
        'view_feedback': "Fikr-mulohazalarni ko'rish 👁️‍🗨️",

        # Guruh yaratish
        'enter_group_name': "Guruh nomini kiriting: ✍️",
        'invalid_group_name': "Guruh nomi bo'sh bo'lmasligi kerak. 🚫",
        'group_exists': "Bunday nomli guruh allaqachon mavjud. Boshqa nom tanlang. ⚠️",
        'enter_class_times': "Dars vaqtlarini kiriting (masalan: Dushanba, Chorshanba, Juma 14:00-16:00): ⏰",
        'group_created': "Guruh '{group_name}' muvaffaqiyatli yaratildi! 🎉",
        'group_created_with_teacher': "Guruh '{group_name}' muvaffaqiyatli yaratildi. Dars vaqtlari: {class_times}. O'qituvchi: {teacher}. ✅",
        'no_teacher': "Tayinlanmagan",
        'select_teacher': "O'qituvchini tanlang: 🧑‍🏫",
        'no_teachers': "Hozircha o'qituvchilar ro'yxati bo'sh. 🤷‍♀️",
        'teacher_assigned': "O'qituvchi {teacher_id} '{group_name}' guruhiga muvaffaqiyatli tayinlandi. ✅",

        # Talaba/O'qituvchi taqsimlash
        'select_group': "Guruhni tanlang: 👇",
        'no_groups': "Hozircha guruhlar ro'yxati bo'sh. 🤷‍♂️",
        'select_student': "Talabani tanlang: 👇",
        'no_students': "Hozircha talabalar ro'yxati bo'sh. 🤷‍♂️",
        'student_assigned': "Talaba {student_id} '{group_name}' guruhiga muvaffaqiyatli taqsimlandi. ✅",
        'group_details': "Guruh ma'lumotlari:\nNomi: {group_name}\nO'qituvchi: {teacher_info}\nDars vaqtlari: {class_times}\nTalabalar:\n{students}",
        'not_set': "Belgilanmagan",
        'group_students_list': "{group_name} guruhining talabalari:\n",

        # Rollarni belgilash
        'no_pending_users': "Hozircha 'pending' holatidagi foydalanuvchilar yo'q. ✅",
        'pending_users': "Kutayotgan foydalanuvchilar:\n",
        'pending_user_info': "ID: {id}, Login: {login}, Telefon: {phone}, Ism: {name}\n",
        'role_format': "Rolni belgilash uchun `login:rol` yoki `login:rol:tarif` formatida yuboring (masalan: `ali:Student:Elite` yoki `vali:Teacher`).\nMavjud rollar: Student, Parent, Teacher.\nMavjud tariflar: Elite (800000), Express (1600000).",
        'invalid_role': "Noto'g'ri rol. Mavjud rollar: {roles}. 🚫",
        'user_not_found_login': "Login `{login}` bilan foydalanuvchi topilmadi. 🤷‍♀️",
        'invalid_tariff': "Noto'g'ri tarif rejasi. Mavjud tariflar: Elite, Express. 🚫",
        'tariff_required_student_parent': "Talaba yoki Ota-ona roli uchun tarif rejasi majburiy. Iltimos, `login:rol:tarif` formatida kiriting. ⚠️",
        'role_assigned': "Foydalanuvchi `{login}`ga `{role}` roli va `{tariff}` tarifi ({price} so'm) muvaffaqiyatli berildi. ✅",
        'role_assigned_no_tariff': "Foydalanuvchi `{login}`ga `{role}` roli muvaffaqiyatli berildi. ✅",
        'enter_child_login': "Ota-onaga biriktiriladigan farzandning loginini kiriting: 👶",
        'student_not_found_for_parent': "Talaba `{login}` topilmadi yoki u 'Student' rolida emas. ❌",
        'parent_linked_to_student': "Ota-ona `{parent_login}` talaba `{student_login}`ga muvaffaqiyatli biriktirildi. ✅",

        # Dars jadvali (Talaba)
        'no_group_assigned': "Sizga hali guruh tayinlanmagan. Iltimos, admin bilan bog'laning. ⏳",
        'no_schedule': "Sizning guruhingiz uchun dars jadvali hali belgilanmagan. ⏳",
        'schedule_info': "{group_name} guruhining dars jadvali:\n{class_times} 🗓️",
        'only_for_students': "Bu funksiya faqat talabalar uchun mavjud. 🚫",

        # Dars jadvali (O'qituvchi)
        'not_authorized': "Sizda bu amalni bajarish uchun ruxsat yo'q. 🚫",
        'no_groups_for_teacher': "Sizga biriktirilgan guruhlar mavjud emas. 🤷‍♀️",
        'select_group_for_schedule': "Jadvalni ko'rish uchun guruhni tanlang: 👇",

        # Mening ma'lumotlarim
        'my_info_details': "Sizning ma'lumotlaringiz:\nIsm: {full_name}\nLogin: {login}\nTelefon: {phone}\nRol: {role}\nGuruh: {group_name}\nTarif reja: {tariff_plan}\nTarif narxi: {tariff_price} so'm\nQarz miqdori: {debt_amount} so'm\nTo'lov holati: {payment_status}",

        # Davomat tarixi (Talaba/Ota-ona)
        'no_attendance_history': "Davomat tarixi mavjud emas. 🤷‍♀️",
        'attendance_history_text': "Davomat tarixingiz:\n",
        'attendance_record': "- {date}: {status} {comment}\n",
        'attendance_notification_attended': "Hurmatli ota-ona, farzandingiz {student_name} ({date}) darsga qatnashdi. ✅",
        'attendance_notification_missed': "Hurmatli ota-ona, farzandingiz {student_name} ({date}) darsga qatnashmadi. ❌",
        'attendance_notification_excused': "Hurmatli ota-ona, farzandingiz {student_name} ({date}) darsda uzrli sabab bilan qatnashmadi. 📝",
        'serious_warning_missed_classes': "DIQQAT! Farzandingiz {student_name} {month}-oyida {missed_count} ta darsni qoldirdi. Iltimos, sababini aniqlang. ⚠️",

        # Davomat belgilash (O'qituvchi)
        'select_attendance_date': "Davomat belgilash uchun sanani tanlang: 🗓️",
        'today_button': "Bugun 🗓️",
        'date_not_selected_error': "Sana tanlanmadi. Iltimos, qaytadan urinib ko'ring. ❌",
        'attended': "Qatnashdi ✅",
        'missed': "Qatnashmadi ❌",
        'excused': "Uzrli sabab 📝",
        'select_attendance_status': "Davomat holatini tanlang: 👇",
        'attendance_marked': "Davomat {student_id} uchun '{status}' deb belgilandi. ✅",

        # Dars jadvalini belgilash (Super Admin)
        'enter_class_times_for_date': "{date} sanasi uchun dars vaqtlarini kiriting: ⏰",
        'class_times_empty': "Dars vaqtlari bo'sh bo'lmasligi kerak. 🚫",
        'confirm_schedule_text_with_date': "Guruh: {group_name}\nSana: {date}\nDars vaqtlari: {class_times}\n\nUshbu jadvalni saqlashni tasdiqlaysizmi?",
        'confirm_save_schedule_yes': "Ha, saqlash ✅",
        'confirm_save_schedule_no': "Yo'q, qayta kiritish 🔄",
        'schedule_assigned_confirmed': "Dars jadvali '{group_name}' uchun '{class_times}' deb muvaffaqiyatli belgilandi. 🎉",

        # Statistika
        'statistics_text': "Statistika:\n",
        'missed_classes': "qoldirilgan darslar",

        # Foydalanuvchilar (Super Admin)
        'all_users_list': "Barcha foydalanuvchilar:\n",
        'user_details': "ID: {id}, Ism: {name}, Login: {login}, Telefon: {phone}, Rol: {role}\n",
        'select_user_for_details': "Ma'lumotlarini ko'rish uchun foydalanuvchini tanlang: 👇",
        'select_user_for_role_change': "Rolini o'zgartirish uchun foydalanuvchini tanlang: 👇",
        'user_details_full': "Foydalanuvchi ma'lumotlari:\nID: {user_id}\nIsm: {full_name}\nFamiliya: {last_name}\nLogin: {login}\nTelefon: {phone}\nRol: {role}\nGuruh: {group_name}\nTarif: {tariff_plan} ({tariff_price} so'm)\nQarz: {debt_amount} so'm\nTo'lov holati: {payment_status}\nTil: {language}",
        'enter_new_role_for_user': "Foydalanuvchi `{login}` uchun yangi rolni kiriting (Student, Parent, Teacher) yoki `login:rol:tarif` formatida tarif bilan birga: ✍️",

        # O'qituvchi samaradorligi (Teacher Panel)
        'teacher_performance_title': "O'qituvchi {teacher_name} samaradorligi:\n",
        'last_month_rating': "So'nggi oy bahosi: {rating}\n",
        'last_3_months_rating': "Oxirgi 3 oy o'rtacha bahosi: {rating}\n",
        'overall_rating': "Umumiy reyting: {rating}\n",
        'total_ratings_count': "Jami baholagan talabalar soni: {count} ta\n",
        'not_rated': "Baholanmagan",
        'performance_excellent': "🏆 Sizning reytingingiz ajoyib! Davom eting!",
        'performance_very_good': "👍 Juda yaxshi natija! Kichik yaxshilanishlar bilan yanada yuqori cho'qqilarga erishishingiz mumkin.",
        'performance_good': "👌 Yaxshi natija. Ba'zi jihatlarni yaxshilashga e'tibor qarating.",
        'performance_needs_improvement': "💡 Samaradorlikni oshirish uchun qo'shimcha treninglar yoki maslahatlar kerak bo'lishi mumkin.",
        'performance_no_data': "Hozircha samaradorlik ma'lumotlari mavjud emas. Talabalar baholashini kuting.",
        
        'registration_success_generated_credentials': "Siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\nSizning login va parolingiz:\nLogin: {login}\nParol: {password}\n\nIltimos, ushbu ma'lumotlarni saqlab qo'ying. Keyingi safar kirish uchun ulardan foydalanasiz.",
        'enter_phone_share_button': "Iltimos, telefon raqamingizni 'Telefon raqami bilan bo'lishish' tugmasi orqali yuboring:",
        'use_share_phone_button': "Iltimos, telefon raqamingizni qo'lda kiritmang. Quyidagi 'Telefon raqami bilan bo'lishish' tugmasidan foydalaning.",

        # Talaba o'qituvchini baholash (Student Panel)
        'no_group_assigned_for_evaluation': "Sizga guruh tayinlanmagan, shuning uchun o'qituvchini baholay olmaysiz. 🤷‍♀️",
        'no_teacher_for_group': "Sizning guruhingizga o'qituvchi tayinlanmagan. 🤷‍♀️",
        'teacher_not_found_db': "O'qituvchi ma'lumotlar bazasida topilmadi. 🛠️",
        'eval_q1': "O‘qituvchi dars vaqtida sizni faol ishtirok etishga undaydimi?\n(1 – Umuman emas, 5 – Har doim faol ishtirok etaman)",
        'eval_q2': "Dars materiallari (mashqlar, topshiriqlar, matnlar) siz uchun qanchalik qiziqarli va foydali?\n(1 – Juda zerikarli, 5 – Juda qiziqarli va foydali)",
        'eval_q3': "Siz ushbu darslardan keyin o‘z bilimingiz oshayotganini his qilyapsizmi?\n(1 – Umuman emas, 5 – Ha, aniq rivojlanishni sezayapman)",
        'rating_accepted': "Qabul qilindi ✅",
        'thank_you_for_rating': "Rahmat, baholadingiz! 👍",
        'evaluation_saved': "Baholaringiz muvaffaqiyatli saqlandi. 🎉",

        # Ommaviy va shaxsiy xabar yuborish (Super Admin)
        'enter_mass_message': "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabarni kiriting: 📢",
        'message_empty': "Xabar matni bo'sh bo'lmasligi kerak. 🚫",
        'mass_message_sent_summary': "Ommaviy xabar yuborish yakunlandi.\nYuborildi: {sent} ta\nXatolik: {failed} ta",
        'message_from_admin': "Bu xabar admin tomonidan yuborildi.",
        'message_from_admin_individual': "Bu xabar admin tomonidan shaxsan sizga yuborildi.",
        'select_user_type_for_message': "Xabar yuborish uchun foydalanuvchi turini tanlang: 👇",
        'student_role': "Talaba 🧑‍🎓",
        'parent_role': "Ota-ona 👨‍👩‍👧‍👦",
        'teacher_role': "O'qituvchi 🧑‍🏫",
        'all_users': "Barcha foydalanuvchilar 🌐",
        'no_users_found_for_role': "'{role}' roli uchun foydalanuvchilar topilmadi. 🤷‍♀️",
        'select_user_to_message': "Xabar yuboriladigan foydalanuvchini tanlang: 👇",
        'enter_message_for_user': "{user_name}ga yubormoqchi bo'lgan xabarni kiriting: ✉️",
        'message_sent_success': "Xabar {user_name}ga muvaffaqiyatli yuborildi. ✅",
        'message_sent_failed': "Xabar {user_name}ga yuborishda xatolik yuz berdi. ❌",

        # Talaba fikr qoldirish (Student Panel)
        'no_group_assigned_for_feedback': "Sizga guruh tayinlanmagan, shuning uchun fikr qoldira olmaysiz. 🤷‍♀️",
        'no_teacher_for_group_feedback': "Sizning guruhingizga o'qituvchi tayinlanmagan, shuning uchun fikr qoldira olmaysiz. 🤷‍♀️",
        'enter_feedback_text': "Anonim fikringizni kiriting: 💬",
        'feedback_empty': "Fikr matni bo'sh bo'lmasligi kerak. 🚫",
        'feedback_saved': "Fikringiz muvaffaqiyatli saqlandi. Rahmat! 🙏",

        # Fikrlar bazasini ko'rish (Super Admin)
        'no_teachers_for_feedback_view': "Fikrlar bazasini ko'rish uchun o'qituvchilar topilmadi. 🤷‍♀️",
        'select_teacher_for_feedback_view': "Fikr-mulohazalarni ko'rish uchun o'qituvchini tanlang: 👇",
        'no_feedback_for_teacher': "{teacher_name} uchun hali hech qanday fikr-mulohaza mavjud emas. 🤷‍♀️",
        'feedback_list_for_teacher': "{teacher_name} uchun fikr-mulohazalar:\n",
        'feedback_entry': "📅 {date}\n💬 {feedback}\n\n",
    },
    'ru': {
        'welcome': "Здравствуйте! Добро пожаловать в наш бот! 👋",
        'register': "Зарегистрироваться 📝",
        'login': "Войти 🚪",
        'reset_password': "Сбросить пароль 🔑",
        'change_language': "Изменить язык 🌐",
        'select_language': "Выберите язык: 👇",
        'language_updated': "Язык изменен на {lang}. ✅",
        'db_error': "Произошла ошибка в базе данных. Пожалуйста, попробуйте позже. 🛠️",
        'already_registered': "Вы уже зарегистрированы! Ваши данные для входа:\nЛогин: `{login}`\nРоль: `{role}`\n\nНажмите 'Войти', чтобы войти.",
        'enter_phone': "Пожалуйста, введите ваш номер телефона в формате +998XXYYYYZZ или нажмите кнопку 'Поделиться номером телефона': 📞",
        'share_phone': "Поделиться номером телефона 📲",
        'invalid_phone': "Неверный формат номера телефона. Пожалуйста, введите в формате +998XXXXXXXXX. ❌",
        'enter_first_name': "Введите ваше имя: 👤",
        'enter_last_name': "Введите вашу фамилию: 👥",
        'registration_success': "Вы успешно зарегистрировались! 🎉\nВаш логин и пароль:\nЛогин: `{login}`\nПароль: `{password}`\n\nПожалуйста, сохраните эти данные. Нажмите 'Войти', чтобы войти.",
        'enter_login': "Введите ваш логин: ✍️",
        'invalid_login': "Логин должен содержать не менее 3 символов и состоять только из букв и цифр. 🚫",
        'enter_password': "Введите ваш пароль: 🔒",
        'login_success': "Вы успешно вошли! Ваша роль: {role} ✅",
        'login_failed': "Неверный логин или пароль. Пожалуйста, попробуйте еще раз. ⚠️",
        'not_logged_in': "Вы не вошли в систему. Пожалуйста, отправьте команду /start. ⛔",
        'logout_success': "Вы вышли из системы. Отправьте команду /start, чтобы войти снова. 👋",
        'stop_success': "Все процессы остановлены. Отправьте команду /start, чтобы начать снова. 🛑",
        'enter_new_password': "Введите новый пароль (минимум 6 символов): 🆕🔑",
        'invalid_password': "Пароль должен содержать не менее 6 символов. ❌",
        'confirm_new_password': "Подтвердите новый пароль: 🔁🔑",
        'passwords_not_match': "Пароли не совпадают. Пожалуйста, введите еще раз. 🚫",
        'confirm_reset': "Подтверждаете сброс пароля? 🤔",
        'confirm': "Подтвердить ✅",
        'cancel': "Отмена ❌",
        'password_reset_success': "Ваш пароль успешно сброшен. 🎉",
        'password_reset_failed': "Произошла ошибка при сбросе пароля. Пожалуйста, попробуйте позже. 🛠️",
        'invalid_choice': "Неверный выбор. Пожалуйста, нажмите одну из кнопок. 👆",
        'user_not_found': "Пользователь не найден. 🤷‍♂️",
        'not_super_admin': "Вы не являетесь супер-админом. У вас нет разрешения на использование этой функции. 🚫",
        'invalid_action': "Неверное действие. ⚠️",

        # Панели
        'student_panel': "Панель студента 🎓",
        'parent_panel': "Панель родителя 👨‍👩‍👧‍👦",
        'teacher_panel': "Панель учителя 🧑‍🏫",
        'super_admin_panel': "Панель супер-админа 👑",

        # Кнопки панели студента
        'class_schedule': "Расписание занятий 🗓️",
        'attendance_history': "История посещаемости 📊",
        'my_info': "Моя информация ℹ️",
        'evaluate_teacher': "Оценить учителя ⭐",
        'leave_feedback': "Оставить отзыв 💬",

        # Кнопки панели родителя
        'child_info': "Информация о ребенке 👶",
        'leave_comment': "Оставить комментарий ✍️",

        # Кнопки панели учителя
        'mark_attendance': "Отметить посещаемость ✅",
        'group_students': "Студенты группы 🧑‍🎓",
        'view_class_schedule': "Посмотреть расписание занятий 📅",
        'view_student_attendance': "Посмотреть посещаемость студента 📈",
        'teacher_performance': "Эффективность 📊",
        'statistics': "Статистика 📈",

        # Кнопки панели супер-админа
        'show_groups': "Список групп 📋",
        'create_group': "Создать группу ➕",
        'assign_students_to_groups': "Назначить студентов в группы 🔄",
        'assign_teachers_to_groups': "Назначить учителей в группы 🧑‍🏫",
        'assign_schedule': "Назначить расписание 🗓️",
        'users': "Пользователи 🧑‍💻",
        'assign_roles': "Назначить роли 🏷️",
        'send_mass_message': "Отправить массовое сообщение 📢",
        'send_individual_message': "Отправить личное сообщение ✉️",
        'view_feedback': "Просмотреть отзывы 👁️‍🗨️",

        # Создание группы
        'enter_group_name': "Введите название группы: ✍️",
        'invalid_group_name': "Название группы не может быть пустым. 🚫",
        'group_exists': "Группа с таким названием уже существует. Выберите другое название. ⚠️",
        'enter_class_times': "Введите время занятий (например: Понедельник, Среда, Пятница 14:00-16:00): ⏰",
        'group_created': "Группа '{group_name}' успешно создана! 🎉",
        'group_created_with_teacher': "Группа '{group_name}' успешно создана. Время занятий: {class_times}. Учитель: {teacher}. ✅",
        'no_teacher': "Не назначен",
        'select_teacher': "Выберите учителя: 🧑‍🏫",
        'no_teachers': "Список учителей пока пуст. 🤷‍♀️",
        'teacher_assigned': "Учитель {teacher_id} успешно назначен в группу '{group_name}'. ✅",
        

        # Назначение студента/учителя
        'select_group': "Выберите группу: 👇",
        'no_groups': "Список групп пока пуст. 🤷‍♂️",
        'select_student': "Выберите студента: 👇",
        'no_students': "Список студентов пока пуст. 🤷‍♂️",
        'student_assigned': "Студент {student_id} успешно назначен в группу '{group_name}'. ✅",
        'group_details': "Информация о группе:\nНазвание: {group_name}\nУчитель: {teacher_info}\nВремя занятий: {class_times}\nСтуденты:\n{students}",
        'not_set': "Не установлено",
        'group_students_list': "Студенты группы {group_name}:\n",

        # Назначение ролей
        'no_pending_users': "Пользователей в статусе 'pending' пока нет. ✅",
        'pending_users': "Ожидающие пользователи:\n",
        'pending_user_info': "ID: {id}, Логин: {login}, Телефон: {phone}, Имя: {name}\n",
        'role_format': "Для назначения роли отправьте в формате `логин:роль` или `логин:роль:тариф` (например: `ali:Student:Elite` или `vali:Teacher`).\nДоступные роли: Student, Parent, Teacher.\nДоступные тарифы: Elite (800000), Express (1600000).",
        'invalid_role': "Неверная роль. Доступные роли: {roles}. 🚫",
        'user_not_found_login': "Пользователь с логином `{login}` не найден. 🤷‍♀️",
        'invalid_tariff': "Неверный тарифный план. Доступные тарифы: Elite, Express. 🚫",
        'tariff_required_student_parent': "Для роли студента или родителя тарифный план обязателен. Пожалуйста, введите в формате `логин:роль:тариф`. ⚠️",
        'role_assigned': "Пользователю `{login}` успешно назначена роль `{role}` и тариф `{tariff}` ({price} сум). ✅",
        'role_assigned_no_tariff': "Пользователю `{login}` успешно назначена роль `{role}`. ✅",
        'enter_child_login': "Введите логин ребенка, которого нужно привязать к родителю: 👶",
        'student_not_found_for_parent': "Студент `{login}` не найден или не имеет роли 'Student'. ❌",
        'parent_linked_to_student': "Родитель `{parent_login}` успешно привязан к студенту `{student_login}`. ✅",

        # Расписание занятий (Студент)
        'no_group_assigned': "Вам еще не назначена группа. Пожалуйста, свяжитесь с администратором. ⏳",
        'no_schedule': "Расписание занятий для вашей группы еще не установлено. ⏳",
        'schedule_info': "Расписание занятий для группы {group_name}:\n{class_times} 🗓️",
        'only_for_students': "Эта функция доступна только для студентов. 🚫",

        # Расписание занятий (Учитель)
        'not_authorized': "У вас нет разрешения на выполнение этого действия. 🚫",
        'no_groups_for_teacher': "У вас нет назначенных групп. 🤷‍♀️",
        'select_group_for_schedule': "Выберите группу для просмотра расписания: 👇",

        # Моя информация
        'my_info_details': "Ваша информация:\nИмя: {full_name}\nЛогин: {login}\nТелефон: {phone}\nРоль: {role}\nГруппа: {group_name}\nТарифный план: {tariff_plan}\nСтоимость тарифа: {tariff_price} сум\nСумма долга: {debt_amount} сум\nСтатус оплаты: {payment_status}",

        # История посещаемости (Студент/Родитель)
        'no_attendance_history': "История посещаемости отсутствует. 🤷‍♀️",
        'attendance_history_text': "Ваша история посещаемости:\n",
        'attendance_record': "- {date}: {status} {comment}\n",
        'attendance_notification_attended': "Уважаемый родитель, ваш ребенок {student_name} ({date}) посетил занятие. ✅",
        'attendance_notification_missed': "Уважаемый родитель, ваш ребенок {student_name} ({date}) пропустил занятие. ❌",
        'attendance_notification_excused': "Уважаемый родитель, ваш ребенок {student_name} ({date}) пропустил занятие по уважительной причине. 📝",
        'serious_warning_missed_classes': "ВНИМАНИЕ! Ваш ребенок {student_name} пропустил {missed_count} занятий в {month} месяце. Пожалуйста, выясните причину. ⚠️",

        # Отметка посещаемости (Учитель)
        'select_attendance_date': "Выберите дату для отметки посещаемости: 🗓️",
        'today_button': "Сегодня 🗓️",
        'date_not_selected_error': "Дата не выбрана. Пожалуйста, попробуйте еще раз. ❌",
        'attended': "Присутствовал ✅",
        'missed': "Отсутствовал ❌",
        'excused': "По уважительной причине 📝",
        'select_attendance_status': "Выберите статус посещаемости: 👇",
        'attendance_marked': "Посещаемость для {student_id} отмечена как '{status}'. ✅",

        # Назначение расписания (Супер-админ)
        'enter_class_times_for_date': "Введите время занятий для {date}: ⏰",
        'class_times_empty': "Время занятий не может быть пустым. 🚫",
        'confirm_schedule_text_with_date': "Группа: {group_name}\nДата: {date}\nВремя занятий: {class_times}\n\nПодтверждаете сохранение этого расписания?",
        'confirm_save_schedule_yes': "Да, сохранить ✅",
        'confirm_save_schedule_no': "Нет, ввести заново 🔄",
        'schedule_assigned_confirmed': "Расписание для группы '{group_name}' успешно установлено на '{class_times}'. 🎉",

        # Статистика
        'statistics_text': "Статистика:\n",
        'missed_classes': "пропущенных занятий",

        # Пользователи (Супер-админ)
        'all_users_list': "Все пользователи:\n",
        'user_details': "ID: {id}, Имя: {name}, Логин: {login}, Телефон: {phone}, Роль: {role}\n",
        'select_user_for_details': "Выберите пользователя для просмотра деталей: 👇",
        'select_user_for_role_change': "Выберите пользователя для изменения роли: 👇",
        'user_details_full': "Информация о пользователе:\nID: {user_id}\nИмя: {full_name}\nФамилия: {last_name}\nЛогин: {login}\nТелефон: {phone}\nРоль: {role}\nГруппа: {group_name}\nТариф: {tariff_plan} ({tariff_price} сум)\nДолг: {debt_amount} сум\nСтатус оплаты: {payment_status}\nЯзык: {language}",
        'enter_new_role_for_user': "Введите новую роль для пользователя `{login}` (Student, Parent, Teacher) или в формате `логин:роль:тариф`: ✍️",

        # Эффективность учителя (Панель учителя)
        'teacher_performance_title': "Эффективность учителя {teacher_name}:\n",
        'last_month_rating': "Оценка за последний месяц: {rating}\n",
        'last_3_months_rating': "Средняя оценка за последние 3 месяца: {rating}\n",
        'overall_rating': "Общая оценка: {rating}\n",
        'total_ratings_count': "Общее количество оценок от студентов: {count}\n",
        'not_rated': "Не оценено",
        'performance_excellent': "🏆 Ваш рейтинг превосходен! Продолжайте в том же духе!",
        'performance_very_good': "👍 Отличный результат! С небольшими улучшениями вы сможете достичь еще больших высот.",
        'performance_good': "👌 Хороший результат. Обратите внимание на некоторые аспекты для улучшения.",
        'performance_needs_improvement': "💡 Возможно, вам потребуются дополнительные тренинги или консультации для повышения эффективности.",
        'performance_no_data': "Данные об эффективности пока отсутствуют. Дождитесь оценок студентов.",

        # Оценка учителя студентом (Панель студента)
        'no_group_assigned_for_evaluation': "Вам не назначена группа, поэтому вы не можете оценить учителя. 🤷‍♀️",
        'no_teacher_for_group': "Вашей группе не назначен учитель. 🤷‍♀️",
        'teacher_not_found_db': "Учитель не найден в базе данных. 🛠️",
        'eval_q1': "Побуждает ли учитель вас активно участвовать в занятиях?\n(1 – Совсем нет, 5 – Всегда активно участвую)",
        'eval_q2': "Насколько интересны и полезны для вас учебные материалы (упражнения, задания, тексты)?\n(1 – Очень скучно, 5 – Очень интересно и полезно)",
        'eval_q3': "Чувствуете ли вы, что ваши знания улучшаются после этих занятий?\n(1 – Совсем нет, 5 – Да, я замечаю явный прогресс)",
        'rating_accepted': "Принято ✅",
        'thank_you_for_rating': "Спасибо за оценку! 👍",
        'evaluation_saved': "Ваши оценки успешно сохранены. 🎉",

        # Массовая и индивидуальная рассылка сообщений (Супер-админ)
        'enter_mass_message': "Введите сообщение, которое вы хотите отправить всем пользователям: 📢",
        'message_empty': "Текст сообщения не может быть пустым. 🚫",
        'mass_message_sent_summary': "Массовая рассылка сообщений завершена.\nОтправлено: {sent}\nОшибок: {failed}",
        'message_from_admin': "Это сообщение отправлено администратором.",
        'message_from_admin_individual': "Это сообщение отправлено вам лично администратором.",
        'select_user_type_for_message': "Выберите тип пользователя для отправки сообщения: 👇",
        'student_role': "Студент 🧑‍🎓",
        'parent_role': "Родитель 👨‍👩‍👧‍👦",
        'teacher_role': "Учитель 🧑‍🏫",
        'all_users': "Все пользователи 🌐",
        'no_users_found_for_role': "Пользователи для роли '{role}' не найдены. 🤷‍♀️",
        'select_user_to_message': "Выберите пользователя, которому отправить сообщение: 👇",
        'enter_message_for_user': "Введите сообщение, которое вы хотите отправить {user_name}: ✉️",
        'message_sent_success': "Сообщение успешно отправлено {user_name}. ✅",
        'message_sent_failed': "Произошла ошибка при отправке сообщения {user_name}. ❌",

        # Отзывы студентов (Панель студента)
        'no_group_assigned_for_feedback': "Вам не назначена группа, поэтому вы не можете оставить отзыв. 🤷‍♀️",
        'no_teacher_for_group_feedback': "Вашей группе не назначен учитель, поэтому вы не можете оставить отзыв. 🤷‍♀️",
        'enter_feedback_text': "Введите ваш анонимный отзыв: 💬",
        'feedback_empty': "Текст отзыва не может быть пустым. 🚫",
        'feedback_saved': "Ваш отзыв успешно сохранен. Спасибо! 🙏",

        # Просмотр отзывов (Супер-админ)
        'no_teachers_for_feedback_view': "Учителя для просмотра отзывов не найдены. 🤷‍♀️",
        'select_teacher_for_feedback_view': "Выберите учителя для просмотра отзывов: 👇",
        'no_feedback_for_teacher': "Отзывов для {teacher_name} пока нет. 🤷‍♀️",
        'feedback_list_for_teacher': "Отзывы для {teacher_name}:\n",
        'feedback_entry': "📅 {date}\n💬 {feedback}\n\n",
    }
}

def get_text(lang, key, default=None):
    """
    Berilgan til va kalit bo'yicha tarjimani qaytaradi.
    Agar tarjima topilmasa, default qiymatni yoki kalit nomini qaytaradi.
    """
    return translations.get(lang, {}).get(key, default if default is not None else f"[{key}]")

def get_all_translations_for_key(key):
    """
    Barcha tillar bo'yicha berilgan kalitning tarjimalarini qaytaradi.
    """
    all_translated_texts = []
    for lang_code in translations:
        text = translations[lang_code].get(key)
        if text:
            all_translated_texts.append(text)
    return all_translated_texts