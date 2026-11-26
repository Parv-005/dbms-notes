"""Functional-dependency engine for the Unit 4 notes.

Every key / normal-form / decomposition answer in the notes is recomputed here at build time
(see checks.py), so a typo in a hand-written answer stops the build.

Attribute names: single letters ("ABC" = {A,B,C}) or names separated by commas/spaces
("StudentID, CourseID").  FDs: "AB->C, C->D" or a list of (lhs, rhs) strings.
"""
from itertools import combinations
import html


# ----------------------------------------------------------------- parsing / printing
def aset(s):
    """'ABC' -> {A,B,C};  'StudentID, CourseID' -> {StudentID, CourseID}; set/list passes through."""
    if isinstance(s, (set, frozenset, list, tuple)):
        return frozenset(s)
    s = s.strip().strip('{}()')
    if not s or s == '∅':
        return frozenset()
    if ',' in s or ' ' in s:
        return frozenset(t for t in s.replace(',', ' ').split() if t)
    if s.isalpha() and s.isupper():
        return frozenset(s)          # 'ABC' = three single-letter attributes
    return frozenset([s])            # one named attribute


def fds(spec):
    """'AB->C, C->D' (single-letter) or 'StudentID CourseID -> Semester; X -> Y' (';' separated when names are used)."""
    if not isinstance(spec, str):
        return [(aset(l), aset(r)) for l, r in spec]
    sep = ';' if ';' in spec else ','
    out = []
    for part in spec.split(sep):
        part = part.strip()
        if not part:
            continue
        l, r = part.replace('→', '->').split('->')
        out.append((aset(l), aset(r)))
    return out


ORDER = {}
SHORT = {}          # optional display abbreviations (set temporarily by renderers)


def srt(X):
    return sorted(X, key=lambda a: (ORDER.get(a, 999), a))


def show(X, sep=None):
    X = [SHORT.get(a, a) for a in srt(X)]
    if not X:
        return '∅'
    if sep is None:
        sep = '' if all(len(a) == 1 for a in X) else ', '
    return sep.join(X)


def showfd(f):
    l, r = f
    return f'{show(l)} → {show(r)}'


# ----------------------------------------------------------------- core algorithms
def closure(X, F, trace=False):
    X = set(aset(X))
    steps = []
    changed = True
    while changed:
        changed = False
        for l, r in F:
            if l <= X and not r <= X:
                new = r - X
                X |= r
                steps.append(((l, r), frozenset(new), frozenset(X)))
                changed = True
    return (frozenset(X), steps) if trace else frozenset(X)


def is_superkey(X, R, F):
    return closure(X, F) >= R


def candidate_keys(R, F):
    R = aset(R)
    rhs = set().union(*[r - l for l, r in F]) if F else set()
    lhs = set().union(*[l for l, r in F]) if F else set()
    core = frozenset(a for a in R if a not in rhs)      # never determined -> in every key
    rest = [a for a in srt(R - core)]
    keys = []
    if is_superkey(core, R, F):
        return [core]
    for k in range(1, len(rest) + 1):
        for comb in combinations(rest, k):
            X = core | frozenset(comb)
            if any(K <= X for K in keys):
                continue
            if is_superkey(X, R, F):
                keys.append(X)
    return keys


def prime_attrs(R, F):
    return frozenset().union(*candidate_keys(R, F))


def count_superkeys(R, F):
    R = aset(R)
    keys = candidate_keys(R, F)
    n = 0
    for k in range(len(R) + 1):
        for comb in combinations(srt(R), k):
            if any(K <= set(comb) for K in keys):
                n += 1
    return n


def split_rhs(F):
    return [(l, frozenset([a])) for l, r in F for a in srt(r) if a not in l]


def minimal_cover(F, trace=False):
    steps = []
    G = []
    for f in split_rhs(F):
        if f not in G:
            G.append(f)
    steps.append(('split', list(G)))
    # remove extraneous LHS attributes
    H = []
    for l, r in G:
        L = set(l)
        for a in srt(l):
            if len(L) > 1 and r <= closure(L - {a}, G):
                steps.append(('lhs', (frozenset(L), r), a))
                L -= {a}
        H.append((frozenset(L), r))
    G = []
    for f in H:
        if f not in G:
            G.append(f)
    # remove redundant FDs
    i = 0
    while i < len(G):
        f = G[i]
        rest = G[:i] + G[i + 1:]
        if f[1] <= closure(f[0], rest):
            steps.append(('red', f))
            G = rest
        else:
            i += 1
    return (G, steps) if trace else G


def combine(F):
    """merge FDs with the same LHS (for printing a canonical cover)."""
    out = []
    for l, r in F:
        for k, (l2, r2) in enumerate(out):
            if l2 == l:
                out[k] = (l, r2 | r)
                break
        else:
            out.append((l, r))
    return out


def equivalent(F, G):
    return all(r <= closure(l, G) for l, r in F) and all(r <= closure(l, F) for l, r in G)


def project(F, Ri, minimal=True):
    """FDs of F+ that hold on Ri (computed from closures of all subsets)."""
    Ri = aset(Ri)
    out = []
    for k in range(1, len(Ri)):
        for comb in combinations(srt(Ri), k):
            X = frozenset(comb)
            Y = (closure(X, F) & Ri) - X
            if Y:
                out.append((X, Y))
    return combine(minimal_cover(out)) if minimal else out


# ----------------------------------------------------------------- normal forms
def nf_report(R, F):
    """Returns dict with keys, prime, per-FD analysis and highest NF (1..BCNF as 1,2,3,'BCNF')."""
    R = aset(R)
    keys = candidate_keys(R, F)
    prime = frozenset().union(*keys)
    rows = []
    partial = []
    # 2NF: non-prime attribute determined by a proper subset of a key
    for K in keys:
        for k in range(1, len(K)):
            for comb in combinations(srt(K), k):
                S = frozenset(comb)
                dep = (closure(S, F) - S) & (R - prime)
                if dep:
                    partial.append((S, dep, K))
    trans = []
    bcnf_v = []
    for l, r in split_rhs(F):
        sk = is_superkey(l, R, F)
        a = next(iter(r))
        p = a in prime
        rows.append(dict(fd=(l, r), superkey=sk, prime_rhs=p))
        if not sk:
            bcnf_v.append((l, r))
            if not p:
                trans.append((l, r))
    if partial:
        nf = 1
    elif trans:
        nf = 2
    elif bcnf_v:
        nf = 3
    else:
        nf = 'BCNF'
    return dict(keys=keys, prime=prime, nonprime=R - prime, rows=rows, partial=partial, trans=trans,
                bcnf_viol=bcnf_v, nf=nf)


def nf_name(n):
    return {1: '1NF', 2: '2NF', 3: '3NF', 'BCNF': 'BCNF'}[n]


def bcnf_decompose(R, F, trace=False, pick=None):
    """Standard algorithm: while some Ri has a non-trivial X->Y (from F+) with X not a superkey of Ri,
    replace Ri by (X ∪ Y) and (Ri − (Y − X)) where Y = X+ ∩ Ri."""
    R = aset(R)
    result = [R]
    steps = []
    while True:
        for i, Ri in enumerate(result):
            viol = None
            cand = [f for f in split_rhs(F) if f[0] <= Ri and f[1] <= Ri]
            # also FDs implied on Ri (projection)
            cand += [f for f in project(F, Ri) if f not in cand]
            for l, r in cand:
                Xp = closure(l, F) & Ri
                if not Xp >= Ri:
                    viol = (l, Xp - l)
                    break
            if viol:
                l, Y = viol
                R1 = l | Y
                R2 = Ri - Y
                steps.append((Ri, viol, R1, R2))
                result = result[:i] + [R1, R2] + result[i + 1:]
                break
        else:
            break
    return (result, steps) if trace else result


def synth_3nf(R, F, trace=False):
    R = aset(R)
    G = combine(minimal_cover(F))
    rels = [l | r for l, r in G]
    keys = candidate_keys(R, F)
    added = None
    if not any(K <= Ri for K in keys for Ri in rels):
        added = keys[0]
        rels.append(keys[0])
    # remove relations contained in others
    out = []
    for i, Ri in enumerate(rels):
        if any(Ri < Rj for j, Rj in enumerate(rels) if j != i) or Ri in out:
            continue
        out.append(Ri)
    return (out, G, added) if trace else out


# ----------------------------------------------------------------- decomposition tests
def binary_lossless(R1, R2, F):
    R1, R2 = aset(R1), aset(R2)
    c = closure(R1 & R2, F)
    return c >= R1 or c >= R2


def chase(R, decomp, F):
    """Tableau (chase) test. Returns (lossless, tableau rows) with 'a' / 'b<i>' symbols."""
    R = srt(aset(R))
    decomp = [aset(d) for d in decomp]
    T = [[('a' if A in Ri else f'b{i + 1}') for A in R] for i, Ri in enumerate(decomp)]
    idx = {A: j for j, A in enumerate(R)}
    changed = True
    while changed:
        changed = False
        for l, r in split_rhs(F):
            for i in range(len(T)):
                for k in range(i + 1, len(T)):
                    if all(T[i][idx[A]] == T[k][idx[A]] for A in l):
                        for A in r:
                            j = idx[A]
                            x, y = T[i][j], T[k][j]
                            if x != y:
                                keep = 'a' if 'a' in (x, y) else min(x, y)
                                drop = y if keep == x else x
                                for row in T:
                                    if row[j] == drop:
                                        row[j] = keep
                                changed = True
    ok = any(all(v == 'a' for v in row) for row in T)
    return ok, R, T


def preserves(F, decomp, trace=False):
    """Dependency preservation via the res-algorithm (no F+ needed)."""
    decomp = [aset(d) for d in decomp]
    report = []
    allok = True
    for l, r in F:
        res = set(l)
        steps = []
        changed = True
        while changed:
            changed = False
            for Ri in decomp:
                t = closure(res & Ri, F) & Ri
                if not t <= res:
                    steps.append((Ri, frozenset(t - res)))
                    res |= t
                    changed = True
        ok = r <= res
        allok &= ok
        report.append(((l, r), ok, frozenset(res), steps))
    return (allok, report) if trace else allok


def holds_in(rows, cols, l, r):
    """Does FD l->r hold in this relation instance?"""
    idx = {c: i for i, c in enumerate(cols)}
    seen = {}
    for row in rows:
        k = tuple(row[idx[a]] for a in srt(l))
        v = tuple(row[idx[a]] for a in srt(r))
        if k in seen and seen[k] != v:
            return False
        seen[k] = v
    return True


# ----------------------------------------------------------------- HTML helpers
def h(s):
    return html.escape(s)


def closure_html(X, F, R=None):
    """step list for X+ (used inside answers)."""
    c, steps = closure(X, F, trace=True)
    out = [f'<span class="cl">{h(show(aset(X)))}<sup>+</sup> = {h(show(aset(X)))}']
    for f, new, now in steps:
        out.append(f' <span class="muted">→ ({h(showfd(f))})</span> {h(show(now))}')
    out.append('</span>')
    tag = ''
    if R is not None:
        tag = ' ✔ superkey' if c >= aset(R) else ''
    return ''.join(out) + tag


def chase_html(R, decomp, F, names=None):
    ok, cols, T = chase(R, decomp, F)
    names = names or [show(aset(d)) for d in decomp]
    head = ''.join(f'<th>{h(c)}</th>' for c in cols)
    body = ''
    for name, row in zip(names, T):
        full = all(v == 'a' for v in row)
        cells = ''.join('<td class="ta">a</td>' if v == 'a' else f'<td class="tb">b<sub>{v[1:]}</sub></td>' for v in row)
        rc = ' class="fullrow"' if full else ''
        body += f'<tr{rc}><th>{h(name)}</th>{cells}</tr>'
    verdict = ('<b>A row of all a’s appears → lossless.</b>' if ok else '<b>No row becomes all a’s → lossy.</b>')
    return (f'<div class="tbl-wrap"><table class="tbl small center chase"><tr><th></th>{head}</tr>{body}</table></div>'
            f'<p class="small">Final tableau after applying the FDs until nothing changes. {verdict}</p>')
