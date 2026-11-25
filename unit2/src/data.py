"""Sample databases (SQLite).  conn(name) returns a fresh-loaded, cached connection.

Every RA example is computed on these same tables (via ra.from_sqlite), and every SQL answer is executed on them,
so the result tables printed in the notes are real outputs, not hand-typed ones.
"""
import sqlite3

DISPLAY = {}

DB = {}

# ---------------------------------------------------------------- 1. Sailors – Boats – Reserves (RA / RC teaching DB)
DB['sb'] = """
CREATE TABLE Sailors(sid INTEGER PRIMARY KEY, sname TEXT, rating INTEGER, age REAL);
CREATE TABLE Boats(bid INTEGER PRIMARY KEY, bname TEXT, color TEXT);
CREATE TABLE Reserves(sid INTEGER REFERENCES Sailors, bid INTEGER REFERENCES Boats, day TEXT, PRIMARY KEY(sid,bid,day));
INSERT INTO Sailors VALUES (22,'Dustin',7,45.0),(29,'Brutus',1,33.0),(31,'Lubber',8,55.5),(32,'Andy',8,25.5),
 (58,'Rusty',10,35.0),(64,'Horatio',7,35.0),(71,'Zorba',10,16.0),(74,'Horatio',9,35.0),(85,'Art',3,25.5),(95,'Bob',3,63.5);
INSERT INTO Boats VALUES (101,'Interlake','blue'),(102,'Interlake','red'),(103,'Clipper','green'),(104,'Marine','red');
INSERT INTO Reserves VALUES (22,101,'2024-10-10'),(22,102,'2024-10-10'),(22,103,'2024-10-08'),(22,104,'2024-10-07'),
 (31,102,'2024-11-10'),(31,103,'2024-11-06'),(31,104,'2024-11-12'),(64,101,'2024-09-05'),(64,102,'2024-09-08'),
 (74,103,'2024-09-08'),(32,104,'2024-09-12'),(58,102,'2024-10-15');
"""

# ---------------------------------------------------------------- 2. tiny R / S for operator demos
DB['rs'] = """
CREATE TABLE R(A TEXT, B INTEGER);
CREATE TABLE S(A TEXT, B INTEGER);
INSERT INTO R VALUES ('a1',1),('a2',2),('a3',3);
INSERT INTO S VALUES ('a2',2),('a3',3),('a4',4);
CREATE TABLE Emp(eno INTEGER, ename TEXT, dno INTEGER);
CREATE TABLE Dept(dno INTEGER, dname TEXT);
INSERT INTO Emp VALUES (1,'Aman',10),(2,'Bela',20),(3,'Chirag',10),(4,'Dev',NULL);
INSERT INTO Dept VALUES (10,'Sales'),(20,'IT'),(30,'HR');
CREATE TABLE Enrolled(sid TEXT, cid TEXT);
CREATE TABLE Course(cid TEXT);
INSERT INTO Enrolled VALUES ('S1','C1'),('S1','C2'),('S1','C3'),('S2','C1'),('S2','C3'),('S3','C2'),('S4','C1'),('S4','C2');
INSERT INTO Course VALUES ('C1'),('C2');
CREATE TABLE A1(x INTEGER, y INTEGER);
INSERT INTO A1 VALUES (1,2),(2,3),(3,4);
CREATE TABLE A2(y INTEGER, z INTEGER);
INSERT INTO A2 VALUES (2,5),(4,6),(7,8);
"""

# ---------------------------------------------------------------- 3. Company DB (SQL teaching)
DB['co'] = """
CREATE TABLE department(dept_id INTEGER PRIMARY KEY, dept_name TEXT NOT NULL UNIQUE, location TEXT);
CREATE TABLE employee(emp_id INTEGER PRIMARY KEY, name TEXT NOT NULL, dept_id INTEGER REFERENCES department(dept_id),
  salary INTEGER CHECK (salary > 0), manager_id INTEGER REFERENCES employee(emp_id), city TEXT, hire_date TEXT);
CREATE TABLE project(proj_id TEXT PRIMARY KEY, pname TEXT, dept_id INTEGER REFERENCES department(dept_id), budget INTEGER);
CREATE TABLE works_on(emp_id INTEGER REFERENCES employee(emp_id), proj_id TEXT REFERENCES project(proj_id), hours INTEGER,
  PRIMARY KEY(emp_id, proj_id));
INSERT INTO department VALUES (10,'Sales','Delhi'),(20,'IT','Bengaluru'),(30,'HR','Mumbai'),(40,'Research','Hyderabad');
INSERT INTO employee VALUES
 (1,'Aarav',20,95000,NULL,'Delhi','2018-04-12'),
 (2,'Diya',20,72000,1,'Bengaluru','2020-07-01'),
 (3,'Kabir',20,72000,1,'Delhi','2021-02-15'),
 (4,'Meera',10,64000,1,'Mumbai','2019-09-23'),
 (5,'Rohan',10,48000,4,'Delhi','2022-01-10'),
 (6,'Sara',10,51000,4,'Pune','2023-03-05'),
 (7,'Ishaan',30,45000,1,'Mumbai','2021-11-30'),
 (8,'Zoya',NULL,39000,4,'Delhi','2024-06-17'),
 (9,'Neel',20,NULL,2,'Bengaluru','2024-08-01');
INSERT INTO project VALUES ('P1','Website',20,500000),('P2','Mobile App',20,800000),('P3','Campaign',10,200000),
 ('P4','Hiring Drive',30,100000),('P5','AI Lab',40,900000);
INSERT INTO works_on VALUES (2,'P1',120),(3,'P1',80),(3,'P2',150),(1,'P2',40),(2,'P2',60),(4,'P3',90),(5,'P3',60),
 (6,'P3',30),(7,'P4',100);
"""

_cache = {}


def conn(name, fresh=False):
    if fresh or name not in _cache:
        c = sqlite3.connect(':memory:')
        c.execute('PRAGMA foreign_keys = ON')
        c.executescript(DB[name])
        if fresh:
            return c
        _cache[name] = c
    return _cache[name]
