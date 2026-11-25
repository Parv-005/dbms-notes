"""All ER diagrams of Unit 3.  Each ER(...) registers itself; build.py calls check() on every one
(mapping compared with `expect`, DDL executed in SQLite)."""
from er import ER, End

# ---------------------------------------------------------------- PYQ: End-Sem 2023 Q3(c) (= class notes extended image 1)
e = ER('p23', notation='none', expect=['A(_a1,a2,b1,c1)', 'B(_b1,b2)', 'C(_c1,c2)', 'R3(_b1,_c1)'])
e.entity('A', 120, 120, top=['_a1', 'a2'])
e.entity('B', 520, 120, top=['_b1', 'b2'])
e.entity('C', 320, 330, bottom=['_c1', 'c2'])
e.rel('R1', 320, 120, [End('A', 'N', arrow='rel'), End('B', '1')])
e.rel('R2', 120, 240, [End('A', 'N', arrow='rel'), End('C', '1', via=[(120, 330)])])
e.rel('R3', 520, 240, [End('B', 'M'), End('C', 'N', via=[(520, 330)])])

# ---------------------------------------------------------------- PYQ: End-Sem 2022 Q2(b)
e = ER('p22b', expect=['E1(_m1,m2,n1)', 'E2(_n1,n2)', 'E3(_p1,p2,n1)', 'E4(_p1,_q1,q2)'])
e.entity('E1', 80, 110, top=['_m1', 'm2'])
e.rel('R1', 220, 110, [End('E1', 'N', total=True), End('E2', '1')])
e.entity('E2', 360, 110, top=['_n1', 'n2'])
e.rel('R2', 500, 110, [End('E2', '1'), End('E3', 'N', total=True)])
e.entity('E3', 640, 110, top=['_p1', 'p2'])
e.rel('R3', 640, 230, [End('E3', '1'), End('E4', 'N', total=True)], identifying=True)
e.entity('E4', 640, 340, weak=True, left=['~q1'], right=['q2'])

# ---------------------------------------------------------------- PYQ: End-Sem (no year) Q1(c)
e = ER('pny', notation='none', expect=['E1(_A1,A2)', 'E2(_A1,_A3,A4,A5)', 'E3(_A6,A7)', 'E3_A8(_A6,_A8)', 'E4(_A9,A10)',
                                        'R2(_A1,_A6,D1)', 'R3(_A1,_A9)', 'R4(_A9,_R4b_A9,D2,D3)'])
e.entity('E1', 300, 70, bottom=['_A1', 'A2'])
e.rel('R1', 520, 70, [End('E1', '1'), End('E2', 'N', total=True)], identifying=True)
e.entity('E2', 720, 70, weak=True, right=['~A3'], bottom=['A4', 'A5'])
e.rel('R2', 110, 200, [End('E1', 'M', total=True), End('E3', 'N')], right=['D1'])
e.entity('E3', 110, 320, right=['*A8'], bottom=['_A6', 'A7'])
e.rel('R3', 470, 200, [End('E1', 'M', total=True), End('E4', 'N')])
e.entity('E4', 470, 320, left=['_A9'], top=['A10'], at={'A10': (580, 250)})
e.rel('R4', 700, 320, [End('E4', 'M'), End('E4', 'N', role='R4b', via=[(700, 380), (470, 380)])], right=['D2', 'D3'])

# ======================================================================= THEORY EXAMPLES
# attribute types on one entity (class notes p7 + course PDF p45-47)
e = ER('t_attrs', expect=['STUDENT(_roll_no,first_name,middle_name,last_name,dob,email)', 'STUDENT_phone(_roll_no,_phone)'])
e.entity('STUDENT', 330, 150, top=['name(first_name,middle_name,last_name)'], left=['_roll_no', 'dob'],
         right=['*phone', '/age'], bottom=['email'], gap={'top': 40, 'left': 46, 'right': 46, 'bottom': 34})

# relationship set basic: Employee WORKS_FOR Department (course PDF p43)
e = ER('t_rel', expect=['EMPLOYEE(_emp_id,name,dept_id,since)', 'DEPARTMENT(_dept_id,dname)'])
e.entity('EMPLOYEE', 90, 100, top=['_emp_id', 'name'])
e.rel('WORKS_FOR', 330, 100, [End('EMPLOYEE', 'N'), End('DEPARTMENT', '1')], bottom=['since'])
e.entity('DEPARTMENT', 570, 100, top=['_dept_id', 'dname'])

# degree: unary (recursive with roles)
e = ER('t_unary', expect=['EMPLOYEE(_emp_id,name,supervisor_emp_id)'])
e.entity('EMPLOYEE', 120, 120, left=['_emp_id', 'name'])
e.rel('SUPERVISES', 360, 120, [End('EMPLOYEE', '1', role='supervisor', via=[(360, 40), (120, 40)]),
                                End('EMPLOYEE', 'N', role='supervisee', via=[(360, 200), (120, 200)])])

# degree: ternary
e = ER('t_ternary', expect=['SUPPLIER(_s_id,sname)', 'PART(_p_id,pname)', 'PROJECT(_j_id,jname)', 'SUPPLY(_s_id,_p_id,_j_id,quantity)'])
e.entity('SUPPLIER', 110, 110, top=['_s_id', 'sname'])
e.rel('SUPPLY', 360, 110, [End('SUPPLIER', 'M'), End('PART', 'N'), End('PROJECT', 'P')], top=['quantity'], gap={'top': 30})
e.entity('PART', 610, 110, top=['_p_id', 'pname'])
e.entity('PROJECT', 360, 250, left=['_j_id'], right=['jname'])

# three binaries instead of the ternary (for the comparison)
e = ER('t_3bin', notation='label')
e.entity('SUPPLIER', 110, 80)
e.entity('PART', 560, 80)
e.entity('PROJECT', 335, 270)
e.rel('CAN_SUPPLY', 335, 80, [End('SUPPLIER', 'M'), End('PART', 'N')])
e.rel('USES', 470, 190, [End('PROJECT', 'M'), End('PART', 'N')])
e.rel('SUPPLIES', 200, 190, [End('SUPPLIER', 'M'), End('PROJECT', 'N')])

# participation: MANAGES (partial employee, total department) - also 1:1
e = ER('t_part', expect=['EMPLOYEE(_emp_id,name)', 'DEPARTMENT(_dept_id,dname,emp_id,start_date)'])
e.entity('EMPLOYEE', 90, 100, top=['_emp_id', 'name'])
e.rel('MANAGES', 330, 100, [End('EMPLOYEE', '1'), End('DEPARTMENT', '1', total=True)], bottom=['start_date'])
e.entity('DEPARTMENT', 570, 100, top=['_dept_id', 'dname'])

# (min,max) notation on the same schema + works_for
e = ER('t_minmax', notation='minmax')
e.entity('EMPLOYEE', 90, 150)
e.entity('DEPARTMENT', 590, 150)
e.rel('MANAGES', 340, 60, [End('EMPLOYEE', '1', minmax='(0,1)', via=[(90, 60)]), End('DEPARTMENT', '1', total=True, minmax='(1,1)', via=[(590, 60)])])
e.rel('WORKS_FOR', 340, 240, [End('EMPLOYEE', 'N', total=True, minmax='(1,1)', via=[(90, 240)]), End('DEPARTMENT', '1', total=True, minmax='(1,N)', via=[(590, 240)])])

# one relationship in four notations: Chen labels / Korth arrow / Ramakrishnan arrow
for nid, nota, arr in (('t_n_label', 'label', None), ('t_n_korth', 'arrow', None), ('t_n_rama', 'none', 'rel'), ('t_n_mm', 'minmax', None)):
    e = ER(nid, notation=nota)
    e.entity('EMPLOYEE', 90, 60)
    e.rel('WORKS_FOR', 300, 60, [End('EMPLOYEE', 'N', total=True, minmax='(1,1)', arrow=arr),
                                  End('DEPARTMENT', '1', minmax='(0,N)', arrow=False if arr else None)])
    e.entity('DEPARTMENT', 510, 60)

# weak entity: LOAN - PAYMENT (Korth / course PDF p44 'installment')
e = ER('t_weak', expect=['LOAN(_loan_no,amount)', 'PAYMENT(_loan_no,_payment_no,pay_date,pay_amount)'])
e.entity('LOAN', 90, 110, top=['_loan_no', 'amount'])
e.rel('LOAN_PAYMENT', 330, 110, [End('LOAN', '1'), End('PAYMENT', 'N', total=True)], identifying=True)
e.entity('PAYMENT', 580, 110, weak=True, top=['~payment_no', 'pay_date', 'pay_amount'])

# weak entity whose identifying relationship is ternary (2025 Q3b)
e = ER('t_weak3', expect=['APPLICANT(_app_id,name)', 'COMPANY(_cname,city)', 'INTERVIEW(_app_id,_cname,_int_date,result)'])
e.entity('APPLICANT', 100, 100, top=['_app_id', 'name'])
e.entity('COMPANY', 600, 100, top=['_cname', 'city'])
e.rel('INTERVIEWS', 350, 100, [End('APPLICANT', '1'), End('COMPANY', '1'), End('INTERVIEW', 'N', total=True)], identifying=True)
e.entity('INTERVIEW', 350, 240, weak=True, left=['~int_date'], right=['result'])

# specialization: EMPLOYEE -> SECRETARY / TECHNICIAN / ENGINEER (disjoint, partial)
e = ER('t_spec', expect=['EMPLOYEE(_emp_id,name,salary)', 'SECRETARY(_emp_id,typing_speed)', 'TECHNICIAN(_emp_id,tgrade)', 'ENGINEER(_emp_id,eng_type)'])
e.entity('EMPLOYEE', 330, 70, top=['_emp_id', 'name', 'salary'], gap={'top': 30})
e.isa('EMPLOYEE', ['SECRETARY', 'TECHNICIAN', 'ENGINEER'], 330, 170, disjoint=True, total=False)
e.entity('SECRETARY', 120, 270, bottom=['typing_speed'], gap={'bottom': 30})
e.entity('TECHNICIAN', 330, 270, bottom=['tgrade'], gap={'bottom': 30})
e.entity('ENGINEER', 540, 270, bottom=['eng_type'], gap={'bottom': 30})

# overlapping, total: PERSON -> EMPLOYEE / STUDENT  (a TA is both)
e = ER('t_overlap', expect=['PERSON(_pid,name,address,salary,roll_no,is_employee,is_student)'], opts={})
e.entity('PERSON', 300, 70, top=['_pid', 'name', 'address'], gap={'top': 30})
e.isa('PERSON', ['EMPLOYEE', 'STUDENT'], 300, 170, disjoint=False, total=True, method='flags')
e.entity('EMPLOYEE', 160, 270, bottom=['salary'], gap={'bottom': 30})
e.entity('STUDENT', 440, 270, bottom=['roll_no'], gap={'bottom': 30})

# generalization: CAR + TRUCK -> VEHICLE (bottom-up)
e = ER('t_gen')
e.entity('VEHICLE', 300, 70, top=['_vehicle_id', 'price', 'license_plate'], gap={'top': 30})
e.isa('VEHICLE', ['CAR', 'TRUCK'], 300, 170, disjoint=True, total=True)
e.entity('CAR', 160, 270, bottom=['max_speed', 'no_of_passengers'], gap={'bottom': 30})
e.entity('TRUCK', 440, 270, bottom=['no_of_axles', 'tonnage'], gap={'bottom': 30})

# before generalization
e = ER('t_gen0')
e.entity('CAR', 150, 90, top=['_vehicle_id', 'price', 'license_plate'], bottom=['max_speed', 'no_of_passengers'], gap={'top': 30, 'bottom': 30})
e.entity('TRUCK', 560, 90, top=['_vehicle_id', 'price', 'license_plate'], bottom=['no_of_axles', 'tonnage'], gap={'top': 30, 'bottom': 30})

# aggregation 1: course PDF p59 Center-offers-Course, Visitor enquires
e = ER('t_agg1', expect=['CENTER(_center_id,cname)', 'COURSE(_course_id,title)', 'OFFERS(_center_id,_course_id,fee)',
                          'VISITOR(_visitor_id,vname)', 'ENQUIRES(_visitor_id,_center_id,_course_id,enq_date)'])
e.entity('CENTER', 110, 90, top=['_center_id', 'cname'], gap={'top': 44})
e.rel('OFFERS', 330, 90, [End('CENTER', 'M'), End('COURSE', 'N')], bottom=['fee'], gap={'bottom': 18})
e.entity('COURSE', 550, 90, top=['_course_id', 'title'], gap={'top': 44})
e.aggregate('CENTER_COURSE', 'OFFERS', (30, 56, 640, 175))
e.rel('ENQUIRES', 330, 255, [End('CENTER_COURSE', 'N', via=[(330, 175)]), End('VISITOR', 'M')], right=['enq_date'])
e.entity('VISITOR', 330, 370, left=['_visitor_id'], right=['vname'])

# aggregation 2: Korth - EMPLOYEE works_on PROJECT, MANAGER monitors (works_on)
e = ER('t_agg2', expect=['EMPLOYEE(_emp_id,ename)', 'PROJECT(_proj_id,pname)', 'WORKS_ON(_emp_id,_proj_id,hours)',
                          'MANAGER(_mgr_id,mname)', 'MONITORS(_emp_id,_proj_id,mgr_id)'])
e.entity('EMPLOYEE', 110, 90, top=['_emp_id', 'ename'], gap={'top': 44})
e.rel('WORKS_ON', 330, 90, [End('EMPLOYEE', 'M'), End('PROJECT', 'N')], bottom=['hours'], gap={'bottom': 18})
e.entity('PROJECT', 550, 90, top=['_proj_id', 'pname'], gap={'top': 44})
e.aggregate('EMP_PROJ', 'WORKS_ON', (30, 56, 640, 175))
e.rel('MONITORS', 330, 255, [End('EMP_PROJ', 'N', via=[(330, 175)]), End('MANAGER', '1')])
e.entity('MANAGER', 330, 370, left=['_mgr_id'], right=['mname'])

# the wrong way without aggregation: a ternary with a redundant 'monitors'
e = ER('t_agg_bad')
e.entity('EMPLOYEE', 110, 90)
e.rel('WORKS_ON', 330, 90, [End('EMPLOYEE', 'M'), End('PROJECT', 'N')])
e.entity('PROJECT', 550, 90)
e.entity('MANAGER', 330, 330)
e.rel('MONITORS', 330, 210, [End('EMPLOYEE', 'M', via=[(110, 210)]), End('PROJECT', 'N', via=[(550, 210)]), End('MANAGER', '1')])

# ======================================================================= MAPPING RULES (class notes, rules 1-7 + extras)
e = ER('r1', expect=['STUDENT(_roll_no,name,gender)'])
e.entity('STUDENT', 200, 100, top=['name', '_roll_no', 'gender'])

e = ER('r2', expect=['STUDENT(_roll_no,f_name,l_name,gender)'])
e.entity('STUDENT', 220, 130, top=['name(f_name,l_name)', '_roll_no', 'gender'])

e = ER('r3', expect=['STUDENT(_roll_no,f_name,l_name,gender)', 'STUDENT_mobile_no(_roll_no,_mobile_no)'])
e.entity('STUDENT', 220, 130, top=['name(f_name,l_name)', '_roll_no', 'gender'], right=['*mobile_no'])

e = ER('r3c', expect=['STUDENT(_roll_no,name)', 'STUDENT_address(_roll_no,_house_no,_street,_city)'])
e.entity('STUDENT', 200, 100, left=['_roll_no', 'name'], right=['*address(house_no,street,city)'])

e = ER('r4', expect=['EMP(_emp_no,ename)', 'DEPARTMENT(_dept_id,dname)', 'WORKS(_emp_no,_dept_id,since)'])
e.entity('EMP', 90, 100, top=['_emp_no', 'ename'])
e.rel('WORKS', 320, 100, [End('EMP', 'M'), End('DEPARTMENT', 'N')], top=['since'])
e.entity('DEPARTMENT', 550, 100, top=['_dept_id', 'dname'])

e = ER('r5a', expect=['A(_a1,a2)', 'B(_b1,b2,a1)'])
e.entity('A', 90, 90, top=['_a1', 'a2'])
e.rel('R', 290, 90, [End('A', '1', arrow=True), End('B', 'N')])
e.entity('B', 490, 90, top=['_b1', 'b2'])

e = ER('r5b', expect=['A(_a1,a2,b1)', 'B(_b1,b2)'])
e.entity('A', 90, 90, top=['_a1', 'a2'])
e.rel('R', 290, 90, [End('A', 'N'), End('B', '1', arrow=True)])
e.entity('B', 490, 90, top=['_b1', 'b2'])

e = ER('r5c', expect=['A(_a1,a2,b1)', 'B(_b1,b2)'])
e.entity('A', 90, 90, top=['_a1', 'a2'])
e.rel('R', 290, 90, [End('A', '1', arrow=True), End('B', '1', arrow=True)])
e.entity('B', 490, 90, top=['_b1', 'b2'])
e = ER('r5c2', expect=['A(_a1,a2)', 'B(_b1,b2,a1)'], opts={'R_side': 'B'})
e.entity('A', 90, 90, top=['_a1', 'a2'])
e.rel('R', 290, 90, [End('A', '1', arrow=True), End('B', '1', arrow=True)])
e.entity('B', 490, 90, top=['_b1', 'b2'])

e = ER('r5d', expect=['A(_a1,a2)', 'B(_b1,b2,a1)'])
e.entity('A', 90, 90, top=['_a1', 'a2'])
e.rel('R', 290, 90, [End('A', '1', arrow=True), End('B', 'N', total=True)])
e.entity('B', 490, 90, top=['_b1', 'b2'])

e = ER('r6', expect=['A(_a1,a2,b1,b2)'])
e.entity('A', 90, 90, top=['_a1', 'a2'])
e.rel('R', 290, 90, [End('A', '1', total=True, arrow=True), End('B', '1', total=True, arrow=True)])
e.entity('B', 490, 90, top=['_b1', 'b2'])

e = ER('r6b', expect=['A(_a1,a2)', 'B(_b1,b2,a1)'])
e.entity('A', 90, 90, top=['_a1', 'a2'])
e.rel('R', 290, 90, [End('A', '1', arrow=True), End('B', '1', total=True, arrow=True)])
e.entity('B', 490, 90, top=['_b1', 'b2'])

e = ER('r7', expect=['A(_a1,a2)', 'B(_a1,_b1,b2)'])
e.entity('A', 90, 90, top=['_a1', 'a2'])
e.rel('R', 290, 90, [End('A', '1', arrow=True), End('B', 'N', total=True)], identifying=True)
e.entity('B', 490, 90, weak=True, top=['~b1', 'b2'])

e = ER('r8', expect=['COURSE(_course_id,title)', 'PREREQ(_course_id,_prereq_course_id)'])
e.entity('COURSE', 120, 120, left=['_course_id', 'title'])
e.rel('PREREQ', 360, 120, [End('COURSE', 'M', role='course', via=[(360, 40), (120, 40)]),
                            End('COURSE', 'N', role='prereq', via=[(360, 200), (120, 200)])])

e = ER('r9', expect=['INSTRUCTOR(_ins_id,iname)', 'COURSE(_course_id,title)', 'STUDENT(_student_id,sname)',
                      'TEACHES(_course_id,_student_id,ins_id,semester,grade)'])
e.entity('INSTRUCTOR', 110, 110, top=['_ins_id', 'iname'])
e.rel('TEACHES', 360, 110, [End('INSTRUCTOR', '1'), End('COURSE', 'N'), End('STUDENT', 'M', total=True)], top=['semester', 'grade'], gap={'top': 30})
e.entity('COURSE', 610, 110, top=['_course_id', 'title'])
e.entity('STUDENT', 360, 250, left=['_student_id'], right=['sname'])

# specialization mapping - the 2022 Doctor hierarchy in all four ways
def doctor(eid, method, expect, total=True, disjoint=True):
    e = ER(eid, expect=expect, opts={'typecol': 'doctor_type'})
    e.entity('DOCTOR', 330, 70, top=['_id', 'name', 'area'], gap={'top': 30})
    e.isa('DOCTOR', ['PERMANENT', 'RESIDENT', 'VISITING'], 330, 170, disjoint=disjoint, total=total, method=method)
    e.entity('PERMANENT', 110, 270, bottom=['salary'], gap={'bottom': 30})
    e.entity('RESIDENT', 330, 270, bottom=['stipend'], gap={'bottom': 30})
    e.entity('VISITING', 550, 270, bottom=['wages_per_hour'], gap={'bottom': 30})
    return e


doctor('p22c_er', 'er', ['DOCTOR(_id,name,area)', 'PERMANENT(_id,salary)', 'RESIDENT(_id,stipend)', 'VISITING(_id,wages_per_hour)'])
doctor('p22c', 'sub', ['PERMANENT(_id,name,area,salary)', 'RESIDENT(_id,name,area,stipend)', 'VISITING(_id,name,area,wages_per_hour)'])
doctor('p22c_single', 'single', ['DOCTOR(_id,name,area,salary,stipend,wages_per_hour,doctor_type)'])

# ======================================================================= CLASS-NOTES PRACTICE QUESTIONS
e = ER('q_mpn', notation='arrow', expect=['P(_p1,p2)', 'M(_m1,m2,m3,p1)', 'N(_p1,_n1,n2)'])
e.entity('M', 90, 100, top=['_m1', 'm2', 'm3'])
e.rel('R1', 280, 100, [End('M', 'N', total=True), End('P', '1')])
e.entity('P', 460, 100, top=['_p1', 'p2'])
e.rel('R2', 640, 100, [End('P', '1'), End('N', 'N', total=True)], identifying=True)
e.entity('N', 830, 100, weak=True, top=['~n1', 'n2'])

e = ER('q_e123', notation='arrow', expect=['E1(_a1,a2)', 'E3(_c1,c2)', 'E2(_b1,b2,b3,a1,c1)'])
e.entity('E1', 90, 100, top=['_a1', 'a2'])
e.rel('R1', 270, 100, [End('E1', '1'), End('E2', 'N')])
e.entity('E2', 450, 100, top=['_b1', 'b2', 'b3'])
e.rel('R2', 630, 100, [End('E2', 'N'), End('E3', '1')])
e.entity('E3', 810, 100, top=['_c1', 'c2'])

e = ER('q_abcd', notation='arrow', expect=['A(_a1,a2,b1)', 'B(_b1,b2,b3)', 'R2(_a1,_c1)', 'C(_c1,c2,c3)', 'R3(_c1,_d1)', 'D(_d1,d2,b1)'])
e.entity('A', 110, 100, top=['_a1', 'a2'])
e.rel('R1', 340, 100, [End('A', 'N', total=True), End('B', '1')])
e.entity('B', 570, 100, top=['_b1', 'b2', 'b3'])
e.rel('R2', 110, 220, [End('A', 'M'), End('C', 'N')])
e.entity('C', 110, 340, bottom=['_c1', 'c2', 'c3'])
e.rel('R3', 340, 340, [End('C', 'M'), End('D', 'N')])
e.entity('D', 570, 340, bottom=['_d1', 'd2'])
e.rel('R4', 570, 220, [End('D', 'N', total=True), End('B', '1')])

# ======================================================================= PYQ DESIGN ANSWERS
# ---- End-Sem 2024 Q3(a): airline reservations (redrawn from the paper)
pre = {'DEPARTURE_AIRPORT': 'dep', 'ARRIVAL_AIRPORT': 'arr', 'DEPARTS': 'dep', 'ARRIVES': 'arr'}
e = ER('p24a', opts={'prefix': pre}, expect=[
    'AIRPORT(_airport_code,name,city,state)',
    'FLIGHT(_number,airline,weekdays)',
    'FLIGHT_LEG(_number,_leg_no,dep_airport_code,scheduled_dep_time,arr_airport_code,scheduled_arr_time)',
    'LEG_INSTANCE(_number,_leg_no,_date,no_of_avail_seats,dep_airport_code,dep_time,arr_airport_code,arr_time,airplane_id)',
    'FARE(_number,_code,amount,restrictions)',
    'AIRPLANE_TYPE(_type_name,max_seats,company)',
    'CAN_LAND(_type_name,_airport_code)',
    'AIRPLANE(_airplane_id,total_no_of_seats,type_name)',
    'SEAT(_number,_leg_no,_date,_seat_no,customer_name,cphone)'])
e.entity('AIRPORT', 190, 140, left=['_airport_code', 'name', 'city', 'state'])
e.rel('DEPARTURE_AIRPORT', 480, 40, [End('AIRPORT', '1'), End('FLIGHT_LEG', 'N', total=True)], top=['scheduled_dep_time'], gap={'top': 16})
e.rel('ARRIVAL_AIRPORT', 480, 170, [End('AIRPORT', '1'), End('FLIGHT_LEG', 'N', total=True)], bottom=['scheduled_arr_time'], gap={'bottom': 14})
e.entity('FLIGHT_LEG', 800, 110, weak=True, right=['~leg_no'])
e.rel('LEGS', 800, 230, [End('FLIGHT', '1'), End('FLIGHT_LEG', 'N', total=True)], identifying=True)
e.entity('FLIGHT', 800, 350, bottom=['_number', 'airline', 'weekdays'], gap={'bottom': 30})
e.rel('FARES', 1010, 350, [End('FLIGHT', '1'), End('FARE', 'N', total=True)], identifying=True)
e.entity('FARE', 1010, 480, weak=True, bottom=['~code', 'amount', 'restrictions'], gap={'bottom': 30})
e.rel('INSTANCE_OF', 610, 330, [End('FLIGHT_LEG', '1'), End('LEG_INSTANCE', 'N', total=True)], identifying=True)
e.entity('LEG_INSTANCE', 560, 600, weak=True, right=['~date', 'no_of_avail_seats'], gap={'right': 26})
e.rel('DEPARTS', 360, 380, [End('AIRPORT', '1', via=[(222, 380)]), End('LEG_INSTANCE', 'N', total=True)], top=['dep_time'], gap={'top': 14})
e.rel('ARRIVES', 360, 500, [End('AIRPORT', '1', via=[(202, 500)]), End('LEG_INSTANCE', 'N', total=True)], bottom=['arr_time'], gap={'bottom': 14})
e.rel('CAN_LAND', 100, 300, [End('AIRPLANE_TYPE', 'M'), End('AIRPORT', 'N')])
e.entity('AIRPLANE_TYPE', 100, 470, left=['_type_name', 'max_seats', 'company'])
e.rel('TYPE', 100, 600, [End('AIRPLANE_TYPE', '1'), End('AIRPLANE', 'N', total=True)])
e.entity('AIRPLANE', 100, 730, bottom=['_airplane_id', 'total_no_of_seats'], gap={'bottom': 30})
e.rel('ASSIGNED', 360, 690, [End('AIRPLANE', '1'), End('LEG_INSTANCE', 'N', total=True)])
e.rel('RESERVATION', 560, 790, [End('LEG_INSTANCE', '1'), End('SEAT', 'N', total=True)], identifying=True,
      right=['customer_name', 'cphone'])
e.entity('SEAT', 560, 900, weak=True, left=['~seat_no'])

# ---- End-Sem 2024 Q3(c): car selling
e = ER('p24c', expect=['SELLER(_seller_id,name,address)', 'SELLER_qualification(_seller_id,_qualification)',
                        'CAR(_car_id,serial_no,model_no,colour,year,seller_id)',
                        'BUYER(_buyer_id,name,mobile_no,landline_no,address,country,city)',
                        'INVOICE(_invoice_id,inv_date,car_id,buyer_id)'])
e.entity('SELLER', 110, 120, top=['_seller_id', 'name'], left=['address', '*qualification'], gap={'left': 30})
e.rel('SELLS', 340, 120, [End('SELLER', '1'), End('CAR', 'N', total=True)])
e.entity('CAR', 580, 120, top=['_car_id', 'serial_no', 'model(model_no,colour,year)'], gap={'top': 40})
e.rel('BILLED_FOR', 580, 260, [End('CAR', '1'), End('INVOICE', '1', total=True)])
e.entity('INVOICE', 580, 390, right=['_invoice_id', 'inv_date'])
e.rel('BUYS', 340, 390, [End('BUYER', '1'), End('INVOICE', 'N', total=True)])
e.entity('BUYER', 110, 390, left=['_buyer_id', 'name', 'address'], bottom=['country', 'city', 'contact_no(mobile_no,landline_no)'], gap={'left': 30, 'bottom': 34})

# ---- End-Sem 2025 Q3(c): university registrar's office (Korth-style)
e = ER('p25c', expect=['COURSE(_course_no,title,credits,syllabus)', 'PREREQ(_course_no,_prereq_course_no)',
                        'OFFERING(_course_no,_year,_semester,_section_no,classroom)',
                        'OFFERING_timings(_course_no,_year,_semester,_section_no,_timings)',
                        'INSTRUCTOR(_ins_id,name,department,title)',
                        'TEACHES(_ins_id,_course_no,_year,_semester,_section_no)',
                        'STUDENT(_student_id,name,program)',
                        'ENROLS(_student_id,_course_no,_year,_semester,_section_no,grade)'])
e.entity('COURSE', 140, 120, top=['_course_no', 'title', 'credits', 'syllabus'], gap={'top': 34})
e.rel('PREREQ', 140, 290, [End('COURSE', 'M', role='course'), End('COURSE', 'N', role='prereq', via=[(260, 290), (260, 132)])])
e.rel('IS_OFFERED', 420, 120, [End('COURSE', '1'), End('OFFERING', 'N', total=True)], identifying=True)
e.entity('OFFERING', 700, 120, weak=True, top=['~year', '~semester', '~section_no'], right=['*timings', 'classroom'], gap={'top': 34})
e.rel('TEACHES', 700, 280, [End('INSTRUCTOR', 'M'), End('OFFERING', 'N')])
e.entity('INSTRUCTOR', 700, 410, right=['_ins_id', 'name', 'department', 'title'], gap={'right': 30})
e.rel('ENROLS', 420, 280, [End('STUDENT', 'M'), End('OFFERING', 'N')], left=['grade'], gap={'left': 14})
e.entity('STUDENT', 420, 410, bottom=['_student_id', 'name', 'program'], gap={'bottom': 34})

# ---- Mid-Sem Oct 2021 Q3(c): registrar - class, instructor, students, grade
e = ER('p21', expect=['DEPARTMENT(_dept_id,dname,ins_id)', 'INSTRUCTOR(_ins_id,first,last)', 'INSTRUCTOR_phone(_ins_id,_phone)',
                       'COURSE(_course_no,title,credits)', 'CLASS(_course_no,_section_no,_semester,_year,room,meet_time,ins_id)',
                       'STUDENT(_roll_no,name,dob)', 'TAKES(_roll_no,_course_no,_section_no,_semester,_year,grade)'])
e.entity('DEPARTMENT', 120, 100, top=['_dept_id', 'dname'])
e.rel('HEADED_BY', 120, 230, [End('INSTRUCTOR', '1'), End('DEPARTMENT', '1', total=True)])
e.entity('INSTRUCTOR', 120, 360, left=['_ins_id', '*phone'], bottom=['name(first,last)'], gap={'left': 30, 'bottom': 30})
e.rel('TEACHES', 360, 360, [End('INSTRUCTOR', '1'), End('CLASS', 'N', total=True)])
e.entity('CLASS', 620, 360, weak=True, right=['~section_no', '~semester', '~year', 'room', 'meet_time', '/no_enrolled'], gap={'right': 30})
e.rel('OFFERED_AS', 620, 230, [End('COURSE', '1'), End('CLASS', 'N', total=True)], identifying=True)
e.entity('COURSE', 620, 100, top=['_course_no', 'title', 'credits'])
e.rel('TAKES', 360, 530, [End('STUDENT', 'M'), End('CLASS', 'N', via=[(620, 530)])], bottom=['grade'], gap={'bottom': 22})
e.entity('STUDENT', 120, 530, bottom=['_roll_no', 'name', 'dob', '/age'], gap={'bottom': 30})

# ---- End-Sem July 2026 Q3(a): hospital management
e = ER('p26a', expect=['DEPARTMENT(_dept_id,dname,location,head_doc_id)', 'DOCTOR(_doc_id,first,last,specialization,dept_id)',
                        'DOCTOR_phone(_doc_id,_phone)', 'PATIENT(_pid,pname,dob,address)', 'PATIENT_phone(_pid,_phone)',
                        'APPOINTMENT(_appt_id,appt_date,slot,pid,doc_id)', 'PRESCRIPTION(_appt_id,_presc_no,notes)',
                        'MEDICINE(_med_id,mname,unit_price)', 'CONTAINS(_appt_id,_presc_no,_med_id,dosage,quantity)',
                        'BILL(_bill_no,amount,bill_date,status,appt_id)'],
       opts={'prefix': {'HEADS': 'head'}})
e.entity('DEPARTMENT', 120, 90, top=['_dept_id', 'dname', 'location'])
e.rel('WORKS_IN', 120, 220, [End('DEPARTMENT', '1'), End('DOCTOR', 'N', total=True)])
e.rel('HEADS', 330, 160, [End('DOCTOR', '1'), End('DEPARTMENT', '1', total=True)])
e.entity('DOCTOR', 120, 350, left=['_doc_id', 'name(first,last)', 'specialization', '*phone'], gap={'left': 26})
e.rel('ATTENDS', 310, 350, [End('DOCTOR', '1'), End('APPOINTMENT', 'N', total=True)])
e.entity('APPOINTMENT', 510, 350, top=['_appt_id', 'appt_date', 'slot'], gap={'top': 30})
e.rel('BOOKS', 700, 350, [End('PATIENT', '1'), End('APPOINTMENT', 'N', total=True)])
e.entity('PATIENT', 880, 350, top=['_pid', 'pname', 'dob'], bottom=['/age', '*phone', 'address'], gap={'top': 30, 'bottom': 30})
e.rel('ISSUES', 510, 480, [End('APPOINTMENT', '1'), End('PRESCRIPTION', 'N', total=True)], identifying=True)
e.entity('PRESCRIPTION', 510, 610, weak=True, bottom=['~presc_no', 'notes'], gap={'bottom': 30})
e.rel('CONTAINS', 700, 610, [End('PRESCRIPTION', 'M', total=True), End('MEDICINE', 'N')], top=['dosage', 'quantity'], gap={'top': 18})
e.entity('MEDICINE', 880, 610, bottom=['_med_id', 'mname', 'unit_price'], gap={'bottom': 30})
e.rel('BILLED_AS', 310, 480, [End('APPOINTMENT', '1'), End('BILL', '1', total=True)])
e.entity('BILL', 310, 610, left=['_bill_no', 'amount', 'bill_date', 'status'], gap={'left': 26})

# ---- End-Sem July 2026 Q3(c): car rental
e = ER('p26c', expect=['BRANCH(_branch_id,bname,city,street)', 'VEHICLE(_reg_no,model,vtype,daily_rate,branch_id,policy_no,insurer,expiry)',
                        'CUSTOMER(_cust_id,cname,licence_no)', 'CUSTOMER_phone(_cust_id,_phone)',
                        'DRIVER(_driver_id,dname,dl_no,branch_id)',
                        'RESERVATION(_res_id,pickup_date,return_date,cust_id,reg_no,driver_id)',
                        'PAYMENT(_res_id,_pay_no,amount,mode,pay_date)'])
e.entity('BRANCH', 110, 110, top=['_branch_id', 'bname', 'address(city,street)'], gap={'top': 36})
e.rel('HAS', 300, 110, [End('BRANCH', '1'), End('VEHICLE', 'N', total=True)])
e.entity('VEHICLE', 490, 110, top=['_reg_no', 'model', 'vtype', 'daily_rate'], gap={'top': 36})
e.rel('COVERED_BY', 680, 110, [End('VEHICLE', '1', total=True), End('INSURANCE', '1', total=True)])
e.entity('INSURANCE', 870, 110, top=['_policy_no', 'insurer', 'expiry'], gap={'top': 36})
e.rel('EMPLOYS', 110, 250, [End('BRANCH', '1'), End('DRIVER', 'N', total=True)])
e.entity('DRIVER', 110, 390, left=['_driver_id', 'dname', 'dl_no'], gap={'left': 30})
e.rel('DRIVEN_BY', 300, 390, [End('DRIVER', '1'), End('RESERVATION', 'N')])
e.rel('FOR', 490, 250, [End('VEHICLE', '1'), End('RESERVATION', 'N', total=True)])
e.entity('RESERVATION', 490, 390, right=['_res_id', 'pickup_date', 'return_date'], gap={'right': 26}, at={})
e.rel('MAKES', 490, 520, [End('CUSTOMER', '1'), End('RESERVATION', 'N', total=True)])
e.entity('CUSTOMER', 490, 650, left=['_cust_id', 'cname'], right=['*phone', 'licence_no'], gap={'left': 30, 'right': 30})
e.rel('PAID_BY', 300, 520, [End('RESERVATION', '1', via=[(460, 455)] and None), End('PAYMENT', 'N', total=True)], identifying=True)
e.entity('PAYMENT', 230, 650, weak=True, left=['~pay_no', 'amount', 'mode', 'pay_date'], gap={'left': 26})

# ---- Mid-Sem 2025 Q5(b): NSUT_UBER
e = ER('m25uber', expect=['APP_USER(_user_id,first_name,last_name,email,dob)', 'APP_USER_phone(_user_id,_phone)',
                           'DRIVER(_user_id,licence_no,spot_id)', 'VEHICLE(_vehicle_no,model,vtype,user_id)',
                           'PARKING_SPOT(_spot_id,location)', 'RIDE(_ride_id,pickup,drop_loc,fare,date_time,user_id)',
                           'BOOKING(_booking_id,status,payment_mode,user_id,ride_id)'])
e.entity('APP_USER', 430, 110, top=['_user_id', 'name(first_name,last_name)', 'email', '*phone', 'dob', '/age'], gap={'top': 36})
e.isa('APP_USER', ['DRIVER'], 430, 210, disjoint=True, total=False, note='partial')
e.entity('DRIVER', 430, 310, right=['licence_no'], at={'licence_no': (560, 255)})
e.rel('ALLOTTED', 650, 310, [End('DRIVER', '1', total=True), End('PARKING_SPOT', '1')])
e.entity('PARKING_SPOT', 870, 310, top=['_spot_id', 'location'])
e.rel('USES', 430, 430, [End('DRIVER', '1'), End('VEHICLE', 'N')])
e.entity('VEHICLE', 430, 550, left=['_vehicle_no'], right=['model', 'vtype'], gap={'left': 26, 'right': 26})
e.rel('REQUESTS', 130, 110, [End('APP_USER', '1'), End('RIDE', 'N', total=True)])
e.entity('RIDE', 130, 250, left=['_ride_id', 'pickup', 'drop_loc', 'fare', 'date_time'], gap={'left': 26})
e.rel('FOR_RIDE', 130, 400, [End('RIDE', '1'), End('BOOKING', 'N', total=True)])
e.entity('BOOKING', 130, 540, left=['_booking_id', 'status', 'payment_mode'], gap={'left': 26})
e.rel('BOOKS', 260, 290, [End('APP_USER', '1'), End('BOOKING', 'N', total=True)])

# ---- Mid-Sem Sep 2026 Q4(b): employee / dependent
e = ER('m26dep', expect=['EMPLOYEE(_emp_id,ename,salary)', 'DEPENDENT(_emp_id,_dep_name,relation,dob)'])
e.entity('EMPLOYEE', 100, 100, top=['_emp_id', 'ename', 'salary'])
e.rel('HAS_DEPENDENT', 350, 100, [End('EMPLOYEE', '1'), End('DEPENDENT', 'N', total=True)], identifying=True)
e.entity('DEPENDENT', 610, 100, weak=True, top=['~dep_name', 'relation', 'dob'])

# ---- Summer mid-sem Q3(b): hospital staff hierarchy (concept identification)
e = ER('msum', notation='label')
e.entity('HOSPITAL_STAFF', 420, 60, top=['_staff_id', 'name'], gap={'top': 26})
e.isa('HOSPITAL_STAFF', ['MEDICAL_STAFF', 'ADMIN_EMPLOYEE'], 420, 150, disjoint=True, total=True, note='generalization (disjoint, total)')
e.entity('MEDICAL_STAFF', 260, 240)
e.entity('ADMIN_EMPLOYEE', 600, 240, right=['office'], gap={'right': 26})
e.isa('MEDICAL_STAFF', ['DOCTOR', 'NURSE'], 260, 330, disjoint=True, total=True, note='disjoint, total')
e.entity('DOCTOR', 150, 430, left=['specialization'], gap={'left': 26})
e.entity('NURSE', 380, 430, right=['shift'], gap={'right': 26})
e.rel('ASSIGNED_TO', 150, 560, [End('DOCTOR', 'N'), End('DEPARTMENT', '1')])
e.entity('DEPARTMENT', 150, 680, left=['_dept_id'], gap={'left': 26})
e.rel('PRESCRIBES', 600, 560, [End('DOCTOR', '1', via=[(300, 500), (480, 500)] and None), End('PATIENT', 'M', total=True), End('TREATMENT', 'N')])
e.entity('PATIENT', 840, 560, right=['_pid'], gap={'right': 26})
e.entity('TREATMENT', 600, 680, right=['_treat_id'], gap={'right': 26})
e.aggregate('PRESCRIPTION_AGG', 'PRESCRIBES', (470, 500, 930, 720))
e.rel('SUPERVISES', 700, 430, [End('PRESCRIPTION_AGG', 'N', via=[(700, 500)]), End('DOCTOR', '1', role='senior doctor', via=[(700, 380), (150, 380)])])

# ======================================================================= FULL WORKED EXAMPLE: COMPANY (Elmasri)
e = ER('company', opts={'prefix': {'MANAGES': 'mgr'}}, expect=[
    'EMPLOYEE(_ssn,fname,minit,lname,bdate,address,salary,sex,dnumber,supervisor_ssn)',
    'DEPARTMENT(_dnumber,dname,mgr_ssn,start_date)', 'DEPARTMENT_locations(_dnumber,_locations)',
    'PROJECT(_pnumber,pname,plocation,dnumber)', 'WORKS_ON(_ssn,_pnumber,hours)',
    'DEPENDENT(_ssn,_dependent_name,sex,birth_date,relationship)'])
e.entity('EMPLOYEE', 300, 300, top=['_ssn', 'name(fname,minit,lname)', 'bdate', 'address', 'salary', 'sex'], gap={'top': 50})
e.rel('SUPERVISION', 130, 450, [End('EMPLOYEE', '1', role='supervisor', via=[(130, 300)]), End('EMPLOYEE', 'N', role='supervisee')])
e.rel('DEPENDENTS_OF', 400, 460, [End('EMPLOYEE', '1'), End('DEPENDENT', 'N', total=True)], identifying=True)
e.entity('DEPENDENT', 400, 590, weak=True, bottom=['~dependent_name', 'sex', 'birth_date', 'relationship'], gap={'bottom': 30})
e.rel('WORKS_FOR', 620, 230, [End('EMPLOYEE', 'N', total=True), End('DEPARTMENT', '1', total=True)])
e.rel('MANAGES', 620, 360, [End('EMPLOYEE', '1'), End('DEPARTMENT', '1', total=True)], bottom=['start_date'], gap={'bottom': 16})
e.entity('DEPARTMENT', 900, 300, right=['_dnumber', '_dname', '*locations', '/number_of_employees'], gap={'right': 30})
e.rel('CONTROLS', 900, 450, [End('DEPARTMENT', '1'), End('PROJECT', 'N', total=True)])
e.entity('PROJECT', 900, 600, bottom=['_pnumber', 'pname', 'plocation'], gap={'bottom': 30})
e.rel('WORKS_ON', 640, 600, [End('EMPLOYEE', 'M', total=True), End('PROJECT', 'N', total=True)], bottom=['hours'], gap={'bottom': 16})

# ======================================================================= PRACTICE
# P1: weak entity owned by a weak entity + 1:1 total both + recursive + composite multivalued
e = ER('pr1', expect=['PERSON(_pid,first,last,passport_no,expiry,mentor_pid,bid,floor_no,room_no,since)',
                       'PERSON_email(_pid,_email)', 'BUILDING(_bid,bname)', 'FLOOR(_bid,_floor_no,wing)',
                       'ROOM(_bid,_floor_no,_room_no,capacity)'])
e.entity('PASSPORT', 110, 100, top=['_passport_no', 'expiry'])
e.rel('HOLDS', 330, 100, [End('PERSON', '1', total=True), End('PASSPORT', '1', total=True)])
e.entity('PERSON', 560, 100, top=['_pid', 'name(first,last)', '*email'], gap={'top': 36})
e.rel('MENTORS', 800, 100, [End('PERSON', '1', role='mentor'), End('PERSON', 'N', role='mentee', via=[(800, 175), (598, 175)])])
e.rel('OCCUPIES', 560, 230, [End('PERSON', 'N'), End('ROOM', '1')], left=['since'], gap={'left': 16})
e.entity('ROOM', 560, 360, weak=True, right=['~room_no', 'capacity'], gap={'right': 26})
e.rel('HAS_ROOM', 330, 360, [End('FLOOR', '1'), End('ROOM', 'N', total=True)], identifying=True)
e.entity('FLOOR', 110, 360, weak=True, left=['~floor_no', 'wing'], gap={'left': 26})
e.rel('HAS_FLOOR', 110, 480, [End('BUILDING', '1'), End('FLOOR', 'N', total=True)], identifying=True)
e.entity('BUILDING', 110, 600, right=['_bid', 'bname'], gap={'right': 26})

# P2: ternary with a '1' side + aggregation (IPL auction)
e = ER('pr2', expect=['PLAYER(_pid,pname,role)', 'TEAM(_team_id,tname)', 'SEASON(_year)', 'CONTRACT(_pid,_year,team_id,price)',
                       'AGENT(_agent_id,aname)', 'NEGOTIATES(_pid,_year,agent_id,commission)'])
e.entity('PLAYER', 110, 110, top=['_pid', 'pname', 'role'])
e.rel('CONTRACT', 360, 110, [End('PLAYER', 'N'), End('TEAM', '1'), End('SEASON', 'M')], bottom=['price'], gap={'bottom': 14})
e.entity('TEAM', 610, 110, top=['_team_id', 'tname'])
e.entity('SEASON', 360, 270, right=['_year'], gap={'right': 26})
e.aggregate('CONTRACT_AGG', 'CONTRACT', (20, 60, 700, 310))
e.rel('NEGOTIATES', 360, 400, [End('CONTRACT_AGG', 'N', via=[(360, 310)]), End('AGENT', '1')], right=['commission'], gap={'right': 16})
e.entity('AGENT', 360, 520, left=['_agent_id'], right=['aname'], gap={'left': 26, 'right': 26})

# P3: online food delivery
e = ER('pr3', expect=['CUSTOMER(_cust_id,cname,phone)', 'CUSTOMER_address(_cust_id,_house,_street,_city,_pin)',
                       'RESTAURANT(_rest_id,rname)', 'RESTAURANT_cuisine(_rest_id,_cuisine)',
                       'MENU_ITEM(_rest_id,_item_no,iname,price)',
                       'FOOD_ORDER(_order_id,order_time,status,cust_id,rest_id,dp_id)',
                       'CONTAINS(_order_id,_rest_id,_item_no,quantity)', 'DELIVERY_PARTNER(_dp_id,dname,vehicle_no)'])
e.entity('CUSTOMER', 150, 110, top=['_cust_id', 'cname', 'phone'], left=['*address(house,street,city,pin)'], gap={'left': 30})
e.rel('PLACES', 150, 260, [End('CUSTOMER', '1'), End('FOOD_ORDER', 'N', total=True, via=[(150, 400)])])
e.entity('FOOD_ORDER', 450, 400, bottom=['_order_id', 'order_time', 'status', '/total_amount'], gap={'bottom': 30})
e.rel('FROM_REST', 450, 260, [End('RESTAURANT', '1'), End('FOOD_ORDER', 'N', total=True)])
e.entity('RESTAURANT', 450, 110, top=['_rest_id', 'rname', '*cuisine', '/avg_rating'])
e.rel('OFFERS', 710, 110, [End('RESTAURANT', '1'), End('MENU_ITEM', 'N', total=True)], identifying=True)
e.entity('MENU_ITEM', 930, 110, weak=True, top=['~item_no', 'iname', 'price'])
e.rel('CONTAINS', 710, 400, [End('FOOD_ORDER', 'M', total=True), End('MENU_ITEM', 'N', via=[(930, 400)])], bottom=['quantity'], gap={'bottom': 16})
e.rel('DELIVERS', 450, 580, [End('DELIVERY_PARTNER', '1'), End('FOOD_ORDER', 'N')])
e.entity('DELIVERY_PARTNER', 450, 700, left=['_dp_id'], right=['dname', 'vehicle_no'], gap={'left': 26, 'right': 26})

# P4: hostel allotment
e = ER('pr4', expect=['HOSTEL(_hostel_id,hname,htype,warden_id,wname,wphone)', 'ROOM(_hostel_id,_room_no,capacity)',
                       'STUDENT(_roll_no,sname,dob,hostel_id,room_no,since)', 'STUDENT_phone(_roll_no,_phone)',
                       'COMPLAINT(_complaint_id,ctext,status,roll_no)'])
e.entity('WARDEN', 110, 100, top=['_warden_id', 'wname', 'wphone'])
e.rel('MANAGED_BY', 330, 100, [End('HOSTEL', '1', total=True), End('WARDEN', '1', total=True)])
e.entity('HOSTEL', 560, 100, top=['_hostel_id', 'hname', 'htype'])
e.rel('HAS', 560, 230, [End('HOSTEL', '1'), End('ROOM', 'N', total=True)], identifying=True)
e.entity('ROOM', 560, 360, weak=True, right=['~room_no', 'capacity'], gap={'right': 26})
e.rel('ALLOTTED', 330, 360, [End('STUDENT', 'N'), End('ROOM', '1')], top=['since'], gap={'top': 14})
e.entity('STUDENT', 110, 360, left=['_roll_no', 'sname', '*phone', 'dob', '/age'], gap={'left': 26})
e.rel('FILES', 110, 490, [End('STUDENT', '1'), End('COMPLAINT', 'N', total=True)])
e.entity('COMPLAINT', 110, 610, right=['_complaint_id', 'ctext', 'status'], gap={'right': 26})

# P5: reverse engineering answer (library)
e = ER('pr5', expect=['PUBLISHER(_pub_name,city)', 'BOOK(_isbn,title,pub_name)', 'BOOK_author(_isbn,_author)',
                       'BOOK_COPY(_isbn,_copy_no,shelf,mid,issue_date)', 'MEMBER(_mid,mname)'])
e.entity('PUBLISHER', 110, 100, top=['_pub_name', 'city'])
e.rel('PUBLISHES', 330, 100, [End('PUBLISHER', '1'), End('BOOK', 'N', total=True)])
e.entity('BOOK', 560, 100, top=['_isbn', 'title', '*author'])
e.rel('HAS_COPY', 560, 230, [End('BOOK', '1'), End('BOOK_COPY', 'N', total=True)], identifying=True)
e.entity('BOOK_COPY', 560, 360, weak=True, right=['~copy_no', 'shelf'], gap={'right': 26})
e.rel('BORROWS', 330, 360, [End('MEMBER', '1'), End('BOOK_COPY', 'N')], top=['issue_date'], gap={'top': 14})
e.entity('MEMBER', 110, 360, left=['_mid', 'mname'], gap={'left': 26})

# ======================================================================= MIN-TABLES DRILL (section 9)
e = ER('d1', expect=['A(_a1,a2,b1)', 'B(_b1,b2)', 'C(_c1,c2,b1)'])
e.entity('A', 80, 90, top=['_a1', 'a2'])
e.rel('R1', 250, 90, [End('A', '1'), End('B', '1')])
e.entity('B', 420, 90, top=['_b1', 'b2'])
e.rel('R2', 590, 90, [End('B', '1'), End('C', 'N')])
e.entity('C', 760, 90, top=['_c1', 'c2'])

e = ER('d2', expect=['A(_a1,a2,b1,b2)', 'R2(_b1,_c1)', 'C(_c1)', 'C_x(_c1,_x)'])
e.entity('A', 80, 90, top=['_a1', 'a2'])
e.rel('R1', 250, 90, [End('A', '1', total=True), End('B', '1', total=True)])
e.entity('B', 420, 90, top=['_b1', 'b2'])
e.rel('R2', 590, 90, [End('B', 'M'), End('C', 'N')])
e.entity('C', 760, 90, top=['_c1', '*x'])

e = ER('d3', expect=['E(_e1,e2)', 'W(_e1,_w1,w2)', 'F(_f1)', 'S(_e1,_w1,_f1)'])
e.entity('E', 80, 90, top=['_e1', 'e2'])
e.rel('R', 250, 90, [End('E', '1'), End('W', 'N', total=True)], identifying=True)
e.entity('W', 420, 90, weak=True, top=['~w1', 'w2'])
e.rel('S', 590, 90, [End('W', 'M'), End('F', 'N')])
e.entity('F', 760, 90, top=['_f1'])

e = ER('d4', expect=['A(_a1)', 'B(_b1,a1)', 'C(_c1,b1)', 'D(_d1,c1)'])
for i, (n, x) in enumerate([('A', 70), ('B', 330), ('C', 590), ('D', 850)]):
    e.entity(n, x, 90, top=['_' + n.lower() + '1'])
for i, (r, a, b, x) in enumerate([('R1', 'A', 'B', 200), ('R2', 'B', 'C', 460), ('R3', 'C', 'D', 720)]):
    e.rel(r, x, 90, [End(a, '1'), End(b, 'N')])

e = ER('d5', expect=['A(_a1)', 'B(_b1)', 'R(_a1,_b1)'])
e.entity('A', 80, 90, top=['_a1'])
e.rel('R', 260, 90, [End('A', 'M', total=True), End('B', 'N', total=True)])
e.entity('B', 440, 90, top=['_b1'])

# P6: ternary with two '1' sides -> two candidate keys
e = ER('pr6', expect=['STUDENT(_roll_no,sname)', 'PROJECT(_proj_id,title)', 'GUIDE(_fac_id,fname)', 'GUIDES(_roll_no,proj_id,_fac_id)'])
e.entity('STUDENT', 110, 100, top=['_roll_no', 'sname'])
e.rel('GUIDES', 360, 100, [End('STUDENT', 'N'), End('PROJECT', '1'), End('GUIDE', '1')])
e.entity('PROJECT', 610, 100, top=['_proj_id', 'title'])
e.entity('GUIDE', 360, 240, left=['_fac_id'], right=['fname'], gap={'left': 26, 'right': 26})
