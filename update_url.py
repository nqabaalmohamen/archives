import sys
import os
import re

if len(sys.argv) < 2:
    print("No URL provided")
    sys.exit(1)

new_url = sys.argv[1]

files = ['index.html', 'track.html', 'live.html', 'archive_system/settings.py']

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        content = re.sub(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', new_url, content)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated URL in {f}")
