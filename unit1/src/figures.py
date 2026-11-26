"""Hand-designed figures for Unit 1 (inline SVG, theme-aware via CSS classes)."""
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



# ====================================================================== Unit 1 figures


def file_vs_db():
    """file-processing system vs database approach."""
    f = Fig(860, 330, 'file processing system versus database system', maxw=860)
    # left: file system
    f.box(5, 5, 410, 320, cls='bx-mut', rx=14)
    f.text(210, 26, 'File-processing system', 't tb', fs=15)
    apps = [('Admissions\nprogram', 'students.csv\n(roll, name, addr)'),
            ('Fees\nprogram', 'fees.xls\n(roll, name, addr, due)'),
            ('Exam\nprogram', 'marks.dat\n(roll, name, marks)')]
    for k, (a, fl) in enumerate(apps):
        y = 52 + k * 88
        f.box(20, y, 130, 58, a, cls='bx-plain', fs=13.5)
        f.arrow(150, y + 29, 228, y + 29, 'ink')
        f.box(230, y, 170, 58, fl, cls='bx-bad' if k < 2 else 'bx-warn', fs=12.5)
    f.text(210, 314, 'same name / address stored 3 times → redundancy, inconsistency', 't ts tw', fs=12.5)
    # right: DBMS
    f.box(445, 5, 410, 320, cls='bx-mut', rx=14)
    f.text(650, 26, 'Database approach', 't tb', fs=15)
    for k, a in enumerate(['Admissions', 'Fees', 'Exam']):
        x = 460 + k * 130
        f.box(x, 50, 120, 44, a, cls='bx-plain', fs=13.5)
        f.arrow(x + 60, 94, 650, 140, 'acc')
    f.box(520, 142, 260, 56, 'DBMS\n(one copy, constraints, security,\nconcurrency, recovery)', cls='bx-acc', fs=12.5, lh=15)
    f.arrow(650, 198, 650, 226, 'acc')
    f.raw('<path d="M560,236 a90,12 0 0,0 180,0 v52 a90,12 0 0,1 -180,0 z" class="bx bx-good"/>'
          '<ellipse cx="650" cy="236" rx="90" ry="12" class="bx bx-good"/>')
    f.text(650, 268, 'integrated database\n+ data dictionary', 't', fs=13)
    f.text(650, 314, 'each fact stored once, shared by all programs', 't ts tgood', fs=12.5)
    return f.render('Left: every program owns its own files, so the same fact is stored many times and the files drift apart. '
                    'Right: all programs go through one DBMS to one integrated database.')


def three_schema():
    """ANSI/SPARC three-schema architecture with mappings and data independence."""
    f = Fig(820, 470, 'three-schema architecture', maxw=820)
    # level labels
    for y, t in [(60, 'External\n(view) level'), (210, 'Conceptual\n(logical) level'), (335, 'Internal\n(physical) level')]:
        f.text(60, y, t, 't tb', fs=13.5)
    f.line(120, 130, 640, 130, 'ln-dash')
    f.line(120, 272, 640, 272, 'ln-dash')
    views = ['View 1\n(Student portal)', 'View 2\n(Accounts)', 'View 3\n(Faculty)']
    for k, v in enumerate(views):
        x = 140 + k * 170
        f.box(x, 35, 150, 52, v, cls='bx-plain', fs=13)
        f.arrow(x + 75, 87, 380, 186, 'acc', both=True)
    f.text(130, 150, 'external / conceptual mapping', 't ts tacc', anchor='start', fs=12)
    f.box(270, 188, 220, 50, 'Conceptual schema\n(all entities, relationships, constraints)', cls='bx-acc', fs=12.5, lh=15)
    f.arrow(380, 238, 380, 306, 'acc', both=True)
    f.text(392, 290, 'conceptual / internal mapping', 't ts tacc', anchor='start', fs=12)
    f.box(270, 308, 220, 50, 'Internal schema\n(files, records, indexes, B+ trees)', cls='bx-good', fs=12.5, lh=15)
    f.arrow(380, 358, 380, 392, 'ink')
    f.raw('<path d="M320,400 a60,10 0 0,0 120,0 v40 a60,10 0 0,1 -120,0 z" class="bx bx-mut"/>'
          '<ellipse cx="380" cy="400" rx="60" ry="10" class="bx bx-mut"/>')
    f.text(380, 428, 'stored database', 't ts', fs=12.5)
    # independence braces
    f.box(660, 60, 150, 170, cls='bx-pur', rx=10)
    f.text(735, 145, 'LOGICAL data\nindependence\n\nchange conceptual\nschema, views and\nprograms unchanged', 't', fs=12.5, lh=16)
    f.box(660, 245, 150, 170, cls='bx-pur', rx=10)
    f.text(735, 330, 'PHYSICAL data\nindependence\n\nchange internal\nschema, conceptual\nschema unchanged', 't', fs=12.5, lh=16)
    return f.render('Users see only their external view. The DBMS converts a request on a view into a request on the conceptual schema and then '
                    'into one on the internal schema, using the two mappings. Data independence is exactly the ability to change one level '
                    'and absorb the change in the mapping above it.')


def hier_model():
    """hierarchical model: a tree of record types with duplication for M:N."""
    f = Fig(760, 300, 'hierarchical data model', maxw=760)
    f.box(305, 10, 150, 44, 'Dept: IT', cls='bx-acc', fs=14)
    ch = [('Course: DBMS', 120), ('Course: OS', 380), ('Teacher: Rao', 630)]
    for t, x in ch:
        f.line(380, 54, x, 100, 'ln')
        f.box(x - 80, 100, 160, 42, t, cls='bx-plain', fs=13.5)
    leaves = [('Asha', 50, 120), ('Vikram', 190, 120), ('Asha', 330, 380), ('Neha', 450, 380)]
    for t, x, px in leaves:
        f.line(px, 142, x, 200, 'ln')
        f.box(x - 55, 200, 110, 40, 'Student: ' + t, cls='bx-bad' if t == 'Asha' else 'bx-plain', fs=12.5)
    f.text(380, 270, 'Asha takes two courses → her record is stored twice (a child has only ONE parent)', 't ts tw', fs=12.5)
    f.text(380, 290, 'access path is fixed: Dept → Course → Student; “courses of Asha” needs a full tree scan', 't ts', fs=12.5)
    return f.render('Hierarchical model (e.g. IBM IMS): records form a tree of parent–child (1:N) links. '
                    'An M:N relationship can only be stored by duplicating the child record (or with “virtual” pointer records).')


def net_model():
    """network model: owner-member sets, a record can have many owners."""
    f = Fig(760, 290, 'network data model', maxw=760)
    cs = [('DBMS', 200), ('OS', 520)]
    ss = [('Vikram', 120), ('Asha', 380), ('Neha', 640)]
    for t, x in cs:
        f.box(x - 75, 20, 150, 44, 'Course: ' + t, cls='bx-acc', fs=13.5)
    for t, x in ss:
        f.box(x - 70, 205, 140, 44, 'Student: ' + t, cls='bx-plain', fs=13.5)
    links = [(200, 120, 110), (200, 380, 270), (520, 380, 490), (520, 640, 650)]
    for cx, sx, lx in links:
        f.box(lx - 50, 118, 100, 34, 'enrol', cls='bx-warn', fs=12.5)
        f.arrow(cx, 64, lx, 116, 'ink')
        f.arrow(lx, 152, sx, 203, 'ink')
    f.text(380, 108, 'owner → link → member', 't ts', fs=12)
    f.text(380, 275, 'Asha stored once, linked to two owners (graph, not tree) · queries follow pointers record by record', 't ts', fs=12.5)
    return f.render('Network model (CODASYL / DBTG, e.g. IDMS): records are linked by pointer-based <i>set types</i> (owner → members). '
                    'A record may have several owners, so M:N is represented without duplication through a link record — '
                    'but programs must navigate the pointers themselves.')


def dbms_structure():
    """overall system structure of a DBMS (Korth)."""
    f = Fig(860, 640, 'structure of a database management system', maxw=860)
    users = [('Naive users\n(tellers, web users)', 'use app interfaces'), ('Application\nprogrammers', 'write programs'),
             ('Sophisticated\nusers (analysts)', 'ad-hoc queries'), ('Database\nadministrator', 'uses admin tools')]
    for k, (u, a) in enumerate(users):
        x = 10 + k * 212
        f.box(x, 8, 196, 46, u, cls='bx-mut', fs=12.5, lh=15)
        f.arrow(x + 98, 54, x + 98, 76, 'ink')
    tools = ['Application\ninterfaces', 'Application programs\n→ compiler & linker', 'Query tools\n(SQL)', 'Administration\ntools (DDL)']
    for k, t in enumerate(tools):
        x = 10 + k * 212
        f.box(x, 78, 196, 46, t, cls='bx-plain', fs=12.5, lh=15)
        f.arrow(x + 98, 124, x + 98, 158, 'ink')
    # query processor
    f.box(10, 160, 840, 150, cls='bx-acc', rx=12)
    f.text(24, 178, 'QUERY PROCESSOR', 't tb tacc', anchor='start', fs=13)
    f.box(40, 195, 230, 44, 'DML compiler &\norganizer (optimizer)', cls='bx-plain', fs=12.5, lh=15)
    f.box(320, 195, 210, 44, 'DDL interpreter', cls='bx-plain', fs=13)
    f.box(580, 195, 240, 44, 'Embedded DML\nprecompiler', cls='bx-plain', fs=12.5, lh=15)
    f.box(220, 255, 420, 42, 'Query evaluation engine (executes the plan)', cls='bx-plain', fs=13)
    f.arrow(155, 239, 300, 255, 'ink')
    f.arrow(700, 239, 580, 255, 'ink')
    f.arrow(430, 297, 430, 336, 'ink')
    # storage manager
    f.box(10, 338, 840, 140, cls='bx-good', rx=12)
    f.text(24, 356, 'STORAGE MANAGER', 't tb tgood', anchor='start', fs=13)
    sm = ['Authorization &\nintegrity manager', 'Transaction manager\n(concurrency + recovery)', 'File manager', 'Buffer manager']
    for k, t in enumerate(sm):
        x = 30 + k * 205
        f.box(x, 372, 190, 50, t, cls='bx-plain', fs=12.5, lh=15)
    f.text(430, 452, 'interface between low-level stored data and the programs / queries', 't ts', fs=12.5)
    f.arrow(430, 478, 430, 512, 'ink', both=True)
    # disk
    f.box(10, 514, 840, 118, cls='bx-mut', rx=12)
    f.text(24, 532, 'DISK STORAGE', 't tb', anchor='start', fs=13)
    disk = ['Data files', 'Indices', 'Data dictionary\n(metadata)', 'Statistical data']
    for k, t in enumerate(disk):
        cx = 120 + k * 205
        f.raw(f'<path d="M{cx - 70},560 a70,10 0 0,0 140,0 v44 a70,10 0 0,1 -140,0 z" class="bx bx-plain"/>'
              f'<ellipse cx="{cx}" cy="560" rx="70" ry="10" class="bx bx-plain"/>')
        f.text(cx, 588, t, 't', fs=12.5, lh=15)
    return f.render('The two big modules are the <b>query processor</b> (turns DDL/DML into low-level actions) and the <b>storage manager</b> '
                    '(stores, retrieves and protects the data on disk). Users reach them through different interfaces.')


def tiers():
    """1-tier, 2-tier and 3-tier architectures."""
    f = Fig(860, 330, '1-tier, 2-tier and 3-tier architecture', maxw=860)
    cols = [(10, '1-tier'), (300, '2-tier (client–server)'), (590, '3-tier')]
    for x, t in cols:
        f.box(x, 5, 260, 320, cls='bx-mut', rx=14)
        f.text(x + 130, 26, t, 't tb', fs=15)

    def db(cx, y):
        f.raw(f'<path d="M{cx - 55},{y} a55,9 0 0,0 110,0 v34 a55,9 0 0,1 -110,0 z" class="bx bx-good"/>'
              f'<ellipse cx="{cx}" cy="{y}" rx="55" ry="9" class="bx bx-good"/>')
        f.text(cx, y + 20, 'Database', 't ts', fs=12.5)
    # 1 tier
    f.box(35, 50, 210, 210, cls='bx-plain', rx=10)
    f.text(140, 68, 'one machine', 't ts', fs=12)
    f.box(60, 82, 160, 36, 'User + client tool', cls='bx-acc', fs=12.5)
    f.arrow(140, 118, 140, 140, 'ink', both=True)
    f.box(60, 142, 160, 36, 'DBMS', cls='bx-plain', fs=13)
    f.arrow(140, 178, 140, 196, 'ink', both=True)
    db(140, 206)
    f.text(140, 292, 'e.g. MS Access, SQLite on a\nlaptop, DBA at the console', 't ts', fs=12)
    # 2 tier
    f.box(325, 50, 210, 80, cls='bx-plain', rx=10)
    f.text(430, 64, 'CLIENT', 't ts tb', fs=11.5)
    f.box(345, 74, 170, 44, 'User interface +\napplication program', cls='bx-acc', fs=12.5, lh=15)
    f.arrow(430, 130, 430, 166, 'ink', both=True)
    f.text(440, 148, 'ODBC / JDBC', 't ts', anchor='start', fs=11.5)
    f.box(325, 168, 210, 110, cls='bx-plain', rx=10)
    f.text(430, 182, 'SERVER', 't ts tb', fs=11.5)
    f.box(355, 192, 150, 30, 'DBMS', cls='bx-plain', fs=13)
    db(430, 232)
    f.text(430, 304, 'e.g. college desktop app\nconnecting to Oracle server', 't ts', fs=12)
    # 3 tier
    f.box(615, 46, 210, 50, 'Client: browser / app\n(presentation)', cls='bx-acc', fs=12.5, lh=15)
    f.arrow(720, 96, 720, 116, 'ink', both=True)
    f.box(615, 118, 210, 50, 'Application server\n(business logic)', cls='bx-warn', fs=12.5, lh=15)
    f.arrow(720, 168, 720, 188, 'ink', both=True)
    f.box(615, 190, 210, 94, cls='bx-plain', rx=10)
    f.text(720, 204, 'DATABASE SERVER', 't ts tb', fs=11.5)
    f.box(660, 212, 120, 26, 'DBMS', cls='bx-plain', fs=13)
    db(720, 246)
    f.text(720, 306, 'e.g. Amazon, IRCTC, NSUT IMS', 't ts', fs=12)
    return f.render('2-tier: the client talks to the database server directly. 3-tier: the client never touches the database; an application '
                    'server in the middle holds the business rules, security checks and connection pooling.')


def design_phases():
    f = Fig(820, 120, 'phases of database design', maxw=820)
    st = [('Requirements\ncollection & analysis', 'bx-plain'), ('Conceptual design\n(ER diagram) — Unit 3', 'bx-acc'),
          ('Logical design\n(relational schema,\nnormalization) — Units 3–4', 'bx-acc'), ('Physical design\n(files, indexes)', 'bx-good')]
    for k, (t, c) in enumerate(st):
        x = 5 + k * 205
        f.box(x, 20, 180, 80, t, cls=c, fs=12.5, lh=16)
        if k < 3:
            f.arrow(x + 180, 60, x + 203, 60, 'ink')
    return f.render('Top-down design moves from <i>what</i> data is needed to <i>how</i> it is stored — the same direction as the three '
                    'levels of abstraction (view → conceptual → internal).')
