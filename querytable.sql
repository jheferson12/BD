
------------------------recupera registros en la tabla--------------------
SELECT * FROM employees WHERE email = 'example@example.com';
----------Obtener empleados y sus departamentos:---------------------------
SELECT e.employee_id, e.name, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id
ORDER BY e.employee_id;
------------------Mostrar empleados contratados en los últimos 30 días-------------------
SELECT e.employee_id, e.name, e.hire_date
FROM employees e
WHERE e.hire_date >= CURDATE() - INTERVAL 30 DAY;
---------------------Detectar correos electrónicos duplicados en empleados------------------
SELECT email, COUNT(*) AS occurrences
FROM employees
GROUP BY email
HAVING occurrences > 1;
----------------mostrar el total de empleados por posicion----------------------
SELECT position, COUNT(employee_id) AS total_employees
FROM employees
GROUP BY position
ORDER BY total_employees DESC;
------------------empleados que no tienen telefono registrado-----------------
SELECT employee_id, name, email FROM employees WHERE phone IS NULL;