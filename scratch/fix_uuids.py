import sys
import os
import django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive_system.settings')
django.setup()

from eams.models import Transaction
import uuid

def run():
    for t in Transaction.objects.all():
        t.secure_token = uuid.uuid4()
        t.save()
        print(f"Updated Transaction {t.id} with token {t.secure_token}")

if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archive_system.settings')
    django.setup()
    run()
