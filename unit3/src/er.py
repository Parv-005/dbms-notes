"""ER model for Unit 3.

One definition of an ER schema is used for two things:
  1. draw()      -> an inline SVG ER diagram in Chen notation (theme-aware via CSS classes)
  2. mapping()   -> the relational schema produced by the standard ER->relational algorithm
                    (minimum number of tables), checked against the hand-written expectation
                    and turned into CREATE TABLE statements that are executed in SQLite.

Attribute mini-syntax (strings):
   _ssn            key attribute (underlined)
   ~dname          partial key / discriminator of a weak entity (dashed underline)
   *phone          multivalued (double ellipse)
   /age            derived (dashed ellipse)
   name(first,last)  composite; components may carry the same prefixes
Cardinality on a relationship end = the label written next to that entity in the diagram
('1', 'N' or 'M'): "DEPT 1 -- WORKS_FOR -- N EMP" means one dept : many employees.
"""
import math, html, re, sqlite3
from svglib import uid, esc

CH = 7.3      # average char width at 13px
CAPW = 8.7


def tw(s, fs=13):
    s = str(s)
    w = sum(CAPW if c.isupper() else (4.2 if c in 'il.,:;|!() ' else CH) for c in s)
    return w * fs / 13


# ====================================================================== model
class Attr:
    def __init__(self, spec):
        spec = spec.strip()
        self.key = self.partial = self.multi = self.derived = False
        while spec and spec[0] in '_~*/':
            c, spec = spec[0], spec[1:]
            if c == '_':
                self.key = True
            elif c == '~':
                self.partial = True
            elif c == '*':
                self.multi = True
            elif c == '/':
                self.derived = True
        self.sub = []
        m = re.match(r'^([^()]+)\((.*)\)$', spec)
        if m:
            spec = m.group(1).strip()
            self.sub = [Attr(s) for s in _split(m.group(2))]
        self.name = spec

    def simple_cols(self):
        """columns this attribute contributes to a table (composite -> its components)"""
        if self.derived or self.multi:
            return []
        if self.sub:
            out = []
            for s in self.sub:
                out += s.simple_cols()
            return out
        return [self.name]

    def leaf_names(self):
        if self.sub:
            out = []
            for s in self.sub:
                out += s.leaf_names()
            return out
        return [self.name]


def _split(s):
    out, depth, cur = [], 0, ''
    for c in s:
        if c == ',' and depth == 0:
            out.append(cur)
            cur = ''
            continue
        depth += c == '('
        depth -= c == ')'
        cur += c
    if cur.strip():
        out.append(cur)
    return out


class Node:
    def __init__(self, kind, name, x, y, label=None):
        self.kind, self.name, self.x, self.y = kind, name, x, y
        self.label = label or name
        self.attrs = []          # list of (Attr, side)
        self.at = {}             # attr name -> (x, y) absolute override
        self.gap = {}


class End:
    def __init__(self, ent, card='N', total=False, role=None, minmax=None, lpos=None, via=None, arrow=None):
        self.ent, self.card, self.total, self.role = ent, card, total, role
        self.minmax, self.lpos, self.via, self.arrow = minmax, lpos, via or [], arrow


class ER:
    REG = {}

    def __init__(self, eid, notation='label', expect=None, opts=None, title=''):
        self.id = eid
        self.notation = notation          # label | arrow | minmax | none
        self.nodes = {}                    # name -> Node
        self.order = []
        self.rels = []                     # names of relationship nodes
        self.ents = []
        self.isas = []
        self.aggs = {}
        self.expect = expect
        self.opts = opts or {}
        self.notes = []
        self.extra = []                    # free decorations (text etc.)
        ER.REG[eid] = self

    # ------------------------------------------------------------ building
    def _attrs(self, node, top=(), bottom=(), left=(), right=(), at=None, gap=None):
        for side, lst in (('top', top), ('bottom', bottom), ('left', left), ('right', right)):
            for s in lst:
                node.attrs.append((Attr(s), side))
        node.at = at or {}
        node.gap = gap if isinstance(gap, dict) else ({} if gap is None else {'all': gap})

    def entity(self, name, x, y, weak=False, label=None, **kw):
        n = Node('weak' if weak else 'ent', name, x, y, label)
        self._attrs(n, **kw)
        self.nodes[name] = n
        self.ents.append(name)
        self.order.append(name)
        return n

    def rel(self, name, x, y, ends, identifying=False, label=None, **kw):
        n = Node('idrel' if identifying else 'rel', name, x, y, label)
        n.ends = [e if isinstance(e, End) else End(*e) for e in ends]
        self._attrs(n, **kw)
        self.nodes[name] = n
        self.rels.append(name)
        self.order.append(name)
        return n

    def isa(self, sup, subs, x, y, disjoint=True, total=False, method='er', label='ISA', note=None, sublines=None):
        n = Node('isa', f'isa{len(self.isas)}', x, y, label)
        n.sup, n.subs, n.disjoint, n.total, n.method = sup, subs, disjoint, total, method
        n.note = note
        n.sublines = sublines or {}
        self.nodes[n.name] = n
        self.isas.append(n.name)
        return n

    def aggregate(self, name, relname, box):
        """box = (x1, y1, x2, y2) drawn around the aggregated relationship + its entities"""
        n = Node('agg', name, (box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
        n.rel = relname
        n.box = box
        self.nodes[name] = n
        self.aggs[name] = n
        return n

    def text(self, x, y, s, cls='t ts', anchor='middle'):
        self.extra.append((x, y, s, cls, anchor))

    # ------------------------------------------------------------ geometry
    def size(self, n):
        if n.kind in ('ent', 'weak'):
            return max(84, tw(n.label, 14) + 30), 40
        if n.kind in ('rel', 'idrel'):
            return max(96, tw(n.label, 13) * 1.25 + 44), 54
        if n.kind == 'isa':
            return 56, 40
        if n.kind == 'agg':
            return n.box[2] - n.box[0], n.box[3] - n.box[1]
        return 60, 30

    def boundary(self, n, px, py):
        """point where the segment centre->(px,py) leaves node n"""
        dx, dy = px - n.x, py - n.y
        if abs(dx) < 1e-9 and abs(dy) < 1e-9:
            return n.x, n.y
        w, h = self.size(n)
        if n.kind in ('rel', 'idrel'):
            s = 1 / (abs(dx) / (w / 2) + abs(dy) / (h / 2))
        elif n.kind == 'isa':
            # triangle pointing down: top edge at y-h/2 ; treat as rect for simplicity of line ends
            s = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
        else:
            s = min((w / 2) / abs(dx) if dx else 1e9, (h / 2) / abs(dy) if dy else 1e9)
        return n.x + dx * s, n.y + dy * s

    def attach(self, n, px, py):
        """like boundary(), but a waypoint level with / above a box gives a straight orthogonal joint"""
        w, h = self.size(n)
        if n.kind in ('ent', 'weak', 'agg'):
            if abs(px - n.x) < w / 2 - 3:
                return px, n.y + (h / 2 if py > n.y else -h / 2)
            if abs(py - n.y) < h / 2 - 3:
                return n.x + (w / 2 if px > n.x else -w / 2), py
        if n.kind in ('rel', 'idrel'):
            if abs(px - n.x) < 1:
                return n.x, n.y + (h / 2 if py > n.y else -h / 2)
            if abs(py - n.y) < 1:
                return n.x + (w / 2 if px > n.x else -w / 2), n.y
        return self.boundary(n, px, py)

    # ------------------------------------------------------------ drawing
    def draw(self, caption='', maxw=None, scale=1.0):
        P = []
        box = [1e9, 1e9, -1e9, -1e9]

        def ext(x1, y1, x2=None, y2=None):
            x2 = x1 if x2 is None else x2
            y2 = y1 if y2 is None else y2
            box[0] = min(box[0], x1, x2)
            box[1] = min(box[1], y1, y2)
            box[2] = max(box[2], x1, x2)
            box[3] = max(box[3], y1, y2)

        lines, shapes, texts = [], [], []

        def seg(pts, total=False, cls='erl', dash=False):
            d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
            for x, y in pts:
                ext(x, y)
            if total:
                lines.append(f'<path d="{d}" class="erl-o"/>')
                lines.append(f'<path d="{d}" class="erl-i"/>')
            else:
                lines.append(f'<path d="{d}" class="{cls}{" erl-dash" if dash else ""}"/>')

        def arrowhead(x, y, fx, fy):
            """arrowhead with tip at (x,y) coming from (fx,fy)"""
            dx, dy = x - fx, y - fy
            L = math.hypot(dx, dy) or 1
            ux, uy = dx / L, dy / L
            px, py = -uy, ux
            a = (x - ux * 11 + px * 5.5, y - uy * 11 + py * 5.5)
            b = (x - ux * 11 - px * 5.5, y - uy * 11 - py * 5.5)
            shapes.append(f'<polygon points="{x:.1f},{y:.1f} {a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f}" class="er-ah"/>')

        def label_near(x, y, fx, fy, s, cls='er-card', off=11, along=16, lpos=None):
            dx, dy = fx - x, fy - y
            L = math.hypot(dx, dy) or 1
            ux, uy = dx / L, dy / L
            px, py = -uy, ux
            if py > 0 or (abs(py) < 1e-6 and px < 0):   # keep labels above / right of the line
                px, py = -px, -py
            lx, ly = x + ux * along + px * off, y + uy * along + py * off
            if lpos:
                lx, ly = lpos
            ext(lx - 14, ly - 9, lx + 14, ly + 9)
            texts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="{cls}" text-anchor="middle" dominant-baseline="central">{esc(s)}</text>')

        # ---- attributes
        def ell_size(a):
            return max(30, tw(a.name, 12.5) / 2 + 15), 15

        def place_attrs(n):
            w, h = self.size(n)
            groups = {}
            for a, side in n.attrs:
                groups.setdefault(side, []).append(a)
            res = []
            for side, lst in groups.items():
                g = n.gap.get(side, n.gap.get('all', 44))
                if side in ('top', 'bottom'):
                    widths = [2 * ell_size(a)[0] + 10 for a in lst]
                    total = sum(widths)
                    x = n.x - total / 2
                    sgn = -1 if side == 'top' else 1
                    y = n.y + sgn * (h / 2 + g)
                    for a, wd in zip(lst, widths):
                        cx = x + wd / 2
                        x += wd
                        # slight arc: outer ones closer to the node
                        k = len(lst)
                        res.append((a, cx, y, side))
                else:
                    heights = [38 for _ in lst]
                    total = sum(heights)
                    y = n.y - total / 2 + 19
                    sgn = -1 if side == 'left' else 1
                    for a in lst:
                        rx, _ = ell_size(a)
                        cx = n.x + sgn * (w / 2 + g + rx)
                        res.append((a, cx, y, side))
                        y += 38
            out = []
            for a, cx, cy, side in res:
                if a.name in n.at:
                    cx, cy = n.at[a.name]
                out.append((a, cx, cy, side))
            return out

        def draw_attr(a, cx, cy, ox, oy, owner_shape, side, at):
            rx, ry = ell_size(a)
            # line from owner boundary to ellipse boundary
            if owner_shape is not None:
                sx, sy = self.boundary(owner_shape, cx, cy)
            else:
                # owner is another (composite) ellipse at (ox, oy) with radii
                orx, ory = at
                dx, dy = cx - ox, cy - oy
                s = 1 / math.sqrt((dx / orx) ** 2 + (dy / ory) ** 2) if (dx or dy) else 0
                sx, sy = ox + dx * s, oy + dy * s
            dx, dy = sx - cx, sy - cy
            s = 1 / math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2) if (dx or dy) else 0
            ex, ey = cx + dx * s, cy + dy * s
            seg([(sx, sy), (ex, ey)])
            cls = 'er-att' + (' er-der' if a.derived else '')
            if a.multi:
                shapes.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx + 4:.1f}" ry="{ry + 4:.1f}" class="{cls}"/>')
            shapes.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" class="{cls}"/>')
            ext(cx - rx - 5, cy - ry - 5, cx + rx + 5, cy + ry + 5)
            texts.append(f'<text x="{cx:.1f}" y="{cy:.1f}" class="er-at" text-anchor="middle" dominant-baseline="central">{esc(a.name)}</text>')
            if a.key or a.partial:
                half = tw(a.name, 12.5) * 0.56
                texts.append(f'<line x1="{cx - half:.1f}" y1="{cy + 8:.1f}" x2="{cx + half:.1f}" y2="{cy + 8:.1f}" '
                             f'class="er-ul{" er-ul-d" if a.partial else ""}"/>')
            # composite components
            if a.sub:
                k = len(a.sub)
                for i, s in enumerate(a.sub):
                    srx, _ = ell_size(s)
                    if side in ('top', 'bottom'):
                        spread = [2 * ell_size(t)[0] + 8 for t in a.sub]
                        tot = sum(spread)
                        x0 = cx - tot / 2 + sum(spread[:i]) + spread[i] / 2
                        y0 = cy + (-50 if side == 'top' else 50)
                    else:
                        x0 = cx + (-(rx + srx + 26) if side == 'left' else (rx + srx + 26))
                        y0 = cy + (i - (k - 1) / 2) * 36
                    if s.name in self._sub_at:
                        x0, y0 = self._sub_at[s.name]
                    draw_attr(s, x0, y0, cx, cy, None, side, (rx, ry))

        self._sub_at = self.opts.get('sub_at', {})

        for name in self.order:
            n = self.nodes[name]
            for a, cx, cy, side in place_attrs(n):
                draw_attr(a, cx, cy, n.x, n.y, n, side, None)

        # ---- relationship lines
        for rn in self.rels:
            r = self.nodes[rn]
            for e in r.ends:
                en = self.nodes[e.ent]
                pts_mid = e.via
                first = pts_mid[0] if pts_mid else (en.x, en.y)
                last = pts_mid[-1] if pts_mid else (r.x, r.y)
                if pts_mid:
                    a = self.attach(r, *first)
                    b = self.attach(en, *last)
                    pts = [a] + list(pts_mid) + [b]
                else:
                    a = self.boundary(r, en.x, en.y)
                    b = self.boundary(en, r.x, r.y)
                    pts = [a, b]
                seg(pts, total=e.total)
                ex_, ey_ = pts[-1]
                fx, fy = pts[-2]
                arrow = e.arrow if e.arrow is not None else (self.notation == 'arrow' and e.card == '1')
                if arrow == 'rel':
                    arrowhead(pts[0][0], pts[0][1], pts[1][0], pts[1][1])
                elif arrow:
                    arrowhead(ex_, ey_, fx, fy)
                if self.notation in ('label', 'both') and e.card:
                    label_near(ex_, ey_, fx, fy, e.card, lpos=e.lpos)
                if self.notation in ('minmax', 'both') and e.minmax:
                    label_near(ex_, ey_, fx, fy, e.minmax, cls='er-mm', along=34 if self.notation == 'both' else 30,
                               off=12, lpos=e.lpos if self.notation == 'minmax' else None)
                if e.role:
                    mx, my = (pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2
                    if len(pts) > 2:
                        mx, my = pts[len(pts) // 2]
                    texts.append(f'<text x="{mx:.1f}" y="{my - 8:.1f}" class="er-role" text-anchor="middle">{esc(e.role)}</text>')
                    ext(mx - tw(e.role, 11.5) / 2, my - 22, mx + tw(e.role, 11.5) / 2, my)

        # ---- ISA
        for iname in self.isas:
            n = self.nodes[iname]
            sup = self.nodes[n.sup]
            w, h = 56, 40
            top = n.y - h / 2
            b = self.boundary(sup, n.x, top)
            seg([b, (n.x, top)], total=n.total)
            tri = [(n.x - w / 2, top), (n.x + w / 2, top), (n.x, n.y + h / 2)]
            shapes.append('<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in tri) + '" class="er-isa"/>')
            ext(n.x - w / 2, top, n.x + w / 2, n.y + h / 2)
            texts.append(f'<text x="{n.x:.1f}" y="{n.y - 6:.1f}" class="er-isat" text-anchor="middle" dominant-baseline="central">{esc(n.label)}</text>')
            apex = (n.x, n.y + h / 2)
            for s in n.subs:
                sn = self.nodes[s]
                via = n.sublines.get(s)
                if via:
                    pts = [apex] + via + [self.boundary(sn, *via[-1])]
                else:
                    pts = [apex, self.boundary(sn, *apex)]
                seg(pts)
            note = n.note
            if note is None:
                note = ('disjoint' if n.disjoint else 'overlapping') + ', ' + ('total' if n.total else 'partial')
            if note:
                texts.append(f'<text x="{n.x + w / 2 + 8:.1f}" y="{n.y - 6:.1f}" class="er-isan" text-anchor="start" dominant-baseline="central">{esc(note)}</text>')
                ext(n.x + w / 2 + 8, n.y - 12, n.x + w / 2 + 14 + tw(note, 12), n.y)

        # ---- nodes
        for name in self.order + list(self.aggs):
            n = self.nodes[name]
            w, h = self.size(n)
            x0, y0 = n.x - w / 2, n.y - h / 2
            ext(x0, y0, x0 + w, y0 + h)
            if n.kind in ('ent', 'weak'):
                shapes.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h}" class="er-ent"/>')
                if n.kind == 'weak':
                    shapes.append(f'<rect x="{x0 + 4:.1f}" y="{y0 + 4:.1f}" width="{w - 8:.1f}" height="{h - 8}" class="er-ent2"/>')
                texts.append(f'<text x="{n.x:.1f}" y="{n.y:.1f}" class="er-et" text-anchor="middle" dominant-baseline="central">{esc(n.label)}</text>')
            elif n.kind in ('rel', 'idrel'):
                pts = [(n.x, y0), (x0 + w, n.y), (n.x, y0 + h), (x0, n.y)]
                shapes.append('<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '" class="er-rel"/>')
                if n.kind == 'idrel':
                    k = 6
                    pts = [(n.x, y0 + k * .62), (x0 + w - k, n.y), (n.x, y0 + h - k * .62), (x0 + k, n.y)]
                    shapes.append('<polygon points="' + ' '.join(f'{x:.1f},{y:.1f}' for x, y in pts) + '" class="er-rel2"/>')
                texts.append(f'<text x="{n.x:.1f}" y="{n.y:.1f}" class="er-rt" text-anchor="middle" dominant-baseline="central">{esc(n.label)}</text>')
            elif n.kind == 'agg':
                bx = n.box
                lines.insert(0, f'<rect x="{bx[0]}" y="{bx[1]}" width="{bx[2] - bx[0]}" height="{bx[3] - bx[1]}" rx="6" class="er-agg"/>')

        for x, y, s, cls, anc in self.extra:
            texts.append(f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anc}" dominant-baseline="central">{esc(s)}</text>')
            ext(x - (tw(s) if anc != 'start' else 0), y - 10, x + tw(s), y + 10)

        pad = 14
        x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
        W, H = x1 - x0, y1 - y0
        mw = maxw or W * scale
        svg = (f'<svg class="fig-svg er-svg" viewBox="{x0:.0f} {y0:.0f} {W:.0f} {H:.0f}" style="max-width:{mw:.0f}px" '
               f'role="img" aria-label="ER diagram {esc(self.id)}">'
               f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{W:.0f}" height="{H:.0f}" rx="12" class="er-bg"/>'
               + ''.join(lines) + ''.join(shapes) + ''.join(texts) + '</svg>')
        cap = f'<figcaption>{caption}</figcaption>' if caption else ''
        return f'<figure class="fig">{svg}{cap}</figure>'

    # ================================================================== mapping
    def mapping(self):
        """ER -> relational, minimum-tables version.  Returns list of Table."""
        opts = self.opts
        T = {}            # table name -> Table
        home = {}         # entity name -> table name that holds it
        notes = []

        def pk_of(ent):
            return T[home[ent]].pk_for(ent)

        # ---- subclass handling (ISA)
        sub_of = {}
        for iname in self.isas:
            n = self.nodes[iname]
            for s in n.subs:
                sub_of[s] = n

        def own_cols(node):
            cols, keys, partial, multis, derived = [], [], [], [], []
            for a, _ in node.attrs:
                if a.derived:
                    derived.append(a.name)
                    continue
                if a.multi:
                    multis.append(a)
                    continue
                c = a.simple_cols()
                cols += c
                if a.key:
                    keys.append(c)
                if a.partial:
                    partial += c
            return cols, keys, partial, multis, derived

        multi_tables = []

        # strong entities (not subclasses)
        for en in self.ents:
            n = self.nodes[en]
            if n.kind != 'ent' or en in sub_of:
                continue
            cols, keys, _, multis, derived = own_cols(n)
            t = Table(en, cols, keys[0] if keys else [], [en])
            for k in keys[1:]:
                t.unique.append(k)
            T[en] = t
            home[en] = en
            if derived:
                t.notes.append(f'derived attribute{"s" if len(derived) > 1 else ""} {", ".join(derived)} not stored (computed when needed)')
            multi_tables.append((en, multis))

        # ISA (needs superclass first; process in definition order, repeated for hierarchies)
        pending = list(self.isas)
        guard = 0
        while pending and guard < 20:
            guard += 1
            for iname in list(pending):
                n = self.nodes[iname]
                if n.sup not in home:
                    continue
                pending.remove(iname)
                sup_t = T[home[n.sup]]
                spk = sup_t.pk_for(n.sup)
                if n.method == 'er':
                    for s in n.subs:
                        sn = self.nodes[s]
                        cols, keys, _, multis, derived = own_cols(sn)
                        t = Table(s, list(spk) + cols, list(spk), [s])
                        t.fks.append(FK(list(spk), home[n.sup], list(spk), 'ON DELETE CASCADE'))
                        T[s] = t
                        home[s] = s
                        multi_tables.append((s, multis))
                elif n.method == 'sub':
                    # only subclass tables (valid when total): inherit all superclass columns
                    for s in n.subs:
                        sn = self.nodes[s]
                        cols, keys, _, multis, derived = own_cols(sn)
                        t = Table(s, list(sup_t.cols) + cols, list(spk), [n.sup, s])
                        t.fks = [FK(f.cols, f.ref, f.refcols, f.action) for f in sup_t.fks]
                        T[s] = t
                        home[s] = s
                        multi_tables.append((s, multis))
                    del T[sup_t.name]
                    home[n.sup] = None
                    notes.append(f'{n.sup} has no table of its own: every {n.sup} belongs to some subclass (total).')
                elif n.method in ('single', 'flags'):
                    for s in n.subs:
                        sn = self.nodes[s]
                        cols, keys, _, multis, derived = own_cols(sn)
                        sup_t.cols += cols
                        sup_t.merged.append(s)
                        home[s] = sup_t.name
                        multi_tables.append((s, multis))
                    if n.method == 'single':
                        tcol = opts.get('typecol', 'type')
                        sup_t.cols.append(tcol)
                        sup_t.notes.append(f'{tcol} tells which subclass the row belongs to (disjoint)')
                    else:
                        for s in n.subs:
                            sup_t.cols.append(f'is_{s.lower()}')
                        sup_t.notes.append('one boolean flag per subclass (overlap allowed)')

        # weak entities (owners must exist; loop until all placed)
        weak = [e for e in self.ents if self.nodes[e].kind == 'weak']
        guard = 0
        while weak and guard < 20:
            guard += 1
            for en in list(weak):
                n = self.nodes[en]
                idr = [self.nodes[r] for r in self.rels if self.nodes[r].kind == 'idrel' and any(e.ent == en and e.card.upper() != '1' for e in self.nodes[r].ends)]
                if not idr:
                    raise ValueError(f'weak entity {en} has no identifying relationship')
                r = idr[0]
                owners = [e.ent for e in r.ends if e.ent != en]
                if any(o not in home for o in owners):
                    continue
                weak.remove(en)
                cols, keys, partial, multis, derived = own_cols(n)
                pre = []
                fks = []
                for o in owners:
                    opk = T[home[o]].pk_for(o)
                    pre += opk
                    fks.append(FK(list(opk), home[o], list(opk), 'ON DELETE CASCADE'))
                rcols, _, _, rmult, _ = own_cols(r)
                t = Table(en, pre + cols + rcols, pre + partial, [en, r.name])
                t.fks = fks
                T[en] = t
                home[en] = en
                r.done = True
                multi_tables.append((en, multis))

        # aggregation: the aggregated relationship is handled first (must become its own table)
        agg_rel = {a.rel: a.name for a in self.aggs.values()}

        def rel_order():
            first = [r for r in self.rels if r in agg_rel]
            return first + [r for r in self.rels if r not in agg_rel]

        for rn in rel_order():
            r = self.nodes[rn]
            if r.kind == 'idrel':
                continue
            rcols, _, _, rmult, _ = own_cols(r)
            ends = r.ends
            if len(ends) == 2 and rn not in agg_rel and not any(x.ent in self.aggs for x in ends):
                a, b = ends
                ca, cb = a.card.upper(), b.card.upper()
                one_a, one_b = ca == '1', cb == '1'
                recursive = a.ent == b.ent
                if one_a and one_b:
                    # 1:1
                    if a.total and b.total and not recursive and opts.get(rn) != 'fk':
                        self._merge(T, home, a.ent, b.ent, rn, rcols)
                        continue
                    if a.total and not b.total:
                        holder, other = a, b
                    elif b.total and not a.total:
                        holder, other = b, a
                    else:
                        side = opts.get(rn + '_side')
                        holder, other = (b, a) if side == b.ent else (a, b)
                    self._fk_into(T, home, holder, other, rn, rcols, unique=True, notnull=holder.total)
                elif one_a != one_b:
                    # 1:N  -> FK on the N side, referencing the 1 side
                    many, one = (b, a) if one_a else (a, b)
                    self._fk_into(T, home, many, one, rn, rcols, unique=False, notnull=many.total)
                else:
                    self._rel_table(T, home, r, rcols)
            else:
                self._rel_table(T, home, r, rcols)
            if rmult:
                for m in rmult:
                    notes.append(f'multivalued relationship attribute {m.name} needs its own table')

        # multivalued attributes
        for en, multis in multi_tables:
            for a in multis:
                if home.get(en) is None:
                    continue
                pk = T[home[en]].pk_for(en)
                cols = a.leaf_names()
                tn = f'{en}_{a.name}'.replace(' ', '_')
                t = Table(tn, list(pk) + cols, list(pk) + cols, [])
                t.fks.append(FK(list(pk), home[en], list(pk), 'ON DELETE CASCADE'))
                t.notes.append(f'multivalued attribute {a.name} of {en}')
                T[tn] = t

        self.notes = notes
        self.tables = list(T.values())
        return self.tables

    # -------------------------------------------------- helpers
    def _merge(self, T, home, ea, eb, rn, rcols):
        ta, tb = T[home[ea]], T[home[eb]]
        bpk = tb.pk_for(eb)
        for c in tb.cols:
            if c not in ta.cols:
                ta.cols.append(c)
        ta.unique.append(list(bpk))
        ta.notnull += [c for c in bpk if c not in ta.pk]
        ta.cols += [c for c in rcols if c not in ta.cols]
        ta.merged += tb.merged + [rn]
        ta.fks += tb.fks
        ta.unique += tb.unique
        ta.notes.append(f'{eb} and {rn} merged in (1:1 with total participation on both sides); '
                        f'{", ".join(bpk)} is an alternate (candidate) key')
        ta.alias[eb] = list(bpk)
        for k, v in list(home.items()):
            if v == tb.name:
                home[k] = ta.name
        del T[tb.name]

    def _fk_into(self, T, home, holder, other, rn, rcols, unique, notnull):
        t = T[home[holder.ent]]
        opk = T[home[other.ent]].pk_for(other.ent)
        cols = []
        prefix = self.opts.get('prefix', {}).get(rn)
        for c in opk:
            nm = c
            if prefix:
                nm = f'{prefix}_{c}'
            elif nm in t.cols or holder.ent == other.ent:
                pref = other.role or rn
                nm = f'{pref}_{c}'.replace(' ', '_')
            cols.append(nm)
        t.cols += cols
        t.cols += [c for c in rcols if c not in t.cols]
        t.fks.append(FK(cols, home[other.ent], list(opk), '', via=rn))
        if unique:
            t.unique.append(cols)
        if notnull:
            t.notnull += cols
        t.merged.append(rn)

    def _rel_table(self, T, home, r, rcols):
        cols, pk, fks = [], [], []
        ends = r.ends
        n_ary = len(ends) > 2
        for e in ends:
            if e.ent in self.aggs:
                agg = self.aggs[e.ent]
                rt = T[agg.rel]
                epk = list(rt.pk)
                ref = agg.rel
            else:
                epk = T[home[e.ent]].pk_for(e.ent)
                ref = home[e.ent]
            names = []
            for c in epk:
                nm = c
                if nm in cols:
                    nm = f'{e.role or e.ent}_{c}'.replace(' ', '_')
                names.append(nm)
            cols += names
            fks.append(FK(names, ref, list(epk), ''))
            if len(ends) == 2:
                pk += names
            elif e.card.upper() != '1':
                pk += names
        if len(ends) == 2:
            a, b = ends
            if a.card.upper() == '1' and b.card.upper() == '1':
                pk = fks[0].cols
            elif a.card.upper() == '1' or b.card.upper() == '1':
                many = 0 if b.card.upper() == '1' else 1
                pk = fks[many].cols
        uniq = []
        if n_ary:
            ones = [i for i, e in enumerate(ends) if e.card.upper() == '1']
            if not ones:
                pk = list(cols)
            else:
                # each '1' end is functionally determined by all the other ends -> one candidate key per '1' end
                cks = [[c for j, f in enumerate(fks) if j != i for c in f.cols] for i in ones]
                pk, uniq = cks[0], cks[1:]
        t = Table(r.name, cols + [c for c in rcols if c not in cols], pk, [r.name])
        t.unique += uniq
        t.fks = fks
        T[r.name] = t
        return t

    # -------------------------------------------------- checks + rendering
    def check(self):
        tabs = self.mapping()
        if self.expect is not None:
            got = {t.sig() for t in tabs}
            exp = set()
            for s in self.expect:
                m = re.match(r'^\s*(\w+)\((.*)\)\s*$', s)
                name, cols = m.group(1), [c.strip() for c in m.group(2).split(',')]
                pk = frozenset(c[1:] for c in cols if c.startswith('_'))
                cs = frozenset(c.lstrip('_') for c in cols)
                exp.add((name, cs, pk))
            if got != exp:
                def show(sset):
                    return '\n   '.join(sorted(f'{n}({", ".join(sorted(c))}) pk={sorted(p)}' for n, c, p in sset))
                raise AssertionError(f'[{self.id}] mapping differs\n got only:\n   {show(got - exp)}\n expected only:\n   {show(exp - got)}')
        if any(not t.pk for t in tabs):
            if self.expect is not None:
                raise AssertionError(f'[{self.id}] table without primary key')
            self.ddl_sql = ''
            return tabs
        self.ddl_sql = ddl(tabs)
        run_ddl(self.id, tabs, self.ddl_sql)
        return tabs


class FK:
    def __init__(self, cols, ref, refcols, action='', via=None):
        self.cols, self.ref, self.refcols, self.action, self.via = list(cols), ref, list(refcols), action, via


class Table:
    def __init__(self, name, cols, pk, merged):
        self.name = name
        self.cols = list(dict.fromkeys(cols))
        self.pk = list(pk)
        self.merged = list(merged)
        self.fks = []
        self.unique = []
        self.notnull = []
        self.notes = []
        self.alias = {}

    def pk_for(self, ent):
        return self.alias.get(ent, self.pk)

    def sig(self):
        return (self.name, frozenset(self.cols), frozenset(self.pk))


# ---------------------------------------------------------------------- DDL
NUMW = ('salary', 'amount', 'price', 'fare', 'credits', 'hours', 'age', 'seats', 'count', 'balance', 'fee', 'stipend',
        'wages', 'rating', 'marks', 'budget', 'qty', 'quantity', 'cost', 'total', 'max', 'number_of', 'no_of', 'year', 'semester_no', 'capacity')
DATEW = ('date', 'dob', 'birth', 'since', 'time', 'day')


def coltype(c):
    l = c.lower()
    if l.startswith('is_'):
        return 'BOOLEAN'
    if any(w in l for w in DATEW):
        return 'TIME' if 'time' in l and 'date' not in l else 'DATE'
    if any(w in l for w in NUMW):
        return 'NUMERIC(10,2)' if any(w in l for w in ('salary', 'amount', 'price', 'fare', 'balance', 'fee', 'stipend', 'wages', 'budget', 'cost')) else 'INT'
    return 'VARCHAR(30)'


def ddl(tabs):
    out = []
    for t in tabs:
        lines = []
        for c in ordered(t):
            nn = ' NOT NULL' if (c in t.notnull and c not in t.pk) else ''
            lines.append(f'  {c} {coltype(c)}{nn}')
        lines.append(f'  PRIMARY KEY ({", ".join(t.pk)})')
        for u in t.unique:
            lines.append(f'  UNIQUE ({", ".join(u)})')
        for f in t.fks:
            act = f' {f.action}' if f.action else ''
            lines.append(f'  FOREIGN KEY ({", ".join(f.cols)}) REFERENCES {f.ref}({", ".join(f.refcols)}){act}')
        out.append(f'CREATE TABLE {t.name} (\n' + ',\n'.join(lines) + '\n);')
    return '\n'.join(out)


def run_ddl(eid, tabs, sql):
    """create the tables in SQLite and insert one row per table in FK order: catches wrong FK targets"""
    con = sqlite3.connect(':memory:')
    con.execute('PRAGMA foreign_keys=ON')
    con.executescript(sql.replace('BOOLEAN', 'INT'))
    names = {t.name: t for t in tabs}
    for t in tabs:
        for f in t.fks:
            if f.ref not in names:
                raise AssertionError(f'[{eid}] {t.name} references missing table {f.ref}')
            rt = names[f.ref]
            if set(f.refcols) != set(rt.pk) and not any(set(f.refcols) == set(u) for u in rt.unique):
                raise AssertionError(f'[{eid}] FK {t.name}{f.cols} -> {f.ref}{f.refcols} is not a key of {f.ref}')
    done, guard = set(), 0
    while len(done) < len(tabs) and guard < 50:
        guard += 1
        for t in tabs:
            if t.name in done:
                continue
            if any(f.ref not in done and f.ref != t.name for f in t.fks):
                continue
            vals = []
            for c in t.cols:
                v = 'v1'
                for f in t.fks:
                    if c in f.cols and f.ref == t.name:
                        v = None
                vals.append(v)
            # self-references: insert with NULL then they are fine
            q = f'INSERT INTO {t.name} ({", ".join(t.cols)}) VALUES ({", ".join("?" * len(t.cols))})'
            fk_self = {c for f in t.fks if f.ref == t.name for c in f.cols}
            vals = [None if c in fk_self and c not in t.pk else ('v1' if c not in fk_self else 'v1') for c in t.cols]
            con.execute(q, vals)
            done.add(t.name)
    if len(done) < len(tabs):
        # circular foreign keys (e.g. DEPT.head -> EMP, EMP.dept -> DEPT): real DBMSs need DEFERRABLE constraints;
        # here just make sure the remaining tables accept a row with checking switched off
        con.commit()
        con.execute('PRAGMA foreign_keys=OFF')
        for t in tabs:
            if t.name not in done:
                con.execute(f'INSERT INTO {t.name} ({", ".join(t.cols)}) VALUES ({", ".join("?" * len(t.cols))})', ['v1'] * len(t.cols))
        CYCLES.add(eid)
    con.close()


CYCLES = set()


def ordered(t):
    return [c for c in t.cols if c in t.pk] + [c for c in t.cols if c not in t.pk]


def schema_html(tabs, notes=(), show_fk=True):
    h = ['<div class="schema">']
    for t in tabs:
        fkcols = {c: f for f in t.fks for c in f.cols}
        cs = []
        for c in ordered(t):
            s = html.escape(c)
            if c in t.pk:
                s = f'<u>{s}</u>'
            if c in fkcols:
                s = f'<span class="fkc">{s}</span>'
            cs.append(s)
        merged = [m for m in t.merged if m != t.name]
        mtag = f'<span class="mg">+ {", ".join(html.escape(m) for m in merged)}</span>' if merged else ''
        h.append(f'<div class="srow"><span class="tn">{html.escape(t.name)}</span>({", ".join(cs)}){mtag}</div>')
        det = []
        if show_fk:
            for f in t.fks:
                det.append(f'FK {", ".join(f.cols)} → {html.escape(f.ref)}({", ".join(f.refcols)})'
                           + (f' <span class="muted">{f.action.lower()}</span>' if f.action else ''))
        for u in t.unique:
            if not any(set(u) == set(f.cols) for f in t.fks) or True:
                det.append(f'UNIQUE({", ".join(u)})')
        nn = [c for c in t.notnull if c not in t.pk]
        if nn:
            det.append(f'NOT NULL({", ".join(nn)})')
        det += [html.escape(n) for n in t.notes]
        if det:
            h.append(f'<div class="sdet">{" · ".join(det)}</div>')
    h.append(f'<div class="scount">{len(tabs)} table{"s" if len(tabs) != 1 else ""}'
             f'<span class="legend-k"> &nbsp;·&nbsp; <u>underlined</u> = primary key, <span class="fkc">purple italic</span> = foreign key</span></div>')
    for n in notes:
        h.append(f'<div class="sdet">{html.escape(n)}</div>')
    h.append('</div>')
    return ''.join(h)
