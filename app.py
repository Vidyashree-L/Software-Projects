import sqlite3
import streamlit as st
import pandas as pd

DB_FILE = "project_database.db"

def connect_to_db():
    try:
        return sqlite3.connect(DB_FILE)
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

def setup_database_table():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_tasks (
            task_id INTEGER PRIMARY KEY,
            task_name TEXT NOT NULL,
            category TEXT,
            status TEXT DEFAULT 'Pending'
        )
        """)
        conn.commit()
        conn.close()

def fetch_tasks_from_db():
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT task_id, task_name, category, status FROM project_tasks ORDER BY status DESC, task_id DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    return []

def add_task_to_db(task_id, name, category):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO project_tasks (task_id, task_name, category) VALUES (?, ?, ?)", (task_id, name, category))
            conn.commit()
            st.success(f"Task '{name}' added successfully!")
        except Exception as e:
            st.error(f"Error saving to Database: {e}")
        finally:
            conn.close()

def update_task_status(task_id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE project_tasks SET status = 'Completed' WHERE task_id = ?", (task_id,))
            conn.commit()
            st.toast(f"Task #{task_id} marked as completed!")
        except Exception as e:
            st.error(f"Error updating database: {e}")
        finally:
            conn.close()

def delete_task_from_db(task_id):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM project_tasks WHERE task_id = ?", (task_id,))
            conn.commit()
            st.toast(f"Task #{task_id} deleted successfully!")
        except Exception as e:
            st.error(f"Error deleting from Database: {e}")
        finally:
            conn.close()

# Initialize database
setup_database_table()

# --- STREAMLIT WEB INTERFACE ---
st.set_page_config(page_title="Project Task Tracker", layout="centered")

# Custom CSS styling for premium look
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    div[data-testid="stMetric"] { background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .task-header { font-weight: bold; color: #4f4f4f; border-bottom: 2px solid #e0e0e0; padding-bottom: 5px; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("📋 Enterprise Project Task Tracker")
st.write("Powered by Python & SQL Database Engine")

st.sidebar.header("Add New Task")
all_current_tasks = fetch_tasks_from_db()

# Calculate numbers for Metrics Cards
total_tasks = len(all_current_tasks)
completed_tasks = sum(1 for row in all_current_tasks if row[3] == "Completed")
pending_tasks = total_tasks - completed_tasks

# --- METRICS DISPLAY BLOCK ---
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric(label="Total Tasks", value=total_tasks)
with m_col2:
    st.metric(label="⏳ Pending", value=pending_tasks)
with m_col3:
    st.metric(label="✅ Completed", value=completed_tasks)

st.markdown("---")

# --- SIDEBAR INPUT LOGIC ---
next_id = max([row[0] for row in all_current_tasks]) + 1 if all_current_tasks else 1

new_task = st.sidebar.text_input("Task Name", placeholder="e.g., Run code analysis")
category = st.sidebar.selectbox("Category", ["Backend", "Frontend", "Database", "Testing"])

if st.sidebar.button("Add Task"):
    if new_task:
        add_task_to_db(next_id, new_task, category)
        st.rerun()
    else:
        st.sidebar.warning("Please enter a task name.")

# --- SEARCH AND FILTER INTERFACE ---
st.subheader("Current Tasks in Database")

search_col1, search_col2 = st.columns([2, 1])
with search_col1:
    search_query = st.text_input("🔍 Search by task name", placeholder="Type to search...").strip().lower()
with search_col2:
    filter_category = st.selectbox("📂 Filter by Category", ["All", "Backend", "Frontend", "Database", "Testing"])

# Filter the list
filtered_tasks = all_current_tasks
if filter_category != "All":
    filtered_tasks = [row for row in filtered_tasks if row[2] == filter_category]
if search_query:
    filtered_tasks = [row for row in filtered_tasks if search_query in row[1].lower()]

st.markdown("<br>", unsafe_allow_html=True)

# --- POLISHED TABLE HEADERS ---
if filtered_tasks:
    h_id, h_name, h_cat, h_act = st.columns([1, 3, 2, 2])
    with h_id: st.markdown("<div class='task-header'>ID</div>", unsafe_allow_html=True)
    with h_name: st.markdown("<div class='task-header'>Task Name</div>", unsafe_allow_html=True)
    with h_cat: st.markdown("<div class='task-header'>Details</div>", unsafe_allow_html=True)
    with h_act: st.markdown("<div class='task-header'>Actions</div>", unsafe_allow_html=True)

    # Display rows
    for row in filtered_tasks:
        is_completed = row[3] == "Completed"
        status_emoji = "✅" if is_completed else "⏳"
        
        col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 1, 1])
        
        with col1:
            st.write(f"**#{row[0]}**")
        with col2:
            if is_completed:
                st.markdown(f"<span style='color: #a0a0a0;'>~~{row[1]}~~</span>", unsafe_allow_html=True)
            else:
                st.write(row[1])
        with col3:
            st.caption(f"📂 {row[2]} | {status_emoji} {row[3]}")
        with col4:
            if not is_completed:
                if st.button("✅", key=f"done_{row[0]}"):
                    update_task_status(row[0])
                    st.rerun()
            else:
                st.write("")
        with col5:
            if st.button("🗑️", key=f"del_{row[0]}"):
                delete_task_from_db(row[0])
                st.rerun()
        st.markdown("<hr style='margin: 8px 0px; border-color: #f0f0f0;'>", unsafe_allow_html=True)
else:
    st.info("No matching tasks found.")

# --- VISUAL ANALYTICS CHART BLOCK ---
if all_current_tasks:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### 📊 Task Breakdown by Category")
    df = pd.DataFrame(all_current_tasks, columns=["ID", "Name", "Category", "Status"])
    chart_data = df["Category"].value_counts()
    st.bar_chart(chart_data)