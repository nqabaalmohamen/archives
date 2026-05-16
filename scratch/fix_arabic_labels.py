import os
import re

def fix_file(path):
    if not os.path.exists(path):
        return
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace options using regex
    content = re.sub(r'<option value="incoming"(.*?)>.*?</option>', r'<option value="incoming"\1>وارد</option>', content)
    content = re.sub(r'<option value="outgoing"(.*?)>.*?</option>', r'<option value="outgoing"\1>صادر</option>', content)
    content = re.sub(r'<option value="internal"(.*?)>.*?</option>', r'<option value="internal"\1>داخلي</option>', content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Fixed Arabic labels in {path}")

fix_file('templates/eams/document_form.html')
fix_file('templates/eams/reports.html')
