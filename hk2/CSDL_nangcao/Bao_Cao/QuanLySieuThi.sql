IF DB_ID('QuanLySieuThi') IS NOT NULL
BEGIN
    ALTER DATABASE QuanLySieuThi SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE QuanLySieuThi;
END;
GO

CREATE DATABASE QuanLySieuThi;
GO
USE QuanLySieuThi;
GO
CREATE TABLE NGANH_HANG (
    MaNganh VARCHAR(10) NOT NULL,
    TenNganh NVARCHAR(100) NOT NULL,
    CONSTRAINT PK_NGANH_HANG PRIMARY KEY (MaNganh),
    CONSTRAINT UQ_NGANH_HANG_Ten UNIQUE (TenNganh)
);
GO

CREATE TABLE NHA_SAN_XUAT (
    MaNSX VARCHAR(10) NOT NULL,
    TenNSX NVARCHAR(120) NOT NULL,
    DiaChi NVARCHAR(200) NOT NULL,
    SDT VARCHAR(15) NOT NULL,
    CONSTRAINT PK_NHA_SAN_XUAT PRIMARY KEY (MaNSX),
    CONSTRAINT UQ_NHA_SAN_XUAT_Ten UNIQUE (TenNSX),
    CONSTRAINT UQ_NHA_SAN_XUAT_SDT UNIQUE (SDT)
);
GO

CREATE TABLE NHA_PHAN_PHOI (
    MaNPP VARCHAR(10) NOT NULL,
    TenNPP NVARCHAR(120) NOT NULL,
    DiaChi NVARCHAR(200) NOT NULL,
    SDT VARCHAR(15) NOT NULL,
    CONSTRAINT PK_NHA_PHAN_PHOI PRIMARY KEY (MaNPP),
    CONSTRAINT UQ_NHA_PHAN_PHOI_Ten UNIQUE (TenNPP),
    CONSTRAINT UQ_NHA_PHAN_PHOI_SDT UNIQUE (SDT)
);
GO

CREATE TABLE KHUYEN_MAI (
    MaKM VARCHAR(10) NOT NULL,
    TenChuongTrinh NVARCHAR(120) NOT NULL,
    PhanTramGiam DECIMAL(5,2) NOT NULL,
    NgayBatDau DATE NOT NULL,
    NgayKetThuc DATE NOT NULL,
    TrangThai NVARCHAR(20) NOT NULL CONSTRAINT DF_KHUYEN_MAI_TrangThai DEFAULT N'Hoạt động',
    CONSTRAINT PK_KHUYEN_MAI PRIMARY KEY (MaKM),
    CONSTRAINT CK_KHUYEN_MAI_PhanTram CHECK (PhanTramGiam BETWEEN 0 AND 100),
    CONSTRAINT CK_KHUYEN_MAI_TrangThai CHECK (TrangThai IN (N'Hoạt động', N'Tạm dừng', N'Hết hạn')),
    CONSTRAINT CK_KHUYEN_MAI_Ngay CHECK (NgayKetThuc >= NgayBatDau)
);
GO

CREATE TABLE NHAN_VIEN (
    MaNV VARCHAR(10) NOT NULL,
    HoTen NVARCHAR(100) NOT NULL,
    SDT VARCHAR(15) NOT NULL,
    DiaChi NVARCHAR(200) NOT NULL,
    ChucVu NVARCHAR(30) NOT NULL CONSTRAINT DF_NHAN_VIEN_ChucVu DEFAULT N'Nhân viên',
    TrangThai NVARCHAR(20) NOT NULL CONSTRAINT DF_NHAN_VIEN_TrangThai DEFAULT N'Đang làm',
    CONSTRAINT PK_NHAN_VIEN PRIMARY KEY (MaNV),
    CONSTRAINT UQ_NHAN_VIEN_SDT UNIQUE (SDT),
    CONSTRAINT CK_NHAN_VIEN_ChucVu CHECK (ChucVu IN (N'Quản lý', N'Thu ngân', N'Kho', N'Nhân viên')),
    CONSTRAINT CK_NHAN_VIEN_TrangThai CHECK (TrangThai IN (N'Đang làm', N'Tạm nghỉ', N'Nghỉ việc'))
);
GO

CREATE TABLE LOAI_HANG (
    MaLoai VARCHAR(10) NOT NULL,
    TenLoai NVARCHAR(100) NOT NULL,
    MaNganh VARCHAR(10) NOT NULL,
    CONSTRAINT PK_LOAI_HANG PRIMARY KEY (MaLoai),
    CONSTRAINT UQ_LOAI_HANG_Ten UNIQUE (TenLoai),
    CONSTRAINT FK_LOAI_HANG_NGANH_HANG FOREIGN KEY (MaNganh) REFERENCES NGANH_HANG(MaNganh)
);
GO

CREATE TABLE TAI_KHOAN (
    MaTK VARCHAR(10) NOT NULL,
    TenDangNhap VARCHAR(50) NOT NULL,
    MatKhau VARCHAR(50) NOT NULL,
    Quyen VARCHAR(20) NOT NULL,
    MaNV VARCHAR(10) NOT NULL,
    DangHoatDong BIT NOT NULL CONSTRAINT DF_TAI_KHOAN_DangHoatDong DEFAULT 1,
    CONSTRAINT PK_TAI_KHOAN PRIMARY KEY (MaTK),
    CONSTRAINT UQ_TAI_KHOAN_TenDangNhap UNIQUE (TenDangNhap),
    CONSTRAINT UQ_TAI_KHOAN_MaNV UNIQUE (MaNV),
    CONSTRAINT FK_TAI_KHOAN_NHAN_VIEN FOREIGN KEY (MaNV) REFERENCES NHAN_VIEN(MaNV),
    CONSTRAINT CK_TAI_KHOAN_Quyen CHECK (Quyen IN ('Admin', 'NhanVien'))
);
GO

CREATE TABLE KHACH_HANG (
    MaKH VARCHAR(10) NOT NULL,
    HoTen NVARCHAR(100) NOT NULL,
    SDT VARCHAR(15) NOT NULL,
    DiaChi NVARCHAR(200) NOT NULL,
    HangThanhVien NVARCHAR(20) NOT NULL CONSTRAINT DF_KHACH_HANG_Hang DEFAULT N'Thường',
    DiemTichLuy INT NOT NULL CONSTRAINT DF_KHACH_HANG_Diem DEFAULT 0,
    CONSTRAINT PK_KHACH_HANG PRIMARY KEY (MaKH),
    CONSTRAINT UQ_KHACH_HANG_SDT UNIQUE (SDT),
    CONSTRAINT CK_KHACH_HANG_Hang CHECK (HangThanhVien IN (N'Thường', N'Bạc', N'Vàng', N'Kim cương')),
    CONSTRAINT CK_KHACH_HANG_Diem CHECK (DiemTichLuy >= 0)
);
GO

CREATE TABLE MAT_HANG (
    MaHang VARCHAR(10) NOT NULL,
    TenHang NVARCHAR(120) NOT NULL,
    DonViTinh NVARCHAR(20) NOT NULL,
    GiaGoc DECIMAL(18,0) NOT NULL,
    GiaBan DECIMAL(18,0) NOT NULL,
    MaLoai VARCHAR(10) NOT NULL,
    MaNSX VARCHAR(10) NOT NULL,
    MaNPP VARCHAR(10) NOT NULL,
    TrangThai NVARCHAR(20) NOT NULL CONSTRAINT DF_MAT_HANG_TrangThai DEFAULT N'Đang bán',
    CONSTRAINT PK_MAT_HANG PRIMARY KEY (MaHang),
    CONSTRAINT FK_MAT_HANG_LOAI FOREIGN KEY (MaLoai) REFERENCES LOAI_HANG(MaLoai),
    CONSTRAINT FK_MAT_HANG_NSX FOREIGN KEY (MaNSX) REFERENCES NHA_SAN_XUAT(MaNSX),
    CONSTRAINT FK_MAT_HANG_NPP FOREIGN KEY (MaNPP) REFERENCES NHA_PHAN_PHOI(MaNPP),
    CONSTRAINT CK_MAT_HANG_Gia CHECK (GiaBan >= GiaGoc),
    CONSTRAINT CK_MAT_HANG_TrangThai CHECK (TrangThai IN (N'Đang bán', N'Ngừng bán', N'Sắp về'))
);
GO

CREATE TABLE LO_HANG (
    MaLo VARCHAR(10) NOT NULL,
    TenLo NVARCHAR(80) NOT NULL,
    MaHang VARCHAR(10) NOT NULL,
    SoLuongNhap INT NOT NULL,
    TonKho INT NOT NULL,
    TenVT NVARCHAR(100) NOT NULL,
    NgayNhap DATE NOT NULL,
    CONSTRAINT PK_LO_HANG PRIMARY KEY (MaLo),
    CONSTRAINT FK_LO_HANG_MAT_HANG FOREIGN KEY (MaHang) REFERENCES MAT_HANG(MaHang),
    CONSTRAINT CK_LO_HANG_SoLuongNhap CHECK (SoLuongNhap > 0),
    CONSTRAINT CK_LO_HANG_TonKho CHECK (TonKho >= 0 AND TonKho <= SoLuongNhap)
);
GO

CREATE TABLE HOA_DON (
    MaHD VARCHAR(10) NOT NULL,
    NgayLap DATETIME NOT NULL CONSTRAINT DF_HOA_DON_NgayLap DEFAULT GETDATE(),
    TongTien DECIMAL(18,0) NOT NULL CONSTRAINT DF_HOA_DON_TongTien DEFAULT 0,
    MaNV VARCHAR(10) NOT NULL,
    MaKM VARCHAR(10) NULL,
    MaKH VARCHAR(10) NULL,
    PhuongThucThanhToan NVARCHAR(20) NOT NULL CONSTRAINT DF_HOA_DON_PTTT DEFAULT N'Tiền mặt',
    TrangThai NVARCHAR(20) NOT NULL CONSTRAINT DF_HOA_DON_TrangThai DEFAULT N'Hoàn tất',
    CONSTRAINT PK_HOA_DON PRIMARY KEY (MaHD),
    CONSTRAINT FK_HOA_DON_NHAN_VIEN FOREIGN KEY (MaNV) REFERENCES NHAN_VIEN(MaNV),
    CONSTRAINT FK_HOA_DON_KHUYEN_MAI FOREIGN KEY (MaKM) REFERENCES KHUYEN_MAI(MaKM),
    CONSTRAINT FK_HOA_DON_KHACH_HANG FOREIGN KEY (MaKH) REFERENCES KHACH_HANG(MaKH),
    CONSTRAINT CK_HOA_DON_TongTien CHECK (TongTien >= 0),
    CONSTRAINT CK_HOA_DON_PTTT CHECK (PhuongThucThanhToan IN (N'Tiền mặt', N'Chuyển khoản', N'Thẻ', N'Ví điện tử')),
    CONSTRAINT CK_HOA_DON_TrangThai CHECK (TrangThai IN (N'Hoàn tất', N'Treo', N'Đã hủy'))
);
GO

CREATE TABLE CHI_TIET_HOA_DON (
    MaHD VARCHAR(10) NOT NULL,
    MaHang VARCHAR(10) NOT NULL,
    SoLuong INT NOT NULL,
    DonGiaBan DECIMAL(18,0) NOT NULL,
    CONSTRAINT PK_CHI_TIET_HOA_DON PRIMARY KEY (MaHD, MaHang),
    CONSTRAINT FK_CTHD_HOA_DON FOREIGN KEY (MaHD) REFERENCES HOA_DON(MaHD),
    CONSTRAINT FK_CTHD_MAT_HANG FOREIGN KEY (MaHang) REFERENCES MAT_HANG(MaHang),
    CONSTRAINT CK_CTHD_SoLuong CHECK (SoLuong > 0),
    CONSTRAINT CK_CTHD_DonGia CHECK (DonGiaBan > 0)
);
GO


CREATE INDEX IX_MAT_HANG_MaLoai ON MAT_HANG(MaLoai);
CREATE INDEX IX_MAT_HANG_MaNSX ON MAT_HANG(MaNSX);
CREATE INDEX IX_LO_HANG_MaHang ON LO_HANG(MaHang);
CREATE INDEX IX_HOA_DON_NgayLap ON HOA_DON(NgayLap);
CREATE INDEX IX_HOA_DON_MaKH ON HOA_DON(MaKH);
CREATE INDEX IX_CTHD_MaHang ON CHI_TIET_HOA_DON(MaHang);
GO


INSERT INTO NGANH_HANG (MaNganh, TenNganh) VALUES
('NH01', N'Thực phẩm tươi sống'),
('NH02', N'Đồ uống'),
('NH03', N'Hóa mỹ phẩm'),
('NH04', N'Gia vị'),
('NH05', N'Đồ đóng hộp'),
('NH06', N'Sữa và chế phẩm từ sữa'),
('NH07', N'Bánh kẹo'),
('NH08', N'Đồ gia dụng'),
('NH09', N'Điện gia dụng nhỏ'),
('NH10', N'Thời trang'),
('NH11', N'Văn phòng phẩm'),
('NH12', N'Đồ chơi'),
('NH13', N'Hàng đông lạnh'),
('NH14', N'Rau củ quả'),
('NH15', N'Thực phẩm chức năng'),
('NH16', N'Thức ăn nhanh'),
('NH17', N'Đồ dùng nhà bếp'),
('NH18', N'Hóa chất tẩy rửa'),
('NH19', N'Chăm sóc cá nhân'),
('NH20', N'Phụ kiện gia đình');
GO
INSERT INTO NHA_SAN_XUAT (MaNSX, TenNSX, DiaChi, SDT) VALUES
('NSX01', N'Vinamilk', N'Quan 7, TP.HCM', '0281000001'),
('NSX02', N'Unilever Viet Nam', N'Cu Chi, TP.HCM', '0281000002'),
('NSX03', N'Sunhouse', N'Thanh Xuan, Ha Noi', '0281000003'),
('NSX04', N'Suntory PepsiCo', N'Quan 3, TP.HCM', '0281000004'),
('NSX05', N'Viet Tien', N'Tan Binh, TP.HCM', '0281000005'),
('NSX06', N'Acecook Viet Nam', N'Binh Tan, TP.HCM', '0281000006'),
('NSX07', N'Bibica', N'Bien Hoa, Dong Nai', '0281000007'),
('NSX08', N'Masan Consumer', N'Quan 1, TP.HCM', '0281000008'),
('NSX09', N'Orion Food', N'Binh Duong', '0281000009'),
('NSX10', N'Thien Long', N'Tan Tao, TP.HCM', '0281000010'),
('NSX11', N'LocknLock', N'Long An', '0281000011'),
('NSX12', N'Panasonic Viet Nam', N'Ha Noi', '0281000012'),
('NSX13', N'Dien Quang', N'Thu Duc, TP.HCM', '0281000013'),
('NSX14', N'Thorakao', N'Quan 5, TP.HCM', '0281000014'),
('NSX15', N'Thuan Phat Foods', N'Quan 12, TP.HCM', '0281000015'),
('NSX16', N'CJ Cau Tre', N'Long An', '0281000016'),
('NSX17', N'Lafooco', N'Binh Phuoc', '0281000017'),
('NSX18', N'Nutifood', N'Thanh pho Thu Duc', '0281000018'),
('NSX19', N'Dong A Plastic', N'Binh Duong', '0281000019'),
('NSX20', N'P/S Viet Nam', N'Thu Duc, TP.HCM', '0281000020');
GO

INSERT INTO NHA_PHAN_PHOI (MaNPP, TenNPP, DiaChi, SDT) VALUES
('NPP01', N'Phu Thai Distribution', N'Binh Duong', '0274100001'),
('NPP02', N'Mesa Group', N'Quan 3, TP.HCM', '0274100002'),
('NPP03', N'DKSH Viet Nam', N'Binh Duong', '0274100003'),
('NPP04', N'An Nam Food', N'Quan 1, TP.HCM', '0274100004'),
('NPP05', N'Hoang Gia Distribution', N'Dong Nai', '0274100005'),
('NPP06', N'Satra Phan Phoi', N'Quan 10, TP.HCM', '0274100006'),
('NPP07', N'Saigon Co.op Supply', N'Quan 1, TP.HCM', '0274100007'),
('NPP08', N'Bach Hoa Tong Hop', N'Quan 12, TP.HCM', '0274100008'),
('NPP09', N'Thien An Trading', N'Thu Duc, TP.HCM', '0274100009'),
('NPP10', N'Minh Chau Logistic', N'Go Vap, TP.HCM', '0274100010'),
('NPP11', N'Tan Phat Service', N'Quan 5, TP.HCM', '0274100011'),
('NPP12', N'Hung Thinh Retail Supply', N'Tan Binh, TP.HCM', '0274100012'),
('NPP13', N'Viet An Distributor', N'Quan 7, TP.HCM', '0274100013'),
('NPP14', N'Dong Nam Solution', N'Binh Tan, TP.HCM', '0274100014'),
('NPP15', N'Thanh Dat Trading', N'Quan 6, TP.HCM', '0274100015'),
('NPP16', N'Phuc Long Supply', N'Quan 11, TP.HCM', '0274100016'),
('NPP17', N'Thanh Cong Distributor', N'Quan 8, TP.HCM', '0274100017'),
('NPP18', N'Dai Viet Wholesale', N'Long An', '0274100018'),
('NPP19', N'Gia Phat Commerce', N'Tay Ninh', '0274100019'),
('NPP20', N'Hoa Sen Distribution', N'Binh Phuoc', '0274100020');
GO

INSERT INTO KHUYEN_MAI (MaKM, TenChuongTrinh, PhanTramGiam, NgayBatDau, NgayKetThuc, TrangThai) VALUES
('KM01', N'Tết tiết kiệm', 5, '2026-01-01', '2026-01-31', N'Hết hạn'),
('KM02', N'Mừng xuân', 10, '2026-02-01', '2026-02-28', N'Hết hạn'),
('KM03', N'Ngày 8 tháng 3', 8, '2026-03-01', '2026-03-10', N'Hết hạn'),
('KM04', N'Khai trương quầy mới', 12, '2026-03-15', '2026-04-15', N'Hết hạn'),
('KM05', N'Lễ 30/4', 15, '2026-04-20', '2026-05-02', N'Hết hạn'),
('KM06', N'Mùa hè tiết kiệm', 7, '2026-05-15', '2026-06-15', N'Hết hạn'),
('KM07', N'Thiếu nhi 1/6', 6, '2026-05-28', '2026-06-03', N'Hết hạn'),
('KM08', N'Gia dụng giá tốt', 9, '2026-06-10', '2026-06-30', N'Hết hạn'),
('KM09', N'Tựu trường', 10, '2026-07-25', '2026-08-20', N'Hết hạn'),
('KM10', N'Quốc khánh', 12, '2026-08-25', '2026-09-05', N'Hết hạn'),
('KM11', N'Trung thu vui vẻ', 5, '2026-09-10', '2026-09-20', N'Hết hạn'),
('KM12', N'Phụ nữ Việt Nam', 8, '2026-10-10', '2026-10-20', N'Hết hạn'),
('KM13', N'Hello November', 6, '2026-11-01', '2026-11-15', N'Hết hạn'),
('KM14', N'Black Friday', 20, '2026-11-20', '2026-11-29', N'Hết hạn'),
('KM15', N'Noel an lành', 10, '2026-12-15', '2026-12-25', N'Hoạt động'),
('KM16', N'Thành viên bạc', 5, '2026-01-01', '2026-12-31', N'Hoạt động'),
('KM17', N'Thành viên vàng', 7, '2026-01-01', '2026-12-31', N'Hoạt động'),
('KM18', N'Thành viên kim cương', 10, '2026-01-01', '2026-12-31', N'Hoạt động'),
('KM19', N'Combo gia đình', 6, '2026-03-01', '2026-12-31', N'Hoạt động'),
('KM20', N'Giá niêm yết', 0, '2026-01-01', '2026-12-31', N'Hoạt động');
GO

INSERT INTO NHAN_VIEN (MaNV, HoTen, SDT, DiaChi, ChucVu, TrangThai) VALUES
('NV01', N'Trần Minh Tâm', '0901000001', N'Quận 7, TP.HCM', N'Quản lý', N'Đang làm'),
('NV02', N'Lê Thị Hồng Ngân', '0901000002', N'Thủ Đức, TP.HCM', N'Thu ngân', N'Đang làm'),
('NV03', N'Nguyễn Hoàng Nam', '0901000003', N'Quận 12, TP.HCM', N'Thu ngân', N'Đang làm'),
('NV04', N'Phạm Mỹ Linh', '0901000004', N'Quận 3, TP.HCM', N'Kho', N'Đang làm'),
('NV05', N'Đặng Văn Hùng', '0901000005', N'Gò Vấp, TP.HCM', N'Kho', N'Đang làm'),
('NV06', N'Võ Thị Mai', '0901000006', N'Quận 1, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV07', N'Bùi Quốc Đạt', '0901000007', N'Quận 2, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV08', N'Nguyễn Thu Hà', '0901000008', N'Quận 4, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV09', N'Phạm Tuấn Kiệt', '0901000009', N'Quận 5, TP.HCM', N'Thu ngân', N'Đang làm'),
('NV10', N'Lê Gia Bảo', '0901000010', N'Quận 6, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV11', N'Trần Nhật Linh', '0901000011', N'Quận 8, TP.HCM', N'Kho', N'Đang làm'),
('NV12', N'Nguyễn Thanh Vy', '0901000012', N'Quận 9, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV13', N'Phan Quốc Anh', '0901000013', N'Quận 10, TP.HCM', N'Thu ngân', N'Đang làm'),
('NV14', N'Hoàng Minh Châu', '0901000014', N'Quận 11, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV15', N'Vũ Ngọc Hân', '0901000015', N'Bình Thạnh, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV16', N'Nguyễn Đình Sơn', '0901000016', N'Phú Nhuận, TP.HCM', N'Kho', N'Đang làm'),
('NV17', N'Phạm Khánh Nhi', '0901000017', N'Tân Bình, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV18', N'Lê Quang Huy', '0901000018', N'Tân Phú, TP.HCM', N'Thu ngân', N'Đang làm'),
('NV19', N'Trịnh Bảo Trâm', '0901000019', N'Bình Tân, TP.HCM', N'Nhân viên', N'Đang làm'),
('NV20', N'Đỗ Văn Phúc', '0901000020', N'Nhà Bè, TP.HCM', N'Nhân viên', N'Đang làm');
GO

INSERT INTO LOAI_HANG (MaLoai, TenLoai, MaNganh) VALUES
('LH01', N'Sữa tươi', 'NH06'),
('LH02', N'Sữa chua', 'NH06'),
('LH03', N'Nước ngọt có gas', 'NH02'),
('LH04', N'Nước trái cây', 'NH02'),
('LH05', N'Dầu gội', 'NH03'),
('LH06', N'Sữa tắm', 'NH03'),
('LH07', N'Mì gói', 'NH16'),
('LH08', N'Bánh quy', 'NH07'),
('LH09', N'Gia vị nấu ăn', 'NH04'),
('LH10', N'Thực phẩm đóng hộp', 'NH05'),
('LH11', N'Nồi chiên không dầu', 'NH09'),
('LH12', N'Nồi cơm điện', 'NH09'),
('LH13', N'Áo thun', 'NH10'),
('LH14', N'Bút viết', 'NH11'),
('LH15', N'Đồ chơi trẻ em', 'NH12'),
('LH16', N'Thực phẩm đông lạnh', 'NH13'),
('LH17', N'Rau sạch', 'NH14'),
('LH18', N'Viên bổ sung', 'NH15'),
('LH19', N'Nước rửa chén', 'NH18'),
('LH20', N'Bàn chải đánh răng', 'NH19');
GO

INSERT INTO TAI_KHOAN (MaTK, TenDangNhap, MatKhau, Quyen, MaNV, DangHoatDong) VALUES
('TK01', 'admin_tam', '123456', 'Admin', 'NV01', 1),
('TK02', 'thu_ngan_02', '123456', 'NhanVien', 'NV02', 1),
('TK03', 'thu_ngan_03', '123456', 'NhanVien', 'NV03', 1),
('TK04', 'kho_04', '123456', 'NhanVien', 'NV04', 1),
('TK05', 'kho_05', '123456', 'NhanVien', 'NV05', 1),
('TK06', 'nv_06', '123456', 'NhanVien', 'NV06', 1),
('TK07', 'nv_07', '123456', 'NhanVien', 'NV07', 1),
('TK08', 'nv_08', '123456', 'NhanVien', 'NV08', 1),
('TK09', 'thu_ngan_09', '123456', 'NhanVien', 'NV09', 1),
('TK10', 'nv_10', '123456', 'NhanVien', 'NV10', 1),
('TK11', 'kho_11', '123456', 'NhanVien', 'NV11', 1),
('TK12', 'nv_12', '123456', 'NhanVien', 'NV12', 1),
('TK13', 'thu_ngan_13', '123456', 'NhanVien', 'NV13', 1),
('TK14', 'nv_14', '123456', 'NhanVien', 'NV14', 1),
('TK15', 'nv_15', '123456', 'NhanVien', 'NV15', 1),
('TK16', 'kho_16', '123456', 'NhanVien', 'NV16', 1),
('TK17', 'nv_17', '123456', 'NhanVien', 'NV17', 1),
('TK18', 'thu_ngan_18', '123456', 'NhanVien', 'NV18', 1),
('TK19', 'nv_19', '123456', 'NhanVien', 'NV19', 1),
('TK20', 'nv_20', '123456', 'NhanVien', 'NV20', 1);
GO

INSERT INTO KHACH_HANG (MaKH, HoTen, SDT, DiaChi, HangThanhVien, DiemTichLuy) VALUES
('KH01', N'Nguyễn Anh Khoa', '0907000001', N'Quận 1, TP.HCM', N'Thường', 120),
('KH02', N'Trần Minh Châu', '0907000002', N'Quận 5, TP.HCM', N'Bạc', 420),
('KH03', N'Lê Thu Trang', '0907000003', N'Tân Bình, TP.HCM', N'Vàng', 980),
('KH04', N'Võ Quốc Huy', '0907000004', N'Quận 7, TP.HCM', N'Thường', 50),
('KH05', N'Phạm Gia Hân', '0907000005', N'Gò Vấp, TP.HCM', N'Thường', 75),
('KH06', N'Nguyễn Hoàng Yến', '0907000006', N'Quận 12, TP.HCM', N'Bạc', 220),
('KH07', N'Trịnh Minh Khang', '0907000007', N'Bình Thạnh, TP.HCM', N'Thường', 90),
('KH08', N'Đặng Nhật Vy', '0907000008', N'Thủ Đức, TP.HCM', N'Thường', 30),
('KH09', N'Lê Bảo Ngọc', '0907000009', N'Quận 3, TP.HCM', N'Bạc', 310),
('KH10', N'Nguyễn Tuấn Anh', '0907000010', N'Quận 4, TP.HCM', N'Thường', 60),
('KH11', N'Phạm Thị Thu', '0907000011', N'Quận 6, TP.HCM', N'Thường', 45),
('KH12', N'Bùi Minh Đức', '0907000012', N'Quận 8, TP.HCM', N'Vàng', 520),
('KH13', N'Nguyễn Quỳnh Như', '0907000013', N'Quận 9, TP.HCM', N'Thường', 110),
('KH14', N'Tạ Hoàng Phúc', '0907000014', N'Quận 10, TP.HCM', N'Thường', 80),
('KH15', N'Lê Khánh Chi', '0907000015', N'Quận 11, TP.HCM', N'Bạc', 260),
('KH16', N'Phạm Thành Long', '0907000016', N'Phú Nhuận, TP.HCM', N'Thường', 95),
('KH17', N'Hoàng Minh Quân', '0907000017', N'Tân Phú, TP.HCM', N'Thường', 20),
('KH18', N'Nguyễn Bảo Trâm', '0907000018', N'Bình Tân, TP.HCM', N'Thường', 130),
('KH19', N'Đỗ Nhật Nam', '0907000019', N'Nhà Bè, TP.HCM', N'Kim cương', 1200),
('KH20', N'Trần Tú Uyên', '0907000020', N'Hóc Môn, TP.HCM', N'Bạc', 350);
GO

INSERT INTO MAT_HANG (MaHang, TenHang, DonViTinh, GiaGoc, GiaBan, MaLoai, MaNSX, MaNPP, TrangThai) VALUES
('MH01', N'Sữa Vinamilk ít đường 180ml', N'Thùng', 320000, 365000, 'LH01', 'NSX01', 'NPP01', N'Đang bán'),
('MH02', N'Sữa chua Vinamilk có đường', N'Thùng', 180000, 215000, 'LH02', 'NSX01', 'NPP02', N'Đang bán'),
('MH03', N'Pepsi lon 330ml thùng 24', N'Thùng', 195000, 225000, 'LH03', 'NSX04', 'NPP03', N'Đang bán'),
('MH04', N'Tropicana cam ép 1L', N'Chai', 32000, 39000, 'LH04', 'NSX04', 'NPP04', N'Đang bán'),
('MH05', N'Dầu gội Clear bạc hà 630g', N'Chai', 145000, 175000, 'LH05', 'NSX02', 'NPP05', N'Đang bán'),
('MH06', N'Sữa tắm Lifebuoy 850g', N'Chai', 115000, 145000, 'LH06', 'NSX02', 'NPP06', N'Đang bán'),
('MH07', N'Mì Hảo Hảo tôm chua cay', N'Thùng', 112000, 132000, 'LH07', 'NSX06', 'NPP07', N'Đang bán'),
('MH08', N'Bánh ChocoPie hộp 12 cái', N'Hộp', 54000, 69000, 'LH08', 'NSX09', 'NPP08', N'Đang bán'),
('MH09', N'Nước mắm Nam Ngư 900ml', N'Chai', 38000, 47000, 'LH09', 'NSX08', 'NPP09', N'Đang bán'),
('MH10', N'Cá hộp 3 cô gái 155g', N'Hộp', 22000, 28000, 'LH10', 'NSX15', 'NPP10', N'Đang bán'),
('MH11', N'Nồi chiên Sunhouse SHD4026', N'Cái', 1200000, 1650000, 'LH11', 'NSX03', 'NPP11', N'Đang bán'),
('MH12', N'Nồi cơm điện Panasonic 1.8L', N'Cái', 890000, 1090000, 'LH12', 'NSX12', 'NPP12', N'Đang bán'),
('MH13', N'Áo thun Việt Tiến cotton', N'Cái', 180000, 285000, 'LH13', 'NSX05', 'NPP13', N'Đang bán'),
('MH14', N'Bút bi Thiên Long TL027', N'Hộp', 35000, 45000, 'LH14', 'NSX10', 'NPP14', N'Đang bán'),
('MH15', N'Bộ đồ chơi xếp hình 120 chi tiết', N'Hộp', 125000, 165000, 'LH15', 'NSX19', 'NPP15', N'Đang bán'),
('MH16', N'Xúc xích viên đông lạnh 500g', N'Gói', 48000, 62000, 'LH16', 'NSX16', 'NPP16', N'Đang bán'),
('MH17', N'Rau cải ngọt hữu cơ 500g', N'Gói', 18000, 25000, 'LH17', 'NSX15', 'NPP17', N'Đang bán'),
('MH18', N'Viên uống vitamin C 100 viên', N'Lọ', 92000, 125000, 'LH18', 'NSX18', 'NPP18', N'Đang bán'),
('MH19', N'Nước rửa chén Sunlight 750ml', N'Chai', 29000, 39000, 'LH19', 'NSX02', 'NPP19', N'Đang bán'),
('MH20', N'Bàn chải đánh răng P/S than hoạt tính', N'Cây', 18000, 26000, 'LH20', 'NSX20', 'NPP20', N'Đang bán');
GO

INSERT INTO LO_HANG (MaLo, TenLo, MaHang, SoLuongNhap, TonKho, TenVT, NgayNhap) VALUES
('L001', N'Lô sữa 01', 'MH01', 120, 95, N'Kệ sữa A1', '2026-01-05'),
('L002', N'Lô sữa chua 01', 'MH02', 100, 78, N'Kệ sữa A2', '2026-01-07'),
('L003', N'Lô Pepsi 01', 'MH03', 150, 120, N'Kệ nước B1', '2026-01-08'),
('L004', N'Lô Tropicana 01', 'MH04', 90, 65, N'Kệ nước B2', '2026-01-09'),
('L005', N'Lô Clear 01', 'MH05', 80, 60, N'Kệ hóa mỹ phẩm C1', '2026-01-10'),
('L006', N'Lô Lifebuoy 01', 'MH06', 75, 52, N'Kệ hóa mỹ phẩm C2', '2026-01-11'),
('L007', N'Lô Hảo Hảo 01', 'MH07', 200, 165, N'Kệ thức ăn D1', '2026-01-12'),
('L008', N'Lô ChocoPie 01', 'MH08', 130, 100, N'Kệ bánh kẹo D2', '2026-01-13'),
('L009', N'Lô nước mắm 01', 'MH09', 95, 74, N'Kệ gia vị D3', '2026-01-14'),
('L010', N'Lô cá hộp 01', 'MH10', 110, 85, N'Kệ đồ hộp D4', '2026-01-15'),
('L011', N'Lô nồi chiên 01', 'MH11', 25, 18, N'Khu điện máy E1', '2026-01-16'),
('L012', N'Lô nồi cơm 01', 'MH12', 30, 22, N'Khu điện máy E2', '2026-01-17'),
('L013', N'Lô áo thun 01', 'MH13', 70, 54, N'Khu thời trang F1', '2026-01-18'),
('L014', N'Lô bút viết 01', 'MH14', 140, 110, N'Kệ văn phòng F2', '2026-01-19'),
('L015', N'Lô đồ chơi 01', 'MH15', 60, 48, N'Khu đồ chơi F3', '2026-01-20'),
('L016', N'Lô xúc xích 01', 'MH16', 85, 63, N'Kho đông lạnh G1', '2026-01-21'),
('L017', N'Lô rau sạch 01', 'MH17', 90, 68, N'Kệ rau củ G2', '2026-01-22'),
('L018', N'Lô vitamin C 01', 'MH18', 55, 40, N'Kệ sức khỏe G3', '2026-01-23'),
('L019', N'Lô Sunlight 01', 'MH19', 100, 79, N'Kệ tẩy rửa G4', '2026-01-24'),
('L020', N'Lô bàn chải 01', 'MH20', 120, 91, N'Kệ chăm sóc cá nhân G5', '2026-01-25');
GO

INSERT INTO HOA_DON (MaHD, NgayLap, TongTien, MaNV, MaKM, MaKH, PhuongThucThanhToan, TrangThai) VALUES
('HD01', '2026-03-01 08:10:00', 0, 'NV02', 'KM03', 'KH01', N'Tiền mặt', N'Hoàn tất'),
('HD02', '2026-03-01 09:15:00', 0, 'NV03', 'KM20', 'KH02', N'Thẻ', N'Hoàn tất'),
('HD03', '2026-03-02 10:05:00', 0, 'NV09', 'KM20', 'KH03', N'Chuyển khoản', N'Hoàn tất'),
('HD04', '2026-03-02 11:20:00', 0, 'NV13', 'KM19', 'KH04', N'Tiền mặt', N'Hoàn tất'),
('HD05', '2026-03-03 08:40:00', 0, 'NV18', 'KM20', 'KH05', N'Ví điện tử', N'Hoàn tất'),
('HD06', '2026-03-03 14:10:00', 0, 'NV02', 'KM03', 'KH06', N'Tiền mặt', N'Hoàn tất'),
('HD07', '2026-03-04 09:00:00', 0, 'NV03', 'KM20', 'KH07', N'Tiền mặt', N'Hoàn tất'),
('HD08', '2026-03-04 16:30:00', 0, 'NV09', 'KM19', 'KH08', N'Thẻ', N'Hoàn tất'),
('HD09', '2026-03-05 10:50:00', 0, 'NV13', 'KM20', 'KH09', N'Chuyển khoản', N'Hoàn tất'),
('HD10', '2026-03-05 18:00:00', 0, 'NV18', 'KM03', 'KH10', N'Tiền mặt', N'Hoàn tất'),
('HD11', '2026-03-06 08:25:00', 0, 'NV02', 'KM20', 'KH11', N'Thẻ', N'Hoàn tất'),
('HD12', '2026-03-06 15:45:00', 0, 'NV03', 'KM19', 'KH12', N'Tiền mặt', N'Hoàn tất'),
('HD13', '2026-03-07 09:35:00', 0, 'NV09', 'KM20', 'KH13', N'Thẻ', N'Hoàn tất'),
('HD14', '2026-03-07 17:20:00', 0, 'NV13', 'KM03', 'KH14', N'Chuyển khoản', N'Hoàn tất'),
('HD15', '2026-03-08 10:10:00', 0, 'NV18', 'KM20', 'KH15', N'Tiền mặt', N'Hoàn tất'),
('HD16', '2026-03-08 19:00:00', 0, 'NV02', 'KM19', 'KH16', N'Ví điện tử', N'Hoàn tất'),
('HD17', '2026-03-09 11:05:00', 0, 'NV03', 'KM20', 'KH17', N'Tiền mặt', N'Hoàn tất'),
('HD18', '2026-03-09 16:40:00', 0, 'NV09', 'KM03', 'KH18', N'Thẻ', N'Hoàn tất'),
('HD19', '2026-03-10 13:15:00', 0, 'NV13', 'KM20', 'KH19', N'Tiền mặt', N'Hoàn tất'),
('HD20', '2026-03-10 20:05:00', 0, 'NV18', 'KM19', 'KH20', N'Chuyển khoản', N'Hoàn tất');
GO

INSERT INTO CHI_TIET_HOA_DON (MaHD, MaHang, SoLuong, DonGiaBan) VALUES
('HD01', 'MH01', 2, 365000),
('HD02', 'MH03', 1, 225000),
('HD03', 'MH05', 1, 175000),
('HD04', 'MH07', 2, 132000),
('HD05', 'MH09', 3, 47000),
('HD06', 'MH11', 1, 1650000),
('HD07', 'MH13', 1, 285000),
('HD08', 'MH15', 1, 165000),
('HD09', 'MH17', 4, 25000),
('HD10', 'MH19', 2, 39000),
('HD11', 'MH02', 2, 215000),
('HD12', 'MH04', 3, 39000),
('HD13', 'MH06', 1, 145000),
('HD14', 'MH08', 2, 69000),
('HD15', 'MH10', 4, 28000),
('HD16', 'MH12', 1, 1090000),
('HD17', 'MH14', 3, 45000),
('HD18', 'MH16', 2, 62000),
('HD19', 'MH18', 1, 125000),
('HD20', 'MH20', 5, 26000);
GO

-----------------FUNCTION, TRIGGER, PROCEDURE-------------------------
CREATE OR ALTER FUNCTION fn_KiemTraTonKho (@MaHang VARCHAR(10))
RETURNS NVARCHAR(30)
AS
BEGIN
    RETURN (
        SELECT CASE
            WHEN SUM(TonKho) IS NULL OR SUM(TonKho) = 0 THEN N'Hết hàng'
            WHEN SUM(TonKho) <= 20 THEN N'Sắp hết'
            ELSE N'Còn hàng'
        END
        FROM LO_HANG
        WHERE MaHang = @MaHang
    );
END;
GO
---kiem tra
SELECT dbo.fn_KiemTraTonKho('MH01') AS TrangThaiTonKho_MH01;

CREATE OR ALTER TRIGGER TRG_CapNhatTongTienHoaDon
ON CHI_TIET_HOA_DON
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    ;WITH DanhSachHoaDon AS (
        SELECT MaHD FROM inserted
        UNION
        SELECT MaHD FROM deleted
    )
    UPDATE hd
    SET TongTien = ISNULL((
        SELECT SUM(ct.SoLuong * ct.DonGiaBan)
        FROM CHI_TIET_HOA_DON ct
        WHERE ct.MaHD = hd.MaHD
    ), 0)
    FROM HOA_DON hd
    JOIN DanhSachHoaDon ds ON ds.MaHD = hd.MaHD;
END;
GO

-- Tao hoa don 
INSERT INTO HOA_DON (MaHD, NgayLap, TongTien, MaNV, MaKM, MaKH, PhuongThucThanhToan, TrangThai)
VALUES ('HD_TEST', GETDATE(), 0, 'NV01', 'KM20', 'KH01', N'Tiền mặt', N'Hoàn tất');
GO
-- Them chi tiet hoa don
INSERT INTO CHI_TIET_HOA_DON (MaHD, MaHang, SoLuong, DonGiaBan)
VALUES ('HD_TEST', 'MH01', 2, 365000);
GO
-- Kiem tra TongTien da duoc cap nhat chua
SELECT MaHD, TongTien
FROM HOA_DON
WHERE MaHD = 'HD_TEST';
GO

CREATE OR ALTER TRIGGER TRG_TruTonKho
ON CHI_TIET_HOA_DON
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE lh
    SET TonKho = lh.TonKho - i.SoLuong
    FROM LO_HANG lh
    JOIN inserted i ON i.MaHang = lh.MaHang;

    IF EXISTS (SELECT 1 FROM LO_HANG WHERE TonKho < 0)
    BEGIN
        RAISERROR (N'Tồn kho không đủ để bán.', 16, 1);
        ROLLBACK TRANSACTION;
    END
END;
GO
---kiem tra
SELECT MaHang, TonKho
FROM LO_HANG
WHERE MaHang = 'MH01';
GO
INSERT INTO HOA_DON (MaHD, NgayLap, TongTien, MaNV, MaKM, MaKH, PhuongThucThanhToan, TrangThai)
VALUES ('HD_TEST2', GETDATE(), 0, 'NV01', 'KM20', 'KH01', N'Tiền mặt', N'Hoàn tất');
GO
INSERT INTO CHI_TIET_HOA_DON (MaHD, MaHang, SoLuong, DonGiaBan)
VALUES ('HD_TEST2', 'MH01', 1, 365000);
GO
SELECT MaHang, TonKho
FROM LO_HANG
WHERE MaHang = 'MH01';
GO

CREATE OR ALTER PROCEDURE SP_NhapLoHang
    @MaLo VARCHAR(10),
    @TenLo NVARCHAR(80),
    @MaHang VARCHAR(10),
    @SoLuongNhap INT,
    @TenVT NVARCHAR(100),
    @NgayNhap DATE
AS
BEGIN
    SET NOCOUNT ON;
    IF @SoLuongNhap <= 0
    BEGIN
        RAISERROR (N'Số lượng nhập phải lớn hơn 0.', 16, 1);
        RETURN;
    END
    INSERT INTO LO_HANG (MaLo, TenLo, MaHang, SoLuongNhap, TonKho, TenVT, NgayNhap)
    VALUES (@MaLo, @TenLo, @MaHang, @SoLuongNhap, @SoLuongNhap, @TenVT, @NgayNhap);
END;
GO
--Kiểm tra
EXEC SP_NhapLoHang 'L021', N'Lo bo sung sua 02', 'MH01', 0, N'Ke sua A3', '2026-03-12';

UPDATE hd
SET TongTien = (
    SELECT SUM(ct.SoLuong * ct.DonGiaBan)
    FROM CHI_TIET_HOA_DON ct
    WHERE ct.MaHD = hd.MaHD
)
FROM HOA_DON hd;
GO
CREATE OR ALTER PROCEDURE SP_BaoCaoDoanhThu
    @TuNgay DATE,
    @DenNgay DATE
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        CAST(NgayLap AS DATE) AS Ngay,
        COUNT(*) AS SoHoaDon,
        SUM(TongTien) AS DoanhThu
    FROM HOA_DON
    WHERE CAST(NgayLap AS DATE) BETWEEN @TuNgay AND @DenNgay
      AND TrangThai = N'Hoàn tất'
    GROUP BY CAST(NgayLap AS DATE)
    ORDER BY Ngay;
END;
GO
EXEC SP_BaoCaoDoanhThu '2026-03-01', '2026-03-10';


CREATE OR ALTER PROCEDURE SP_TopMatHangBanChay
    @TopN INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP (@TopN)
        mh.MaHang,
        mh.TenHang,
        SUM(ct.SoLuong) AS TongSoLuongBan
    FROM CHI_TIET_HOA_DON ct
    JOIN MAT_HANG mh ON mh.MaHang = ct.MaHang
    JOIN HOA_DON hd ON hd.MaHD = ct.MaHD
    WHERE hd.TrangThai = N'Hoàn tất'
    GROUP BY mh.MaHang, mh.TenHang
    ORDER BY SUM(ct.SoLuong) DESC, mh.MaHang;
END;
GO
EXEC SP_TopMatHangBanChay 5;

--------------VIEW---------------------------
CREATE OR ALTER VIEW VW_DoanhThuNgay
AS
SELECT
    CAST(NgayLap AS DATE) AS Ngay,
    COUNT(*) AS SoHoaDon,
    SUM(TongTien) AS DoanhThu
FROM HOA_DON
WHERE TrangThai = N'Hoàn tất'
GROUP BY CAST(NgayLap AS DATE);
GO
SELECT * FROM VW_DoanhThuNgay;

CREATE OR ALTER VIEW VW_TonKhoMatHang
AS
SELECT
    mh.MaHang,
    mh.TenHang,
    SUM(lh.TonKho) AS TongTonKho,
    dbo.fn_KiemTraTonKho(mh.MaHang) AS TrangThaiTonKho
FROM MAT_HANG mh
LEFT JOIN LO_HANG lh ON lh.MaHang = mh.MaHang
GROUP BY mh.MaHang, mh.TenHang;
GO
SELECT * FROM VW_TonKhoMatHang;

CREATE OR ALTER VIEW VW_ChiTietBanHang
AS
SELECT
    hd.MaHD,
    CAST(hd.NgayLap AS DATE) AS NgayLap,
    nv.HoTen AS TenNhanVien,
    kh.HoTen AS TenKhachHang,
    mh.TenHang,
    ct.SoLuong,
    ct.DonGiaBan,
    ct.SoLuong * ct.DonGiaBan AS ThanhTien
FROM HOA_DON hd
JOIN NHAN_VIEN nv ON nv.MaNV = hd.MaNV
LEFT JOIN KHACH_HANG kh ON kh.MaKH = hd.MaKH
JOIN CHI_TIET_HOA_DON ct ON ct.MaHD = hd.MaHD
JOIN MAT_HANG mh ON mh.MaHang = ct.MaHang;
GO
SELECT * FROM VW_ChiTietBanHang;
CREATE OR ALTER VIEW VW_KhachHangThanThiet
AS
SELECT
    MaKH,
    HoTen,
    SDT,
    HangThanhVien,
    DiemTichLuy
FROM KHACH_HANG
WHERE DiemTichLuy >= 300;
GO
SELECT * FROM VW_KhachHangThanThiet;

---10 TRUY VẤN SQL THỰC TẾ
-- 1. Danh sách mặt hàng đang bán
SELECT MaHang, TenHang, GiaBan, TrangThai
FROM MAT_HANG
WHERE TrangThai = N'Đang bán';
GO
-- 2. INNER JOIN mặt hàng với loại hàng
SELECT mh.MaHang, mh.TenHang, lh.TenLoai
FROM MAT_HANG mh
INNER JOIN LOAI_HANG lh ON mh.MaLoai = lh.MaLoai;
GO
-- 3. LEFT JOIN hóa đơn với khách hàng
SELECT hd.MaHD, hd.NgayLap, kh.HoTen, hd.TongTien
FROM HOA_DON hd
LEFT JOIN KHACH_HANG kh ON hd.MaKH = kh.MaKH;
GO
-- 4. RIGHT JOIN mặt hàng với chi tiết hóa đơn
SELECT mh.TenHang, ct.MaHD, ct.SoLuong
FROM MAT_HANG mh
RIGHT JOIN CHI_TIET_HOA_DON ct ON mh.MaHang = ct.MaHang;
GO
-- 5. GROUP BY doanh thu theo nhân viên
SELECT nv.MaNV, nv.HoTen, SUM(hd.TongTien) AS TongDoanhThu
FROM HOA_DON hd
JOIN NHAN_VIEN nv ON hd.MaNV = nv.MaNV
GROUP BY nv.MaNV, nv.HoTen;
GO
-- 6. Liệt kê các nhân viên có tổng số lượng mặt hàng đã bán lớn hơn 3
SELECT nv.MaNV, nv.HoTen, SUM(ct.SoLuong) AS TongSoLuongDaBan
FROM HOA_DON hd
JOIN NHAN_VIEN nv ON hd.MaNV = nv.MaNV
JOIN CHI_TIET_HOA_DON ct ON hd.MaHD = ct.MaHD
GROUP BY nv.MaNV, nv.HoTen
HAVING SUM(ct.SoLuong) > 3;
GO
-- 7. Subquery tìm mặt hàng có giá bán cao hơn giá bán trung bình
SELECT MaHang, TenHang, GiaBan
FROM MAT_HANG
WHERE GiaBan > (SELECT AVG(GiaBan) FROM MAT_HANG);
GO
-- 8. Aggregate function COUNT, SUM, AVG, MAX, MIN
SELECT
    COUNT(*) AS SoMatHang,
    SUM(GiaBan) AS TongGiaBan,
    AVG(GiaBan) AS GiaTrungBinh,
    MAX(GiaBan) AS GiaCaoNhat,
    MIN(GiaBan) AS GiaThapNhat
FROM MAT_HANG;
GO
-- 9. Tổng tồn kho theo mặt hàng
SELECT mh.MaHang, mh.TenHang, SUM(lh.TonKho) AS TongTonKho
FROM MAT_HANG mh
JOIN LO_HANG lh ON mh.MaHang = lh.MaHang
GROUP BY mh.MaHang, mh.TenHang;
GO
-- 10. Top 5 mặt hàng bán chạy
SELECT TOP 5 mh.MaHang, mh.TenHang, SUM(ct.SoLuong) AS TongBan
FROM CHI_TIET_HOA_DON ct
JOIN MAT_HANG mh ON ct.MaHang = mh.MaHang
GROUP BY mh.MaHang, mh.TenHang
ORDER BY SUM(ct.SoLuong) DESC;
GO
----6. LỆNH DEMO VIEW, PROCEDURE, FUNCTION
SELECT * FROM VW_DoanhThuNgay;
SELECT * FROM VW_TonKhoMatHang;
SELECT * FROM VW_ChiTietBanHang;
SELECT * FROM VW_KhachHangThanThiet;
GO
EXEC SP_BaoCaoDoanhThu '2026-03-01', '2026-03-10';
EXEC SP_TopMatHangBanChay 5;
GO
-- nhập lô hàng
-- EXEC SP_NhapLoHang 'L021', N'Lo bo sung sua 02', 'MH01', 40, N'Ke sua A3', '2026-03-12';
SELECT dbo.fn_KiemTraTonKho('MH01') AS TrangThaiTonKho_MH01;
GO
---7. KIỂM TRA SỐ BẢN GHI
SELECT 'NGANH_HANG' AS TenBang, COUNT(*) AS SoBanGhi FROM NGANH_HANG
UNION ALL SELECT 'NHA_SAN_XUAT', COUNT(*) FROM NHA_SAN_XUAT
UNION ALL SELECT 'NHA_PHAN_PHOI', COUNT(*) FROM NHA_PHAN_PHOI
UNION ALL SELECT 'KHUYEN_MAI', COUNT(*) FROM KHUYEN_MAI
UNION ALL SELECT 'NHAN_VIEN', COUNT(*) FROM NHAN_VIEN
UNION ALL SELECT 'LOAI_HANG', COUNT(*) FROM LOAI_HANG
UNION ALL SELECT 'TAI_KHOAN', COUNT(*) FROM TAI_KHOAN
UNION ALL SELECT 'KHACH_HANG', COUNT(*) FROM KHACH_HANG
UNION ALL SELECT 'MAT_HANG', COUNT(*) FROM MAT_HANG
UNION ALL SELECT 'LO_HANG', COUNT(*) FROM LO_HANG
UNION ALL SELECT 'HOA_DON', COUNT(*) FROM HOA_DON
UNION ALL SELECT 'CHI_TIET_HOA_DON', COUNT(*) FROM CHI_TIET_HOA_DON;
GO

/* =========================================================
   8. PHAN QUYEN
   ========================================================= */


IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'NhomQuanLy')
    CREATE ROLE NhomQuanLy;
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'NhomNhanVien')
    CREATE ROLE NhomNhanVien;
GO

GRANT CONTROL ON DATABASE::QuanLySieuThi TO NhomQuanLy;
GO

GRANT SELECT ON NGANH_HANG TO NhomNhanVien;
GRANT SELECT ON LOAI_HANG TO NhomNhanVien;
GRANT SELECT ON MAT_HANG TO NhomNhanVien;
GRANT SELECT ON LO_HANG TO NhomNhanVien;
GRANT SELECT ON KHUYEN_MAI TO NhomNhanVien;
GRANT SELECT ON KHACH_HANG TO NhomNhanVien;
GRANT SELECT ON NHAN_VIEN TO NhomNhanVien;
GRANT SELECT, INSERT, UPDATE ON HOA_DON TO NhomNhanVien;
GRANT SELECT, INSERT, UPDATE ON CHI_TIET_HOA_DON TO NhomNhanVien;
GO

DENY INSERT, UPDATE, DELETE ON NGANH_HANG TO NhomNhanVien;
DENY INSERT, UPDATE, DELETE ON LOAI_HANG TO NhomNhanVien;
DENY INSERT, UPDATE, DELETE ON MAT_HANG TO NhomNhanVien;
DENY INSERT, UPDATE, DELETE ON LO_HANG TO NhomNhanVien;
DENY INSERT, UPDATE, DELETE ON KHUYEN_MAI TO NhomNhanVien;
DENY INSERT, UPDATE, DELETE ON NHAN_VIEN TO NhomNhanVien;
DENY INSERT, UPDATE, DELETE ON TAI_KHOAN TO NhomNhanVien;
DENY DELETE ON HOA_DON TO NhomNhanVien;
DENY DELETE ON CHI_TIET_HOA_DON TO NhomNhanVien;
GO

IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'admin_tam')
    CREATE LOGIN admin_tam WITH PASSWORD = '123456';
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'thu_ngan_02')
    CREATE LOGIN thu_ngan_02 WITH PASSWORD = '123456';
IF NOT EXISTS (SELECT 1 FROM sys.server_principals WHERE name = N'thu_ngan_03')
    CREATE LOGIN thu_ngan_03 WITH PASSWORD = '123456';
GO

IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'admin_tam')
    CREATE USER admin_tam FOR LOGIN admin_tam;
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'thu_ngan_02')
    CREATE USER thu_ngan_02 FOR LOGIN thu_ngan_02;
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'thu_ngan_03')
    CREATE USER thu_ngan_03 FOR LOGIN thu_ngan_03;
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.database_role_members rm
    JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
    JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
    WHERE r.name = N'NhomQuanLy' AND m.name = N'admin_tam'
)
    ALTER ROLE NhomQuanLy ADD MEMBER admin_tam;

IF NOT EXISTS (
    SELECT 1
    FROM sys.database_role_members rm
    JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
    JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
    WHERE r.name = N'NhomNhanVien' AND m.name = N'thu_ngan_02'
)
    ALTER ROLE NhomNhanVien ADD MEMBER thu_ngan_02;

IF NOT EXISTS (
    SELECT 1
    FROM sys.database_role_members rm
    JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
    JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
    WHERE r.name = N'NhomNhanVien' AND m.name = N'thu_ngan_03'
)
    ALTER ROLE NhomNhanVien ADD MEMBER thu_ngan_03;
GO

SELECT 
    r.name AS RoleName,
    OBJECT_NAME(perm.major_id) AS TableName,
    perm.permission_name,
    perm.state_desc
FROM sys.database_permissions perm
JOIN sys.database_principals r 
    ON perm.grantee_principal_id = r.principal_id
WHERE r.name IN ('NhomQuanLy', 'NhomNhanVien')
AND perm.major_id > 0
ORDER BY r.name, TableName;

SELECT 
    u.name AS UserName,
    r.name AS RoleName
FROM sys.database_role_members rm
JOIN sys.database_principals r 
    ON rm.role_principal_id = r.principal_id
JOIN sys.database_principals u 
    ON rm.member_principal_id = u.principal_id
WHERE u.name IN ('admin_tam', 'thu_ngan_02', 'thu_ngan_03');

