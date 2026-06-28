-- Create Departments Table
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_name TEXT NOT NULL UNIQUE,
    budget INTEGER NOT NULL
);

-- Create Employees Table with a Foreign Key link
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    role TEXT NOT NULL,
    salary REAL NOT NULL,
    joining_date TEXT NOT NULL,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Seed initial department data for the company
INSERT OR IGNORE INTO departments (department_name, budget) VALUES 
('Backend Engineering', 1500000),
('Frontend UI/UX', 1200000),
('Data Science & AI', 2000000),
('Quality Assurance', 800000);