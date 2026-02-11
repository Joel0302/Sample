CREATE TABLE IF NOT EXISTS employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    department VARCHAR(150),
    salary DECIMAL(10, 2),
    hire_date DATE DEFAULT CURRENT_DATE
);


INSERT INTO employees (first_name, last_name, department, salary)
VALUES ('John', 'Doe', 'Engineering', 95000.00);


