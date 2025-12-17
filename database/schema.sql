-- منصة دوائي - مخطط قاعدة البيانات
-- إدارة الأدوية والتذكيرات الطبية

-- جدول المستخدمين
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'patient', -- patient, doctor, pharmacist, caregiver, user
    date_of_birth DATE,
    gender VARCHAR(10), -- male, female
    weight REAL, -- بالكيلوغرام
    height REAL, -- بالسنتيمتر
    chronic_diseases TEXT, -- أمراض مزمنة
    drug_allergies TEXT, -- حساسية أدوية
    emergency_contact_name VARCHAR(255),
    emergency_contact_phone VARCHAR(20),
    doctor_id INTEGER,
    blood_type VARCHAR(10), -- فصيلة الدم: A+, A-, B+, B-, AB+, AB-, O+, O-
    notification_preferences TEXT, -- JSON : {"email": true, "sms": true}
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (doctor_id) REFERENCES users (id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول الأدوية
CREATE TABLE medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    form VARCHAR(50) NOT NULL, -- حبوب، شراب، حقن، إلخ
    dosage VARCHAR(100) NOT NULL, -- الجرعة مثل 500mg
    frequency VARCHAR(100) NOT NULL, -- تكرار الجرعات
    duration_days INTEGER, -- مدة العلاج بالأيام
    start_date DATE NOT NULL,
    end_date DATE,
    quantity INTEGER, -- عدد الحبوب/الكمية في العلبة
    notes TEXT, -- ملاحظات المريض
    doctor_notes TEXT, -- ملاحظات الطبيب
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- جدول الجرعات المحددة
CREATE TABLE medication_doses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_id INTEGER NOT NULL,
    scheduled_time TIME NOT NULL,
    day_of_week INTEGER, -- 0=الأحد، 1=الاثنين، إلخ (NULL للجرعات اليومية)
    is_taken BOOLEAN DEFAULT 0,
    taken_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medication_id) REFERENCES medications (id)
);

-- جدول التذكيرات
CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_dose_id INTEGER NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    notification_type VARCHAR(20) NOT NULL, -- email, sms, in_app
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed
    sent_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (medication_dose_id) REFERENCES medication_doses (id)
);

-- جدول مشاركة السجلات
CREATE TABLE shared_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    shared_with_user_id INTEGER NOT NULL,
    permission_type VARCHAR(20) NOT NULL, -- read_only, read_write
    medication_id INTEGER, -- NULL لمشاركة جميع الأدوية
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users (id),
    FOREIGN KEY (shared_with_user_id) REFERENCES users (id),
    FOREIGN KEY (medication_id) REFERENCES medications (id)
);

-- جدول استشارات الصيدلي
CREATE TABLE consultations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    pharmacist_id INTEGER,
    subject VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    attachment_path VARCHAR(500), -- مسار الملف المرفق
    status VARCHAR(20) DEFAULT 'pending', -- pending, replied, closed
    reply TEXT,
    replied_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users (id),
    FOREIGN KEY (pharmacist_id) REFERENCES users (id)
);

-- جدول تقييمات المنتجات
CREATE TABLE product_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    is_verified BOOLEAN DEFAULT 0, -- تم التحقق من التقييم
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- جدول التقارير
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255),
    report_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    doctor_name VARCHAR(255),
    summary TEXT,
    status VARCHAR(20) DEFAULT 'completed',
    file_path VARCHAR(500),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- جدول سجلات التدقيق
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    table_name VARCHAR(100),
    record_id INTEGER,
    old_values TEXT, -- JSON
    new_values TEXT, -- JSON
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- جدول إعدادات النظام
CREATE TABLE system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- إدراج الإعدادات الافتراضية
INSERT INTO system_settings (key, value, description) VALUES ('app_name', 'دوائي', 'اسم التطبيق');
INSERT INTO system_settings (key, value, description) VALUES ('app_version', '1.0.0', 'إصدار التطبيق');
INSERT INTO system_settings (key, value, description) VALUES ('reminder_advance_minutes', '10', 'دقائق قبل موعد الجرعة لإرسال التذكير');
INSERT INTO system_settings (key, value, description) VALUES ('max_upload_size', '16777216', 'الحد الأقصى لحجم الملف المرفق بالبايت');
INSERT INTO system_settings (key, value, description) VALUES ('sms_enabled', '1', 'تفعيل إرسال الرسائل النصية');
INSERT INTO system_settings (key, value, description) VALUES ('email_enabled', '1', 'تفعيل إرسال البريد الإلكتروني');

-- جدول الصيدليات
CREATE TABLE pharmacies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    license_number VARCHAR(100),
    owner_name VARCHAR(255),
    city VARCHAR(100),
    district VARCHAR(100),
    latitude REAL,
    longitude REAL,
    delivery_radius INTEGER DEFAULT 10,
    delivery_fee REAL DEFAULT 0,
    min_order_amount REAL DEFAULT 0,
    working_hours TEXT,
    is_active BOOLEAN DEFAULT 1,
    rating REAL DEFAULT 0,
    total_orders INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول منتجات الصيدليات
CREATE TABLE pharmacy_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pharmacy_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    manufacturer VARCHAR(255),
    form VARCHAR(50),
    strength VARCHAR(100),
    description TEXT,
    price REAL,
    stock_quantity INTEGER DEFAULT 0,
    min_stock_level INTEGER DEFAULT 10,
    requires_prescription BOOLEAN DEFAULT 0,
    category VARCHAR(100),
    side_effects TEXT,
    contraindications TEXT,
    dosage_instructions TEXT,
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id)
);

-- جدول الطلبات
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,
    pharmacy_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_method VARCHAR(50),
    subtotal REAL NOT NULL,
    delivery_fee REAL DEFAULT 0,
    tax_amount REAL DEFAULT 0,
    total_amount REAL NOT NULL,
    delivery_address TEXT NOT NULL,
    delivery_phone VARCHAR(20) NOT NULL,
    delivery_notes TEXT,
    prescription_image VARCHAR(500),
    estimated_delivery_time TIMESTAMP,
    actual_delivery_time TIMESTAMP,
    delivery_person_name VARCHAR(255),
    delivery_person_phone VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id)
);

-- جدول عناصر الطلبات
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total_price REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES pharmacy_products (id)
);

-- جدول تتبع الطلبات
CREATE TABLE order_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders (id)
);

-- جدول توصيات الذكاء الاصطناعي
CREATE TABLE ai_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    recommendation_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    confidence_score REAL,
    is_read BOOLEAN DEFAULT 0,
    feedback VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- جدول المراجعات
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pharmacy_id INTEGER,
    product_id INTEGER,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    comment TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (pharmacy_id) REFERENCES pharmacies (id),
    FOREIGN KEY (product_id) REFERENCES pharmacy_products (id)
);

-- إنشاء الفهارس لتحسين الأداء
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_medications_user_id ON medications(user_id);
CREATE INDEX idx_medications_active ON medications(is_active);
CREATE INDEX idx_medication_doses_medication_id ON medication_doses(medication_id);
CREATE INDEX idx_reminders_time ON reminders(reminder_time);
CREATE INDEX idx_reminders_status ON reminders(status);
CREATE INDEX idx_consultations_patient_id ON consultations(patient_id);
CREATE INDEX idx_consultations_status ON consultations(status);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);

-- جدول التقييمات الطبية
CREATE TABLE evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    evaluation_date DATE NOT NULL,
    evaluation_type VARCHAR(50) NOT NULL, -- routine, follow_up, emergency, consultation
    symptoms TEXT,
    diagnosis TEXT,
    vital_signs TEXT, -- JSON: {"blood_pressure": "120/80", "temperature": "37", "heart_rate": "72"}
    physical_examination TEXT,
    lab_results TEXT,
    recommendations TEXT,
    prescribed_medications TEXT, -- JSON array of medication IDs
    next_visit_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users (id),
    FOREIGN KEY (doctor_id) REFERENCES users (id)
);

-- إنشاء فهرس للتقييمات
CREATE INDEX idx_evaluations_patient_id ON evaluations(patient_id);
CREATE INDEX idx_evaluations_doctor_id ON evaluations(doctor_id);
CREATE INDEX idx_evaluations_date ON evaluations(evaluation_date);

-- جدول المواعيد
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    appointment_type VARCHAR(50) NOT NULL, -- routine, follow_up, emergency, consultation
    status VARCHAR(20) DEFAULT 'scheduled', -- scheduled, confirmed, completed, cancelled, rescheduled
    reason TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES users (id),
    FOREIGN KEY (doctor_id) REFERENCES users (id)
);

-- إنشاء فهرس للمواعيد
CREATE INDEX idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);