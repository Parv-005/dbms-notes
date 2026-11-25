"""Registry of every RA expression and SQL query shown in the notes.

RA entries are *computed* with the engine in ra.py on the sample databases; SQL entries are *executed* by SQLite.
`expect=` pins the answer, so a wrong query breaks the build instead of silently printing a wrong table.
Relational-calculus formulas are checked by evaluating a literal Python transcription (any/all) and
comparing with the RA answer (see check_rc).
"""
import data
from ra import R, from_sqlite

RA, SQL = {}, {}
_rel_cache = {}


def rels(db):
    if db not in _rel_cache:
        c = data.conn(db)
        names = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        _rel_cache[db] = {n: from_sqlite(c, n) for n in names}
    return _rel_cache[db]


def A(qid, db, expr, fn, expect=None, cap=None):
    D = rels(db)
    res = fn(D)
    if expect is not None:
        got = sorted(map(tuple, res.rows), key=str)
        exp = sorted(map(tuple, expect), key=str)
        assert got == exp, f'RA {qid}: got {got} expected {exp}'
    RA[qid] = dict(expr=expr, res=res, cap=cap)
    return res


def Q(qid, db, sql, run=None, expect=None, cap=None, setup=None, after=None, sort=False, fresh=False):
    """run = SQLite variant if display SQL uses another dialect; setup = statements before; after = query to show."""
    con = data.conn(db, fresh=bool(fresh or setup or after))
    if setup:
        con.executescript(setup)
    cur = con.execute(run or sql) if not after else None
    if after:
        con.executescript(run or sql)
        cur = con.execute(after)
    attrs = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    if expect is not None:
        got = sorted(map(tuple, rows), key=str)
        exp = sorted(map(tuple, expect), key=str)
        assert got == exp, f'SQL {qid}: got {got} expected {exp}'
    SQL[qid] = dict(sql=sql, res=(attrs, rows), cap=cap, sort=sort)
    return rows


VIOL = {}


def V(vid, setup, stmts, after=None):
    """Run each (stmt, expected 'ok'|'err', explanation) on a fresh DB; assert the DBMS really accepts/rejects it."""
    import sqlite3
    con = sqlite3.connect(':memory:')
    con.execute('PRAGMA foreign_keys = ON')
    import re as _re
    # standard SQL: a PRIMARY KEY column is implicitly NOT NULL (SQLite only does this for INTEGER PRIMARY KEY)
    con.executescript(_re.sub(r'(?<!NOT NULL) PRIMARY KEY(?!\s*\()', ' NOT NULL PRIMARY KEY', setup))
    rows = []
    for st, exp, why in stmts:
        try:
            con.executescript(st)
            got = 'ok'
        except sqlite3.Error as e:
            got = 'err'
        assert got == exp, f'VIOL {vid}: {st!r} expected {exp} got {got}'
        rows.append((st, got, why))
    res = None
    if after:
        cur = con.execute(after)
        res = ([d[0] for d in cur.description], cur.fetchall())
    VIOL[vid] = dict(setup=setup, rows=rows, after=res)


def check_rc(name, rc_rows, ra_res):
    got = set(map(tuple, rc_rows))
    exp = set(ra_res.rows)
    assert got == exp, f'RC check {name}: calculus gives {sorted(got)} but RA gives {sorted(exp)}'


# =================================================================== 3. RELATIONAL ALGEBRA (teaching DB "sb")
red = lambda D: D['Boats'].sel(lambda t: t.color == 'red')
green = lambda D: D['Boats'].sel(lambda t: t.color == 'green')

A('sel1', 'sb', r"\sigma_{rating > 7}(Sailors)", lambda D: D['Sailors'].sel(lambda t: t.rating > 7),
  expect=[(31, 'Lubber', 8, 55.5), (32, 'Andy', 8, 25.5), (58, 'Rusty', 10, 35.0), (71, 'Zorba', 10, 16.0), (74, 'Horatio', 9, 35.0)])
A('sel2', 'sb', r"\sigma_{rating > 7 \and age < 40}(Sailors)",
  lambda D: D['Sailors'].sel(lambda t: t.rating > 7 and t.age < 40))
A('sel3', 'sb', r"\sigma_{color = 'red' \or color = 'green'}(Boats)",
  lambda D: D['Boats'].sel(lambda t: t.color in ('red', 'green')))
A('proj1', 'sb', r"\pi_{sname, rating}(Sailors)", lambda D: D['Sailors'].proj('sname', 'rating'))
A('proj2', 'sb', r"\pi_{age}(Sailors)", lambda D: D['Sailors'].proj('age'),
  cap='Result: only 7 tuples — the 10 sailors have only 7 distinct ages (duplicates removed)')
A('proj3', 'sb', r"\pi_{sname}(Sailors)", lambda D: D['Sailors'].proj('sname'),
  cap='Result: 9 tuples — “Horatio” appears once although two sailors have that name')
A('selproj', 'sb', r"\pi_{sname, rating}(\sigma_{rating > 7}(Sailors))",
  lambda D: D['Sailors'].sel(lambda t: t.rating > 7).proj('sname', 'rating'))

# ---- set operations on tiny R, S
A('union', 'rs', r"R \cup S", lambda D: D['R'] | D['S'])
A('inter', 'rs', r"R \cap S", lambda D: D['R'] & D['S'])
A('diff1', 'rs', r"R \minus S", lambda D: D['R'] - D['S'])
A('diff2', 'rs', r"S \minus R", lambda D: D['S'] - D['R'])

# ---- product and joins on Emp / Dept
def _empq(D):
    return D['Emp'].ren(names=['eno', 'ename', 'Emp.dno'])


def _deptq(D):
    return D['Dept'].ren(names=['Dept.dno', 'dname'])


A('prod', 'rs', r"Emp \x Dept", lambda D: _empq(D).x(_deptq(D)),
  cap='Result: 4 × 3 = 12 tuples, degree 3 + 2 = 5 (most rows are meaningless pairs)')
A('theta', 'rs', r"Emp \join_{Emp.dno = Dept.dno} Dept",
  lambda D: _empq(D).theta(_deptq(D), lambda t: t['Emp.dno'] == t['Dept.dno']),
  cap='Result: 3 tuples (equi-join keeps BOTH dno columns; Dev has dno = NULL so matches nothing)')
A('natjoin', 'rs', r"Emp \join Dept", lambda D: D['Emp'].nat(D['Dept']),
  cap='Result: 3 tuples — common attribute dno appears only once')
A('ljoin', 'rs', r"Emp \ljoin Dept", lambda D: D['Emp'].ljoin(D['Dept']),
  cap='Left outer join: every Emp tuple survives; Dev is padded with NULL')
A('rjoin', 'rs', r"Emp \rjoin Dept", lambda D: D['Emp'].rjoin(D['Dept']),
  cap='Right outer join: every Dept tuple survives; HR (no employee) is padded with NULLs')
A('fjoin', 'rs', r"Emp \fjoin Dept", lambda D: D['Emp'].fjoin(D['Dept']),
  cap='Full outer join = left ∪ right: unmatched tuples of BOTH sides survive')
A('semij', 'sb', r"Sailors \semi Reserves", lambda D: D['Sailors'].semi(D['Reserves']),
  cap='Semi-join: sailors that have at least one matching Reserves tuple (only Sailors’ columns)')
A('antij', 'sb', r"Sailors \anti Reserves", lambda D: D['Sailors'].anti(D['Reserves']),
  cap='Anti-join: sailors with NO matching Reserves tuple')

# ---- division (Enrolled / Course)
A('div1', 'rs', r"Enrolled \div Course", lambda D: D['Enrolled'].div(D['Course']),
  expect=[('S1',), ('S4',)])
A('divT1', 'rs', r"T1 \gets \pi_{sid}(Enrolled)", lambda D: D['Enrolled'].proj('sid'), cap='T1: every candidate sid')
A('divT2', 'rs', r"T2 \gets T1 \x Course", lambda D: D['Enrolled'].proj('sid').x(D['Course']),
  cap='T2: every pair (sid, cid) that WOULD exist if each student took every course')
A('divT3', 'rs', r"T3 \gets T2 \minus Enrolled",
  lambda D: D['Enrolled'].proj('sid').x(D['Course']) - D['Enrolled'],
  cap='T3: the “missing” pairs — a required course this student has NOT taken')
A('divT4', 'rs', r"T4 \gets \pi_{sid}(T3)",
  lambda D: (D['Enrolled'].proj('sid').x(D['Course']) - D['Enrolled']).proj('sid'),
  cap='T4: disqualified students (they miss at least one course)')
A('divT5', 'rs', r"Result \gets T1 \minus T4", lambda D: D['Enrolled'].div_by_formula(D['Course']),
  expect=[('S1',), ('S4',)], cap='Result = T1 − T4 = S1, S4 — same as Enrolled ÷ Course')

# ---- cookbook on Sailors
names = lambda D, sids: sids.nat(D['Sailors']).proj('sname')
A('c1', 'sb', r"\pi_{sname}(\sigma_{bid = 103}(Reserves) \join Sailors)",
  lambda D: D['Reserves'].sel(lambda t: t.bid == 103).nat(D['Sailors']).proj('sname'),
  expect=[('Dustin',), ('Lubber',), ('Horatio',)])
A('c1b', 'sb', r"\pi_{sname}(\sigma_{bid = 103}(Reserves \join Sailors))",
  lambda D: D['Reserves'].nat(D['Sailors']).sel(lambda t: t.bid == 103).proj('sname'))
A('c2', 'sb', r"\pi_{sname}(\sigma_{color = 'red'}(Boats) \join Reserves \join Sailors)",
  lambda D: red(D).nat(D['Reserves']).nat(D['Sailors']).proj('sname'),
  expect=[('Dustin',), ('Lubber',), ('Horatio',), ('Andy',), ('Rusty',)])
A('c3', 'sb', r"\pi_{color}(\sigma_{sname = 'Lubber'}(Sailors) \join Reserves \join Boats)",
  lambda D: D['Sailors'].sel(lambda t: t.sname == 'Lubber').nat(D['Reserves']).nat(D['Boats']).proj('color'),
  expect=[('red',), ('green',)])
A('c4', 'sb', r"\pi_{sname}(Sailors \join Reserves)",
  lambda D: D['Sailors'].nat(D['Reserves']).proj('sname'))
A('c5', 'sb', r"\pi_{sname}(\sigma_{color = 'red' \or color = 'green'}(Boats) \join Reserves \join Sailors)",
  lambda D: D['Boats'].sel(lambda t: t.color in ('red', 'green')).nat(D['Reserves']).nat(D['Sailors']).proj('sname'))
_redsid = lambda D: red(D).nat(D['Reserves']).proj('sid')
_greensid = lambda D: green(D).nat(D['Reserves']).proj('sid')
A('c6', 'sb', r"\pi_{sname}((\pi_{sid}(\sigma_{color='red'}(Boats) \join Reserves) \cap \pi_{sid}(\sigma_{color='green'}(Boats) \join Reserves)) \join Sailors)",
  lambda D: (_redsid(D) & _greensid(D)).nat(D['Sailors']).proj('sname'),
  expect=[('Dustin',), ('Lubber',)])
A('c6wrong', 'sb', r"\pi_{sname}(\sigma_{color='red'}(Boats) \join Reserves \join Sailors) \cap \pi_{sname}(\sigma_{color='green'}(Boats) \join Reserves \join Sailors)",
  lambda D: red(D).nat(D['Reserves']).nat(D['Sailors']).proj('sname') & green(D).nat(D['Reserves']).nat(D['Sailors']).proj('sname'),
  cap='WRONG result: Horatio appears — but sailor 64 Horatio reserved only red/blue and sailor 74 Horatio only green')
A('c6empty', 'sb', r"\pi_{sname}(\sigma_{color='red' \and color='green'}(Boats) \join Reserves \join Sailors)",
  lambda D: D['Boats'].sel(lambda t: t.color == 'red' and t.color == 'green').nat(D['Reserves']).nat(D['Sailors']).proj('sname'),
  cap='WRONG: a single boat can never be both red and green → always empty')


def _two(D):
    r1 = D['Reserves'].ren(names=['sid1', 'bid1', 'day1'])
    r2 = D['Reserves'].ren(names=['sid2', 'bid2', 'day2'])
    return r1.theta(r2, lambda t: t.sid1 == t.sid2 and t.bid1 != t.bid2).proj('sid1').ren(names=['sid'])


A('c7', 'sb', r"\pi_{R1.sid}(\rho_{R1}(Reserves) \join_{R1.sid = R2.sid \and R1.bid \ne R2.bid} \rho_{R2}(Reserves))",
  _two, expect=[(22,), (31,), (64,)], cap='sids that reserved at least two different boats')
A('c7n', 'sb', r"\pi_{sid, sname}(TwoPlus \join Sailors)", lambda D: _two(D).nat(D['Sailors']).proj('sid', 'sname'))
A('c8', 'sb', r"\pi_{sname}((\pi_{sid}(Sailors) \minus \pi_{sid}(\sigma_{color='red'}(Boats) \join Reserves)) \join Sailors)",
  lambda D: (D['Sailors'].proj('sid') - _redsid(D)).nat(D['Sailors']).proj('sname'),
  expect=[('Brutus',), ('Zorba',), ('Horatio',), ('Art',), ('Bob',)])
A('c8wrong', 'sb', r"\pi_{sname}(Sailors) \minus \pi_{sname}(\sigma_{color='red'}(Boats) \join Reserves \join Sailors)",
  lambda D: D['Sailors'].proj('sname') - red(D).nat(D['Reserves']).nat(D['Sailors']).proj('sname'),
  cap='WRONG: sailor 74 Horatio (who never reserved a red boat) is lost because the OTHER Horatio did')
A('c9', 'sb', r"\pi_{sid}(Reserves) \minus \pi_{sid}(\sigma_{color \ne 'red'}(Boats) \join Reserves)",
  lambda D: D['Reserves'].proj('sid') - D['Boats'].sel(lambda t: t.color != 'red').nat(D['Reserves']).proj('sid'),
  expect=[(32,), (58,)], cap='sids that reserved ONLY red boats (and at least one boat)')
A('c10', 'sb', r"\pi_{sname}((\pi_{sid, bid}(Reserves) \div \pi_{bid}(Boats)) \join Sailors)",
  lambda D: D['Reserves'].proj('sid', 'bid').div(D['Boats'].proj('bid')).nat(D['Sailors']).proj('sname'),
  expect=[('Dustin',)])
A('c10wrong', 'sb', r"Reserves \div \pi_{bid}(Boats)",
  lambda D: D['Reserves'].div(D['Boats'].proj('bid')),
  cap='WRONG: forgot to project away “day” — now it asks for a (sid, day) pair that covers all boats → empty')
A('c11', 'sb', r"\pi_{sname}((\pi_{sid, bid}(Reserves) \div \pi_{bid}(\sigma_{color='red'}(Boats))) \join Sailors)",
  lambda D: D['Reserves'].proj('sid', 'bid').div(red(D).proj('bid')).nat(D['Sailors']).proj('sname'),
  expect=[('Dustin',), ('Lubber',)])


def _oldest(D):
    s1 = D['Sailors'].ren(names=['sid1', 'sname1', 'rating1', 'age1'])
    s2 = D['Sailors'].ren(names=['sid2', 'sname2', 'rating2', 'age2'])
    notmax = s1.theta(s2, lambda t: t.age1 < t.age2).proj('sid1').ren(names=['sid'])
    return (D['Sailors'].proj('sid') - notmax).nat(D['Sailors']).proj('sname', 'age')


A('c12', 'sb', r"\pi_{sname, age}((\pi_{sid}(Sailors) \minus \pi_{S1.sid}(\rho_{S1}(Sailors) \join_{S1.age < S2.age} \rho_{S2}(Sailors))) \join Sailors)",
  _oldest, expect=[('Bob', 63.5)])


def _toprating(D):
    s1 = D['Sailors'].ren(names=['sid1', 'sname1', 'rating1', 'age1'])
    s2 = D['Sailors'].ren(names=['sid2', 'sname2', 'rating2', 'age2'])
    notmax = s1.theta(s2, lambda t: t.rating1 < t.rating2).proj('sid1').ren(names=['sid'])
    return (D['Sailors'].proj('sid') - notmax).nat(D['Sailors']).proj('sname', 'age')


A('c13', 'sb', r"\pi_{sname, age}((\pi_{sid}(Sailors) \minus \pi_{S1.sid}(\rho_{S1}(Sailors) \join_{S1.rating < S2.rating} \rho_{S2}(Sailors))) \join Sailors)",
  _toprating, expect=[('Rusty', 35.0), ('Zorba', 16.0)])
A('c14', 'sb', r"\pi_{sid}(Reserves) \minus TwoPlus",
  lambda D: D['Reserves'].proj('sid') - _two(D), expect=[(74,), (32,), (58,)],
  cap='sids that reserved exactly one boat (at least one − at least two)')
A('c15', 'sb', r"_{sid}\gamma_{count(bid) \to n}(Reserves)",
  lambda D: D['Reserves'].proj('sid', 'bid').agg(['sid'], [('count', 'bid', 'n')]))
A('c16', 'sb', r"_{rating}\gamma_{avg(age) \to avg\_age, count(sid) \to n}(Sailors)",
  lambda D: D['Sailors'].agg(['rating'], [('avg', 'age', 'avg_age'), ('count', 'sid', 'n')]))
A('c17', 'sb', r"\gamma_{max(age) \to oldest}(Sailors)", lambda D: D['Sailors'].agg([], [('max', 'age', 'oldest')]))
A('c18', 'sb', r"\sigma_{n > 2}(_{sid}\gamma_{count(bid) \to n}(Reserves))",
  lambda D: D['Reserves'].proj('sid', 'bid').agg(['sid'], [('count', 'bid', 'n')]).sel(lambda t: t.n > 2),
  expect=[(22, 4), (31, 3)], cap='sailors with more than two reservations (γ first, then σ on the aggregate)')
A('gp', 'sb', r"\pi_{sname, rating \times 10 \to score}(\sigma_{rating \ge 9}(Sailors))",
  lambda D: D['Sailors'].sel(lambda t: t.rating >= 9).ext('score', lambda t: t.rating * 10).proj('sname', 'score'))
A('semi_eq', 'sb', r"\pi_{sid,sname,rating,age}(Sailors \join Reserves)",
  lambda D: D['Sailors'].nat(D['Reserves']).proj('sid', 'sname', 'rating', 'age'))

# ---- relational calculus checks (literal transcriptions of the TRC/DRC formulas in section 4)
_D = rels('sb')
S_, B_, Rv_ = _D['Sailors'], _D['Boats'], _D['Reserves']
Srows = [S_._d(r) for r in S_.rows]
Brows = [B_._d(r) for r in B_.rows]
Rrows = [Rv_._d(r) for r in Rv_.rows]
# {t | ∃s∈Sailors (s.rating>7 ∧ t.sname=s.sname)}  -> projection of names
check_rc('trc-sel', [(s.sname, s.rating) for s in Srows if s.rating > 7], RA['selproj']['res'])
# names of sailors who reserved boat 103
check_rc('trc-103', {(s.sname,) for s in Srows if any(r.sid == s.sid and r.bid == 103 for r in Rrows)}, RA['c1']['res'])
# red boat:  ∃s∈Sailors ∃r∈Reserves ∃b∈Boats (...)
check_rc('trc-red', {(s.sname,) for s in Srows for r in Rrows for b in Brows
                     if r.sid == s.sid and r.bid == b.bid and b.color == 'red'}, RA['c2']['res'])
# both red and green (two different boat variables!)
check_rc('trc-both', {(s.sname,) for s in Srows
                      if any(r1.sid == s.sid and b1.bid == r1.bid and b1.color == 'red' for r1 in Rrows for b1 in Brows)
                      and any(r2.sid == s.sid and b2.bid == r2.bid and b2.color == 'green' for r2 in Rrows for b2 in Brows)},
         RA['c6']['res'])
# all boats: ∀b∈Boats ∃r∈Reserves (r.sid = s.sid ∧ r.bid = b.bid)
check_rc('trc-all', {(s.sname,) for s in Srows if all(any(r.sid == s.sid and r.bid == b.bid for r in Rrows) for b in Brows)},
         RA['c10']['res'])
# all red boats: ∀b∈Boats (b.color='red' ⇒ ∃r∈Reserves(...))
check_rc('trc-allred', {(s.sname,) for s in Srows
                        if all((b.color != 'red') or any(r.sid == s.sid and r.bid == b.bid for r in Rrows) for b in Brows)},
         RA['c11']['res'])
# not reserved a red boat: ¬∃r∈Reserves ∃b∈Boats(...)
check_rc('trc-notred', {(s.sname,) for s in Srows
                        if not any(r.sid == s.sid and r.bid == b.bid and b.color == 'red' for r in Rrows for b in Brows)},
         RA['c8']['res'])
# oldest: ¬∃s2 (s2.age > s.age)
check_rc('trc-oldest', {(s.sname, s.age) for s in Srows if not any(s2.age > s.age for s2 in Srows)}, RA['c12']['res'])
# at least two boats
check_rc('trc-two', {(s.sid, s.sname) for s in Srows
                     if any(r1.sid == s.sid and r2.sid == s.sid and r1.bid != r2.bid for r1 in Rrows for r2 in Rrows)},
         RA['c7n']['res'])
# only red boats: ∃r(r.sid=s.sid) ∧ ∀r(r.sid=s.sid ⇒ ∃b(b.bid=r.bid ∧ b.color='red'))
check_rc('trc-onlyred', {(s.sid,) for s in Srows if any(r.sid == s.sid for r in Rrows)
                         and all(r.sid != s.sid or any(b.bid == r.bid and b.color == 'red' for b in Brows) for r in Rrows)},
         RA['c9']['res'])

import qdefs_sql  # noqa: E402,F401  (SQL teaching queries)
import qdefs_pyq  # noqa: E402,F401  (PYQ answers + practice, all verified)
import qdefs_practice  # noqa: E402,F401
