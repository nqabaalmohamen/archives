from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, Transaction
from .utils import sync_transaction_to_remote
import threading

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()

@receiver(post_save, sender=Transaction)
def sync_transaction(sender, instance, **kwargs):
    """تزامن المعاملة مع الاستضافة الخارجية عند الحفظ"""
    # استخدام threading لتجنب تأخير استجابة النظام المحلي في حالة بطء الإنترنت
    thread = threading.Thread(target=sync_transaction_to_remote, args=(instance,))
    thread.start()
