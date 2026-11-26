"""Hand-designed figures for Unit 4 (inline SVG, theme-aware via CSS classes)."""
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



# ====================================================================== Unit 4 figures


def nf_onion():
    """nested normal forms with what each one removes."""
    f = Fig(760, 340, 'normal forms nested inside each other', maxw=760)
    layers = [
        ('1NF', 'atomic values only (no repeating groups / multivalued cells)', 'bx-plain'),
        ('2NF', '+ no partial dependency of a non-prime attribute on a key', 'bx-plain'),
        ('3NF', '+ no transitive dependency (X→A needs X superkey or A prime)', 'bx-acc'),
        ('BCNF', '+ every determinant is a superkey', 'bx-good'),
        ('4NF', '+ no non-trivial MVD (beyond syllabus)', 'bx-mut'),
        ('5NF', 'no join dependency (beyond)', 'bx-mut'),
    ]
    x, y, w, h = 10, 10, 740, 320
    for k, (name, txt, cls) in enumerate(layers):
        f.box(x, y, w, h, cls=cls, rx=16)
        f.text(x + 14, y + 19, name, 't tb', anchor='start', fs=16)
        f.text(x + 14 + 11 * len(name) + 14, y + 19, txt, 't', anchor='start', fs=14)
        x += 20
        y += 46
        w -= 40
        h -= 52
    return f.render('Each normal form is stricter than the one outside it: a relation in BCNF is automatically in 3NF, 2NF and 1NF. '
                    'The syllabus stops at BCNF.')


def nf_flow():
    """decision procedure for the highest normal form."""
    f = Fig(720, 440, 'how to find the highest normal form', maxw=720)
    bw, bh, gap = 330, 54, 34
    x0 = 20
    cxm = x0 + bw / 2
    steps = [
        ('Find all candidate keys →\nprime / non-prime attributes', None),
        ('A non-prime attribute depends on a\nPROPER PART of a candidate key?', '1NF only'),
        ('A non-prime attribute depends on\na set that is NOT a superkey?', '2NF'),
        ('Some non-trivial X → A with X not\na superkey (so A must be prime)?', '3NF'),
    ]
    y = 10
    for k, (t, res) in enumerate(steps):
        f.box(x0, y, bw, bh, t, cls='bx-acc' if k == 0 else 'bx-plain', fs=14, lh=18)
        if res:
            f.arrow(x0 + bw, y + bh / 2, 500, y + bh / 2, 'bad')
            f.text((x0 + bw + 500) / 2, y + bh / 2 - 11, 'yes', 't ts', fs=13)
            f.box(502, y + 6, 196, bh - 12, f'highest NF = {res}', cls='bx-bad', fs=14)
        f.arrow(cxm, y + bh, cxm, y + bh + gap - 2, 'good')
        if k > 0:
            f.text(cxm + 10, y + bh + gap / 2, 'no', 't ts', anchor='start', fs=13)
        y += bh + gap
    f.box(cxm - 110, y, 220, 46, 'highest NF = BCNF', cls='bx-good', fs=15)
    return f.render('Test from the top; the first “yes” gives the answer. In words: partial dependency → only 1NF; '
                    'transitive dependency → only 2NF; a non-key determinant of a prime attribute → only 3NF; otherwise BCNF.')
