import sqlite3

CONN = sqlite3.connect("company.db")
CURSOR = CONN.cursor()

class Employee:
    def __init__(self, name, job_title, department_id, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department_id = department_id

    def get_department(self):
        from department import Department  # Local import
        return Department.find_by_id(self.department_id)

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT,
                job_title TEXT,
                department_id INTEGER,
                FOREIGN KEY(department_id) REFERENCES departments(id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CONN.commit()

    def save(self):
        CURSOR.execute("INSERT INTO employees (name, job_title, department_id) VALUES (?, ?, ?)",
                       (self.name, self.job_title, self.department_id))
        CONN.commit()
        self.id = CURSOR.lastrowid

    @classmethod
    def create(cls, name, job_title, department_id):
        employee = cls(name, job_title, department_id)
        employee.save()
        return employee

    def update(self):
        CURSOR.execute("UPDATE employees SET name=?, job_title=?, department_id=? WHERE id=?",
                       (self.name, self.job_title, self.department_id, self.id))
        CONN.commit()

    def delete(self):
        """Deletes the employee from the database and resets its id."""
        if self.id:
            CURSOR.execute("DELETE FROM employees WHERE id=?", (self.id,))
            CONN.commit()
            self.id = None  # Reset id after deletion


    @classmethod
    def instance_from_db(cls, row):
        return cls(id=row[0], name=row[1], job_title=row[2], department_id=row[3]) if row else None

    @classmethod
    def get_all(cls):
        rows = CURSOR.execute("SELECT * FROM employees").fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        row = CURSOR.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def find_by_name(cls, name):
        row = CURSOR.execute("SELECT * FROM employees WHERE name=?", (name,)).fetchone()
        return cls.instance_from_db(row)

    @classmethod
    def find_by_department(cls, department_id):
        rows = CURSOR.execute("SELECT * FROM employees WHERE department_id=?", (department_id,)).fetchall()
        return [cls.instance_from_db(row) for row in rows]
