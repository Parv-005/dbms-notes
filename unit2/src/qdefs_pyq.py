"""Test databases for every PYQ schema + all PYQ answers (SQL executed by SQLite, RA computed by the engine).

Each schema is the one printed in the question paper; the rows are invented test data designed to exercise the
tricky cases (ties, NULLs, rows with no match).  expect= pins the hand-derived answer.
"""
import data
from qdefs import Q, A, V, RA

D = data.DB

# =========================================================================== 2024 end-sem Q2(b)
D['p24'] = """
CREATE TABLE Departments(DepartmentID INT PRIMARY KEY, DepartmentName TEXT);
CREATE TABLE Employees(EmployeeID INT PRIMARY KEY, Name TEXT, DepartmentID INT REFERENCES Departments, Salary INT);
CREATE TABLE Projects(ProjectID INT PRIMARY KEY, ProjectName TEXT, DepartmentID INT REFERENCES Departments);
CREATE TABLE EmployeeProjects(EmployeeID INT REFERENCES Employees, ProjectID INT REFERENCES Projects, HoursWorked INT,
  PRIMARY KEY(EmployeeID, ProjectID));
CREATE TABLE Sales(SalesID INT PRIMARY KEY, EmployeeID INT REFERENCES Employees, SaleDate TEXT, SaleAmount INT);
INSERT INTO Departments VALUES (1,'Sales'),(2,'Engineering'),(3,'HR');
INSERT INTO Employees VALUES (1,'Ann',1,65000),(2,'Bob',1,72000),(3,'Cid',2,90000),(4,'Dee',2,90000),(5,'Eve',2,71000),
  (6,'Fay',3,50000),(7,'Gus',3,48000);
INSERT INTO Projects VALUES (10,'CRM',1),(11,'Website',2),(12,'AI',2),(13,'Payroll',3);
INSERT INTO EmployeeProjects VALUES (1,10,300),(2,10,250),(3,11,250),(4,11,150),(5,12,220),(3,12,100),(6,13,120),(7,13,90);
INSERT INTO Sales VALUES (1,1,'2024-01-05',3000),(2,1,'2024-02-10',2500),(3,2,'2024-01-20',1500),(4,2,'2024-03-02',1000),
  (5,3,'2024-02-14',4000),(6,3,'2024-03-01',2600),(7,6,'2024-01-11',800),(8,5,'2024-04-04',2100);
"""
Q('p24_1', 'p24', """SELECT d.DepartmentName, e.Name, e.Salary
FROM   Employees e
JOIN   Departments d ON d.DepartmentID = e.DepartmentID
WHERE  e.Salary = (SELECT MAX(x.Salary)
                   FROM   Employees x
                   WHERE  x.DepartmentID = e.DepartmentID);""",
  expect=[('Sales', 'Bob', 72000), ('Engineering', 'Cid', 90000), ('Engineering', 'Dee', 90000), ('HR', 'Fay', 50000)])
Q('p24_2', 'p24', """SELECT d.DepartmentName,
       SUM(ep.HoursWorked)           AS TotalHours,
       COUNT(DISTINCT ep.EmployeeID) AS NumEmployees
FROM   Departments d
JOIN   Projects p          ON p.DepartmentID = d.DepartmentID
JOIN   EmployeeProjects ep ON ep.ProjectID   = p.ProjectID
GROUP  BY d.DepartmentID, d.DepartmentName
HAVING SUM(ep.HoursWorked) &gt; 500;""".replace('&gt;', '>'),
  expect=[('Sales', 550, 2), ('Engineering', 720, 3)])
Q('p24_3', 'p24', """SELECT d.DepartmentName, e.Name, SUM(s.SaleAmount) AS TotalSales
FROM   Employees e
JOIN   Departments d ON d.DepartmentID = e.DepartmentID
JOIN   Sales s       ON s.EmployeeID   = e.EmployeeID
GROUP  BY d.DepartmentName, e.EmployeeID, e.Name
HAVING SUM(s.SaleAmount) > 5000;""", expect=[('Sales', 'Ann', 5500), ('Engineering', 'Cid', 6600)])
Q('p24_4', 'p24', """SELECT p.ProjectName
FROM   Projects p
JOIN   EmployeeProjects ep ON ep.ProjectID  = p.ProjectID
JOIN   Employees e         ON e.EmployeeID  = ep.EmployeeID
GROUP  BY p.ProjectID, p.ProjectName
HAVING MIN(e.Salary) > 70000;          -- the lowest-paid member earns > 70000""",
  expect=[('Website',), ('AI',)])
Q('p24_4b', 'p24', """SELECT p.ProjectName
FROM   Projects p
WHERE  EXISTS (SELECT * FROM EmployeeProjects ep WHERE ep.ProjectID = p.ProjectID)
AND    NOT EXISTS (SELECT *
                   FROM   EmployeeProjects ep JOIN Employees e ON e.EmployeeID = ep.EmployeeID
                   WHERE  ep.ProjectID = p.ProjectID AND e.Salary <= 70000);""",
  expect=[('Website',), ('AI',)])
Q('p24_5', 'p24', """SELECT d.DepartmentName, p.ProjectName, AVG(s.SaleAmount) AS AvgSale
FROM   Departments d
JOIN   Projects p          ON p.DepartmentID = d.DepartmentID
JOIN   EmployeeProjects ep ON ep.ProjectID   = p.ProjectID
JOIN   Sales s             ON s.EmployeeID   = ep.EmployeeID
GROUP  BY d.DepartmentName, p.ProjectID, p.ProjectName
HAVING AVG(s.SaleAmount) > 2000;""", expect=[('Engineering', 'Website', 3300.0), ('Engineering', 'AI', 2900.0)])

# =========================================================================== 2024 end-sem Q2(c) and 2025 end-sem Q2(c) (RA)
D['uni'] = """
CREATE TABLE Students(StudentID INT PRIMARY KEY, Name TEXT, Age INT, Major TEXT);
CREATE TABLE Courses(CourseID TEXT PRIMARY KEY, CourseName TEXT, Credits INT);
CREATE TABLE Enrollments(StudentID INT REFERENCES Students, CourseID TEXT REFERENCES Courses, Grade TEXT);
CREATE TABLE Professors(ProfessorID INT PRIMARY KEY, Name TEXT, Department TEXT);
CREATE TABLE Teaches(ProfessorID INT REFERENCES Professors, CourseID TEXT REFERENCES Courses, Semester TEXT);
INSERT INTO Students VALUES (1,'Aditi',19,'CSE'),(2,'Bharat',21,'ECE'),(3,'Charu',22,'CSE'),(4,'Dev',18,'ME'),(5,'Esha',20,'CSE');
INSERT INTO Courses VALUES ('C1','DBMS',4),('C2','Networks',3),('C3','Thermodynamics',3),('C4','AI',4),('C5','Signals',3);
INSERT INTO Professors VALUES (101,'Dr. Smith','CSE'),(102,'Dr. Rao','ECE'),(103,'Dr. Khan','ME'),(104,'Dr. Bose','CSE');
INSERT INTO Teaches VALUES (101,'C1','Fall'),(101,'C4','Fall'),(102,'C5','Spring'),(103,'C3','Fall'),(104,'C2','Spring');
INSERT INTO Enrollments VALUES (1,'C1','A'),(1,'C4','A'),(1,'C2','A'),(2,'C5','A'),(2,'C1','B'),(3,'C1','A'),(3,'C4','B'),
  (3,'C2','A'),(3,'C3','A'),(4,'C1','C'),(4,'C2','B'),(5,'C4','A'),(5,'C1','A');
"""
from qdefs import rels  # noqa: E402

A('u1', 'uni', r"SmithCourses \gets \pi_{CourseID}(\sigma_{Name='Dr. Smith'}(Professors) \join Teaches) \br Result \gets \pi_{Name}((\pi_{StudentID, CourseID}(Enrollments) \div SmithCourses) \join Students)",
  lambda D: (D['Enrollments'].proj('StudentID', 'CourseID')
             .div(D['Professors'].sel(lambda t: t.Name == 'Dr. Smith').nat(D['Teaches']).proj('CourseID'))
             .nat(D['Students']).proj('Name')),
  expect=[('Aditi',), ('Charu',), ('Esha',)])


def _three_A(D):
    e = D['Enrollments'].sel(lambda t: t.Grade == 'A').proj('StudentID', 'CourseID')
    e1, e2, e3 = (e.ren(names=[f'S{i}', f'C{i}']) for i in (1, 2, 3))
    j = e1.theta(e2, lambda t: t.S1 == t.S2 and t.C1 < t.C2).theta(e3, lambda t: t.S1 == t.S3 and t.C2 < t.C3)
    return j.proj('S1').ren(names=['StudentID']).nat(D['Students']).proj('Name', 'Major')


A('u2', 'uni', r"\pi_{Name, Major}(\sigma_{cnt > 2}(_{StudentID}\gamma_{count(CourseID) \to cnt}(\sigma_{Grade='A'}(Enrollments))) \join Students)",
  lambda D: D['Enrollments'].sel(lambda t: t.Grade == 'A').agg(['StudentID'], [('count', 'CourseID', 'cnt')])
  .sel(lambda t: t.cnt > 2).nat(D['Students']).proj('Name', 'Major'),
  expect=[('Aditi', 'CSE'), ('Charu', 'CSE')])
A('u2b', 'uni', r"E \gets \pi_{StudentID, CourseID}(\sigma_{Grade='A'}(Enrollments)) \br \pi_{Name, Major}(\pi_{E1.StudentID}(\rho_{E1}(E) \join_{E1.StudentID=E2.StudentID \and E1.CourseID<E2.CourseID} \rho_{E2}(E) \join_{E2.StudentID=E3.StudentID \and E2.CourseID<E3.CourseID} \rho_{E3}(E)) \join Students)",
  _three_A, expect=[('Aditi', 'CSE'), ('Charu', 'CSE')])
A('u3', 'uni', r"Fall \gets \pi_{CourseID}(\sigma_{Semester='Fall'}(Teaches)) \br _{CourseID, CourseName}\gamma_{count(StudentID) \to NumStudents}(Courses \join Fall \join Enrollments)",
  lambda D: D['Courses'].nat(D['Teaches'].sel(lambda t: t.Semester == 'Fall').proj('CourseID')).nat(D['Enrollments'])
  .proj('CourseID', 'CourseName', 'StudentID').agg(['CourseID', 'CourseName'], [('count', 'StudentID', 'NumStudents')]),
  expect=[('C1', 'DBMS', 5), ('C4', 'AI', 3), ('C3', 'Thermodynamics', 1)])
A('u4', 'uni', r"P \gets \rho_{(ProfessorID, PName, Department)}(Professors) \br \pi_{StudentID, Name}(\sigma_{Major = Department}(Students \join Enrollments \join Teaches \join P))",
  lambda D: D['Students'].nat(D['Enrollments']).nat(D['Teaches'])
  .nat(D['Professors'].ren(names=['ProfessorID', 'PName', 'Department']))
  .sel(lambda t: t.Major == t.Department).proj('StudentID', 'Name'),
  expect=[(1, 'Aditi'), (2, 'Bharat'), (3, 'Charu'), (5, 'Esha')])
A('u5', 'uni', r"Taught \gets \pi_{ProfessorID}(Teaches \join Enrollments \join \sigma_{Age < 20}(Students)) \br \pi_{Name}((\pi_{ProfessorID}(Professors) \minus Taught) \join Professors)",
  lambda D: (D['Professors'].proj('ProfessorID') - D['Teaches'].nat(D['Enrollments'])
             .nat(D['Students'].sel(lambda t: t.Age < 20)).proj('ProfessorID')).nat(D['Professors']).proj('Name'),
  expect=[('Dr. Rao',), ('Dr. Khan',)])

# =========================================================================== 2026 summer end-sem Q2(b) (RA)
D['shop'] = """
CREATE TABLE Customer(CustomerID INT PRIMARY KEY, Name TEXT, City TEXT);
CREATE TABLE Orders(OrderID INT PRIMARY KEY, CustomerID INT REFERENCES Customer, OrderDate TEXT, Amount INT);
CREATE TABLE Products(ProductID INT PRIMARY KEY, ProductName TEXT, Price INT);
CREATE TABLE OrderDetails(OrderID INT REFERENCES Orders, ProductID INT REFERENCES Products, Quantity INT);
INSERT INTO Customer VALUES (1,'Asha','Delhi'),(2,'Ravi','Mumbai'),(3,'Meena','Delhi'),(4,'John','Pune');
INSERT INTO Products VALUES (1,'Laptop',65000),(2,'Phone',25000),(3,'TV',45000),(4,'Mouse',800),(5,'Keyboard',1500),
  (6,'Pen drive',600),(7,'Headphones',3000);
INSERT INTO Orders VALUES (101,1,'2025-01-05',90000),(102,1,'2025-02-01',45000),(103,2,'2025-02-10',68100),
  (104,2,'2025-03-01',26800),(105,3,'2025-03-03',2300),(106,3,'2025-04-09',25000);
INSERT INTO OrderDetails VALUES (101,1,1),(101,2,1),(102,3,1),(103,1,1),(103,4,2),(103,5,1),(104,2,1),(104,6,3),
  (105,4,1),(105,5,1),(106,2,1);
"""
A('s1', 'shop', r"CP \gets \pi_{CustomerID, ProductID}(Orders \join OrderDetails) \br Costly \gets \pi_{ProductID}(\sigma_{Price > 10000}(Products)) \br \pi_{CustomerID, Name}((CP \div Costly) \join Customer)",
  lambda D: D['Orders'].nat(D['OrderDetails']).proj('CustomerID', 'ProductID')
  .div(D['Products'].sel(lambda t: t.Price > 10000).proj('ProductID')).nat(D['Customer']).proj('CustomerID', 'Name'),
  expect=[(1, 'Asha')])
A('s2', 'shop', r"\pi_{ProductID, ProductName}((\pi_{ProductID}(Products) \minus \pi_{ProductID}(OrderDetails)) \join Products)",
  lambda D: (D['Products'].proj('ProductID') - D['OrderDetails'].proj('ProductID')).nat(D['Products']).proj('ProductID', 'ProductName'),
  expect=[(7, 'Headphones')])
A('s3', 'shop', r"\pi_{CustomerID, Name, Total}(\sigma_{Total > 50000}(_{CustomerID}\gamma_{sum(Amount) \to Total}(Orders)) \join Customer)",
  lambda D: D['Orders'].agg(['CustomerID'], [('sum', 'Amount', 'Total')]).sel(lambda t: t.Total > 50000)
  .nat(D['Customer']).proj('CustomerID', 'Name', 'Total'),
  expect=[(1, 'Asha', 135000), (2, 'Ravi', 94900)])
A('s4', 'shop', r"\pi_{ProductName}(\sigma_{City='Delhi'}(Customer) \join Orders \join OrderDetails \join Products)",
  lambda D: D['Customer'].sel(lambda t: t.City == 'Delhi').nat(D['Orders']).nat(D['OrderDetails'])
  .nat(D['Products']).proj('ProductName'),
  expect=[('Laptop',), ('Phone',), ('TV',), ('Mouse',), ('Keyboard',)])
A('s5', 'shop', r"CP \gets \pi_{CustomerID, ProductID}(Orders \join OrderDetails) \br \pi_{CustomerID, Name}(\sigma_{n > 3}(_{CustomerID}\gamma_{count(ProductID) \to n}(CP)) \join Customer)",
  lambda D: D['Orders'].nat(D['OrderDetails']).proj('CustomerID', 'ProductID').agg(['CustomerID'], [('count', 'ProductID', 'n')])
  .sel(lambda t: t.n > 3).nat(D['Customer']).proj('CustomerID', 'Name'),
  expect=[(2, 'Ravi')])

# =========================================================================== 2025 end-sem Q2(a) AQI (SQL)
D['aqi'] = """
CREATE TABLE LOCATIONS(LocID INT PRIMARY KEY, AreaName TEXT, Zone TEXT, PopulationDensity INT);
CREATE TABLE SENSORS(SensorID INT PRIMARY KEY, LocID INT REFERENCES LOCATIONS, SensorType TEXT, InstalledDate TEXT);
CREATE TABLE READINGS(SensorID INT REFERENCES SENSORS, RDate TEXT, PM2_5 REAL, PM10 REAL, NO2 REAL, SO2 REAL, AQI INT,
  PRIMARY KEY(SensorID, RDate));
CREATE TABLE ALERTS(AlertID INT PRIMARY KEY, LocID INT REFERENCES LOCATIONS, ADate TEXT, AQI_Level TEXT, AlertType TEXT);
INSERT INTO LOCATIONS VALUES (1,'Anand Vihar','East',30000),(2,'RK Puram','South',12000),(3,'Dwarka','West',9000),
  (4,'Lodhi Road','Central',7000);
INSERT INTO SENSORS VALUES (101,1,'PM','2023-01-10'),(102,1,'Gas','2023-05-01'),(201,2,'PM','2024-02-02'),(301,3,'PM','2024-07-07');
INSERT INTO READINGS VALUES
  (101,'2025-11-01',310,420,80,12,450),(101,'2025-11-03',280,400,70,10,420),(101,'2025-11-07',350,470,90,15,480),
  (101,'2024-11-07',300,430,85,14,430),(102,'2025-11-02',250,380,60,9,390),
  (201,'2025-11-05',260,390,66,11,410),(201,'2025-11-06',255,385,60,10,405),(201,'2025-01-10',60,120,30,5,150),
  (301,'2025-11-07',90,170,35,6,180),(301,'2025-11-08',120,210,40,7,220);
INSERT INTO ALERTS VALUES (1,1,'2025-11-07','Severe','Smog'),(2,2,'2025-11-07','Very Poor','Smog'),
  (3,2,'2025-11-06','Severe','Smog'),(4,3,'2025-11-07','Moderate','Info');
"""
Q('aqi1', 'aqi', """SELECT DISTINCT L.AreaName
FROM   LOCATIONS L JOIN ALERTS A ON A.LocID = L.LocID
WHERE  A.AQI_Level = 'Severe'
AND    A.ADate = '2025-11-07';""", expect=[('Anand Vihar',)])
Q('aqi2', 'aqi', """SELECT L.LocID, L.AreaName
FROM   LOCATIONS L
WHERE  NOT EXISTS (SELECT * FROM SENSORS S WHERE S.LocID = L.LocID);""", expect=[(4, 'Lodhi Road')])
Q('aqi2b', 'aqi', """SELECT L.LocID, L.AreaName
FROM   LOCATIONS L LEFT JOIN SENSORS S ON S.LocID = L.LocID
WHERE  S.SensorID IS NULL;""", expect=[(4, 'Lodhi Road')])
Q('aqi3', 'aqi', """SELECT L.AreaName, COUNT(S.SensorID) AS NumSensors
FROM   LOCATIONS L LEFT JOIN SENSORS S ON S.LocID = L.LocID
GROUP  BY L.LocID, L.AreaName
ORDER  BY NumSensors DESC;""", sort=False,
  expect=[('Anand Vihar', 2), ('RK Puram', 1), ('Dwarka', 1), ('Lodhi Road', 0)])
Q('aqi4', 'aqi', """SELECT L.LocID, L.AreaName, COUNT(*) AS TimesAbove400
FROM   LOCATIONS L
JOIN   SENSORS  S ON S.LocID    = L.LocID
JOIN   READINGS R ON R.SensorID = S.SensorID
WHERE  R.AQI > 400
AND    R.RDate BETWEEN '2025-01-01' AND '2025-12-31'     -- or YEAR(R.RDate) = 2025
GROUP  BY L.LocID, L.AreaName
HAVING COUNT(*) >= 3;""", expect=[(1, 'Anand Vihar', 3)])
Q('aqi5', 'aqi', """SELECT L.AreaName, AVG(R.AQI) AS AvgAQI
FROM   LOCATIONS L
JOIN   SENSORS  S ON S.LocID    = L.LocID
JOIN   READINGS R ON R.SensorID = S.SensorID
GROUP  BY L.LocID, L.AreaName
HAVING AVG(R.AQI) > 250;""", expect=[('Anand Vihar', 434.0), ('RK Puram', 321.6666666666667)])

# =========================================================================== 2026 summer end-sem Q2(a)(i) Employee
D['emp26'] = """
CREATE TABLE Employee(EmpID INT PRIMARY KEY, Name TEXT, Department TEXT, Salary INT);
INSERT INTO Employee VALUES (1,'Aarav','IT',90000),(2,'Bhavya','IT',85000),(3,'Chetan','IT',85000),(4,'Dia','IT',70000),
 (5,'Eshan','IT',60000),(6,'Farah','IT',55000),(7,'Gauri','HR',50000),(8,'Harsh','HR',45000),(9,'Ira','HR',40000),
 (10,'Jai','Sales',65000),(11,'Kavya','Sales',62000),(12,'Laksh','Sales',58000),(13,'Mira','Sales',52000),
 (14,'Nikhil','Sales',50000),(15,'Ojas','Sales',47000);
"""
Q('e26a', 'emp26', """SELECT e.Department, e.Name, e.Salary
FROM   Employee e
WHERE  e.Salary = (SELECT MAX(x.Salary)                       -- highest salary ...
                   FROM   Employee x
                   WHERE  x.Department = e.Department
                   AND    x.Salary < (SELECT MAX(y.Salary)    -- ... below the department maximum
                                      FROM   Employee y
                                      WHERE  y.Department = e.Department));""",
  expect=[('IT', 'Bhavya', 85000), ('IT', 'Chetan', 85000), ('HR', 'Harsh', 45000), ('Sales', 'Kavya', 62000)])
Q('e26a2', 'emp26', """SELECT e.Department, e.Name, e.Salary
FROM   Employee e
WHERE  1 = (SELECT COUNT(DISTINCT x.Salary)      -- exactly one distinct salary above mine
            FROM   Employee x
            WHERE  x.Department = e.Department
            AND    x.Salary > e.Salary);""",
  expect=[('IT', 'Bhavya', 85000), ('IT', 'Chetan', 85000), ('HR', 'Harsh', 45000), ('Sales', 'Kavya', 62000)])
Q('e26b', 'emp26', """SELECT Department, ROUND(AVG(Salary), 2) AS AvgSalary, COUNT(*) AS NumEmp
FROM   Employee
GROUP  BY Department
HAVING COUNT(*) > 5;""", expect=[('IT', 74166.67, 6), ('Sales', 55666.67, 6)])
Q('e26c', 'emp26', """SELECT e.Name, e.Department, e.Salary
FROM   Employee e
WHERE  e.Salary > (SELECT AVG(x.Salary) FROM Employee x WHERE x.Department = e.Department);""",
  expect=[('Aarav', 'IT', 90000), ('Bhavya', 'IT', 85000), ('Chetan', 'IT', 85000), ('Gauri', 'HR', 50000),
          ('Jai', 'Sales', 65000), ('Kavya', 'Sales', 62000), ('Laksh', 'Sales', 58000)])

# =========================================================================== 2026 summer end-sem Q2(c) banking
D['bank26'] = """
CREATE TABLE Customer(CustomerID INT PRIMARY KEY, Name TEXT, City TEXT);
CREATE TABLE Branch(BranchID INT PRIMARY KEY, BranchName TEXT);
CREATE TABLE Account(AccountNo INT PRIMARY KEY, CustomerID INT REFERENCES Customer, Balance INT);
CREATE TABLE Loan(LoanID INT PRIMARY KEY, CustomerID INT REFERENCES Customer, Amount INT);
INSERT INTO Customer VALUES (1,'Asha','Delhi'),(2,'Ravi','Mumbai'),(3,'Meena','Delhi'),(4,'John','Pune'),(5,'Zara','Mumbai'),
  (6,'Kiran','Pune');
INSERT INTO Branch VALUES (1,'Connaught Place'),(2,'Andheri');
INSERT INTO Account VALUES (1001,1,50000),(1002,1,30000),(1003,2,15000),(1004,3,90000),(1005,4,5000),(1006,5,120000);
INSERT INTO Loan VALUES (1,2,40000),(2,3,20000),(3,4,25000),(4,4,10000),(5,6,30000);
"""
Q('b1', 'bank26', """-- R1. Each customer's total balance over all accounts (join + aggregate)
SELECT c.CustomerID, c.Name, SUM(a.Balance) AS TotalBalance, COUNT(*) AS NumAccounts
FROM   Customer c JOIN Account a ON a.CustomerID = c.CustomerID
GROUP  BY c.CustomerID, c.Name;""",
  expect=[(1, 'Asha', 80000, 2), (2, 'Ravi', 15000, 1), (3, 'Meena', 90000, 1), (4, 'John', 5000, 1), (5, 'Zara', 120000, 1)])
Q('b2', 'bank26', """-- R2. Cities whose customers hold more than ₹1,00,000 in total (GROUP BY + HAVING)
SELECT c.City, COUNT(DISTINCT c.CustomerID) AS Customers, SUM(a.Balance) AS TotalDeposits
FROM   Customer c JOIN Account a ON a.CustomerID = c.CustomerID
GROUP  BY c.City
HAVING SUM(a.Balance) > 100000;""", expect=[('Delhi', 2, 170000), ('Mumbai', 2, 135000)])
Q('b3', 'bank26', """-- R3. Risky customers: total loan exceeds total balance (sub-queries in FROM)
SELECT c.Name, l.TotalLoan, COALESCE(a.TotalBal, 0) AS TotalBalance
FROM   Customer c
JOIN   (SELECT CustomerID, SUM(Amount)  AS TotalLoan FROM Loan    GROUP BY CustomerID) l ON l.CustomerID = c.CustomerID
LEFT JOIN (SELECT CustomerID, SUM(Balance) AS TotalBal FROM Account GROUP BY CustomerID) a ON a.CustomerID = c.CustomerID
WHERE  l.TotalLoan > COALESCE(a.TotalBal, 0);""",
  expect=[('Ravi', 40000, 15000), ('John', 35000, 5000), ('Kiran', 30000, 0)])
Q('b4', 'bank26', """-- R4. Depositors who have never taken a loan (NOT EXISTS)
SELECT DISTINCT c.Name
FROM   Customer c JOIN Account a ON a.CustomerID = c.CustomerID
WHERE  NOT EXISTS (SELECT * FROM Loan l WHERE l.CustomerID = c.CustomerID);""", expect=[('Asha',), ('Zara',)])
Q('b5', 'bank26', """-- R5. Account(s) with the highest balance and the owner (scalar sub-query)
SELECT a.AccountNo, c.Name, a.Balance
FROM   Account a JOIN Customer c ON c.CustomerID = a.CustomerID
WHERE  a.Balance = (SELECT MAX(Balance) FROM Account);""", expect=[(1006, 'Zara', 120000)])
Q('b6', 'bank26', """-- R6. Customers whose loan is above the average loan amount (correlated / non-correlated)
SELECT c.Name, l.LoanID, l.Amount
FROM   Loan l JOIN Customer c ON c.CustomerID = l.CustomerID
WHERE  l.Amount > (SELECT AVG(Amount) FROM Loan);""", expect=[('Ravi', 1, 40000), ('Kiran', 5, 30000)])

# =========================================================================== Mid-sem Sep 2024 Q5(a) + Summer mid-sem Q5(a)
D['nsut'] = """
CREATE TABLE STUDENT(student_id INT PRIMARY KEY, student_name TEXT, age INT, gender TEXT, city TEXT, major TEXT);
CREATE TABLE FACULTY(faculty_id INT PRIMARY KEY, faculty_name TEXT, department TEXT, position TEXT, salary INT);
CREATE TABLE COURSES(course_id TEXT PRIMARY KEY, course_name TEXT, faculty_id INT REFERENCES FACULTY, credits INT, semester INT);
CREATE TABLE ENROLLMENT(student_id INT REFERENCES STUDENT, course_id TEXT REFERENCES COURSES, enrollment_date TEXT, grade TEXT);
INSERT INTO FACULTY VALUES (1,'Dr. Rao','Information Technology','Professor',150000),
 (2,'Dr. Sen','Information Technology','Assistant Professor',90000),(3,'Dr. Iyer','Computer Engineering','Professor',140000),
 (4,'Dr. Das','Information Technology','Associate Professor',110000);
INSERT INTO COURSES VALUES ('C1','Data Structures',1,5,3),('C2','Database Management System',2,4,3),('C3','Discrete Maths',3,4,3),
 ('C4','Computer Networks',1,5,5),('C5','Operating Systems',3,5,3),('C6','Web Technology',4,3,5);
INSERT INTO STUDENT VALUES (1,'Aman',19,'M','Delhi','Information Technology'),(2,'Bina',20,'F','Noida','Information Technology'),
 (3,'Chirag',21,'M','Delhi','Computer Engineering'),(4,'Divya',19,'F','Delhi','Information Technology'),
 (5,'Eklavya',22,'M','Pune','Information Technology');
INSERT INTO ENROLLMENT VALUES (1,'C1','2024-08-01','A'),(1,'C2','2024-08-01','B'),(1,'C3','2024-08-02','A'),
 (2,'C1','2024-08-01','B'),(2,'C2','2024-08-03','A'),(2,'C4','2024-08-03','A'),
 (3,'C1','2024-08-01','C'),(3,'C2','2024-08-01','B'),(3,'C3','2024-08-01','B'),(3,'C5','2024-08-01','A'),
 (4,'C1','2024-08-02','A'),(4,'C2','2024-08-02','A'),(4,'C5','2024-08-02','B'),(5,'C1','2024-08-05','B');
"""
Q('n1', 'nsut', """SELECT s.student_id, s.student_name
FROM   STUDENT s
JOIN   ENROLLMENT e ON e.student_id = s.student_id
JOIN   COURSES c    ON c.course_id  = e.course_id
WHERE  s.major = 'Information Technology'
AND    c.semester = 3
GROUP  BY s.student_id, s.student_name
HAVING COUNT(DISTINCT c.course_id) >= 3;""", expect=[(1, 'Aman'), (4, 'Divya')])
Q('n2', 'nsut', """SELECT f.faculty_name, c.course_name
FROM   FACULTY f JOIN COURSES c ON c.faculty_id = f.faculty_id
WHERE  c.credits > 4
AND    f.department = 'Information Technology';""",
  expect=[('Dr. Rao', 'Data Structures'), ('Dr. Rao', 'Computer Networks')])
Q('n3', 'nsut', """SELECT s.gender, ROUND(AVG(s.age), 2) AS avg_age
FROM   STUDENT s
JOIN   ENROLLMENT e ON e.student_id = s.student_id
JOIN   COURSES c    ON c.course_id  = e.course_id
WHERE  c.course_name = 'Data Structures'
GROUP  BY s.gender;""", expect=[('F', 19.5), ('M', 20.67)])
Q('n4', 'nsut', """SELECT f.faculty_name
FROM   FACULTY f
WHERE  f.faculty_id NOT IN (SELECT c.faculty_id FROM COURSES c
                            WHERE c.semester = 3 AND c.faculty_id IS NOT NULL);""", expect=[('Dr. Das',)])
Q('n1b', 'nsut', """SELECT s.student_id, s.student_name
FROM   STUDENT s
JOIN   ENROLLMENT e ON e.student_id = s.student_id
JOIN   COURSES c    ON c.course_id  = e.course_id
WHERE  s.major = 'Information Technology' AND c.semester = 3
GROUP  BY s.student_id, s.student_name
HAVING COUNT(DISTINCT c.course_id) >= 2;""", expect=[(1, 'Aman'), (2, 'Bina'), (4, 'Divya')])
Q('n3b', 'nsut', """SELECT s.gender, ROUND(AVG(s.age), 2) AS avg_age
FROM   STUDENT s
JOIN   ENROLLMENT e ON e.student_id = s.student_id
JOIN   COURSES c    ON c.course_id  = e.course_id
WHERE  c.course_name = 'Database Management System'
GROUP  BY s.gender;""", expect=[('F', 19.5), ('M', 20.0)])

# =========================================================================== Summer mid-sem Q4(a) — data given in the paper
D['sm4'] = """
CREATE TABLE EMPLOYEE(emp_id TEXT PRIMARY KEY, emp_name TEXT, dept_id TEXT, salary INT);
CREATE TABLE DEPARTMENT(dept_id TEXT PRIMARY KEY, dept_name TEXT);
INSERT INTO EMPLOYEE VALUES ('E1','Rahul','D1',60000),('E2','Nitin','D2',45000),('E3','Amit','D3',75000),('E4','Priya','D4',55000);
INSERT INTO DEPARTMENT VALUES ('D1','IT'),('D2','HR'),('D3','Finance');
"""
Q('sm1', 'sm4', """SELECT E.emp_name, D.dept_name
FROM   EMPLOYEE E
INNER JOIN DEPARTMENT D ON E.dept_id = D.dept_id;""",
  expect=[('Rahul', 'IT'), ('Nitin', 'HR'), ('Amit', 'Finance')])
Q('sm2', 'sm4', """SELECT emp_id, emp_name, salary
FROM   EMPLOYEE
WHERE  salary > (SELECT AVG(salary) FROM EMPLOYEE);      -- AVG = 58750""",
  expect=[('E1', 'Rahul', 60000), ('E3', 'Amit', 75000)])
Q('sm3', 'sm4', """SELECT E.emp_id, E.emp_name, E.dept_id, E.salary
FROM   EMPLOYEE E
WHERE  E.salary = (SELECT MAX(E2.salary)
                   FROM   EMPLOYEE E2
                   WHERE  E2.dept_id = E.dept_id);""",
  expect=[('E1', 'Rahul', 'D1', 60000), ('E2', 'Nitin', 'D2', 45000), ('E3', 'Amit', 'D3', 75000), ('E4', 'Priya', 'D4', 55000)])

# =========================================================================== Mid-sem 2025
D['m25'] = """
CREATE TABLE Customers(customer_id INT PRIMARY KEY, name TEXT, email TEXT, city TEXT, join_date TEXT);
CREATE TABLE Orders(order_id INT PRIMARY KEY, customer_id INT REFERENCES Customers, order_date TEXT, total_amount INT);
INSERT INTO Customers VALUES (1,'Asha','asha@x.in','Delhi','2023-01-01'),(2,'Ravi','ravi@x.in','Pune','2023-05-05'),
 (3,'Meena','meena@x.in','Delhi','2024-02-02'),(4,'John','john@x.in','Goa','2024-03-03');
INSERT INTO Orders VALUES (1,1,'2025-04-02',5000),(2,1,'2025-05-10',6000),(3,1,'2025-07-01',4500),(4,1,'2025-08-20',5500),
 (5,2,'2025-04-01',500),(6,2,'2025-05-01',700),(7,2,'2025-06-01',600),(8,2,'2025-07-01',800),(9,2,'2025-08-01',400),
 (10,3,'2025-06-11',9000),(11,3,'2025-07-12',8000),(12,3,'2025-08-13',7000),
 (13,4,'2024-12-01',5000),(14,4,'2025-04-01',6000),(15,4,'2025-05-01',6000),(16,4,'2025-06-01',6000);
"""
Q('m25a', 'm25', """SELECT c.name
FROM   Customers c
JOIN   Orders o ON o.customer_id = c.customer_id
WHERE  o.order_date >= CURRENT_DATE - INTERVAL 6 MONTH       -- last 6 months (MySQL)
GROUP  BY c.customer_id, c.name
HAVING COUNT(*) > 3
AND    AVG(o.total_amount) > (SELECT AVG(total_amount) FROM Orders);""",
  run="""SELECT c.name FROM Customers c JOIN Orders o ON o.customer_id = c.customer_id
WHERE o.order_date >= date('2025-09-15', '-6 months')
GROUP BY c.customer_id, c.name HAVING COUNT(*) > 3 AND AVG(o.total_amount) > (SELECT AVG(total_amount) FROM Orders)""",
  expect=[('Asha',)], cap='Output on the test data (today taken as 15-Sep-2025; overall average = 4437.5)')

D['fb'] = """
CREATE TABLE Users(user_id INT PRIMARY KEY, user_name VARCHAR(50), email VARCHAR(100));
CREATE TABLE Posts(post_id INT PRIMARY KEY, user_id INT REFERENCES Users, content VARCHAR(500), likes_count INT);
INSERT INTO Users VALUES (1,'asha','asha@facebook.com'),(2,'ravi','ravi@gmail.com'),(3,'meena','meena@facebook.com'),
 (4,'john','john@facebook.com');
INSERT INTO Posts VALUES (11,1,'My travel diary: Ladakh',500),(12,1,'travel for work to Pune',900),(13,2,'travel vlog Goa',800),
 (14,3,'Weekend travel plans',150),(15,3,'office work',50),(16,4,'Travel tips for students',400),(17,1,'Lunch',20);
"""
Q('fb1', 'fb', """SELECT u.user_name, u.email, p.post_id, p.likes_count
FROM   Users u
JOIN   Posts p ON p.user_id = u.user_id
WHERE  p.content LIKE '%travel%'
AND    p.content NOT LIKE '%work%'
AND    u.email LIKE '%@facebook.com'
AND    p.likes_count > (SELECT AVG(likes_count) FROM Posts);   -- average over ALL posts""",
  expect=[('asha', 'asha@facebook.com', 11, 500)], cap='Output on the test data (average likes = 402.86)')

# =========================================================================== Mid-sem 2025 Q5(a): Loan ÷ Borrower
D['lb'] = """
CREATE TABLE Loan(loan_number TEXT, branch_name TEXT, amount INT);
CREATE TABLE Borrower(customer_name TEXT, loan_num TEXT);
INSERT INTO Loan VALUES ('L11','Banjara Hills',90000),('L14','Kondapur',50000),('L15','SR Nagar',40000),('L22','SR Nagar',25000),
 ('L23','Balanagar',80000),('L25','Kondapur',70000),('L19','SR Nagar',65000);
INSERT INTO Borrower VALUES ('Anand','L11'),('Karteek','L11'),('Karteek','L14'),('Ankita','L15'),('Gopal','L19'),
 ('Karteek','L22'),('Karteek','L23'),('Sunil','L23'),('Sunil','L25');
"""
A('lb1', 'lb', r"\pi_{branch\_name, customer\_name}(Loan \join Borrower) \div \pi_{branch\_name}(Loan)",
  lambda D: D['Loan'].nat(D['Borrower'].ren(names=['customer_name', 'loan_number'])).proj('branch_name', 'customer_name')
  .div(D['Loan'].proj('branch_name')), expect=[('Karteek',)],
  cap='Result (joining on loan number): 1 tuple')
A('lb_join', 'lb', r"Loan \join Borrower", lambda D: D['Loan'].nat(D['Borrower'].ren(names=['customer_name', 'loan_number'])),
  cap='Loan ⋈ Borrower (loan_number = loan_num): 9 tuples')
A('lb_lit', 'lb', r"\pi_{branch\_name, customer\_name}(Loan \x Borrower) \div \pi_{branch\_name}(Loan)",
  lambda D: D['Loan'].x(D['Borrower']).proj('branch_name', 'customer_name').div(D['Loan'].proj('branch_name')),
  expect=[('Anand',), ('Karteek',), ('Ankita',), ('Gopal',), ('Sunil',)],
  cap='Literal reading (no common attribute ⇒ ⋈ = ×): 5 tuples')

# =========================================================================== Mid-sem 2024 Q4(a)
D['m24'] = """
CREATE TABLE department(dept_id INT, dept_name TEXT);
CREATE TABLE student(roll_no INT, name TEXT, dept_id INT);
INSERT INTO department VALUES (1,'Mathematics');
INSERT INTO department VALUES (2,'Physics');
INSERT INTO student VALUES (1,'Navin',1);
INSERT INTO student VALUES (2,'Mukesh',2);
INSERT INTO student VALUES (3,'Gita',1);
"""
Q('m24a', 'm24', "SELECT * FROM student, department;",
  cap='Output: 6 rows × 5 columns (3 students × 2 departments)', sort=False)
import sqlite3 as _sq  # noqa: E402
try:
    data.conn('m24').execute('SELECT * FROM student UNION SELECT * FROM department')
    raise AssertionError('union should fail')
except _sq.OperationalError as _e:
    M24_ERR = str(_e)

# =========================================================================== Mid-sem 2026 train
_p = [(1, 'Arjun', 34, 'M', 'Delhi'), (2, 'Bela', 28, 'F', 'Delhi'), (3, 'Chetna', 45, 'F', 'Delhi'), (4, 'Deepak', 52, 'M', 'Mumbai'),
      (5, 'Elena', 23, 'F', 'Mumbai'), (6, 'Farhan', 31, 'M', 'Mumbai'), (7, 'Gopi', 40, 'M', 'Kolkata'), (8, 'Hema', 36, 'F', 'Kolkata')]
_trains = [(12951, 'Mumbai Rajdhani', 'Delhi', 'Mumbai', 1384), (12002, 'Bhopal Shatabdi', 'Delhi', 'Bhopal', 702),
           (12301, 'Howrah Rajdhani', 'Delhi', 'Howrah', 1447)]
_b = []
_fares = {12951: 8200, 12002: 1500, 12301: 4600}
_bid = 1
_plan = [(1, 12951, 4), (2, 12002, 3), (3, 12301, 2), (1, 12301, 2), (2, 12951, 1),     # Delhi: 12 bookings
         (4, 12951, 5), (5, 12002, 3), (6, 12951, 3),                                   # Mumbai: 11 bookings
         (7, 12301, 4), (8, 12002, 3)]                                                 # Kolkata: 7 bookings
for pid, tno, k in _plan:
    for i in range(k):
        fare = _fares[tno] + 100 * i
        _b.append((_bid, pid, tno, f'2026-0{1 + i % 8}-1{i}', '2A' if fare > 3000 else 'CC', fare, 'Confirmed'))
        _bid += 1
_b.append((_bid, 3, 12301, '2026-02-14', '1A', 15000, 'Confirmed'))   # the single highest fare (Delhi → 13 bookings)
D['train'] = ("CREATE TABLE TRAIN(TrainNo INT PRIMARY KEY, TrainName TEXT, Source TEXT, Destination TEXT, Distance INT);\n"
              "CREATE TABLE PASSENGER(PassengerID INT PRIMARY KEY, PassengerName TEXT, Age INT, Gender TEXT, City TEXT);\n"
              "CREATE TABLE BOOKING(BookingID INT PRIMARY KEY, PassengerID INT REFERENCES PASSENGER, TrainNo INT REFERENCES TRAIN,"
              " JourneyDate TEXT, Class TEXT, Fare INT, Status TEXT);\n" +
              ''.join(f"INSERT INTO TRAIN VALUES {t!r};\n" for t in _trains) +
              ''.join(f"INSERT INTO PASSENGER VALUES {p!r};\n" for p in _p) +
              ''.join(f"INSERT INTO BOOKING VALUES {b!r};\n" for b in _b))
# independent expected values computed in Python
_rev = {}
for b in _b:
    _rev[b[2]] = _rev.get(b[2], 0) + b[5]
_city = {}
for b in _b:
    c = [p for p in _p if p[0] == b[1]][0][4]
    _city[c] = _city.get(c, 0) + 1
Q('t1', 'train', """SELECT DISTINCT P.PassengerName
FROM   PASSENGER P JOIN BOOKING B ON B.PassengerID = P.PassengerID
WHERE  B.Fare = (SELECT MAX(Fare) FROM BOOKING);""", expect=[('Chetna',)])
Q('t2', 'train', """SELECT TrainNo, SUM(Fare) AS Revenue
FROM   BOOKING
GROUP  BY TrainNo
HAVING SUM(Fare) > 100000;""", expect=[(k, v) for k, v in _rev.items() if v > 100000])
Q('t3', 'train', """SELECT P.City, COUNT(*) AS NumBookings
FROM   PASSENGER P JOIN BOOKING B ON B.PassengerID = P.PassengerID
GROUP  BY P.City
HAVING COUNT(*) > 10;""", expect=[(k, v) for k, v in _city.items() if v > 10])
Q('t4', 'train', """SELECT B.BookingID, B.PassengerID, B.Fare
FROM   BOOKING B
WHERE  B.Fare > (SELECT AVG(B2.Fare) FROM BOOKING B2 WHERE B2.PassengerID = B.PassengerID);""",
  cap='Output on the test data — bookings costlier than that passenger’s own average fare')
TRAIN_REV = _rev
TRAIN_CITY = _city

# =========================================================================== Mid-sem 2021 Worker / Title
D['wk'] = """
CREATE TABLE Worker(Worker_Id INT PRIMARY KEY, First_name TEXT, salary INT, joining_date TEXT, department TEXT);
CREATE TABLE Title(Worker_ref_id INT REFERENCES Worker(Worker_Id) ON DELETE CASCADE, Worker_title TEXT, affected_from TEXT);
INSERT INTO Worker VALUES (1,'Monika',100000,'2021-02-20','HR'),(2,'Niharika',80000,'2021-06-11','Admin'),
 (3,'Vishal',300000,'2022-07-20','HR'),(4,'Amitabh',500000,'2021-02-20','Admin'),(5,'Vivek',500000,'2022-06-11','Admin'),
 (6,'Vipul',200000,'2021-06-11','Account'),(7,'Satish',75000,'2021-01-20','Account'),(8,'Geetika',90000,'2022-08-11','Admin'),
 (9,'Rahul',80000,'2022-03-01','HR');
INSERT INTO Title VALUES (1,'Manager','2022-02-20'),(2,'Executive','2021-06-11'),(8,'Executive','2022-08-11'),
 (5,'Manager','2022-06-11'),(4,'Asst. Manager','2022-06-11'),(7,'Executive','2021-06-11'),(6,'Lead','2021-06-11'),
 (3,'Lead','2022-07-20'),(3,'Manager','2023-01-01');
"""
Q('w1', 'wk', """SELECT W1.Worker_Id, W1.First_name, W1.salary
FROM   Worker W1
WHERE  EXISTS (SELECT * FROM Worker W2
               WHERE W2.salary = W1.salary AND W2.Worker_Id <> W1.Worker_Id)
ORDER  BY W1.salary;""", sort=False,
  expect=[(2, 'Niharika', 80000), (9, 'Rahul', 80000), (4, 'Amitabh', 500000), (5, 'Vivek', 500000)])
Q('w2', 'wk', """SELECT W.department, W.First_name, W.salary
FROM   Worker W
WHERE  W.salary = (SELECT MAX(X.salary) FROM Worker X WHERE X.department = W.department);""",
  expect=[('HR', 'Vishal', 300000), ('Admin', 'Amitabh', 500000), ('Admin', 'Vivek', 500000), ('Account', 'Vipul', 200000)])
Q('w3', 'wk', """SELECT W.First_name
FROM   Worker W JOIN Title T ON T.Worker_ref_id = W.Worker_Id
WHERE  T.Worker_title = 'Manager'
AND    W.joining_date > '2022-06-20';""", expect=[('Vishal',)])
Q('w4', 'wk', """SELECT First_name, salary
FROM   Worker
WHERE  salary BETWEEN 50000 AND 100000;""",
  expect=[('Monika', 100000), ('Niharika', 80000), ('Satish', 75000), ('Geetika', 90000), ('Rahul', 80000)])
A('wra1', 'wk', r"\pi_{Worker\_Id}(\sigma_{department='HR'}(Worker) \join_{Worker\_Id = Worker\_ref\_id} \sigma_{Worker\_title='Manager'}(Title))",
  lambda D: D['Worker'].sel(lambda t: t.department == 'HR').theta(D['Title'].sel(lambda t: t.Worker_title == 'Manager'),
                                                                   lambda t: t.Worker_Id == t.Worker_ref_id).proj('Worker_Id'),
  expect=[(1,), (3,)])
A('wra2', 'wk', r"\pi_{Worker\_Id, First\_name, salary, joining\_date, department}(Worker \join_{Worker\_Id = Worker\_ref\_id} \sigma_{Worker\_title='Manager'}(Title))",
  lambda D: D['Worker'].theta(D['Title'].sel(lambda t: t.Worker_title == 'Manager'), lambda t: t.Worker_Id == t.Worker_ref_id)
  .proj('Worker_Id', 'First_name', 'salary', 'joining_date', 'department'),
  expect=[(1, 'Monika', 100000, '2021-02-20', 'HR'), (3, 'Vishal', 300000, '2022-07-20', 'HR'), (5, 'Vivek', 500000, '2022-06-11', 'Admin')])

# =========================================================================== End-sem 2023 Suppliers / Parts / Catalog
D['sp'] = """
CREATE TABLE Suppliers(sid INTEGER PRIMARY KEY, sname VARCHAR(10), address VARCHAR(20));
CREATE TABLE Parts(pid INTEGER PRIMARY KEY, pname VARCHAR(10), color VARCHAR(10));
CREATE TABLE Catalog(sid INTEGER REFERENCES Suppliers, pid INTEGER REFERENCES Parts, cost REAL, PRIMARY KEY(sid, pid));
INSERT INTO Suppliers VALUES (1,'Acme','221 Packer Ave'),(2,'Bolt','12 MG Road'),(3,'Crest','5 Ring Rd'),(4,'Dyna','9 Lake View'),
 (50,'Zenith','1 Mall Rd'),(6,'Fresh','221 Packer Ave');
INSERT INTO Parts VALUES (1,'bolt','red'),(2,'nut','red'),(3,'screw','green'),(4,'washer','black'),(5,'rivet','black'),(6,'gear','blue');
INSERT INTO Catalog VALUES (1,4,10),(1,5,12),(2,1,5),(2,2,6),(2,3,7),(3,1,8),(4,3,9),(4,4,3),(50,1,4),(50,2,5),(50,6,15);
"""
Q('sp2', 'sp', """SELECT S.sname, COUNT(*) AS num_parts
FROM   Suppliers S JOIN Catalog C ON C.sid = S.sid
WHERE  NOT EXISTS (SELECT *                                     -- no non-black part supplied
                   FROM   Catalog C2 JOIN Parts P ON P.pid = C2.pid
                   WHERE  C2.sid = S.sid AND P.color <> 'black')
GROUP  BY S.sid, S.sname;""", expect=[('Acme', 2)])
Q('sp2b', 'sp', """SELECT S.sname, COUNT(*) AS num_parts
FROM   Suppliers S
JOIN   Catalog C ON C.sid = S.sid
JOIN   Parts   P ON P.pid = C.pid
GROUP  BY S.sid, S.sname
HAVING SUM(CASE WHEN P.color = 'black' THEN 0 ELSE 1 END) = 0;   -- every part black""", expect=[('Acme', 2)])
Q('sp4', 'sp', """SELECT C.pid, C.cost
FROM   Catalog C
WHERE  C.sid = 50;""", expect=[(1, 4.0), (2, 5.0), (6, 15.0)])
V('sp_chk', D['sp'], [
    ("ALTER TABLE Parts RENAME TO Parts_old; CREATE TABLE Parts(pid INTEGER PRIMARY KEY, pname VARCHAR(10), color VARCHAR(10) "
     "CHECK (color IN ('green','red','blue','black'))); INSERT INTO Parts SELECT * FROM Parts_old;", 'ok',
     '(SQLite cannot ADD CONSTRAINT, so the table is rebuilt — in Oracle/MySQL use the one-line ALTER TABLE)'),
    ("INSERT INTO Parts VALUES (7, 'spring', 'yellow');", 'err', 'yellow violates the CHECK'),
    ("INSERT INTO Parts VALUES (8, 'clip', 'blue');", 'ok', 'allowed colour'),
])
_redS = lambda D: D['Parts'].sel(lambda t: t.color == 'red').nat(D['Catalog']).proj('sid')
A('sp_ra1', 'sp', r"\pi_{sname}(\sigma_{color='red'}(Parts) \join Catalog \join Suppliers)",
  lambda D: D['Parts'].sel(lambda t: t.color == 'red').nat(D['Catalog']).nat(D['Suppliers']).proj('sname'),
  expect=[('Bolt',), ('Crest',), ('Zenith',)])
A('sp_ra2', 'sp', r"\pi_{sid}(\sigma_{color='red' \or color='green'}(Parts) \join Catalog)",
  lambda D: D['Parts'].sel(lambda t: t.color in ('red', 'green')).nat(D['Catalog']).proj('sid'),
  expect=[(2,), (3,), (4,), (50,)])
A('sp_ra3', 'sp', r"\pi_{sid}(\sigma_{color='red'}(Parts) \join Catalog) \cup \pi_{sid}(\sigma_{address='221 Packer Ave'}(Suppliers))",
  lambda D: _redS(D) | D['Suppliers'].sel(lambda t: t.address == '221 Packer Ave').proj('sid'),
  expect=[(1,), (2,), (3,), (6,), (50,)])
A('sp_ra4', 'sp', r"\pi_{sid, pid}(Catalog) \div \pi_{pid}(\sigma_{color='red'}(Parts))",
  lambda D: D['Catalog'].proj('sid', 'pid').div(D['Parts'].sel(lambda t: t.color == 'red').proj('pid')),
  expect=[(2,), (50,)])

# =========================================================================== End-sem (year not printed) employee/works  + bank RA
D['comp'] = """
CREATE TABLE employee(ID INT PRIMARY KEY, person_name TEXT, street TEXT, city TEXT);
CREATE TABLE company(company_name TEXT PRIMARY KEY, city TEXT);
CREATE TABLE works(ID INT PRIMARY KEY REFERENCES employee, company_name TEXT REFERENCES company, salary INT);
CREATE TABLE manages(ID INT PRIMARY KEY REFERENCES employee, manager_id INT REFERENCES employee);
INSERT INTO employee VALUES (1,'Aman','MG Rd','Delhi'),(2,'Bela','Park St','Kolkata'),(3,'Chirag','Link Rd','Mumbai'),
 (4,'Dev','Lake Rd','Pune'),(5,'Esha','Ring Rd','Delhi'),(6,'Farid','Mall Rd','Shimla'),(7,'Gita','Hill Rd','Ooty');
INSERT INTO company VALUES ('First Bank Corporation','Delhi'),('Small Bank Corporation','Pune'),('Infotech','Bengaluru');
INSERT INTO works VALUES (1,'First Bank Corporation',50000),(2,'First Bank Corporation',70000),(3,'Small Bank Corporation',40000),
 (4,'Small Bank Corporation',65000),(5,'Infotech',80000),(6,'Infotech',60000);
"""
Q('cw1', 'comp', """SELECT e.ID
FROM   employee e
WHERE  e.ID NOT IN (SELECT w.ID FROM works w
                    WHERE  w.company_name = 'First Bank Corporation');""", expect=[(3,), (4,), (5,), (6,), (7,)])
Q('cw2', 'comp', """SELECT w.ID
FROM   works w
WHERE  w.salary > ALL (SELECT w2.salary FROM works w2
                       WHERE  w2.company_name = 'Small Bank Corporation');""",
  run="SELECT w.ID FROM works w WHERE w.salary > (SELECT MAX(w2.salary) FROM works w2 WHERE w2.company_name = 'Small Bank Corporation')",
  expect=[(2,), (5,)])
D['bankra'] = """
CREATE TABLE loan(loan_number TEXT, branch_name TEXT, amount INT);
CREATE TABLE account(account_number TEXT, branch_name TEXT, balance INT);
CREATE TABLE depositor(ID INT, account_number TEXT);
INSERT INTO loan VALUES ('L-11','Round Hill',900),('L-14','Downtown',15000),('L-15','Perryridge',15000),('L-16','Perryridge',13000),
 ('L-17','Downtown',1000),('L-23','Redwood',20000),('L-93','Mianus',500);
INSERT INTO account VALUES ('A-101','Uptown',25000),('A-102','Uptown',18000),('A-201','Downtown',30000),('A-215','Uptown',19000);
INSERT INTO depositor VALUES (101,'A-101'),(102,'A-102'),(103,'A-201'),(104,'A-215'),(105,'A-101');
"""
A('bk1', 'bankra', r"\pi_{loan\_number}(\sigma_{amount > 11000}(loan))",
  lambda D: D['loan'].sel(lambda t: t.amount > 11000).proj('loan_number'),
  expect=[('L-14',), ('L-15',), ('L-16',), ('L-23',)])
A('bk2', 'bankra', r"\pi_{ID}(\sigma_{branch\_name='Uptown' \and balance > 18000}(account) \join depositor)",
  lambda D: D['account'].sel(lambda t: t.branch_name == 'Uptown' and t.balance > 18000).nat(D['depositor']).proj('ID'),
  expect=[(101,), (104,), (105,)])

# =========================================================================== End-sem 2022 Worker / Project / Assign
D['wp'] = """
CREATE TABLE Worker(empid INT PRIMARY KEY, empname TEXT, empmagr INT, dept TEXT, birthdate TEXT, hiredate TEXT, salary INT);
CREATE TABLE Project(projno INT PRIMARY KEY, projname TEXT, projmgr INT, budget INT, startdate TEXT, duration INT);
CREATE TABLE Assign(projno INT, empid INT, hoursassign INT, rating INT, PRIMARY KEY(projno, empid));
INSERT INTO Worker VALUES (1,'Arun',NULL,'IT','1980-01-01','2010-05-01',150000),(2,'Bela',1,'IT','1990-02-02','2015-06-01',90000),
 (3,'Chand',1,'IT','1992-03-03','2016-07-01',80000),(4,'Dina',2,'IT','1995-04-04','2019-08-01',60000),
 (5,'Esha',2,'IT','1996-05-05','2020-09-01',55000),(6,'Farid',1,'IT','1993-06-06','2018-10-01',70000);
INSERT INTO Project VALUES (10,'Alpha',1,500000,'2022-02-01',6),(20,'Beta',2,300000,'2022-03-15',4),(30,'Gamma',1,200000,'2022-02-01',3);
INSERT INTO Assign VALUES (10,2,40,4),(10,4,30,5),(20,3,25,3),(30,2,20,4),(30,5,35,5);
"""
A('wp1', 'wp', r"\pi_{projname, empname}(\sigma_{startdate='2022-02-01'}(Project) \join Assign \join Worker)",
  lambda D: D['Project'].sel(lambda t: t.startdate == '2022-02-01').nat(D['Assign']).nat(D['Worker']).proj('projname', 'empname'),
  expect=[('Alpha', 'Bela'), ('Alpha', 'Dina'), ('Gamma', 'Bela'), ('Gamma', 'Esha')])


def _wp2(D):
    free = (D['Worker'].proj('empid') - D['Assign'].proj('empid')).nat(D['Worker']).proj('empid', 'empname', 'empmagr')
    mgr = D['Worker'].proj('empid', 'empname').ren(names=['mid', 'manager_name'])
    j = free.ren(names=['empid', 'empname', 'mid']).ljoin(mgr)
    return j.proj('empname', 'manager_name')


A('wp2', 'wp', r"Free \gets (\pi_{empid}(Worker) \minus \pi_{empid}(Assign)) \join Worker \br M \gets \rho_{M(mid, manager\_name)}(\pi_{empid, empname}(Worker)) \br \pi_{empname, manager\_name}(Free \ljoin_{Free.empmagr = M.mid} M)",
  _wp2, expect=[('Arun', None), ('Farid', 'Arun')])
Q('wp1s', 'wp', """SELECT P.projname, W.empname
FROM   Project P
JOIN   Assign  A ON A.projno = P.projno
JOIN   Worker  W ON W.empid  = A.empid
WHERE  P.startdate = DATE '2022-02-01';""",
  run="SELECT P.projname, W.empname FROM Project P JOIN Assign A ON A.projno = P.projno JOIN Worker W ON W.empid = A.empid WHERE P.startdate = '2022-02-01'",
  expect=[('Alpha', 'Bela'), ('Alpha', 'Dina'), ('Gamma', 'Bela'), ('Gamma', 'Esha')])
Q('wp2s', 'wp', """SELECT W.empname, M.empname AS manager_name
FROM   Worker W
LEFT JOIN Worker M ON M.empid = W.empmagr
WHERE  NOT EXISTS (SELECT * FROM Assign A WHERE A.empid = W.empid);""",
  expect=[('Arun', None), ('Farid', 'Arun')])

# =========================================================================== 2025 end-sem Q2(b) Event (calculus) — verified via RA
D['ev'] = """
CREATE TABLE Event(EventId INT, EventName TEXT, Organizer TEXT, EventDept TEXT, Location TEXT, Date TEXT, Emailid TEXT,
  Phone TEXT, Address TEXT);
CREATE TABLE Topic(TopicId INT, EventId INT, TopicTitle TEXT, Date TEXT, TimeDuration TEXT);
CREATE TABLE EminentSpeaker(EventId INT, TopicId INT, SpeakerName TEXT, Institution TEXT, TopicTitle TEXT);
CREATE TABLE Registration(ParticipantId INT, ParticipantName TEXT, EventId INT, ParticipantInstitution TEXT, Fee INT, Category TEXT);
INSERT INTO Event VALUES (1,'5-day workshop on Qiskit','IEEE','IT','APJ Hall','2025-10-06','q@nsut.ac.in','999','Dwarka');
INSERT INTO Topic VALUES (1,1,'Quantum Gates','2025-10-06','3h'),(2,1,'Database Handling','2025-10-08','2h'),
 (3,1,'Qiskit Runtime','2025-10-09','3h');
INSERT INTO EminentSpeaker VALUES (1,1,'ABC','NSUT','Quantum Gates'),(1,2,'PQR','IIT Delhi','Database Handling'),
 (1,3,'ABC','NSUT','Qiskit Runtime');
INSERT INTO Registration VALUES (1,'Ira',1,'NSUT',500,'UG Student'),(2,'Kabir',1,'DTU',800,'PG Student'),
 (3,'Lata',1,'NSUT',800,'PG Student'),(4,'Manu',1,'IIIT',1500,'Faculty');
"""
A('ev_b', 'ev', r"\pi_{TopicTitle}(\sigma_{SpeakerName='ABC' \and Institution='NSUT'}(EminentSpeaker))",
  lambda D: D['EminentSpeaker'].sel(lambda t: t.SpeakerName == 'ABC' and t.Institution == 'NSUT').proj('TopicTitle'),
  expect=[('Quantum Gates',), ('Qiskit Runtime',)])
A('ev_c', 'ev', r"\pi_{Date, SpeakerName}(\sigma_{TopicTitle='Database Handling'}(Topic) \join EminentSpeaker)",
  lambda D: D['Topic'].sel(lambda t: t.TopicTitle == 'Database Handling').nat(D['EminentSpeaker']).proj('Date', 'SpeakerName'),
  expect=[('2025-10-08', 'PQR')])
A('ev_d', 'ev', r"\pi_{ParticipantName}(\sigma_{Category='PG Student'}(Registration))",
  lambda D: D['Registration'].sel(lambda t: t.Category == 'PG Student').proj('ParticipantName'),
  expect=[('Kabir',), ('Lata',)])

# =========================================================================== Mid-sem 2025 Q4(a) DDL — run & test
UNI25 = """CREATE TABLE Department (
  DeptID    VARCHAR(10)  PRIMARY KEY,
  DeptName  VARCHAR(50)  NOT NULL,
  HOD       VARCHAR(50)
);
CREATE TABLE Student (
  StudentID VARCHAR(10)  PRIMARY KEY,
  Name      VARCHAR(50)  NOT NULL,
  Email     VARCHAR(80)  UNIQUE,
  Phone     VARCHAR(15),
  DeptID    VARCHAR(10),
  FOREIGN KEY (DeptID) REFERENCES Department(DeptID)
);
CREATE TABLE Course (
  CourseID  VARCHAR(10)  PRIMARY KEY,
  Title     VARCHAR(80)  NOT NULL,
  Credits   INT          CHECK (Credits BETWEEN 1 AND 5),
  DeptID    VARCHAR(10)  NOT NULL,
  FOREIGN KEY (DeptID) REFERENCES Department(DeptID)
);
CREATE TABLE Enrollment (
  EnrollID  INT          PRIMARY KEY,
  StudentID VARCHAR(10)  NOT NULL,
  CourseID  VARCHAR(10)  NOT NULL,
  Semester  INT          NOT NULL,
  Grade     CHAR(1)      CHECK (Grade IN ('A','B','C','D','F','I')),
  UNIQUE (StudentID, CourseID, Semester),
  FOREIGN KEY (StudentID) REFERENCES Student(StudentID) ON DELETE CASCADE,
  FOREIGN KEY (CourseID)  REFERENCES Course(CourseID)
);"""
V('uni25', UNI25 + """
INSERT INTO Department VALUES ('IT','Information Technology','Dr. Rao');
INSERT INTO Student VALUES ('S101','Asha','asha@nsut.ac.in','999','IT');
INSERT INTO Course VALUES ('IT301','DBMS',4,'IT');""", [
    ("INSERT INTO Enrollment VALUES (1,'S101','IT301',3,'A');", 'ok', 'valid'),
    ("INSERT INTO Enrollment VALUES (2,'S101','IT301',3,'B');", 'err', 'UNIQUE(StudentID, CourseID, Semester) — same course twice in one semester'),
    ("INSERT INTO Enrollment VALUES (3,'S101','IT301',5,'E');", 'err', 'CHECK — grade E not allowed'),
    ("INSERT INTO Course VALUES ('IT999','Thesis',6,'IT');", 'err', 'CHECK — credits must be 1..5'),
    ("INSERT INTO Student VALUES ('S102','Ravi','asha@nsut.ac.in','888','IT');", 'err', 'UNIQUE — email already used'),
    ("DELETE FROM Student WHERE StudentID = 'S101';", 'ok', 'ON DELETE CASCADE removes S101’s enrollment rows too'),
], after='SELECT COUNT(*) AS enrollment_rows_left FROM Enrollment')

# =========================================================================== Summer mid-sem Q3(a) DDL — run & test
SM3 = """CREATE TABLE STUDENT (
  StudentID   INT          PRIMARY KEY,                       -- entity integrity + key
  Name        VARCHAR(50)  NOT NULL,
  Age         INT          CHECK (Age >= 16),
  Department  VARCHAR(30)
);
CREATE TABLE COURSE (
  CourseID    VARCHAR(10)  PRIMARY KEY,
  CourseName  VARCHAR(60)  NOT NULL UNIQUE,                   -- no two courses with same name
  Credits     INT          NOT NULL CHECK (Credits BETWEEN 1 AND 5)
);
CREATE TABLE ENROLLMENT (
  StudentID   INT          NOT NULL,
  CourseID    VARCHAR(10)  NOT NULL,
  Marks       INT          CHECK (Marks BETWEEN 0 AND 100),
  PRIMARY KEY (StudentID, CourseID),                          -- composite key
  FOREIGN KEY (StudentID) REFERENCES STUDENT(StudentID),
  FOREIGN KEY (CourseID)  REFERENCES COURSE(CourseID)
);"""
V('sm3', SM3 + """
INSERT INTO STUDENT VALUES (1,'Asha',19,'IT');
INSERT INTO COURSE VALUES ('C1','DBMS',4);""", [
    ("INSERT INTO STUDENT VALUES (1,'Ravi',20,'CSE');", 'err', 'PRIMARY KEY — duplicate StudentID'),
    ("INSERT INTO STUDENT VALUES (NULL,'Ravi',20,'CSE');", 'err', 'PRIMARY KEY — NULL id (entity integrity)'),
    ("INSERT INTO STUDENT VALUES (2,NULL,20,'CSE');", 'err', 'NOT NULL — name missing'),
    ("INSERT INTO STUDENT VALUES (3,'Kid',12,'CSE');", 'err', 'CHECK — age below 16'),
    ("INSERT INTO COURSE VALUES ('C2','DBMS',3);", 'err', 'UNIQUE — course name repeated'),
    ("INSERT INTO ENROLLMENT VALUES (1,'C9',80);", 'err', 'FOREIGN KEY — course C9 does not exist'),
    ("INSERT INTO ENROLLMENT VALUES (1,'C1',180);", 'err', 'CHECK — marks above 100'),
    ("INSERT INTO ENROLLMENT VALUES (1,'C1',88);", 'ok', 'valid'),
    ("INSERT INTO ENROLLMENT VALUES (1,'C1',91);", 'err', 'PRIMARY KEY — same student-course pair twice'),
])
# Mid-sem 2021 Q2(c): referential integrity Worker/Title (ON DELETE CASCADE)
V('wk_ri', D['wk'], [
    ("INSERT INTO Title VALUES (42,'Manager','2023-01-01');", 'err', 'no Worker 42 — rejected'),
    ("DELETE FROM Worker WHERE Worker_Id = 3;", 'ok', 'cascade: both Title rows of worker 3 deleted'),
], after='SELECT COUNT(*) AS titles_left FROM Title')
