import os

files = ['track.html', 'index.html', 'live.html']

old_code = """                const banner = document.getElementById('offline-banner');
                if (banner) {
                    banner.innerHTML = '<i class="fas fa-wifi-slash"></i> عرض آخر بيانات مسجلة (النظام غير متصل حالياً)';
                    banner.classList.add('active');
                    banner.style.background = "rgba(239, 68, 68, 0.15)";
                    banner.style.color = "#fca5a5";
                    banner.style.borderColor = "rgba(239, 68, 68, 0.4)";
                }"""

new_code = """                const banner = document.getElementById('offline-banner');
                if (banner) {
                    banner.classList.remove('active');
                    banner.style.display = 'none';
                }"""

for f in files:
    if os.path.exists(f):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        content = content.replace(old_code, new_code)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Updated {f}")
