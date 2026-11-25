"""A tiny relational-algebra engine (set semantics) used to compute and verify every RA example.

Relations are immutable: R(attrs, rows).  Rows inside predicates are given as a dict-like object
`t` so you can write  lambda t: t['color'] == 'red'.
"""
from itertools import product as _prod

NULL = None


class Row(dict):
    __getattr__ = dict.__getitem__


class R:
    def __init__(self, attrs, rows=()):
        self.attrs = tuple(attrs)
        if len(set(self.attrs)) != len(self.attrs):
            raise ValueError(f'duplicate attribute names {self.attrs} — rename first')
        self.rows = frozenset(tuple(r) for r in rows)
        for r in self.rows:
            if len(r) != len(self.attrs):
                raise ValueError('arity mismatch')

    # ---- helpers
    def _d(self, r):
        return Row(zip(self.attrs, r))

    def __len__(self):
        return len(self.rows)

    def __eq__(self, o):
        return isinstance(o, R) and self.rows == o.rows and len(self.attrs) == len(o.attrs)

    def __hash__(self):
        return hash(self.rows)

    def __repr__(self):
        return f'R{self.attrs} {sorted(self.rows, key=_key)}'

    def col(self, a):
        i = self.attrs.index(a)
        return {r[i] for r in self.rows}

    def sorted_rows(self):
        return sorted(self.rows, key=_key)

    # ---- basic operators
    def sel(self, pred):
        """σ"""
        return R(self.attrs, [r for r in self.rows if pred(self._d(r))])

    def proj(self, *attrs):
        """π (duplicates removed automatically – set semantics)"""
        idx = [self.attrs.index(a) for a in attrs]
        return R(attrs, [tuple(r[i] for i in idx) for r in self.rows])

    def ren(self, mapping=None, prefix=None, names=None):
        """ρ – rename attributes: mapping {'old':'new'}, or prefix 'S1.' for all, or full new list"""
        if names:
            return R(names, self.rows)
        if prefix:
            return R([prefix + a for a in self.attrs], self.rows)
        return R([mapping.get(a, a) for a in self.attrs], self.rows)

    def _compat(self, o):
        if len(self.attrs) != len(o.attrs):
            raise ValueError('not union-compatible')

    def __or__(self, o):            # ∪
        self._compat(o)
        return R(self.attrs, self.rows | o.rows)

    def __sub__(self, o):           # −
        self._compat(o)
        return R(self.attrs, self.rows - o.rows)

    def __and__(self, o):           # ∩
        self._compat(o)
        return R(self.attrs, self.rows & o.rows)

    def x(self, o):                 # ×
        return R(self.attrs + o.attrs, [a + b for a, b in _prod(self.rows, o.rows)])

    def theta(self, o, pred):       # ⋈θ
        return self.x(o).sel(pred)

    def nat(self, o):               # ⋈ natural
        common = [a for a in self.attrs if a in o.attrs]
        oi = [o.attrs.index(a) for a in common]
        si = [self.attrs.index(a) for a in common]
        rest = [i for i, a in enumerate(o.attrs) if a not in common]
        out = []
        for a in self.rows:
            for b in o.rows:
                if all(a[i] == b[j] and a[i] is not None for i, j in zip(si, oi)):
                    out.append(a + tuple(b[k] for k in rest))
        return R(self.attrs + tuple(o.attrs[k] for k in rest), out)

    def _outer(self, o, left, right):
        common = [a for a in self.attrs if a in o.attrs]
        oi = [o.attrs.index(a) for a in common]
        si = [self.attrs.index(a) for a in common]
        rest = [i for i, a in enumerate(o.attrs) if a not in common]
        out, lm, rm = [], set(), set()
        for a in self.rows:
            for b in o.rows:
                if all(a[i] == b[j] and a[i] is not None for i, j in zip(si, oi)):
                    out.append(a + tuple(b[k] for k in rest))
                    lm.add(a)
                    rm.add(b)
        if left:
            for a in self.rows - lm:
                out.append(a + tuple(None for _ in rest))
        if right:
            for b in o.rows - rm:
                row = []
                for k, at in enumerate(self.attrs):
                    row.append(b[o.attrs.index(at)] if at in common else None)
                out.append(tuple(row) + tuple(b[k] for k in rest))
        return R(self.attrs + tuple(o.attrs[k] for k in rest), out)

    def ljoin(self, o):
        return self._outer(o, True, False)

    def rjoin(self, o):
        return self._outer(o, False, True)

    def fjoin(self, o):
        return self._outer(o, True, True)

    def semi(self, o):              # ⋉
        return self.nat(o).proj(*self.attrs)

    def anti(self, o):              # ▷
        return self - self.semi(o)

    def div(self, o):               # ÷
        keep = [a for a in self.attrs if a not in o.attrs]
        if not all(a in self.attrs for a in o.attrs):
            raise ValueError('divisor attributes must be a subset of dividend attributes')
        cand = self.proj(*keep)
        S = o.rows
        oi = [self.attrs.index(a) for a in o.attrs]
        ki = [self.attrs.index(a) for a in keep]
        have = {}
        for r in self.rows:
            have.setdefault(tuple(r[i] for i in ki), set()).add(tuple(r[i] for i in oi))
        return R(keep, [c for c in cand.rows if S <= have.get(c, set())])

    def div_by_formula(self, o):
        """R ÷ S = π_X(R) − π_X( (π_X(R) × S) − R )  – used to prove the formula gives the same answer"""
        keep = [a for a in self.attrs if a not in o.attrs]
        px = self.proj(*keep)
        allpairs = px.x(o).proj(*self.attrs)
        missing = allpairs - self.proj(*self.attrs)
        return px - missing.proj(*keep)

    def agg(self, group, aggs):
        """𝒢 : group = list of attrs, aggs = list of (func, attr, newname); func in count,sum,avg,min,max,count_distinct"""
        gi = [self.attrs.index(a) for a in group]
        groups = {}
        for r in self.rows:
            groups.setdefault(tuple(r[i] for i in gi), []).append(r)
        if not group and not groups:
            groups[()] = []
        out = []
        for g, rows in groups.items():
            vals = []
            for (fn, a, _) in aggs:
                col = [r[self.attrs.index(a)] for r in rows] if a != '*' else [1] * len(rows)
                col = [v for v in col if v is not None]
                if fn == 'count':
                    v = len(col)
                elif fn == 'count_distinct':
                    v = len(set(col))
                elif fn == 'sum':
                    v = sum(col) if col else None
                elif fn == 'avg':
                    v = round(sum(col) / len(col), 2) if col else None
                elif fn == 'min':
                    v = min(col) if col else None
                elif fn == 'max':
                    v = max(col) if col else None
                vals.append(v)
            out.append(g + tuple(vals))
        return R(list(group) + [n for (_, _, n) in aggs], out)

    def ext(self, newname, fn):
        """generalized projection helper: add a computed column"""
        return R(self.attrs + (newname,), [r + (fn(self._d(r)),) for r in self.rows])


def _key(r):
    return tuple((0, '') if v is None else ((1, v) if isinstance(v, (int, float)) else (2, str(v))) for v in r)


def from_sqlite(con, table):
    cur = con.execute(f'SELECT * FROM {table}')
    attrs = [d[0] for d in cur.description]
    return R(attrs, cur.fetchall())
