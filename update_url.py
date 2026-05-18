import sys
import os
import re
import requests

if len(sys.argv) < 2:
    print("No URL provided")
    sys.exit(1)

new_url = sys.argv[1]

# ✅ تحديث النفق النشط في المخزن العام keyval.org لضمان عمل الرابط الثابت بنسبة 100%
try:
    val_to_store = new_url.replace("https://", "https_")
    url_to_set = f"https://api.keyval.org/set/nqaba_almohamen_fayoum_archive_tunnel_secure/{val_to_store}"
    r = requests.get(url_to_set, timeout=10)
    if r.status_code == 200:
        print("Successfully updated active tunnel URL on keyval.org storage!")
    else:
        print(f"Failed to update keyval.org: {r.status_code}")
except Exception as e:
    print(f"Error updating keyval.org: {e}")

files = ['index.html', 'track.html', 'live.html', 'archive_system/settings.py']

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        content = re.sub(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', new_url, content)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated URL in {f}")
