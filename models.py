#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# منصة دوائي - النماذج (Models)
# إدارة الأدوية والتذكيرات الطبية

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date, time
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    # نموذج المستخدم
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='patient')
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    chronic_diseases = db.Column(db.Text)
    drug_allergies = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(255))
    emergency_contact_phone = db.Column(db.String(20))
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    blood_type = db.Column(db.String(10))  # فصيلة الدم: A+, A-, B+, B-, AB+, AB-, O+, O-
    notification_preferences = db.Column(db.Text)  # JSON
    # حقول العنوان
    address = db.Column(db.Text)  # العنوان التفصيلي
    city = db.Column(db.String(100))  # المدينة
    postal_code = db.Column(db.String(20))  # الرمز البريدي
    # حقول طبية إضافية
    medical_conditions = db.Column(db.Text)  # الحالات الطبية
    allergies = db.Column(db.Text)  # الحساسيات
    emergency_contact = db.Column(db.String(255))  # جهة الاتصال في الطوارئ
    # إعدادات
    language = db.Column(db.String(10), default='ar')  # اللغة المفضلة
    timezone = db.Column(db.String(50), default='Asia/Riyadh')  # المنطقة الزمنية
    email_notifications = db.Column(db.Boolean, default=True)  # الإشعارات عبر البريد الإلكتروني
    sms_notifications = db.Column(db.Boolean, default=False)  # الإشعارات عبر الرسائل النصية
    last_login = db.Column(db.DateTime)  # آخر تسجيل دخول
    avatar_url = db.Column(db.String(500))  # رابط صورة الملف الشخصي
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    medications = db.relationship('Medication', backref='user', lazy=True, cascade='all, delete-orphan')
    consultations_as_patient = db.relationship('Consultation', foreign_keys='Consultation.patient_id', lazy=True, overlaps="patient_consultations")
    consultations_as_pharmacist = db.relationship('Consultation', foreign_keys='Consultation.pharmacist_id', lazy=True, overlaps="pharmacist_consultations")
    product_ratings = db.relationship('ProductRating', backref='user', lazy=True)
    reports = db.relationship('Report', backref='user', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    doctor = db.relationship('User', remote_side=[id], foreign_keys=[doctor_id], backref='patients')
    
    def get_notification_preferences(self):
        # الحصول على إعدادات الإشعارات
        if self.notification_preferences:
            return json.loads(self.notification_preferences)
        return {'email': True, 'sms': True}
    
    def set_notification_preferences(self, preferences):
        # تعيين إعدادات الإشعارات
        self.notification_preferences = json.dumps(preferences)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Medication(db.Model):
    # نموذج الدواء
    __tablename__ = 'medications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    form = db.Column(db.String(50), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)
    duration_days = db.Column(db.Integer)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    quantity = db.Column(db.Integer)
    notes = db.Column(db.Text)
    doctor_notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    doses = db.relationship('MedicationDose', backref='medication', lazy=True, cascade='all, delete-orphan')
    shared_records = db.relationship('SharedRecord', backref='medication', lazy=True)
    
    def calculate_end_date(self):
        # حساب تاريخ الانتهاء
        if self.duration_days and self.start_date:
            from datetime import timedelta
            self.end_date = self.start_date + timedelta(days=self.duration_days)
    
    def get_remaining_days(self):
        # الحصول على الأيام المتبقية
        if self.end_date:
            remaining = (self.end_date - date.today()).days
            return max(0, remaining)
        return None
    
    def __repr__(self):
        return f'<Medication {self.name}>'

class MedicationDose(db.Model):
    """نموذج الجرعة المحددة"""
    __tablename__ = 'medication_doses'
    
    id = db.Column(db.Integer, primary_key=True)
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'), nullable=False)
    scheduled_time = db.Column(db.Time, nullable=False)
    day_of_week = db.Column(db.Integer)  # 0=الأحد، 1=الاثنين، إلخ
    is_taken = db.Column(db.Boolean, default=False)
    taken_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    reminders = db.relationship('Reminder', backref='medication_dose', lazy=True, cascade='all, delete-orphan')
    
    def get_day_name(self):
        """الحصول على اسم اليوم"""
        days = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
        if self.day_of_week is not None:
            return days[self.day_of_week]
        return 'يومياً'
    
    def __repr__(self):
        return f'<MedicationDose {self.scheduled_time}>'

class Reminder(db.Model):
    """نموذج التذكير"""
    __tablename__ = 'reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    medication_dose_id = db.Column(db.Integer, db.ForeignKey('medication_doses.id'), nullable=False)
    reminder_time = db.Column(db.DateTime, nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # email, sms, in_app
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed
    sent_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Reminder {self.reminder_time}>'

class SharedRecord(db.Model):
    """نموذج السجلات المشتركة"""
    __tablename__ = 'shared_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_type = db.Column(db.String(20), nullable=False)  # read_only, read_write
    medication_id = db.Column(db.Integer, db.ForeignKey('medications.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    patient = db.relationship('User', foreign_keys=[patient_id], backref='shared_records_as_patient')
    shared_with_user = db.relationship('User', foreign_keys=[shared_with_user_id], backref='shared_records_as_shared')
    
    def __repr__(self):
        return f'<SharedRecord {self.patient_id} -> {self.shared_with_user_id}>'

class Consultation(db.Model):
    """نموذج الاستشارة"""
    __tablename__ = 'consultations'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    pharmacist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(500))
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, closed
    reply = db.Column(db.Text)
    replied_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_consultations', overlaps="consultations_as_patient")
    pharmacist = db.relationship('User', foreign_keys=[pharmacist_id], backref='pharmacist_consultations', overlaps="consultations_as_pharmacist")
    
    def __repr__(self):
        return f'<Consultation {self.subject} by {self.patient_id}>'

class ProductRating(db.Model):
    """نموذج تقييم المنتج"""
    __tablename__ = 'product_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductRating {self.product_name}: {self.rating} stars>'

class Report(db.Model):
    """نموذج التقرير"""
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # weekly, monthly, custom
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    file_path = db.Column(db.String(500))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Report {self.report_type} {self.start_date} - {self.end_date}>'

class AuditLog(db.Model):
    """نموذج سجل التدقيق"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    table_name = db.Column(db.String(100))
    record_id = db.Column(db.Integer)
    old_values = db.Column(db.Text)  # JSON
    new_values = db.Column(db.Text)  # JSON
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action} by {self.user_id}>'

class SystemSetting(db.Model):
    """نموذج إعدادات النظام"""
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_setting(key, default=None):
        """الحصول على إعداد"""
        setting = SystemSetting.query.filter_by(key=key).first()
        return setting.value if setting else default
    
    @staticmethod
    def set_setting(key, value, description=None):
        """تعيين إعداد"""
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SystemSetting(key=key, value=value, description=description)
            db.session.add(setting)
        db.session.commit()
    
    def __repr__(self):
        return f'<SystemSetting {self.key}: {self.value}>'

# ===== نماذج الصيدليات والطلبات =====

class Pharmacy(db.Model):
    """نموذج الصيدلية"""
    __tablename__ = 'pharmacies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(255))
    license_number = db.Column(db.String(100), unique=True)
    owner_name = db.Column(db.String(255))
    city = db.Column(db.String(100))
    district = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    delivery_radius = db.Column(db.Integer, default=10)  # بالكيلومتر
    delivery_fee = db.Column(db.Float, default=0)
    min_order_amount = db.Column(db.Float, default=0)
    working_hours = db.Column(db.Text)  # JSON
    is_active = db.Column(db.Boolean, default=True)
    rating = db.Column(db.Float, default=0)
    total_orders = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    products = db.relationship('PharmacyProduct', backref='pharmacy', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='pharmacy', lazy=True)
    
    def get_working_hours(self):
        """الحصول على ساعات العمل"""
        if self.working_hours:
            return json.loads(self.working_hours)
        return {}
    
    def set_working_hours(self, hours):
        """تعيين ساعات العمل"""
        self.working_hours = json.dumps(hours)
    
    def is_open_now(self):
        """التحقق من أن الصيدلية مفتوحة الآن"""
        now = datetime.now()
        current_day = now.strftime('%A').lower()
        current_time = now.time()
        
        hours = self.get_working_hours()
        if current_day in hours:
            day_hours = hours[current_day]
            if day_hours['is_open']:
                open_time = datetime.strptime(day_hours['open'], '%H:%M').time()
                close_time = datetime.strptime(day_hours['close'], '%H:%M').time()
                return open_time <= current_time <= close_time
        return False
    
    def __repr__(self):
        return f'<Pharmacy {self.name}>'

class PharmacyProduct(db.Model):
    """نموذج منتجات الصيدلية"""
    __tablename__ = 'pharmacy_products'
    
    id = db.Column(db.Integer, primary_key=True)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    generic_name = db.Column(db.String(255))
    manufacturer = db.Column(db.String(255))
    form = db.Column(db.String(50))  # tablet, capsule, syrup, etc.
    strength = db.Column(db.String(100))  # 500mg, 10ml, etc.
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=5)
    requires_prescription = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(100))  # pain relief, antibiotics, etc.
    side_effects = db.Column(db.Text)
    contraindications = db.Column(db.Text)
    dosage_instructions = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    order_items = db.relationship('OrderItem', backref='pharmacy_product', lazy=True)
    
    def is_in_stock(self):
        """التحقق من توفر المنتج"""
        return self.stock_quantity > 0
    
    def is_low_stock(self):
        """التحقق من انخفاض المخزون"""
        return self.stock_quantity <= self.min_stock_level
    
    def __repr__(self):
        return f'<PharmacyProduct {self.name}>'

class Order(db.Model):
    """نموذج الطلب"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, preparing, ready, out_for_delivery, delivered, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, failed, refunded
    payment_method = db.Column(db.String(50))  # cash, card, online
    subtotal = db.Column(db.Float, nullable=False)
    delivery_fee = db.Column(db.Float, default=0)
    tax_amount = db.Column(db.Float, default=0)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_phone = db.Column(db.String(20), nullable=False)
    delivery_notes = db.Column(db.Text)
    prescription_image = db.Column(db.String(500))
    estimated_delivery_time = db.Column(db.DateTime)
    actual_delivery_time = db.Column(db.DateTime)
    delivery_person_name = db.Column(db.String(255))
    delivery_person_phone = db.Column(db.String(20))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    tracking = db.relationship('OrderTracking', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def get_status_arabic(self):
        """الحصول على حالة الطلب بالعربية"""
        status_map = {
            'pending': 'في الانتظار',
            'confirmed': 'مؤكد',
            'preparing': 'قيد التحضير',
            'ready': 'جاهز للتوصيل',
            'out_for_delivery': 'في الطريق',
            'delivered': 'تم التوصيل',
            'cancelled': 'ملغي'
        }
        return status_map.get(self.status, self.status)
    
    def calculate_total(self):
        """حساب المجموع الكلي"""
        self.total_amount = self.subtotal + self.delivery_fee + self.tax_amount
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """نموذج عناصر الطلب"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    pharmacy_product_id = db.Column(db.Integer, db.ForeignKey('pharmacy_products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_total(self):
        """حساب المجموع"""
        self.total_price = self.quantity * self.unit_price
    
    def __repr__(self):
        return f'<OrderItem {self.quantity}x {self.pharmacy_product.name}>'

class OrderTracking(db.Model):
    """نموذج تتبع الطلب"""
    __tablename__ = 'order_tracking'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.String(100))  # system, pharmacy, delivery_person
    
    def __repr__(self):
        return f'<OrderTracking {self.status} at {self.timestamp}>'

class AIRecommendation(db.Model):
    """نموذج توصيات الذكاء الاصطناعي"""
    __tablename__ = 'ai_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recommendation_type = db.Column(db.String(50), nullable=False)  # medication, pharmacy, dosage, lifestyle
    recommended_item_id = db.Column(db.Integer)
    recommended_item_type = db.Column(db.String(50))
    confidence_score = db.Column(db.Float, default=0.0)  # 0.00 to 1.00
    reason = db.Column(db.Text)
    algorithm_version = db.Column(db.String(20))
    is_accepted = db.Column(db.Boolean, default=False)
    feedback_score = db.Column(db.Integer)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='ai_recommendations')
    
    def __repr__(self):
        return f'<AIRecommendation {self.recommendation_type} for user {self.user_id}>'

# ===== نماذج إضافية =====

class Review(db.Model):
    """نموذج المراجعات"""
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('pharmacy_products.id'), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # تقييم للطبيب
    pharmacist_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # تقييم للصيدلي
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    title = db.Column(db.String(255))
    comment = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', foreign_keys=[user_id], backref='reviews')
    pharmacy = db.relationship('Pharmacy', backref='reviews')
    product = db.relationship('PharmacyProduct', backref='reviews')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_reviews')
    pharmacist = db.relationship('User', foreign_keys=[pharmacist_id], backref='pharmacist_reviews')
    
    def __repr__(self):
        return f'<Review {self.rating} stars by {self.user_id}>'

class Evaluation(db.Model):
    """نموذج التقييم الطبي"""
    __tablename__ = 'evaluations'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    evaluation_date = db.Column(db.Date, nullable=False)
    evaluation_type = db.Column(db.String(50), nullable=False)  # routine, follow_up, emergency, consultation
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    vital_signs = db.Column(db.Text)  # JSON
    physical_examination = db.Column(db.Text)
    lab_results = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    prescribed_medications = db.Column(db.Text)  # JSON array
    next_visit_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    patient = db.relationship('User', foreign_keys=[patient_id], backref='patient_evaluations')
    doctor = db.relationship('User', foreign_keys=[doctor_id], backref='doctor_evaluations')
    
    def get_vital_signs(self):
        """الحصول على العلامات الحيوية"""
        if self.vital_signs:
            return json.loads(self.vital_signs)
        return {}
    
    def set_vital_signs(self, vital_signs):
        """تعيين العلامات الحيوية"""
        self.vital_signs = json.dumps(vital_signs)
    
    def get_prescribed_medications(self):
        """الحصول على الأدوية الموصوفة"""
        if self.prescribed_medications:
            return json.loads(self.prescribed_medications)
        return []
    
    def set_prescribed_medications(self, medications):
        """تعيين الأدوية الموصوفة"""
        self.prescribed_medications = json.dumps(medications)
    
    def __repr__(self):
        return f'<Evaluation {self.evaluation_type} for patient {self.patient_id} by doctor {self.doctor_id}>'

class Income(db.Model):
    """نموذج الدخل"""
    __tablename__ = 'incomes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))  # sales, subscriptions, services, etc.
    source = db.Column(db.String(255))  # مصدر الدخل
    transaction_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50))  # cash, bank_transfer, card, etc.
    reference_number = db.Column(db.String(100))  # رقم المرجع
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_incomes')
    
    def __repr__(self):
        return f'<Income {self.title}: {self.amount}>'

class Expense(db.Model):
    """نموذج المصروفات"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100))  # salaries, rent, utilities, supplies, marketing, etc.
    vendor = db.Column(db.String(255))  # المورد
    transaction_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.String(50))  # cash, bank_transfer, card, etc.
    reference_number = db.Column(db.String(100))  # رقم المرجع
    receipt_url = db.Column(db.String(500))  # رابط الفاتورة
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_expenses')
    
    def __repr__(self):
        return f'<Expense {self.title}: {self.amount}>'

class Department(db.Model):
    """نموذج الأقسام"""
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    budget = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    manager = db.relationship('User', foreign_keys=[manager_id], backref='managed_departments')
    employees = db.relationship('Employee', backref='department', lazy=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Employee(db.Model):
    """نموذج الموظفين"""
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    employee_number = db.Column(db.String(50), unique=True, nullable=False)
    position = db.Column(db.String(255), nullable=False)  # المسمى الوظيفي
    hire_date = db.Column(db.Date, nullable=False)
    salary = db.Column(db.Float, default=0.0)
    employment_type = db.Column(db.String(50), default='full_time')  # full_time, part_time, contract
    status = db.Column(db.String(50), default='active')  # active, on_leave, terminated
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    phone_extension = db.Column(db.String(20))
    office_location = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='employee_profile')
    manager = db.relationship('User', foreign_keys=[manager_id], backref='managed_employees')
    
    def __repr__(self):
        return f'<Employee {self.employee_number}: {self.position}>'

class Notification(db.Model):
    # نموذج الإشعار
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')  # info, warning, success, error, medication, appointment, system
    is_read = db.Column(db.Boolean, default=False)
    scheduled_time = db.Column(db.DateTime)  # وقت الجدولة
    sent_at = db.Column(db.DateTime)  # وقت الإرسال الفعلي
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title} for user {self.user_id}>'