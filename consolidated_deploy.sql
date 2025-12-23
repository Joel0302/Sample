-- Consolidated Script Generated: Tue Dec 23 06:53:48 UTC 2025
-- Content from script1 --
CREATE TABLE IF NOT EXISTS employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    salary DECIMAL(10, 2),
    hire_date DATE DEFAULT CURRENT_DATE
);


INSERT INTO employees (first_name, last_name, department, salary)
VALUES ('John', 'Doe', 'Engineering', 85000.00);

-- Content from script2 --
CREATE OR REPLACE VIEW department_salary_summary AS
SELECT 
    department,
    COUNT(employee_id) AS total_employees,
    SUM(salary) AS total_budget,
    ROUND(AVG(salary), 2) AS average_salary
FROM 
    employees
GROUP BY 
    department;