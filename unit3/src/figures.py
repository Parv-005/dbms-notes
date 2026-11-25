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



# ====================================================================== Unit 3 figures
def design_phases():
    f = Fig(860, 250, 'database design phases')
    steps = [('Requirements\ncollection & analysis', 'bx-mut', 'what data, which users,\nwhich transactions'),
             ('Conceptual design', 'bx-acc', 'ER / EER diagram\n(this unit)'),
             ('Logical design\n(data-model mapping)', 'bx-good', 'ER → relational tables\n(this unit)'),
             ('Schema refinement', 'bx-warn', 'functional dependencies,\nnormalization (Unit 4)'),
             ('Physical design', 'bx-pur', 'files, indexes,\nstorage, tuning')]
    x = 10
    for i, (t, c, sub) in enumerate(steps):
        f.box(x, 40, 150, 70, t, c, fs=13)
        f.text(x + 75, 150, sub, 't tx', fs=11.5, lh=15)
        if i < len(steps) - 1:
            f.arrow(x + 152, 75, x + 172, 75)
        x += 172
    f.text(430, 205, 'DBMS-independent  ←───────────────────────→  DBMS-specific', 't tx', fs=12)
    f.line(10, 225, 850, 225, 'ln-mut')
    f.text(250, 18, 'top-down: start from the whole enterprise, refine into entities → relationships → attributes', 't tx', fs=12)
    return f.render('The database design process. Units 3 and 4 cover the two middle steps.')


def topdown():
    f = Fig(860, 270, 'top-down vs bottom-up design')
    # top-down
    f.text(210, 18, 'Top-down (ER model, specialization)', 't tb', fs=14)
    f.box(140, 40, 140, 38, 'Enterprise / mini-world', 'bx-acc', fs=12.5)
    f.box(40, 120, 110, 36, 'entity types', 'bx-plain', fs=12.5)
    f.box(160, 120, 110, 36, 'relationships', 'bx-plain', fs=12.5)
    f.box(280, 120, 110, 36, 'constraints', 'bx-plain', fs=12.5)
    for x in (95, 215, 335):
        f.arrow(210, 80, x, 118)
    f.box(40, 200, 110, 36, 'subclasses', 'bx-mut', fs=12.5)
    f.box(160, 200, 110, 36, 'attributes', 'bx-mut', fs=12.5)
    f.arrow(95, 158, 95, 198)
    f.arrow(215, 158, 215, 198)
    f.text(215, 255, 'general concepts first → refine into detail', 't tx', fs=12)
    # bottom-up
    f.text(650, 18, 'Bottom-up (generalization, synthesis)', 't tb', fs=14)
    for i, a in enumerate(['emp_id', 'name', 'salary', 'roll_no', 'cgpa']):
        f.box(470 + i * 74, 200, 66, 32, a, 'bx-mut', fs=12)
    f.box(500, 120, 120, 36, 'EMPLOYEE', 'bx-plain', fs=12.5)
    f.box(660, 120, 120, 36, 'STUDENT', 'bx-plain', fs=12.5)
    for x in (503, 577):
        f.arrow(x, 198, 545, 158)
    for x in (651, 725, 799):
        f.arrow(x, 198, 715, 158)
    f.box(580, 40, 120, 38, 'PERSON', 'bx-acc', fs=12.5)
    f.arrow(560, 118, 625, 80)
    f.arrow(720, 118, 655, 80)
    f.text(640, 255, 'attributes / small entities first → group into general ones', 't tx', fs=12)
    return f.render('Top-down starts from the big picture and refines it; bottom-up starts from attributes and combines them.')


def _sets(f, x0, title, left, right, pairs, ltitle='E1', rtitle='E2', total_l=False, total_r=False):
    f.text(x0 + 95, 16, title, 't tb', fs=13.5)
    ys_l = [60 + i * 34 for i in range(len(left))]
    ys_r = [60 + i * 34 for i in range(len(right))]
    hl = 4 * 34 + 30
    f.ellipse(x0 + 30, 40 + hl / 2 - 6, 26, hl / 2, 'inst-set')
    f.ellipse(x0 + 160, 40 + hl / 2 - 6, 26, hl / 2, 'inst-set')
    f.text(x0 + 30, hl + 62, ltitle + (' (total)' if total_l else ''), 't ts', fs=12)
    f.text(x0 + 160, hl + 62, rtitle + (' (total)' if total_r else ''), 't ts', fs=12)
    for (a, b) in pairs:
        f.line(x0 + 36, ys_l[a], x0 + 154, ys_r[b], 'ln-acc')
    for i, y in enumerate(ys_l):
        f.circle(x0 + 30, y, 5, 'inst-dot')
        f.text(x0 + 14, y, left[i], 't tx', anchor='end', fs=11)
    for i, y in enumerate(ys_r):
        f.circle(x0 + 160, y, 5, 'inst-dot')
        f.text(x0 + 176, y, right[i], 't tx', anchor='start', fs=11)


def cardinality():
    f = Fig(900, 250, 'cardinality ratios with instances', maxw=900)
    _sets(f, 15, '1 : 1', ['e1', 'e2', 'e3'], ['d1', 'd2', 'd3'], [(0, 0), (1, 2)], 'EMPLOYEE', 'DEPT', )
    _sets(f, 240, '1 : N', ['d1', 'd2', 'd3'], ['e1', 'e2', 'e3', 'e4'], [(0, 0), (0, 1), (1, 2), (1, 3)], 'DEPT', 'EMPLOYEE')
    _sets(f, 465, 'N : 1', ['e1', 'e2', 'e3', 'e4'], ['d1', 'd2', 'd3'], [(0, 0), (1, 0), (2, 1), (3, 1)], 'EMPLOYEE', 'DEPT')
    _sets(f, 690, 'M : N', ['e1', 'e2', 'e3'], ['p1', 'p2', 'p3'], [(0, 0), (0, 1), (1, 1), (2, 0), (2, 2)], 'EMPLOYEE', 'PROJECT')
    return f.render('Each line is one relationship instance. 1:1 — every dot has at most one line. 1:N — a left dot may have many '
                    'lines, a right dot at most one. M:N — no limit on either side.')


def participation():
    f = Fig(560, 250, 'total vs partial participation')
    _sets(f, 40, 'MANAGES', ['e1', 'e2', 'e3', 'e4'], ['d1', 'd2', 'd3'], [(0, 1), (2, 0), (3, 2)], 'EMPLOYEE', 'DEPARTMENT', False, True)
    f.text(370, 70, 'e2 manages nothing → EMPLOYEE', 't ts', anchor='start', fs=12)
    f.text(370, 88, 'participation is PARTIAL', 't ts tbad', anchor='start', fs=12)
    f.text(370, 130, 'every department has a', 't ts', anchor='start', fs=12)
    f.text(370, 148, 'manager → DEPARTMENT', 't ts', anchor='start', fs=12)
    f.text(370, 166, 'participation is TOTAL', 't ts tgood', anchor='start', fs=12)
    return f.render('Total participation = every entity of the set appears in at least one relationship instance (drawn as a double line). '
                    'Partial = some entities may not participate.')


def notation():
    f = Fig(900, 430, 'Chen ER notation')
    def item(x, y, draw, label):
        draw(x, y)
        f.text(x + 75, y, label, 't ts', anchor='start', fs=12.5)
    def ent(x, y):
        f.raw(f'<rect x="{x - 45}" y="{y - 17}" width="90" height="34" class="er-ent"/>')
        f.text(x, y, 'ENTITY', 'er-et', fs=12)
    def went(x, y):
        f.raw(f'<rect x="{x - 45}" y="{y - 17}" width="90" height="34" class="er-ent"/><rect x="{x - 41}" y="{y - 13}" width="82" height="26" class="er-ent2"/>')
        f.text(x, y, 'WEAK', 'er-et', fs=12)
    def rel(x, y, dbl=False):
        f.raw(f'<polygon points="{x},{y - 22} {x + 45},{y} {x},{y + 22} {x - 45},{y}" class="er-rel"/>')
        if dbl:
            f.raw(f'<polygon points="{x},{y - 17} {x + 37},{y} {x},{y + 17} {x - 37},{y}" class="er-rel2"/>')
        f.text(x, y, 'REL', 'er-rt', fs=12)
    def att(x, y, kind=''):
        cls = 'er-att' + (' er-der' if kind == 'd' else '')
        if kind == 'm':
            f.raw(f'<ellipse cx="{x}" cy="{y}" rx="44" ry="19" class="{cls}"/>')
        f.raw(f'<ellipse cx="{x}" cy="{y}" rx="40" ry="15" class="{cls}"/>')
        name = {'k': 'roll_no', 'p': 'dep_name', 'm': 'phone', 'd': 'age'}.get(kind, 'name')
        f.text(x, y, name, 'er-at', fs=12)
        if kind in ('k', 'p'):
            f.raw(f'<line x1="{x - 22}" y1="{y + 8}" x2="{x + 22}" y2="{y + 8}" class="er-ul{" er-ul-d" if kind == "p" else ""}"/>')
    rows = [(ent, 'entity type (strong)'), (went, 'weak entity type'),
            (lambda x, y: rel(x, y), 'relationship type'), (lambda x, y: rel(x, y, True), 'identifying relationship (of a weak entity)'),
            (lambda x, y: att(x, y), 'attribute (simple, single-valued)'), (lambda x, y: att(x, y, 'k'), 'key attribute (underlined)'),
            (lambda x, y: att(x, y, 'p'), 'partial key / discriminator (dashed underline)')]
    rows2 = [(lambda x, y: att(x, y, 'm'), 'multivalued attribute (double ellipse)'), (lambda x, y: att(x, y, 'd'), 'derived attribute (dashed ellipse)'),
             (None, 'composite attribute'), (None, 'partial participation (single line)'), (None, 'total participation (double line)'),
             (None, 'cardinality: 1, N, M written near the entity'), (None, 'ISA triangle: specialization / generalization')]
    for i, (d, l) in enumerate(rows):
        item(70, 30 + i * 57, d, l)
    x = 520
    for i, (d, l) in enumerate(rows2):
        y = 30 + i * 57
        if d:
            item(x, y, d, l)
            continue
        if i == 2:
            f.raw(f'<line x1="{x}" y1="{y}" x2="{x - 30}" y2="{y + 14}" class="erl"/><line x1="{x}" y1="{y}" x2="{x + 30}" y2="{y + 14}" class="erl"/>')
            f.raw(f'<ellipse cx="{x}" cy="{y - 6}" rx="26" ry="12" class="er-att"/>')
            f.text(x, y - 6, 'name', 'er-at', fs=11)
            f.raw(f'<ellipse cx="{x - 34}" cy="{y + 20}" rx="22" ry="10" class="er-att"/><ellipse cx="{x + 34}" cy="{y + 20}" rx="22" ry="10" class="er-att"/>')
            f.text(x - 34, y + 20, 'first', 'er-at', fs=10)
            f.text(x + 34, y + 20, 'last', 'er-at', fs=10)
        elif i == 3:
            f.raw(f'<path d="M{x - 45},{y} L{x + 45},{y}" class="erl"/>')
        elif i == 4:
            f.raw(f'<path d="M{x - 45},{y} L{x + 45},{y}" class="erl-o"/><path d="M{x - 45},{y} L{x + 45},{y}" class="erl-i"/>')
        elif i == 5:
            f.raw(f'<path d="M{x - 45},{y} L{x + 45},{y}" class="erl"/>')
            f.text(x - 36, y - 10, '1', 'er-card', fs=13)
            f.text(x + 36, y - 10, 'N', 'er-card', fs=13)
        elif i == 6:
            f.raw(f'<polygon points="{x - 24},{y - 16} {x + 24},{y - 16} {x},{y + 18}" class="er-isa"/>')
            f.text(x, y - 5, 'ISA', 'er-isat', fs=10.5)
        f.text(x + 75, y, l, 't ts', anchor='start', fs=12.5)
    f.raw('<rect x="0" y="0" width="900" height="430" rx="12" class="er-bg" style="fill:none"/>')
    return f.render('Chen notation as used in NSUT papers and in Korth/Elmasri. Learn these by heart — the papers use them without explanation.')


def crowsfoot():
    f = Fig(860, 230, "crow's-foot notation")
    def ent(x, y, t):
        f.raw(f'<rect x="{x - 55}" y="{y - 18}" width="110" height="36" class="er-ent"/>')
        f.text(x, y, t, 'er-et', fs=12.5)
    rows = [('one and only one (1,1)', 'one'), ('zero or one (0,1)', 'zo'), ('one or many (1,N)', 'om'), ('zero or many (0,N)', 'zm')]
    for i, (lab, kind) in enumerate(rows):
        y = 30 + i * 50
        x1, x2 = 40, 230
        f.raw(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" class="erl"/>')
        # mark near x2
        if kind in ('one', 'zo'):
            f.raw(f'<line x1="{x2 - 12}" y1="{y - 9}" x2="{x2 - 12}" y2="{y + 9}" class="erl"/>')
        if kind == 'one':
            f.raw(f'<line x1="{x2 - 20}" y1="{y - 9}" x2="{x2 - 20}" y2="{y + 9}" class="erl"/>')
        if kind in ('om', 'zm'):
            f.raw(f'<line x1="{x2 - 14}" y1="{y}" x2="{x2}" y2="{y - 9}" class="erl"/><line x1="{x2 - 14}" y1="{y}" x2="{x2}" y2="{y + 9}" class="erl"/>')
        if kind == 'om':
            f.raw(f'<line x1="{x2 - 22}" y1="{y - 9}" x2="{x2 - 22}" y2="{y + 9}" class="erl"/>')
        if kind in ('zo', 'zm'):
            f.raw(f'<circle cx="{x2 - 30}" cy="{y}" r="6" class="er-att"/>')
        f.text(250, y, lab, 't ts', anchor='start', fs=12.5)
    # example
    ent(520, 110, 'DEPARTMENT')
    ent(780, 110, 'EMPLOYEE')
    y = 110
    f.raw(f'<line x1="575" y1="{y}" x2="725" y2="{y}" class="erl"/>')
    for xx in (587, 595):
        f.raw(f'<line x1="{xx}" y1="{y - 9}" x2="{xx}" y2="{y + 9}" class="erl"/>')
    f.raw(f'<line x1="711" y1="{y}" x2="725" y2="{y - 9}" class="erl"/><line x1="711" y1="{y}" x2="725" y2="{y + 9}" class="erl"/>')
    f.raw(f'<line x1="703" y1="{y - 9}" x2="703" y2="{y + 9}" class="erl"/>')
    f.text(650, 95, 'works in', 'er-role', fs=12)
    f.text(650, 160, 'each employee: exactly one department', 't tx', fs=11.5)
    f.text(650, 178, 'each department: one or many employees', 't tx', fs=11.5)
    return f.render("Crow's-foot (IE) notation — used by tools like MySQL Workbench and shown on p. 51 of the course notes. The symbol "
                    "<b>next to an entity</b> says how many of <b>that</b> entity go with one of the other.")


def ternary_vs_binary():
    f = Fig(860, 230, 'ternary vs three binaries')
    f.text(160, 18, 'Ternary SUPPLY (3 facts)', 't tb', fs=13.5)
    f.grid(40, 35, ['supplier', 'part', 'project'], [['S1', 'P1', 'J2'], ['S1', 'P2', 'J1'], ['S2', 'P1', 'J1']], 80, 28, fs=12.5)
    f.text(600, 18, 'Same facts stored as three binary relationships', 't tb', fs=13.5)
    f.grid(380, 35, ['s', 'p'], [['S1', 'P1'], ['S1', 'P2'], ['S2', 'P1']], 50, 28, fs=12.5)
    f.grid(530, 35, ['p', 'j'], [['P1', 'J2'], ['P2', 'J1'], ['P1', 'J1']], 50, 28, fs=12.5)
    f.grid(680, 35, ['s', 'j'], [['S1', 'J2'], ['S1', 'J1'], ['S2', 'J1']], 50, 28, fs=12.5)
    f.box(380, 168, 400, 44, '', 'bx-bad')
    f.text(580, 182, 'Rebuild by joining: (S1, P1, J1) satisfies all three pairs', 't ts', fs=12.5)
    f.text(580, 199, 'but S1 never supplied P1 to J1  →  a false (spurious) fact', 't ts tbad', fs=12.5)
    return f.render('Three binary relationships keep only pairs. Joining them back can create triples that never happened, so in general '
                    'a ternary relationship cannot be replaced by three binary ones.')
