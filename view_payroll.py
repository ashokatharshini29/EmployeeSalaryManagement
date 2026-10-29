
from db import get_connection


def view_payroll():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT
            p.payroll_id,
            e.employee_name,
            p.salary_month,
            p.gross_salary,
            p.total_deductions,
            p.net_salary
        FROM payroll p
        JOIN employees e
            ON p.employee_id = e.employee_id
        ORDER BY p.salary_month DESC
        """

        cursor.execute(query)
        records = cursor.fetchall()

        if not records:
            print("No payroll records found.")
            return

        print("\n===== EMPLOYEE SALARY REPORT =====")

        for row in records:
            print("-" * 35)
            print("Payroll ID:", row[0])
            print("Employee Name:", row[1])
            print("Salary Month:", row[2])
            print("Gross Salary: Rs.", row[3])
            print("Deductions: Rs.", row[4])
            print("Net Salary: Rs.", row[5])

        print("=" * 35)

    except Exception as error:
        print("Error:", error)

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    view_payroll()
