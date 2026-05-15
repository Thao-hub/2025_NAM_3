CREATE DATABASE quanlysinhvien1;
GO

USE quanlysinhvien1;
GO

CREATE TABLE Khoa (
    maKhoa NVARCHAR(10) PRIMARY KEY,
    tenKhoa NVARCHAR(100) NOT NULL
);
GO

CREATE TABLE GiangVien (
    maGV NVARCHAR(10) PRIMARY KEY,
    hoTen NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    sdt NVARCHAR(15),
    hinh NVARCHAR(500),
    maKhoa NVARCHAR(10) NOT NULL,
    
    CONSTRAINT FK_GiangVien_Khoa FOREIGN KEY (maKhoa) REFERENCES Khoa(maKhoa)
);
GO

CREATE TABLE Lop (
    maLop NVARCHAR(15) PRIMARY KEY,
    tenLop NVARCHAR(100) NOT NULL,
    nienKhoa NVARCHAR(10),
    maKhoa NVARCHAR(10) NOT NULL,
    maGVCN NVARCHAR(10) NULL,
    
    CONSTRAINT FK_Lop_Khoa FOREIGN KEY (maKhoa) REFERENCES Khoa(maKhoa),
    CONSTRAINT FK_Lop_GiangVienCN FOREIGN KEY (maGVCN) REFERENCES GiangVien(maGV)
);
GO

CREATE TABLE MonHoc (
    maMH NVARCHAR(10) PRIMARY KEY,
    tenMH NVARCHAR(100) NOT NULL,
    soTinChi INT NOT NULL,
    hocKy INT 
);
GO

CREATE TABLE TaiKhoan (
    tendn NVARCHAR(50) PRIMARY KEY,
    matKhau NVARCHAR(100) NOT NULL,
    vaitro NVARCHAR(10) NOT NULL
);
GO

CREATE TABLE CanBoQuanLy (
    maCBQL NVARCHAR(50) PRIMARY KEY,
    hoTen NVARCHAR(100) NOT NULL, 
    email NVARCHAR(100) UNIQUE NOT NULL, 
    sdt NVARCHAR(15), 
    hinh NVARCHAR(500),
    
    tendn_cb NVARCHAR(50) NOT NULL UNIQUE, 
    CONSTRAINT FK_CanBo_TaiKhoan FOREIGN KEY (tendn_cb) REFERENCES TaiKhoan(tendn)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);
GO

CREATE TABLE SinhVien (
    maSV NVARCHAR(50) PRIMARY KEY,
    hoTen NVARCHAR(100) NOT NULL,
    ngaySinh DATE,
    email NVARCHAR(100) UNIQUE NOT NULL, 
    sdt NVARCHAR(15), 
    diaChi NVARCHAR(255),
    hinh NVARCHAR(500),
    maLop NVARCHAR(15) NOT NULL,
    
    tendn_sv NVARCHAR(50) NOT NULL UNIQUE, 
    
    CONSTRAINT FK_SinhVien_TaiKhoan FOREIGN KEY (tendn_sv) REFERENCES TaiKhoan(tendn)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    
    CONSTRAINT FK_SinhVien_Lop FOREIGN KEY (maLop) REFERENCES Lop(maLop)
);
GO

CREATE TABLE Diem (
    maD INT PRIMARY KEY IDENTITY(1,1),
    maSV NVARCHAR(50) NOT NULL,
    maMH NVARCHAR(10) NOT NULL,
    diem FLOAT,
    
    CONSTRAINT FK_Diem_SinhVien FOREIGN KEY (maSV) REFERENCES SinhVien(maSV)
    ON DELETE CASCADE,
    
    CONSTRAINT FK_Diem_MonHoc FOREIGN KEY (maMH) REFERENCES MonHoc(maMH)
);
GO

INSERT INTO TaiKhoan (tendn, matKhau, vaitro)
VALUES ('admin', '123', 'admin');
GO

INSERT INTO CanBoQuanLy (maCBQL, hoTen, email, sdt, hinh, tendn_cb)
VALUES ('ADMIN01', N'Trần Thị Thanh Thảo', 'thao.admin@email.com', '0909123456', NULL, 'admin');
GO
/*
================================================================
== SCRIPT DỮ LIỆU MẪU (MOCK DATA) CHO PROJECT QUẢN LÝ SINH VIÊN ==
== (An toàn để chạy nhiều lần - Sẽ xóa dữ liệu cũ trước)      ==
================================================================
*/




-- Phải xóa theo thứ tự ngược lại (từ bảng con đến bảng cha)
DELETE FROM Diem;
DELETE FROM SinhVien;
DELETE FROM CanBoQuanLy WHERE tendn_cb <> 'admin'; -- Giữ lại admin chính của em
DELETE FROM TaiKhoan WHERE tendn <> 'admin';     -- Giữ lại tài khoản admin chính
DELETE FROM Lop;
DELETE FROM GiangVien;
DELETE FROM MonHoc;
DELETE FROM Khoa;
GO
