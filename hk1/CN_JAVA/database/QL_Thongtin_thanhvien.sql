CREATE DATABASE QL_Thongtin_thanhvien;
USE QL_Thongtin_thanhvien;
CREATE TABLE thanhvien (
    id INT NOT NULL PRIMARY KEY IDENTITY(1,1),
    hoten NVARCHAR(100) NOT NULL,
    tuoi INT CHECK (tuoi >= 0),
    email NVARCHAR(100) NOT NULL UNIQUE,
    tendn NVARCHAR(50) NOT NULL UNIQUE,
    matkhau NVARCHAR(255) NOT NULL,
);

