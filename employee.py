
from db import get_connection


def add_employee():
    name = input("Enter employee name: ")
    email = input("Enter employee email: ")
    phone = input("Enter phone number: ")
    department_id = int(input("Enter department ID (1-4): "))
    designation = input("Enter designation: ")
    joining_date = input("Enter joining date (YYYY-MM-DD): ")
    basic_salary = float(input("Enter basic salary: "))
    hra = float(input("Enter HRA: "))
    other_allowance = float(input("Enter other allowance: "))

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO employees
    (employee_name, email, phone, department_id,
     designation, joining_date, basic_salary,
     hra, other_allowance)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        name, email, phone, department_id,
        designation, joining_date, basic_salary,
        hra, other_allowance
    )

    try:
        cursor.execute(query, values)
        conn.commit()
        print("Employee added successfully!")

    except Exception as error:
        conn.rollback()
        print("Error:", error)

    finally:
        cursor.close()
        conn.close()


def view_employees():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT e.employee_id, e.employee_name,
           e.email, d.department_name,
           e.designation, e.basic_salary
    FROM employees e
    LEFT JOIN departments d
        ON e.department_id = d.department_id
    ORDER BY e.employee_id
    """

    try:
        cursor.execute(query)
        employees = cursor.fetchall()

        if not employees:
            print("No employees found.")
        else:
            for employee in employees:
                print(employee)

    except Exception as error:
        print("Error:", error)

    finally:
        cursor.close()
        conn.close()


while True:
    print("\n--- Employee Salary Management ---")
    print("1. Add Employee")
    print("2. View Employees")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        add_employee()
    elif choice == "2":
        view_employees()
    elif choice == "3":
        print("Thank you!")
        break
    else:
        print("Invalid choice. Try again.")
