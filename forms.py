#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# منصة دوائي - النماذج (Forms)
# إدارة الأدوية والتذكيرات الطبية

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField, TimeField, IntegerField, DecimalField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, NumberRange, ValidationError
from wtforms.widgets import TextArea
import re

class LoginForm(FlaskForm):
    # نموذج تسجيل الدخول
    email = StringField('البريد الإلكتروني', validators=[DataRequired()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember_me = BooleanField('تذكرني')

class RegisterForm(FlaskForm):
    # نموذج التسجيل
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password')])
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=2, max=255)])
    phone = StringField('رقم الجوال', validators=[Optional()])
    role = SelectField('نوع المستخدم', choices=[
        ('patient', 'مريض'),
        ('doctor', 'طبيب'),
        ('pharmacist', 'صيدلي')
    ], default='patient', validators=[DataRequired()])
    agree_terms = BooleanField('أوافق على شروط الاستخدام', validators=[DataRequired()])

class PatientProfileForm(FlaskForm):
    # نموذج ملف المريض
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(min=2, max=255)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    phone = StringField('رقم الهاتف', validators=[Optional()])
    date_of_birth = DateField('تاريخ الميلاد', validators=[Optional()])
    gender = SelectField('الجنس', choices=[
        ('', 'اختر الجنس'),
        ('male', 'ذكر'),
        ('female', 'أنثى')
    ], validators=[Optional()])
    role = SelectField('نوع الحساب', choices=[
        ('user', 'مستخدم عادي'),
        ('user', 'مستخدم')
    ], validators=[Optional()])
    weight = DecimalField('الوزن (كيلوغرام)', validators=[Optional(), NumberRange(min=10, max=300)])
    height = DecimalField('الطول (سنتيمتر)', validators=[Optional(), NumberRange(min=50, max=250)])
    chronic_diseases = TextAreaField('الأمراض المزمنة', validators=[Optional()])
    drug_allergies = TextAreaField('حساسية الأدوية', validators=[Optional()])
    emergency_contact_name = StringField('اسم جهة الاتصال للطوارئ', validators=[Optional()])
    emergency_contact_phone = StringField('رقم جهة الاتصال للطوارئ', validators=[Optional()])
    doctor_id = SelectField('الطبيب المعالج', choices=[], validators=[Optional()], coerce=int)
    blood_type = SelectField('فصيلة الدم', choices=[
        ('', 'غير محدد'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-')
    ], validators=[Optional()])
    # حقول العنوان
    address = TextAreaField('العنوان التفصيلي', validators=[Optional()])
    city = StringField('المدينة', validators=[Optional(), Length(max=100)])
    postal_code = StringField('الرمز البريدي', validators=[Optional(), Length(max=20)])
    # حقول طبية إضافية
    medical_conditions = TextAreaField('الحالات الطبية', validators=[Optional()])
    allergies = TextAreaField('الحساسيات', validators=[Optional()])
    emergency_contact = StringField('جهة الاتصال في الطوارئ', validators=[Optional()])
    # إعدادات
    language = SelectField('اللغة المفضلة', choices=[
        ('ar', 'العربية'),
        ('en', 'English')
    ], validators=[Optional()], default='ar')
    timezone = SelectField('المنطقة الزمنية', choices=[
        ('Asia/Riyadh', 'الرياض (GMT+3)'),
        ('Asia/Dubai', 'دبي (GMT+4)'),
        ('Africa/Cairo', 'القاهرة (GMT+2)'),
        ('UTC', 'UTC (GMT+0)')
    ], validators=[Optional()], default='Asia/Riyadh')
    email_notifications = BooleanField('الإشعارات عبر البريد الإلكتروني', default=True)
    sms_notifications = BooleanField('الإشعارات عبر الرسائل النصية', default=False)

class MedicationForm(FlaskForm):
    # نموذج إضافة/تعديل دواء
    name = StringField('اسم الدواء', validators=[DataRequired(), Length(min=2, max=255)])
    form = SelectField('شكل الدواء', choices=[
        ('حبوب', 'حبوب'),
        ('شراب', 'شراب'),
        ('حقن', 'حقن'),
        ('مرهم', 'مرهم'),
        ('قطرة', 'قطرة'),
        ('بخاخ', 'بخاخ'),
        ('أخرى', 'أخرى')
    ], validators=[DataRequired()])
    dosage = StringField('الجرعة', validators=[DataRequired(), Length(min=1, max=100)])
    frequency = SelectField('تكرار الجرعات', choices=[
        ('مرة واحدة يومياً', 'مرة واحدة يومياً'),
        ('مرتين يومياً', 'مرتين يومياً'),
        ('ثلاث مرات يومياً', 'ثلاث مرات يومياً'),
        ('أربع مرات يومياً', 'أربع مرات يومياً'),
        ('كل 6 ساعات', 'كل 6 ساعات'),
        ('كل 8 ساعات', 'كل 8 ساعات'),
        ('كل 12 ساعة', 'كل 12 ساعة'),
        ('حسب الحاجة', 'حسب الحاجة'),
        ('أخرى', 'أخرى')
    ], validators=[DataRequired()])
    custom_frequency = StringField('تكرار مخصص', validators=[Optional()])
    duration_days = IntegerField('مدة العلاج (أيام)', validators=[Optional(), NumberRange(min=1, max=3650)])
    start_date = DateField('تاريخ البدء', validators=[Optional()])
    quantity = IntegerField('الكمية المتوفرة', validators=[Optional(), NumberRange(min=1)])
    notes = TextAreaField('ملاحظات المريض', validators=[Optional()])
    doctor_notes = TextAreaField('ملاحظات الطبيب', validators=[Optional()])
    time_of_day = SelectField('وقت التناول', choices=[
        ('صباحاً', 'صباحاً'),
        ('ظهراً', 'ظهراً'),
        ('مساءً', 'مساءً'),
        ('قبل النوم', 'قبل النوم'),
        ('مع الطعام', 'مع الطعام'),
        ('على معدة فارغة', 'على معدة فارغة'),
        ('حسب الحاجة', 'حسب الحاجة')
    ], validators=[DataRequired()])
    duration = StringField('مدة العلاج', validators=[DataRequired()])
    instructions = TextAreaField('تعليمات خاصة', validators=[Optional()])
    prescription_image = FileField('صورة الوصفة الطبية', validators=[Optional()])
    enable_reminders = BooleanField('تفعيل التذكيرات', default=True)
    reminder_method = SelectField('طريقة التذكير', choices=[
        ('email', 'البريد الإلكتروني'),
        ('sms', 'الرسائل النصية'),
        ('whatsapp', 'واتساب'),
        ('push', 'الإشعارات')
    ], default='email')

class MedicationDoseForm(FlaskForm):
    """نموذج إضافة جرعة محددة"""
    medication_id = IntegerField('معرف الدواء', validators=[DataRequired()])
    scheduled_time = TimeField('وقت الجرعة', validators=[DataRequired()])
    day_of_week = SelectField('يوم الأسبوع', choices=[
        (None, 'يومياً'),
        (0, 'الأحد'),
        (1, 'الاثنين'),
        (2, 'الثلاثاء'),
        (3, 'الأربعاء'),
        (4, 'الخميس'),
        (5, 'الجمعة'),
        (6, 'السبت')
    ], validators=[Optional()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])

class ConsultationForm(FlaskForm):
    """نموذج استشارة الصيدلي"""
    consultation_type = SelectField('نوع الاستشارة', choices=[
        ('medication_advice', 'نصيحة دوائية'),
        ('drug_interaction', 'تفاعل دوائي'),
        ('dosage_question', 'سؤال عن الجرعة'),
        ('side_effects', 'آثار جانبية'),
        ('general_health', 'صحة عامة'),
        ('other', 'أخرى')
    ], validators=[DataRequired()])
    subject = StringField('موضوع الاستشارة', validators=[DataRequired(), Length(min=5, max=255)])
    description = TextAreaField('وصف المشكلة', validators=[DataRequired(), Length(min=10)])
    current_medications = TextAreaField('الأدوية الحالية', validators=[Optional()])
    allergies = TextAreaField('الحساسيات', validators=[Optional()])
    medical_history = TextAreaField('التاريخ الطبي', validators=[Optional()])
    urgency = SelectField('مستوى الإلحاح', choices=[
        ('low', 'منخفض'),
        ('medium', 'متوسط'),
        ('high', 'عالي')
    ], default='medium')
    preferred_contact_method = SelectField('طريقة التواصل المفضلة', choices=[
        ('email', 'البريد الإلكتروني'),
        ('sms', 'الرسائل النصية'),
        ('whatsapp', 'واتساب'),
        ('phone', 'الهاتف')
    ], default='email')
    attachment = FileField('مرفق (اختياري)', validators=[Optional()])
    agree_terms = BooleanField('أوافق على أن هذه الاستشارة لا تحل محل زيارة الطبيب المباشرة', validators=[DataRequired()])
    emergency_acknowledgment = BooleanField('أؤكد أن هذه ليست حالة طوارئ طبية', validators=[DataRequired()])

class ConsultationReplyForm(FlaskForm):
    """نموذج رد على الاستشارة"""
    reply = TextAreaField('الرد', validators=[DataRequired(), Length(min=10)])

class ProductRatingForm(FlaskForm):
    """نموذج تقييم المنتج"""
    product_name = StringField('اسم المنتج', validators=[DataRequired(), Length(min=2, max=255)])
    rating = SelectField('التقييم', choices=[
        (1, '⭐ (1)'),
        (2, '⭐⭐ (2)'),
        (3, '⭐⭐⭐ (3)'),
        (4, '⭐⭐⭐⭐ (4)'),
        (5, '⭐⭐⭐⭐⭐ (5)')
    ], validators=[DataRequired()])
    review = TextAreaField('التعليق', validators=[Optional()])
    manufacturer = StringField('الشركة المصنعة', validators=[Optional()])
    effectiveness = SelectField('فعالية الدواء', choices=[
        ('ممتاز', 'ممتاز'),
        ('جيد', 'جيد'),
        ('متوسط', 'متوسط'),
        ('ضعيف', 'ضعيف')
    ], validators=[Optional()])
    side_effects = TextAreaField('الآثار الجانبية', validators=[Optional()])
    duration_of_use = StringField('مدة الاستخدام', validators=[Optional()])
    would_recommend = BooleanField('أنصح الآخرين بهذا الدواء', default=False)
    prescription_required = BooleanField('يتطلب وصفة طبية', default=False)

class NotificationSettingsForm(FlaskForm):
    """نموذج إعدادات الإشعارات"""
    email_notifications = BooleanField('الإشعارات عبر البريد الإلكتروني', default=True)
    sms_notifications = BooleanField('الإشعارات عبر الرسائل النصية', default=False)
    email_reminders = BooleanField('تذكيرات الأدوية عبر البريد الإلكتروني')
    email_reports = BooleanField('التقارير الدورية عبر البريد الإلكتروني')
    email_consultations = BooleanField('تحديثات الاستشارات عبر البريد الإلكتروني')
    email_orders = BooleanField('تحديثات الطلبات عبر البريد الإلكتروني')
    sms_reminders = BooleanField('تذكيرات الأدوية عبر الرسائل النصية')
    sms_consultations = BooleanField('تحديثات الاستشارات عبر الرسائل النصية')
    sms_orders = BooleanField('تحديثات الطلبات عبر الرسائل النصية')
    whatsapp_reminders = BooleanField('تذكيرات الأدوية عبر واتساب')
    whatsapp_consultations = BooleanField('تحديثات الاستشارات عبر واتساب')
    whatsapp_orders = BooleanField('تحديثات الطلبات عبر واتساب')
    reminder_advance_minutes = IntegerField('دقائق قبل موعد الجرعة', validators=[NumberRange(min=0, max=60)])

class PrivacySettingsForm(FlaskForm):
    """نموذج إعدادات الخصوصية"""
    share_medical_info = BooleanField('مشاركة المعلومات الطبية')
    share_medications = BooleanField('مشاركة قائمة الأدوية')
    share_medical_history = BooleanField('مشاركة التاريخ الطبي')
    share_with_family = BooleanField('مشاركة مع أفراد العائلة')
    share_with_caregivers = BooleanField('مشاركة مع مقدمي الرعاية')
    share_for_research = BooleanField('مشاركة البيانات للبحث')
    reminder_notifications = BooleanField('إشعارات التذكير')
    consultation_notifications = BooleanField('إشعارات الاستشارات')
    order_notifications = BooleanField('إشعارات الطلبات')
    local_data_storage = BooleanField('حفظ البيانات محلياً')
    data_encryption = BooleanField('تشفير البيانات')
    auto_delete_data = BooleanField('حذف البيانات التلقائي')

class ReportForm(FlaskForm):
    """نموذج إنشاء تقرير"""
    title = StringField('عنوان التقرير', validators=[DataRequired(), Length(min=5, max=255)])
    report_type = SelectField('نوع التقرير', choices=[
        ('medication_adherence', 'التزام الأدوية'),
        ('health_summary', 'ملخص صحي'),
        ('doctor_report', 'تقرير للطبيب'),
        ('monthly_summary', 'ملخص شهري')
    ], validators=[DataRequired()])
    start_date = DateField('تاريخ البداية', validators=[DataRequired()])
    end_date = DateField('تاريخ النهاية', validators=[DataRequired()])
    doctor_name = StringField('اسم الطبيب', validators=[Optional()])
    summary = TextAreaField('ملخص التقرير', validators=[Optional()])

class ShareRecordForm(FlaskForm):
    """نموذج مشاركة السجل"""
    shared_with_email = StringField('بريد المستخدم للمشاركة', validators=[DataRequired(), Email()])
    permission_type = SelectField('نوع الصلاحية', choices=[
        ('read_only', 'قراءة فقط'),
        ('read_write', 'قراءة وكتابة')
    ], validators=[DataRequired()])
    medication_id = SelectField('الدواء (اختياري)', choices=[], validators=[Optional()])

class ChangePasswordForm(FlaskForm):
    """نموذج تغيير كلمة المرور"""
    current_password = PasswordField('كلمة المرور الحالية', validators=[DataRequired()])
    new_password = PasswordField('كلمة المرور الجديدة', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('تأكيد كلمة المرور الجديدة', validators=[DataRequired(), EqualTo('new_password')])

def validate_phone(form, field):
    """التحقق من صحة رقم الهاتف"""
    if field.data:
        # إزالة المسافات والرموز الخاصة
        phone = re.sub(r'[^\d+]', '', field.data)
        # التحقق من أن الرقم يبدأ بـ + أو رقم
        if not re.match(r'^\+?[1-9]\d{7,14}$', phone):
            raise ValidationError('رقم الهاتف غير صحيح')

def validate_saudi_phone(form, field):
    """التحقق من صحة رقم الهاتف السعودي"""
    if field.data:
        phone = re.sub(r'[^\d+]', '', field.data)
        # التحقق من أن الرقم سعودي
        if not re.match(r'^(\+966|966|0)?[5][0-9]{8}$', phone):
            raise ValidationError('رقم الهاتف السعودي غير صحيح')

# ===== نماذج الطلبات والتوصيل =====

class PharmacyForm(FlaskForm):
    """نموذج إضافة/تعديل صيدلية"""
    name = StringField('اسم الصيدلية', validators=[DataRequired(), Length(min=2, max=255)])
    address = TextAreaField('العنوان', validators=[DataRequired()])
    phone = StringField('رقم الهاتف', validators=[DataRequired(), validate_phone])
    email = StringField('البريد الإلكتروني', validators=[Optional(), Email()])
    license_number = StringField('رقم الترخيص', validators=[DataRequired(), Length(min=5, max=100)])
    owner_name = StringField('اسم المالك', validators=[DataRequired(), Length(min=2, max=255)])
    city = SelectField('المدينة', choices=[
        ('الرياض', 'الرياض'),
        ('جدة', 'جدة'),
        ('مكة المكرمة', 'مكة المكرمة'),
        ('المدينة المنورة', 'المدينة المنورة'),
        ('الدمام', 'الدمام'),
        ('الخبر', 'الخبر'),
        ('الطائف', 'الطائف'),
        ('بريدة', 'بريدة'),
        ('تبوك', 'تبوك'),
        ('خميس مشيط', 'خميس مشيط'),
        ('حائل', 'حائل'),
        ('نجران', 'نجران'),
        ('الجبيل', 'الجبيل'),
        ('ينبع', 'ينبع'),
        ('أخرى', 'أخرى')
    ], validators=[DataRequired()])
    district = StringField('الحي', validators=[Optional(), Length(min=2, max=100)])
    latitude = DecimalField('خط العرض', validators=[Optional(), NumberRange(min=-90, max=90)])
    longitude = DecimalField('خط الطول', validators=[Optional(), NumberRange(min=-180, max=180)])
    delivery_radius = IntegerField('نطاق التوصيل (كم)', validators=[Optional(), NumberRange(min=1, max=50)], default=10)
    delivery_fee = DecimalField('رسوم التوصيل', validators=[Optional(), NumberRange(min=0)], default=0)
    min_order_amount = DecimalField('الحد الأدنى للطلب', validators=[Optional(), NumberRange(min=0)], default=0)
    working_hours = StringField('ساعات العمل', validators=[Optional()])
    rating = DecimalField('التقييم', validators=[Optional(), NumberRange(min=0, max=5)], default=0)
    is_active = BooleanField('نشط', default=True)
    
    # إضافة الحقول المفقودة من HTML
    description = TextAreaField('وصف الصيدلية', validators=[Optional()])
    postal_code = StringField('الرمز البريدي', validators=[Optional()])
    working_hours_weekdays = StringField('ساعات العمل (السبت - الخميس)', validators=[Optional()])
    working_hours_friday = StringField('ساعات العمل (الجمعة)', validators=[Optional()])
    is_24_hours = BooleanField('صيدلية 24 ساعة', default=False)
    delivery_available = BooleanField('خدمة التوصيل', default=True)
    consultation_available = BooleanField('الاستشارات الطبية', default=True)
    emergency_service = BooleanField('خدمة الطوارئ', default=False)
    online_ordering = BooleanField('الطلب الإلكتروني', default=True)
    prescription_services = BooleanField('خدمات الوصفات الطبية', default=True)
    health_products = BooleanField('المنتجات الصحية', default=True)
    logo = FileField('شعار الصيدلية', validators=[Optional()])
    license_document = FileField('وثيقة الترخيص', validators=[Optional()])
    manager_name = StringField('اسم المدير', validators=[Optional()])
    manager_phone = StringField('هاتف المدير', validators=[Optional()])
    manager_email = StringField('بريد المدير الإلكتروني', validators=[Optional(), Email()])

class PharmacyProductForm(FlaskForm):
    """نموذج إضافة/تعديل منتج صيدلية"""
    pharmacy_id = SelectField('الصيدلية', validators=[DataRequired()], coerce=int)
    name = StringField('اسم المنتج', validators=[DataRequired(), Length(min=2, max=255)])
    generic_name = StringField('الاسم العلمي', validators=[Optional(), Length(min=2, max=255)])
    manufacturer = StringField('الشركة المصنعة', validators=[Optional(), Length(min=2, max=255)])
    form = SelectField('الشكل الدوائي', choices=[
        ('tablet', 'أقراص'),
        ('capsule', 'كبسولات'),
        ('syrup', 'شراب'),
        ('injection', 'حقن'),
        ('cream', 'كريم'),
        ('ointment', 'مرهم'),
        ('drops', 'قطرات'),
        ('spray', 'بخاخ'),
        ('patch', 'لصقة'),
        ('suppository', 'تحاميل')
    ], validators=[DataRequired()])
    strength = StringField('القوة', validators=[Optional(), Length(min=1, max=100)])
    description = TextAreaField('الوصف', validators=[Optional()])
    price = DecimalField('السعر', validators=[DataRequired(), NumberRange(min=0.01)])
    stock_quantity = IntegerField('الكمية المتوفرة', validators=[DataRequired(), NumberRange(min=0)], default=0)
    is_prescription_required = BooleanField('يتطلب وصفة طبية', default=False)
    is_active = BooleanField('نشط', default=True)
    category = SelectField('الفئة', choices=[
        ('prescription', 'وصفة طبية'),
        ('otc', 'بدون وصفة'),
        ('supplement', 'مكمل غذائي'),
        ('medical_device', 'جهاز طبي'),
        ('other', 'أخرى')
    ], validators=[DataRequired()])
    side_effects = TextAreaField('الآثار الجانبية', validators=[Optional()])
    contraindications = TextAreaField('موانع الاستخدام', validators=[Optional()])
    dosage_instructions = TextAreaField('تعليمات الاستخدام', validators=[Optional()])

class OrderForm(FlaskForm):
    """نموذج إنشاء طلب"""
    pharmacy_id = SelectField('الصيدلية', validators=[DataRequired()], coerce=int)
    delivery_address = TextAreaField('عنوان التوصيل', validators=[DataRequired(), Length(min=10)])
    delivery_phone = StringField('رقم هاتف التوصيل', validators=[DataRequired(), validate_phone])
    delivery_date = DateField('تاريخ التوصيل المفضل', validators=[DataRequired()])
    delivery_time = SelectField('وقت التوصيل المفضل', choices=[
        ('morning', 'صباحاً (8-12)'),
        ('afternoon', 'ظهراً (12-16)'),
        ('evening', 'مساءً (16-20)'),
        ('anytime', 'أي وقت')
    ], validators=[DataRequired()])
    delivery_notes = TextAreaField('ملاحظات التوصيل', validators=[Optional()])
    payment_method = SelectField('طريقة الدفع', choices=[
        ('cash', 'الدفع عند الاستلام'),
        ('card', 'بطاقة ائتمان'),
        ('online', 'دفع إلكتروني')
    ], validators=[DataRequired()])
    prescription_image = FileField('صورة الوصفة الطبية', validators=[Optional()])

class OrderItemForm(FlaskForm):
    """نموذج عنصر الطلب"""
    product_id = SelectField('المنتج', validators=[DataRequired()], coerce=int)
    quantity = IntegerField('الكمية', validators=[DataRequired(), NumberRange(min=1, max=100)], default=1)
    notes = TextAreaField('ملاحظات', validators=[Optional()])

class OrderStatusUpdateForm(FlaskForm):
    """نموذج تحديث حالة الطلب"""
    status = SelectField('الحالة الجديدة', choices=[
        ('pending', 'في الانتظار'),
        ('confirmed', 'مؤكد'),
        ('preparing', 'قيد التحضير'),
        ('ready', 'جاهز للتوصيل'),
        ('out_for_delivery', 'في الطريق'),
        ('delivered', 'تم التوصيل'),
        ('cancelled', 'ملغي')
    ], validators=[DataRequired()])
    notes = TextAreaField('ملاحظات', validators=[Optional()])

class DeliveryAssignmentForm(FlaskForm):
    """نموذج تعيين شخص التوصيل"""
    delivery_person_name = StringField('اسم شخص التوصيل', validators=[DataRequired(), Length(min=2, max=255)])
    delivery_person_phone = StringField('رقم هاتف شخص التوصيل', validators=[DataRequired(), validate_phone])

class OrderTrackingForm(FlaskForm):
    """نموذج تتبع الطلب"""
    order_number = StringField('رقم الطلب', validators=[DataRequired(), Length(min=10, max=50)])

class AIRecommendationFeedbackForm(FlaskForm):
    """نموذج تقييم التوصيات"""
    is_accepted = BooleanField('هل قبلت هذه التوصية؟')
    feedback_score = SelectField('تقييم التوصية', choices=[
        (1, '⭐ (1)'),
        (2, '⭐⭐ (2)'),
        (3, '⭐⭐⭐ (3)'),
        (4, '⭐⭐⭐⭐ (4)'),
        (5, '⭐⭐⭐⭐⭐ (5)')
    ], validators=[Optional()], coerce=int)
    feedback_notes = TextAreaField('ملاحظات إضافية', validators=[Optional()])

class SearchForm(FlaskForm):
    """نموذج البحث"""
    query = StringField('البحث', validators=[DataRequired(), Length(min=2, max=100)])
    category = SelectField('الفئة', choices=[
        ('', 'جميع الفئات'),
        ('pain_relief', 'مسكنات الألم'),
        ('antibiotics', 'مضادات حيوية'),
        ('vitamins', 'فيتامينات'),
        ('supplements', 'مكملات غذائية'),
        ('chronic_disease', 'أمراض مزمنة'),
        ('respiratory', 'جهاز تنفسي'),
        ('cardiovascular', 'قلب وأوعية دموية'),
        ('digestive', 'جهاز هضمي'),
        ('skin_care', 'العناية بالبشرة'),
        ('baby_care', 'العناية بالأطفال'),
        ('first_aid', 'إسعافات أولية'),
        ('other', 'أخرى')
    ], validators=[Optional()])
    min_price = DecimalField('الحد الأدنى للسعر', validators=[Optional(), NumberRange(min=0)])
    max_price = DecimalField('الحد الأقصى للسعر', validators=[Optional(), NumberRange(min=0)])
    pharmacy_id = SelectField('الصيدلية', validators=[Optional()], coerce=int)
    requires_prescription = BooleanField('يتطلب وصفة طبية فقط')

class FilterForm(FlaskForm):
    """نموذج الفلترة"""
    sort_by = SelectField('ترتيب حسب', choices=[
        ('name', 'الاسم'),
        ('price_asc', 'السعر (من الأقل للأعلى)'),
        ('price_desc', 'السعر (من الأعلى للأقل)'),
        ('rating', 'التقييم'),
        ('popularity', 'الشعبية')
    ], default='name')
    in_stock_only = BooleanField('متوفر فقط')
    pharmacy_open = BooleanField('صيدليات مفتوحة فقط')