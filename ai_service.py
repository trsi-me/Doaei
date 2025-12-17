#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة الذكاء الاصطناعي - منصة دوائي
نظام توصيات ذكي مدرب للأدوية والصحة
"""

import numpy as np
from datetime import datetime, timedelta
from models import db, AIRecommendation, Medication, User, MedicationDose, Reminder
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os

class AIService:
    """خدمة الذكاء الاصطناعي للتوصيات الطبية"""
    
    def __init__(self):
        self.model_path = 'ai_models/recommendation_model.pkl'
        self.encoder_path = 'ai_models/label_encoder.pkl'
        self.model = None
        self.encoder = None
        self._load_or_train_model()
    
    def _load_or_train_model(self):
        """تحميل أو تدريب النموذج"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.encoder_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(self.encoder_path, 'rb') as f:
                    self.encoder = pickle.load(f)
            else:
                self._train_model()
        except Exception as e:
            print(f"خطأ في تحميل النموذج: {e}")
            self._train_model()
    
    def _train_model(self):
        """تدريب نموذج الذكاء الاصطناعي"""
        try:
            # إنشاء مجلد النماذج إذا لم يكن موجوداً
            os.makedirs('ai_models', exist_ok=True)
            
            # بيانات تدريب أساسية للتوصيات الدوائية
            # الميزات: [العمر، الجنس(0=ذكر,1=أنثى), عدد الأدوية الحالية، وجود أمراض مزمنة(0/1)]
            X_train = np.array([
                [25, 0, 1, 0],  # شاب، ذكر، دواء واحد، لا أمراض مزمنة
                [45, 1, 3, 1],  # امرأة، 3 أدوية، أمراض مزمنة
                [60, 0, 5, 1],  # رجل كبير، 5 أدوية، أمراض مزمنة
                [30, 1, 2, 0],  # امرأة شابة، دوائين، لا أمراض
                [70, 1, 4, 1],  # امرأة كبيرة، 4 أدوية، أمراض مزمنة
                [35, 0, 1, 0],  # رجل، دواء واحد، لا أمراض
                [50, 1, 3, 1],  # امرأة، 3 أدوية، أمراض مزمنة
                [28, 0, 2, 0],  # شاب، دوائين، لا أمراض
            ])
            
            # التصنيفات: نوع التوصية
            y_train = [
                'medication_timing',      # توقيت الأدوية
                'interaction_warning',    # تحذير من التفاعلات
                'adherence_support',      # دعم الالتزام
                'dosage_optimization',    # تحسين الجرعات
                'monitoring_required',    # مراقبة مطلوبة
                'lifestyle_advice',       # نصائح نمط الحياة
                'interaction_warning',    # تحذير من التفاعلات
                'medication_timing',      # توقيت الأدوية
            ]
            
            # تدريب المشفر
            self.encoder = LabelEncoder()
            y_encoded = self.encoder.fit_transform(y_train)
            
            # تدريب النموذج
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_encoded)
            
            # حفظ النموذج
            with open(self.model_path, 'wb') as f:
                pickle.dump(self.model, f)
            with open(self.encoder_path, 'wb') as f:
                pickle.dump(self.encoder, f)
                
            print("تم تدريب النموذج بنجاح")
            
        except Exception as e:
            print(f"خطأ في تدريب النموذج: {e}")
            # إنشاء نموذج افتراضي بسيط
            self.model = None
            self.encoder = None
    
    def generate_recommendation(self, user_id, symptoms='', medical_history='', 
                              current_medications='', age=None, gender=''):
        """إنشاء توصية ذكية للمستخدم"""
        try:
            user = User.query.get(user_id)
            if not user:
                return None
            
            # حساب العمر إذا لم يتم توفيره
            if age is None and user.date_of_birth:
                age = (datetime.now().date() - user.date_of_birth).days // 365
            elif age is None:
                age = 30  # افتراضي
            
            # تحديد الجنس
            gender_encoded = 1 if gender == 'female' or user.gender == 'female' else 0
            
            # عدد الأدوية الحالية
            medications_count = Medication.query.filter_by(
                user_id=user_id, is_active=True
            ).count()
            
            # وجود أمراض مزمنة
            has_chronic = 1 if (user.chronic_diseases and len(user.chronic_diseases) > 0) else 0
            
            # إنشاء ميزات للتنبؤ
            features = np.array([[age, gender_encoded, medications_count, has_chronic]])
            
            # التنبؤ بنوع التوصية
            recommendation_type = 'general_health'
            confidence_score = 0.75
            
            if self.model and self.encoder:
                try:
                    prediction = self.model.predict(features)
                    recommendation_type = self.encoder.inverse_transform(prediction)[0]
                    
                    # حساب درجة الثقة
                    probabilities = self.model.predict_proba(features)
                    confidence_score = float(np.max(probabilities))
                except Exception as e:
                    print(f"خطأ في التنبؤ: {e}")
            
            # إنشاء التوصية بناءً على النوع
            title, description, recommendations = self._generate_recommendation_content(
                recommendation_type, user, symptoms, medical_history, current_medications
            )
            
            # حفظ التوصية في قاعدة البيانات
            recommendation = AIRecommendation(
                user_id=user_id,
                recommendation_type=recommendation_type,
                title=title,
                description=description,
                recommendations=recommendations,
                confidence_score=confidence_score,
                input_data={
                    'symptoms': symptoms,
                    'medical_history': medical_history,
                    'current_medications': current_medications,
                    'age': age,
                    'gender': gender
                }
            )
            
            db.session.add(recommendation)
            db.session.commit()
            
            return recommendation
            
        except Exception as e:
            print(f"خطأ في إنشاء التوصية: {e}")
            db.session.rollback()
            return None
    
    def _generate_recommendation_content(self, rec_type, user, symptoms, 
                                        medical_history, current_medications):
        """إنشاء محتوى التوصية بناءً على النوع"""
        
        recommendations_map = {
            'medication_timing': {
                'title': 'توصيات حول توقيت تناول الأدوية',
                'description': 'نصائح لتحسين توقيت تناول أدويتك لزيادة الفعالية',
                'recommendations': [
                    'تناول الأدوية في نفس الوقت يومياً لضمان الالتزام',
                    'بعض الأدوية تكون أكثر فعالية عند تناولها في أوقات محددة',
                    'استخدم تطبيق دوائي لتذكيرك بمواعيد الأدوية',
                    'تجنب تناول أدوية متعددة في نفس الوقت دون استشارة الطبيب'
                ]
            },
            'interaction_warning': {
                'title': 'تحذير من التفاعلات الدوائية المحتملة',
                'description': 'تنبيه حول احتمالية وجود تفاعلات بين الأدوية الحالية',
                'recommendations': [
                    'استشر الصيدلي حول التفاعلات المحتملة بين أدويتك',
                    'لا تتناول أدوية جديدة دون إخبار طبيبك بالأدوية الحالية',
                    'احتفظ بقائمة محدثة بجميع الأدوية التي تتناولها',
                    'انتبه للأعراض غير المعتادة وأبلغ طبيبك فوراً'
                ]
            },
            'adherence_support': {
                'title': 'دعم الالتزام بالعلاج',
                'description': 'نصائح لمساعدتك على الالتزام بخطة العلاج',
                'recommendations': [
                    'استخدم صندوق أدوية منظم لتتبع الجرعات اليومية',
                    'اضبط تذكيرات متعددة على هاتفك',
                    'احتفظ بالأدوية في مكان مرئي تراه يومياً',
                    'اطلب دعم العائلة في تذكيرك بمواعيد الأدوية'
                ]
            },
            'dosage_optimization': {
                'title': 'تحسين الجرعات الدوائية',
                'description': 'توصيات لتحسين فعالية الجرعات',
                'recommendations': [
                    'تأكد من تناول الجرعة الكاملة الموصوفة',
                    'لا تقم بتعديل الجرعة دون استشارة الطبيب',
                    'سجل أي آثار جانبية لمناقشتها مع طبيبك',
                    'راجع طبيبك بانتظام لتقييم فعالية العلاج'
                ]
            },
            'monitoring_required': {
                'title': 'مراقبة صحية مطلوبة',
                'description': 'توصيات للمراقبة الصحية المنتظمة',
                'recommendations': [
                    'قم بإجراء الفحوصات الدورية الموصى بها',
                    'راقب الأعراض وسجلها في تطبيق دوائي',
                    'احتفظ بسجل لقياسات الضغط/السكر إن وجدت',
                    'لا تتردد في التواصل مع طبيبك عند ملاحظة تغييرات'
                ]
            },
            'lifestyle_advice': {
                'title': 'نصائح نمط الحياة الصحي',
                'description': 'توصيات لتحسين نمط حياتك الصحي',
                'recommendations': [
                    'اتبع نظاماً غذائياً متوازناً غنياً بالفواكه والخضروات',
                    'مارس الرياضة بانتظام حسب قدرتك الصحية',
                    'احصل على قسط كافٍ من النوم (7-8 ساعات)',
                    'قلل من التوتر من خلال تقنيات الاسترخاء'
                ]
            }
        }
        
        # الحصول على المحتوى المناسب
        content = recommendations_map.get(rec_type, recommendations_map['lifestyle_advice'])
        
        # تخصيص التوصيات بناءً على الأعراض
        if symptoms:
            content['recommendations'].insert(0, f'بناءً على الأعراض المذكورة ({symptoms})، ننصح باستشارة الطبيب')
        
        return content['title'], content['description'], '\n'.join(content['recommendations'])
    
    def get_ai_dashboard_data(self, user_id):
        """الحصول على بيانات لوحة تحكم الذكاء الاصطناعي"""
        try:
            # التوصيات الحديثة
            recommendations = AIRecommendation.query.filter_by(
                user_id=user_id
            ).order_by(AIRecommendation.created_at.desc()).limit(5).all()
            
            # إحصائيات
            total_recommendations = AIRecommendation.query.filter_by(user_id=user_id).count()
            accepted_recommendations = AIRecommendation.query.filter_by(
                user_id=user_id, status='accepted'
            ).count()
            
            # معدل الالتزام
            adherence_rate = self._calculate_adherence_rate(user_id)
            
            # اقتراحات التوقيت
            timing_suggestions = self._get_timing_suggestions(user_id)
            
            # رؤى صحية
            insights = self._generate_health_insights(user_id)
            
            return {
                'recommendations': recommendations,
                'stats': {
                    'total': total_recommendations,
                    'accepted': accepted_recommendations,
                    'acceptance_rate': (accepted_recommendations / total_recommendations * 100) if total_recommendations > 0 else 0,
                    'adherence_rate': adherence_rate
                },
                'timing_suggestions': timing_suggestions,
                'adherence': {
                    'rate': adherence_rate,
                    'trend': 'improving' if adherence_rate > 70 else 'needs_attention'
                },
                'insights': insights,
                'interactions': []
            }
            
        except Exception as e:
            print(f"خطأ في جلب بيانات لوحة التحكم: {e}")
            return {
                'recommendations': [],
                'stats': {'total': 0, 'accepted': 0, 'acceptance_rate': 0, 'adherence_rate': 0},
                'timing_suggestions': [],
                'adherence': {'rate': 0, 'trend': 'unknown'},
                'insights': [],
                'interactions': []
            }
    
    def _calculate_adherence_rate(self, user_id):
        """حساب معدل الالتزام بالأدوية"""
        try:
            # الحصول على جميع الجرعات في آخر 30 يوم
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            total_doses = MedicationDose.query.join(Medication).filter(
                Medication.user_id == user_id,
                MedicationDose.created_at >= thirty_days_ago
            ).count()
            
            taken_doses = MedicationDose.query.join(Medication).filter(
                Medication.user_id == user_id,
                MedicationDose.created_at >= thirty_days_ago,
                MedicationDose.is_taken == True
            ).count()
            
            if total_doses == 0:
                return 0
            
            return round((taken_doses / total_doses) * 100, 1)
            
        except Exception as e:
            print(f"خطأ في حساب معدل الالتزام: {e}")
            return 0
    
    def _get_timing_suggestions(self, user_id):
        """الحصول على اقتراحات التوقيت"""
        suggestions = []
        
        try:
            medications = Medication.query.filter_by(
                user_id=user_id, is_active=True
            ).all()
            
            for med in medications:
                if 'صباحاً' in med.frequency or 'morning' in med.frequency.lower():
                    suggestions.append({
                        'medication': med.name,
                        'suggestion': 'يفضل تناوله بين 7-9 صباحاً مع وجبة الإفطار',
                        'reason': 'لتحسين الامتصاص وتقليل الآثار الجانبية'
                    })
                elif 'مساءً' in med.frequency or 'evening' in med.frequency.lower():
                    suggestions.append({
                        'medication': med.name,
                        'suggestion': 'يفضل تناوله بين 7-9 مساءً مع وجبة العشاء',
                        'reason': 'للحفاظ على مستويات ثابتة في الدم'
                    })
            
        except Exception as e:
            print(f"خطأ في الحصول على اقتراحات التوقيت: {e}")
        
        return suggestions
    
    def _generate_health_insights(self, user_id):
        """إنشاء رؤى صحية"""
        insights = []
        
        try:
            user = User.query.get(user_id)
            medications_count = Medication.query.filter_by(
                user_id=user_id, is_active=True
            ).count()
            
            if medications_count > 3:
                insights.append({
                    'type': 'warning',
                    'title': 'تعدد الأدوية',
                    'message': f'تتناول حالياً {medications_count} أدوية. تأكد من مراجعة طبيبك بانتظام.',
                    'priority': 'high'
                })
            
            # التحقق من الالتزام
            adherence = self._calculate_adherence_rate(user_id)
            if adherence < 70:
                insights.append({
                    'type': 'alert',
                    'title': 'معدل التزام منخفض',
                    'message': f'معدل التزامك بالأدوية {adherence}%. حاول تحسينه للحصول على أفضل النتائج.',
                    'priority': 'high'
                })
            elif adherence > 90:
                insights.append({
                    'type': 'success',
                    'title': 'التزام ممتاز',
                    'message': f'معدل التزامك {adherence}%. استمر في هذا الأداء الرائع!',
                    'priority': 'low'
                })
            
            # نصائح عامة
            insights.append({
                'type': 'info',
                'title': 'نصيحة صحية',
                'message': 'احرص على شرب كمية كافية من الماء يومياً (8 أكواب على الأقل).',
                'priority': 'medium'
            })
            
        except Exception as e:
            print(f"خطأ في إنشاء الرؤى الصحية: {e}")
        
        return insights
    
    def update_recommendation_feedback(self, recommendation_id, is_accepted, feedback_score=None):
        """تحديث تقييم التوصية"""
        try:
            recommendation = AIRecommendation.query.get(recommendation_id)
            if not recommendation:
                return False
            
            if is_accepted:
                recommendation.status = 'accepted'
                recommendation.accepted_at = datetime.utcnow()
            else:
                recommendation.status = 'rejected'
                recommendation.rejected_at = datetime.utcnow()
            
            if feedback_score:
                recommendation.feedback_score = feedback_score
            
            db.session.commit()
            
            # تحديث النموذج بناءً على التغذية الراجعة (للتحسين المستقبلي)
            self._update_model_with_feedback(recommendation)
            
            return True
            
        except Exception as e:
            print(f"خطأ في تحديث التقييم: {e}")
            db.session.rollback()
            return False
    
    def _update_model_with_feedback(self, recommendation):
        """تحديث النموذج بناءً على التغذية الراجعة"""
        # يمكن تطوير هذه الدالة لاحقاً لإعادة تدريب النموذج
        pass
