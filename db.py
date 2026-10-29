import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="karan@2001",
        database="employee_salary_db"
    )

if __name__ == "__main__":
    try:
        conn = get_connection()
        print("MySQL connection successful!")
        conn.close()

    except mysql.connector.Error as error:
        print("Connection failed:", error)