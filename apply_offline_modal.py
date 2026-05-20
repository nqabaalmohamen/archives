import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ═══════════════════════════════════════════════════════════
# 1) CSS styles for the modal overlay
# ═══════════════════════════════════════════════════════════
MODAL_CSS = """
        /* ═══ Offline Notice Modal ═══ */
        #offline-modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            z-index: 9999;
            background: rgba(0, 0, 0, 0.72);
            backdrop-filter: blur(6px);
            -webkit-backdrop-filter: blur(6px);
            align-items: center;
            justify-content: center;
            padding: 20px;
            animation: fadeInModal 0.3s ease;
        }
        #offline-modal-overlay.show { display: flex; }
        @keyframes fadeInModal {
            from { opacity: 0; transform: scale(0.95); }
            to   { opacity: 1; transform: scale(1); }
        }
        #offline-modal-box {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid rgba(245,158,11,0.45);
            border-radius: 20px;
            padding: 32px 28px 24px;
            max-width: 420px;
            width: 100%;
            text-align: center;
            box-shadow: 0 0 60px rgba(245,158,11,0.18), 0 24px 60px rgba(0,0,0,0.6);
            direction: rtl;
        }
        #offline-modal-box .om-icon {
            font-size: 48px;
            color: #f59e0b;
            margin-bottom: 14px;
            animation: warnPulse 2s infinite;
        }
        @keyframes warnPulse {
            0%,100% { text-shadow: 0 0 12px rgba(245,158,11,0.5); }
            50%      { text-shadow: 0 0 30px rgba(245,158,11,0.9); }
        }
        #offline-modal-box h3 {
            color: #fcd34d;
            font-size: 15px;
            font-weight: 900;
            margin: 0 0 14px;
            line-height: 1.5;
        }
        #offline-modal-box p {
            color: rgba(255,255,255,0.75);
            font-size: 13px;
            line-height: 1.8;
            margin: 0 0 22px;
        }
        #offline-modal-box button {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: #0f172a;
            border: none;
            border-radius: 12px;
            padding: 12px 36px;
            font-size: 15px;
            font-weight: 900;
            cursor: pointer;
            width: 100%;
            transition: all 0.25s ease;
            box-shadow: 0 4px 20px rgba(245,158,11,0.4);
        }
        #offline-modal-box button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 28px rgba(245,158,11,0.55);
        }
        #offline-modal-box .om-note {
            margin-top: 14px;
            font-size: 11px;
            color: rgba(255,255,255,0.35);
        }
"""

# ═══════════════════════════════════════════════════════════
# 2) HTML for the modal (injected just after <body>)
# ═══════════════════════════════════════════════════════════
MODAL_HTML = """
<!-- ═══ Offline Notice Modal Overlay ═══ -->
<div id="offline-modal-overlay">
    <div id="offline-modal-box">
        <div class="om-icon"><i class="fas fa-exclamation-triangle"></i></div>
        <h3>⚠️ تنبيه: النظام غير متصل حالياً</h3>
        <p>
            قم بتحديث المتصفح أو تأكيد بأنك متصل بالانترنت لتتابع المعاملة مباشرةً.<br><br>
            إذا كنت متأكداً من تحديث المتصفح وأنك متصل بالانترنت، فهذا يعني أن النقابة
            قد تكون خارج مواعيد العمل الرسمية<br>
            <strong style="color:#fcd34d;">من 9 ص إلى 2 م</strong>
            أو في أيام الإجازات مثل الجمعة والإجازات الرسمية.
        </p>
        <button onclick="document.getElementById('offline-modal-overlay').classList.remove('show'); document.getElementById('offline-modal-overlay').style.display='none';">
            <i class="fas fa-check-circle" style="margin-left:6px;"></i> موافق — عرض آخر بيانات مؤرشفة
        </button>
        <div class="om-note">سيتم الاتصال تلقائياً عند عودة النظام للعمل</div>
    </div>
</div>
"""

# ═══════════════════════════════════════════════════════════
# 3) New JS catch block — shows modal, keeps live indicator
# ═══════════════════════════════════════════════════════════
NEW_CATCH = """} catch (err) {
        console.warn("Offline Mode - Showing Cache");
        
        if (cachedData) {
            try {
                const parsed = JSON.parse(cachedData);
                renderTransaction(parsed.transaction);
                
                // Show the offline modal overlay (only on first load, not silent poll)
                if (!isSilent) {
                    const modal = document.getElementById('offline-modal-overlay');
                    if (modal) {
                        modal.style.display = 'flex';
                        modal.classList.add('show');
                    }
                }
                
                const liveText = document.querySelector('.live-text');
                if (liveText) {
                    liveText.textContent = "عرض آخر حالة مؤرشفة";
                    liveText.style.color = "#f59e0b";
                }
                const liveDot = document.querySelector('.live-dot');
                if (liveDot) {
                    liveDot.style.background = "#f59e0b";
                    liveDot.style.boxShadow = "0 0 10px #f59e0b";
                    liveDot.style.animation = "livePulse 2s infinite";
                }
                
                const banner = document.getElementById('offline-banner');
                if (banner) {
                    banner.classList.remove('active');
                    banner.style.display = 'none';
                }
            } catch(e) {}
        } else {
            if (!isSilent) show('maintenance-card');
        }
    }"""

# ═══════════════════════════════════════════════════════════
# Pattern to match the existing catch block
# ═══════════════════════════════════════════════════════════
CATCH_PATTERN = re.compile(
    r'\}\s*catch\s*\(err\)\s*\{[\s\S]+?console\.warn\("Offline Mode - Showing Cache"\);[\s\S]+?if\s*\(cachedData\)\s*\{[\s\S]+?\}\s*else\s*\{\s*if\s*\(!isSilent\)\s*show\(\'maintenance-card\'\);\s*\}\s*\}'
)

files = ['index.html', 'track.html', 'live.html', 'test_live.html']

for filename in files:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        changed = False

        # --- Step 1: Inject CSS before </style> (only if not already injected) ---
        if 'offline-modal-overlay' not in content:
            content = content.replace('</style>', MODAL_CSS + '        </style>', 1)
            changed = True
            print(f"[{filename}] ✓ Injected modal CSS")
        else:
            # Update CSS if already exists — replace old block
            content = re.sub(
                r'/\* ═══ Offline Notice Modal ═══ \*/[\s\S]+?\.om-note \{[^}]+\}',
                MODAL_CSS.strip(),
                content
            )
            changed = True
            print(f"[{filename}] ✓ Updated modal CSS")

        # --- Step 2: Inject/update HTML modal after <body> ---
        if 'offline-modal-overlay' not in content:
            content = content.replace('<body>', '<body>\n' + MODAL_HTML, 1)
            changed = True
            print(f"[{filename}] ✓ Injected modal HTML")
        else:
            # Replace existing modal HTML block
            content = re.sub(
                r'<!-- ═══ Offline Notice Modal Overlay ═══ -->[\s\S]+?</div>\n</div>',
                MODAL_HTML.strip(),
                content
            )
            changed = True
            print(f"[{filename}] ✓ Updated modal HTML")

        # --- Step 3: Replace the catch block ---
        if CATCH_PATTERN.search(content):
            content = CATCH_PATTERN.sub(NEW_CATCH, content)
            changed = True
            print(f"[{filename}] ✓ Updated catch block")
        else:
            print(f"[{filename}] ⚠ catch block pattern not matched - skipping JS update")

        if changed:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[{filename}] ✅ Saved successfully\n")

    except FileNotFoundError:
        print(f"[{filename}] ⚠ File not found, skipping\n")
    except Exception as e:
        print(f"[{filename}] ❌ Error: {e}\n")
