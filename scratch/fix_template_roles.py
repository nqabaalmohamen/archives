files = [
    'templates/eams/user_detail.html',
    'templates/eams/category_list.html',
]

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace("request.user.profile.role == 'admin'", "request.user.profile.access_users")
    content = content.replace("target_user.profile.role == 'admin'", "target_user.profile.access_users")
    content = content.replace("target_user.profile.role == 'employee'", "target_user.profile.access_categories")
    content = content.replace("profile.get_role_display", "profile.job_title|default:'موظف'")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Fixed: {filepath}')
