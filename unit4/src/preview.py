"""python3 preview.py '{{fdd:run}}' 'fig:nf_onion' parts/03_x.html ... -> scratch png for checking"""
import sys, os, subprocess
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
sys.argv, args = sys.argv[:1], sys.argv[1:]
import build  # noqa: E402
S = '/tmp/claude-1000/-home-pj-Study-Sem3-DBMS-Notes/8aa1628f-5065-4d79-8cf7-01ee7c8d5c07/scratchpad/u4'
css = open(os.path.join(BASE, 'style.css')).read()
theme = os.environ.get('THEME', 'light')
body = ''
for a in args:
    if a.startswith('fig:'):
        body += f'{{{{svg:{a[4:]}}}}}'
    elif a.endswith('.html'):
        body += open(os.path.join(BASE, a)).read()
    else:
        body += a
body = build.expand(body)
html = (f'<html data-theme="{theme}"><head><meta charset=utf-8><style>{css} body{{padding:20px;max-width:1000px}}</style>'
        f'</head><body><main class="content">{body}</main></body></html>')
open(f'{S}/prev.html', 'w').write(html)
h = int(os.environ.get('H', 1400))
subprocess.run(['chromium', '--headless', '--disable-gpu', '--hide-scrollbars', f'--window-size=1040,{h}',
                f'--screenshot={S}/prev.png', f'file://{S}/prev.html'], capture_output=True)
print('ok')
