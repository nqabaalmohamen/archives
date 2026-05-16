import os

settings_path = 'archive_system/settings.py'
with open(settings_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add CORS_ALLOW_HEADERS if not present
if 'CORS_ALLOW_HEADERS' not in content:
    header_addition = """
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    'ngrok-skip-browser-warning',
    'cf-skip-browser-warning',
]
"""
    content += header_addition

with open(settings_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Settings updated successfully.")
