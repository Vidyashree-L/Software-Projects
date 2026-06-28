import sqlite3

def init_database():
    conn = sqlite3.connect("ems_database.db")
    cursor = conn.cursor()
    
    # Read the SQL schema file
    with open("ems_schema.sql", "r") as f:
        sql_script = f.read()
        
    # Execute the script to create tables
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print("🚀 Employee Management Database initialized successfully with relational constraints!")

if __name__ == "__main__":
    init_database()