
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from db import get_connection

app = Flask(__name__)
app.secret_key = "employee-salary-demo-key"


# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM employees")
        total_employees = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM employees
            WHERE status = 'Active'
        """)
        active_employees = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM payroll")
        total_payrolls = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT d.department_name,
                   COUNT(e.employee_id) AS employee_count
            FROM departments d
            LEFT JOIN employees e
                ON d.department_id = e.department_id
            GROUP BY d.department_id, d.department_name
            ORDER BY d.department_name
        """)
        departments = cursor.fetchall()

        search = request.args.get("search", "").strip()
        selected_department = request.args.get("department", "").strip()
        selected_month = request.args.get("month", "").strip()

        query = """
            SELECT
                p.payroll_id,
                e.employee_name,
                d.department_name,
                p.salary_month,
                p.gross_salary,
                p.total_deductions,
                p.net_salary
            FROM payroll p
            JOIN employees e ON p.employee_id = e.employee_id
            LEFT JOIN departments d
                ON e.department_id = d.department_id
            WHERE e.employee_name LIKE %s
        """
        params = [f"%{search}%"]

        if selected_department:
            query += " AND d.department_name = %s"
            params.append(selected_department)

        if selected_month:
            query += " AND p.salary_month = %s"
            params.append(selected_month + "-01")

        query += " ORDER BY p.salary_month DESC"

        cursor.execute(query, tuple(params))
        payrolls = cursor.fetchall()

        cursor.execute("""
            SELECT
                salary_month,
                SUM(gross_salary) AS total_gross,
                SUM(total_deductions) AS total_deductions,
                SUM(net_salary) AS total_net
            FROM payroll
            GROUP BY salary_month
            ORDER BY salary_month DESC
        """)
        monthly_summary = cursor.fetchall()

        return render_template(
            "dashboard.html",
            total_employees=total_employees,
            active_employees=active_employees,
            total_payrolls=total_payrolls,
            departments=departments,
            payrolls=payrolls,
            monthly_summary=monthly_summary,
            search=search,
            selected_department=selected_department,
            selected_month=selected_month
        )

    except Exception as error:
        app.logger.exception("Dashboard error")
        return f"Dashboard error: {error}", 500

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


# ---------------- ADD EMPLOYEE ----------------
@app.route("/employees/add", methods=["GET", "POST"])
def add_employee():
    conn = None
    cursor = None

    try:
        conn = get_connection()

        if request.method == "POST":
            name = request.form.get(
                "employee_name", ""
            ).strip()

            email = request.form.get(
                "email", ""
            ).strip() or None

            phone = request.form.get(
                "phone", ""
            ).strip() or None

            department_text = request.form.get(
                "department_id", ""
            ).strip()

            designation = request.form.get(
                "designation", ""
            ).strip() or None

            joining_text = request.form.get(
                "joining_date", ""
            ).strip()

            basic_salary = request.form.get(
                "basic_salary", ""
            ).strip()

            hra = request.form.get(
                "hra", "0"
            ).strip() or "0"

            allowance = request.form.get(
                "other_allowance", "0"
            ).strip() or "0"

            if not name or not basic_salary:
                flash("Employee name and basic salary are required.")
                return redirect(url_for("add_employee"))

            try:
                basic_salary = float(basic_salary)
                hra = float(hra)
                allowance = float(allowance)

                if (
                    basic_salary < 0
                    or hra < 0
                    or allowance < 0
                ):
                    flash("Salary amounts cannot be negative.")
                    return redirect(url_for("add_employee"))

            except ValueError:
                flash("Please enter valid salary amounts.")
                return redirect(url_for("add_employee"))

            if department_text:
                department_id = int(department_text)

                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT department_id
                    FROM departments
                    WHERE department_id = %s
                    """,
                    (department_id,)
                )

                if cursor.fetchone() is None:
                    flash("Please select a valid department.")
                    return redirect(url_for("add_employee"))

                cursor.close()
                cursor = None
            else:
                department_id = None

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO employees
                (
                    employee_name,
                    email,
                    phone,
                    department_id,
                    designation,
                    joining_date,
                    basic_salary,
                    hra,
                    other_allowance,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                name,
                email,
                phone,
                department_id,
                designation,
                joining_text or None,
                basic_salary,
                hra,
                allowance,
                "Active"
            ))

            conn.commit()

            flash("Employee added successfully!")
            return redirect(url_for("add_employee"))

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT department_id, department_name
            FROM departments
            ORDER BY department_name
        """)

        departments = cursor.fetchall()

        return render_template(
            "add_employee.html",
            departments=departments
        )

    except Exception as error:
        if conn is not None:
            conn.rollback()

        app.logger.exception("Add employee failed")

        flash(f"Could not add employee: {error}")

        if request.method == "POST":
            return redirect(url_for("add_employee"))

        return (
            "Unable to load employee form. "
            "Check the Flask terminal.",
            500
        )

    finally:
        if cursor is not None:
            cursor.close()

        if conn is not None and conn.is_connected():
            conn.close()


# ---------------- RUN APPLICATION ----------------
if __name__ == "__main__":
    app.run(debug=True)
