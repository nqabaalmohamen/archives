import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update the view to include a dynamic report title
new_code = """
    # Dynamic Title Logic
    report_title = "تقرير إحصائيات الأرشيف العام"
    if doc_type == 'incoming': report_title = "تقرير البريد الوارد"
    elif doc_type == 'outgoing': report_title = "تقرير البريد الصادر"
    elif doc_type == 'internal': report_title = "تقرير البريد الداخلي"
    
    if category_id:
        try:
            cat_name = Category.objects.get(id=category_id).name
            report_title += f" - قسم {cat_name}"
        except: pass

    context = {
        'report_title': report_title,
        'documents': docs.order_by('-uploaded_at'),
"""

import re
# Insert the title logic before the context definition
pattern = r"docs = docs\.filter\(uploaded_at__date__lte=end_date\)\s+.*?\s+context = \{"
# We need to find where to insert. Let's be safer.
content = content.replace("context = {", new_code)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated views.py with dynamic report title logic")
