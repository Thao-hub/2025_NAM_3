CREATE DATABASE QuanLySinhVien;
GO

USE QuanLySinhVien;
GO

CREATE TABLE TaiKhoan (
    tendn NVARCHAR(50) PRIMARY KEY,       
    hoten NVARCHAR(50) NOT NULL,
    matkhau NVARCHAR(100) NOT NULL,       
    email NVARCHAR(100) UNIQUE NOT NULL,
    sdt NVARCHAR(15),
    -- Đã đổi 'role' thành 'vaitro'
    vaitro NVARCHAR(10) NOT NULL DEFAULT 'student'  
);
GO

-- THÊM TÀI KHOẢN (ĐÃ SỬA DÙNG 'vaitro')
INSERT INTO TaiKhoan (tendn, hoten, matkhau, email, sdt, vaitro)
VALUES 
('admin', N'Trần Thị Thanh Thảo', 'admin123', 'admin@edu.com', '0123456789', 'admin'),
('sv001', N'Nguyễn Văn A', '123456', 'sv001@edu.com', '0987654321', 'student');
GO

-- 1. Bảng Khoa
CREATE TABLE Khoa (
    maKhoa NVARCHAR(10) PRIMARY KEY,
    tenKhoa NVARCHAR(100) NOT NULL
);
GO

-- 2. Bảng Lớp
CREATE TABLE Lop (
    maLop NVARCHAR(15) PRIMARY KEY,
    tenLop NVARCHAR(100) NOT NULL,
    maKhoa NVARCHAR(10) NOT NULL,
    
    CONSTRAINT FK_Lop_Khoa FOREIGN KEY (maKhoa) REFERENCES Khoa(maKhoa)
);
GO

-- 3. Bảng Sinh Viên
CREATE TABLE SinhVien (
    maSV NVARCHAR(50) PRIMARY KEY,  -- Khóa chính
    ngaySinh DATE,
    diaChi NVARCHAR(255),
    -- Đã đổi 'avatarURL' thành 'hinh'
    hinh NVARCHAR(500),           -- Đường dẫn ảnh đại diện
    maLop NVARCHAR(15),           -- Lớp của sinh viên
    
    CONSTRAINT FK_SinhVien_TaiKhoan FOREIGN KEY (maSV) REFERENCES TaiKhoan(tendn),
    CONSTRAINT FK_SinhVien_Lop FOREIGN KEY (maLop) REFERENCES Lop(maLop)
);
GO

-- 4. Bảng Môn Học
CREATE TABLE MonHoc (
    maMH NVARCHAR(10) PRIMARY KEY,
    tenMH NVARCHAR(100) NOT NULL,
    soTinChi INT NOT NULL
);
GO

-- 5. Bảng Điểm
CREATE TABLE Diem (
    -- Đã đổi 'id' thành 'maD'
    maD INT IDENTITY(1,1) PRIMARY KEY, -- Khóa tự tăng
    maSV NVARCHAR(50) NOT NULL,
    maMH NVARCHAR(10) NOT NULL,
    diem FLOAT, 
    
    CONSTRAINT FK_Diem_SinhVien FOREIGN KEY (maSV) REFERENCES SinhVien(maSV),
    CONSTRAINT FK_Diem_MonHoc FOREIGN KEY (maMH) REFERENCES MonHoc(maMH),
    CONSTRAINT UQ_Diem_SV_MH UNIQUE (maSV, maMH)
);
GO

-- THÊM DỮ LIỆU MẪU
INSERT INTO Khoa (maKhoa, tenKhoa) 
VALUES('CNTT', N'Công nghệ thông tin'),
	('QTKD', N'Quản trị kinh doanh');
GO

INSERT INTO Lop (maLop, tenLop, maKhoa) 
VALUES('D21CNTT01', N'Đại học CNTT Khóa 21 - Lớp 1', 'CNTT'),
	('D21QTKD01', N'Đại học QTKD Khóa 21 - Lớp 1', 'QTKD');
GO

INSERT INTO SinhVien (maSV, ngaySinh, diaChi, maLop) 
VALUES('sv001', '2003-10-20', N'123 Nguyễn Văn Cừ, Q5, TPHCM', 'D21CNTT01');
GO

INSERT INTO MonHoc (maMH, tenMH, soTinChi) 
VALUES('OOP', N'Lập trình Hướng đối tượng', 3),
	('DBI', N'Cơ sở dữ liệu', 3);
GO