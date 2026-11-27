"""Every relation used in the notes, with the hand-written answers that the build re-checks."""
from fdview import Prob

# ---------------------------------------------------------------- theory / running examples
Prob('run', 'Roll, Name, Course, CName, Credits, Instructor, Office, Grade',
     'Roll -> Name; Course -> CName Credits Instructor; Instructor -> Office; Roll Course -> Grade',
     keys=['Roll, Course'], nf='1NF', superkeys=64,
     twonf=['Roll, Name', 'Course, CName, Credits, Instructor, Office', 'Roll, Course, Grade'],
     tnf=['Roll, Name', 'Course, CName, Credits, Instructor', 'Instructor, Office', 'Roll, Course, Grade'],
     bcnf=['Roll, Name', 'Instructor, Office', 'Course, CName, Credits, Instructor', 'Roll, Course, Grade'],
     short={'Instructor': 'Instr', 'Credits': 'Cr'})
Prob('stc', 'Student, Course, Teacher', 'Student Course -> Teacher; Teacher -> Course',
     keys=['Student, Course', 'Student, Teacher'], nf='3NF',
     bcnf=['Teacher, Course', 'Student, Teacher'],
     decomps={'bc': (['Teacher, Course', 'Student, Teacher'], True, False)})
Prob('ab_d', 'ABCD', 'A->B, B->C, C->D', keys=['A'], nf='2NF')
Prob('lossy1', 'ABC', 'A->B',
     decomps={'bad': (['AB', 'BC'], False, True), 'good': (['AB', 'AC'], True, True)})

# ---------------------------------------------------------------- class notes / Dhruv / course PDF
Prob('c2nf', 'ABCDEH', 'A->B, BC->D, E->C, D->A', keys=['AEH', 'BEH', 'DEH'], nf='1NF')
Prob('d2nf', 'ABCDE', 'A->B, BC->D, E->C, D->A', keys=['AE', 'BE', 'DE'], nf='1NF')
Prob('ckey', 'ABCDE', 'A->B, A->C, CD->E, B->D, E->A', keys=['A', 'E', 'BC', 'CD'], nf='3NF')
Prob('c3nf', 'ABCDEFG', 'AB->CD, AF->D, DE->F, C->G, F->E, G->A',
     keys=['ABE', 'ABF', 'BCE', 'BCF', 'BEG', 'BFG'], nf='1NF')
Prob('d3nf', 'ABCDE', 'AB->CD, ABC->E, C->A', keys=['AB', 'BC'], nf='3NF')
Prob('cabc', 'ABC', 'A->B, B->C, C->A', keys=['A', 'B', 'C'], nf='BCNF')
Prob('cAC', 'ABCD', 'A->B, C->D', keys=['AC'], nf='1NF', twonf=['AB', 'CD', 'AC'],
     decomps={'d': (['AB', 'CD', 'AC'], True, True)})
Prob('cCD', 'ABCD', 'C->D, AB->C, C->A', keys=['AB', 'BC'], nf='1NF',
     decomps={'d': (['CD', 'ABC'], True, True)})
Prob('cABD', 'ABCD', 'AB->D, BC->D, A->C, C->A', keys=['AB', 'BC'], nf='3NF')
Prob('c3way', 'ABCDE', 'A->B, B->C, C->D, D->E', keys=['A'], nf='2NF',
     decomps={'d': (['ABC', 'BCD', 'CDE'], True, True)})
Prob('cACBD', 'ABCD', 'AB->CD, A->C, B->D', keys=['AB'], nf='1NF',
     decomps={'d': (['AC', 'BD'], False, True)})
Prob('ccyc', 'ABCD', 'A->B, B->C, C->D, D->A', keys=['A', 'B', 'C', 'D'], nf='BCNF',
     decomps={'d': (['AB', 'BC', 'CD'], True, True)})
Prob('pdf86', 'ABCDEF', 'A->C, C->D, D->B, E->F', keys=['AE'], nf='1NF')
Prob('pdf87', 'ABCD', 'A->B, B->C, C->A', keys=['AD', 'BD', 'CD'], nf='3NF')
Prob('pdf106', 'VWXYZ', 'Z->V, W->Y, XY->Z, V->WX', keys=['V', 'Z', 'WX', 'XY'], nf='3NF',
     decomps={'i': (['VWX', 'VYZ'], True, False), 'ii': (['VWX', 'XYZ'], False, False)})

# ---------------------------------------------------------------- PYQs
Prob('y24a', 'StudentID, CourseID, InstructorID, Semester, Department, CourseName',
     'StudentID CourseID -> Semester InstructorID; CourseID -> Department CourseName; InstructorID Semester -> CourseID',
     keys=['StudentID, CourseID', 'StudentID, InstructorID, Semester'], nf='1NF',
     tnf=['StudentID, CourseID, InstructorID, Semester', 'CourseID, Department, CourseName'],
     bcnf=['CourseID, Department, CourseName', 'InstructorID, Semester, CourseID', 'StudentID, InstructorID, Semester'],
     decomps={'bcnf': (['CourseID, Department, CourseName', 'InstructorID, Semester, CourseID',
                        'StudentID, InstructorID, Semester'], True, False),
              'tnf': (['StudentID, CourseID, InstructorID, Semester', 'CourseID, Department, CourseName'], True, True)},
     short={'StudentID': 'SID', 'CourseID': 'CID', 'InstructorID': 'IID', 'Semester': 'Sem', 'Department': 'Dept',
            'CourseName': 'CName'})
Prob('y24b', 'Volume, Number, StartPage, EndPage, Title, Year, Price',
     'Volume Number StartPage EndPage -> Title; Volume Number -> Year; Volume Number StartPage EndPage -> Price',
     keys=['Volume, Number, StartPage, EndPage'], nf='1NF',
     decomps={'new': (['Volume, Number, StartPage, EndPage, Title, Price', 'Volume, Number, Year'], True, True)},
     bcnf=['Volume, Number, StartPage, EndPage, Title, Price', 'Volume, Number, Year'],
     short={'Volume': 'Vol', 'Number': 'Num', 'StartPage': 'SPage', 'EndPage': 'EPage'})
Prob('y25b', 'ABCDEFGHIJ', 'AB->C, A->DE, B->F, F->GH, D->IJ', keys=['AB'], nf='1NF',
     twonf=['ABC', 'ADEIJ', 'BFGH'], tnf=['ABC', 'ADE', 'DIJ', 'BF', 'FGH'], superkeys=256)
Prob('y25c', ['M', 'Y', 'P', 'MP', 'C'], [(['M'], ['MP']), (['M', 'Y'], ['P']), (['MP'], ['C'])],
     keys=[['M', 'Y']], nf='1NF',
     decomps={'D': ([['M', 'Y', 'P'], ['M', 'MP', 'C']], True, True)},
     tnf=[['M', 'Y', 'P'], ['M', 'MP'], ['MP', 'C']])
Prob('y26a', 'StudentID, StudentName, CourseID, CourseName, FacultyID, FacultyName, Department, Semester',
     'StudentID -> StudentName; CourseID -> CourseName Department; FacultyID -> FacultyName; StudentID CourseID -> Semester FacultyID',
     keys=['StudentID, CourseID'], nf='1NF', superkeys=64,
     bcnf=['StudentID, StudentName', 'CourseID, CourseName, Department', 'FacultyID, FacultyName',
           'StudentID, CourseID, Semester, FacultyID'],
     decomps={'f': (['StudentID, StudentName', 'CourseID, CourseName, Department', 'FacultyID, FacultyName',
                     'StudentID, CourseID, Semester, FacultyID'], True, True)},
     short={'StudentID': 'SID', 'StudentName': 'SName', 'CourseID': 'CID', 'CourseName': 'CName', 'FacultyID': 'FID',
            'FacultyName': 'FName', 'Department': 'Dept', 'Semester': 'Sem'})
Prob('y26b', 'PaperID, Title, AuthorID, AuthorName, Department, Conference, Year, ReviewerID, ReviewerName',
     'PaperID -> Title Conference Year AuthorID; AuthorID -> AuthorName Department; ReviewerID -> ReviewerName',
     keys=['PaperID, ReviewerID'], nf='1NF',
     twonf=['PaperID, Title, AuthorID, AuthorName, Department, Conference, Year', 'ReviewerID, ReviewerName',
            'PaperID, ReviewerID'],
     bcnf=['PaperID, Title, Conference, Year, AuthorID', 'AuthorID, AuthorName, Department', 'ReviewerID, ReviewerName',
           'PaperID, ReviewerID'],
     decomps={'f': (['PaperID, Title, Conference, Year, AuthorID', 'AuthorID, AuthorName, Department',
                     'ReviewerID, ReviewerName', 'PaperID, ReviewerID'], True, True)},
     short={'PaperID': 'PID', 'AuthorID': 'AID', 'AuthorName': 'AName', 'Department': 'Dept', 'Conference': 'Conf',
            'ReviewerID': 'RID', 'ReviewerName': 'RName'})
Prob('y23a', 'ABCD', 'A->B, B->C, C->D', keys=['A'], nf='2NF',
     decomps={'d': (['AB', 'AD', 'CD'], False, False)})
Prob('y23b', 'ABCDE', 'AB->C, C->D, D->E, A->C', keys=['AB'], nf='1NF',
     tnf=['AC', 'CD', 'DE', 'AB'], twonf=['AB', 'ACDE'],
     decomps={'t': (['AC', 'CD', 'DE', 'AB'], True, True),
              'd2': (['AB', 'ACDE'], True, True),          # decomposition approach, step 1 (2NF)
              'd3': (['AB', 'ACD', 'DE'], True, True),     # step 2: split off D -> E
              'bad': (['AB', 'CD', 'ACE'], True, False)})  # wrong order: C -> D split alone loses D -> E
Prob('y22b', 'ABCDE', 'A->B, BC->E, ED->A', keys=['ACD', 'BCD', 'CDE'], nf='3NF', superkeys=7)
Prob('y22c', 'ABCDE', 'A->BC, CD->E, B->D, E->A, B->E', keys=['A', 'B', 'E', 'CD'], nf='BCNF', superkeys=29,
     decomps={'d': (['ABC', 'ADE'], True, False)})
Prob('c23a', 'ABCDEFGH', 'CH->G, A->BC, B->CFH, E->A, F->EG', keys=['AD', 'BD', 'DE', 'DF'], nf='1NF',
     bcnf=['CGH', 'ABCEFH', 'AD'], decomps={'b': (['CGH', 'ABCEFH', 'AD'], True, True)})
Prob('c23b', 'ABCDEF', 'A->B, CD->AB, BC->D, AE->F, CE->DA', keys=['CE'], nf='2NF',
     decomps={'d': (['AB', 'ACD', 'BCD', 'AEF', 'CDE'], True, True)})
Prob('c23c', 'ABCDEH', 'BCD->H, A->BC, CD->E, E->C, D->AEH, ABH->BD, DH->C', keys=['D', 'AH'],
     cover='D -> A, D -> E, D -> H, A -> B, A -> C, E -> C, AH -> D')
Prob('m21a', 'ABCDE', 'ABC->D, CD->AE', keys=['ABC', 'BCD'], nf='1NF', superkeys=6,
     tnf=['ABCD', 'ACDE'], bcnf=['ACDE', 'BCD'],
     decomps={'t': (['ABCD', 'ACDE'], True, True), 'b': (['ACDE', 'BCD'], True, False)})
Prob('m21b', 'ABCDE', 'A->BCDE, BC->ADE', keys=['A', 'BC'], nf='BCNF', superkeys=20)

# ---------------------------------------------------------------- practice
Prob('pr1', 'ABCDEFG', 'AB->C, C->D, D->A, E->F, BF->E, CE->G',
     keys=['ABE', 'ABF', 'BCE', 'BCF', 'BDE', 'BDF'], nf='1NF', superkeys=42,
     tnf=['ABC', 'CD', 'AD', 'BEF', 'CEG', 'ABE'])
Prob('pr2', 'ABCDE', 'A->C, B->C, C->D, DE->C, CE->A', keys=['BE'], nf='1NF',
     decomps={'five': (['AD', 'AB', 'BE', 'CDE', 'AE'], True, False), 'four': (['AD', 'AB', 'BE', 'CDE'], False, False)})
Prob('pr3', 'ABCDE', 'AB->C, C->D, D->BE', keys=['AB', 'AC', 'AD'], nf='1NF', superkeys=14,
     tnf=['ABC', 'CD', 'BDE'], bcnf=['BDE', 'CD', 'AC'],
     decomps={'b': (['BDE', 'CD', 'AC'], True, False), 't': (['ABC', 'CD', 'BDE'], True, True)})
Prob('pr4', 'Flight, Date, Pilot, Gate, Plane, Time',
     'Flight Date -> Pilot Plane Gate; Flight -> Time; Plane Date Time -> Gate',
     keys=['Flight, Date'], nf='1NF',
     bcnf=['Flight, Time', 'Flight, Date, Pilot, Plane, Gate'],
     tnf=['Flight, Date, Pilot, Plane', 'Flight, Time', 'Plane, Date, Time, Gate'],
     decomps={'b': (['Flight, Time', 'Flight, Date, Pilot, Plane, Gate'], True, False),
              't': (['Flight, Date, Pilot, Plane', 'Flight, Time', 'Plane, Date, Time, Gate'], True, True)})
Prob('pr7', 'ABCDE', 'A->BC, CD->E, B->D, E->A', keys=['A', 'E', 'BC', 'CD'], nf='3NF', superkeys=27,
     bcnf=['BD', 'ABCE'],
     decomps={'x': (['ABC', 'CDE'], False, False), 'y': (['ABC', 'ADE'], True, False), 'b': (['BD', 'ABCE'], True, False)})
Prob('pr6a', 'ABC', 'A->BC, B->AC, C->AB', keys=['A', 'B', 'C'], nf='BCNF', cover='A -> B, B -> C, C -> A')
Prob('pr6b', 'ABC', 'A->BC, B->AC, C->AB', cover='A -> C, B -> C, C -> A, C -> B')

# ---------------------------------------------------------------- theory examples (sections 3-6)
Prob('korth', 'ABCGHI', 'A->B, A->C, CG->H, CG->I, B->H', keys=['AG'], nf='1NF')
Prob('kcover', 'ABC', 'A->BC, B->C, A->B, AB->C', keys=['A'], cover='A -> B, B -> C')
Prob('eqF', 'ACDEH', 'A->C, AC->D, E->AD, E->H', cover='A -> C, A -> D, E -> A, E -> H')

# ---------------------------------------------------------------- MCQ checks
Prob('q3', 'ABCD', 'A->B, B->C, C->D', keys=['A'], superkeys=8)
Prob('q8', 'ABCD', 'AB->C, C->D', keys=['AB'], nf='2NF')
Prob('q13', 'ABC', 'AB->C, C->A', keys=['AB', 'BC'], nf='3NF')
Prob('q12', 'ABC', 'A->B, B->C, A->C', cover='A -> B, B -> C')
Prob('y26c', 'ABCD', 'A->B, B->C, A->C, C->D', keys=['A'], nf='2NF', cover='A -> B, B -> C, C -> D',
     decomps={'l': (['AB', 'BCD'], True, True), 'x': (['AB', 'CD'], False, False), 'p': (['AB', 'BC', 'CD'], True, True)})
