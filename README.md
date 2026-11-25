# DBMS Notes (ITITC302)

Unit-wise study notes with diagrams and fully solved previous-year questions.

**Read online:** https://parv-005.github.io/dbms-notes/

| Unit | Folder | Topic |
|---|---|---|
| 2 | `unit2/` | Relational model, integrity constraints, relational algebra & calculus, SQL, triggers, NoSQL |
| 5 | `unit5/` | Transactions, concurrency control, recovery, security |

Each unit is a single self-contained `index.html` generated from `unitN/src/`:

```sh
cd unit2/src && python3 build.py ../index.html
```

Unit 2's SQL outputs are produced by executing the queries in SQLite and its relational-algebra results by a small RA engine;
expected answers are asserted, so a wrong answer fails the build.
