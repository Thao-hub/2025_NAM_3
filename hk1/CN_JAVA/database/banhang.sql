create database banhang;
use banhang;

create table Hanghoa
(
	mahh varchar(15) primary key,
	tenhh varchar(50),
	dongia int,
	xuatxu varchar(20),
	loaihh varchar(5),
	hinh varchar(128),
	xuhuong int,
	phobien int
)
DROP TABLE IF EXISTS Hanghoa;

INSERT INTO Hanghoa (mahh, tenhh, dongia, xuatxu, loaihh, hinh, xuhuong, phobien)
VALUES
('01001', 'Men''s Office shoes', 45, 'Ý', '01', 'giay-da-handmade.jpg', 1, 0),
('02001', 'Women''s Office shoes', 52, 'VN', '02', 'giay nu 4s.jpg', 1, 1),
('03001', 'Women''s Office bag', 45, 'Pháp', '03', 'tui-xach-handmade.jpg', 1, 1),
('04001', 'Men''s wallet', 47, 'Pháp', '04', 'vi.jpg', 0, 1);

USE banhang;
ALTER AUTHORIZATION ON DATABASE::banhang TO sa;

INSERT INTO Hanghoa (mahh, tenhh, dongia, xuatxu, loaihh, hinh, xuhuong, phobien)
VALUES
('05001', 'Office shoes', 45, 'Ý', '01', 'giay nu 3.jpg', 1, 0)

SELECT mahh, tenhh FROM Hanghoa;
SELECT * FROM Hanghoa WHERE mahh='05001';

CREATE TABLE TAIKHOAN (
    tendn NVARCHAR(30) PRIMARY KEY,
	hoten NVARCHAR(50)NOT NULL,
    matkhau NVARCHAR(100) NOT NULL,
    email NVARCHAR(100)UNIQUE NOT NULL,
    sdt NVARCHAR(20),
	role NVARCHAR(10) NOT NULL DEFAULT 'user'

);
SELECT * FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'TAIKHOAN';

DROP TABLE IF EXISTS TAIKHOAN;
sp_who2
SELECT * FROM TAIKHOAN
SELECT 
    s.session_id,
    s.login_name,
    d.name AS database_name,
    s.host_name,
    s.program_name
FROM 
    sys.dm_exec_sessions AS s
JOIN 
    sys.databases AS d ON s.database_id = d.database_id
WHERE 
    s.is_user_process = 1        -- Chỉ hiển thị kết nối từ người dùng
    AND d.name = 'banhang'       -- Lọc database 'banhang'
    AND s.login_name = 'sa';     -- Lọc user 'sa'
INSERT INTO TAIKHOAN (tendn, hoten, matkhau, email, sdt, role)
VALUES 
('admin', N'Quản Trị Viên', 'admin123', 'admin@edu.com', '0123456789', 'admin'),
('us001', N'Nguyễn Văn A', '123456', 'us001@edu.com', '0987654321', 'user');
SELECT tendn, role FROM TAIKHOAN;
SELECT tendn, hoten, matkhau FROM TAIKHOAN;

CREATE TABLE DonHang (
    maHD INT IDENTITY(1,1) PRIMARY KEY,
    tendn NVARCHAR(30) NOT NULL,
    ngayDat DATETIME DEFAULT GETDATE(),
    tongTien INT NOT NULL,
    trangThai NVARCHAR(30) DEFAULT N'Đang xử lý',

    FOREIGN KEY (tendn) REFERENCES TAIKHOAN(tendn)
);
CREATE TABLE ChiTietDonHang (
    maCTDH INT IDENTITY(1,1) PRIMARY KEY,
    maHD INT NOT NULL,
    mahh VARCHAR(15) NOT NULL,
    soLuong INT NOT NULL,
    donGiaLucMua INT NOT NULL,

    FOREIGN KEY (maHD) REFERENCES DonHang(maHD),
    FOREIGN KEY (mahh) REFERENCES Hanghoa(mahh)
);