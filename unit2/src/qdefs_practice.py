"""Practice set (harder than the PYQs).  Each query is solved TWICE — in RA (engine) and in SQL (SQLite) — and the
two answers are asserted equal, so a mistake in either formulation breaks the build."""
import data
from qdefs import Q, A, V, RA, SQL, rels, check_rc

D = data.DB
D['fl'] = """
CREATE TABLE Flights(flno INT PRIMARY KEY, origin TEXT, destination TEXT, distance INT, departs TEXT);
CREATE TABLE Aircraft(aid INT PRIMARY KEY, aname TEXT, cruisingrange INT);
CREATE TABLE Employees(eid INT PRIMARY KEY, ename TEXT, salary INT);
CREATE TABLE Certified(eid INT REFERENCES Employees, aid INT REFERENCES Aircraft, PRIMARY KEY(eid, aid));
INSERT INTO Aircraft VALUES (1,'Boeing 747-400',8430),(2,'Boeing 737-800',3383),(3,'Airbus A340-300',7120),
 (4,'Jetstream 41',1502),(5,'Embraer ERJ-145',1530),(6,'SAAB 340',2128),(7,'Piper Archer III',520),(8,'Tupolev 154',4103),
 (9,'Boeing 757-300',3989),(10,'Airbus A320',2605);
INSERT INTO Employees VALUES (101,'Alice',260000),(102,'Bob',205000),(103,'Chen',190000),(104,'Dara',120000),(105,'Eli',95000),
 (106,'Fay',205000),(107,'Gus',40000),(108,'Hana',30000),(109,'Ivan',150000),(110,'Jia',70000);
INSERT INTO Certified VALUES (101,1),(101,2),(101,3),(101,9),(102,2),(102,4),(102,10),(103,3),(103,8),(103,6),
 (104,4),(104,5),(104,6),(104,7),(105,7),(106,1),(106,9),(109,3),(109,10),(109,6),(110,2);
INSERT INTO Flights VALUES (99,'Los Angeles','Washington D.C.',2308,'09:30'),(13,'Los Angeles','Chicago',1749,'08:45'),
 (346,'Los Angeles','Dallas',1251,'11:50'),(387,'Los Angeles','Boston',2606,'07:03'),(7,'Los Angeles','Sydney',7487,'22:30'),
 (2,'Los Angeles','Tokyo',5478,'12:30'),(33,'Los Angeles','Honolulu',2551,'09:15'),(1,'Los Angeles','New York',2475,'10:00'),
 (5,'New York','Chicago',740,'07:30'),(68,'Chicago','New York',802,'09:00');
"""


def both(qid, expr, fn, sql, run=None, expect=None, cap=None):
    r = A('ra_' + qid, 'fl', expr, fn, expect=expect, cap=cap)
    rows = Q('sql_' + qid, 'fl', sql, run=run, cap=cap)
    assert set(map(tuple, rows)) == set(r.rows), f'practice {qid}: RA {sorted(r.rows)} vs SQL {sorted(rows)}'
    return r


boeing = lambda D: D['Aircraft'].sel(lambda t: t.aname.startswith('Boeing'))
airbus = lambda D: D['Aircraft'].sel(lambda t: t.aname.startswith('Airbus'))

both('f1', r"\pi_{ename}(\sigma_{aname\ LIKE\ 'Boeing\%'}(Aircraft) \join Certified \join Employees)",
     lambda D: boeing(D).nat(D['Certified']).nat(D['Employees']).proj('ename'),
     """SELECT DISTINCT E.ename
FROM   Employees E
JOIN   Certified C ON C.eid = E.eid
JOIN   Aircraft  A ON A.aid = C.aid
WHERE  A.aname LIKE 'Boeing%';""", expect=[('Alice',), ('Bob',), ('Fay',), ('Jia',)])

both('f2', r"\pi_{aid}(Aircraft \join_{cruisingrange > distance} \sigma_{origin='Los Angeles' \and destination='New York'}(Flights))",
     lambda D: D['Aircraft'].theta(D['Flights'].sel(lambda t: t.origin == 'Los Angeles' and t.destination == 'New York'),
                                   lambda t: t.cruisingrange > t.distance).proj('aid'),
     """SELECT A.aid
FROM   Aircraft A
WHERE  A.cruisingrange > ALL (SELECT F.distance FROM Flights F
                              WHERE  F.origin = 'Los Angeles' AND F.destination = 'New York');""",
     run="""SELECT A.aid FROM Aircraft A WHERE A.cruisingrange > (SELECT MAX(F.distance) FROM Flights F
WHERE F.origin = 'Los Angeles' AND F.destination = 'New York')""",
     expect=[(1,), (2,), (3,), (8,), (9,), (10,)])

both('f3', r"Long \gets \pi_{eid}(\sigma_{cruisingrange > 3000}(Aircraft) \join Certified) \br BoeingPilots \gets \pi_{eid}(\sigma_{aname\ LIKE\ 'Boeing\%'}(Aircraft) \join Certified) \br \pi_{ename}((Long \minus BoeingPilots) \join Employees)",
     lambda D: (D['Aircraft'].sel(lambda t: t.cruisingrange > 3000).nat(D['Certified']).proj('eid')
                - boeing(D).nat(D['Certified']).proj('eid')).nat(D['Employees']).proj('ename'),
     """SELECT E.ename
FROM   Employees E
WHERE  EXISTS     (SELECT * FROM Certified C JOIN Aircraft A ON A.aid = C.aid
                   WHERE C.eid = E.eid AND A.cruisingrange > 3000)
AND    NOT EXISTS (SELECT * FROM Certified C JOIN Aircraft A ON A.aid = C.aid
                   WHERE C.eid = E.eid AND A.aname LIKE 'Boeing%');""", expect=[('Chen',), ('Ivan',)])


def _second(D):
    e1 = D['Employees'].ren(names=['eid1', 'n1', 's1'])
    e2 = D['Employees'].ren(names=['eid2', 'n2', 's2'])
    notmax = e1.theta(e2, lambda t: t.s1 < t.s2).proj('eid1').ren(names=['eid'])
    rest = (D['Employees'].proj('eid') - (D['Employees'].proj('eid') - notmax)).nat(D['Employees'])   # everyone except the top
    r1 = rest.ren(names=['eid1', 'n1', 's1'])
    r2 = rest.ren(names=['eid2', 'n2', 's2'])
    notmax2 = r1.theta(r2, lambda t: t.s1 < t.s2).proj('eid1').ren(names=['eid'])
    return rest.proj('eid') - notmax2


both('f4', r"Beaten \gets \pi_{E1.eid}(\rho_{E1}(Employees) \join_{E1.salary < E2.salary} \rho_{E2}(Employees)) \br Rest \gets Beaten \join Employees \quad (everyone except the top earner) \br Beaten2 \gets \pi_{R1.eid}(\rho_{R1}(Rest) \join_{R1.salary < R2.salary} \rho_{R2}(Rest)) \br Result \gets \pi_{eid}(Rest) \minus Beaten2",
     _second,
     """SELECT eid
FROM   Employees
WHERE  salary = (SELECT MAX(salary) FROM Employees
                 WHERE  salary < (SELECT MAX(salary) FROM Employees));""",
     expect=[(102,), (106,)])


def _cert_atleast(D, k):
    cs = [D['Certified'].ren(names=[f'e{i}', f'a{i}']) for i in range(k)]
    j = cs[0]
    for i in range(1, k):
        j = j.theta(cs[i], lambda t, i=i: t[f'e{i}'] == t['e0'] and t[f'a{i - 1}'] < t[f'a{i}'])
    return j.proj('e0').ren(names=['eid'])


both('f5', r"AtLeast3 \gets \pi_{C1.eid}(\rho_{C1}(Certified) \join_{C1.eid=C2.eid \and C1.aid<C2.aid} \rho_{C2}(Certified) \join_{C2.eid=C3.eid \and C2.aid<C3.aid} \rho_{C3}(Certified)) \br AtLeast4 \gets (same\ with\ four\ copies) \br Result \gets AtLeast3 \minus AtLeast4",
     lambda D: _cert_atleast(D, 3) - _cert_atleast(D, 4),
     """SELECT eid
FROM   Certified
GROUP  BY eid
HAVING COUNT(*) = 3;""", expect=[(102,), (103,), (109,)])

both('f6', r"\pi_{ename}((Certified \div \pi_{aid}(\sigma_{aname\ LIKE\ 'Airbus\%'}(Aircraft))) \join Employees)",
     lambda D: D['Certified'].div(airbus(D).proj('aid')).nat(D['Employees']).proj('ename'),
     """SELECT E.ename
FROM   Employees E
WHERE  E.eid IN (SELECT eid FROM Certified)
AND    NOT EXISTS (SELECT * FROM Aircraft A
                   WHERE  A.aname LIKE 'Airbus%'
                   AND    NOT EXISTS (SELECT * FROM Certified C
                                      WHERE C.eid = E.eid AND C.aid = A.aid));""", expect=[('Ivan',)])


def _f7(D):
    can = D['Certified'].nat(D['Aircraft']).theta(D['Flights'], lambda t: t.cruisingrange >= t.distance).proj('flno', 'eid')
    rich = D['Employees'].sel(lambda t: t.salary > 200000).proj('eid') & D['Certified'].proj('eid')
    return can.div(rich)


both('f7', r"Can \gets \pi_{flno, eid}((Certified \join Aircraft) \join_{cruisingrange \ge distance} Flights) \br Rich \gets \pi_{eid}(\sigma_{salary > 200000}(Employees)) \cap \pi_{eid}(Certified) \br Result \gets Can \div Rich",
     _f7,
     """SELECT F.flno
FROM   Flights F
WHERE  NOT EXISTS (                         -- no rich pilot ...
         SELECT * FROM Employees E
         WHERE  E.salary > 200000
         AND    E.eid IN (SELECT eid FROM Certified)
         AND    NOT EXISTS (                -- ... who cannot fly F
                  SELECT * FROM Certified C JOIN Aircraft A ON A.aid = C.aid
                  WHERE  C.eid = E.eid AND A.cruisingrange >= F.distance));""",
     expect=[(99,), (13,), (346,), (387,), (33,), (1,), (5,), (68,)])

Q('f8', 'fl', """SELECT A.aname, ROUND(AVG(E.salary)) AS avg_pilot_salary
FROM   Aircraft A
JOIN   Certified C ON C.aid = A.aid
JOIN   Employees E ON E.eid = C.eid
WHERE  A.cruisingrange > 1000
GROUP  BY A.aid, A.aname;""")
Q('f9', 'fl', """SELECT E.ename, E.salary,
       E.salary - (SELECT AVG(salary) FROM Employees
                   WHERE eid IN (SELECT eid FROM Certified)) AS above_pilot_avg
FROM   Employees E
WHERE  E.eid IN (SELECT eid FROM Certified)
AND    E.salary > (SELECT AVG(salary) FROM Employees
                   WHERE eid IN (SELECT eid FROM Certified));""",
  expect=[('Alice', 260000, 98125.0), ('Bob', 205000, 43125.0), ('Chen', 190000, 28125.0), ('Fay', 205000, 43125.0)])
Q('f10', 'fl', """SELECT C.eid, MAX(A.cruisingrange) AS max_range
FROM   Certified C JOIN Aircraft A ON A.aid = C.aid
GROUP  BY C.eid
HAVING COUNT(*) > 3;""", expect=[(101, 8430), (104, 2128)])
Q('f11', 'fl', """SELECT (SELECT AVG(salary) FROM Employees WHERE eid IN (SELECT eid FROM Certified))
     - (SELECT AVG(salary) FROM Employees) AS pilot_minus_all;""", expect=[(25375.0,)])
Q('f12', 'fl', """SELECT E.ename
FROM   Employees E
WHERE  E.eid IN (SELECT eid FROM Certified)
AND    NOT EXISTS (SELECT * FROM Certified C JOIN Aircraft A ON A.aid = C.aid
                   WHERE  C.eid = E.eid AND A.cruisingrange <= 2000)   -- every plane > 2000 ...
AND    (SELECT COUNT(*) FROM Certified C WHERE C.eid = E.eid) >= 2;     -- ... and at least two of them""",
  expect=[('Alice',), ('Chen',), ('Fay',), ('Ivan',)])
Q('f13', 'fl', """SELECT DISTINCT F.origin, F.destination
FROM   Flights F
WHERE  NOT EXISTS (SELECT * FROM Certified C JOIN Aircraft A ON A.aid = C.aid
                   WHERE  C.eid = 102 AND A.cruisingrange >= F.distance);""",
  expect=[('Los Angeles', 'Sydney'), ('Los Angeles', 'Tokyo')])
Q('f14', 'fl', """SELECT ename, salary
FROM   Employees e1
WHERE  3 > (SELECT COUNT(DISTINCT e2.salary) FROM Employees e2 WHERE e2.salary > e1.salary)
ORDER  BY salary DESC;""", sort=False,
  expect=[('Alice', 260000), ('Bob', 205000), ('Fay', 205000), ('Chen', 190000)])

# ---- calculus practice, checked against RA
_D = rels('fl')
E_ = [_D['Employees']._d(r) for r in _D['Employees'].rows]
C_ = [_D['Certified']._d(r) for r in _D['Certified'].rows]
A_ = [_D['Aircraft']._d(r) for r in _D['Aircraft'].rows]
check_rc('pr-airbus', {(e.ename,) for e in E_ if any(c.eid == e.eid for c in C_) and
                       all((not a.aname.startswith('Airbus')) or any(c.eid == e.eid and c.aid == a.aid for c in C_) for a in A_)},
         RA['ra_f6']['res'])
A('pr_only', 'fl', r"\pi_{ename}((\pi_{eid}(Certified) \minus \pi_{eid}(\sigma_{cruisingrange \le 2000}(Aircraft) \join Certified)) \join Employees)",
  lambda D: (D['Certified'].proj('eid') - D['Aircraft'].sel(lambda t: t.cruisingrange <= 2000).nat(D['Certified']).proj('eid'))
  .nat(D['Employees']).proj('ename'))
check_rc('pr-only', {(e.ename,) for e in E_ if any(c.eid == e.eid for c in C_) and
                     all(c.eid != e.eid or any(a.aid == c.aid and a.cruisingrange > 2000 for a in A_) for c in C_)},
         RA['pr_only']['res'])

# ---- tuple-count practice
D['cnt'] = """
CREATE TABLE R(A INT, B INT);
CREATE TABLE S(B INT, C INT);
INSERT INTO R VALUES (1,10),(2,10),(3,20),(4,30),(5,NULL);
INSERT INTO S VALUES (10,'x'),(10,'y'),(20,'z'),(40,'w');
"""
A('cnt_nat', 'cnt', r"R \join S", lambda D: D['R'].nat(D['S']))
A('cnt_l', 'cnt', r"R \ljoin S", lambda D: D['R'].ljoin(D['S']))
A('cnt_f', 'cnt', r"R \fjoin S", lambda D: D['R'].fjoin(D['S']))
A('cnt_semi', 'cnt', r"R \semi S", lambda D: D['R'].semi(D['S']))
A('cnt_pb', 'cnt', r"\pi_{B}(R) \minus \pi_{B}(S)", lambda D: D['R'].proj('B') - D['S'].proj('B'))
assert len(RA['cnt_nat']['res']) == 5 and len(RA['cnt_l']['res']) == 7 and len(RA['cnt_f']['res']) == 8

# ---- cascade / set null practice
V('pr_casc', """CREATE TABLE dept(dno INT PRIMARY KEY, dname TEXT);
CREATE TABLE emp(eno INT PRIMARY KEY, dno INT REFERENCES dept ON DELETE CASCADE, mgr INT REFERENCES emp ON DELETE SET NULL);
CREATE TABLE dependent(eno INT REFERENCES emp ON DELETE CASCADE, dname TEXT);
INSERT INTO dept VALUES (1,'R&D'),(2,'Ops');
INSERT INTO emp VALUES (10,1,NULL),(11,1,10),(12,2,10),(13,2,12),(14,1,11);
INSERT INTO dependent VALUES (10,'Ria'),(11,'Om'),(13,'Tia'),(14,'Avi');""",
  [("DELETE FROM dept WHERE dno = 1;", 'ok', 'cascades to emp 10, 11, 14; then to their dependents; emp 12’s mgr (10) becomes NULL')],
  after="SELECT 'emp' AS tbl, eno, dno, mgr FROM emp UNION ALL SELECT 'dependent', eno, NULL, dname FROM dependent")

# ---- trigger practice (stock)
Q('pr_trg', 'fl', """CREATE TABLE product(pid INT PRIMARY KEY, pname TEXT, stock INT CHECK (stock >= 0));
CREATE TABLE order_item(oid INT, pid INT REFERENCES product, qty INT);
CREATE TRIGGER trg_check_stock BEFORE INSERT ON order_item
FOR EACH ROW WHEN NEW.qty > (SELECT stock FROM product WHERE pid = NEW.pid)
BEGIN
  SELECT RAISE(ABORT, 'insufficient stock');
END;
CREATE TRIGGER trg_reduce_stock AFTER INSERT ON order_item
FOR EACH ROW
BEGIN
  UPDATE product SET stock = stock - NEW.qty WHERE pid = NEW.pid;
END;
INSERT INTO product VALUES (1,'Pen',100),(2,'Ink',5);
INSERT INTO order_item VALUES (501,1,30);
INSERT INTO order_item VALUES (502,2,5);
INSERT INTO order_item VALUES (503,1,20);""", after="SELECT * FROM product", fresh=True,
  expect=[(1, 'Pen', 50), (2, 'Ink', 0)])
import sqlite3 as _s  # noqa: E402
_c = data.conn('fl', fresh=True)
_c.executescript(SQL['pr_trg']['sql'])
try:
    _c.execute("INSERT INTO order_item VALUES (504,2,1)")
    raise AssertionError('trigger should reject')
except _s.IntegrityError:
    pass
