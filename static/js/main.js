// منصة دوائي - ملف JavaScript الرئيسي

document.addEventListener('DOMContentLoaded', function () {
    // تهيئة التطبيق
    initializeApp();

    // إعداد القوائم المنسدلة
    setupDropdowns();

    // إعداد النماذج التفاعلية
    setupInteractiveForms();

    // إعداد الإشعارات
    setupNotifications();

    // إعداد التذكيرات
    setupReminders();
});

function initializeApp() {
    console.log('تم تحميل منصة دوائي بنجاح');

    // إضافة تأثيرات الحركة للعناصر
    addScrollAnimations();

    // إعداد القوائم المحمولة
    setupMobileMenu();

    // إعداد التمرير السلس
    setupSmoothScrolling();
}

function setupDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');

    dropdowns.forEach(dropdown => {
        const button = dropdown.querySelector('.dropdown-btn');
        const content = dropdown.querySelector('.dropdown-content');

        if (button && content) {
            button.addEventListener('click', function (e) {
                e.stopPropagation();
                toggleDropdown(dropdown);
            });
        }
    });

    // إغلاق القوائم المنسدلة عند النقر خارجها
    document.addEventListener('click', function () {
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    });
}

function toggleDropdown(dropdown) {
    const isActive = dropdown.classList.contains('active');

    // إغلاق جميع القوائم المنسدلة الأخرى
    document.querySelectorAll('.dropdown').forEach(d => {
        d.classList.remove('active');
    });

    // تبديل القائمة الحالية
    if (!isActive) {
        dropdown.classList.add('active');
    }
}

function setupInteractiveForms() {
    // إضافة تأثيرات للعناصر التفاعلية
    const inputs = document.querySelectorAll('.form-input, .form-select');

    inputs.forEach(input => {
        // تأثير التركيز
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function () {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });

        // التحقق من صحة البيانات أثناء الكتابة
        input.addEventListener('input', function () {
            validateInput(this);
        });
    });

    // إعداد أزرار التحميل
    setupLoadingButtons();
}

function validateInput(input) {
    const value = input.value.trim();
    const type = input.type;
    const name = input.name;

    // إزالة رسائل الخطأ السابقة
    removeErrorMessages(input);

    // التحقق من البريد الإلكتروني
    if (type === 'email' || name === 'email') {
        if (value && !isValidEmail(value)) {
            showInputError(input, 'البريد الإلكتروني غير صحيح');
        }
    }

    // التحقق من رقم الهاتف
    if (name === 'phone') {
        if (value && !isValidSaudiPhone(value)) {
            showInputError(input, 'رقم الهاتف السعودي غير صحيح (يجب أن يبدأ بـ 05)');
        }
    }

    // التحقق من كلمة المرور
    if (name === 'password') {
        updatePasswordStrength(input);
    }

    // التحقق من تطابق كلمة المرور
    if (name === 'confirm_password') {
        const passwordInput = document.querySelector('input[name="password"]');
        if (passwordInput && value !== passwordInput.value) {
            showInputError(input, 'كلمة المرور غير متطابقة');
        }
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidSaudiPhone(phone) {
    const cleanPhone = phone.replace(/[^\d+]/g, '');
    const saudiPhoneRegex = /^(\+966|966|0)?[5][0-9]{8}$/;
    return saudiPhoneRegex.test(cleanPhone);
}

function showInputError(input, message) {
    input.classList.add('invalid');

    const errorDiv = document.createElement('div');
    errorDiv.className = 'input-error error';
    errorDiv.textContent = message;

    input.parentElement.appendChild(errorDiv);
}

function removeErrorMessages(input) {
    input.classList.remove('invalid');
    const errorDiv = input.parentElement.querySelector('.input-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

function updatePasswordStrength(input) {
    const strengthBar = document.querySelector('.strength-fill');
    const strengthText = document.querySelector('.strength-text');

    if (!strengthBar || !strengthText) return;

    const password = input.value;
    const strength = calculatePasswordStrength(password);

    strengthBar.style.width = strength.percentage + '%';
    strengthBar.className = 'strength-fill ' + strength.class;
    strengthText.textContent = strength.text;
}

function calculatePasswordStrength(password) {
    let score = 0;
    let feedback = [];

    if (password.length >= 6) score += 1;
    else feedback.push('6 أحرف على الأقل');

    if (password.length >= 8) score += 1;

    if (/[a-z]/.test(password)) score += 1;
    else feedback.push('حرف صغير');

    if (/[A-Z]/.test(password)) score += 1;
    else feedback.push('حرف كبير');

    if (/[0-9]/.test(password)) score += 1;
    else feedback.push('رقم');

    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    else feedback.push('رمز خاص');

    if (score <= 2) {
        return {
            percentage: 25,
            class: 'weak',
            text: 'ضعيفة - أضف: ' + feedback.join(', ')
        };
    } else if (score <= 4) {
        return {
            percentage: 60,
            class: 'medium',
            text: 'متوسطة - أضف: ' + feedback.join(', ')
        };
    } else {
        return {
            percentage: 100,
            class: 'strong',
            text: 'قوية جداً'
        };
    }
}

function setupLoadingButtons() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                showButtonLoading(submitBtn);
            }
        });
    });
}

function showButtonLoading(button) {
    const originalText = button.textContent;
    button.textContent = 'جاري المعالجة...';
    button.disabled = true;

    // إعادة تعيين الزر بعد 5 ثوانٍ كحد أقصى
    setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
    }, 5000);
}

function setupNotifications() {
    // طلب إذن الإشعارات
    if ('Notification' in window) {
        Notification.requestPermission();
    }

    // إعداد إشعارات التطبيق
    setupAppNotifications();

    // إعداد رسائل التنبيه التلقائية
    setupFlashMessages();
}

function setupFlashMessages() {
    // البحث عن جميع رسائل التنبيه الموجودة
    const flashMessages = document.querySelectorAll('.flash-message');

    flashMessages.forEach(message => {
        // إضافة تأثير التلاشي التلقائي بعد 5 ثوانٍ
        setTimeout(() => {
            message.classList.add('fade-out');
            setTimeout(() => {
                if (message.parentElement) {
                    message.remove();
                }
            }, 500);
        }, 5000);

        // إضافة مستمع للنقر على زر الإغلاق
        const closeBtn = message.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function () {
                message.classList.add('fade-out');
                setTimeout(() => {
                    if (message.parentElement) {
                        message.remove();
                    }
                }, 500);
            });
        }
    });
}

function setupAppNotifications() {
    // إضافة زر الإشعارات إذا كان متوفراً
    if ('serviceWorker' in navigator && 'PushManager' in window) {
        registerServiceWorker();
    }
}

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('تم تسجيل Service Worker بنجاح:', registration.scope);
            })
            .catch(error => {
                console.log('فشل في تسجيل Service Worker:', error);
            });
    }
}

// التحقق من تسجيل الدخول
function isLoggedIn() {
    // التحقق من وجود عنصر يظهر أن المستخدم مسجل الدخول
    const userMenu = document.querySelector('.user-menu');
    const loginLink = document.querySelector('a[href*="login"]');

    return userMenu && !loginLink;
}

function setupReminders() {
    // التحقق من التذكيرات كل دقيقة
    setInterval(checkReminders, 60000);

    // التحقق من التذكيرات عند تحميل الصفحة
    checkReminders();
}

function checkReminders() {
    // التحقق من تسجيل الدخول أولاً
    if (!isLoggedIn()) {
        console.log('المستخدم غير مسجل الدخول - تخطي فحص التذكيرات');
        return;
    }

    // جلب التذكيرات من الخادم
    fetch('/api/reminders', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(reminders => {
            if (Array.isArray(reminders)) {
                reminders.forEach(reminder => {
                    if (reminder.status === 'pending') {
                        showReminderNotification(reminder);
                    }
                });
            }
        })
        .catch(error => {
            console.error('خطأ في جلب التذكيرات:', error);
            // عدم إظهار رسائل خطأ للمستخدم في حالة عدم تسجيل الدخول
            if (error.message.includes('401') || error.message.includes('403')) {
                console.log('المستخدم غير مخول - تخطي التذكيرات');
            }
        });
}

function showReminderNotification(reminder) {
    // إظهار إشعار التطبيق
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification('تذكير دواء - دوائي', {
            body: `حان وقت تناول ${reminder.medication_name} - الجرعة: ${reminder.dosage}`,
            icon: '/static/images/icon.png',
            tag: 'medication-reminder'
        });

        notification.onclick = function () {
            window.focus();
            notification.close();
        };
    }

    // إظهار إشعار داخل التطبيق
    showInAppNotification(reminder);
}

function showInAppNotification(reminder) {
    const notificationDiv = document.createElement('div');
    notificationDiv.className = 'in-app-notification';
    notificationDiv.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">💊</div>
            <div class="notification-text">
                <strong>تذكير دواء</strong>
                <p>حان وقت تناول ${reminder.medication_name}</p>
            </div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    document.body.appendChild(notificationDiv);

    // إضافة تأثير الظهور
    setTimeout(() => {
        notificationDiv.classList.add('show');
    }, 100);

    // إزالة الإشعار تلقائياً بعد 8 ثوانٍ مع تأثير التلاشي
    setTimeout(() => {
        notificationDiv.classList.add('fade-out');
        setTimeout(() => {
            if (notificationDiv.parentElement) {
                notificationDiv.remove();
            }
        }, 500);
    }, 8000);
}

function setupMobileMenu() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
            mobileToggle.classList.toggle('active');
        });
    }
}

function setupSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');

    links.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();

            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);

            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function addScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // مراقبة العناصر القابلة للتحريك
    const animatedElements = document.querySelectorAll('.feature-card, .testimonial-card, .stat-item');
    animatedElements.forEach(element => {
        observer.observe(element);
    });
}

// دوال مساعدة عامة
function formatDate(date) {
    const options = {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        calendar: 'islamic'
    };
    return new Intl.DateTimeFormat('ar-SA', options).format(new Date(date));
}

function formatTime(time) {
    const options = {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    };
    return new Intl.DateTimeFormat('ar-SA', options).format(new Date(`2000-01-01T${time}`));
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // إضافة تأثير الظهور
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // إزالة التوست بعد 3 ثوانٍ
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 300);
    }, 3000);
}

function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// دوال خاصة بإدارة الأدوية
function markDoseAsTaken(doseId) {
    fetch(`/api/take-dose/${doseId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('تم تسجيل تناول الجرعة بنجاح', 'success');
                // تحديث واجهة المستخدم
                updateDoseStatus(doseId);
            } else {
                showToast('حدث خطأ في تسجيل الجرعة', 'error');
            }
        })
        .catch(error => {
            console.error('خطأ:', error);
            showToast('حدث خطأ في الاتصال', 'error');
        });
}

function updateDoseStatus(doseId) {
    const doseElement = document.querySelector(`[data-dose-id="${doseId}"]`);
    if (doseElement) {
        doseElement.classList.add('taken');
        doseElement.querySelector('.dose-status').textContent = 'تم التناول';
    }
}

// دوال خاصة بالتقارير
function generateReport(type, startDate, endDate) {
    const formData = new FormData();
    formData.append('report_type', type);
    formData.append('start_date', startDate);
    formData.append('end_date', endDate);

    fetch('/reports/generate', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            throw new Error('فشل في إنشاء التقرير');
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `report_${type}_${startDate}_${endDate}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showToast('تم إنشاء التقرير بنجاح', 'success');
        })
        .catch(error => {
            console.error('خطأ:', error);
            showToast('حدث خطأ في إنشاء التقرير', 'error');
        });
}

// تصدير الدوال للاستخدام العام
window.DoaeiApp = {
    markDoseAsTaken,
    generateReport,
    showToast,
    confirmAction,
    formatDate,
    formatTime
};
