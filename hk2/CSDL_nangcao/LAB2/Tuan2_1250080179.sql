CREATE TABLE regions (
    region_id    NUMBER(5)    CONSTRAINT regions_pk PRIMARY KEY,
    region_name  VARCHAR2(25) NOT NULL
);

CREATE TABLE countries (
    country_id    CHAR(2)      CONSTRAINT countries_pk PRIMARY KEY,
    country_name  VARCHAR2(40) NOT NULL,
    region_id     NUMBER(5)    NOT NULL,
    CONSTRAINT countries_region_fk
        FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

CREATE TABLE locations (
    location_id     NUMBER(4)    CONSTRAINT locations_pk PRIMARY KEY,
    street_address  VARCHAR2(40),
    postal_code     VARCHAR2(12),
    city            VARCHAR2(30) NOT NULL,
    state_province  VARCHAR2(25),
    country_id      CHAR(2)      NOT NULL,
    CONSTRAINT locations_country_fk
        FOREIGN KEY (country_id) REFERENCES countries(country_id)
);

CREATE TABLE departments (
    department_id    NUMBER(4)    CONSTRAINT departments_pk PRIMARY KEY,
    department_name  VARCHAR2(30) NOT NULL,
    manager_id       NUMBER(6),
    location_id      NUMBER(4),
    CONSTRAINT departments_location_fk
        FOREIGN KEY (location_id) REFERENCES locations(location_id)
);

CREATE TABLE jobs (
    job_id       VARCHAR2(10) CONSTRAINT jobs_pk PRIMARY KEY,
    job_title    VARCHAR2(35) NOT NULL,
    min_salary   NUMBER(6),
    max_salary   NUMBER(6)
);

CREATE TABLE employees (
    employee_id      NUMBER(6)    CONSTRAINT employees_pk PRIMARY KEY,
    first_name       VARCHAR2(20),
    last_name        VARCHAR2(25) NOT NULL,
    email            VARCHAR2(25) NOT NULL,
    phone_number     VARCHAR2(20),
    hire_date        DATE         NOT NULL,
    job_id           VARCHAR2(10) NOT NULL,
    salary           NUMBER(8,2),
    commission_pct   NUMBER(3,2),
    manager_id       NUMBER(6),
    department_id    NUMBER(4),
    CONSTRAINT employees_job_fk
        FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    CONSTRAINT employees_department_fk
        FOREIGN KEY (department_id) REFERENCES departments(department_id),
    CONSTRAINT employees_manager_fk
        FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

CREATE TABLE job_history (
    employee_id    NUMBER(6)    NOT NULL,
    start_date     DATE         NOT NULL,
    end_date       DATE         NOT NULL,
    job_id         VARCHAR2(10) NOT NULL,
    department_id  NUMBER(4),
    CONSTRAINT job_history_pk PRIMARY KEY (employee_id, start_date),
    CONSTRAINT job_history_employee_fk
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    CONSTRAINT job_history_job_fk
        FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    CONSTRAINT job_history_department_fk
        FOREIGN KEY (department_id) REFERENCES departments(department_id),
    CONSTRAINT job_history_date_ck CHECK (end_date > start_date)
);

INSERT INTO regions (region_id, region_name) VALUES (1, 'Europe');
INSERT INTO regions (region_id, region_name) VALUES (2, 'Americas');
INSERT INTO regions (region_id, region_name) VALUES (3, 'Asia');
INSERT INTO regions (region_id, region_name) VALUES (4, 'Middle East and Africa');

INSERT INTO countries (country_id, country_name, region_id) VALUES ('US', 'United States of America', 2);
INSERT INTO countries (country_id, country_name, region_id) VALUES ('CA', 'Canada', 2);
INSERT INTO countries (country_id, country_name, region_id) VALUES ('UK', 'United Kingdom', 1);

INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id)
VALUES (1700, '2004 Charade Rd', '98199', 'Seattle', 'Washington', 'US');
INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id)
VALUES (1500, '2011 Interiors Blvd', '99236', 'South San Francisco', 'California', 'US');
INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id)
VALUES (1800, '147 Spadina Ave', 'M5V 2L7', 'Toronto', 'Ontario', 'CA');
INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id)
VALUES (2400, '8204 Arthur St', 'SW1 8JR', 'London', 'England', 'UK');
INSERT INTO locations (location_id, street_address, postal_code, city, state_province, country_id)
VALUES (2500, 'Magdalen Centre', 'OX9 9ZB', 'Oxford', 'Oxfordshire', 'UK');

INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (20,  'Marketing',         NULL, 1800);
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (40,  'Human Resources',   NULL, 2400);
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (50,  'Shipping',          NULL, 1500);
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (60,  'IT',                NULL, 1700);
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (70,  'Public Relations',  NULL, 1700);
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (80,  'Sales',             NULL, 2500);
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (90,  'Executive',         NULL, 1700);
INSERT INTO departments (department_id, department_name, manager_id, location_id) VALUES (500, 'Temporary Dept',    NULL, 1700);

INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('AD_PRES',  'President',             20000, 40000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('AD_VP',    'Administration Vice President', 15000, 30000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('ST_MAN',   'Stock Manager',          5500,  8500);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('ST_CLERK', 'Stock Clerk',           800,   5000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('IT_PROG',  'Programmer',            4000,  10000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('MK_MAN',   'Marketing Manager',     9000,  15000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('MK_REP',   'Marketing Representative', 4000, 9000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('SA_MAN',   'Sales Manager',         10000, 16000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('SA_REP',   'Sales Representative',  2000,  12000);
INSERT INTO jobs (job_id, job_title, min_salary, max_salary) VALUES ('HR_REP',   'Human Resources Representative', 3000, 6500);

PROMPT ===== 4. INSERT EMPLOYEES =====

INSERT INTO employees VALUES (1,  'Steven',    'King',     'SKING',     '515.123.4567', TO_DATE('17/06/1993', 'DD/MM/YYYY'), 'AD_PRES', 24000, NULL, NULL, 90);
INSERT INTO employees VALUES (2,  'Neena',     'Kochhar',  'NKOCHHAR',  '515.123.4568', TO_DATE('21/09/1994', 'DD/MM/YYYY'), 'AD_VP',   17000, NULL, 1,    90);
INSERT INTO employees VALUES (3,  'Lex',       'De Haan',  'LDEHAAN',   '515.123.4569', TO_DATE('13/01/1995', 'DD/MM/YYYY'), 'AD_VP',   17000, NULL, 1,    90);
INSERT INTO employees VALUES (4,  'Alexander', 'Hunold',   'AHUNOLD',   '590.423.4567', TO_DATE('03/01/1998', 'DD/MM/YYYY'), 'IT_PROG',  9000, NULL, 3,    60);
INSERT INTO employees VALUES (5,  'Bruce',     'Ernst',    'BERNST',    '590.423.4568', TO_DATE('21/05/1998', 'DD/MM/YYYY'), 'IT_PROG',  6000, NULL, 4,    60);
INSERT INTO employees VALUES (6,  'David',     'Austin',   'DAUSTIN',   '590.423.4569', TO_DATE('25/06/1996', 'DD/MM/YYYY'), 'IT_PROG',  4800, NULL, 4,    60);
INSERT INTO employees VALUES (7,  'Valli',     'Davies',   'VDAVIES',   '590.423.4570', TO_DATE('20/02/1998', 'DD/MM/YYYY'), 'IT_PROG',  4200, NULL, 4,    60);
INSERT INTO employees VALUES (8,  'Michael',   'Hartstein','MHARTSTE',  '515.123.5555', TO_DATE('17/02/1996', 'DD/MM/YYYY'), 'MK_MAN',  13000, NULL, 1,    20);
INSERT INTO employees VALUES (9,  'Pat',       'Fay',      'PFAY',      '515.123.5556', TO_DATE('17/08/1997', 'DD/MM/YYYY'), 'MK_REP',   6000, NULL, 8,    20);
INSERT INTO employees VALUES (10, 'Adam',      'Fripp',    'AFRIPP',    '650.123.1234', TO_DATE('10/04/1994', 'DD/MM/YYYY'), 'ST_MAN',   8200, NULL, 1,    50);
INSERT INTO employees VALUES (11, 'Shanta',    'Vollman',  'SVOLLMAN',  '650.123.2234', TO_DATE('10/03/1995', 'DD/MM/YYYY'), 'ST_CLERK', 2600, NULL, 10,   50);
INSERT INTO employees VALUES (12, 'Kevin',     'Mourgos',  'KMOURGOS',  '650.123.3234', TO_DATE('16/11/1996', 'DD/MM/YYYY'), 'ST_CLERK', 2500, NULL, 10,   50);
INSERT INTO employees VALUES (13, 'Julia',     'Nayer',    'JNAYER',    '650.123.4234', TO_DATE('15/07/1997', 'DD/MM/YYYY'), 'ST_CLERK', 3200, NULL, 10,   50);
INSERT INTO employees VALUES (14, 'TJ',        'Olson',    'TOLSON',    '650.123.5234', TO_DATE('30/03/1998', 'DD/MM/YYYY'), 'ST_CLERK',  800, NULL, 10,   50);
INSERT INTO employees VALUES (15, 'John',      'Russell',  'JRUSSELL',  '011.44.1344.429268', TO_DATE('01/10/1996', 'DD/MM/YYYY'), 'SA_MAN', 14000, 0.40, 1, 80);
INSERT INTO employees VALUES (16, 'Alyssa',    'James',    'AJAMES',    '011.44.1344.429267', TO_DATE('15/03/1997', 'DD/MM/YYYY'), 'SA_REP', 2400, 0.10, 15, 80);
INSERT INTO employees VALUES (17, 'Peter',     'Tucker',   'PTUCKER',   '011.44.1344.129267', TO_DATE('30/01/1997', 'DD/MM/YYYY'), 'SA_REP', 10000, 0.30, 15, 80);
INSERT INTO employees VALUES (18, 'Eleni',     'Zlotkey',  'EZLOTKEY',  '011.44.1344.129268', TO_DATE('29/01/1998', 'DD/MM/YYYY'), 'SA_REP', 10500, 0.20, 15, 80);
INSERT INTO employees VALUES (19, 'William',   'Taylor',   'WTAYLOR',   '011.44.1344.129269', TO_DATE('24/03/1998', 'DD/MM/YYYY'), 'SA_REP',  8600, 0.20, 15, 80);
INSERT INTO employees VALUES (20, 'Jennifer',  'Lee',      'JLEE',      '011.44.1344.129270', TO_DATE('01/05/1998', 'DD/MM/YYYY'), 'HR_REP',  3500, NULL, 2,    40);

UPDATE departments SET manager_id = 8  WHERE department_id = 20;
UPDATE departments SET manager_id = 20 WHERE department_id = 40;
UPDATE departments SET manager_id = 10 WHERE department_id = 50;
UPDATE departments SET manager_id = 4  WHERE department_id = 60;
UPDATE departments SET manager_id = 15 WHERE department_id = 80;
UPDATE departments SET manager_id = 1  WHERE department_id = 90;

ALTER TABLE departments
    ADD CONSTRAINT departments_manager_fk
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id);

INSERT INTO job_history (employee_id, start_date, end_date, job_id, department_id)
VALUES (7, TO_DATE('01/01/1997', 'DD/MM/YYYY'), TO_DATE('19/02/1998', 'DD/MM/YYYY'), 'ST_CLERK', 50);

INSERT INTO job_history (employee_id, start_date, end_date, job_id, department_id)
VALUES (20, TO_DATE('01/01/1997', 'DD/MM/YYYY'), TO_DATE('30/04/1998', 'DD/MM/YYYY'), 'MK_REP', 20);

COMMIT;

PROMPT ===== 5. QUICK CHECK =====

SELECT table_name
FROM   user_tables
WHERE  table_name IN ('REGIONS', 'COUNTRIES', 'LOCATIONS', 'DEPARTMENTS', 'JOBS', 'EMPLOYEES', 'JOB_HISTORY')
ORDER BY table_name;


-- Cau 1
SELECT last_name, salary
FROM   employees
WHERE  salary > 12000;

-- Cau 2
SELECT last_name, salary
FROM   employees
WHERE  salary < 5000 OR salary > 12000;

SELECT last_name, salary
FROM   employees
WHERE  salary NOT BETWEEN 5000 AND 12000;

-- Cau 3
SELECT last_name, job_id, hire_date
FROM   employees
WHERE  hire_date BETWEEN TO_DATE('20/02/1998', 'DD/MM/YYYY')
                     AND TO_DATE('01/05/1998', 'DD/MM/YYYY')
ORDER BY hire_date ASC;

-- Cau 4
SELECT last_name, department_id
FROM   employees
WHERE  department_id IN (20, 50)
ORDER BY last_name ASC;

-- Cau 5
SELECT last_name, hire_date
FROM   employees
WHERE  TO_CHAR(hire_date, 'YYYY') = '1994';

SELECT last_name, hire_date
FROM   employees
WHERE  hire_date BETWEEN TO_DATE('01/01/1994', 'DD/MM/YYYY')
                     AND TO_DATE('31/12/1994', 'DD/MM/YYYY');

-- Cau 6
SELECT last_name, job_id
FROM   employees
WHERE  manager_id IS NULL;

-- Cau 7
SELECT last_name, salary, commission_pct
FROM   employees
WHERE  commission_pct IS NOT NULL
ORDER BY salary DESC, commission_pct DESC;

-- Cau 8
SELECT last_name
FROM   employees
WHERE  last_name LIKE 'A%';

-- Cau 9
SELECT last_name
FROM   employees
WHERE  last_name LIKE '%a%'
AND    last_name LIKE '%e%';

-- Cau 10
SELECT last_name, job_id, salary
FROM   employees
WHERE  job_id IN ('SA_REP', 'ST_CLERK')
AND    salary NOT IN (2500, 3500, 7000);


-- Cau 11
SELECT employee_id,
       last_name,
       ROUND(salary * 1.15, 0) AS "New Salary"
FROM   employees;

-- Cau 12
SELECT INITCAP(last_name) AS "Ten Nhan Vien",
       LENGTH(last_name)  AS "Chieu Dai"
FROM   employees
WHERE  SUBSTR(last_name, 1, 1) IN ('J', 'A', 'L', 'M')
ORDER BY last_name ASC;

-- Cau 13
SELECT last_name,
       TRUNC(MONTHS_BETWEEN(SYSDATE, hire_date)) AS "So Thang Lam Viec"
FROM   employees
ORDER BY MONTHS_BETWEEN(SYSDATE, hire_date) ASC;

-- Cau 14
SELECT last_name || ' earns '
       || TO_CHAR(salary, '$99,999') || ' monthly but wants '
       || TO_CHAR(salary * 3, '$99,999') AS "Dream Salaries"
FROM   employees;

-- Cau 15
SELECT last_name,
       CASE
           WHEN commission_pct IS NULL THEN 'No commission'
           ELSE TO_CHAR(commission_pct)
       END AS "Commission"
FROM   employees;

SELECT last_name,
       NVL(TO_CHAR(commission_pct), 'No commission') AS "Commission"
FROM   employees;

-- Cau 16
SELECT job_id,
       DECODE(job_id,
              'AD_PRES',  'A',
              'ST_MAN',   'B',
              'IT_PROG',  'C',
              'SA_REP',   'D',
              'ST_CLERK', 'E',
              '0') AS "GRADE"
FROM   employees;

SELECT job_id,
       CASE job_id
           WHEN 'AD_PRES'  THEN 'A'
           WHEN 'ST_MAN'   THEN 'B'
           WHEN 'IT_PROG'  THEN 'C'
           WHEN 'SA_REP'   THEN 'D'
           WHEN 'ST_CLERK' THEN 'E'
           ELSE '0'
       END AS "GRADE"
FROM   employees;


-- Cau 17
SELECT e.last_name, e.department_id, d.department_name
FROM   employees e, departments d, locations l
WHERE  e.department_id = d.department_id
AND    d.location_id   = l.location_id
AND    UPPER(l.city)   = 'TORONTO';

-- Cau 18
SELECT e.employee_id AS "Ma NV",
       e.last_name   AS "Ten NV",
       m.employee_id AS "Ma Quan Ly",
       m.last_name   AS "Ten Quan Ly"
FROM   employees e, employees m
WHERE  e.manager_id = m.employee_id;

-- Cau 19
SELECT e1.last_name     AS "Nhan Vien 1",
       e2.last_name     AS "Nhan Vien 2",
       e1.department_id AS "Phong Ban"
FROM   employees e1, employees e2
WHERE  e1.department_id = e2.department_id
AND    e1.employee_id   < e2.employee_id
ORDER BY e1.department_id, e1.last_name;

-- Cau 20
SELECT last_name, hire_date
FROM   employees
WHERE  hire_date > (
           SELECT hire_date
           FROM   employees
           WHERE  last_name = 'Davies'
       );

-- Cau 21
SELECT e.last_name AS "Nhan Vien",
       e.hire_date AS "Ngay Vao",
       m.last_name AS "Quan Ly",
       m.hire_date AS "Quan Ly Vao"
FROM   employees e, employees m
WHERE  e.manager_id = m.employee_id
AND    e.hire_date  < m.hire_date;


-- Cau 22
SELECT job_id,
       MIN(salary)          AS "Luong Thap Nhat",
       MAX(salary)          AS "Luong Cao Nhat",
       ROUND(AVG(salary),2) AS "Luong Trung Binh",
       SUM(salary)          AS "Tong Luong"
FROM   employees
GROUP BY job_id
ORDER BY job_id;

-- Cau 23
SELECT d.department_id,
       d.department_name,
       COUNT(e.employee_id) AS "So Nhan Vien"
FROM   departments d
LEFT JOIN employees e
       ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name
ORDER BY d.department_id;

SELECT COUNT(*) AS "Tong NV",
       SUM(CASE WHEN TO_CHAR(hire_date, 'YYYY') = '1995' THEN 1 ELSE 0 END) AS "Nam 1995",
       SUM(CASE WHEN TO_CHAR(hire_date, 'YYYY') = '1996' THEN 1 ELSE 0 END) AS "Nam 1996",
       SUM(CASE WHEN TO_CHAR(hire_date, 'YYYY') = '1997' THEN 1 ELSE 0 END) AS "Nam 1997",
       SUM(CASE WHEN TO_CHAR(hire_date, 'YYYY') = '1998' THEN 1 ELSE 0 END) AS "Nam 1998"
FROM   employees;


-- Cau 25
SELECT last_name, hire_date
FROM   employees
WHERE  department_id = (
           SELECT department_id
           FROM   employees
           WHERE  last_name = 'Zlotkey'
       )
AND    last_name <> 'Zlotkey';

-- Cau 26
SELECT last_name, department_id, job_id
FROM   employees
WHERE  department_id IN (
           SELECT department_id
           FROM   departments
           WHERE  location_id = 1700
       );

-- Cau 27
SELECT last_name, manager_id
FROM   employees
WHERE  manager_id IN (
           SELECT employee_id
           FROM   employees
           WHERE  last_name = 'King'
       );

-- Cau 28
SELECT last_name, salary, department_id
FROM   employees
WHERE  salary > (SELECT AVG(salary) FROM employees)
AND    department_id IN (
           SELECT department_id
           FROM   employees
           WHERE  last_name LIKE '%n'
       );

-- Cau 29
SELECT department_id, department_name
FROM   departments d
WHERE  (
           SELECT COUNT(*)
           FROM   employees e
           WHERE  e.department_id = d.department_id
       ) < 3
ORDER BY department_id;

SELECT d.department_id,
       d.department_name,
       COUNT(e.employee_id) AS "So NV"
FROM   departments d
LEFT JOIN employees e
       ON d.department_id = e.department_id
GROUP BY d.department_id, d.department_name
HAVING COUNT(e.employee_id) < 3
ORDER BY d.department_id;

-- Cau 30
SELECT department_id, COUNT(*) AS "So Nhan Vien", 'Dong nhat' AS "Loai"
FROM   employees
GROUP BY department_id
HAVING COUNT(*) = (
           SELECT MAX(COUNT(*))
           FROM   employees
           GROUP BY department_id
       )
UNION ALL
SELECT department_id, COUNT(*), 'It nhat'
FROM   employees
GROUP BY department_id
HAVING COUNT(*) = (
           SELECT MIN(COUNT(*))
           FROM   employees
           GROUP BY department_id
       );

-- Cau 31
SELECT last_name,
       hire_date,
       TRIM(TO_CHAR(hire_date, 'Day')) AS "Thu trong tuan"
FROM   employees
WHERE  TRIM(TO_CHAR(hire_date, 'Day')) IN (
    SELECT TRIM(TO_CHAR(hire_date, 'Day'))
    FROM   employees
    GROUP BY TRIM(TO_CHAR(hire_date, 'Day'))
    HAVING COUNT(*) = (
        SELECT MAX(COUNT(*))
        FROM   employees
        GROUP BY TRIM(TO_CHAR(hire_date, 'Day'))
    )
);


-- Cau 32
SELECT last_name, salary
FROM (
    SELECT last_name, salary
    FROM   employees
    ORDER BY salary DESC
)
WHERE ROWNUM <= 3;

-- Cau 33
SELECT e.last_name, e.department_id
FROM   employees   e,
       departments d,
       locations   l
WHERE  e.department_id = d.department_id
AND    d.location_id   = l.location_id
AND    UPPER(l.state_province) = 'CALIFORNIA';

-- Cau 34
SELECT employee_id, last_name
FROM   employees
WHERE  employee_id = 3;

UPDATE employees
SET    last_name = 'Drexler'
WHERE  employee_id = 3;

COMMIT;

SELECT employee_id, last_name
FROM   employees
WHERE  employee_id = 3;

-- Cau 35
SELECT e1.last_name, e1.salary, e1.department_id
FROM   employees e1
WHERE  e1.salary < (
           SELECT AVG(e2.salary)
           FROM   employees e2
           WHERE  e2.department_id = e1.department_id
       )
ORDER BY e1.department_id;

-- Cau 36
SELECT employee_id, last_name, salary
FROM   employees
WHERE  salary < 900;

UPDATE employees
SET    salary = salary + 100
WHERE  salary < 900;

COMMIT;

-- Cau 37
SELECT COUNT(*)
FROM   employees
WHERE  department_id = 500;

DELETE FROM departments
WHERE  department_id = 500;

COMMIT;

UPDATE employees
SET    department_id = NULL
WHERE  department_id = 500;

DELETE FROM departments
WHERE  department_id = 500;

COMMIT;

-- Cau 38
SELECT department_id, department_name
FROM   departments
WHERE  department_id NOT IN (
           SELECT DISTINCT department_id
           FROM   employees
           WHERE  department_id IS NOT NULL
       );

DELETE FROM departments
WHERE  department_id NOT IN (
           SELECT DISTINCT department_id
           FROM   employees
           WHERE  department_id IS NOT NULL
       );

COMMIT;

DELETE FROM departments d
WHERE NOT EXISTS (
    SELECT 1
    FROM   employees e
    WHERE  e.department_id = d.department_id
);

ROLLBACK;
