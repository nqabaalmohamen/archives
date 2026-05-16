import os

file_path = 'eams/views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Filter out the garbage lines at the end of the file
# We look for lines that are clearly outside any function
new_lines = []
for line in lines:
    if line.strip() == ", ('employee', ''), ('viewer', '')]" or line.strip() == "})":
        # Check if this is trailing garbage
        continue
    new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Cleaned up garbage in views.py")
