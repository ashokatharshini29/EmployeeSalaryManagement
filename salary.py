
from db import get_connection
from decimal import Decimal
from datetime import datetime


def generate_salary():
    conn = None
    cursor = None

    try:
        # Get employee details
        employee_id = int(input("Enter Employee ID: "))
        salary_month = input("Enter salary month (YYYY-MM-01): ")

        # Validate salary month
        month_date = datetime.strptime(
            salary_month, "%Y-%m-%d"
        ).date()

        if month_date.day != 1:
            print("Please enter the first day of the month.")
            return

        # Connect to MySQL
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT employee_name, basic_salary, hra,
               other_allowance
        FROM employees
        WHERE employee_id = %s
          AND status = 'Active'
        """

        cursor.execute(query, (employee_id,))
        employee = cursor.fetchone()

        if employee is None:
            print("Employee not found or inactive.")
            return

        name, basic, hra, allowance = employee

        # Convert values to Decimal
        basic = Decimal(str(basic))
        hra = Decimal(str(hra or 0))
        allowance = Decimal(str(allowance or 0))

        # Calculate gross salary
        gross_salary = basic + hra + allowance

        # Example deductions
        pf = (basic * Decimal("0.12")).quantize(
            Decimal("0.01")
        )
        other_deductions = Decimal("200.00")

        total_deductions = pf + other_deductions
        net_salary = gross_salary - total_deductions

        # Display salary details
        print("\n========== SALARY DETAILS ==========")
        print("Employee ID:", employee_id)
        print("Employee Name:", name)
        print("Salary Month:", salary_month)
        print("------------------------------------")
        print(f"Basic Salary:      Rs. {basic:.2f}")
        print(f"HRA:               Rs. {hra:.2f}")
        print(f"Other Allowance:   Rs. {allowance:.2f}")
        print(f"Gross Salary:      Rs. {gross_salary:.2f}")
        print("------------------------------------")
        print(f"PF (example):      Rs. {pf:.2f}")
        print(f"Other Deduction:   Rs. {other_deductions:.2f}")
        print(f"Total Deductions:  Rs. {total_deductions:.2f}")
        print("------------------------------------")
        print(f"NET SALARY:        Rs. {net_salary:.2f}")
        print("====================================")

        # Save payroll
        save = input("Save payroll? (yes/no): ").strip().lower()

        if save == "yes":
            insert_query = """
            INSERT INTO payroll
            (employee_id, salary_month, gross_salary,
             total_deductions, net_salary)
            VALUES (%s, %s, %s, %s, %s)
            """

            values = (
                employee_id,
                month_date,
                gross_salary,
                total_deductions,
                net_salary
            )

            cursor.execute(insert_query, values)
            conn.commit()

            print("Payroll saved successfully!")

        else:
            print("Payroll was not saved.")

    except ValueError:
        print("Invalid input. Check employee ID or date format.")

    except Exception as error:
        if conn is not None and conn.is_connected():
            conn.rollback()

        print("Error:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    generate_salary()
