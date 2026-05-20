import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MODAL_HTML = (
    '\n<!-- === Offline Notice Modal Overlay === -->\n'
    '<div id="offline-modal-overlay" style="display:none;position:fixed;inset:0;z-index:9999;'
    'background:rgba(0,0,0,0.75);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);'
    'align-items:center;justify-content:center;padding:20px;">\n'
    '    <div style="background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);'
    'border:1px solid rgba(245,158,11,0.5);border-radius:20px;padding:32px 28px 24px;'
    'max-width:430px;width:100%;text-align:center;'
    'box-shadow:0 0 60px rgba(245,158,11,0.2),0 24px 60px rgba(0,0,0,0.6);direction:rtl;">\n'
    '        <div style="font-size:50px;color:#f59e0b;margin-bottom:16px;">'
    '<i class="fas fa-exclamation-triangle"></i></div>\n'
    '        <h3 style="color:#fcd34d;font-size:16px;font-weight:900;margin:0 0 14px;line-height:1.5;">'
    'تنبيه: النظام غير متصل حالياً</h3>\n'
    '        <p style="color:rgba(255,255,255,0.78);font-size:13px;line-height:2;margin:0 0 22px;">\n'
    '            قم بتحديث المتصفح أو تأكيد بأنك متصل بالانترنت لتتابع المعاملة مباشرةً.<br><br>\n'
    '            إذا كنت متأكداً من تحديث المتصفح وأنك متصل بالانترنت، فهذا يعني أن النقابة\n'
    '            قد تكون خارج مواعيد العمل الرسمية\n'
    '            <strong style="color:#fcd34d;">من 9 ص إلى 2 م</strong>\n'
    '            أو في أيام الإجازات مثل الجمعة والإجازات الرسمية.\n'
    '        </p>\n'
    '        <button onclick="document.getElementById(\'offline-modal-overlay\').style.display=\'none\';" '
    'style="background:linear-gradient(135deg,#f59e0b,#d97706);color:#0f172a;border:none;'
    'border-radius:12px;padding:13px 36px;font-size:15px;font-weight:900;cursor:pointer;'
    'width:100%;box-shadow:0 4px 20px rgba(245,158,11,0.4);">\n'
    '            <i class="fas fa-check-circle" style="margin-left:6px;"></i>'
    ' موافق &mdash; عرض آخر بيانات مؤرشفة\n'
    '        </button>\n'
    '        <div style="margin-top:14px;font-size:11px;color:rgba(255,255,255,0.35);">'
    'سيتم الاتصال تلقائياً عند عودة النظام للعمل</div>\n'
    '    </div>\n'
    '</div>\n'
)

# JS snippet to show the modal
SHOW_MODAL_JS = (
    "                // Show offline modal on first load\n"
    "                if (!isSilent) {\n"
    "                    const om = document.getElementById('offline-modal-overlay');\n"
    "                    if (om) { om.style.display = 'flex'; }\n"
    "                }\n"
)

# JS snippet to hide the modal when back online
HIDE_MODAL_JS = (
    "            const om = document.getElementById('offline-modal-overlay');\n"
    "            if (om) { om.style.display = 'none'; }\n"
)

files = ['index.html', 'track.html', 'live.html', 'test_live.html']

for filename in files:
    try:
        with open(filename, encoding='utf-8') as f:
            content = f.read()

        # ── Step 1: Remove old modal div if already injected ──
        content = re.sub(
            r'\n<!-- === Offline Notice Modal Overlay === -->[\s\S]+?</div>\n</div>\n',
            '',
            content
        )

        # ── Step 2: Inject modal HTML right after <body> ──
        if '<body>' in content:
            content = content.replace('<body>', '<body>' + MODAL_HTML, 1)
            print(f'[{filename}] modal HTML injected')
        else:
            print(f'[{filename}] WARNING: <body> not found')

        # ── Step 3: Ensure JS shows modal in catch block ──
        # Add show-modal call after renderTransaction(parsed.transaction); inside catch
        if 'offline-modal-overlay' not in content.split('catch (err)')[1][:500] if 'catch (err)' in content else True:
            content = content.replace(
                "                renderTransaction(parsed.transaction);\n"
                "                \n"
                "                // Show offline modal on first load",
                "                renderTransaction(parsed.transaction);\n\n"
                "                // Show offline modal on first load"
            )
        # Make sure the show-modal JS is in the catch block
        if "om.style.display = 'flex'" not in content:
            content = content.replace(
                "                renderTransaction(parsed.transaction);\n",
                "                renderTransaction(parsed.transaction);\n" + SHOW_MODAL_JS,
                1  # only first occurrence (inside catch)
            )
            print(f'[{filename}] show-modal JS added')

        # ── Step 4: Ensure JS hides modal when back online ──
        if "om.style.display = 'none'" not in content:
            # Hide modal right after the banner hide in the online success block
            content = content.replace(
                "            const banner = document.getElementById('offline-banner');\n"
                "            if (banner) {\n"
                "                banner.classList.remove('active');\n"
                "                banner.style.display = 'none';\n"
                "            }",
                HIDE_MODAL_JS +
                "            const banner = document.getElementById('offline-banner');\n"
                "            if (banner) {\n"
                "                banner.classList.remove('active');\n"
                "                banner.style.display = 'none';\n"
                "            }"
            )
            print(f'[{filename}] hide-modal JS added')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[{filename}] SAVED OK\n')

    except FileNotFoundError:
        print(f'[{filename}] NOT FOUND, skipping\n')
    except Exception as e:
        print(f'[{filename}] ERROR: {e}\n')
