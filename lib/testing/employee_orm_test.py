from __init__ import CONN, CURSOR
from employee import Employee
from department import Department
from faker import Faker
import pytest


class TestEmployee:
    '''Class Employee in employee.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''drop tables prior to each test.'''

        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")

        Department.all = {}
        Employee.all = {}

    def test_creates_table(self):
        '''contains method "create_table()" that creates table "employees" if it does not exist.'''

        Department.create_table()  # ensure Department table exists due to FK constraint
        Employee.create_table()
        assert (CURSOR.execute("SELECT * FROM employees"))

    def test_drops_table(self):
        '''contains method "drop_table()" that drops table "employees" if it exists.'''

        sql = """
            CREATE TABLE IF NOT EXISTS departments
                (id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT)
        """
        CURSOR.execute(sql)

        sql = """  
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)

        Employee.drop_table()

        # Confirm departments table exists
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='departments'
            LIMIT 1
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert (result)

        # Confirm employees table does not exist
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='employees'
            LIMIT 1
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert (result is None)

    def test_saves_employee(self):
        '''contains method "save()" that saves an Employee instance to the db and sets the instance id.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()  # tested in department_test.py

        Employee.create_table()
        employee = Employee("Sasha", "Manager", department.id)
        employee.save()

        sql = """
            SELECT * FROM employees
        """

        row = CURSOR.execute(sql).fetchone()
        assert ((row[0], row[1], row[2], row[3]) ==
                (employee.id, employee.name, employee.job_title, employee.department_id) ==
                (employee.id, "Sasha", "Manager", department.id))
