# lib/department.py

from __init__ import CURSOR, CONN

from employee import Employee

class Department:
    """Represents a Department with database persistence"""

    # Dictionary to store objects saved to the database
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

        # Store in dictionary only if the instance has an id
        if self.id:
            type(self).all[self.id] = self

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """Creates the departments table if it does not exist."""
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                location TEXT
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """Drops the departments table."""
        sql = "DROP TABLE IF EXISTS departments"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Inserts or updates a department in the database."""
        if self.id:
            self.update()
        else:
            sql = "INSERT INTO departments (name, location) VALUES (?, ?)"
            CURSOR.execute(sql, (self.name, self.location))
            CONN.commit()

            self.id = CURSOR.lastrowid
            type(self).all[self.id] = self

    @classmethod
    def create(cls, name, location):
        """Creates a new Department instance and saves it to the database."""
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Updates the corresponding database record."""
        if self.id:
            sql = "UPDATE departments SET name = ?, location = ? WHERE id = ?"
            CURSOR.execute(sql, (self.name, self.location, self.id))
            CONN.commit()

    def delete(self):
        """Deletes the department from the database and removes it from memory."""
        if self.id:
            sql = "DELETE FROM departments WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()

            # Remove from dictionary and reset id
            del type(self).all[self.id]
            self.id = None

    @classmethod
    def instance_from_db(cls, row):
        """Returns a Department object corresponding to a database row."""
        department = cls.all.get(row[0])
        if department:
            department.name, department.location = row[1], row[2]
        else:
            department = cls(row[1], row[2], row[0])
        return department

    @classmethod
    def get_all(cls):
        """Retrieves all departments from the database."""
        sql = "SELECT * FROM departments"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        """Finds a department by ID."""
        sql = "SELECT * FROM departments WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Finds a department by name."""
        sql = "SELECT * FROM departments WHERE name = ?"
        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None
    
    def employees(self):
        """Returns a list of Employee instances belonging to this department."""
        return Employee.find_by_department(self.id) if self.id else []