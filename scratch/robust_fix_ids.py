import os
import re

path = 'templates/eams/reports.html'
if not os.path.exists(path):
    print("File not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove all 'id="main_..."' occurrences to clean up
content = re.sub(r'\s+id="main_[^"]+"', '', content)

# 2. Find the main filter form section
# It starts around line 70 usually
parts = content.split('<!-- Enhanced Filter Form -->')
if len(parts) < 2:
    print("Tag not found")
    exit(1)

header = parts[0]
form_body = parts[1]

# 3. Add IDs only to the visible inputs in the form_body
form_body = form_body.replace('name="q"', 'name="q" id="main_q"', 1)
form_body = form_body.replace('name="category"', 'name="category" id="main_category"', 1)
form_body = form_body.replace('name="doc_type"', 'name="doc_type" id="main_doc_type"', 1)
form_body = form_body.replace('name="user_id"', 'name="user_id" id="main_user_id"', 1)
form_body = form_body.replace('name="start_date"', 'name="start_date" id="main_start_date"', 1)
form_body = form_body.replace('name="end_date"', 'name="end_date" id="main_end_date"', 1)

new_content = header + '<!-- Enhanced Filter Form -->' + form_body

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully cleaned and mapped IDs for PDF export functionality")
