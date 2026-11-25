"""Hand-designed figures for Unit 2 (inline SVG, theme-aware via CSS classes)."""
import math
from svglib import markers, uid, esc


class Fig:
    def __init__(self, w, h, label='figure', maxw=None):
        self.mid = uid()
        self.w, self.h = w, h
        self.label = label
        self.maxw = maxw or w
        self.p = []
        self.defs = []

    def box(self, x, y, w, h, text='', cls='', rx=10, tcls='t', fs=None, lh=16):
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="bx {cls}"/>')
        if text:
            self.text(x + w / 2, y + h / 2, text, tcls, fs=fs, lh=lh)

    def text(self, x, y, s, cls='t', anchor='middle', fs=None, lh=16):
        lines = s.split('\n')
        st = f' style="font-size:{fs}px"' if fs else ''
        for k, ln in enumerate(lines):
            dy = (k - (len(lines) - 1) / 2) * lh
            self.p.append(f'<text x="{x:.1f}" y="{y + dy:.1f}" class="{cls}" text-anchor="{anchor}" '
                          f'dominant-baseline="central"{st}>{esc(ln)}</text>')

    def line(self, x1, y1, x2, y2, cls='ln'):
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}"/>')

    def poly(self, pts, cls='ln', close=False):
        d = ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        tag = 'polygon' if close else 'polyline'
        fill = '' if close else ' fill="none"'
        self.p.append(f'<{tag} points="{d}" class="{cls}"{fill}/>')

    def arrow(self, x1, y1, x2, y2, c='ink', dash=False, curve=0, both=False, w=None):
        d = ' dashed' if dash else ''
        sw = f' style="stroke-width:{w}"' if w else ''
        ms = f' marker-start="url(#{self.mid}-{c})"' if both else ''
        if curve:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1
            cx, cy = mx - dy / L * curve, my + dx / L * curve
            self.p.append(f'<path d="M{x1},{y1} Q{cx:.1f},{cy:.1f} {x2},{y2}" class="edge e-{c}{d}"{sw} '
                          f'marker-end="url(#{self.mid}-{c})"{ms}/>')
        else:
            self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge e-{c}{d}"{sw} '
                          f'marker-end="url(#{self.mid}-{c})"{ms}/>')

    def circle(self, cx, cy, r, cls='node'):
        self.p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" class="{cls}"/>')

    def ellipse(self, cx, cy, rx, ry, cls='bx'):
        self.p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" class="{cls}"/>')

    def raw(self, s):
        self.p.append(s)

    def grid(self, x, y, cols, rows, cw, rh, header_cls='bx-mut', cell_cls='bx-plain', hl_rows=(), hl_cols=(),
             hl_cls='bx-acc', fs=12.5, dim_rows=(), dim_cls='bx-mut'):
        """draw a small table; cols = list of header strings (or widths list via cw list)"""
        cws = cw if isinstance(cw, (list, tuple)) else [cw] * len(cols)
        xx = x
        for j, hdr in enumerate(cols):
            self.p.append(f'<rect x="{xx}" y="{y}" width="{cws[j]}" height="{rh}" class="bx {header_cls}" rx="0"/>')
            self.text(xx + cws[j] / 2, y + rh / 2, hdr, 't tb', fs=fs)
            xx += cws[j]
        for i, row in enumerate(rows):
            xx = x
            yy = y + rh * (i + 1)
            for j, v in enumerate(row):
                c = cell_cls
                if i in hl_rows or j in hl_cols:
                    c = hl_cls
                if i in dim_rows:
                    c = dim_cls
                self.p.append(f'<rect x="{xx}" y="{yy}" width="{cws[j]}" height="{rh}" class="bx {c}" rx="0"/>')
                self.text(xx + cws[j] / 2, yy + rh / 2, str(v), 't', fs=fs)
                xx += cws[j]
        return sum(cws), rh * (len(rows) + 1)

    def render(self, caption=''):
        defs = ''.join(self.defs)
        svg = (f'<svg class="fig-svg" viewBox="0 0 {self.w} {self.h}" style="max-width:{self.maxw}px" role="img" '
               f'aria-label="{esc(self.label)}">' + markers(self.mid) + (f'<defs>{defs}</defs>' if defs else '') +
               ''.join(self.p) + '</svg>')
        cap = f'<figcaption>{caption}</figcaption>' if caption else ''
        return f'<figure class="fig">{svg}{cap}</figure>'


# ================================================================== intro
def roadmap():
    f = Fig(920, 300, 'Unit 2 roadmap')
    f.box(300, 10, 320, 50, 'RELATIONAL DATA MODEL & SQL\n(how data is stored, protected and queried)', 'bx-acc', tcls='t tb', fs=13)
    cols = [('1. Relational model', 'tables, tuples, domains\nkeys · NULL\nCodd’s 12 rules', ''),
            ('2. Integrity constraints', 'domain · key · entity\nreferential (FK)\nhow they are enforced', 'bx-good'),
            ('3–4. Formal languages', 'Relational ALGEBRA\n(procedural)\nRelational CALCULUS\n(TRC, DRC — declarative)', 'bx-warn'),
            ('5–11. SQL', 'DDL · DML · DCL · TCL\nSELECT · aggregates\nGROUP BY · HAVING\njoins · subqueries\ntriggers', 'bx-pur'),
            ('12. NoSQL', 'key-value · document\ncolumn · graph\nCAP · BASE\nSQL vs NoSQL', 'bx-bad')]
    for k, (h, body, c) in enumerate(cols):
        x = 15 + k * 180
        f.box(x, 105, 168, 36, h, c, tcls='t tb', fs=13)
        f.box(x, 150, 168, 100, body, '', tcls='t ts', lh=17)
        f.arrow(460, 60, x + 84, 103, 'mut')
    f.text(460, 280, 'RA and RC are the theory SQL is built on — learn RA first and SQL becomes easy (and vice-versa).', 't ts')
    return f.render('The whole unit on one page. Sections 3–4 (algebra &amp; calculus) get the most space because PYQs ask them every year.')


# ================================================================== section 1
def relation_anatomy():
    f = Fig(900, 360, 'anatomy of a relation')
    x0, y0 = 170, 95
    cws = [110, 120, 80, 130]
    rows = [(101, 'Aman', 20, 'Delhi'), (102, 'Chirag', 21, 'Noida'), (103, 'Dev', 19, 'Delhi'), (104, 'Riya', 20, 'Pune')]
    f.grid(x0, y0, ['Roll_No', 'Name', 'Age', 'City'], rows, cws, 34, hl_rows=(1,), hl_cls='bx-warn')
    # PK underline
    f.line(x0 + 25, y0 + 26, x0 + 85, y0 + 26, 'ln')
    W = sum(cws)
    f.text(x0 + W / 2, 30, 'Relation (table) name:  STUDENT', 't tb')
    f.text(x0 + W / 2, 55, 'Schema:  STUDENT(Roll_No, Name, Age, City)', 't ts')
    # attribute label
    f.arrow(x0 + 300, 78, x0 + 270, 94, 'acc')
    f.text(x0 + 310, 72, 'attribute = column (field)', 't ts tacc', anchor='start')
    # tuple label
    f.arrow(x0 - 18, y0 + 34 * 2 + 17, x0 - 2, y0 + 34 * 2 + 17, 'acc')
    f.text(x0 - 22, y0 + 34 * 2 + 17, 'tuple = row\n(record)', 't ts tacc', anchor='end')
    f.text(x0 - 22, y0 + 17, 'primary key\n(underlined)', 't ts', anchor='end')
    f.arrow(x0 - 18, y0 + 17, x0 + 20, y0 + 22, 'mut')
    # degree
    yb = y0 + 34 * 5 + 18
    f.arrow(x0, yb, x0 + W, yb, 'ink', both=True)
    f.text(x0 + W / 2, yb + 18, 'DEGREE (arity) = number of attributes = 4', 't ts tb')
    # cardinality
    xr = x0 + W + 18
    f.arrow(xr, y0 + 34, xr, y0 + 34 * 5, 'ink', both=True)
    f.text(xr + 10, y0 + 34 * 3, 'CARDINALITY = number\nof tuples = 4\n(changes with time)', 't ts tb', anchor='start')
    # domain
    f.text(x0 + 250, y0 + 34 * 5 + 62, 'Domain of Age = set of allowed atomic values (e.g. integers 17–60)  ·  each cell holds ONE atomic value  ·  the table contents at a moment = an INSTANCE', 't ts')
    return f.render('Every term of the relational model on one table. <b>Schema</b> = the structure (rarely changes); <b>instance</b> = the rows present right now (changes all the time).')


def keys_venn():
    f = Fig(900, 300, 'super key, candidate key, primary key')
    f.ellipse(230, 150, 215, 135, 'bx bx-mut')
    f.ellipse(255, 170, 150, 92, 'bx bx-warn')
    f.ellipse(215, 185, 70, 42, 'bx bx-acc')
    f.text(230, 35, 'SUPER KEYS', 't tb')
    f.text(230, 55, 'any set of attributes that identifies a tuple', 't tx')
    f.text(262, 104, 'CANDIDATE KEYS', 't tb')
    f.text(262, 122, 'minimal super keys', 't tx')
    f.text(215, 178, 'PRIMARY KEY', 't tb', fs=13)
    f.text(215, 196, 'one chosen candidate', 't tx')
    f.text(340, 192, 'alternate', 't ts tb')
    f.text(340, 208, 'keys', 't ts tb')
    # example
    X = 480
    f.box(X, 20, 405, 260, '', 'bx-plain')
    f.text(X + 202, 42, 'Example: STUDENT(Roll, Email, Aadhaar, Name)', 't tb ts')
    lines = [('Super keys (some):', '{Roll}, {Email}, {Aadhaar}, {Roll, Name},', '{Email, Name}, {Roll, Email, Name} …'),
             ('Candidate keys:', '{Roll}, {Email}, {Aadhaar}', '(no proper subset is a key)'),
             ('Primary key:', '{Roll}  (chosen by the designer)', ''),
             ('Alternate keys:', '{Email}, {Aadhaar}  = candidate − primary', ''),
             ('NOT a key:', '{Name} — two students can share a name', '')]
    y = 72
    for h, a, b in lines:
        f.text(X + 14, y, h, 't ts tb', anchor='start')
        f.text(X + 140, y, a, 't ts', anchor='start')
        if b:
            f.text(X + 140, y + 17, b, 't ts', anchor='start')
            y += 17
        y += 34
    return f.render('Every primary key is a candidate key and every candidate key is a super key — but not the other way round.')


def ic_tree():
    f = Fig(920, 250, 'classification of integrity constraints')
    f.box(330, 8, 260, 40, 'INTEGRITY CONSTRAINTS', 'bx-acc', tcls='t tb')
    kids = [('Domain', 'data type · NOT NULL\nCHECK · DEFAULT', 'single attribute'),
            ('Key', 'PRIMARY KEY\nUNIQUE', 'no two tuples equal'),
            ('Entity integrity', 'primary key\nvalue ≠ NULL', 'every row identifiable'),
            ('Referential', 'FOREIGN KEY …\nREFERENCES', 'between two tables'),
            ('General / semantic', 'CHECK on table,\nASSERTION, TRIGGER', 'business rules')]
    for k, (h, b, s) in enumerate(kids):
        x = 10 + k * 182
        c = ['', 'bx-warn', 'bx-good', 'bx-pur', 'bx-mut'][k]
        f.box(x, 90, 170, 34, h, c, tcls='t tb', fs=13.5)
        f.box(x, 132, 170, 54, b, '', tcls='t ts', lh=17)
        f.text(x + 85, 202, s, 't tx')
        f.arrow(460, 48, x + 85, 88, 'mut')
    f.text(460, 232, 'Intra-relation: domain, key, entity  ·  Inter-relation: referential  ·  All are declared once (DDL) and checked by the DBMS on every INSERT / UPDATE / DELETE', 't ts')
    return f.render('The four classic constraints (domain, key, entity, referential) plus general constraints.')


def fk_actions():
    f = Fig(920, 330, 'referential actions on delete')
    # parent
    f.text(120, 18, 'PARENT  department', 't tb ts')
    f.grid(40, 30, ['dept_id', 'dname'], [(10, 'Sales'), (20, 'IT')], [70, 90], 28, hl_rows=(0,), hl_cls='bx-bad')
    f.text(120, 128, 'DELETE dept 10', 't ts tbad tb')
    f.text(400, 18, 'CHILD  employee (dept_id is FK)', 't tb ts')
    f.grid(310, 30, ['emp', 'dept_id'], [('Aman', 10), ('Bela', 20), ('Chirag', 10)], [90, 80], 28, hl_rows=(0, 2), hl_cls='bx-warn')
    f.arrow(308, 72, 202, 72, 'acc')
    f.text(256, 60, 'references', 't tx')
    f.text(690, 40, 'FK value must be NULL or', 't ts', anchor='middle')
    f.text(690, 58, 'match an existing PK value', 't ts', anchor='middle')
    panels = [('ON DELETE RESTRICT / NO ACTION', [('Aman', 10), ('Bela', 20), ('Chirag', 10)], 'delete REJECTED (error)\nparent row stays', 'bx-bad'),
              ('ON DELETE CASCADE', [('Bela', 20)], 'children deleted too', 'bx-warn'),
              ('ON DELETE SET NULL', [('Aman', 'NULL'), ('Bela', 20), ('Chirag', 'NULL')], 'children kept,\nFK set to NULL', 'bx-good'),
              ('ON DELETE SET DEFAULT', [('Aman', 99), ('Bela', 20), ('Chirag', 99)], 'FK set to default (99)\n(99 must exist in parent)', 'bx-pur')]
    for k, (h, rows, note, c) in enumerate(panels):
        x = 10 + k * 228
        f.box(x, 160, 218, 28, h, c, tcls='t tb', fs=11.5, rx=6)
        f.grid(x + 29, 196, ['emp', 'dept_id'], rows, [80, 80], 24, fs=12)
        f.text(x + 109, 305, note, 't tx', lh=14)
    return f.render('What the DBMS does to the CHILD rows when a referenced PARENT row is deleted, for each referential action.')


def cascade_chain():
    f = Fig(760, 210, 'cascading deletes for the 2024 PYQ')
    nodes = {'(2,4)': (90, 105), '(5,2)': (300, 55), '(7,2)': (300, 155), '(9,5)': (510, 55)}
    for n, (x, y) in nodes.items():
        c = 'bx-bad' if n == '(2,4)' else 'bx-warn'
        f.box(x - 45, y - 20, 90, 40, n, c, tcls='t tb')
    f.arrow(255, 55, 137, 98, 'bad')
    f.arrow(255, 155, 137, 112, 'bad')
    f.arrow(465, 55, 347, 55, 'bad')
    f.text(196, 62, 'C=2 refers A=2', 't tx', anchor='middle')
    f.text(196, 150, 'C=2 refers A=2', 't tx', anchor='middle')
    f.text(406, 40, 'C=5 refers A=5', 't tx')
    f.text(90, 145, 'deleted by user', 't ts tbad')
    f.box(570, 120, 180, 70, 'no tuple has C = 7\nor C = 9 → chain\nstops here', 'bx-mut', tcls='t ts', lh=16)
    return f.render('Arrows point from a child tuple to the parent tuple it references. Deleting (2,4) cascades along the reversed arrows: (5,2), (7,2), then (9,5).')


# ================================================================== section 3 (RA)
def query_langs():
    f = Fig(920, 250, 'classification of query languages')
    f.box(350, 10, 220, 40, 'QUERY LANGUAGES', 'bx-acc', tcls='t tb')
    f.box(40, 90, 330, 54, 'PROCEDURAL — say WHAT and HOW\n(sequence of operations)', 'bx-warn', tcls='t ts tb')
    f.box(550, 90, 330, 54, 'NON-PROCEDURAL / DECLARATIVE\nsay only WHAT you want', 'bx-good', tcls='t ts tb')
    f.arrow(410, 50, 205, 88, 'mut')
    f.arrow(510, 50, 715, 88, 'mut')
    f.box(80, 170, 250, 40, 'Relational Algebra (RA)', '', tcls='t tb')
    f.box(500, 170, 190, 40, 'Tuple Rel. Calculus', '', tcls='t tb ts')
    f.box(700, 170, 200, 40, 'Domain Rel. Calculus', '', tcls='t tb ts')
    f.arrow(205, 144, 205, 168, 'mut')
    f.arrow(680, 144, 595, 168, 'mut')
    f.arrow(750, 144, 800, 168, 'mut')
    f.text(205, 228, 'operators: σ π ∪ − × ρ (+ ⋈ ∩ ÷ …)', 't tx')
    f.text(595, 228, '{ t | P(t) }  → basis of SQL', 't tx')
    f.text(800, 228, '{ ⟨x,y⟩ | P }  → basis of QBE', 't tx')
    return f.render('RA, TRC and DRC are <b>formal</b> (mathematical) languages; SQL is the <b>commercial</b> language that mixes ideas from RA and TRC.')


def sel_proj():
    f = Fig(900, 240, 'selection vs projection')
    rows = [('22', 'Dustin', '7', '45'), ('31', 'Lubber', '8', '55.5'), ('58', 'Rusty', '10', '35'), ('85', 'Art', '3', '25.5')]
    cols = ['sid', 'sname', 'rating', 'age']
    f.text(205, 15, 'σ rating > 7 (Sailors)  — picks ROWS', 't tb ts')
    f.grid(40, 30, cols, rows, [70, 100, 80, 80], 30, hl_rows=(1, 2), hl_cls='bx-acc', dim_rows=(0, 3), dim_cls='bx-mut op50')
    f.text(205, 200, 'horizontal subset · degree unchanged', 't tx')
    f.text(205, 218, 'cardinality ≤ original', 't tx')
    f.text(675, 15, 'π sname, rating (Sailors)  — picks COLUMNS', 't tb ts')
    f.grid(500, 30, cols, rows, [70, 100, 80, 80], 30, hl_cols=(1, 2), hl_cls='bx-good')
    for i in range(5):
        f.p.append(f'<rect x="500" y="{30 + 30 * i}" width="70" height="30" class="bx bx-mut op50" rx="0"/>')
        f.p.append(f'<rect x="750" y="{30 + 30 * i}" width="80" height="30" class="bx bx-mut op50" rx="0"/>')
    f.text(675, 200, 'vertical subset · duplicates removed', 't tx')
    f.text(675, 218, 'degree = no. of listed attributes', 't tx')
    return f.render('<b>σ (select)</b> keeps the highlighted rows; <b>π (project)</b> keeps the highlighted columns.')


def _venn(f, cx, cy, label, mode):
    r = 46
    a, b = cx - 26, cx + 26
    cid = uid()
    f.defs.append(f'<clipPath id="{cid}a"><circle cx="{a}" cy="{cy}" r="{r}"/></clipPath>'
                  f'<clipPath id="{cid}b"><circle cx="{b}" cy="{cy}" r="{r}"/></clipPath>')
    shade = 'bx-acc'
    if mode in ('union', 'full'):
        f.circle(a, cy, r, f'bx {shade}')
        f.circle(b, cy, r, f'bx {shade}')
    elif mode in ('left',):
        f.circle(a, cy, r, f'bx {shade}')
        f.circle(b, cy, r, 'bx bx-plain')
        f.raw(f'<circle cx="{a}" cy="{cy}" r="{r}" class="bx {shade}" clip-path="url(#{cid}b)"/>')
    elif mode in ('right',):
        f.circle(b, cy, r, f'bx {shade}')
        f.circle(a, cy, r, 'bx bx-plain')
        f.raw(f'<circle cx="{b}" cy="{cy}" r="{r}" class="bx {shade}" clip-path="url(#{cid}a)"/>')
    elif mode in ('inter', 'inner'):
        f.circle(a, cy, r, 'bx bx-plain')
        f.circle(b, cy, r, 'bx bx-plain')
        f.raw(f'<circle cx="{a}" cy="{cy}" r="{r}" class="bx {shade}" clip-path="url(#{cid}b)"/>')
    elif mode == 'diff':
        f.circle(a, cy, r, f'bx {shade}')
        f.raw(f'<circle cx="{b}" cy="{cy}" r="{r}" class="bx bx-plain"/>')
    # outlines on top
    f.raw(f'<circle cx="{a}" cy="{cy}" r="{r}" fill="none" class="ln"/>')
    f.raw(f'<circle cx="{b}" cy="{cy}" r="{r}" fill="none" class="ln"/>')
    f.text(a - 22, cy, 'R' if mode in ('union', 'inter', 'diff') else 'L', 't tb')
    f.text(b + 22, cy, 'S' if mode in ('union', 'inter', 'diff') else 'R', 't tb')
    f.text(cx, cy + r + 20, label, 't tb ts')


def setops():
    f = Fig(780, 165, 'set operations')
    _venn(f, 130, 65, 'R ∪ S  (in either)', 'union')
    _venn(f, 390, 65, 'R ∩ S  (in both)', 'inter')
    _venn(f, 650, 65, 'R − S  (in R, not in S)', 'diff')
    return f.render('Shaded = tuples in the result. R and S must be <b>union-compatible</b>: same number of attributes, with compatible domains, position by position.')


def join_venn():
    f = Fig(920, 170, 'join types')
    for k, (lab, mode) in enumerate([('INNER JOIN — matches only', 'inner'), ('LEFT OUTER — all of left', 'left'),
                                     ('RIGHT OUTER — all of right', 'right'), ('FULL OUTER — all of both', 'full')]):
        _venn(f, 115 + k * 230, 65, lab, mode)
    return f.render('A common memory aid (L = left table, R = right table). The overlap stands for <i>matching</i> rows; unmatched rows of a preserved side appear padded with NULLs. (Venn diagrams are only an analogy — a join combines columns, it is not a set intersection.)')


def division_visual():
    f = Fig(760, 280, 'division')
    studs = ['S1', 'S2', 'S3', 'S4']
    crs = [('C1', True), ('C2', True), ('C3', False)]
    pairs = [('S1', 'C1'), ('S1', 'C2'), ('S1', 'C3'), ('S2', 'C1'), ('S2', 'C3'), ('S3', 'C2'), ('S4', 'C1'), ('S4', 'C2')]
    sy = {s: 50 + 55 * i for i, s in enumerate(studs)}
    cy = {c: 80 + 65 * i for i, (c, _) in enumerate(crs)}
    for s, c in pairs:
        good = s in ('S1', 'S4') and c in ('C1', 'C2')
        f.line(150, sy[s], 400, cy[c], 'ln-acc' if good else 'ln-mut')
    for s in studs:
        f.box(90, sy[s] - 17, 60, 34, s, 'bx-good' if s in ('S1', 'S4') else 'bx-mut', tcls='t tb')
    for c, req in crs:
        f.box(400, cy[c] - 17, 60, 34, c, 'bx-warn' if req else 'bx-mut', tcls='t tb')
    f.text(120, 18, 'Enrolled.sid', 't ts tb')
    f.text(430, 18, 'cid', 't ts tb')
    f.box(500, 40, 245, 210, '', 'bx-plain')
    f.text(622, 62, 'Enrolled ÷ Course', 't tb')
    f.text(515, 92, 'Course (divisor) = {C1, C2}', 't ts', anchor='start')
    f.text(515, 118, 'S1 → C1 ✔  C2 ✔  (C3 extra, OK)', 't ts tgood', anchor='start')
    f.text(515, 142, 'S2 → C1 ✔  C2 ✘', 't ts tbad', anchor='start')
    f.text(515, 166, 'S3 → C1 ✘  C2 ✔', 't ts tbad', anchor='start')
    f.text(515, 190, 'S4 → C1 ✔  C2 ✔', 't ts tgood', anchor='start')
    f.text(515, 222, 'Result = { S1, S4 }', 't tb', anchor='start')
    return f.render('R ÷ S returns the x-values that are paired in R with <b>every</b> tuple of S. Extra partners (S1–C3) do not matter; a single missing partner disqualifies.')


def query_tree():
    f = Fig(820, 330, 'query tree')
    # nodes: (label, x, y, cls)
    N = {'p': ('π sname', 300, 30, 'bx-good'), 'j2': ('⋈ (sid)', 300, 100, 'bx-acc'), 'j1': ('⋈ (bid)', 190, 170, 'bx-acc'),
         's': ('σ color=\'red\'', 110, 240, 'bx-warn'), 'B': ('Boats', 110, 305, 'bx-mut'), 'R': ('Reserves', 270, 240, 'bx-mut'),
         'S': ('Sailors', 410, 170, 'bx-mut')}
    E = [('p', 'j2'), ('j2', 'j1'), ('j2', 'S'), ('j1', 's'), ('j1', 'R'), ('s', 'B')]
    for a, b in E:
        _, x1, y1, _ = N[a]
        _, x2, y2, _ = N[b]
        f.line(x1, y1 + 16, x2, y2 - 16, 'ln')
    for k, (lab, x, y, c) in N.items():
        f.box(x - 62, y - 16, 124, 32, lab, c, tcls='t tb', fs=13)
    f.box(520, 40, 290, 250, '', 'bx-plain')
    f.text(665, 62, 'Read it bottom-up', 't tb')
    steps = ['1. σ: keep only red boats (102, 104)', '2. ⋈ Reserves on bid → who', '    reserved a red boat, when',
             '3. ⋈ Sailors on sid → attach', '    the sailor’s details', '4. π sname → keep the column', '    asked for (duplicates go)']
    for i, s in enumerate(steps):
        f.text(535, 92 + i * 26, s, 't ts', anchor='start')
    return f.render('The expression π<sub>sname</sub>(σ<sub>color=\'red\'</sub>(Boats) ⋈ Reserves ⋈ Sailors) as a <b>query tree</b>: leaves are relations, inner nodes are operators, data flows upward.')


def ra_sql_map():
    f = Fig(900, 300, 'relational algebra to SQL')
    rows = [('π A1, A2', 'SELECT DISTINCT A1, A2', 'projection ↔ SELECT list'),
            ('σ condition', 'WHERE condition', 'selection ↔ WHERE'),
            ('R × S', 'FROM R, S   /   R CROSS JOIN S', 'product ↔ comma in FROM'),
            ('R ⋈θ S', 'FROM R JOIN S ON θ', 'join ↔ JOIN … ON'),
            ('R ∪ S,  R ∩ S,  R − S', 'UNION, INTERSECT, EXCEPT (MINUS)', 'set operators'),
            ('ρ X(R)', 'FROM R AS X  /  col AS new', 'rename ↔ alias'),
            ('G γ F(A) (R)', 'GROUP BY G … F(A)', 'aggregation'),
            ('R ÷ S', 'NOT EXISTS (… EXCEPT …)', 'no direct keyword!')]
    f.box(20, 10, 230, 30, 'Relational algebra', 'bx-warn', tcls='t tb')
    f.box(300, 10, 330, 30, 'SQL', 'bx-pur', tcls='t tb')
    for i, (a, b, c) in enumerate(rows):
        y = 50 + i * 31
        f.box(20, y, 230, 27, a, 'bx-plain', tcls='t ts tb', rx=6)
        f.arrow(252, y + 13, 297, y + 13, 'mut')
        f.box(300, y, 330, 27, b, 'bx-plain', tcls='t ts', rx=6)
        f.text(645, y + 13, c, 't tx', anchor='start')
    return f.render('Each RA operator has an SQL counterpart. Important difference: SQL keeps duplicates unless you write DISTINCT; RA never has duplicates.')


def calc_triangle():
    f = Fig(820, 290, 'expressive power')
    f.box(320, 15, 180, 46, 'Relational Algebra', 'bx-warn', tcls='t tb')
    f.box(80, 190, 200, 46, 'safe Tuple Calculus', 'bx-good', tcls='t tb')
    f.box(540, 190, 200, 46, 'safe Domain Calculus', 'bx-good', tcls='t tb')
    f.arrow(320, 55, 220, 188, 'acc', both=True)
    f.arrow(500, 55, 600, 188, 'acc', both=True)
    f.arrow(282, 213, 538, 213, 'acc', both=True)
    f.text(410, 135, 'Codd’s theorem:', 't tb ts')
    f.text(410, 155, 'all three are EQUALLY expressive', 't ts')
    f.text(410, 175, '(“relationally complete”)', 't tx')
    f.text(180, 255, 'SQL is modelled on TRC', 't tx')
    f.text(640, 255, 'QBE is modelled on DRC', 't tx')
    f.text(410, 280, 'Any query written in one can be translated into the other two.', 't tx')
    return f.render('Safe relational calculus and relational algebra can express exactly the same set of queries.')


# ================================================================== SQL
def sql_sublang():
    f = Fig(920, 245, 'SQL sub-languages')
    f.box(390, 8, 140, 38, 'SQL', 'bx-acc', tcls='t tb')
    kids = [('DDL', 'Data Definition', 'CREATE · ALTER\nDROP · TRUNCATE\nRENAME · COMMENT', 'bx-warn'),
            ('DQL', 'Data Query', 'SELECT', 'bx-good'),
            ('DML', 'Data Manipulation', 'INSERT · UPDATE\nDELETE · MERGE\n(+ SELECT)', 'bx-good'),
            ('DCL', 'Data Control', 'GRANT\nREVOKE', 'bx-pur'),
            ('TCL', 'Transaction Control', 'COMMIT · ROLLBACK\nSAVEPOINT', 'bx-bad')]
    for k, (h, sub, cmds, c) in enumerate(kids):
        x = 10 + k * 182
        f.box(x, 80, 170, 46, f'{h}\n{sub}', c, tcls='t tb ts', lh=17)
        f.box(x, 134, 170, 70, cmds, '', tcls='t ts', lh=17)
        f.arrow(460, 46, x + 85, 78, 'mut')
    f.text(460, 228, 'DDL works on the STRUCTURE (schema) · DML/DQL on the DATA · DCL on PERMISSIONS · TCL on TRANSACTIONS', 't ts')
    return f.render('Many books put SELECT inside DML; others (and your course PDF) list it separately as DQL. Either is accepted.')


def sql_order():
    f = Fig(920, 210, 'logical order of SQL clauses')
    written = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY', 'LIMIT']
    f.text(20, 22, 'Written order:', 't ts tb', anchor='start')
    for i, w in enumerate(written):
        f.box(140 + i * 110, 8, 100, 28, w, 'bx-mut', tcls='t ts tb', rx=6)
    f.text(20, 92, 'Executed order:', 't ts tb', anchor='start')
    seq = [('FROM / JOIN', 'build rows'), ('WHERE', 'filter rows'), ('GROUP BY', 'make groups'), ('HAVING', 'filter groups'),
           ('SELECT', 'compute cols'), ('DISTINCT', 'drop dups'), ('ORDER BY', 'sort'), ('LIMIT', 'cut')]
    for i, (a, b) in enumerate(seq):
        x = 140 + i * 97
        c = 'bx-acc' if a in ('WHERE', 'HAVING') else ('bx-good' if a == 'SELECT' else '')
        f.box(x, 72, 88, 40, a, c, tcls='t ts tb', rx=6)
        f.text(x + 44, 126, b, 't tx')
        f.text(x + 44, 60, str(i + 1), 't tx tb')
        if i:
            f.arrow(x - 9, 92, x - 1, 92, 'ink')
    f.text(460, 160, 'Consequences:  ① WHERE cannot use aggregates (groups do not exist yet)  ② WHERE cannot use a SELECT alias', 't ts')
    f.text(460, 182, '③ HAVING / ORDER BY can use aggregates  ④ ORDER BY can use SELECT aliases (it runs after SELECT)', 't ts')
    return f.render('The order in which a query is <i>written</i> is not the order in which it is <i>evaluated</i>. Knowing the real order explains almost every SQL rule.')


def groupby_visual():
    f = Fig(920, 270, 'GROUP BY and HAVING')
    rows = [('IT', 'Aarav', 95), ('Sales', 'Meera', 64), ('IT', 'Diya', 72), ('HR', 'Ishaan', 45), ('Sales', 'Rohan', 48),
            ('IT', 'Kabir', 72), ('Sales', 'Sara', 51)]
    f.text(120, 14, 'employee (after WHERE)', 't ts tb')
    f.grid(20, 26, ['dept', 'name', 'sal (k)'], rows, [70, 70, 60], 26, fs=12)
    f.arrow(212, 125, 262, 125, 'ink')
    f.text(237, 110, 'GROUP BY dept', 't tx')
    groups = [('IT', [('Aarav', 95), ('Diya', 72), ('Kabir', 72)], 'bx-acc'), ('Sales', [('Meera', 64), ('Rohan', 48), ('Sara', 51)], 'bx-warn'),
              ('HR', [('Ishaan', 45)], 'bx-pur')]
    y = 22
    for g, members, c in groups:
        h = 22 * len(members) + 8
        f.box(270, y, 190, h, '', c, rx=8)
        f.text(290, y + h / 2, g, 't tb ts', anchor='start')
        for i, (n, s) in enumerate(members):
            f.text(345, y + 15 + 22 * i, f'{n}  {s}', 't ts', anchor='start')
        y += h + 10
    f.arrow(465, 125, 515, 125, 'ink')
    f.text(490, 110, 'aggregate', 't tx')
    f.grid(525, 50, ['dept', 'COUNT(*)', 'AVG(sal)'], [('IT', 3, '79.7'), ('Sales', 3, '54.3'), ('HR', 1, '45.0')], [70, 80, 80], 28, fs=12)
    f.arrow(760, 125, 800, 125, 'ink')
    f.text(780, 104, 'HAVING', 't tx')
    f.text(780, 116, 'COUNT(*)>1', 't tx')
    f.grid(808, 78, ['dept', 'n'], [('IT', 3), ('Sales', 3)], [55, 45], 28, fs=12)
    f.text(460, 250, 'One output row per GROUP.  HAVING removes whole groups (HR has only 1 employee), WHERE had removed individual rows earlier.', 't ts')
    return f.render('How <code>GROUP BY dept … HAVING COUNT(*) &gt; 1</code> turns rows into groups and groups into result rows.')


def correlated():
    f = Fig(900, 250, 'correlated subquery execution')
    f.box(20, 70, 210, 90, 'OUTER query\ntakes the next row e\n(e.g. Meera, dept 10)', 'bx-acc', tcls='t ts', lh=18)
    f.box(320, 70, 250, 90, 'INNER query runs again\nwith e.dept_id = 10:\nAVG(salary) of dept 10 = 54333', 'bx-warn', tcls='t ts', lh=18)
    f.box(660, 70, 220, 90, 'compare:\n64000 > 54333 ?\nTRUE → output Meera', 'bx-good', tcls='t ts', lh=18)
    f.arrow(232, 115, 318, 115, 'ink')
    f.arrow(572, 115, 658, 115, 'ink')
    f.arrow(770, 162, 130, 162, 'mut', curve=-55)
    f.text(450, 232, 'repeat for EVERY row of the outer table', 't ts tb')
    f.text(275, 100, 'passes e', 't tx')
    f.text(615, 100, 'value', 't tx')
    return f.render('A <b>correlated</b> subquery refers to a column of the outer query, so (logically) it is re-evaluated once per outer row. A <b>non-correlated</b> subquery runs once.')


def trigger_flow():
    f = Fig(920, 250, 'trigger timing')
    f.box(10, 90, 150, 60, 'INSERT / UPDATE /\nDELETE issued', 'bx-mut', tcls='t ts tb', lh=17)
    f.box(200, 90, 170, 60, 'BEFORE trigger\ncheck / modify NEW\nor reject', 'bx-warn', tcls='t ts', lh=17)
    f.box(410, 90, 170, 60, 'constraints checked\nrow actually\nchanged', 'bx-acc', tcls='t ts', lh=17)
    f.box(620, 90, 170, 60, 'AFTER trigger\naudit, log, update\nother tables', 'bx-good', tcls='t ts', lh=17)
    f.box(820, 90, 90, 60, 'done', 'bx-mut', tcls='t ts tb')
    for x1, x2 in ((160, 198), (370, 408), (580, 618), (790, 818)):
        f.arrow(x1, 120, x2, 120, 'ink')
    f.box(330, 190, 330, 50, 'INSTEAD OF trigger (on VIEWS): the trigger body RUNS\nINSTEAD OF the original statement', 'bx-pur', tcls='t ts', lh=17)
    f.arrow(160, 140, 330, 210, 'mut', dash=True)
    f.text(285, 30, 'NEW = row after change (INSERT, UPDATE)', 't ts', anchor='start')
    f.text(285, 52, 'OLD = row before change (UPDATE, DELETE)', 't ts', anchor='start')
    return f.render('Where BEFORE, AFTER and INSTEAD OF triggers fire relative to the triggering statement.')


def nosql_types():
    f = Fig(920, 300, 'four kinds of NoSQL databases')
    W = 220
    # key value
    x = 5
    f.box(x, 5, W - 10, 32, 'Key–Value', 'bx-acc', tcls='t tb')
    for i, (k, v) in enumerate([('cart:101', '[p7, p9]'), ('sess:ab3', '{user:42}'), ('otp:9876', '“4821”')]):
        f.box(x + 5, 50 + i * 42, 85, 32, k, 'bx-mut', tcls='t ts', rx=6)
        f.arrow(x + 92, 66 + i * 42, x + 108, 66 + i * 42, 'ink')
        f.box(x + 110, 50 + i * 42, 90, 32, v, '', tcls='t ts', rx=6)
    f.text(x + 105, 200, 'Redis, DynamoDB', 't ts tb')
    f.text(x + 105, 220, 'get/put by key — fastest', 't tx')
    f.text(x + 105, 238, 'caches, sessions, carts', 't tx')
    # document
    x = 5 + W + 10
    f.box(x, 5, W - 10, 32, 'Document', 'bx-good', tcls='t tb')
    f.box(x + 5, 48, W - 20, 132, '', 'bx-plain', rx=6)
    doc = ['{ "_id": 42,', '  "name": "Asha",', '  "tags": ["ai","db"],', '  "address": {', '     "city": "Delhi" },', '  "orders": [ … ] }']
    for i, l in enumerate(doc):
        f.text(x + 16, 64 + i * 19, l, 't ts', anchor='start', fs=12)
    f.text(x + 105, 200, 'MongoDB, CouchDB', 't ts tb')
    f.text(x + 105, 220, 'JSON-like, nested, flexible', 't tx')
    f.text(x + 105, 238, 'catalogs, profiles, CMS', 't tx')
    # column family
    x = 5 + 2 * (W + 10)
    f.box(x, 5, W - 10, 32, 'Column-family', 'bx-warn', tcls='t tb')
    f.box(x + 5, 48, 55, 132, 'row\nkey\nu42', 'bx-mut', tcls='t ts', rx=6)
    f.box(x + 65, 48, 135, 60, 'profile:\nname | city', '', tcls='t ts', rx=6)
    f.box(x + 65, 115, 135, 65, 'activity:\nt1 | t2 | t3 | …\n(millions of cols)', '', tcls='t ts', rx=6)
    f.text(x + 105, 200, 'Cassandra, HBase', 't ts tb')
    f.text(x + 105, 220, 'wide rows, huge write rate', 't tx')
    f.text(x + 105, 238, 'logs, IoT, time-series', 't tx')
    # graph
    x = 5 + 3 * (W + 10)
    f.box(x, 5, W - 10, 32, 'Graph', 'bx-pur', tcls='t tb')
    pts = {'Asha': (x + 45, 80), 'Ravi': (x + 165, 80), 'Book': (x + 105, 165), 'Delhi': (x + 45, 165)}
    f.arrow(x + 73, 80, x + 135, 80, 'acc')
    f.text(x + 105, 70, 'FRIEND', 't tx')
    f.arrow(x + 160, 98, x + 122, 146, 'acc')
    f.text(x + 170, 125, 'LIKES', 't tx')
    f.arrow(x + 45, 100, x + 45, 143, 'acc')
    f.text(x + 25, 122, 'LIVES', 't tx', anchor='end')
    for n, (px, py) in pts.items():
        f.circle(px, py, 24, 'node n-acc')
        f.text(px, py, n, 't ts tb', fs=11.5)
    f.text(x + 105, 200, 'Neo4j, Amazon Neptune', 't ts tb')
    f.text(x + 105, 220, 'nodes + relationships', 't tx')
    f.text(x + 105, 238, 'social, recommendations, fraud', 't tx')
    f.text(460, 280, 'All four trade the fixed relational schema and joins for flexible structure and easy horizontal scaling.', 't ts')
    return f.render('The four families of NoSQL databases, with how they store data and what they are typically used for.')


def cap():
    f = Fig(860, 320, 'CAP theorem')
    A_, C_, P_ = (200, 30), (40, 280), (360, 280)
    f.poly([A_, C_, P_], 'ln-acc', close=True)
    for (x, y), t in ((A_, 'C\nConsistency'), (C_, 'A\nAvailability'), (P_, 'P\nPartition\ntolerance')):
        f.circle(x, y, 32, 'node n-acc')
        f.text(x, y, t.split('\n')[0], 't tb', fs=16)
    f.text(200, -0 + 30 - 46 + 8, 'every read sees the latest write', 't tx')
    f.text(40, 330 - 14, 'every request gets a response', 't tx')
    f.text(360, 330 - 14, 'works despite network splits', 't tx')
    f.text(105, 150, 'CA', 't tb tacc')
    f.text(295, 150, 'CP', 't tb tacc')
    f.text(200, 268, 'AP', 't tb tacc')
    f.box(450, 20, 400, 280, '', 'bx-plain')
    lines = [('CAP theorem (Brewer, 2000):', 'tb'), ('a DISTRIBUTED system can guarantee at most', ''),
             ('2 of the 3 properties when a partition occurs.', ''), ('', ''),
             ('Partitions WILL happen in a cluster, so the real', ''), ('choice is C or A during a partition:', ''), ('', ''),
             ('CP → refuse/delay answers: MongoDB*, HBase', 'tacc'), ('AP → answer, maybe stale: Cassandra, DynamoDB', 'tacc'),
             ('CA → only if no partitions: single-node RDBMS', 'tacc'), ('', ''), ('* configurable; many systems are tunable.', 'tx')]
    for i, (l, c) in enumerate(lines):
        f.text(468, 44 + i * 21, l, f't ts {c}', anchor='start')
    return f.render('CAP explains why many NoSQL systems relax consistency (BASE) to stay available and partition tolerant.')


def scaling():
    f = Fig(900, 230, 'vertical vs horizontal scaling')
    f.text(200, 16, 'Vertical scaling (scale UP) — typical RDBMS', 't tb ts')
    f.box(60, 120, 70, 70, 'DB', 'bx-mut', tcls='t tb')
    f.arrow(140, 155, 200, 155, 'ink')
    f.box(210, 50, 140, 140, 'BIGGER DB\nmore CPU,\nRAM, SSD', 'bx-acc', tcls='t tb ts', lh=18)
    f.text(200, 212, 'simple, but has a hardware ceiling and is costly', 't tx')
    f.text(660, 16, 'Horizontal scaling (scale OUT) — typical NoSQL', 't tb ts')
    for i in range(4):
        f.box(470 + i * 100, 80, 80, 70, f'node {i + 1}\nshard {chr(65 + i)}', 'bx-good', tcls='t ts', lh=17)
    f.box(470 + 4 * 100, 80, 60, 70, '+ …', 'bx-mut', tcls='t tb')
    f.text(690, 175, 'data split (sharded) and replicated across cheap machines', 't tx')
    f.text(690, 212, 'add machines as load grows — near-linear growth', 't tx')
    return f.render('Relational databases traditionally scale up; NoSQL databases are designed to scale out.')


def three_schema_sql():
    f = Fig(860, 210, 'DELETE vs TRUNCATE vs DROP')
    cols = [('DELETE FROM t WHERE …', 'DML · row by row · WHERE allowed\nlogged → can ROLLBACK\ntriggers fire · structure stays', 'bx-good'),
            ('TRUNCATE TABLE t', 'DDL · removes ALL rows at once\nminimal logging · fast · auto-commit*\nno WHERE · structure stays', 'bx-warn'),
            ('DROP TABLE t', 'DDL · removes rows AND the table\n(structure, indexes, constraints,\ntriggers, privileges) · auto-commit', 'bx-bad')]
    for k, (h, b, c) in enumerate(cols):
        x = 10 + k * 283
        f.box(x, 10, 270, 36, h, c, tcls='t tb ts')
        f.box(x, 54, 270, 84, b, '', tcls='t ts', lh=18)
    f.text(430, 165, 'After DELETE (no WHERE) and TRUNCATE: empty table still exists.  After DROP: “table does not exist”.', 't ts')
    f.text(430, 190, '* Oracle/MySQL: TRUNCATE commits implicitly; PostgreSQL & SQL Server can roll it back inside a transaction.', 't tx')
    return f.render('The three ways of “removing” data, from gentlest to most drastic.')
