import sys

path = 'archive_system/settings.py'
try:
    with open(path, 'rb') as f:
        data = f.read()
    
    # Try to find a place to insert
    # We'll just append to the very end
    addition = b"\nCORS_ALLOW_HEADERS = [\n    'accept',\n    'authorization',\n    'content-type',\n    'user-agent',\n    'x-csrftoken',\n    'x-requested-with',\n    'ngrok-skip-browser-warning',\n    'cf-skip-browser-warning',\n]\n"
    
    if b'CORS_ALLOW_HEADERS' not in data:
        with open(path, 'ab') as f:
            f.write(addition)
        print("Successfully appended CORS_ALLOW_HEADERS")
    else:
        print("CORS_ALLOW_HEADERS already exists")
except Exception as e:
    print(f"Error: {e}")
