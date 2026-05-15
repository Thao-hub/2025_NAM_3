--DROP TABLE s_inventory;
--DROP TABLE s_warehouse;
--DROP TABLE s_item;
--DROP TABLE s_ord;
--DROP TABLE s_product;
--DROP TABLE s_longtext;
--DROP TABLE s_image;
--DROP TABLE s_customer;
--DROP TABLE s_emp;
--DROP TABLE s_title;
--DROP TABLE s_dept;
--DROP TABLE s_region;
-- Bước 2: Tạo bảng
-- s_region -> s_dept -> s_emp, s_customer, s_product -> s_ord -> s_item -> s_inventory, s_warehouse
-- tạo bảng s_region:
CREATE TABLE s_region (
    id NUMBER(7) CONSTRAINT s_region_id_pk PRIMARY KEY,
    name VARCHAR2(50) NOT NULL
);

-- tạo bảng s_dept (có khóa ngoại tham chiếu s_region):
CREATE TABLE s_dept (
    id NUMBER(7) CONSTRAINT s_dept_id_pk PRIMARY KEY,
    name VARCHAR2(25) NOT NULL,
    region_id NUMBER(7) CONSTRAINT s_dept_region_id_fk REFERENCES s_region(id)
);

-- tạo bảng s_title
CREATE TABLE s_title (
    title VARCHAR2(60) CONSTRAINT s_title_title_pk PRIMARY KEY
);

-- tạo bảng s_emp (có khóa ngoại tham chiếu s_emp, s_title, s_dept):
CREATE TABLE s_emp (
    id NUMBER(7) CONSTRAINT s_emp_id_pk PRIMARY KEY,
    last_name VARCHAR2(25) NOT NULL,
    first_name VARCHAR2(25),
    userid VARCHAR2(8) NOT NULL,
    start_date DATE,
    comments VARCHAR2(255),
    manager_id NUMBER(7) CONSTRAINT s_emp_manager_id_fk REFERENCES s_emp(id),
    title VARCHAR2(60) CONSTRAINT s_emp_title_fk REFERENCES s_title(title),
    dept_id NUMBER(7) CONSTRAINT s_emp_dept_id_fk REFERENCES s_dept(id),
    salary NUMBER(11,2),
    commission_pct NUMBER(4,2)
);

-- tạo bảng s_customer (có khóa ngoại tham chiếu s_emp, s_region):
CREATE TABLE s_customer (
    id NUMBER(7) CONSTRAINT s_customer_id_pk PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    phone VARCHAR2(25),
    address VARCHAR2(100),
    city VARCHAR2(30),
    state VARCHAR2(20),
    country VARCHAR2(30),
    zip_code VARCHAR2(75),
    credit_rating VARCHAR2(9),
    sales_rep_id NUMBER(7) CONSTRAINT s_customer_sales_rep_id_fk REFERENCES s_emp(id),
    region_id NUMBER(7) CONSTRAINT s_customer_region_id_fk REFERENCES s_region(id),
    comments VARCHAR2(255)
);

-- tạo bảng s_image
CREATE TABLE s_image (
    id NUMBER(7) CONSTRAINT s_image_id_pk PRIMARY KEY,
    format VARCHAR2(25),
    use_filename VARCHAR2(1),
    filename VARCHAR2(50),
    image BLOB
);

-- tạo bảng s_longtext
CREATE TABLE s_longtext (
    id NUMBER(7) CONSTRAINT s_longtext_id_pk PRIMARY KEY,
    use_filename VARCHAR2(1),
    filename VARCHAR2(50),
    text CLOB
);

-- tạo bảng s_product (có khóa ngoại tham chiếu s_longtext, s_image):
CREATE TABLE s_product (
    id NUMBER(7) CONSTRAINT s_product_id_pk PRIMARY KEY,
    name VARCHAR2(50) NOT NULL,
    short_desc VARCHAR2(255),
    longtext_id NUMBER(7) CONSTRAINT s_product_longtext_id_fk REFERENCES s_longtext(id),
    image_id NUMBER(7) CONSTRAINT s_product_image_id_fk REFERENCES s_image(id),
    suggested_whlsl_price NUMBER(11,2),
    whlsl_units VARCHAR2(25)
);

-- tạo bảng s_ord (có khóa ngoại tham chiếu s_customer, s_emp):
CREATE TABLE s_ord (
    id NUMBER(7) CONSTRAINT s_ord_id_pk PRIMARY KEY,
    customer_id NUMBER(7) CONSTRAINT s_ord_customer_id_fk REFERENCES s_customer(id),
    date_ordered DATE,
    date_shipped DATE,
    sales_rep_id NUMBER(7) CONSTRAINT s_ord_sales_rep_id_fk REFERENCES s_emp(id),
    total NUMBER(11,2),
    payment_type VARCHAR2(6),
    order_filled VARCHAR2(1)
);

-- tạo bảng s_item (có khóa ngoại tham chiếu s_ord, s_product):
CREATE TABLE s_item (
    ord_id NUMBER(7) CONSTRAINT s_item_ord_id_fk REFERENCES s_ord(id),
    item_id NUMBER(7),
    product_id NUMBER(7) CONSTRAINT s_item_product_id_fk REFERENCES s_product(id),
    price NUMBER(11,2),
    quantity NUMBER(9),
    quantity_shipped NUMBER(9),
    CONSTRAINT s_item_pk PRIMARY KEY (ord_id, item_id)
);

-- tạo bảng s_warehouse (có khóa ngoại tham chiếu s_region, s_emp):
CREATE TABLE s_warehouse (
    id NUMBER(7) CONSTRAINT s_warehouse_id_pk PRIMARY KEY,
    region_id NUMBER(7) CONSTRAINT s_warehouse_region_id_fk REFERENCES s_region(id),
    address VARCHAR2(100),
    city VARCHAR2(30),
    state VARCHAR2(20),
    country VARCHAR2(30),
    zip_code VARCHAR2(75),
    phone VARCHAR2(25),
    manager_id NUMBER(7) CONSTRAINT s_warehouse_manager_id_fk REFERENCES s_emp(id)
);

-- tạo bảng s_inventory (có khóa ngoại tham chiếu s_product, s_warehouse):
CREATE TABLE s_inventory (
    product_id NUMBER(7) CONSTRAINT s_inventory_product_id_fk REFERENCES s_product(id),
    warehouse_id NUMBER(7) CONSTRAINT s_inventory_warehouse_id_fk REFERENCES s_warehouse(id),
    amount_in_stock NUMBER(9),
    reorder_point NUMBER(9),
    max_in_stock NUMBER(9),
    out_of_stock_explanation VARCHAR2(255),
    restock_date DATE,
    CONSTRAINT s_inventory_pk PRIMARY KEY (product_id, warehouse_id)
);

-- Bước 3: Kiểm tra cấu trúc bảng sau khi tạo
DESC s_emp;
DESC s_dept;
DESC s_emp;
DESC s_dept;
DESC s_customer;
DESC s_product;
DESC s_ord;
DESC s_item;
DESC s_inventory;
DESC s_warehouse;

-- Xem danh sách tất cả bảng của user hiện tại:
SELECT table_name
FROM user_tables
ORDER BY table_name;

-- Bước 4: Nhập dữ liệu (INSERT) và xác nhận (COMMIT)
-- Nhập dữ liệu vào bảng s_region
INSERT INTO s_region VALUES (1, 'North America');
INSERT INTO s_region VALUES (2, 'South America');
INSERT INTO s_region VALUES (3, 'Asia');
INSERT INTO s_region VALUES (4, 'Europe');
INSERT INTO s_region VALUES (5, 'Africa');
INSERT INTO s_region VALUES (6, 'Oceania');
INSERT INTO s_region VALUES (7, 'Middle East');
INSERT INTO s_region VALUES (8, 'Central America');
INSERT INTO s_region VALUES (9, 'Caribbean');
INSERT INTO s_region VALUES (10, 'Eastern Europe');
INSERT INTO s_region VALUES (11, 'Western Europe');
INSERT INTO s_region VALUES (12, 'Southeast Asia');
INSERT INTO s_region VALUES (13, 'East Asia');
INSERT INTO s_region VALUES (14, 'South Asia');
INSERT INTO s_region VALUES (15, 'North Africa');
INSERT INTO s_region VALUES (16, 'Southern Africa');
INSERT INTO s_region VALUES (17, 'Nordic');
INSERT INTO s_region VALUES (18, 'Baltic');
INSERT INTO s_region VALUES (19, 'Pacific Islands');
INSERT INTO s_region VALUES (20, 'Central Asia');
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_dept
INSERT INTO s_dept VALUES (10, 'Administration', 1);
INSERT INTO s_dept VALUES (20, 'Sales', 2);
INSERT INTO s_dept VALUES (30, 'Marketing', 3);
INSERT INTO s_dept VALUES (40, 'Finance', 4);
INSERT INTO s_dept VALUES (50, 'HR', 5);
INSERT INTO s_dept VALUES (60, 'IT', 6);
INSERT INTO s_dept VALUES (70, 'Operations', 7);
INSERT INTO s_dept VALUES (80, 'Logistics', 8);
INSERT INTO s_dept VALUES (90, 'Procurement', 9);
INSERT INTO s_dept VALUES (100, 'Support', 10);
INSERT INTO s_dept VALUES (110, 'Legal', 11);
INSERT INTO s_dept VALUES (120, 'Research and Development', 12);
INSERT INTO s_dept VALUES (130, 'Retail', 13);
INSERT INTO s_dept VALUES (140, 'Wholesale', 14);
INSERT INTO s_dept VALUES (150, 'Export', 15);
INSERT INTO s_dept VALUES (160, 'Import', 16);
INSERT INTO s_dept VALUES (170, 'Training', 17);
INSERT INTO s_dept VALUES (180, 'Quality', 18);
INSERT INTO s_dept VALUES (190, 'Planning', 19);
INSERT INTO s_dept VALUES (200, 'Ecommerce', 20);
COMMIT;
-- Nhập dữ liệu vào bảng s_title
INSERT INTO s_title VALUES ('President');
INSERT INTO s_title VALUES ('Vice President');
INSERT INTO s_title VALUES ('Sales Director');
INSERT INTO s_title VALUES ('Sales Representative');
INSERT INTO s_title VALUES ('Marketing Manager');
INSERT INTO s_title VALUES ('Finance Manager');
INSERT INTO s_title VALUES ('HR Specialist');
INSERT INTO s_title VALUES ('IT Manager');
INSERT INTO s_title VALUES ('Warehouse Manager');
INSERT INTO s_title VALUES ('Logistics Coordinator');
INSERT INTO s_title VALUES ('Procurement Officer');
INSERT INTO s_title VALUES ('Support Lead');
INSERT INTO s_title VALUES ('Legal Counsel');
INSERT INTO s_title VALUES ('Research Analyst');
INSERT INTO s_title VALUES ('Retail Supervisor');
INSERT INTO s_title VALUES ('Wholesale Manager');
INSERT INTO s_title VALUES ('Export Specialist');
INSERT INTO s_title VALUES ('Import Specialist');
INSERT INTO s_title VALUES ('Quality Inspector');
INSERT INTO s_title VALUES ('Planning Analyst');
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_emp
INSERT INTO s_emp VALUES (1, 'Smith', 'John', 'JSMITH1', DATE '2021-01-15', 'Chief executive officer', NULL, 'President', 10, 12000, 0.00);
INSERT INTO s_emp VALUES (2, 'Johnson', 'Emily', 'EJOHNS2', DATE '2021-03-10', 'Regional vice president', 1, 'Vice President', 20, 9500, 0.00);
INSERT INTO s_emp VALUES (3, 'Williams', 'Michael', 'MWILLI3', DATE '2021-04-12', 'Leads global sales', 2, 'Sales Director', 10, 8200, 0.12);
INSERT INTO s_emp VALUES (4, 'Brown', 'Sarah', 'SBROWN4', DATE '2021-05-18', 'Handles enterprise accounts', 3, 'Sales Representative', 40, 4200, 0.08);
INSERT INTO s_emp VALUES (5, 'Jones', 'David', 'DJONES5', DATE '2021-06-20', 'B2B account manager', 3, 'Sales Representative', 50, 4300, 0.10);
INSERT INTO s_emp VALUES (6, 'Garcia', 'Maria', 'MGARCI6', DATE '2021-07-08', 'Brand and digital strategy', 2, 'Marketing Manager', 60, 6100, 0.00);
INSERT INTO s_emp VALUES (7, 'Miller', 'James', 'JMILLE7', DATE '2021-08-14', 'Budget oversight', 1, 'Finance Manager', 10, 6800, 0.00);
INSERT INTO s_emp VALUES (8, 'Davis', 'Linda', 'LDAVIS8', DATE '2021-09-03', 'Talent and payroll', 1, 'HR Specialist', 80, 3900, 0.00);
INSERT INTO s_emp VALUES (9, 'Rodriguez', 'Carlos', 'CRODRI9', DATE '2021-10-11', 'Application systems owner', 1, 'IT Manager', 90, 7300, 0.00);
INSERT INTO s_emp VALUES (10, 'Martinez', 'Ana', 'AMARTI10', DATE '2021-11-01', 'Main warehouse lead', 2, 'Warehouse Manager', 100, 5200, 0.00);
INSERT INTO s_emp VALUES (11, 'Hernandez', 'Luis', 'LHERN11', DATE '2022-01-07', 'Fleet and delivery routing', 10, 'Logistics Coordinator', 110, 4100, 0.00);
INSERT INTO s_emp VALUES (12, 'Lopez', 'Sofia', 'SLOPEZ12', DATE '2022-02-14', 'Vendor contracts', 7, 'Procurement Officer', 120, 4500, 0.00);
INSERT INTO s_emp VALUES (13, 'Gonzalez', 'Daniel', 'DGONZA13', DATE '2022-03-19', 'Customer support operations', 2, 'Support Lead', 130, 4000, 0.00);
INSERT INTO s_emp VALUES (14, 'Wilson', 'Olivia', 'OWILSO14', DATE '2022-04-25', 'Corporate legal matters', 1, 'Legal Counsel', 140, 7000, 0.00);
INSERT INTO s_emp VALUES (15, 'Anderson', 'Noah', 'NANDER15', DATE '2022-05-13', 'Market trend research', 6, 'Research Analyst', 150, 4300, 0.00);
INSERT INTO s_emp VALUES (16, 'Thomas', 'Emma', 'ETHOMA16', DATE '2022-06-21', 'Retail floor performance', 3, 'Retail Supervisor', 160, 3900, 0.05);
INSERT INTO s_emp VALUES (17, 'Taylor', 'Liam', 'LTAYLO17', DATE '2022-07-09', 'Wholesale key accounts', 3, 'Wholesale Manager', 170, 5600, 0.07);
INSERT INTO s_emp VALUES (18, 'Moore', 'Ava', 'AMOORE18', DATE '2022-08-17', 'Cross-border export sales', 17, 'Export Specialist', 180, 4700, 0.06);
INSERT INTO s_emp VALUES (19, 'Jackson', 'Ethan', 'EJACKS19', DATE '2022-09-23', 'Import documentation', 12, 'Import Specialist', 190, 4400, 0.00);
INSERT INTO s_emp VALUES (20, 'Martin', 'Mia', 'MMARTI20', DATE '2022-10-30', 'Product quality planning', 7, 'Quality Inspector', 200, 3800, 0.00);
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_customer
INSERT INTO s_customer VALUES (1, 'Walmart Inc', '+1-479-273-4000', '702 SW 8th St', 'Bentonville', 'Arkansas', 'USA', '72716', 'EXCELLENT', 4, 1, 'Mass retail customer');
INSERT INTO s_customer VALUES (2, 'Target Corporation', '+1-612-304-6073', '1000 Nicollet Mall', 'Minneapolis', 'Minnesota', 'USA', '55403', 'EXCELLENT', 5, 1, 'National retail chain');
INSERT INTO s_customer VALUES (3, 'Amazon Mexico', '+52-55-1234-5678', 'Paseo de la Reforma 250', 'Mexico City', 'CDMX', 'Mexico', '06600', 'GOOD', 4, 8, 'Marketplace partner');
INSERT INTO s_customer VALUES (4, 'Falabella Chile', '+56-2-2380-2000', 'Miraflores 383', 'Santiago', 'RM', 'Chile', '8320000', 'GOOD', 5, 2, 'Department store group');
INSERT INTO s_customer VALUES (5, 'Aeon Vietnam', '+84-28-3520-9999', '30 Bo Bao Tan Thang', 'Ho Chi Minh City', 'HCM', 'Vietnam', '700000', 'EXCELLENT', 17, 12, 'Hypermarket partner');
INSERT INTO s_customer VALUES (6, 'Lotte Mart Korea', '+82-2-2145-8000', '300 Olympic-ro', 'Seoul', 'Seoul', 'Korea', '05551', 'GOOD', 17, 13, 'Retail customer');
INSERT INTO s_customer VALUES (7, 'Reliance Retail', '+91-22-3555-3800', 'Maker Chambers IV', 'Mumbai', 'Maharashtra', 'India', '400021', 'EXCELLENT', 18, 14, 'Large wholesale account');
INSERT INTO s_customer VALUES (8, 'Carrefour France', '+33-1-60-91-37-72', '93 Avenue de Paris', 'Massy', 'Ile-de-France', 'France', '91300', 'EXCELLENT', 16, 11, 'European supermarket');
INSERT INTO s_customer VALUES (9, 'Tesco UK', '+44-1992-632222', 'Shire Park', 'Welwyn Garden City', 'Herts', 'UK', 'AL7 1GA', 'GOOD', 16, 4, 'Retail supermarket');
INSERT INTO s_customer VALUES (10, 'IKEA Sweden', '+46-8-795-0000', 'Box 702', 'Almhult', 'Kronoberg', 'Sweden', '34381', 'GOOD', 16, 17, 'Home retail account');
INSERT INTO s_customer VALUES (11, 'Shoprite Nigeria', '+234-1-271-6500', 'Adeniran Ogunsanya', 'Lagos', 'Lagos', 'Nigeria', '101241', 'FAIR', 18, 5, 'Regional chain');
INSERT INTO s_customer VALUES (12, 'Pick n Pay SA', '+27-21-658-1000', 'Main Road', 'Cape Town', 'Western Cape', 'South Africa', '7800', 'GOOD', 18, 16, 'Retail grocery account');
INSERT INTO s_customer VALUES (13, 'Majid Al Futtaim', '+971-4-294-9999', 'Deira City Centre', 'Dubai', 'Dubai', 'UAE', '114100', 'EXCELLENT', 17, 7, 'Mall and retail partner');
INSERT INTO s_customer VALUES (14, 'Cencosud Peru', '+51-1-712-6000', 'Av El Derby 254', 'Lima', 'Lima', 'Peru', '15023', 'GOOD', 5, 2, 'Peru retail chain');
INSERT INTO s_customer VALUES (15, 'PriceSmart Costa Rica', '+506-800-800-8047', 'Escazu', 'San Jose', 'San Jose', 'Costa Rica', '10203', 'GOOD', 4, 8, 'Warehouse club customer');
INSERT INTO s_customer VALUES (16, 'SuperValu Ireland', '+353-1-293-8000', 'Ballymun', 'Dublin', 'Dublin', 'Ireland', 'D11', 'FAIR', 16, 11, 'Irish retail chain');
INSERT INTO s_customer VALUES (17, 'El Corte Ingles', '+34-91-401-8500', 'Calle Hermosilla 112', 'Madrid', 'Madrid', 'Spain', '28009', 'GOOD', 16, 11, 'Department store');
INSERT INTO s_customer VALUES (18, 'NTUC FairPrice', '+65-6380-5858', 'Joo Koon Circle', 'Singapore', 'Singapore', 'Singapore', '629117', 'EXCELLENT', 17, 12, 'Singapore retail');
INSERT INTO s_customer VALUES (19, 'Migros Turkey', '+90-212-321-3434', 'Ataturk Mah', 'Istanbul', 'Istanbul', 'Turkey', '34758', 'GOOD', 18, 7, 'Retail chain customer');
INSERT INTO s_customer VALUES (20, 'Lulu Oman', '+968-2459-1200', 'Bausher', 'Muscat', 'Muscat', 'Oman', '130', 'GOOD', 18, 7, 'Gulf region account');
INSERT INTO s_customer VALUES (21, 'Metro India', '+91-80-6678-0000', 'Hosur Road', 'Bangalore', 'Karnataka', 'India', '560068', 'GOOD', 18, 14, 'New retail customer');

COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_image
INSERT INTO s_image VALUES (1, 'JPG', 'Y', 'mountain_bike.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (2, 'JPG', 'Y', 'road_bike.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (3, 'PNG', 'Y', 'city_bike.png', EMPTY_BLOB());
INSERT INTO s_image VALUES (4, 'JPG', 'Y', 'helmet.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (5, 'PNG', 'Y', 'gloves.png', EMPTY_BLOB());
INSERT INTO s_image VALUES (6, 'JPG', 'Y', 'water_bottle.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (7, 'JPG', 'Y', 'bike_lock.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (8, 'PNG', 'Y', 'front_light.png', EMPTY_BLOB());
INSERT INTO s_image VALUES (9, 'JPG', 'Y', 'rear_light.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (10, 'PNG', 'Y', 'pump.png', EMPTY_BLOB());
INSERT INTO s_image VALUES (11, 'JPG', 'Y', 'repair_kit.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (12, 'JPG', 'Y', 'cycling_jersey.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (13, 'PNG', 'Y', 'cycling_shorts.png', EMPTY_BLOB());
INSERT INTO s_image VALUES (14, 'JPG', 'Y', 'saddle_bag.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (15, 'JPG', 'Y', 'phone_mount.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (16, 'PNG', 'Y', 'kid_bike.png', EMPTY_BLOB());
INSERT INTO s_image VALUES (17, 'JPG', 'Y', 'electric_bike.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (18, 'PNG', 'Y', 'folding_bike.png', EMPTY_BLOB());
INSERT INTO s_image VALUES (19, 'JPG', 'Y', 'bike_trainer.jpg', EMPTY_BLOB());
INSERT INTO s_image VALUES (20, 'PNG', 'Y', 'smart_computer.png', EMPTY_BLOB());
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_longtext
INSERT INTO s_longtext VALUES (1, 'N', 'NA', 'Aluminum mountain bike for trail and urban riding.');
INSERT INTO s_longtext VALUES (2, 'N', 'NA', 'Lightweight road bike designed for endurance training.');
INSERT INTO s_longtext VALUES (3, 'N', 'NA', 'Comfort city bike with basket and upright geometry.');
INSERT INTO s_longtext VALUES (4, 'N', 'NA', 'Impact resistant cycling helmet with ventilation.');
INSERT INTO s_longtext VALUES (5, 'N', 'NA', 'Breathable cycling gloves with gel palm padding.');
INSERT INTO s_longtext VALUES (6, 'N', 'NA', 'Insulated bottle suitable for long distance rides.');
INSERT INTO s_longtext VALUES (7, 'N', 'NA', 'Steel cable lock for daily commuter protection.');
INSERT INTO s_longtext VALUES (8, 'N', 'NA', 'Rechargeable front light with USB charging.');
INSERT INTO s_longtext VALUES (9, 'N', 'NA', 'Compact rear safety light with multiple modes.');
INSERT INTO s_longtext VALUES (10, 'N', 'NA', 'Portable hand pump compatible with presta and schrader.');
INSERT INTO s_longtext VALUES (11, 'N', 'NA', 'Emergency repair kit including patches and tire levers.');
INSERT INTO s_longtext VALUES (12, 'N', 'NA', 'Quick dry jersey for road and gravel cycling.');
INSERT INTO s_longtext VALUES (13, 'N', 'NA', 'Padded bib shorts for comfort on longer routes.');
INSERT INTO s_longtext VALUES (14, 'N', 'NA', 'Water resistant saddle bag with reflective trim.');
INSERT INTO s_longtext VALUES (15, 'N', 'NA', 'Adjustable phone mount for navigation on the bike.');
INSERT INTO s_longtext VALUES (16, 'N', 'NA', 'Kids bike with training wheel compatibility.');
INSERT INTO s_longtext VALUES (17, 'N', 'NA', 'Electric bike with pedal assist and removable battery.');
INSERT INTO s_longtext VALUES (18, 'N', 'NA', 'Folding bike built for compact storage and commuting.');
INSERT INTO s_longtext VALUES (19, 'N', 'NA', 'Indoor smart trainer for structured bicycle workouts.');
INSERT INTO s_longtext VALUES (20, 'N', 'NA', 'GPS bike computer with navigation and ride analytics.');
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_product
INSERT INTO s_product VALUES (1, 'Trail Mountain Bike', '29 inch trail mountain bicycle', 1, 1, 899.00, 'EA');
INSERT INTO s_product VALUES (2, 'Carbon Road Bike', 'Performance road bicycle', 2, 2, 1499.00, 'EA');
INSERT INTO s_product VALUES (3, 'Comfort City Bike', 'Urban city bicycle with basket', 3, 3, 599.00, 'EA');
INSERT INTO s_product VALUES (4, 'Aero Helmet', 'Protective cycling helmet', 4, 4, 79.00, 'EA');
INSERT INTO s_product VALUES (5, 'Ride Gloves', 'Breathable cycling gloves', 5, 5, 24.00, 'PR');
INSERT INTO s_product VALUES (6, 'Thermal Bottle', 'Insulated water bottle', 6, 6, 15.00, 'EA');
INSERT INTO s_product VALUES (7, 'Secure Bike Lock', 'High strength cable lock', 7, 7, 35.00, 'EA');
INSERT INTO s_product VALUES (8, 'Front Light 800', 'USB rechargeable front light', 8, 8, 45.00, 'EA');
INSERT INTO s_product VALUES (9, 'Rear Safety Light', 'Compact rear bike light', 9, 9, 18.00, 'EA');
INSERT INTO s_product VALUES (10, 'Mini Pump Pro', 'Portable bike pump', 10, 10, 28.00, 'EA');
INSERT INTO s_product VALUES (11, 'Flat Repair Kit', 'Patch and tire lever kit', 11, 11, 12.00, 'EA');
INSERT INTO s_product VALUES (12, 'Cycling Jersey', 'Quick dry jersey top', 12, 12, 42.00, 'EA');
INSERT INTO s_product VALUES (13, 'Bib Shorts Elite', 'Padded cycling shorts', 13, 13, 65.00, 'EA');
INSERT INTO s_product VALUES (14, 'Saddle Bag Compact', 'Water resistant saddle bag', 14, 14, 29.00, 'EA');
INSERT INTO s_product VALUES (15, 'Phone Mount Plus', 'Handlebar phone holder', 15, 15, 22.00, 'EA');
INSERT INTO s_product VALUES (16, 'Kids Bike 20', 'Kids bicycle 20 inch', 16, 16, 199.00, 'EA');
INSERT INTO s_product VALUES (17, 'Urban E-Bike', 'Electric commuter bicycle', 17, 17, 1799.00, 'EA');
INSERT INTO s_product VALUES (18, 'FoldGo Bike', 'Compact folding bicycle', 18, 18, 749.00, 'EA');
INSERT INTO s_product VALUES (19, 'Smart Trainer X', 'Indoor bike trainer', 19, 19, 499.00, 'EA');
INSERT INTO s_product VALUES (20, 'GPS Bike Computer', 'Cycling computer with GPS', 20, 20, 159.00, 'EA');
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_ord
INSERT INTO s_ord VALUES (101, 1, DATE '2025-01-10', DATE '2025-01-14', 4, 899.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (102, 2, DATE '2025-01-11', DATE '2025-01-15', 5, 1499.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (103, 3, DATE '2025-01-12', DATE '2025-01-16', 4, 1198.00, 'CASH', 'Y');
INSERT INTO s_ord VALUES (104, 4, DATE '2025-01-13', DATE '2025-01-18', 5, 237.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (105, 5, DATE '2025-01-14', DATE '2025-01-19', 17, 90.00, 'BANK', 'Y');
INSERT INTO s_ord VALUES (106, 6, DATE '2025-01-15', DATE '2025-01-20', 17, 84.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (107, 7, DATE '2025-01-16', DATE '2025-01-21', 18, 130.00, 'BANK', 'Y');
INSERT INTO s_ord VALUES (108, 8, DATE '2025-01-17', DATE '2025-01-22', 16, 116.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (109, 9, DATE '2025-01-18', DATE '2025-01-23', 16, 44.00, 'CASH', 'Y');
INSERT INTO s_ord VALUES (110, 10, DATE '2025-01-19', DATE '2025-01-24', 16, 199.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (111, 11, DATE '2025-01-20', DATE '2025-01-25', 18, 1799.00, 'BANK', 'Y');
INSERT INTO s_ord VALUES (112, 12, DATE '2025-01-21', DATE '2025-01-26', 18, 749.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (113, 13, DATE '2025-01-22', DATE '2025-01-27', 17, 499.00, 'BANK', 'Y');
INSERT INTO s_ord VALUES (114, 14, DATE '2025-01-23', DATE '2025-01-28', 5, 159.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (115, 15, DATE '2025-01-24', DATE '2025-01-29', 4, 928.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (116, 16, DATE '2025-01-25', DATE '2025-01-30', 16, 564.00, 'BANK', 'Y');
INSERT INTO s_ord VALUES (117, 17, DATE '2025-01-26', DATE '2025-01-31', 16, 219.00, 'CASH', 'Y');
INSERT INTO s_ord VALUES (118, 18, DATE '2025-01-27', DATE '2025-02-01', 17, 177.00, 'CARD', 'Y');
INSERT INTO s_ord VALUES (119, 19, DATE '2025-01-28', DATE '2025-02-02', 18, 95.00, 'BANK', 'Y');
INSERT INTO s_ord VALUES (120, 20, DATE '2025-01-29', DATE '2025-02-03', 18, 302.00, 'CARD', 'Y');
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_item
INSERT INTO s_item VALUES (101, 1, 1, 899.00, 1, 1);
INSERT INTO s_item VALUES (102, 1, 2, 1499.00, 1, 1);
INSERT INTO s_item VALUES (103, 1, 3, 599.00, 2, 2);
INSERT INTO s_item VALUES (104, 1, 4, 79.00, 3, 3);
INSERT INTO s_item VALUES (105, 1, 8, 45.00, 2, 2);
INSERT INTO s_item VALUES (106, 1, 12, 42.00, 2, 2);
INSERT INTO s_item VALUES (107, 1, 13, 65.00, 2, 2);
INSERT INTO s_item VALUES (108, 1, 14, 29.00, 4, 4);
INSERT INTO s_item VALUES (109, 1, 15, 22.00, 2, 2);
INSERT INTO s_item VALUES (110, 1, 16, 199.00, 1, 1);
INSERT INTO s_item VALUES (111, 1, 17, 1799.00, 1, 1);
INSERT INTO s_item VALUES (112, 1, 18, 749.00, 1, 1);
INSERT INTO s_item VALUES (113, 1, 19, 499.00, 1, 1);
INSERT INTO s_item VALUES (114, 1, 20, 159.00, 1, 1);
INSERT INTO s_item VALUES (115, 1, 1, 899.00, 1, 1);
INSERT INTO s_item VALUES (116, 1, 6, 15.00, 4, 4);
INSERT INTO s_item VALUES (117, 1, 7, 35.00, 3, 3);
INSERT INTO s_item VALUES (118, 1, 9, 18.00, 3, 3);
INSERT INTO s_item VALUES (119, 1, 10, 28.00, 2, 2);
INSERT INTO s_item VALUES (120, 1, 11, 12.00, 2, 2);
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_warehouse
INSERT INTO s_warehouse VALUES (1, 1, '1200 Commerce Ave', 'Dallas', 'Texas', 'USA', '75201', '+1-214-555-0101', 10);
INSERT INTO s_warehouse VALUES (2, 2, '45 Port Road', 'Sao Paulo', 'SP', 'Brazil', '01000-000', '+55-11-5555-0102', 11);
INSERT INTO s_warehouse VALUES (3, 3, '88 Harbour Street', 'Singapore', 'Singapore', 'Singapore', '018989', '+65-6555-0103', 10);
INSERT INTO s_warehouse VALUES (4, 4, '14 Logistics Park', 'Rotterdam', 'ZH', 'Netherlands', '3011', '+31-10-555-0104', 11);
INSERT INTO s_warehouse VALUES (5, 5, '200 Trade Lane', 'Cairo', 'Cairo', 'Egypt', '11511', '+20-2-5555-0105', 20);
INSERT INTO s_warehouse VALUES (6, 6, '7 Harbor Drive', 'Sydney', 'NSW', 'Australia', '2000', '+61-2-5555-0106', 10);
INSERT INTO s_warehouse VALUES (7, 7, '5 Gulf Storage', 'Dubai', 'Dubai', 'UAE', '114100', '+971-4-555-0107', 11);
INSERT INTO s_warehouse VALUES (8, 8, '101 Canal Ave', 'Panama City', 'Panama', 'Panama', '0801', '+507-555-0108', 10);
INSERT INTO s_warehouse VALUES (9, 9, '22 Bay Street', 'Kingston', 'Kingston', 'Jamaica', '00010', '+1-876-555-0109', 11);
INSERT INTO s_warehouse VALUES (10, 10, '9 Rail Hub', 'Warsaw', 'Mazovia', 'Poland', '00-001', '+48-22-555-0110', 20);
INSERT INTO s_warehouse VALUES (11, 11, '11 Market Road', 'Paris', 'Ile-de-France', 'France', '75001', '+33-1-5555-0111', 10);
INSERT INTO s_warehouse VALUES (12, 12, '77 River Park', 'Ho Chi Minh City', 'HCM', 'Vietnam', '700000', '+84-28-5555-0112', 11);
INSERT INTO s_warehouse VALUES (13, 13, '36 Sakura Ave', 'Osaka', 'Osaka', 'Japan', '530-0001', '+81-6-5555-0113', 10);
INSERT INTO s_warehouse VALUES (14, 14, '18 Cargo Street', 'Mumbai', 'Maharashtra', 'India', '400001', '+91-22-5555-0114', 11);
INSERT INTO s_warehouse VALUES (15, 15, '3 Sahara Depot', 'Casablanca', 'Casablanca', 'Morocco', '20000', '+212-5-5555-0115', 20);
INSERT INTO s_warehouse VALUES (16, 16, '42 Cape Route', 'Cape Town', 'Western Cape', 'South Africa', '8001', '+27-21-555-0116', 10);
INSERT INTO s_warehouse VALUES (17, 17, '6 Nordic Way', 'Stockholm', 'Stockholm', 'Sweden', '11120', '+46-8-5555-0117', 11);
INSERT INTO s_warehouse VALUES (18, 18, '25 Baltic Port', 'Riga', 'Riga', 'Latvia', 'LV-1010', '+371-6-5555-0118', 20);
INSERT INTO s_warehouse VALUES (19, 19, '12 Island Loop', 'Suva', 'Central', 'Fiji', '00001', '+679-555-0119', 10);
INSERT INTO s_warehouse VALUES (20, 20, '55 Silk Road Hub', 'Almaty', 'Almaty', 'Kazakhstan', '050000', '+7-727-555-0120', 11);
COMMIT; -- Xác nhận lưu dữ liệu
-- Nhập dữ liệu vào bảng s_inventory
INSERT INTO s_inventory VALUES (1, 1, 25, 5, 60, NULL, DATE '2025-02-10');
INSERT INTO s_inventory VALUES (2, 2, 18, 4, 40, NULL, DATE '2025-02-11');
INSERT INTO s_inventory VALUES (3, 3, 30, 6, 70, NULL, DATE '2025-02-12');
INSERT INTO s_inventory VALUES (4, 4, 120, 20, 200, NULL, DATE '2025-02-13');
INSERT INTO s_inventory VALUES (5, 5, 150, 25, 250, NULL, DATE '2025-02-14');
INSERT INTO s_inventory VALUES (6, 6, 200, 30, 320, NULL, DATE '2025-02-15');
INSERT INTO s_inventory VALUES (7, 7, 95, 15, 160, NULL, DATE '2025-02-16');
INSERT INTO s_inventory VALUES (8, 8, 88, 12, 140, NULL, DATE '2025-02-17');
INSERT INTO s_inventory VALUES (9, 9, 110, 18, 180, NULL, DATE '2025-02-18');
INSERT INTO s_inventory VALUES (10, 10, 76, 10, 150, NULL, DATE '2025-02-19');
INSERT INTO s_inventory VALUES (11, 11, 160, 25, 260, NULL, DATE '2025-02-20');
INSERT INTO s_inventory VALUES (12, 12, 70, 10, 140, NULL, DATE '2025-02-21');
INSERT INTO s_inventory VALUES (13, 13, 64, 10, 120, NULL, DATE '2025-02-22');
INSERT INTO s_inventory VALUES (14, 14, 82, 12, 150, NULL, DATE '2025-02-23');
INSERT INTO s_inventory VALUES (15, 15, 90, 15, 170, NULL, DATE '2025-02-24');
INSERT INTO s_inventory VALUES (16, 16, 40, 8, 90, NULL, DATE '2025-02-25');
INSERT INTO s_inventory VALUES (17, 17, 12, 3, 30, NULL, DATE '2025-02-26');
INSERT INTO s_inventory VALUES (18, 18, 22, 5, 50, NULL, DATE '2025-02-27');
INSERT INTO s_inventory VALUES (19, 19, 15, 4, 35, NULL, DATE '2025-02-28');
INSERT INTO s_inventory VALUES (20, 20, 50, 8, 100, NULL, DATE '2025-03-01');
COMMIT;  -- Xác nhận lưu dữ liệu

-- Kiểm tra dữ liệu đã nhập:
SELECT * FROM s_region;
SELECT * FROM s_dept;
SELECT * FROM s_title;
SELECT * FROM s_emp;
SELECT * FROM s_customer;
SELECT * FROM s_image;
SELECT * FROM s_longtext;
SELECT * FROM s_product;
SELECT * FROM s_ord;
SELECT * FROM s_item;
SELECT * FROM s_warehouse;
SELECT * FROM s_inventory;
---------------- BÀI 2: Truy Vấn Dữ Liệu Cơ Bản ----------------

-- Câu 1: Hiển thị tên, mã khách hàng; đặt alias cho cột, sắp xếp giảm dần theo mã
SELECT name AS "Ten khach hang", id AS "Ma khach hang"
FROM s_customer
ORDER BY id DESC;

-- Câu 2: Họ, tên và mã phòng nhân viên phòng 10 và 50; nối họ tên thành cột 'Employees', sắp theo tên
SELECT first_name || ' ' || last_name AS "Employees", dept_id
FROM s_emp
WHERE dept_id IN (10, 50)
ORDER BY first_name;

-- Câu 3: Hiển thị tất cả nhân viên có tên chứa chữ 'S'
SELECT last_name, first_name
FROM s_emp
WHERE first_name LIKE '%S%' OR last_name LIKE '%S%';

-- Câu 4: Tên truy nhập và ngày bắt đầu làm việc từ 14/05/2021 đến 26/05/2022
SELECT userid, start_date
FROM s_emp
WHERE start_date BETWEEN TO_DATE('14/05/2021', 'DD/MM/YYYY') AND TO_DATE('26/05/2022', 'DD/MM/YYYY');
-- Câu 5: Tên và lương nhân viên nhận lương từ 4000 đến 7000/tháng
SELECT last_name, salary
FROM s_emp
WHERE salary BETWEEN 4000 AND 7000;

-- Câu 6: Nhân viên phòng 31, 42, 50 nhận lương trên 1.350; đặt alias 'Employee Name' và 'Monthly Salary'
SELECT last_name || ' ' || first_name AS "Employee Name", salary AS "Monthly Salary"
FROM s_emp
WHERE dept_id IN (31, 42, 50) AND salary > 1350;

-- Câu 7: Tên và ngày bắt đầu làm việc của nhân viên được tuyển trong năm 2021
-- Cách 1: Dùng TO_CHAR
SELECT last_name, start_date
FROM s_emp
WHERE TO_CHAR(start_date, 'YYYY') = '2021';

-- Cách 2: Dùng BETWEEN
SELECT last_name, start_date
FROM s_emp
WHERE start_date BETWEEN TO_DATE('01/01/2021', 'DD/MM/YYYY') AND TO_DATE('31/12/2021', 'DD/MM/YYYY');

-- Câu 8: Họ tên tất cả nhân viên không phải là người quản lý
-- Cách 1: NOT IN
SELECT last_name, first_name
FROM s_emp
WHERE id NOT IN (
    SELECT DISTINCT manager_id
    FROM s_emp
    WHERE manager_id IS NOT NULL
);

-- Cách 2: NOT EXISTS
SELECT last_name, first_name
FROM s_emp e
WHERE NOT EXISTS (
    SELECT 1
    FROM s_emp m
    WHERE m.manager_id = e.id
);

-- Câu 9: Sản phẩm có tên bắt đầu với từ 'Bike', hiển thị theo thứ tự abc
SELECT name
FROM s_product
WHERE name LIKE '%Bike%'
ORDER BY name ASC;

-- Câu 10: Tên và SHORT_DESC của sản phẩm có mô tả chứa từ 'bicycle'
SELECT name, short_desc
FROM s_product
WHERE LOWER(short_desc) LIKE '%bicycle%';

-- Câu 11: Hiển thị tất cả SHORT_DESC
SELECT short_desc
FROM s_product;

-- Câu 12: Tên nhân viên và chức vụ trong ngoặc đơn
SELECT last_name || ' ' || first_name || ' (' || title || ')' AS "Nhan vien"
FROM s_emp;

---------------- BÀI 3: Các Loại Hàm Trong SQL ----------------

-- Câu 1: Mã nhân viên, tên và mức lương được tăng thêm 15%
SELECT id, last_name, ROUND(salary * 1.15, 2) AS "Luong moi"
FROM s_emp;

-- Câu 2: Tên nhân viên, ngày tuyển dụng và ngày xét tăng lương
SELECT last_name,
       start_date,
       TO_CHAR(NEXT_DAY(ADD_MONTHS(start_date, 6), 'MONDAY'), 'Ddspth "of" Month YYYY') AS "Ngay xet tang luong"
FROM s_emp;

-- Câu 3: Tên sản phẩm của tất cả sản phẩm có chữ 'light'
SELECT name
FROM s_product
WHERE LOWER(name) LIKE '%light%';

-- Câu 4: Tính số tháng thâm niên của mỗi nhân viên
SELECT last_name, ROUND(MONTHS_BETWEEN(SYSDATE, start_date)) AS "So thang tham nien"
FROM s_emp
ORDER BY MONTHS_BETWEEN(SYSDATE, start_date) ASC;

-- Câu 5: Có bao nhiêu người quản lý?
SELECT COUNT(DISTINCT manager_id) AS "So nguoi quan ly"
FROM s_emp
WHERE manager_id IS NOT NULL;

-- Câu 6: Mức cao nhất và thấp nhất của đơn hàng trong s_ord
SELECT MAX(total) AS "Highest", MIN(total) AS "Lowest"
FROM s_ord;

---------------- BÀI 4: Phép Kết (JOIN) ----------------

-- Câu 1: Tên sản phẩm, mã sản phẩm và số lượng trong đơn hàng mã 101
SELECT p.name, p.id, i.quantity AS "ORDERED"
FROM s_product p, s_item i
WHERE p.id = i.product_id AND i.ord_id = 101;

-- Câu 2: Mã khách hàng và mã đơn đặt hàng của tất cả khách hàng
-- Cách 1: Cú pháp Oracle (+)
SELECT c.id AS "Ma khach hang", o.id AS "Ma don hang"
FROM s_customer c, s_ord o
WHERE c.id = o.customer_id(+)
ORDER BY c.id;

-- Cách 2: Cú pháp ANSI
SELECT c.id AS "Ma khach hang", o.id AS "Ma don hang"
FROM s_customer c
LEFT JOIN s_ord o ON c.id = o.customer_id
ORDER BY c.id;

-- Câu 3: Mã khách hàng, mã sản phẩm và số lượng đặt hàng của đơn hàng có trị giá trên 1000
SELECT o.customer_id, i.product_id, i.quantity
FROM s_ord o, s_item i
WHERE o.id = i.ord_id
  AND o.total > 1000;

---------------- BÀI 5: Các Hàm Gộp Nhóm ----------------

-- Câu 1: Với từng người quản lý, mã người quản lý và số nhân viên họ quản lý
SELECT manager_id AS "Ma quan ly", COUNT(id) AS "So nhan vien"
FROM s_emp
WHERE manager_id IS NOT NULL
GROUP BY manager_id
ORDER BY manager_id;

-- Câu 2: Người quản lý quản lý từ 2 nhân viên trở lên
SELECT manager_id AS "Ma quan ly", COUNT(id) AS "So nhan vien"
FROM s_emp
WHERE manager_id IS NOT NULL
GROUP BY manager_id
HAVING COUNT(id) >= 2;


-- Câu 3: Mã vùng, tên vùng và số phòng ban trực thuộc trong mỗi vùng
SELECT r.id AS "Ma vung", r.name AS "Ten vung", COUNT(d.id) AS "So phong ban"
FROM s_region r, s_dept d
WHERE r.id = d.region_id
GROUP BY r.id, r.name
ORDER BY r.id;

-- Câu 4: Tên khách hàng và số lượng đơn đặt hàng của mỗi khách
SELECT c.name AS "Ten khach hang", COUNT(o.id) AS "So don dat hang"
FROM s_customer c, s_ord o
WHERE c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY c.name;

-- Câu 5: Khách hàng có số đơn đặt hàng nhiều nhất
SELECT c.name, COUNT(o.id) AS "So don hang"
FROM s_customer c, s_ord o
WHERE c.id = o.customer_id
GROUP BY c.id, c.name
HAVING COUNT(o.id) = (
    SELECT MAX(COUNT(id))
    FROM s_ord
    GROUP BY customer_id
);

-- Câu 6: Khách hàng có tổng tiền mua hàng lớn nhất
SELECT c.name, SUM(o.total) AS "Tong tien"
FROM s_customer c, s_ord o
WHERE c.id = o.customer_id
GROUP BY c.id, c.name
HAVING SUM(o.total) = (
    SELECT MAX(SUM(total))
    FROM s_ord
    GROUP BY customer_id
);

---------------- BÀI 6: Truy Vấn Con (Subquery) ----------------

-- Câu 1: Họ, tên và ngày tuyển dụng của nhân viên cùng phòng với 'Michael'
-- Trường hợp chỉ có 1 Michael
SELECT last_name, first_name, start_date
FROM s_emp
WHERE dept_id = (
    SELECT dept_id
    FROM s_emp
    WHERE first_name = 'Michael'
)
AND first_name != 'Michael';

-- Trường hợp có nhiều Michael
SELECT last_name, first_name, start_date
FROM s_emp
WHERE dept_id IN (
    SELECT dept_id
    FROM s_emp
    WHERE first_name = 'Michael'
)
AND first_name != 'Michael';

-- Câu 2: Mã nhân viên, họ, tên và mã truy cập của nhân viên có lương trên mức lương trung bình
SELECT id, last_name, first_name, userid
FROM s_emp
WHERE salary > (
    SELECT AVG(salary)
    FROM s_emp
);

-- Câu 3: Mã, họ, tên của nhân viên có lương trên trung bình và tên chứa ký tự 'L'
SELECT id, last_name, first_name
FROM s_emp
WHERE salary > (
    SELECT AVG(salary)
    FROM s_emp
)
AND (UPPER(first_name) LIKE '%L%' OR UPPER(last_name) LIKE '%L%');
-- Câu 4: Những khách hàng chưa bao giờ đặt hàng
-- Cách 1: NOT IN
SELECT name
FROM s_customer
WHERE id NOT IN (
    SELECT DISTINCT customer_id
    FROM s_ord
    WHERE customer_id IS NOT NULL
);
-- Cách 2: NOT EXISTS
SELECT c.name
FROM s_customer c
WHERE NOT EXISTS (
    SELECT 1
    FROM s_ord o
    WHERE o.customer_id = c.id
);