import streamlit as pd_stream
import sqlite3
import pandas as pd

# Page Configuration
pd_stream.set_page_config(page_title="Enterprise Employee Management System", layout="wide")
pd_stream.title("💼 Enterprise Employee Management System")
pd_stream.markdown("---")

# Helper function to connect to database
def get_db_connection():
    conn = sqlite3.connect("ems_database.db")
    conn.row_factory = sqlite3.Row
    return conn

# 1. DATABASE FETCHING FUNCTIONS
def fetch_departments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT department_id, department_name FROM departments")
    deps = cursor.fetchall()
    conn.close()
    return {row["department_name"]: row["department_id"] for row in deps}

def fetch_employee_dashboard():
    conn = get_db_connection()
    query = """
        SELECT 
            e.employee_id AS "ID",
            e.first_name || ' ' || e.last_name AS "Employee Name",
            e.role AS "Designation",
            e.salary AS "Salary ($)",
            e.joining_date AS "Joining Date",
            d.department_name AS "Department"
        FROM employees e
        LEFT JOIN departments d ON e.department_id = d.department_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def add_employee(first_name, last_name, role, salary, joining_date, dept_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO employees (first_name, last_name, role, salary, joining_date, department_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (first_name, last_name, role, salary, str(joining_date), dept_id))
    conn.commit()
    conn.close()

# Load current structural dropdown details
dept_mapping = fetch_departments()

# 2. SIDEBAR ENTRY FORM
pd_stream.sidebar.header("➕ Add New Employee")
with pd_stream.sidebar.form("employee_form", clear_on_submit=True):
    f_name = pd_stream.text_input("First Name")
    l_name = pd_stream.text_input("Last Name")
    emp_role = pd_stream.text_input("Job Role / Designation")
    emp_salary = pd_stream.number_input("Annual Salary", min_value=0.0, step=5000.0)
    join_date = pd_stream.date_input("Date of Joining")
    selected_dept = pd_stream.selectbox("Assign Department", list(dept_mapping.keys()))
    
    submit_btn = pd_stream.form_submit_button("Register Employee")
    
    if submit_btn:
        if f_name and l_name and emp_role:
            target_dept_id = dept_mapping[selected_dept]
            add_employee(f_name, l_name, emp_role, emp_salary, join_date, target_dept_id)
            pd_stream.sidebar.success(f"Successfully registered {f_name} {l_name}!")
        else:
            pd_stream.sidebar.error("Please fill in all text fields.")

# 3. DASHBOARD METRICS LAYER
df_employees = fetch_employee_dashboard()

col1, col2, col3 = pd_stream.columns(3)
with col1:
    pd_stream.metric("Total Active Workforce", len(df_employees))
with col2:
    pd_stream.metric("Registered Departments", len(dept_mapping))
with col3:
    total_payroll = df_employees["Salary ($)"].sum() if not df_employees.empty else 0
    pd_stream.metric("Total Annual Payroll Budget", f"${total_payroll:,.2f}")

pd_stream.markdown("### 📋 Current Active Employee Directory")

if df_employees.empty:
    pd_stream.info("No employees are currently registered in the database directory. Use the sidebar menu to add your first worker!")
else:
    # Filter tools
    search_query = pd_stream.text_input("🔍 Quick Search by Employee Name or Designation")
    if search_query:
        df_employees = df_employees[
            df_employees["Employee Name"].str.contains(search_query, case=False, na=False) |
            df_employees["Designation"].str.contains(search_query, case=False, na=False)
        ]
        
    pd_stream.dataframe(df_employees, use_container_width=True, hide_index=True)