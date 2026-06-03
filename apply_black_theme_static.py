import re

files = ['index.html', 'track.html', 'live.html']

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update root vars
        content = re.sub(
            r':root\s*\{[^}]+\}',
            """:root {
            --primary:   #000000;
            --accent:    #d4af37;
            --gold:      #d4af37;
            --success:   #22c55e;
            --danger:    #ef4444;
            --bg:        #000000;
            --text:      #ffffff;
            --muted:     #94a3b8;
            --border:    rgba(255,255,255,0.08);
            --surface:   #111111;
        }""",
            content
        )

        # Update bg-wrapper
        content = re.sub(
            r'\.bg-wrapper\s*\{[\s\S]*?\}\s*\.bg-wrapper::before,\s*\.bg-wrapper::after\s*\{[\s\S]*?\}\s*\.bg-wrapper::before\s*\{[\s\S]*?\}\s*\.bg-wrapper::after\s*\{[\s\S]*?\}',
            """.bg-wrapper {
            min-height: 100vh;
            background: #000000;
            position: relative;
            overflow: hidden;
            background-image: 
                linear-gradient(rgba(212, 175, 55, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(212, 175, 55, 0.03) 1px, transparent 1px);
            background-size: 40px 40px;
        }

        .bg-wrapper::before,
        .bg-wrapper::after {
            content: '';
            position: absolute;
            border-radius: 50%;
            opacity: 0.15;
            filter: blur(60px);
            animation: float 8s ease-in-out infinite;
        }
        .bg-wrapper::before { width: 400px; height: 400px; background: #d4af37; top: -100px; right: -100px; }
        .bg-wrapper::after  { width: 300px; height: 300px; background: #ffffff; bottom: -50px; left: -50px; animation-delay: 3s; }""",
            content
        )

        # Update result-card
        content = re.sub(
            r'\.result-card\s*\{[\s\S]*?\}\s*\.result-card\.active\s*\{[\s\S]*?\}\s*@keyframes slideUp\s*\{[\s\S]*?\}\s*/\* رأس البطاقة \*/\s*\.card-header\s*\{[\s\S]*?\}\s*\.trk-chip\s*\{[\s\S]*?\}\s*\.card-title\s*\{[\s\S]*?\}\s*\.card-subtitle\s*\{[\s\S]*?\}',
            """.result-card {
            background: var(--surface);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 25px 60px rgba(0,0,0,0.8);
            animation: slideUp 0.5s ease-out;
            position: relative;
            display: none;
        }
        .result-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 4px;
            background: linear-gradient(90deg, #d4af37, #fff, #d4af37);
        }
        .result-card.active { display: block; }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* رأس البطاقة */
        .card-header {
            background: transparent;
            padding: 30px 22px 20px;
            text-align: center;
        }
        .trk-chip {
            display: inline-block;
            background: rgba(212, 175, 55, 0.1);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 6px;
            padding: 6px 16px;
            font-family: 'Courier New', monospace;
            font-size: 13px; font-weight: 900;
            color: #d4af37;
            letter-spacing: 1px;
            margin-bottom: 15px;
        }
        .card-title { font-size: 22px; font-weight: 900; color: var(--text); margin-bottom: 8px; }
        .card-subtitle { font-size: 13px; color: var(--muted); font-weight: 600; }""",
            content
        )

        # Update logo-circle
        if '.logo-circle {' in content:
            content = re.sub(
                r'\.logo-circle\s*\{[\s\S]*?\}',
                """.logo-circle {
                width: 80px; height: 80px;
                background: #111111;
                border: 2px solid rgba(212, 175, 55, 0.5);
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-size: 34px; color: #d4af37;
                margin: 0 auto 16px;
                box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
            }""",
                content
            )
            
        content = content.replace('#6366f1', '#d4af37')
        content = content.replace('#4f46e5', '#b8860b')
        content = content.replace('99,102,241', '212,175,55')
        
        # specific inline replacements
        content = content.replace(
            'style="background: #f8fafc; padding: 22px; border-bottom: 2px solid #e2e8f0;"',
            'style="background: rgba(255,255,255,0.02); padding: 22px; border-bottom: 1px solid rgba(255,255,255,0.08); border-top: 1px solid rgba(255,255,255,0.08);"'
        )
        content = content.replace(
            'background: #f8fafc;',
            'background: rgba(255,255,255,0.02);'
        )
        content = content.replace(
            'background: #fff;',
            'background: rgba(255,255,255,0.02);'
        )
        content = content.replace(
            'background: linear-gradient(135deg, #111827 0%, #1f2937 100%);',
            'background: transparent;'
        )
        
        # logo addition
        if '<div class="logo-circle"><i class="fas fa-balance-scale"></i></div>' not in content:
            # find where to add
            content = content.replace(
                '<div style="font-size: 16px; font-weight: 900; color: #fff; margin-bottom: 4px; text-align: center;">نقابة المحامين بالفيوم</div>',
                '<div class="logo-circle" style="width:50px;height:50px;font-size:20px;"><i class="fas fa-balance-scale"></i></div>\n<div style="font-size: 16px; font-weight: 900; color: #fff; margin-bottom: 4px; text-align: center;">نقابة المحامين بالفيوم</div>'
            )
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated", file_path)
    except Exception as e:
        print("Error", file_path, e)
