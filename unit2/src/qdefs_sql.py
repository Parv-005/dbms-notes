"""SQL teaching queries (company DB 'co').  Each is executed by SQLite; expect= pins the answer."""
from qdefs import Q

# ------------------------------------------------------------- 6. SELECT basics
Q('s_where', 'co', """SELECT name, salary
FROM   employee
WHERE  dept_id = 20 AND salary > 70000;""", expect=[('Aarav', 95000), ('Diya', 72000), ('Kabir', 72000)])
Q('s_between', 'co', """SELECT name, salary
FROM   employee
WHERE  salary BETWEEN 45000 AND 64000;     -- both ends included""")
Q('s_in', 'co', """SELECT name, city
FROM   employee
WHERE  city IN ('Mumbai', 'Pune');""")
Q('s_like1', 'co', """SELECT name FROM employee
WHERE  name LIKE '%a';        -- ends with a""", expect=[('Diya',), ('Meera',), ('Sara',), ('Zoya',)])
Q('s_like2', 'co', """SELECT name FROM employee
WHERE  name LIKE '_a%';       -- 2nd letter is a""", expect=[('Aarav',), ('Kabir',), ('Sara',)])
Q('s_null_wrong', 'co', """SELECT name FROM employee
WHERE  dept_id = NULL;        -- WRONG: comparison with NULL is UNKNOWN""", expect=[],
  cap='Output: 0 rows (= NULL is never TRUE)')
Q('s_null', 'co', """SELECT name FROM employee
WHERE  dept_id IS NULL;       -- correct""", expect=[('Zoya',)])
Q('s_distinct', 'co', """SELECT DISTINCT city
FROM   employee;""")
Q('s_order', 'co', """SELECT name, dept_id, salary
FROM   employee
ORDER  BY dept_id ASC, salary DESC;""",
  cap='Sorted by dept_id, and inside each dept by salary (highest first). NULL dept_id sorts first here (MySQL/SQLite); Oracle puts NULLs last.')
Q('s_limit', 'co', """SELECT name, salary
FROM   employee
ORDER  BY salary DESC
LIMIT  3;                     -- Oracle/standard: FETCH FIRST 3 ROWS ONLY""", sort=False)
Q('s_expr', 'co', """SELECT name, salary, salary * 12 AS annual_salary
FROM   employee
WHERE  dept_id = 10;""")
Q('s_union', 'co', """SELECT city     FROM employee
UNION                          -- duplicates removed
SELECT location FROM department;""")
Q('s_unionall', 'co', """SELECT COUNT(*) AS rows_in_union_all FROM (
  SELECT city FROM employee
  UNION ALL                    -- duplicates kept
  SELECT location FROM department) t;""", expect=[(13,)])
Q('s_intersect', 'co', """SELECT city     FROM employee
INTERSECT
SELECT location FROM department;""")
Q('s_except', 'co', """SELECT location FROM department
EXCEPT                         -- Oracle: MINUS
SELECT city     FROM employee;""", expect=[('Hyderabad',)], cap='Output: 1 row — the only department city where no employee lives')

# ------------------------------------------------------------- 7. aggregates
Q('a_basic', 'co', """SELECT COUNT(*)                AS all_rows,
       COUNT(salary)           AS salaries,
       COUNT(DISTINCT dept_id) AS depts,
       SUM(salary)             AS total,
       AVG(salary)             AS average,
       MIN(salary)             AS lowest,
       MAX(salary)             AS highest
FROM   employee;""", expect=[(9, 8, 3, 486000, 60750.0, 39000, 95000)])
Q('a_group', 'co', """SELECT dept_id, COUNT(*) AS n, SUM(salary) AS total, AVG(salary) AS avg_sal
FROM   employee
GROUP  BY dept_id;""")
Q('a_having', 'co', """SELECT dept_id, COUNT(*) AS n
FROM   employee
GROUP  BY dept_id
HAVING COUNT(*) >= 3;""", expect=[(10, 3), (20, 4)])
Q('a_where_having', 'co', """SELECT   dept_id, AVG(salary) AS avg_sal
FROM     employee
WHERE    city <> 'Delhi'            -- 1. filter ROWS
GROUP BY dept_id                    -- 2. form groups
HAVING   AVG(salary) > 50000        -- 3. filter GROUPS
ORDER BY avg_sal DESC;              -- 4. sort result""", expect=[(20, 72000.0), (10, 57500.0)])
Q('a_count_wrong', 'co', """SELECT d.dept_name, COUNT(*) AS n
FROM   department d LEFT JOIN employee e ON e.dept_id = d.dept_id
GROUP  BY d.dept_name;""", cap='WRONG for Research: COUNT(*) counts the NULL-padded row → 1')
Q('a_count_right', 'co', """SELECT d.dept_name, COUNT(e.emp_id) AS n
FROM   department d LEFT JOIN employee e ON e.dept_id = d.dept_id
GROUP  BY d.dept_name;""", expect=[('HR', 1), ('IT', 4), ('Research', 0), ('Sales', 3)],
  cap='Correct: COUNT(column) skips NULL → Research shows 0')
Q('a_two_cols', 'co', """SELECT dept_id, city, COUNT(*) AS n
FROM   employee
WHERE  dept_id IS NOT NULL
GROUP  BY dept_id, city
ORDER  BY dept_id, city;""", sort=False)

# ------------------------------------------------------------- 8. joins
Q('j_inner', 'co', """SELECT e.name, d.dept_name
FROM   employee e
INNER JOIN department d ON e.dept_id = d.dept_id;""",
  cap='8 rows — Zoya (dept NULL) and Research (no employee) are missing')
Q('j_left', 'co', """SELECT e.name, d.dept_name
FROM   employee e
LEFT JOIN department d ON e.dept_id = d.dept_id;""", cap='9 rows — every employee; Zoya gets NULL')
Q('j_right', 'co', """SELECT e.name, d.dept_name
FROM   employee e
RIGHT JOIN department d ON e.dept_id = d.dept_id;""", cap='9 rows — every department; Research gets NULL name')
Q('j_full', 'co', """SELECT e.name, d.dept_name
FROM   employee e
FULL OUTER JOIN department d ON e.dept_id = d.dept_id;""", cap='10 rows — unmatched rows from both sides')
Q('j_full_mysql', 'co', """-- MySQL has no FULL OUTER JOIN: simulate it
SELECT e.name, d.dept_name FROM employee e LEFT  JOIN department d ON e.dept_id = d.dept_id
UNION
SELECT e.name, d.dept_name FROM employee e RIGHT JOIN department d ON e.dept_id = d.dept_id;""")
Q('j_cross', 'co', """SELECT COUNT(*) AS rows_in_cross_join
FROM   employee CROSS JOIN department;     -- 9 × 4""", expect=[(36,)])
Q('j_natural', 'co', """SELECT name, dept_name
FROM   employee NATURAL JOIN department;   -- joins on the common column dept_id""")
Q('j_using', 'co', """SELECT name, dept_name, location
FROM   employee JOIN department USING (dept_id)
WHERE  location = 'Delhi';""")
Q('j_self', 'co', """SELECT e.name AS employee, m.name AS manager
FROM   employee e
LEFT JOIN employee m ON e.manager_id = m.emp_id;""", cap='Self join: the same table plays two roles')
Q('j_three', 'co', """SELECT e.name, p.pname, w.hours
FROM   employee e
JOIN   works_on w ON w.emp_id  = e.emp_id
JOIN   project  p ON p.proj_id = w.proj_id
WHERE  p.dept_id = 20
ORDER  BY p.pname, e.name;""", sort=False)
Q('j_anti', 'co', """SELECT d.dept_name
FROM   department d
LEFT JOIN employee e ON e.dept_id = d.dept_id
WHERE  e.emp_id IS NULL;               -- departments with NO employee""", expect=[('Research',)])
Q('j_on_where_bad', 'co', """SELECT d.dept_name, COUNT(e.emp_id) AS rich
FROM   department d
LEFT JOIN employee e ON e.dept_id = d.dept_id
WHERE  e.salary > 60000                -- filter AFTER the join: kills NULL rows
GROUP  BY d.dept_name;""", expect=[('IT', 3), ('Sales', 1)], cap='HR and Research vanished!')
Q('j_on_where_good', 'co', """SELECT d.dept_name, COUNT(e.emp_id) AS rich
FROM   department d
LEFT JOIN employee e ON e.dept_id = d.dept_id
                    AND e.salary > 60000   -- filter INSIDE the join
GROUP  BY d.dept_name;""", expect=[('HR', 0), ('IT', 3), ('Research', 0), ('Sales', 1)])

# ------------------------------------------------------------- 9. subqueries
Q('q_scalar', 'co', """SELECT name, salary
FROM   employee
WHERE  salary > (SELECT AVG(salary) FROM employee);   -- avg = 60750""",
  expect=[('Aarav', 95000), ('Diya', 72000), ('Kabir', 72000), ('Meera', 64000)])
Q('q_in', 'co', """SELECT name
FROM   employee
WHERE  emp_id IN (SELECT w.emp_id
                  FROM   works_on w JOIN project p ON p.proj_id = w.proj_id
                  WHERE  p.budget > 400000);""", expect=[('Aarav',), ('Diya',), ('Kabir',)])
Q('q_notin_bad', 'co', """-- employees who manage nobody?
SELECT name
FROM   employee
WHERE  emp_id NOT IN (SELECT manager_id FROM employee);""", expect=[],
  cap='Output: 0 rows — because the subquery contains a NULL (Aarav has no manager)')
Q('q_notin_good', 'co', """SELECT name
FROM   employee e
WHERE  NOT EXISTS (SELECT * FROM employee x WHERE x.manager_id = e.emp_id);""",
  expect=[('Kabir',), ('Rohan',), ('Sara',), ('Ishaan',), ('Zoya',), ('Neel',)])
Q('q_all', 'co', """SELECT name, salary
FROM   employee
WHERE  salary > ALL (SELECT salary FROM employee WHERE dept_id = 10);  -- > 64000""",
  run="SELECT name, salary FROM employee WHERE salary > (SELECT MAX(salary) FROM employee WHERE dept_id = 10)",
  expect=[('Aarav', 95000), ('Diya', 72000), ('Kabir', 72000)])
Q('q_any', 'co', """SELECT name, salary
FROM   employee
WHERE  dept_id <> 10
  AND  salary > ANY (SELECT salary FROM employee WHERE dept_id = 10);  -- > 48000""",
  run="SELECT name, salary FROM employee WHERE dept_id <> 10 AND salary > (SELECT MIN(salary) FROM employee WHERE dept_id = 10)",
  expect=[('Aarav', 95000), ('Diya', 72000), ('Kabir', 72000)])
Q('q_exists', 'co', """SELECT d.dept_name
FROM   department d
WHERE  EXISTS (SELECT * FROM project p
               WHERE p.dept_id = d.dept_id AND p.budget >= 500000);""", expect=[('IT',), ('Research',)])
Q('q_corr_avg', 'co', """SELECT e.name, e.dept_id, e.salary
FROM   employee e
WHERE  e.salary > (SELECT AVG(x.salary)
                   FROM   employee x
                   WHERE  x.dept_id = e.dept_id);   -- inner query uses OUTER row e""",
  expect=[('Aarav', 20, 95000), ('Meera', 10, 64000)])
Q('q_corr_max', 'co', """SELECT e.name, e.dept_id, e.salary
FROM   employee e
WHERE  e.salary = (SELECT MAX(x.salary)
                   FROM   employee x
                   WHERE  x.dept_id = e.dept_id);""",
  expect=[('Aarav', 20, 95000), ('Meera', 10, 64000), ('Ishaan', 30, 45000)])
Q('q_derived', 'co', """SELECT d.dept_name, t.avg_sal
FROM   (SELECT dept_id, AVG(salary) AS avg_sal
        FROM   employee
        GROUP  BY dept_id) AS t             -- derived table (inline view)
JOIN   department d ON d.dept_id = t.dept_id
WHERE  t.avg_sal > 50000;""")
Q('q_second1', 'co', """SELECT MAX(salary) AS second_highest
FROM   employee
WHERE  salary < (SELECT MAX(salary) FROM employee);""", expect=[(72000,)])
Q('q_second2', 'co', """SELECT DISTINCT salary
FROM   employee
ORDER  BY salary DESC
LIMIT  1 OFFSET 1;          -- skip 1, take 1""", expect=[(72000,)])
Q('q_nth', 'co', """-- N-th highest salary (here N = 3): exactly N-1 distinct salaries are bigger
SELECT DISTINCT e1.salary
FROM   employee e1
WHERE  2 = (SELECT COUNT(DISTINCT e2.salary)
            FROM   employee e2
            WHERE  e2.salary > e1.salary);""", expect=[(64000,)])
Q('q_div_ne', 'co', """-- employees who work on EVERY project of department 20
SELECT e.name
FROM   employee e
WHERE  NOT EXISTS (                       -- there is no IT project ...
         SELECT * FROM project p
         WHERE  p.dept_id = 20
         AND    NOT EXISTS (              -- ... that e does not work on
                  SELECT * FROM works_on w
                  WHERE  w.emp_id = e.emp_id AND w.proj_id = p.proj_id));""",
  expect=[('Diya',), ('Kabir',)])
Q('q_div_cnt', 'co', """SELECT w.emp_id
FROM   works_on w JOIN project p ON p.proj_id = w.proj_id
WHERE  p.dept_id = 20
GROUP  BY w.emp_id
HAVING COUNT(DISTINCT w.proj_id) = (SELECT COUNT(*) FROM project WHERE dept_id = 20);""",
  expect=[(2,), (3,)])
Q('q_div_exc', 'co', """SELECT e.name
FROM   employee e
WHERE  NOT EXISTS (
         SELECT proj_id FROM project  WHERE dept_id = 20
         EXCEPT
         SELECT proj_id FROM works_on WHERE emp_id = e.emp_id);""", expect=[('Diya',), ('Kabir',)])
Q('q_cte', 'co', """WITH dept_avg AS (
    SELECT dept_id, AVG(salary) AS avg_sal
    FROM   employee
    GROUP  BY dept_id)
SELECT e.name, e.salary, ROUND(a.avg_sal) AS dept_avg
FROM   employee e JOIN dept_avg a ON a.dept_id = e.dept_id
WHERE  e.salary > a.avg_sal;""", expect=[('Aarav', 95000, 79667.0), ('Meera', 64000, 54333.0)])
Q('q_window', 'co', """SELECT name, salary,
       RANK()       OVER (ORDER BY salary DESC) AS rnk,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS drnk,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS rn
FROM   employee
WHERE  salary IS NOT NULL
ORDER  BY salary DESC
LIMIT  5;""", sort=False, cap='Ties: RANK skips (1,2,2,4), DENSE_RANK does not (1,2,2,3), ROW_NUMBER never ties')
Q('q_window2', 'co', """SELECT name, dept_id, salary
FROM  (SELECT name, dept_id, salary,
              DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY salary DESC) AS r
       FROM   employee
       WHERE  salary IS NOT NULL) t
WHERE  r = 2;                        -- 2nd highest salary in EACH department""",
  expect=[('Diya', 20, 72000), ('Kabir', 20, 72000), ('Sara', 10, 51000)])
Q('q_selectlist', 'co', """SELECT d.dept_name,
       (SELECT COUNT(*) FROM employee e WHERE e.dept_id = d.dept_id) AS headcount
FROM   department d;""", expect=[('Sales', 3), ('IT', 4), ('HR', 1), ('Research', 0)])

# ------------------------------------------------------------- 5. DML demos
Q('dml_update', 'co', """UPDATE employee
SET    salary = salary * 110 / 100     -- 10% raise
WHERE  dept_id = 10;""", after="SELECT name, salary FROM employee WHERE dept_id = 10",
  cap='Sales employees after the UPDATE')
Q('dml_delete', 'co', """DELETE FROM works_on
WHERE  hours < 50;""", after="SELECT * FROM works_on", cap='works_on after the DELETE (2 rows removed)')
Q('dml_insert_select', 'co', """CREATE TABLE it_staff(emp_id INT, name VARCHAR(30));
INSERT INTO it_staff (emp_id, name)
SELECT emp_id, name FROM employee WHERE dept_id = 20;    -- insert the result of a query""",
  after="SELECT * FROM it_staff")

# ------------------------------------------------------------- 2. integrity constraint demo (really executed)
from qdefs import V
IC_SETUP = """
CREATE TABLE department(dept_id INT NOT NULL PRIMARY KEY, dept_name VARCHAR(30) NOT NULL UNIQUE, building VARCHAR(20) DEFAULT 'Main');
CREATE TABLE student(roll_no INT NOT NULL PRIMARY KEY, name VARCHAR(40) NOT NULL, email VARCHAR(50) UNIQUE,
  age INT CHECK (age BETWEEN 16 AND 40),
  dept_id INT REFERENCES department(dept_id) ON DELETE SET NULL ON UPDATE CASCADE);
"""
V('ic1', IC_SETUP, [
    ("INSERT INTO department VALUES (10, 'CSE', 'Block A');", 'ok', 'all constraints satisfied'),
    ("INSERT INTO department (dept_id, dept_name) VALUES (20, 'IT');", 'ok', 'building not given → DEFAULT <code>Main</code> is stored'),
    ("INSERT INTO department VALUES (30, 'CSE', 'Block C');", 'err', '<b>UNIQUE</b> violated — dept_name CSE already exists'),
    ("INSERT INTO student VALUES (1, 'Aman', 'aman@x.in', 20, 10);", 'ok', 'all constraints satisfied'),
    ("INSERT INTO student VALUES (1, 'Bela', 'bela@x.in', 21, 10);", 'err', '<b>Key constraint</b> — PK roll_no 1 already exists'),
    ("INSERT INTO student VALUES (NULL, 'Chirag', 'ch@x.in', 19, 10);", 'err', '<b>Entity integrity</b> — PK cannot be NULL'),
    ("INSERT INTO student VALUES (2, NULL, 'dev@x.in', 19, 10);", 'err', '<b>NOT NULL</b> (domain) — name is mandatory'),
    ("INSERT INTO student VALUES (3, 'Dev', 'aman@x.in', 19, 10);", 'err', '<b>UNIQUE</b> — email already used'),
    ("INSERT INTO student VALUES (4, 'Esha', 'esha@x.in', 12, 10);", 'err', '<b>CHECK</b> (domain) — age 12 not in 16..40'),
    ("INSERT INTO student VALUES (5, 'Farhan', 'f@x.in', 22, 99);", 'err', '<b>Referential integrity</b> — no department 99'),
    ("INSERT INTO student VALUES (6, 'Gita', NULL, 19, NULL);", 'ok', 'UNIQUE column may be NULL; an FK may be NULL'),
    ("INSERT INTO student VALUES (7, 'Hari', 'hari@x.in', 23, 20);", 'ok', 'department 20 exists'),
    ("UPDATE student SET dept_id = 50 WHERE roll_no = 7;", 'err', '<b>Referential integrity</b> — FK changed to a non-existent value'),
    ("UPDATE department SET dept_id = 21 WHERE dept_id = 20;", 'ok', '<b>ON UPDATE CASCADE</b> — Hari’s dept_id becomes 21 automatically'),
    ("DELETE FROM department WHERE dept_id = 10;", 'ok', '<b>ON DELETE SET NULL</b> — Aman stays, his dept_id becomes NULL'),
], after='SELECT * FROM student')

# 2024 end-sem Q2(a)(i): self-referencing FK with ON DELETE CASCADE
V('cascade24', """CREATE TABLE T(A INT PRIMARY KEY, C INT REFERENCES T(A) ON DELETE CASCADE);
INSERT INTO T VALUES (2,4),(3,4),(4,3),(5,2),(7,2),(9,5),(6,4);""",
  [("DELETE FROM T WHERE A = 2;", 'ok', 'deletes (2,4) and cascades')],
  after='SELECT * FROM T ORDER BY A')

# ------------------------------------------------------------- 4. SQL versions of the calculus queries (sailors DB)
Q('sb_red', 'sb', """SELECT DISTINCT s.sname
FROM   Sailors s, Reserves r, Boats b
WHERE  r.sid = s.sid AND b.bid = r.bid AND b.color = 'red';""",
  expect=[('Dustin',), ('Lubber',), ('Horatio',), ('Andy',), ('Rusty',)])
Q('sb_both', 'sb', """SELECT s.sname
FROM   Sailors s
WHERE  EXISTS (SELECT * FROM Reserves r JOIN Boats b ON b.bid = r.bid
               WHERE r.sid = s.sid AND b.color = 'red')
AND    EXISTS (SELECT * FROM Reserves r JOIN Boats b ON b.bid = r.bid
               WHERE r.sid = s.sid AND b.color = 'green');""", expect=[('Dustin',), ('Lubber',)])
Q('sb_notred', 'sb', """SELECT s.sname
FROM   Sailors s
WHERE  NOT EXISTS (SELECT * FROM Reserves r JOIN Boats b ON b.bid = r.bid
                   WHERE r.sid = s.sid AND b.color = 'red');""",
  expect=[('Brutus',), ('Zorba',), ('Horatio',), ('Art',), ('Bob',)])
Q('sb_all', 'sb', """SELECT s.sname
FROM   Sailors s
WHERE  NOT EXISTS (SELECT * FROM Boats b            -- there is no boat ...
                   WHERE NOT EXISTS (SELECT * FROM Reserves r   -- ... not reserved by s
                                     WHERE r.sid = s.sid AND r.bid = b.bid));""", expect=[('Dustin',)])
Q('sb_oldest', 'sb', """SELECT s.sname, s.age
FROM   Sailors s
WHERE  NOT EXISTS (SELECT * FROM Sailors s2 WHERE s2.age > s.age);""", expect=[('Bob', 63.5)])

# ------------------------------------------------------------- 11. triggers (SQLite syntax, verified)
Q('trg_bank', 'co', """-- bank PYQ (Mid-Sem 2025): keep balance in step with transactions
CREATE TABLE accounts(account_id INT PRIMARY KEY, customer_name TEXT, balance INT);
CREATE TABLE transactions(trans_id INT PRIMARY KEY, account_id INT REFERENCES accounts,
                          amount INT, trans_type TEXT, trans_date TEXT);
CREATE TRIGGER trg_after_txn AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
  UPDATE accounts
  SET    balance = balance + CASE NEW.trans_type
                                WHEN 'DEPOSIT'  THEN  NEW.amount
                                WHEN 'WITHDRAW' THEN -NEW.amount
                             END
  WHERE  account_id = NEW.account_id;
END;
INSERT INTO accounts VALUES (1, 'Asha', 10000), (2, 'Ravi', 5000);
INSERT INTO transactions VALUES (101, 1, 2500, 'DEPOSIT',  '2025-09-01');
INSERT INTO transactions VALUES (102, 2, 1200, 'WITHDRAW', '2025-09-02');
INSERT INTO transactions VALUES (103, 1,  500, 'WITHDRAW', '2025-09-03');""",
  after="SELECT * FROM accounts", fresh=True, cap='accounts after the three inserts: Asha 10000+2500−500, Ravi 5000−1200',
  expect=[(1, 'Asha', 12000), (2, 'Ravi', 3800)])
V('trg_before', """CREATE TABLE emp(id INT PRIMARY KEY, name TEXT, salary INT);
CREATE TABLE salary_audit(id INT, old_sal INT, new_sal INT, changed_on TEXT);
CREATE TRIGGER trg_no_cut BEFORE UPDATE OF salary ON emp
FOR EACH ROW WHEN NEW.salary < OLD.salary
BEGIN
  SELECT RAISE(ABORT, 'salary cannot be decreased');
END;
CREATE TRIGGER trg_audit AFTER UPDATE OF salary ON emp
FOR EACH ROW
BEGIN
  INSERT INTO salary_audit VALUES (OLD.id, OLD.salary, NEW.salary, '2026-11-25');
END;
INSERT INTO emp VALUES (1,'Aarav',90000),(2,'Diya',70000);""", [
    ("UPDATE emp SET salary = 95000 WHERE id = 1;", 'ok', 'BEFORE trigger lets it through; AFTER trigger writes an audit row'),
    ("UPDATE emp SET salary = 60000 WHERE id = 2;", 'err', 'BEFORE trigger raises an error → update cancelled, nothing audited'),
    ("UPDATE emp SET salary = 75000 WHERE id = 2;", 'ok', 'raise allowed → audited'),
], after='SELECT * FROM salary_audit')
