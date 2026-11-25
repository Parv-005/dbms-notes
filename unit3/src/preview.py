"""python3 preview.py ID [ID..] -> renders ER ids into scratch html + png for checking"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import er, erdefs  # noqa
S = '/tmp/claude-1000/-home-pj-Study-Sem3-DBMS-Notes/8aa1628f-5065-4d79-8cf7-01ee7c8d5c07/scratchpad/u3'
css = open(os.path.join(os.path.dirname(__file__), 'style.css')).read()
theme = os.environ.get('THEME', 'light')
body = ''
import figures
for i in sys.argv[1:]:
    if i.startswith('fig:'):
        body += getattr(figures, i[4:])()
        continue
    e = er.ER.REG[i]
    tabs = e.check()
    body += f'<h4>{i}</h4>' + e.draw() + (er.schema_html(tabs, e.notes) if e.expect is not None else '')
html = f'<html data-theme="{theme}"><head><meta charset=utf-8><style>{css} body{{padding:20px;max-width:1000px}}</style></head><body>{body}</body></html>'
open(f'{S}/prev.html', 'w').write(html)
h = int(os.environ.get('H', 1400))
subprocess.run(['chromium', '--headless', '--disable-gpu', '--hide-scrollbars', f'--window-size=1040,{h}',
                f'--screenshot={S}/prev.png', f'file://{S}/prev.html'], capture_output=True)
print('ok')
