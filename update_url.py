import sys
import os
import re
import requests

STATIC_NGROK_DOMAIN = "https://goldfish-banked-valley.ngrok-free.dev"

if len(sys.argv) < 2:
    print("No URL provided")
    sys.exit(1)

new_url = sys.argv[1].strip()

# ✅ إذا كان الرابط المُمرّر هو الدومين الثابت لـ ngrok، نحدّث keyval فقط
# ❌ إذا كان رابط Cloudflare مؤقت، نرفضه ونُبقي على الدومين الثابت
if "trycloudflare.com" in new_url:
    print(f"REJECTED Cloudflare URL: {new_url} — keeping static ngrok domain.")
    new_url = STATIC_NGROK_DOMAIN

# تحديث النفق النشط في المخزن العام keyval.org
try:
    val_to_store = new_url.replace("https://", "https_")
    url_to_set = f"https://api.keyval.org/set/nqaba_almohamen_fayoum_archive_tunnel_secure/{val_to_store}"
    r = requests.get(url_to_set, timeout=10)
    if r.status_code == 200:
        print(f"Updated keyval.org to: {new_url}")
    else:
        print(f"Failed to update keyval.org: {r.status_code}")
except Exception as e:
    print(f"Error updating keyval.org: {e}")

# ✅ تحديث الملفات المحلية لتحتوي على الدومين الثابت
files = ['index.html', 'track.html', 'live.html', 'archive_system/settings.py']

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()

        # استبدال أي رابط ngrok أو cloudflare قديم بالدومين الثابت
        updated = re.sub(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com', STATIC_NGROK_DOMAIN, content)
        updated = re.sub(r'https://[a-zA-Z0-9\-]+\.ngrok-free\.dev', STATIC_NGROK_DOMAIN, updated)
        updated = re.sub(r'https://[a-zA-Z0-9\-]+\.ngrok\.io', STATIC_NGROK_DOMAIN, updated)

        if updated != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(updated)
            print(f"Updated URL in {f}")
        else:
            print(f"No change needed in {f}")

# ✅ الدومين ثابت — لا حاجة لـ git push في كل مرة
# GitHub Pages يحتوي بالفعل على الدومين الثابت
print("Done. Static domain is permanent — no git push needed.")
