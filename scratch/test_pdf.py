import os
from weasyprint import HTML

html_content = "<html><body><h1>Test Arabic: السلام عليكم</h1></body></html>"
try:
    pdf = HTML(string=html_content).write_pdf()
    with open('test_output.pdf', 'wb') as f:
        f.write(pdf)
    print("Success: PDF generated successfully")
except Exception as e:
    print(f"Error: {str(e)}")
