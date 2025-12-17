#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
منصة دوائي - نظام إدارة الطلبات والتوصيل
إدارة طلبات الأدوية والتوصيل للمنازل
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from flask import current_app
from models import db, User, Order, OrderItem, OrderTracking, Pharmacy, PharmacyProduct, AIRecommendation
from utils import NotificationService, AuditLogger

class OrderManagementSystem:
    """نظام إدارة الطلبات"""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def create_order(self, user_id: int, pharmacy_id: int, items: List[Dict], 
                    delivery_address: str, delivery_phone: str, 
                    payment_method: str = 'cash', prescription_image: str = None,
                    delivery_notes: str = None) -> Tuple[bool, str, Optional[Order]]:
        """إنشاء طلب جديد"""
        try:
            # التحقق من صحة البيانات
            user = User.query.get(user_id)
            pharmacy = Pharmacy.query.get(pharmacy_id)
            
            if not user:
                return False, "المستخدم غير موجود", None
            
            if not pharmacy:
                return False, "الصيدلية غير موجودة", None
            
            if not pharmacy.is_active:
                return False, "الصيدلية غير متاحة حالياً", None
            
            if not pharmacy.is_open_now():
                return False, "الصيدلية مغلقة حالياً", None
            
            # إنشاء رقم الطلب
            order_number = self._generate_order_number()
            
            # حساب المجموع
            subtotal = 0
            order_items = []
            
            for item in items:
                product = PharmacyProduct.query.get(item['product_id'])
                if not product:
                    return False, f"المنتج {item['product_id']} غير موجود", None
                
                if not product.is_in_stock():
                    return False, f"المنتج {product.name} غير متوفر", None
                
                if item['quantity'] > product.stock_quantity:
                    return False, f"الكمية المطلوبة من {product.name} غير متوفرة", None
                
                # حساب السعر
                item_total = item['quantity'] * float(product.price)
                subtotal += item_total
                
                order_items.append({
                    'product': product,
                    'quantity': item['quantity'],
                    'unit_price': float(product.price),
                    'total_price': item_total
                })
            
            # حساب رسوم التوصيل والضرائب
            delivery_fee = float(pharmacy.delivery_fee)
            tax_rate = 0.15  # 15% ضريبة القيمة المضافة
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + delivery_fee + tax_amount
            
            # التحقق من الحد الأدنى للطلب
            if subtotal < float(pharmacy.min_order_amount):
                return False, f"الحد الأدنى للطلب {pharmacy.min_order_amount} ريال", None
            
            # إنشاء الطلب
            order = Order(
                order_number=order_number,
                user_id=user_id,
                pharmacy_id=pharmacy_id,
                status='pending',
                payment_status='pending',
                payment_method=payment_method,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                tax_amount=tax_amount,
                total_amount=total_amount,
                delivery_address=delivery_address,
                delivery_phone=delivery_phone,
                delivery_notes=delivery_notes,
                prescription_image=prescription_image,
                estimated_delivery_time=self._calculate_estimated_delivery_time(pharmacy)
            )
            
            db.session.add(order)
            db.session.flush()  # للحصول على ID الطلب
            
            # إضافة عناصر الطلب
            for item_data in order_items:
                order_item = OrderItem(
                    order_id=order.id,
                    pharmacy_product_id=item_data['product'].id,
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price']
                )
                db.session.add(order_item)
                
                # تحديث المخزون
                item_data['product'].stock_quantity -= item_data['quantity']
            
            # إضافة تتبع الطلب
            tracking = OrderTracking(
                order_id=order.id,
                status='تم إنشاء الطلب',
                description='تم إنشاء الطلب بنجاح وانتظار التأكيد من الصيدلية',
                updated_by='system'
            )
            db.session.add(tracking)
            
            # تحديث إحصائيات الصيدلية
            pharmacy.total_orders += 1
            
            db.session.commit()
            
            # إرسال إشعارات
            self._send_order_notifications(order)
            
            # تسجيل في سجل التدقيق
            AuditLogger.log_action(user_id, 'create_order', 'orders', order.id)
            
            return True, "تم إنشاء الطلب بنجاح", order
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إنشاء الطلب: {e}")
            db.session.rollback()
            return False, f"خطأ في إنشاء الطلب: {str(e)}", None
    
    def update_order_status(self, order_id: int, new_status: str, 
                           updated_by: str, notes: str = None) -> Tuple[bool, str]:
        """تحديث حالة الطلب"""
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, "الطلب غير موجود"
            
            old_status = order.status
            order.status = new_status
            order.updated_at = datetime.utcnow()
            
            # إضافة تتبع جديد
            tracking = OrderTracking(
                order_id=order_id,
                status=self._get_status_description(new_status),
                description=notes or f"تم تحديث حالة الطلب من {old_status} إلى {new_status}",
                updated_by=updated_by
            )
            db.session.add(tracking)
            
            db.session.commit()
            
            # إرسال إشعارات للمستخدم
            self._send_status_update_notification(order)
            
            # تسجيل في سجل التدقيق
            AuditLogger.log_action(
                order.user_id, 
                'update_order_status', 
                'orders', 
                order_id,
                {'old_status': old_status, 'new_status': new_status}
            )
            
            return True, "تم تحديث حالة الطلب بنجاح"
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تحديث حالة الطلب: {e}")
            db.session.rollback()
            return False, f"خطأ في تحديث حالة الطلب: {str(e)}"
    
    def cancel_order(self, order_id: int, reason: str, cancelled_by: str) -> Tuple[bool, str]:
        """إلغاء الطلب"""
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, "الطلب غير موجود"
            
            if order.status in ['delivered', 'cancelled']:
                return False, "لا يمكن إلغاء هذا الطلب"
            
            # إرجاع الكميات للمخزون
            for item in order.items:
                product = item.pharmacy_product
                product.stock_quantity += item.quantity
            
            # تحديث حالة الطلب
            order.status = 'cancelled'
            order.updated_at = datetime.utcnow()
            
            # إضافة تتبع الإلغاء
            tracking = OrderTracking(
                order_id=order_id,
                status='تم إلغاء الطلب',
                description=f"تم إلغاء الطلب. السبب: {reason}",
                updated_by=cancelled_by
            )
            db.session.add(tracking)
            
            db.session.commit()
            
            # إرسال إشعار الإلغاء
            self._send_cancellation_notification(order, reason)
            
            return True, "تم إلغاء الطلب بنجاح"
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إلغاء الطلب: {e}")
            db.session.rollback()
            return False, f"خطأ في إلغاء الطلب: {str(e)}"
    
    def get_user_orders(self, user_id: int, status: str = None, limit: int = 20) -> List[Order]:
        """الحصول على طلبات المستخدم"""
        query = Order.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Order.created_at.desc()).limit(limit).all()
    
    def get_pharmacy_orders(self, pharmacy_id: int, status: str = None, limit: int = 50) -> List[Order]:
        """الحصول على طلبات الصيدلية"""
        query = Order.query.filter_by(pharmacy_id=pharmacy_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Order.created_at.desc()).limit(limit).all()
    
    def get_order_details(self, order_id: int) -> Optional[Order]:
        """الحصول على تفاصيل الطلب"""
        return Order.query.get(order_id)
    
    def get_order_tracking(self, order_id: int) -> List[OrderTracking]:
        """الحصول على تتبع الطلب"""
        return OrderTracking.query.filter_by(order_id=order_id).order_by(OrderTracking.timestamp.desc()).all()
    
    def assign_delivery_person(self, order_id: int, delivery_person_name: str, 
                             delivery_person_phone: str) -> Tuple[bool, str]:
        """تعيين شخص التوصيل"""
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, "الطلب غير موجود"
            
            if order.status != 'ready':
                return False, "الطلب غير جاهز للتوصيل"
            
            order.delivery_person_name = delivery_person_name
            order.delivery_person_phone = delivery_person_phone
            order.status = 'out_for_delivery'
            order.updated_at = datetime.utcnow()
            
            # إضافة تتبع التوصيل
            tracking = OrderTracking(
                order_id=order_id,
                status='تم تعيين شخص التوصيل',
                description=f"تم تعيين {delivery_person_name} لتوصيل الطلب",
                updated_by='pharmacy'
            )
            db.session.add(tracking)
            
            db.session.commit()
            
            # إرسال إشعار للمستخدم
            self._send_delivery_assignment_notification(order)
            
            return True, "تم تعيين شخص التوصيل بنجاح"
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تعيين شخص التوصيل: {e}")
            db.session.rollback()
            return False, f"خطأ في تعيين شخص التوصيل: {str(e)}"
    
    def mark_order_delivered(self, order_id: int, delivery_person_name: str) -> Tuple[bool, str]:
        """تسجيل تسليم الطلب"""
        try:
            order = Order.query.get(order_id)
            if not order:
                return False, "الطلب غير موجود"
            
            if order.status != 'out_for_delivery':
                return False, "الطلب غير في حالة التوصيل"
            
            order.status = 'delivered'
            order.actual_delivery_time = datetime.utcnow()
            order.updated_at = datetime.utcnow()
            
            # إضافة تتبع التسليم
            tracking = OrderTracking(
                order_id=order_id,
                status='تم تسليم الطلب',
                description=f"تم تسليم الطلب بنجاح بواسطة {delivery_person_name}",
                updated_by='delivery_person'
            )
            db.session.add(tracking)
            
            db.session.commit()
            
            # إرسال إشعار التسليم
            self._send_delivery_confirmation_notification(order)
            
            return True, "تم تسجيل تسليم الطلب بنجاح"
            
        except Exception as e:
            current_app.logger.error(f"خطأ في تسجيل تسليم الطلب: {e}")
            db.session.rollback()
            return False, f"خطأ في تسجيل تسليم الطلب: {str(e)}"
    
    def _generate_order_number(self) -> str:
        """توليد رقم الطلب"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = str(random.randint(1000, 9999))
        return f"ORD{timestamp}{random_suffix}"
    
    def _calculate_estimated_delivery_time(self, pharmacy: Pharmacy) -> datetime:
        """حساب الوقت المتوقع للتوصيل"""
        # الوقت الأساسي للتوصيل (30 دقيقة)
        base_delivery_time = 30
        
        # إضافة وقت إضافي حسب المسافة
        additional_time = pharmacy.delivery_radius * 2  # دقيقتان لكل كيلومتر
        
        total_minutes = base_delivery_time + additional_time
        
        return datetime.utcnow() + timedelta(minutes=total_minutes)
    
    def _get_status_description(self, status: str) -> str:
        """الحصول على وصف حالة الطلب"""
        status_descriptions = {
            'pending': 'في الانتظار',
            'confirmed': 'مؤكد',
            'preparing': 'قيد التحضير',
            'ready': 'جاهز للتوصيل',
            'out_for_delivery': 'في الطريق',
            'delivered': 'تم التوصيل',
            'cancelled': 'ملغي'
        }
        return status_descriptions.get(status, status)
    
    def _send_order_notifications(self, order: Order):
        """إرسال إشعارات الطلب"""
        try:
            # إشعار للمستخدم
            subject = f"تم إنشاء طلبك رقم {order.order_number}"
            message = f"تم إنشاء طلبك بنجاح. الرقم: {order.order_number}\nالمجموع: {order.total_amount} ريال\nالوقت المتوقع للتوصيل: {order.estimated_delivery_time.strftime('%H:%M')}"
            
            self.notification_service.email_provider.send_email(
                order.user.email, subject, message
            )
            
            # إشعار للصيدلية
            pharmacy_subject = f"طلب جديد رقم {order.order_number}"
            pharmacy_message = f"تم استلام طلب جديد من {order.user.full_name}\nالرقم: {order.order_number}\nالمجموع: {order.total_amount} ريال"
            
            self.notification_service.email_provider.send_email(
                order.pharmacy.email, pharmacy_subject, pharmacy_message
            )
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال إشعارات الطلب: {e}")
    
    def _send_status_update_notification(self, order: Order):
        """إرسال إشعار تحديث الحالة"""
        try:
            subject = f"تحديث حالة طلبك رقم {order.order_number}"
            message = f"تم تحديث حالة طلبك رقم {order.order_number} إلى: {order.get_status_arabic()}"
            
            self.notification_service.email_provider.send_email(
                order.user.email, subject, message
            )
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال إشعار تحديث الحالة: {e}")
    
    def _send_cancellation_notification(self, order: Order, reason: str):
        """إرسال إشعار الإلغاء"""
        try:
            subject = f"تم إلغاء طلبك رقم {order.order_number}"
            message = f"تم إلغاء طلبك رقم {order.order_number}\nالسبب: {reason}"
            
            self.notification_service.email_provider.send_email(
                order.user.email, subject, message
            )
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال إشعار الإلغاء: {e}")
    
    def _send_delivery_assignment_notification(self, order: Order):
        """إرسال إشعار تعيين شخص التوصيل"""
        try:
            subject = f"تم تعيين شخص التوصيل لطلبك رقم {order.order_number}"
            message = f"تم تعيين شخص التوصيل لطلبك رقم {order.order_number}\nالاسم: {order.delivery_person_name}\nالهاتف: {order.delivery_person_phone}"
            
            self.notification_service.email_provider.send_email(
                order.user.email, subject, message
            )
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال إشعار تعيين شخص التوصيل: {e}")
    
    def _send_delivery_confirmation_notification(self, order: Order):
        """إرسال إشعار تأكيد التسليم"""
        try:
            subject = f"تم تسليم طلبك رقم {order.order_number}"
            message = f"تم تسليم طلبك رقم {order.order_number} بنجاح في {order.actual_delivery_time.strftime('%Y-%m-%d %H:%M')}"
            
            self.notification_service.email_provider.send_email(
                order.user.email, subject, message
            )
            
        except Exception as e:
            current_app.logger.error(f"خطأ في إرسال إشعار تأكيد التسليم: {e}")

# دالة مساعدة لإنشاء الطلبات
def create_medication_order(user_id: int, pharmacy_id: int, items: List[Dict], 
                           delivery_address: str, delivery_phone: str, **kwargs) -> Tuple[bool, str, Optional[Order]]:
    """دالة مساعدة لإنشاء طلب أدوية"""
    order_system = OrderManagementSystem()
    return order_system.create_order(
        user_id, pharmacy_id, items, delivery_address, delivery_phone, **kwargs
    )

if __name__ == '__main__':
    # اختبار النظام
    order_system = OrderManagementSystem()
    
    # اختبار إنشاء طلب
    test_items = [
        {'product_id': 1, 'quantity': 2},
        {'product_id': 2, 'quantity': 1}
    ]
    
    success, message, order = order_system.create_order(
        user_id=1,
        pharmacy_id=1,
        items=test_items,
        delivery_address="الرياض، حي النرجس، شارع الملك فهد",
        delivery_phone="0501234567"
    )
    
    if success:
        print(f"تم إنشاء الطلب بنجاح : {order.order_number}")
    else:
        print(f"فشل في إنشاء الطلب : {message}")
