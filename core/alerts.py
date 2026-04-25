"""
Alert System Module

This module provides alert management for heat stress and UV index warnings,
with support for multiple notification methods and multi-language alerts.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert data structure."""
    id: str
    alert_type: str  # 'heat_stress', 'uv', 'combined'
    severity: str  # 'low', 'moderate', 'high', 'very_high', 'extreme'
    location: str
    message: str
    translations: Dict[str, str]
    timestamp: datetime
    expires_at: Optional[datetime] = None
    active: bool = True


@dataclass
class Subscription:
    """Alert subscription data structure."""
    id: str
    location: str
    language: str
    alert_types: List[str]
    notification_method: str  # 'sms', 'email', 'push'
    contact: str
    active: bool = True


class AlertManager:
    """
    Manager for heat stress and UV alerts.
    
    This class handles alert generation, distribution, and subscription management.
    """
    
    def __init__(self):
        """Initialize the alert manager."""
        self.active_alerts: Dict[str, Alert] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        
        # Alert thresholds
        self.heat_stress_thresholds = {
            'extreme': 32.0,
            'very_high': 30.0,
            'high': 28.0,
            'moderate': 25.0
        }
        
        self.uv_thresholds = {
            'extreme': 11.0,
            'very_high': 8.0,
            'high': 6.0,
            'moderate': 3.0
        }
        
        # Multi-language alert templates
        self.alert_templates = self._load_alert_templates()
    
    def _load_alert_templates(self) -> Dict:
        """Load multi-language alert templates."""
        return {
            'heat_stress': {
                'en': {
                    'extreme': 'EXTREME HEAT RISK: Stop all outdoor work immediately. Move to air-conditioned areas.',
                    'very_high': 'VERY HIGH HEAT RISK: Limit outdoor work to 15% with 85% rest breaks.',
                    'high': 'HIGH HEAT RISK: Implement 25% work, 75% rest cycle with mandatory breaks.',
                    'moderate': 'MODERATE HEAT RISK: Provide water every 20 minutes with regular rest breaks.'
                },
                'ar': {
                    'extreme': 'خطر حراري شديد: توقف عن جميع الأعمال في الهواء الطلق فوراً. انتقل إلى مناطق مكيفة.',
                    'very_high': 'خطر حراري عالي جداً: قلل العمل في الهواء الطلق إلى 15% مع استراحات طويلة.',
                    'high': 'خطر حراري عالي: طبق دورة عمل 25% و休息 75% مع فترات راحة إلزامية.',
                    'moderate': 'خطر حراري متوسط: قدم الماء كل 20 دقيقة مع فترات راحة منتظمة.'
                },
                'tl': {
                    'extreme': 'MATINDING PANGANIB: Itigil ang lahat ng trabaho sa labas. Lumipat sa aircon.',
                    'very_high': 'Napakataas na Panganib: Limitado ang trabaho sa labas sa 15% na may mahabang pahinga.',
                    'high': 'Mataas na Panganib: 25% trabaho, 75% pahinga na may mga break.',
                    'moderate': 'Katamtamang Panganib: Magbigay ng tubig bawat 20 minuto na may regular na pahinga.'
                },
                'ur': {
                    'extreme': 'شدہ خطر: باہری کام فوراً روک دیں۔ ایئر کنڈیشنڈ علاقوں میں جائیں۔',
                    'very_high': 'بہت زیادہ خطرہ: باہری کام کو 15% تک محدود کریں۔',
                    'high': 'زیادہ خطرہ: 25% کام اور 75% آرام کا سلسلہ لاگو کریں۔',
                    'moderate': 'متوسط خطرہ: ہر 20 منٹ میں پانی فراہم کریں۔'
                }
            },
            'uv': {
                'en': {
                    'extreme': 'EXTREME UV: Avoid all sun exposure. Maximum protection required.',
                    'very_high': 'VERY HIGH UV: Avoid sun between 10am-4pm. Use SPF 50+.',
                    'high': 'HIGH UV: Seek shade. Use SPF 30+ sunscreen.',
                    'moderate': 'MODERATE UV: Use SPF 15+ sunscreen and sunglasses.'
                },
                'ar': {
                    'extreme': 'أشعة فوق بنفسجية شديدة: تجنب التعرض للشمس تماماً. حماية قصوى مطلوبة.',
                    'very_high': 'أشعة فوق بنفسجية عالية جداً: تجنب الشمس بين 10 صباحاً و 4 مساءً. استخدم واقي SPF 50+.',
                    'high': 'أشعة فوق بنفسجية عالية: ابحث عن الظل. استخدم واقي SPF 30+.',
                    'moderate': 'أشعة فوق بنفسجية متوسطة: استخدم واقي SPF 15+ ونظارات شمسية.'
                },
                'tl': {
                    'extreme': 'Sobrang Taas na UV: Iwasan ang lahat ng exposure sa araw. Maximum protection.',
                    'very_high': 'Napakataas na UV: Iwasan ang araw sa pagitan ng 10am-4pm. Gumamit ng SPF 50+.',
                    'high': 'Mataas na UV: Humanap ng lilim. Gumamit ng SPF 30+ sunscreen.',
                    'moderate': 'Katamtamang UV: Gumamit ng SPF 15+ sunscreen at sunglasses.'
                },
                'ur': {
                    'extreme': 'شدید UV: سورج کی طرف سے بچیں۔ زیادہ سے زیادہ تحفظ کی ضرورت ہے۔',
                    'very_high': 'بہت زیادہ UV: صبح 10 بجے سے شام 4 بجے تک سورج سے بچیں۔ SPF 50+ استعمال کریں۔',
                    'high': 'زیادہ UV: سایہ تلاش کریں۔ SPF 30+ سکرین استعمال کریں۔',
                    'moderate': 'متوسط UV: SPF 15+ سکرین اور دھوپ کے چشمے استعمال کریں۔'
                }
            }
        }
    
    def generate_alert(self, alert_type: str, severity: str, location: str, 
                      value: float, language: str = 'en') -> Alert:
        """
        Generate an alert for specified conditions.
        
        Args:
            alert_type: Type of alert ('heat_stress', 'uv', 'combined')
            severity: Alert severity level
            location: Location name
            value: Trigger value (WBGT or UV index)
            language: Alert language
        
        Returns:
            Alert object
        """
        alert_id = f"{alert_type}_{location}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Get message in requested language
        message = self.alert_templates.get(alert_type, {}).get(language, {}).get(severity, '')
        
        # Get translations for all supported languages
        translations = {}
        for lang in ['en', 'ar', 'tl', 'ur']:
            translations[lang] = self.alert_templates.get(alert_type, {}).get(lang, {}).get(severity, '')
        
        # Set expiration (2 hours for most alerts)
        expires_at = datetime.utcnow() + timedelta(hours=2)
        
        alert = Alert(
            id=alert_id,
            alert_type=alert_type,
            severity=severity,
            location=location,
            message=message,
            translations=translations,
            timestamp=datetime.utcnow(),
            expires_at=expires_at,
            active=True
        )
        
        self.active_alerts[alert_id] = alert
        logger.info(f"Generated alert: {alert_id} for {location}")
        
        return alert
    
    def check_and_generate_heat_stress_alert(self, wbgt: float, location: str, 
                                            language: str = 'en') -> Optional[Alert]:
        """
        Check WBGT and generate alert if needed.
        
        Args:
            wbgt: WBGT temperature
            location: Location name
            language: Alert language
        
        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if wbgt >= self.heat_stress_thresholds['extreme']:
            return self.generate_alert('heat_stress', 'extreme', location, wbgt, language)
        elif wbgt >= self.heat_stress_thresholds['very_high']:
            return self.generate_alert('heat_stress', 'very_high', location, wbgt, language)
        elif wbgt >= self.heat_stress_thresholds['high']:
            return self.generate_alert('heat_stress', 'high', location, wbgt, language)
        elif wbgt >= self.heat_stress_thresholds['moderate']:
            return self.generate_alert('heat_stress', 'moderate', location, wbgt, language)
        
        return None
    
    def check_and_generate_uv_alert(self, uv_index: float, location: str, 
                                    language: str = 'en') -> Optional[Alert]:
        """
        Check UV index and generate alert if needed.
        
        Args:
            uv_index: UV index value
            location: Location name
            language: Alert language
        
        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if uv_index >= self.uv_thresholds['extreme']:
            return self.generate_alert('uv', 'extreme', location, uv_index, language)
        elif uv_index >= self.uv_thresholds['very_high']:
            return self.generate_alert('uv', 'very_high', location, uv_index, language)
        elif uv_index >= self.uv_thresholds['high']:
            return self.generate_alert('uv', 'high', location, uv_index, language)
        elif uv_index >= self.uv_thresholds['moderate']:
            return self.generate_alert('uv', 'moderate', location, uv_index, language)
        
        return None
    
    def get_active_alerts(self, country: str = 'SA', severity: str = 'high') -> List[Dict]:
        """
        Get active alerts for a country and severity level.
        
        Args:
            country: Country code
            severity: Minimum severity level
        
        Returns:
            List of active alerts
        """
        severity_order = ['low', 'moderate', 'high', 'very_high', 'extreme']
        min_severity_index = severity_order.index(severity)
        
        active = []
        for alert in self.active_alerts.values():
            if not alert.active:
                continue
            
            # Check if alert expired
            if alert.expires_at and datetime.utcnow() > alert.expires_at:
                alert.active = False
                continue
            
            # Check severity level
            alert_severity_index = severity_order.index(alert.severity)
            if alert_severity_index >= min_severity_index:
                active.append({
                    'id': alert.id,
                    'type': alert.alert_type,
                    'severity': alert.severity,
                    'location': alert.location,
                    'message': alert.message,
                    'timestamp': alert.timestamp.isoformat(),
                    'expires_at': alert.expires_at.isoformat() if alert.expires_at else None
                })
        
        return active
    
    def subscribe(self, location: str, language: str, alert_types: List[str],
                 notification_method: str, contact: str) -> Dict:
        """
        Subscribe to alerts for a location.
        
        Args:
            location: Location name
            language: Preferred language
            alert_types: Types of alerts to receive
            notification_method: Notification method ('sms', 'email', 'push')
            contact: Contact information (phone number, email, push token)
        
        Returns:
            Subscription details
        """
        subscription_id = f"sub_{location}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        subscription = Subscription(
            id=subscription_id,
            location=location,
            language=language,
            alert_types=alert_types,
            notification_method=notification_method,
            contact=contact,
            active=True
        )
        
        self.subscriptions[subscription_id] = subscription
        logger.info(f"Created subscription: {subscription_id} for {location}")
        
        return {
            'id': subscription_id,
            'location': location,
            'language': language,
            'alert_types': alert_types,
            'notification_method': notification_method,
            'status': 'active'
        }
    
    def send_alert_notification(self, alert: Alert, subscription: Subscription) -> bool:
        """
        Send alert notification to a subscriber.
        
        Args:
            alert: Alert to send
            subscription: Subscription details
        
        Returns:
            True if sent successfully, False otherwise
        """
        # Get message in subscriber's language
        message = alert.translations.get(subscription.language, alert.message)
        
        # Send based on notification method
        if subscription.notification_method == 'sms':
            return self._send_sms(subscription.contact, message)
        elif subscription.notification_method == 'email':
            return self._send_email(subscription.contact, alert.alert_type, message)
        elif subscription.notification_method == 'push':
            return self._send_push(subscription.contact, alert)
        
        return False
    
    def _send_sms(self, phone: str, message: str) -> bool:
        """Send SMS alert (placeholder for actual SMS integration)."""
        logger.info(f"SMS alert to {phone}: {message[:50]}...")
        # TODO: Integrate with SMS service (Twilio, etc.)
        return True
    
    def _send_email(self, email: str, alert_type: str, message: str) -> bool:
        """Send email alert (placeholder for actual email integration)."""
        logger.info(f"Email alert to {email}: {alert_type} - {message[:50]}...")
        # TODO: Integrate with email service
        return True
    
    def _send_push(self, token: str, alert: Alert) -> bool:
        """Send push notification (placeholder for actual push service)."""
        logger.info(f"Push notification to {token}: {alert.alert_type} - {alert.severity}")
        # TODO: Integrate with push notification service (Firebase, etc.)
        return True
    
    def cleanup_expired_alerts(self):
        """Clean up expired alerts."""
        now = datetime.utcnow()
        expired_count = 0
        
        for alert_id, alert in self.active_alerts.items():
            if alert.expires_at and now > alert.expires_at:
                alert.active = False
                expired_count += 1
        
        logger.info(f"Cleaned up {expired_count} expired alerts")
