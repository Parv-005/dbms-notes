#!/usr/bin/env python3
"""Builds the Unit 4 notes (single self-contained HTML).

Placeholders inside parts/*.html (all computed by fd.py from the relations in fddefs.py):
  {{fdd:ID|caption}}   dependency diagram          {{keys:ID}}        candidate-key finding steps
  {{cl:ID|X}}          closure trace of X          {{nft:ID}}         per-FD normal-form test table
  {{chase:ID|NAME}}    chase tableau               {{pres:ID|NAME}}   dependency-preservation table
  {{dec:ID|bcnf|3nf}}  decomposition steps         {{schema:ID|NAME}} final relations with keys
  {{svg:NAME}}         figure from figures.py
  <pre class="sql">...</pre>       SQL highlighted in place
"""
import re, os, html, sys

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import fdview
import fddefs  # noqa: F401  (registers every relation)
import figures

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'out.html')

for _p in fdview.REG.values():
    _p.check()                      # raises if a hand-written key / NF / decomposition answer is wrong
print('relations checked:', len(fdview.REG))

# ------------------------------------------------------------------ SQL highlight
KW = set('''select from where group by having order asc desc distinct all as join inner left right full outer cross natural
on using union intersect except minus insert into values update set delete create table alter add drop column modify
constraint primary key foreign references unique not null check default cascade restrict no action and or in exists
between like is any some case when then else end limit offset fetch first rows only top with view index grant revoke
to public option commit rollback savepoint transaction begin trigger before after instead of for each row execute
procedure function returns return declare if elsif while loop new old truncate rename comment database schema count sum
avg min max coalesce ifnull nullif cast varchar char int integer decimal numeric date real float number text boolean
auto_increment identity over partition rank dense_rank row_number lag lead escape replace session system privileges
nocheck deferrable initially deferred immediate signal sqlstate message_text referencing statement call merge matched
lower upper length substr substring round year month curdate current_date interval varchar2 delimiter raise_application_error
true false use show describe desc'''.split())
TOKRE = re.compile(r"(--[^\n]*)|('(?:[^']|'')*')|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z_0-9]*)|(\s+)|(.)", re.S)


def hl_sql(code):
    code = code.strip('\n')
    out = []
    for m in TOKRE.finditer(code):
        cm, st, num, word, ws, other = m.groups()
        if cm:
            out.append(f'<span class="cm">{html.escape(cm)}</span>')
        elif st:
            out.append(f'<span class="str">{html.escape(st)}</span>')
        elif num:
            out.append(f'<span class="num">{num}</span>')
        elif word:
            out.append(f'<span class="kw">{word}</span>' if word.lower() in KW else html.escape(word))
        else:
            out.append(html.escape(ws or other))
    return ''.join(out)



def _split(arg):
    if '|' in arg:
        a, c = arg.split('|', 1)
        return a.strip(), c.strip()
    return arg.strip(), ''


HANDLERS = dict(fdview.HANDLERS, svg=lambda n: getattr(figures, n.strip())())


def expand(text):
    text = re.sub(r'<pre class="sql">(.*?)</pre>',
                  lambda m: f'<pre class="sql"><code>{hl_sql(html.unescape(m.group(1)))}</code></pre>', text, flags=re.S)

    def rep(m):
        kind, arg = m.group(1), m.group(2)
        return HANDLERS[kind](arg)
    return re.sub(r'\{\{(\w+):([^}]+)\}\}', rep, text)


# ------------------------------------------------------------------ assemble
def toc(body):
    items = re.findall(r'<h([23]) id="([^"]+)"[^>]*>(.*?)</h\1>', body, re.S)
    out = ['<ul class="toc">']
    open_sub = False
    for lvl, hid, txt in items:
        txt = re.sub(r'<span class="beyond-tag">.*?</span>', '', txt)
        txt = re.sub(r'<[^>]+>', '', txt.replace('</span>', ' </span>')).strip()
        if lvl == '2':
            if open_sub:
                out.append('</ul></li>')
                open_sub = False
            elif len(out) > 1:
                out.append('</li>')
            out.append(f'<li><a href="#{hid}" class="t2">{txt}</a>')
        else:
            if not open_sub:
                out.append('<ul>')
                open_sub = True
            out.append(f'<li><a href="#{hid}" class="t3">{txt}</a></li>')
    out.append('</ul></li>' if open_sub else '</li>')
    out.append('</ul>')
    return ''.join(out)


def main():
    parts_dir = os.path.join(BASE, 'parts')
    body = ''
    for fn in sorted(os.listdir(parts_dir)):
        if fn.endswith('.html') and os.environ.get('PARTS', '') in fn:
            body += open(os.path.join(parts_dir, fn), encoding='utf-8').read() + '\n'
    body = expand(body)
    css = open(os.path.join(BASE, 'style.css'), encoding='utf-8').read()
    js = open(os.path.join(BASE, 'app.js'), encoding='utf-8').read()
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DBMS Unit 4 Notes</title>
<meta name="description" content="DBMS Unit 4 notes: functional dependencies, Armstrong's axioms, closure, keys, minimal cover, 1NF, 2NF, 3NF, BCNF, lossless-join and dependency-preserving decomposition, with every PYQ solved and verified.">
<style>{css}</style>
</head>
<body>
<button class="menu-btn" id="menuBtn" aria-label="Open contents">☰ Contents</button>
<aside class="sidebar" id="sidebar">
  <div class="side-head">
    <a class="side-home" href="../">← All units</a>
    <div class="side-title">DBMS · Unit 4</div>
    <div class="side-tools">
      <button id="themeBtn" title="Toggle light / dark">◐ Theme</button>
      <button id="expandBtn" title="Show / hide all answers">▾ Answers</button>
    </div>
  </div>
  <nav>{toc(body)}</nav>
</aside>
<main class="content" id="content">
{body}
</main>
<script>{js}</script>
</body>
</html>'''
    open(OUT, 'w', encoding='utf-8').write(page)
    left = re.findall(r'\{\{[^}]+\}\}', page)
    print('written', OUT, len(page) // 1024, 'KB', 'unresolved:', left[:5])


if __name__ == '__main__':
    main()
