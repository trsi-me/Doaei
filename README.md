# دوائي

منصة عربية لإدارة الأدوية والتذكيرات والاستشارات وطلبات الصيدلية. الخادم Flask في `app.py`. القاعدة `doaei.db` عبر SQLAlchemy. الإصدار المصرح به في `config.py`: `APP_VERSION = 1.0.0` واسم التطبيق «دوائي».

## 1 ما هو المشروع

نظام متعدد الأدوار: مريض يسجّل أدويته وجرعاته، طبيب يتابع مرضاه ومواعيده وتقييماته، صيدلي يرد على الاستشارات ويدير منتجات وطلبات، وحساب بدور `user` يصل إلى لوحات الإدارة (مستخدمون، موظفون، دخل، مصروف، تقارير، تحليلات). يوجد قالب `templates/dashboard/caregiver.html`. دور مقدم الرعاية مذكور في README السابق وفي علم مشاركة `share_with_caregivers`. نموذج التسجيل العام في `forms.py` يعرض ثلاثة أدوار فقط: مريض، طبيب، صيدلي.

تناقض تسمية الدور الإداري: مسارات `/admin/*` تشترط `current_user.role == 'user'` لا `'admin'`. عند الإقلاع توجد عملية تحديث `UPDATE users SET role = 'user' WHERE role = 'admin'`. README السابق يقول إن دور المدير إداري والقيمة `user`. هذا يطابق الكود، والاسم الظاهر «إداري» يختلف عن النص المخزن `user`.

## 2 لماذا وُجد

جمع سجل الدواء والتذكير والاستشارة والتقرير في مكان واحد باللغة العربية، مع توصيات من نموذج Random Forest مدرَّب على مصفوفة صغيرة داخل `ai_service.py`. README السابق يلخص الهدف الطبي. الكود يضيف متجراً للصيدلية (منتجات، سلة، طلب، تتبع).

## 3 المستخدمون

| الدور المخزن | الواجهة |
| --- | --- |
| patient | أدوية، تذكيرات، استشارات، تقييمات، مواعيد، سلة |
| doctor | مرضى مرتبطون بـ `doctor_id`، تقييمات، مواعيد |
| pharmacist | استشارات والرد عليها، صيدليات، منتجات، حالات طلب |
| user | لوحة تُعرض كإدارة |
| caregiver | قالب موجود. التسجيل العام لا يعرض هذا الخيار |

حسابات `init_db.py` و`add_default_data.py` و`fix_passwords.py` و`reset_database.py` تستخدم كلمة مرور موحدة `123456` وبريداً مثل `admin@doaei.com` و`patient@doaei.com` و`doctor1@doaei.com` و`pharmacist@doaei.com`.

تناقض كلمات المرور: `create_test_users.py` يضع `patient123` لمريض تجريبي. مسار داخل `app.py` عند إنشاء صف مريض في فرع تهيئة يجزّئ `patient123`. `forms.py` يقبل كلمة مرور بطول 6 على الأقل، بينما `Config.PASSWORD_MIN_LENGTH` يساوي 8 مع اشتراط حروف كبيرة وصغيرة وأرقام ورموز. الحسابات المزروعة بـ `123456` لا تحقق قاعدة `Config` تلك. المصدران موجودان معاً: الزرع يستخدم 123456، وخصائص Config تطلب كلمة أقوى.

`app.py` عند التشغيل يطبع بريد `admin@doaei.com`.

## 4 الميزات

موجود كمسارات وقوالب:

- أدوية وجرعات وتذكيرات (إضافة، تأجيل، تعليم بالتناول، حذف).
- استشارات ورفع رد من الصيدلي.
- تقييمات ومراجعات منتجات.
- تقارير PDF عبر `pdf_generator.py` وReportLab وتنزيل.
- إحصاءات ولوحة.
- توصيات: قبول ورفض وحفظ وتغذية راجعة وجرعة حسب اسم دواء.
- صيدليات ومنتجات وسلة ودفع طلب وتتبع وتحديث حالة من الصيدلية.
- ملف شخصي وتغيير كلمة مرور وإعدادات حساب وخصوصية وأمان وإشعارات ونظام.
- إشعارات داخلية وجدولتها وفحص المجدول.
- بحث `/api/search`.
- دخل ومصروف وموظفون وتحليلات للحساب ذي الدور `user`.
- مواعيد طبيب ومريض وتقييمات طبية.

التذكير بالبريد وSMS: `utils.py` فيه `send_email` و`send_sms` يقرآن إعدادات البريد و`SMS_API_KEY` / `SMS_API_URL`. الإرسال الفعلي يعتمد على وجود القيم في البيئة. بدونهما الدوال لا تكمل الإرسال الخارجي.

نموذج الذكاء: 8 صفوف تدريب ثابتة، الميزات `[العمر، الجنس 0/1، عدد الأدوية، أمراض مزمنة 0/1]`، والتصنيفات: medication_timing, interaction_warning, adherence_support, dosage_optimization, monitoring_required, lifestyle_advice. المصنف `RandomForestClassifier(n_estimators=100, random_state=42)`. الملف `ai_models/recommendation_model.pkl` و`label_encoder.pkl` يُنشآن إن غابا.

هذا ليس نموذجاً سريرياً معتمداً. البيانات داخل الكود صغيرة وثابتة.

## 5 سير العمل

```
/register أو init_db
  -> /login (Flask-Login)
  -> /dashboard حسب role
مريض: دواء -> create_medication_doses -> تذكيرات
      استشارة -> pharmacist يرد
      منتج -> سلة -> checkout -> order
إدارة user: /admin/dashboard ومالية وموظفون
تذكير خلفي: ReminderService كل دقيقة عند تشغيل app.py
```

`wsgi.py` يستدعي `create_app()` لـ gunicorn. كتلة `__main__` في `app.py` تبدأ خيط التذكيرات بعد ثانيتين. استنتاج من الكود: تشغيل gunicorn عبر Procfile لا يمر بكتلة `__main__`، فخدمة `schedule` قد لا تبدأ إلا مع `python app.py` ما لم تُستدعَ من مكان آخر. البحث في `wsgi.py` يظهر سطراً واحداً: `create_app` فقط.

## 6 أمثلة واقعية

مريض من البذرة (بعد `python init_db.py`) يدخل ببريده وكلمة `123456`، يرى أدوية افتراضية (README السابق: دواءان لكل مريض واستشارتان وتقييم وموعد). يعلّم جرعة مأخوذة من `/api/take-dose/<dose_id>`. يطلب توصية من `/ai/generate` فيُصنّف النموذج أحد الأنواع الستة حسب العمر والأدوية.

صيدلي يفتح الاستشارة ويرد من `/consultations/<id>/reply`.

حساب `admin@doaei.com` بدور `user` يفتح `/admin/income` و`/admin/expenses`.

## 7 رحلة المستخدم

1. تثبيت المتطلبات و`python init_db.py` ثم `python app.py`.
2. فتح `http://localhost:5000`.
3. الدخول بحساب البذرة أو التسجيل كمريض أو طبيب أو صيدلي.
4. المريض يضيف دواءً من `/medications/add` فتتولد الجرعات والتذكيرات.
5. يطلب استشارة ويراجع الرد.
6. يضيف منتجاً للسلة ويتم الطلب ويتابع `/orders/track`.
7. الطبيب يفتح `/doctor/patients` ثم تفاصيل المريض.
8. الخروج من `/logout`.

## 8 الوحدات

| الملف | الدور |
| --- | --- |
| `app.py` | التطبيق والمسارات وخيط التذكير |
| `wsgi.py` | نقطة gunicorn |
| `config.py` | إعدادات وتطوير وإنتاج واختبار |
| `models.py` | نماذج SQLAlchemy |
| `forms.py` | نماذج Flask-WTF |
| `utils.py` | كلمات مرور وإشعارات وبريد وSMS |
| `ai_service.py` | Random Forest |
| `reminder_service.py` | جدولة كل دقيقة وكل ساعة |
| `pdf_generator.py` | PDF |
| `order_management.py` | منطق طلبات |
| `init_db.py` `add_default_data.py` `populate_data.py` `reset_database.py` `fix_passwords.py` `create_test_users.py` `add_user_columns.py` | تهيئة وبيانات |
| `database/schema.sql` | مخطط SQL موازٍ |
| `templates/` | قوالب حسب الدور |
| `static/css/style.css` `static/js/main.js` `static/js/sw.js` | واجهة وعامل خدمة |
| `Procfile` | `web: gunicorn wsgi:app` |

حزمة `schedule` مستوردة في `reminder_service.py` وغير مذكورة في `requirements.txt`. هذا نقص في ملف المتطلبات.

## 9 الكيانات

أصناف `models.py`: `User`, `Medication`, `MedicationDose`, `Reminder`, `SharedRecord`, `Consultation`, `ProductRating`, `Report`, `AuditLog`, `SystemSetting`, `Pharmacy`, `PharmacyProduct`, `Order`, `OrderItem`, `OrderTracking`, `AIRecommendation`, `Review`, `Evaluation`, `Income`, `Expense`, `Department`, `Employee`, `Notification`.

حقول المستخدم تشمل بريداً فريداً، `password_hash`، هاتفاً، دوراً، بيانات طبية، `doctor_id` ذاتي، فصيلة دم، تفضيلات إشعار JSON، عنواناً، لغة افتراضية `ar`، منطقة `Asia/Riyadh`.

`schema.sql` مخطط إضافي. التشغيل الحي عبر SQLAlchemy و`doaei.db`. إن اختلف ملف SQL عن `models.py` فالمستخدم عند التشغيل هو النماذج. راجع الفرق يدوياً قبل الاعتماد على أحدهما.

## 10 الصلاحيات

Flask-Login يحمّل المستخدم. أمثلة من الكود:

- أدوية المريض: `role == patient`.
- مسارات `/admin/*`: `role == user`.
- الطبيب: `role == doctor` والمرضى حيث `doctor_id` يساوي معرفه.
- الصيدلي: مسارات الصيدلية والرد على الاستشارة.
- دوال `can_edit_medication` و`can_view_medication` تفحص الملكية.

`/api/admin/logs` غير موجود هنا. هذا المشروع ليس Diplomi.

بعض مسارات API تتحقق من الدخول عبر `login_required` حيث وُضع المزخرف على الدالة. عند التعديل راجع المزخرف فوق كل مسار لأن الملف طويل.

## 11 الأتمتة

- `create_medication_doses` و`create_reminders_for_dose` عند إضافة دواء.
- `ReminderService`: `schedule.every(1).minutes` لفحص التذكير و`every().hour` لتنظيف القديم، داخل خيط عند `python app.py`.
- `AIService._load_or_train_model` عند الاستخدام.
- إنشاء القاعدة من `init_database` إذا غاب `doaei.db` في كتلة التشغيل.
- تحويل دور `admin` إلى `user` في تهيئة `app.py`.

## 12 تأثير الوحدات على بعضها

- إضافة دواء تنشئ جرعات ثم تذكيرات وقد تنشئ إشعاراً عبر `NotificationService`.
- تعليم الجرعة مأخوذة يحدّث `MedicationDose` وحالة التذكير.
- قبول توصية AI يحدّث صف `AIRecommendation` وقد ينعكس على لوحة المريض.
- الطلب من السلة ينشئ `Order` و`OrderItem` و`OrderTracking`. تحديث الصيدلي لحالة الطلب يغيّر ما يراه المريض في التتبع.
- ربط `doctor_id` يحدد قائمة مرضى الطبيب.
- حذف دواء يتأثر بـ `cascade` على علاقة medications في النموذج.

## 13 مسرد

| المصطلح | هنا |
| --- | --- |
| dose | صف موعد جرعة |
| reminder | تنبيه مرتبط بجرعة |
| role=user | حساب لوحة الإدارة في هذا الكود |
| AIRecommendation | صف توصية مصنّفة من الغابة العشوائية |
| CSRF | نماذج Flask-WTF. الاختبار يعطّل `WTF_CSRF_ENABLED` |

## 14 أسئلة شائعة

**ما كلمة المرور بعد init_db؟** `123456` لكل الحسابات التي يزرعها ذلك الملف، ومنها `admin@doaei.com`.

**لماذا لا أدخل لوحة الإدارة وأنا admin؟** لأن المسار يفحص الدور `user`. التهيئة تعيد تسمية admin إلى user.

**هل الذكاء الاصطناعي يفحص تفاعلاً دوائياً مخبرياً؟** يصنّف ميزات رقمية قليلة إلى نوع توصية. نص التحذير من التفاعل صنف من أصناف التدريب، لا قاعدة تفاعلات خارجية.

**هل SMS يعمل دائماً؟** فقط إذا وُجدت مفاتيح البيئة واستُدعيت دوال `utils.py`.

## 15 مخطط المعمارية ASCII

```
المتصفح + sw.js
      |
      v
Flask app.py  +  wsgi.py (gunicorn)
  Flask-Login  Flask-WTF  SQLAlchemy
      |
      +-- doaei.db
      +-- static/uploads
      +-- ai_models/*.pkl
      |
      +-- reminder_service (خيط مع python app.py)
      +-- utils: SMTP و SMS.to إن وُجدت المفاتيح
      +-- pdf_generator
```

## 16 التقنيات المستخدمة

من `requirements.txt` و`config.py`:

- Flask 2.3.3 وWerkzeug 2.3.7
- Flask-SQLAlchemy 3.0.5 وFlask-Login 0.6.3
- Flask-WTF 1.2.1 وWTForms 3.0.1
- flask-session 0.5.0 وflask-migrate 4.0.5 وflask-cors 4.0.0
- bcrypt 4.0.1 وcryptography 41.0.4
- email-validator 2.0.0 وphonenumbers 8.13.19
- requests 2.31.0 وpython-dotenv 1.0.0 وPillow 10.0.0
- reportlab 4.0.4
- numpy 1.24.3 وscikit-learn 1.3.0 وpandas 2.0.3 وscipy 1.11.1
- gunicorn 21.2.0
- SQLite
- HTML وCSS وJavaScript وخط IBM Plex Sans Arabic حسب README السابق

تناقض نسخة Flask-WTF: README السابق يذكر `1.1.1`. الملف `requirements.txt` الحالي يثبت `1.2.1`. المعتمد للتثبيت هو ملف المتطلبات.

حزمة `schedule` مستخدمة وغير مذكورة في المتطلبات.

## 17 شجرة الملفات

```
Doaei/
├── app.py
├── wsgi.py
├── config.py
├── models.py
├── forms.py
├── utils.py
├── ai_service.py
├── reminder_service.py
├── pdf_generator.py
├── order_management.py
├── init_db.py
├── add_default_data.py
├── populate_data.py
├── reset_database.py
├── fix_passwords.py
├── create_test_users.py
├── add_user_columns.py
├── requirements.txt
├── Procfile
├── doaei.db
├── database/schema.sql
├── ai_models/
├── templates/   auth dashboard medications consultations
│                pharmacy products orders reports ai settings ...
└── static/css  static/js  static/uploads
```

## 18 الواجهة الأمامية

قوالب Jinja عربية RTL. `base.html` إطار. لوحات منفصلة: patient, doctor, pharmacist, admin, user, caregiver. `static/js/main.js` تفاعل عام. `static/js/sw.js` عامل خدمة للمتصفح. النماذج من `forms.py` مع رسائل التحقق.

## 19 الواجهة الخلفية

`create_app` يضبط الإعدادات وFlask-Login (`load_user`) ويسجّل المسارات في `register_routes`.

دوال مساعدة خارج المسارات: `get_upcoming_reminders`, `get_doctor_patients`, `get_user_stats`, `can_edit_medication`, `can_view_medication`, `create_medication_doses`, `create_reminders_for_dose`, `generate_pdf_report`, `get_notification_icon`.

أصناف الخدمات: `AIService`, `ReminderService`, `NotificationService`.

لا FastAPI.

## 20 تدفق الطلب

1. المتصفح يرسل النموذج أو fetch.
2. Flask-Login يتعرف على المستخدم من الجلسة.
3. الدالة تفحص `role`.
4. SQLAlchemy تقرأ أو تكتب `doaei.db`.
5. الرد HTML أو JSON أو ملف PDF.
6. خيط التذكير، إن كان يعمل، يقرأ `Reminder` ويرسل عبر `NotificationService`.

مدة الجلسة في الإعداد: `PERMANENT_SESSION_LIFETIME` يساوي 24 ساعة.

## 21 قاعدة البيانات

`sqlite:///doaei.db` بجانب المشروع في التطوير. الإنتاج يقرأ `DATABASE_URL` إن وُجد وإلا `sqlite:///doaei.db`. الاختبار `sqlite:///:memory:`.

كلمات المرور bcrypt عبر `utils.py`.

`AuditLog` نموذج موجود للسجل. مسارات كثيرة تكتب كيانات العمل. لا تفترض أن كل مسار يدرج تدقيقاً إلا إذا استدعيت الكتابة داخل تلك الدالة.

## 22 نقاط النهاية

المصادقة: «دخول» تعني `@login_required` حيث هو مستخدم على المسار، مع فحص دور إضافي مذكور. المسارات المزدوجة تؤدي إلى نفس الدالة.

| الطريقة | المسار | الغرض | مصادقة |
| --- | --- | --- | --- |
| GET | `/` | الرئيسية | عام |
| GET/POST | `/login` | دخول | عام |
| GET/POST | `/register` | تسجيل | عام |
| GET | `/logout` | خروج | دخول |
| GET | `/dashboard` | لوحة حسب الدور | دخول |
| GET | `/medications` | قائمة أدوية | مريض |
| GET/POST | `/medications/add` و`/add_medication` | إضافة | مريض |
| GET/POST | `/medications/<id>/edit` | تعديل | مريض |
| POST | `/medications/<id>/delete` | حذف | مريض |
| GET | `/consultations` | استشارات | دخول |
| GET/POST | `/consultations/add` و`/add_consultation` | جديدة | حسب الدور |
| GET | `/consultations/<id>` و`/.../view` | عرض | ملكية للمريض |
| GET/POST | `/consultations/<id>/reply` | رد | صيدلي |
| GET | `/patient/ratings` و`/ratings` | تقييمات | مريض |
| GET/POST | `/patient/ratings/add` و`/add_rating` | إضافة تقييم | مريض |
| GET | `/patient/appointments` و`/upcoming-appointments` | مواعيد | مريض |
| GET | `/admin/users` | مستخدمون | user |
| GET | `/admin/employees` | موظفون | user |
| GET | `/admin/income` | دخل | user |
| GET | `/admin/expenses` | مصروف | user |
| GET | `/admin/financial-reports` | تقارير مالية | user |
| GET | `/admin/analytics` | تحليلات | user |
| GET | `/user/dashboard` و`/admin/dashboard` | لوحة الإدارة | user |
| GET | `/doctor/patients` | مرضى الطبيب | طبيب |
| GET | `/doctor/patients/<id>` | تفاصيل | طبيب |
| GET | `/doctor/evaluations` | تقييمات | طبيب |
| GET | `/doctor/evaluations/<id>` | تفاصيل تقييم | طبيب |
| GET/POST | `/doctor/evaluations/add` | تقييم جديد | طبيب |
| GET | `/doctor/appointments` | مواعيد الطبيب | طبيب |
| GET/POST | `/doctor/appointments/add` | موعد | طبيب |
| GET | `/reports` | تقارير | دخول |
| GET | `/statistics` | إحصاءات | دخول |
| GET/POST | `/reports/generate` و`/generate_report` | توليد | دخول |
| GET | `/reports/<id>/download` | PDF | دخول |
| GET | `/profile` | الملف | دخول |
| GET/POST | `/profile/edit` | تعديل | دخول |
| GET/POST | `/profile/change-password` | كلمة مرور | دخول |
| GET/POST | `/settings/notifications` | إشعارات | دخول |
| GET/POST | `/settings/privacy` | خصوصية | دخول |
| GET/POST | `/settings/security` | أمان | دخول |
| GET/POST | `/settings/account` | حساب | دخول |
| GET/POST | `/settings/system` | نظام | دخول |
| GET | `/reminders` | صفحة تذكير | دخول |
| GET/POST | `/api/reminders` | قائمة أو إضافة | دخول |
| POST | `/api/reminders/<id>/mark-taken` | تم التناول | دخول |
| POST | `/api/reminders/<id>/snooze` | تأجيل | دخول |
| DELETE | `/api/reminders/<id>` | حذف | دخول |
| GET/POST | `/api/medications` | قائمة أو إضافة | دخول |
| PUT/DELETE | `/api/medications/<id>` | تعديل أو حذف | دخول |
| GET | `/notifications` | صفحة إشعارات | دخول |
| GET | `/api/notifications` | JSON | دخول |
| POST | `/api/notifications/<id>/read` | مقروء | دخول |
| DELETE | `/api/notifications/<id>` | حذف | دخول |
| POST | `/api/notifications/schedule` | جدولة | دخول |
| POST | `/api/notifications/check-scheduled` | فحص | دخول |
| GET | `/ai/dashboard` و`/api/ai/dashboard` | لوحة AI | دخول |
| POST | `/api/ai/recommendations` | طلب | دخول |
| POST | `/api/ai/recommendations/<id>/accept` | قبول | دخول |
| POST | `/api/ai/recommendations/<id>/reject` | رفض | دخول |
| GET | `/api/user/profile` | ملف JSON | دخول |
| PUT | `/api/user/profile` | تحديث | دخول |
| POST | `/api/user/change-password` | كلمة مرور | دخول |
| GET | `/api/statistics/dashboard` | أرقام | دخول |
| GET | `/api/search` | بحث | دخول |
| POST | `/api/take-dose/<dose_id>` | تناول جرعة | دخول |
| GET | `/pharmacy` | صيدليات | دخول |
| GET | `/pharmacy/<id>` | تفاصيل | دخول |
| GET/POST | `/pharmacy/add` و`/add_pharmacy` | إضافة | حسب الدور |
| GET/POST | `/pharmacy/<id>/edit` | تعديل | حسب الدور |
| POST | `/pharmacy/<id>/delete` | حذف | حسب الدور |
| GET | `/products` و`/products/<id>` | منتجات | عام أو دخول حسب الدالة |
| GET/POST | `/products/add` و`/add_product` | إضافة | حسب الدور |
| GET/POST | `/products/<id>/edit` | تعديل | حسب الدور |
| POST | `/products/<id>/delete` | حذف | حسب الدور |
| GET | `/cart` | سلة | دخول |
| POST | `/cart/add` و`/add_to_cart` | إضافة | دخول |
| POST | `/cart/remove` | إزالة | دخول |
| GET/POST | `/checkout` | إتمام | دخول |
| GET | `/orders` و`/orders/<id>` | طلبات | دخول |
| POST | `/orders/<id>/cancel` | إلغاء | دخول |
| GET/POST | `/orders/track` | تتبع | حسب النموذج |
| GET | `/pharmacy/orders` | طلبات الصيدلية | صيدلي |
| POST | `/pharmacy/orders/<id>/update` | حالة | صيدلي |
| GET | `/recommendations` و`/ai/recommendations` | توصيات | دخول |
| GET/POST | `/ai/recommendations/request` | طلب صفحة | دخول |
| POST | `/ai/recommendations/<id>/accept` | قبول | دخول |
| POST | `/ai/recommendations/<id>/reject` | رفض | دخول |
| POST | `/ai/recommendations/<id>/save` | حفظ | دخول |
| POST | `/recommendations/feedback` | تغذية | دخول |
| GET | `/recommendations/dosage/<medication_name>` | جرعة | دخول |
| GET | `/reviews` | مراجعات | دخول |
| GET/POST | `/reviews/add` و`/add_review` | إضافة | دخول |
| GET/POST | `/reviews/<id>/edit` | تعديل | دخول |
| POST | `/reviews/<id>/delete` | حذف | دخول |
| POST | `/ai/generate` | توليد توصية | دخول |
| POST | `/ai/feedback/<id>` | ملاحظات | دخول |
| POST | `/select-doctor` | اختيار طبيب | مريض |

المعاملات هي حقول النموذج أو JSON الخاصة بكل شاشة (اسم دواء، جرعة، تكرار، نص استشارة، معرفات). الرد HTML للقوالب وJSON لمسارات `/api/*` وملف عند تنزيل التقرير.

## 23 المصادقة

Flask-Login. كلمة المرور bcrypt في `utils.py` (`hashpw` / `checkpw`). الجلسة 24 ساعة حسب الإعداد. نماذج WTF للتسجيل والدخول.

لا JWT في هذا المشروع. PyJWT غير موجود في متطلبات دوائي.

## 24 الأمان الموجود فعلياً في الكود

- bcrypt لكلمات المرور.
- ORM بمعاملات.
- فحص دور على المسارات الحساسة المذكورة.
- CSRF عبر Flask-WTF على النماذج التي تستخدمه. وضع الاختبار يعطّله.
- حد رفع 16 ميجابايت وامتدادات png jpg jpeg gif pdf.
- `AuditLog` نموذج جاهز.
- `SECRET_KEY` من البيئة أو قيمة ثابتة تطويرية في `config.py` (غير مطبوعة هنا).
- حسابات الزرع بكلمة قصيرة مشتركة.
- دور الإدارة اسمه `user` وهذا سهل الخلط.
- CORS مذكور في المتطلبات. تفعيل السياسة الدقيقة راجع تهيئة `create_app` عند التعديل.
- لا حد محاولات دخول ظاهر في مقطع الدخول المختصر.

## 25 مفاتيح الإعداد بدون قيم

| المفتاح | الاستخدام |
| --- | --- |
| SECRET_KEY | جلسة Flask |
| DATABASE_URL | إنتاج، وإلا SQLite |
| MAIL_SERVER | افتراضي smtp.gmail.com |
| MAIL_PORT | افتراضي 587 |
| MAIL_USE_TLS | افتراضي true |
| MAIL_USERNAME | بريد الإرسال |
| MAIL_PASSWORD | سر البريد |
| SMS_API_KEY | الرسائل |
| SMS_API_URL | افتراضي عنوان خدمة sms.to |

`python-dotenv` في المتطلبات. لا ملف `.env.example` ظاهر في الشجرة المقروءة.

ثوابت داخل `Config` بلا بيئة: `PASSWORD_MIN_LENGTH` 8، أعلام تعقيد كلمة المرور، `APP_NAME` دوائي، `APP_VERSION` 1.0.0، `POSTS_PER_PAGE` 20، `CACHE_TYPE` simple، `CACHE_DEFAULT_TIMEOUT` 300.

## 26 التكاملات

- SMTP للبريد عند استدعاء `send_email`.
- SMS عبر HTTP إلى `SMS_API_URL` عند استدعاء `send_sms`.
- ReportLab لملفات PDF.
- scikit-learn للتوصيات المحلية.
- لا بوابة دفع ظاهرية في المتطلبات. طريقة الدفع في الطلب حقل نموذج (`payment_method`).

## 27 المهام المجدولة

`ReminderService` كل دقيقة وساعة، خيط خلفي مع `python app.py`. الحزمة `schedule` غير مثبتة في `requirements.txt`، فالخيط يطبع تحذيراً إن فشل الاستيراد حسب `try` في نهاية `app.py`.

لا ملف cron منفصل. Procfile عملية ويب واحدة.

## 28 تخزين الملفات

`UPLOAD_FOLDER = static/uploads`. مرفقات الاستشارات والوصفات حسب النماذج. التقارير المولدة تُحفظ حسب `pdf_generator.py` وتُنزَّل من مسار التقرير.

## 29 التسجيل

`print` عند الإقلاع وأخطاء التذكير. نموذج `AuditLog` للتدقيق داخل القاعدة. لا إطار logging موحّد في رأس `app.py` المقروء.

## 30 التثبيت من requirements

```
pip install -r requirements.txt
python init_db.py
python app.py
```

لإضافة بيانات على قاعدة موجودة: `python add_default_data.py`.

ثم `http://localhost:5000`.

Python: README السابق والكود في نهاية `app.py` يطلبان 3.8 أو أحدث.

ثبّت حزمة الجدولة `schedule` إذا أردت خيط التذكير، لأنها مستوردة وغير مذكورة في المتطلبات.

## 31 دليل التطوير

- المسارات داخل `register_routes` في `app.py`.
- غيّر النموذج في `models.py` ثم راعِ قاعدة موجودة (هناك `add_user_columns.py` وflask-migrate في المتطلبات).
- لا تخلط دور `user` مع مستخدم عادي في الواجهة.
- نموذج AI يتدرب على 8 صفوف. استبدله ببيانات حقيقية خارج هذا الملف إن تغيّر الغرض، ولا تقدّمه كنصيحة طبية.
- راجع `schema.sql` مقابل النماذج عند الاختلاف.
- `create_test_users.py` كلمة مختلفة عن `init_db.py`.

## 32 النشر

`Procfile`:

```
web: gunicorn wsgi:app
```

لا ملف `DEPLOY_HEROKU.md` داخل Doaei. النشر الموثق هنا هو عملية gunicorn التي تستورد `wsgi:app`. اضبط `SECRET_KEY` و`DATABASE_URL` ومفاتيح البريد في بيئة المنصة. قرص SQLite المحلي يضيع على منصة بلا قرص دائم.

خيط التذكير مرتبط بتشغيل `python app.py` لا بـ `wsgi.py`.

## 33 النسخ الاحتياطي

انسخ `doaei.db` ومجلد `static/uploads` و`ai_models/` إن أردت الإبقاء على النموذج المدرَّب. يمكن إعادة تدريبه تلقائياً عند غيابه من البيانات الثابتة في `ai_service.py`.

## 34 استكشاف الأخطاء

| العرض | الاتجاه |
| --- | --- |
| مكتبة مفقودة | `pip install -r requirements.txt` |
| لا قاعدة | `python init_db.py` |
| دخول الإدارة يفشل بكلمة README | تأكد أن الدور `user` وأن الكلمة 123456 من آخر زرع |
| patient123 لا تعمل | هذه كلمة `create_test_users.py` لا `init_db.py` |
| التذكير لا يعمل تحت gunicorn | الخيط في `__main__` فقط، أو حزمة schedule غير مثبتة |
| البريد لا يخرج | مفاتيح MAIL_* فارغة |
| المنفذ 5000 مشغول | أوقف العملية الأخرى |

## 35 الاعتماديات مع الإصدارات من requirements.txt

| الحزمة | الإصدار |
| --- | --- |
| Flask | 2.3.3 |
| Werkzeug | 2.3.7 |
| Flask-SQLAlchemy | 3.0.5 |
| Flask-Login | 0.6.3 |
| Flask-WTF | 1.2.1 |
| WTForms | 3.0.1 |
| flask-session | 0.5.0 |
| flask-migrate | 4.0.5 |
| flask-cors | 4.0.0 |
| bcrypt | 4.0.1 |
| cryptography | 41.0.4 |
| email-validator | 2.0.0 |
| phonenumbers | 8.13.19 |
| requests | 2.31.0 |
| python-dotenv | 1.0.0 |
| Pillow | 10.0.0 |
| reportlab | 4.0.4 |
| numpy | 1.24.3 |
| scikit-learn | 1.3.0 |
| pandas | 2.0.3 |
| scipy | 1.11.1 |
| gunicorn | 21.2.0 |

## 36 القيود

- نموذج التوصية مدرَّب على 8 عينات ثابتة.
- كلمة الزرع ضعيفة ومشتركة.
- دور الإدارة اسمه `user`.
- تذكير الخلفية لا يبدأ من `wsgi.py`.
- `schedule` خارج المتطلبات.
- SMS والبريد مشروطان بالبيئة.
- الدفع حقل حالة لا بوابة.
- قواعد كلمة المرور في Config لا تُطبَّق على حسابات الزرع.
- لا اختبارات آلية ظاهرة في جذر المجلد.

## 37 الحالة الحالية

منصة كبيرة تعمل بـ Flask وSQLite، بواجهات للأدوار، ومتجر صيدلية، وتقارير، وتوصيات محلية، وتذكير عند التشغيل المباشر. Procfile جاهز لـ gunicorn. بيانات العرض تُزرع بأدوات Python منفصلة.

## 38 قرارات المعمارية

- SQLAlchemy بدل SQL خام في المسارات.
- دور `user` كلوحة إدارة بعد ترحيل قيمة `admin`.
- التوصية مصنف محلي يُحفظ pickle حتى لا يُدرَّب في كل طلب.
- التذكير خيط داخل العملية.
- PDF على الخادم عبر ReportLab.
- إعدادات البيئة للبريد والرسائل مع بقاء SQLite افتراضياً.

## 39 سجل التغييرات

الإصدار المسجّل في `config.py` هو 1.0.0. لا ملف سجل زمني (changelog) يعدد فروقات بين إصدارات. README السابق يصف نفس رقم الميزات العامة. فرق موثق بين ذلك النص و`requirements.txt`: Flask-WTF 1.1.1 هناك و1.2.1 هنا.

## System Overview

منصة دواء عربية متعددة الأدوار على Flask. المريض يدير الجرعات، والطبيب يرى مرضاه، والصيدلي يرد ويحدّث الطلبات، وحساب `user` يدير اللوحات المالية. التذكير والبريد والرسائل طبقات فوق القاعدة. التوصيات مصنف صغير محلي.

## Quick Reference

| البند | القيمة |
| --- | --- |
| تشغيل | `python app.py` |
| إنتاج | `gunicorn wsgi:app` |
| العنوان | `http://localhost:5000` |
| القاعدة | `doaei.db` |
| إصدار الإعداد | 1.0.0 |
| زرع init_db | كلمة 123456 |
| بريد الإدارة | admin@doaei.com |
| دور لوحة الإدارة | user |
| جلسة | 24 ساعة |

## Quick Start

```
pip install -r requirements.txt
python init_db.py
python app.py
```

ادخل بـ `admin@doaei.com` وكلمة `123456` للوحة الإدارة، أو بحساب مريض من رسائل `init_db.py`.

## For Non-Technical Users

بعد تشغيل البرنامج افتح الموقع في المتصفح. إذا كنت مريضاً أضف اسم الدواء وعدد المرات، وسيظهر تذكير داخل الموقع عندما يعمل البرنامج على الجهاز. الطبيب يرى المرضى المرتبطين به. الصيدلي يرد على الأسئلة ويحدّث حالة الطلب. هذه التوصيات الآلية تذكير تنظيمي داخل المشروع التعليمي، وليست بديلاً عن استشارة طبيب أو صيدلي بشري. احفظ نسخة من ملف قاعدة البيانات إن كانت بياناتك مهمة.

## For Developers

ابدأ من `create_app` و`models.py`. وحّد سياسة كلمة المرور بين `Config` و`forms.py` وسكربتات الزرع قبل أي عرض عام. أضف `schedule` إلى المتطلبات أو أزل الاعتماد. اربط التذكير بعملية gunicorn إن كان النشر عبر Procfile. لا تطبع `MAIL_PASSWORD` أو `SMS_API_KEY`. قدّم نموذج AI على حقيقته: 8 صفوف وستة أصناف.
