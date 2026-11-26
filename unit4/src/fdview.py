"""Problem registry + HTML/SVG renderers built on fd.py.

A Prob holds R and F plus the hand-written expected answers. Prob.check() recomputes everything
with fd.py and raises if a hand-written answer is wrong, so the notes cannot drift from the maths.
"""
import fd
from fd import aset, fds, show, showfd, closure, srt
from svglib import markers, uid, esc

REG = {}


def _norm_list(xs):
    return sorted(sorted(aset(x)) for x in xs)


class Prob:
    def __init__(self, pid, R, F, keys=None, nf=None, bcnf=None, tnf=None, decomps=None, superkeys=None,
                 short=None, cover=None, twonf=None):
        self.id = pid
        if isinstance(R, str) and (',' in R or ' ' in R):
            self.order = [t for t in R.replace(',', ' ').split() if t]
        elif isinstance(R, str):
            self.order = list(R)
        else:
            self.order = list(R)
        self.R = frozenset(self.order)
        self.F = fds(F)
        self.short = short or {}          # long name -> abbreviation for diagrams
        self.exp = dict(keys=keys, nf=nf, bcnf=bcnf, tnf=tnf, superkeys=superkeys, cover=cover, twonf=twonf)
        self.decomps = decomps or {}      # name -> (list of relations, lossless?, preserving?)
        REG[pid] = self

    # -------------------------------------------------- checking
    def use(self):
        fd.ORDER = {a: i for i, a in enumerate(self.order)}

    def check(self):
        self.use()
        e = self.exp
        rep = fd.nf_report(self.R, self.F)
        self.rep = rep
        err = []
        if e['keys'] is not None and _norm_list(e['keys']) != _norm_list(rep['keys']):
            err.append(f"keys {e['keys']} != {[show(k) for k in rep['keys']]}")
        if e['nf'] is not None and e['nf'] != fd.nf_name(rep['nf']):
            err.append(f"nf {e['nf']} != {fd.nf_name(rep['nf'])}")
        if e['superkeys'] is not None and e['superkeys'] != fd.count_superkeys(self.R, self.F):
            err.append(f"superkeys {e['superkeys']} != {fd.count_superkeys(self.R, self.F)}")
        for name, rels in (('bcnf', e['bcnf']), ('tnf', e['tnf']), ('twonf', e['twonf'])):
            if rels is None:
                continue
            rels = [aset(r) for r in rels]
            if set().union(*rels) != self.R:
                err.append(f'{name}: attributes lost')
            if not fd.chase(self.R, rels, self.F)[0]:
                err.append(f'{name}: decomposition is lossy')
            for Ri in rels:
                sub = fd.nf_report(Ri, fd.project(self.F, Ri))
                need = {'bcnf': 'BCNF', 'tnf': 3, 'twonf': 2}[name]
                ok = sub['nf'] == 'BCNF' if need == 'BCNF' else (sub['nf'] == 'BCNF' or sub['nf'] >= need)
                if not ok:
                    err.append(f'{name}: {show(Ri)} is only {fd.nf_name(sub["nf"])}')
        if e['cover'] is not None:
            G = fds(e['cover'])
            if not fd.equivalent(G, self.F):
                err.append('cover not equivalent')
            if fd.minimal_cover(G) and len(fd.split_rhs(G)) != len(fd.split_rhs(fd.minimal_cover(G))):
                err.append('cover not minimal')
            for l, r in fd.split_rhs(G):
                for a in l:
                    if len(l) > 1 and r <= closure(l - {a}, G):
                        err.append(f'cover: {a} extraneous in {showfd((l, r))}')
        for name, (rels, ll, dp) in self.decomps.items():
            rels = [aset(r) for r in rels]
            if fd.chase(self.R, rels, self.F)[0] != ll:
                err.append(f'decomp {name}: lossless should be {not ll}')
            if fd.preserves(self.F, rels) != dp:
                err.append(f'decomp {name}: preserving should be {not dp}')
        if err:
            raise AssertionError(f'[{self.id}] ' + '; '.join(err))
        return True

    def rels(self, name):
        if name in self.decomps:
            return [aset(r) for r in self.decomps[name][0]]
        return [aset(r) for r in self.exp[name]]


# ====================================================== renderers
def _h(s):
    return esc(s)


def _ab(p, a):
    return p.short.get(a, a)


def fdd(pid, cap=''):
    """Dependency diagram: attributes in a row, one lane per FD underneath (Elmasri style)."""
    p = REG[pid]
    p.use()
    attrs = p.order
    labels = [_ab(p, a) for a in attrs]
    cw = [max(34, 9 + 7.6 * len(s)) for s in labels]
    gap = 10
    x = 14
    pos = {}
    for a, w in zip(attrs, cw):
        pos[a] = (x, w)
        x += w + gap
    W = x + 4
    scale = 1.3 if W < 560 else 1.0
    keys = p.rep['keys'] if hasattr(p, 'rep') else fd.candidate_keys(p.R, p.F)
    pk = keys[0] if keys else frozenset()
    rep = fd.nf_report(p.R, p.F)
    viol = {}
    for l, r in fd.split_rhs(p.F):
        if not fd.is_superkey(l, p.R, p.F):
            a = next(iter(r))
            if a not in rep['prime']:
                part = any(l < K for K in rep['keys'])
                viol[(l, a)] = 'bad' if part else 'warn'
            else:
                viol[(l, a)] = 'pur'
    y0, bh = 14, 30
    lane0 = y0 + bh + 16
    lh = 20
    H = lane0 + lh * len(p.F) + 6
    mid = uid()
    out = [f'<svg class="fig-svg fdd" viewBox="0 0 {W:.0f} {H:.0f}" style="max-width:{W * scale:.0f}px" role="img" '
           f'aria-label="dependency diagram">', markers(mid)]
    for a, s in zip(attrs, labels):
        x, w = pos[a]
        cls = 'bx bx-acc' if a in pk else 'bx'
        out.append(f'<rect x="{x:.1f}" y="{y0}" width="{w:.1f}" height="{bh}" rx="6" class="{cls}"/>')
        ul = ' text-decoration="underline"' if a in pk else ''
        out.append(f'<text x="{x + w / 2:.1f}" y="{y0 + bh / 2:.1f}" class="t" text-anchor="middle" dominant-baseline="central" '
                   f'style="font-size:12.5px"{ul}>{_h(s)}</text>')
    for k, (l, r) in enumerate(p.F):
        y = lane0 + lh * k
        kinds = {viol.get((l, a)) for a in r}
        c = 'bad' if 'bad' in kinds else 'warn' if 'warn' in kinds else 'pur' if 'pur' in kinds else 'ink'
        lc = 'e-' + c
        mk = c
        xs = []
        for a in l:
            x, w = pos[a]
            cx = x + w / 2 - 5
            xs.append(cx)
            out.append(f'<line x1="{cx:.1f}" y1="{y0 + bh}" x2="{cx:.1f}" y2="{y}" class="edge {lc}"/>')
        for a in r:
            x, w = pos[a]
            cx = x + w / 2 + 5
            xs.append(cx)
            out.append(f'<line x1="{cx:.1f}" y1="{y}" x2="{cx:.1f}" y2="{y0 + bh + 2}" class="edge {lc}" marker-end="url(#{mid}-{mk})"/>')
        out.append(f'<line x1="{min(xs):.1f}" y1="{y}" x2="{max(xs):.1f}" y2="{y}" class="edge {lc}"/>')
        out.append(f'<circle cx="{min(x for x in xs):.1f}" cy="{y}" r="2.6" class="dot-{mk}"/>')
    out.append('</svg>')
    legend = ('<span class="lg"><i class="lg-ink"></i>OK (LHS is a superkey)</span>'
              '<span class="lg"><i class="lg-bad"></i>partial dependency (breaks 2NF)</span>'
              '<span class="lg"><i class="lg-acc"></i>transitive (breaks 3NF)</span>'
              '<span class="lg"><i class="lg-mut"></i>RHS prime, LHS not a key (breaks BCNF only)</span>')
    used = set(viol.values())
    legend_items = ['<span class="lg"><i class="lg-ink"></i>LHS is a superkey</span>']
    if 'bad' in used:
        legend_items.append('<span class="lg"><i class="lg-bad"></i>partial dependency (breaks 2NF)</span>')
    if 'warn' in used:
        legend_items.append('<span class="lg"><i class="lg-warn"></i>transitive dependency (breaks 3NF)</span>')
    if 'pur' in used:
        legend_items.append('<span class="lg"><i class="lg-pur"></i>RHS prime, LHS not a superkey (breaks BCNF only)</span>')
    del legend
    abbr = ', '.join(f'{v} = {k}' for k, v in p.short.items() if k in p.R)
    if abbr:
        cap = (cap + ' ' if cap else '') + f'Abbreviations (also used in the closure lines): {abbr}.'
    capt = (cap + ' ' if cap else '') + 'Shaded, underlined boxes = ' + ('the candidate key' if len(keys) == 1 else 'one candidate key') + '.'
    return (f'<figure class="fig">{"".join(out)}<figcaption>{capt}<br><span class="legend-row">{"".join(legend_items)}</span>'
            f'</figcaption></figure>')


def cl(pid, X):
    """closure trace, one line (uses the problem's abbreviations)."""
    p = REG[pid]
    p.use()
    X = aset(X)
    fd.SHORT = p.short
    c, steps = closure(X, p.F, trace=True)
    s = f'<span class="cl"><b>{{{_h(show(X))}}}<sup>+</sup></b> : {_h(show(X))}'
    for f, new, now in steps:
        s += f' → {_h(show(now))}<span class="via">[{_h(showfd(f))}]</span>'
    s += '</span>'
    if c >= p.R:
        s += ' <span class="ok">= all attributes ✔</span>'
    fd.SHORT = {}
    return s


def keysteps(pid):
    """the standard key-finding method, generated."""
    p = REG[pid]
    p.use()
    F = p.F
    rhs = set().union(*[r - l for l, r in F])
    lhs = set().union(*[l for l, r in F])
    never = [a for a in p.order if a not in rhs]
    only_r = [a for a in p.order if a in rhs and a not in lhs]
    both = [a for a in p.order if a in rhs and a in lhs]
    keys = fd.candidate_keys(p.R, F)
    li = []
    li.append(f'<li>Attributes that never appear on a right-hand side (must be in <b>every</b> key): '
              f'<b>{_h(show(never)) if never else "none"}</b>.'
              + (f' Attributes only on the right-hand side (in <b>no</b> key): {_h(show(only_r))}.' if only_r else '') + '</li>')
    core = frozenset(never)
    if never:
        c = closure(core, F)
        if c >= p.R:
            li.append(f'<li>{cl(pid, core)} → <b>{{{_h(show(core))}}} is the only candidate key</b> (every key must contain it, and it is already a key).</li>')
        else:
            li.append(f'<li>{cl(pid, core)} — not all attributes, so add attributes from {{{_h(show(both))}}}.</li>')
    if not (never and closure(core, F) >= p.R):
        lines = ''.join(f'<div>{cl(pid, K)}</div>' for K in keys)
        li.append(f'<li>Candidate keys found (each is minimal — no proper subset’s closure gives all attributes):{lines}</li>')
    prime = frozenset().union(*keys)
    li.append(f'<li><b>Candidate key{"s" if len(keys) > 1 else ""}: {", ".join("{" + _h(show(k)) + "}" for k in keys)}</b>. '
              f'Prime attributes: {{{_h(show(prime))}}}; non-prime: {{{_h(show(p.R - prime)) if p.R - prime else ""}}}{"" if p.R - prime else "none"}.</li>')
    return '<ol class="steps">' + ''.join(li) + '</ol>'


def nft(pid):
    """per-FD normal-form test table."""
    p = REG[pid]
    p.use()
    rep = fd.nf_report(p.R, p.F)
    keys, prime = rep['keys'], rep['prime']
    rows = []
    for l, r in p.F:
        sk = fd.is_superkey(l, p.R, p.F)
        npr = frozenset(a for a in r if a not in prime and a not in l)
        if sk:
            verdict, cls = 'OK in every NF', 'y'
        elif npr and any(l < K for K in keys):
            verdict, cls = '<b>Partial</b> → violates 2NF<br><span class="small muted">LHS is part of a key, RHS non-prime</span>', 'n'
        elif npr:
            verdict, cls = '<b>Transitive</b> → violates 3NF<br><span class="small muted">LHS not a key, RHS non-prime</span>', 'n'
        else:
            verdict, cls = 'OK in 3NF, <b>violates BCNF</b><br><span class="small muted">RHS prime, but LHS not a superkey</span>', 'w'
        rr = srt(r - l)
        pp = [a for a in rr if a in prime]
        nn = [a for a in rr if a not in prime]
        pr = '; '.join(x for x in (f'prime: {_h(show(pp))}' if pp else '', f'non-prime: {_h(show(nn))}' if nn else '') if x)
        rows.append(f'<tr><td>{_h(showfd((l, r)))}</td><td class="{"y" if sk else "n"}">{"yes" if sk else "no"}</td>'
                    f'<td>{pr}</td><td class="{cls}">{verdict}</td></tr>')
    hi = fd.nf_name(rep['nf'])
    extra = ''
    if rep['nf'] == 1:
        # partial dependencies that come only through closure (not visible in a single FD)
        vis = {(l, a) for l, r in p.F for a in r if any(l < K for K in keys) and a not in prime}
        hidden = [(S, d) for S, d, K in rep['partial'] if not any((S, a) in vis for a in d)]
        if hidden and not vis:
            S, d = hidden[0]
            extra = (f'<p class="small">The partial dependency is implied rather than listed: {cl(pid, S)}, so the non-prime '
                     f'{_h(show(d))} depends on part of a key.</p>')
    return (f'<div class="tbl-wrap"><table class="tbl small nft"><tr><th>FD</th><th>LHS superkey?</th><th>RHS attributes</th>'
            f'<th>Verdict</th></tr>{"".join(rows)}</table></div>{extra}'
            f'<p class="answer-line">Highest normal form: {hi}.</p>')


def chase(pid, name):
    p = REG[pid]
    p.use()
    rels = p.rels(name)
    names = [f'R{i + 1}({show(r)})' for i, r in enumerate(rels)]
    return fd.chase_html(p.R, rels, p.F, names)


def pres(pid, name):
    p = REG[pid]
    p.use()
    rels = p.rels(name)
    ok, report = fd.preserves(p.F, rels, trace=True)
    proj = ''.join(f'<li>R{i + 1}({_h(show(Ri))}): {", ".join(_h(showfd(f)) for f in fd.project(p.F, Ri)) or "only trivial FDs"}</li>'
                   for i, Ri in enumerate(rels))
    rows = ''
    idx = {Ri: i + 1 for i, Ri in enumerate(rels)}
    for (l, r), good, res, steps in report:
        how = ' → '.join(f'R{idx[Ri]}: +{_h(show(new))}' for Ri, new in steps) or 'nothing can be added'
        rows += (f'<tr><td>{_h(showfd((l, r)))}</td><td class="small">{how}</td><td>{_h(show(res))}</td>'
                 f'<td class="{"y" if good else "n"}">{"preserved" if good else "LOST"}</td></tr>')
    return (f'<p class="small">FDs that hold inside each relation (projection of F):</p><ul class="small">{proj}</ul>'
            f'<div class="tbl-wrap"><table class="tbl small"><tr><th>FD of F</th><th>res-algorithm (start res = LHS; repeat res ∪= (res∩Ri)<sup>+</sup>∩Ri)</th>'
            f'<th>final res</th><th>Result</th></tr>{rows}</table></div>'
            f'<p class="answer-line">{"Dependency preserving." if ok else "Not dependency preserving."}</p>')


def dec(pid, kind):
    """decomposition steps (bcnf algorithm trace or 3nf synthesis), generated."""
    p = REG[pid]
    p.use()
    if kind == 'bcnf':
        res, steps = fd.bcnf_decompose(p.R, p.F, trace=True)
        li = []
        for Ri, (l, Y), R1, R2 in steps:
            li.append(f'<li>In ({_h(show(Ri))}): {_h(show(l))} → {_h(show(Y))} holds and {_h(show(l))} is not a superkey of it '
                      f'({_h(show(l))}<sup>+</sup> ∩ R = {_h(show(closure(l, p.F) & Ri))}). Split into '
                      f'<b>({_h(show(R1))})</b> and <b>({_h(show(R2))})</b>.</li>')
        li.append(f'<li>No relation has a violating FD any more. Result: '
                  + ', '.join(f'<b>R{i + 1}({_h(show(r))})</b>' for i, r in enumerate(res)) + '.</li>')
        return '<ol class="steps">' + ''.join(li) + '</ol>'
    if kind == '3nf':
        rels, G, added = fd.synth_3nf(p.R, p.F, trace=True)
        li = [f'<li>Minimal cover: {", ".join(_h(showfd(f)) for f in G)}.</li>',
              '<li>One relation per FD (LHS ∪ RHS): ' + ', '.join(f'({_h(show(l | r))})' for l, r in G) + '.</li>']
        if added:
            li.append(f'<li>No relation contains a candidate key → add ({_h(show(added))}).</li>')
        else:
            li.append('<li>A candidate key is already inside one relation → nothing to add.</li>')
        li.append('<li>Result: ' + ', '.join(f'<b>R{i + 1}({_h(show(r))})</b>' for i, r in enumerate(rels)) + '.</li>')
        return '<ol class="steps">' + ''.join(li) + '</ol>'
    raise KeyError(kind)


def schema(pid, name, keys=True):
    """list of relations with their keys underlined."""
    p = REG[pid]
    p.use()
    rels = p.rels(name)
    out = []
    for i, Ri in enumerate(rels):
        F = fd.project(p.F, Ri)
        K = fd.candidate_keys(Ri, F)
        k0 = K[0]
        cols = [f'<u>{_h(a)}</u>' if a in k0 else _h(a) for a in srt(k0)] + [_h(a) for a in srt(Ri - k0)]
        other = (' <span class="muted small">(other keys: ' + ', '.join('{' + _h(show(k)) + '}' for k in K[1:]) + ')</span>') if len(K) > 1 else ''
        fds_ = ', '.join(_h(showfd(f)) for f in F) or '—'
        out.append(f'<tr><td><b>R{i + 1}</b>({", ".join(cols)}){other}</td><td class="small">{fds_}</td>'
                   f'<td>{fd.nf_name(fd.nf_report(Ri, F)["nf"])}</td></tr>')
    return ('<div class="tbl-wrap"><table class="tbl small"><tr><th>Relation (key underlined)</th><th>FDs inside it</th><th>NF</th></tr>'
            + ''.join(out) + '</table></div>')


HANDLERS = dict(fdd=lambda a: fdd(*_args(a)), cl=lambda a: cl(*_args(a)), keys=lambda a: keysteps(_args(a)[0]),
                nft=lambda a: nft(_args(a)[0]), chase=lambda a: chase(*_args(a)), pres=lambda a: pres(*_args(a)),
                dec=lambda a: dec(*_args(a)), schema=lambda a: schema(*_args(a)))


def _args(a):
    return [x.strip() for x in a.split('|')]
