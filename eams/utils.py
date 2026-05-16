import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def sync_transaction_to_remote(transaction):
    """
    إرسال بيانات المعاملة إلى الاستضافة الخارجية لتحديث صفحة المتابعة
    """
    if not getattr(settings, 'ENABLE_REMOTE_SYNC', False):
        return False

    url = getattr(settings, 'REMOTE_TRACKING_URL', None)
    api_key = getattr(settings, 'REMOTE_TRACKING_API_KEY', None)

    if not url or not api_key:
        logger.warning("Remote tracking sync is enabled but URL or API KEY is missing.")
        return False

    data = {
        'api_key': api_key,
        'secure_token': str(transaction.secure_token),
        'tracking_number': transaction.tracking_number,
        'title': transaction.title,
        'client_name': transaction.client_name,
        'current_status': transaction.current_status,
        'status_label': transaction.get_current_status_display(),
    }

    try:
        # إرسال الطلب في الخلفية أو بمهلة زمنية قصيرة لعدم تعطيل النظام المحلي
        response = requests.post(url, data=data, timeout=5)
        if response.status_code == 200 and response.text == "OK":
            return True
        else:
            logger.error(f"Failed to sync transaction {transaction.tracking_number}. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error syncing transaction {transaction.tracking_number}: {str(e)}")
        return False
