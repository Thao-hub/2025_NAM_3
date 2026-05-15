SET SERVEROUTPUT ON;

-----Tạo bảng HangSX
CREATE TABLE HangSX (
    MaHangSX VARCHAR2(10) CONSTRAINT pk_hangsx PRIMARY KEY,
    TenHang  VARCHAR2(100) NOT NULL,
    DiaChi   VARCHAR2(200),
    SoDT     VARCHAR2(15),
    Email    VARCHAR2(100)
);
/
-----Tạo bảng NhanVien
CREATE TABLE NhanVien (
    MaNV      VARCHAR2(10) CONSTRAINT pk_nhanvien PRIMARY KEY,
    TenNV     VARCHAR2(100) NOT NULL,
    GioiTinh  VARCHAR2(10),
    DiaChi    VARCHAR2(200),
    SoDT      VARCHAR2(15),
    Email     VARCHAR2(100),
    TenPhong  VARCHAR2(100)
);
/
-----Tạo bảng SanPham
CREATE TABLE SanPham (
    MaSP       VARCHAR2(10) CONSTRAINT pk_sanpham PRIMARY KEY,
    MaHangSX   VARCHAR2(10) NOT NULL,
    TenSP      VARCHAR2(100) NOT NULL,
    SoLuong    NUMBER(10) DEFAULT 0 NOT NULL,
    MauSac     VARCHAR2(30),
    GiaBan     NUMBER(15,2) NOT NULL,
    DonViTinh  VARCHAR2(20),
    MoTa       VARCHAR2(200),
    CONSTRAINT fk_sanpham_hangsx FOREIGN KEY (MaHangSX) REFERENCES HangSX(MaHangSX)
);
/
-----Tạo bảng PNhap
CREATE TABLE PNhap (
    SoHDN     VARCHAR2(10) CONSTRAINT pk_pnhap PRIMARY KEY,
    NgayNhap  DATE NOT NULL,
    MaNV      VARCHAR2(10) NOT NULL,
    CONSTRAINT fk_pnhap_nhanvien FOREIGN KEY (MaNV) REFERENCES NhanVien(MaNV)
);
/
-----Tạo bảng Nhap
CREATE TABLE Nhap (
    SoHDN     VARCHAR2(10) NOT NULL,
    MaSP      VARCHAR2(10) NOT NULL,
    SoLuongN  NUMBER(10) NOT NULL,
    DonGiaN   NUMBER(15,2) NOT NULL,
    CONSTRAINT pk_nhap PRIMARY KEY (SoHDN, MaSP),
    CONSTRAINT fk_nhap_pnhap FOREIGN KEY (SoHDN) REFERENCES PNhap(SoHDN),
    CONSTRAINT fk_nhap_sanpham FOREIGN KEY (MaSP) REFERENCES SanPham(MaSP)
);
/
-----Tạo bảng PXuat
CREATE TABLE PXuat (
    SoHDX     VARCHAR2(10) CONSTRAINT pk_pxuat PRIMARY KEY,
    NgayXuat  DATE NOT NULL,
    MaNV      VARCHAR2(10) NOT NULL,
    CONSTRAINT fk_pxuat_nhanvien FOREIGN KEY (MaNV) REFERENCES NhanVien(MaNV)
);
/
-----Tạo bảng Xuat
CREATE TABLE Xuat (
    SoHDX     VARCHAR2(10) NOT NULL,
    MaSP      VARCHAR2(10) NOT NULL,
    SoLuongX  NUMBER(10) NOT NULL,
    CONSTRAINT pk_xuat PRIMARY KEY (SoHDX, MaSP),
    CONSTRAINT fk_xuat_pxuat FOREIGN KEY (SoHDX) REFERENCES PXuat(SoHDX),
    CONSTRAINT fk_xuat_sanpham FOREIGN KEY (MaSP) REFERENCES SanPham(MaSP)
);
/
-----Insert 5 dữ liệu bảng HangSX
INSERT INTO HangSX VALUES ('HSX01', 'Samsung', 'Ha Noi', '0901000001', 'samsung@gmail.com');
INSERT INTO HangSX VALUES ('HSX02', 'Sony', 'TP.HCM', '0901000002', 'sony@gmail.com');
INSERT INTO HangSX VALUES ('HSX03', 'LG', 'Da Nang', '0901000003', 'lg@gmail.com');
INSERT INTO HangSX VALUES ('HSX04', 'Panasonic', 'Can Tho', '0901000004', 'panasonic@gmail.com');
INSERT INTO HangSX VALUES ('HSX05', 'Sharp', 'Hai Phong', '0901000005', 'sharp@gmail.com');
-----Insert 5 dữ liệu bảng NhanVien
INSERT INTO NhanVien VALUES ('NV01', 'Nguyen Van An', 'Nam', 'Quan 1', '0911000001', 'an@gmail.com', 'Kinh Doanh');
INSERT INTO NhanVien VALUES ('NV02', 'Tran Thi Binh', 'Nu', 'Quan 3', '0911000002', 'binh@gmail.com', 'Ke Toan');
INSERT INTO NhanVien VALUES ('NV03', 'Le Van Cuong', 'Nam', 'Thu Duc', '0911000003', 'cuong@gmail.com', 'Kho');
INSERT INTO NhanVien VALUES ('NV04', 'Pham Thi Dung', 'Nu', 'Go Vap', '0911000004', 'dung@gmail.com', 'Ban Hang');
INSERT INTO NhanVien VALUES ('NV05', 'Hoang Minh Duc', 'Nam', 'Binh Thanh', '0911000005', 'duc@gmail.com', 'Van Phong');
-----Insert 5 dữ liệu bảng SanPham
INSERT INTO SanPham VALUES ('SP01', 'HSX01', 'Tivi 43 inch', 50, 'Den', 8500000, 'Cai', 'Tivi thong minh');
INSERT INTO SanPham VALUES ('SP02', 'HSX02', 'Loa Bluetooth', 80, 'Xam', 1200000, 'Cai', 'Loa mini');
INSERT INTO SanPham VALUES ('SP03', 'HSX03', 'May giat', 30, 'Trang', 7200000, 'Cai', 'May giat cua ngang');
INSERT INTO SanPham VALUES ('SP04', 'HSX04', 'Dieu hoa', 25, 'Trang', 9800000, 'Cai', 'Dieu hoa inverter');
INSERT INTO SanPham VALUES ('SP05', 'HSX05', 'Lo vi song', 40, 'Bac', 2500000, 'Cai', 'Lo vi song gia dinh');
-----Insert 5 dữ liệu bảng PNhap
INSERT INTO PNhap VALUES ('N001', DATE '2026-03-01', 'NV01');
INSERT INTO PNhap VALUES ('N002', DATE '2026-03-02', 'NV02');
INSERT INTO PNhap VALUES ('N003', DATE '2026-03-03', 'NV03');
INSERT INTO PNhap VALUES ('N004', DATE '2026-03-04', 'NV04');
INSERT INTO PNhap VALUES ('N005', DATE '2026-03-05', 'NV05');
-----Insert 5 dữ liệu bảng Nhap
INSERT INTO Nhap VALUES ('N001', 'SP01', 10, 7000000);
INSERT INTO Nhap VALUES ('N002', 'SP02', 15, 900000);
INSERT INTO Nhap VALUES ('N003', 'SP03', 5, 6000000);
INSERT INTO Nhap VALUES ('N004', 'SP04', 7, 8200000);
INSERT INTO Nhap VALUES ('N005', 'SP05', 12, 1800000);
-----Insert 5 dữ liệu bảng PXuat
INSERT INTO PXuat VALUES ('X001', DATE '2026-03-10', 'NV01');
INSERT INTO PXuat VALUES ('X002', DATE '2026-03-11', 'NV02');
INSERT INTO PXuat VALUES ('X003', DATE '2026-03-12', 'NV03');
INSERT INTO PXuat VALUES ('X004', DATE '2026-03-13', 'NV04');
INSERT INTO PXuat VALUES ('X005', DATE '2026-03-14', 'NV05');

-----Insert 5 dữ liệu bảng Xuat
INSERT INTO Xuat VALUES ('X001', 'SP01', 5);
INSERT INTO Xuat VALUES ('X002', 'SP02', 8);
INSERT INTO Xuat VALUES ('X003', 'SP03', 3);
INSERT INTO Xuat VALUES ('X004', 'SP04', 2);
INSERT INTO Xuat VALUES ('X005', 'SP05', 4);

COMMIT;
-----a. Trigger INSERT bảng NHAP – trg_Nhap
CREATE OR REPLACE TRIGGER trg_Nhap
BEFORE INSERT ON Nhap
FOR EACH ROW
DECLARE
    v_dem      NUMBER := 0;
    v_so_luong NUMBER := 0;
BEGIN
    SELECT COUNT(*)
      INTO v_dem
      FROM SanPham
     WHERE MaSP = :NEW.MaSP;
    IF v_dem = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'MaSP khong ton tai trong bang SanPham');
    END IF;
    IF NVL(:NEW.SoLuongN, 0) <= 0 OR NVL(:NEW.DonGiaN, 0) <= 0 THEN
        RAISE_APPLICATION_ERROR(-20002, 'SoLuongN va DonGiaN phai lon hon 0');
    END IF;
    SELECT SoLuong
      INTO v_so_luong
      FROM SanPham
     WHERE MaSP = :NEW.MaSP
       FOR UPDATE;
    UPDATE SanPham
       SET SoLuong = v_so_luong + :NEW.SoLuongN
     WHERE MaSP = :NEW.MaSP;
END trg_Nhap;
/

-----b. Trigger INSERT bảng XUAT – trg_Xuat
CREATE OR REPLACE TRIGGER trg_Xuat
BEFORE INSERT ON Xuat
FOR EACH ROW
DECLARE
    v_dem      NUMBER := 0;
    v_so_luong NUMBER := 0;
BEGIN
    SELECT COUNT(*)
      INTO v_dem
      FROM SanPham
     WHERE MaSP = :NEW.MaSP;
    IF v_dem = 0 THEN
        RAISE_APPLICATION_ERROR(-20003, 'MaSP khong ton tai trong bang SanPham');
    END IF;
    IF NVL(:NEW.SoLuongX, 0) <= 0 THEN
        RAISE_APPLICATION_ERROR(-20004, 'SoLuongX phai lon hon 0');
    END IF;
    SELECT SoLuong
      INTO v_so_luong
      FROM SanPham
     WHERE MaSP = :NEW.MaSP
       FOR UPDATE;
    IF :NEW.SoLuongX > v_so_luong THEN
        RAISE_APPLICATION_ERROR(-20005, 'SoLuongX vuot qua so luong ton trong SanPham');
    END IF;
    UPDATE SanPham
       SET SoLuong = v_so_luong - :NEW.SoLuongX
     WHERE MaSP = :NEW.MaSP;
END trg_Xuat;
/

-----c. Trigger DELETE bảng XUAT – trg_XoaXuat
CREATE OR REPLACE TRIGGER trg_XoaXuat
AFTER DELETE ON Xuat
FOR EACH ROW
BEGIN
    UPDATE SanPham
       SET SoLuong = SoLuong + :OLD.SoLuongX
     WHERE MaSP = :OLD.MaSP;
END trg_XoaXuat;
/

----- PHIEU BAI TAP 2 -----

-----Package đếm số dòng cho Compound Trigger – pkg_state
CREATE OR REPLACE PACKAGE pkg_state AS
    g_row_count NUMBER := 0;
END pkg_state;
/

-----a. Trigger UPDATE bảng XUAT – trg_CapNhatXuat
CREATE OR REPLACE TRIGGER trg_CapNhatXuat
FOR UPDATE ON Xuat
COMPOUND TRIGGER
    BEFORE STATEMENT IS
    BEGIN
        pkg_state.g_row_count := 0;
    END BEFORE STATEMENT;

    BEFORE EACH ROW IS
        v_ton_cu  NUMBER := 0;
        v_ton_moi NUMBER := 0;
    BEGIN
        pkg_state.g_row_count := pkg_state.g_row_count + 1;

        IF pkg_state.g_row_count > 1 THEN
            RAISE_APPLICATION_ERROR(-20011, 'Chi duoc UPDATE 1 ban ghi tren bang Xuat');
        END IF;

        IF NVL(:NEW.SoLuongX, 0) <= 0 THEN
            RAISE_APPLICATION_ERROR(-20012, 'SoLuongX phai lon hon 0');
        END IF;

        IF :NEW.MaSP <> :OLD.MaSP THEN
            SELECT SoLuong
              INTO v_ton_moi
              FROM SanPham
             WHERE MaSP = :NEW.MaSP
               FOR UPDATE;

            IF :NEW.SoLuongX > v_ton_moi THEN
                RAISE_APPLICATION_ERROR(-20013, 'SanPham moi khong du so luong de xuat');
            END IF;
        ELSE
            SELECT SoLuong
              INTO v_ton_cu
              FROM SanPham
             WHERE MaSP = :OLD.MaSP
               FOR UPDATE;

            IF (:NEW.SoLuongX - :OLD.SoLuongX) > v_ton_cu THEN
                RAISE_APPLICATION_ERROR(-20014, 'Khong du so luong ton de cap nhat phieu xuat');
            END IF;
        END IF;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            RAISE_APPLICATION_ERROR(-20015, 'MaSP khong ton tai trong bang SanPham');
    END BEFORE EACH ROW;

    AFTER EACH ROW IS
    BEGIN
        IF :NEW.MaSP <> :OLD.MaSP THEN
            UPDATE SanPham
               SET SoLuong = SoLuong + :OLD.SoLuongX
             WHERE MaSP = :OLD.MaSP;

            UPDATE SanPham
               SET SoLuong = SoLuong - :NEW.SoLuongX
             WHERE MaSP = :NEW.MaSP;
        ELSE
            UPDATE SanPham
               SET SoLuong = SoLuong - (:NEW.SoLuongX - :OLD.SoLuongX)
             WHERE MaSP = :NEW.MaSP;
        END IF;
    END AFTER EACH ROW;
END trg_CapNhatXuat;
/

-----b. Trigger UPDATE bảng NHAP – trg_CapNhatNhap
CREATE OR REPLACE TRIGGER trg_CapNhatNhap
FOR UPDATE ON Nhap
COMPOUND TRIGGER
    BEFORE STATEMENT IS
    BEGIN
        pkg_state.g_row_count := 0;
    END BEFORE STATEMENT;

    BEFORE EACH ROW IS
    BEGIN
        pkg_state.g_row_count := pkg_state.g_row_count + 1;

        IF pkg_state.g_row_count > 1 THEN
            RAISE_APPLICATION_ERROR(-20021, 'Chi duoc UPDATE 1 ban ghi tren bang Nhap');
        END IF;

        IF NVL(:NEW.SoLuongN, 0) <= 0 OR NVL(:NEW.DonGiaN, 0) <= 0 THEN
            RAISE_APPLICATION_ERROR(-20022, 'SoLuongN va DonGiaN phai lon hon 0');
        END IF;
    END BEFORE EACH ROW;

    AFTER EACH ROW IS
    BEGIN
        IF :NEW.MaSP <> :OLD.MaSP THEN
            UPDATE SanPham
               SET SoLuong = SoLuong - :OLD.SoLuongN
             WHERE MaSP = :OLD.MaSP;

            UPDATE SanPham
               SET SoLuong = SoLuong + :NEW.SoLuongN
             WHERE MaSP = :NEW.MaSP;
        ELSE
            UPDATE SanPham
               SET SoLuong = SoLuong + (:NEW.SoLuongN - :OLD.SoLuongN)
             WHERE MaSP = :NEW.MaSP;
        END IF;
    END AFTER EACH ROW;
END trg_CapNhatNhap;
/

-----c. Trigger DELETE bảng NHAP – trg_XoaNhap
CREATE OR REPLACE TRIGGER trg_XoaNhap
AFTER DELETE ON Nhap
FOR EACH ROW
DECLARE
    v_so_luong NUMBER := 0;
BEGIN
    SELECT SoLuong
      INTO v_so_luong
      FROM SanPham
     WHERE MaSP = :OLD.MaSP
       FOR UPDATE;

    IF :OLD.SoLuongN > v_so_luong THEN
        RAISE_APPLICATION_ERROR(-20031, 'Khong the xoa phieu nhap vi so luong ton se bi am');
    END IF;

    UPDATE SanPham
       SET SoLuong = v_so_luong - :OLD.SoLuongN
     WHERE MaSP = :OLD.MaSP;
END trg_XoaNhap;
/
