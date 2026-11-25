#!/usr/bin/env python3
"""Builds the Unit 2 notes (single self-contained HTML).

Placeholders inside parts/*.html:
  {{rel:DB.table}}        a base table of a sample database (PK underlined)
  {{ra:ID}}               RA expression + its computed result        {{rares:ID}} result only
  {{sql:ID}}              SQL code + result computed by SQLite       {{sqlc:ID}} code only   {{sqlr:ID}} result only
  {{svg:NAME}}            figure from figures.py
Inline:
  <ra>\\pi_{sname}(\\sigma_{rating>7}(Sailors))</ra>     RA / calculus mini-notation -> pretty HTML
  <pre class="sql">...</pre>                             SQL highlighted in place (not executed)
"""
import re, os, html, sys, sqlite3

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import data
from ra import R, _key
import figures

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'out.html')

# ------------------------------------------------------------------ RA mini notation
SYM = {
    'pi': 'π', 'sigma': 'σ', 'rho': 'ρ', 'gamma': 'γ', 'G': '𝒢', 'join': '⋈', 'ljoin': '⟕', 'rjoin': '⟖', 'fjoin': '⟗',
    'semi': '⋉', 'anti': '▷', 'x': '×', 'div': '÷', 'cup': '∪', 'cap': '∩', 'minus': '−', 'and': '∧', 'or': '∨',
    'not': '¬', 'ne': '≠', 'le': '≤', 'ge': '≥', 'gets': '←', 'exists': '∃', 'forall': '∀', 'in': '∈',
    'notin': '∉', 'implies': '⇒', 'langle': '⟨', 'rangle': '⟩', 'theta': 'θ', 'subseteq': '⊆', 'empty': '∅',
    'iff': '⇔', 'br': '<br>', 'equiv': '≡', 'quad': '&emsp;', 'to': '→', 'neq': '≠', 'times': '×', 'cdot': '·', 'ldots': '…', 'mid': '|', 'sp': '&nbsp;',
}


def ra2html(s, escape=True):
    if escape:
        s = html.escape(s, quote=False)
    s = s.replace('\\_', '_').replace('\\%', '%').replace('\\ ', ' ')
    s = re.sub(r'\\([A-Za-z]+)', lambda m: SYM.get(m.group(1), m.group(0)), s)
    # subscripts with balanced braces
    out, i = [], 0
    while i < len(s):
        if s[i] == '_' and i + 1 < len(s) and s[i + 1] == '{':
            depth, j = 1, i + 2
            while j < len(s) and depth:
                if s[j] == '{':
                    depth += 1
                elif s[j] == '}':
                    depth -= 1
                j += 1
            out.append('<sub>' + s[i + 2:j - 1] + '</sub>')
            i = j
        else:
            out.append(s[i])
            i += 1
    return ''.join(out)


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


# ------------------------------------------------------------------ tables
def fmt(v):
    if v is None:
        return '<span class="null">NULL</span>'
    if isinstance(v, float):
        if v.is_integer():
            return f'{v:.1f}'
        return ('%.2f' % v).rstrip('0').rstrip('.')
    return html.escape(str(v))


def table_html(attrs, rows, cap='', pk=(), cls='', note='', maxrows=40, sort=True):
    rows = list(rows)
    if sort:
        rows = sorted(rows, key=_key)
    h = [f'<div class="tbl-wrap rel-wrap">']
    if cap:
        h.append(f'<div class="rel-cap">{cap}</div>')
    h.append(f'<table class="tbl rel {cls}">')
    h.append('<thead><tr>' + ''.join(
        f'<th>{"<u>" + html.escape(a) + "</u>" if a in pk else html.escape(a)}</th>' for a in attrs) + '</tr></thead><tbody>')
    for r in rows[:maxrows]:
        h.append('<tr>' + ''.join(f'<td>{fmt(v)}</td>' for v in r) + '</tr>')
    if not rows:
        h.append(f'<tr><td colspan="{len(attrs)}" class="muted center">(empty relation — 0 tuples)</td></tr>')
    if len(rows) > maxrows:
        h.append(f'<tr><td colspan="{len(attrs)}" class="muted">… {len(rows) - maxrows} more rows</td></tr>')
    h.append('</tbody></table>')
    if note:
        h.append(f'<div class="rel-note">{note}</div>')
    h.append('</div>')
    return ''.join(h)


def r_rel(arg):
    db, t = arg.split('.', 1)
    con = data.conn(db)
    cur = con.execute(f'SELECT * FROM {t}')
    attrs = [d[0] for d in cur.description]
    pk = [r[1] for r in con.execute(f'PRAGMA table_info({t})') if r[5]]
    rows = cur.fetchall()
    name = data.DISPLAY.get(t, t)
    return table_html(attrs, rows, cap=f'{name}', pk=pk, sort=False)


# ------------------------------------------------------------------ RA / SQL registry
import qdefs  # noqa: E402  (registers RA and SQL entries, runs checks)


def r_ra(qid, only_result=False):
    q = qdefs.RA[qid]
    res = q['res']
    cap = q.get('cap') or f'Result: {len(res)} tuple{"s" if len(res) != 1 else ""}'
    tbl = table_html(res.attrs, res.rows, cap=cap, cls='result')
    if only_result:
        return tbl
    expr = f'<div class="ra-block">{ra2html(q["expr"])}</div>'
    return f'<div class="ra-ex">{expr}{tbl}</div>'


def r_rares(qid):
    return r_ra(qid, True)


def r_sql(qid, mode='both'):
    q = qdefs.SQL[qid]
    code = f'<pre class="sql"><code>{hl_sql(q["sql"])}</code></pre>'
    if mode == 'code':
        return code
    attrs, rows = q['res']
    cap = q.get('cap') or f'Output on the sample data: {len(rows)} row{"s" if len(rows) != 1 else ""}'
    tbl = table_html(attrs, rows, cap=cap, cls='result', sort=q.get('sort', False))
    if mode == 'res':
        return tbl
    return f'<div class="sql-ex">{code}{tbl}</div>'


def r_viol(vid):
    v = qdefs.VIOL[vid]
    h = ['<div class="tbl-wrap"><table class="tbl small viol"><tr><th>Statement</th><th>DBMS response</th><th>Why</th></tr>']
    for st, got, why in v['rows']:
        badge = '<span class="chip good">accepted</span>' if got == 'ok' else '<span class="chip bad">rejected — error</span>'
        h.append(f'<tr><td><code>{html.escape(st)}</code></td><td>{badge}</td><td>{why}</td></tr>')
    h.append('</table></div>')
    if v['after']:
        attrs, rows = v['after']
        h.append(table_html(attrs, rows, cap='Table contents afterwards', cls='result', sort=False))
    return ''.join(h)


HANDLERS = dict(viol=r_viol, rel=r_rel, ra=r_ra, rares=r_rares, sql=r_sql,
                sqlc=lambda a: r_sql(a, 'code'), sqlr=lambda a: r_sql(a, 'res'),
                svg=lambda n: getattr(figures, n)())


def expand(text):
    text = re.sub(r'<ra>(.*?)</ra>', lambda m: f'<span class="ra">{ra2html(m.group(1))}</span>', text, flags=re.S)
    text = re.sub(r'<rab>(.*?)</rab>', lambda m: f'<div class="ra-block">{ra2html(m.group(1))}</div>', text, flags=re.S)
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
<title>DBMS Unit 2 Notes</title>
<meta name="description" content="Complete notes for DBMS Unit 2: relational model, integrity constraints, relational algebra and calculus, SQL (DDL, DML, DCL, joins, aggregates, subqueries), triggers and NoSQL, with topic-wise solved PYQs.">
<style>{css}</style>
</head>
<body>
<button class="menu-btn" id="menuBtn" aria-label="Open contents">☰ Contents</button>
<aside class="sidebar" id="sidebar">
  <div class="side-head">
    <a class="side-home" href="../">← All units</a>
    <div class="side-title">DBMS · Unit 2</div>
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
