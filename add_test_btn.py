import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Test button HTML to inject temporarily before </body>
TEST_BTN = (
    '\n<!-- TEST BUTTON - REMOVE AFTER TESTING -->\n'
    '<button onclick="document.getElementById(\'offline-modal-overlay\').style.display=\'flex\';" '
    'style="position:fixed;bottom:20px;left:20px;z-index:99999;background:#dc2626;color:white;'
    'border:none;border-radius:10px;padding:10px 20px;font-size:14px;font-weight:bold;'
    'cursor:pointer;box-shadow:0 4px 15px rgba(220,38,38,0.5);">'
    'TEST: Show Offline Modal</button>\n'
    '<!-- END TEST BUTTON -->\n'
)

files = ['index.html', 'track.html', 'live.html']

for filename in files:
    try:
        with open(filename, encoding='utf-8') as f:
            content = f.read()
        
        # Remove old test button if exists
        content = re.sub(
            r'\n<!-- TEST BUTTON.*?<!-- END TEST BUTTON -->\n',
            '',
            content,
            flags=re.DOTALL
        )
        
        # Add test button before </body>
        content = content.replace('</body>', TEST_BTN + '</body>')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[{filename}] Test button added')
    except Exception as e:
        print(f'[{filename}] ERROR: {e}')
