CREATE TABLE HangSX (
MaHangSX VARCHAR2(10) CONSTRAINT pk_hangsx PRIMARY KEY,
TenHang VARCHAR2(30) NOT NULL,
DiaChi VARCHAR2(50),
SoDT VARCHAR2(15),

Email VARCHAR2(50)
);
CREATE TABLE SanPham (
MaSP VARCHAR2(10) CONSTRAINT pk_sanpham PRIMARY KEY,
MaHangSX VARCHAR2(10) REFERENCES HangSX(MaHangSX),
TenSP VARCHAR2(50) NOT NULL,
SoLuong NUMBER(10),
MauSac VARCHAR2(20),
GiaBan NUMBER(15,2),
DonViTinh VARCHAR2(15),
MoTa CLOB
);
CREATE TABLE NhanVien (
MaNV VARCHAR2(10) CONSTRAINT pk_nhanvien PRIMARY KEY,
TenNV VARCHAR2(50) NOT NULL,
GioiTinh VARCHAR2(10),
DiaChi VARCHAR2(100),
SoDT VARCHAR2(15),
Email VARCHAR2(50),
TenPhong VARCHAR2(30)
);
CREATE TABLE PNhap (
SoHDN VARCHAR2(10) CONSTRAINT pk_pnhap PRIMARY KEY,
NgayNhap DATE,
MaNV VARCHAR2(10) REFERENCES NhanVien(MaNV)
);
CREATE TABLE Nhap (
SoHDN VARCHAR2(10) REFERENCES PNhap(SoHDN),
MaSP VARCHAR2(10) REFERENCES SanPham(MaSP),
SoLuongN NUMBER(10),
DonGiaN NUMBER(15,2),
CONSTRAINT pk_nhap PRIMARY KEY (SoHDN, MaSP)
);
CREATE TABLE PXuat (
SoHDX VARCHAR2(10) CONSTRAINT pk_pxuat PRIMARY KEY,
NgayXuat DATE,
MaNV VARCHAR2(10) REFERENCES NhanVien(MaNV)
);
CREATE TABLE Xuat (
SoHDX VARCHAR2(10) REFERENCES PXuat(SoHDX),
MaSP VARCHAR2(10) REFERENCES SanPham(MaSP),
SoLuongX NUMBER(10),
CONSTRAINT pk_xuat PRIMARY KEY (SoHDX, MaSP)
);

-----phieu bai tap 1
---Câu a:  Thủ tục sp_NhapHangSX
CREATE OR REPLACE PROCEDURE sp_NhapHangSX(
    p_MaHangSX VARCHAR2,
    p_TenHang VARCHAR2,
    p_DiaChi VARCHAR2,
    p_SoDT VARCHAR2,
    p_Email VARCHAR2
)
AS
    v_count NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM HangSX
    WHERE TenHang = p_TenHang;

    IF v_count > 0 THEN
        DBMS_OUTPUT.PUT_LINE('Ten hang da ton tai');
    ELSE
        INSERT INTO HangSX
        VALUES(p_MaHangSX,p_TenHang,p_DiaChi,p_SoDT,p_Email);
    END IF;
END;

SET SERVEROUTPUT ON;
---kiểm tra
BEGIN
    sp_NhapHangSX('HSX06','LG','Hàn Quốc','0906666666','lg@gmail.com');
END;
SELECT * FROM HangSX WHERE TenHang='LG';

---Câu b: Thủ tục sp_NhapSP
CREATE OR REPLACE PROCEDURE sp_NhapSP(
    p_MaSP VARCHAR2,
    p_TenHang VARCHAR2,
    p_TenSP VARCHAR2,
    p_SoLuong NUMBER,
    p_MauSac VARCHAR2,
    p_GiaBan NUMBER,
    p_DonViTinh VARCHAR2,
    p_MoTa VARCHAR2
)
AS
    v_mahang VARCHAR2(10);
    v_count NUMBER;
BEGIN

    SELECT MaHangSX INTO v_mahang
    FROM HangSX
    WHERE TenHang = p_TenHang;

    SELECT COUNT(*) INTO v_count
    FROM SanPham
    WHERE MaSP = p_MaSP;

    IF v_count > 0 THEN
        UPDATE SanPham
        SET TenSP=p_TenSP,
            SoLuong=p_SoLuong,
            MauSac=p_MauSac,
            GiaBan=p_GiaBan,
            DonViTinh=p_DonViTinh,
            MoTa=p_MoTa
        WHERE MaSP=p_MaSP;
    ELSE
        INSERT INTO SanPham
        VALUES(p_MaSP,v_mahang,p_TenSP,p_SoLuong,p_MauSac,p_GiaBan,p_DonViTinh,p_MoTa);
    END IF;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('Ten hang khong ton tai');

END;


---Câu c: Thủ tục sp_xoaHangSX
CREATE OR REPLACE PROCEDURE sp_xoaHangSX(
    p_TenHang VARCHAR2
)
AS
    v_mahang VARCHAR2(10);
BEGIN

    SELECT MaHangSX INTO v_mahang
    FROM HangSX
    WHERE TenHang=p_TenHang;

    DELETE FROM SanPham
    WHERE MaHangSX=v_mahang;

    DELETE FROM HangSX
    WHERE MaHangSX=v_mahang;

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('Ten hang khong ton tai');
END;

---Câu d: Thủ tục nhập dữ liệu NhanVien (có biến FLAG)
CREATE OR REPLACE PROCEDURE sp_NhapNhanVien(
    p_MaNV VARCHAR2,
    p_TenNV VARCHAR2,
    p_GioiTinh VARCHAR2,
    p_DiaChi VARCHAR2,
    p_SoDT VARCHAR2,
    p_Email VARCHAR2,
    p_TenPhong VARCHAR2,
    p_Flag NUMBER
)
AS
BEGIN

    IF p_Flag = 0 THEN

        UPDATE NhanVien
        SET TenNV=p_TenNV,
            GioiTinh=p_GioiTinh,
            DiaChi=p_DiaChi,
            SoDT=p_SoDT,
            Email=p_Email,
            TenPhong=p_TenPhong
        WHERE MaNV=p_MaNV;

    ELSE

        INSERT INTO NhanVien
        VALUES(p_MaNV,p_TenNV,p_GioiTinh,p_DiaChi,p_SoDT,p_Email,p_TenPhong);

    END IF;

END;

---Câu e: Thủ tục nhập dữ liệu bảng Nhap
CREATE OR REPLACE PROCEDURE sp_NhapNhap(
    p_SoHDN VARCHAR2,
    p_MaSP VARCHAR2,
    p_MaNV VARCHAR2,
    p_NgayNhap DATE,
    p_SoLuongN NUMBER,
    p_DonGiaN NUMBER
)
AS
    v_count NUMBER;
BEGIN

    SELECT COUNT(*) INTO v_count FROM SanPham WHERE MaSP=p_MaSP;
    IF v_count=0 THEN
        DBMS_OUTPUT.PUT_LINE('MaSP khong ton tai');
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_count FROM NhanVien WHERE MaNV=p_MaNV;
    IF v_count=0 THEN
        DBMS_OUTPUT.PUT_LINE('MaNV khong ton tai');
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_count FROM PNhap WHERE SoHDN=p_SoHDN;

    IF v_count>0 THEN

        UPDATE Nhap
        SET SoLuongN=p_SoLuongN,
            DonGiaN=p_DonGiaN
        WHERE SoHDN=p_SoHDN AND MaSP=p_MaSP;

    ELSE

        INSERT INTO PNhap VALUES(p_SoHDN,p_NgayNhap,p_MaNV);

        INSERT INTO Nhap
        VALUES(p_SoHDN,p_MaSP,p_SoLuongN,p_DonGiaN);

    END IF;

END;

---Câu f: Thủ tục nhập dữ liệu bảng Xuat
CREATE OR REPLACE PROCEDURE sp_NhapXuat(
    p_SoHDX VARCHAR2,
    p_MaSP VARCHAR2,
    p_MaNV VARCHAR2,
    p_NgayXuat DATE,
    p_SoLuongX NUMBER
)
AS
    v_count NUMBER;
    v_soluong NUMBER;
BEGIN

    SELECT COUNT(*) INTO v_count FROM SanPham WHERE MaSP=p_MaSP;
    IF v_count=0 THEN
        DBMS_OUTPUT.PUT_LINE('MaSP khong ton tai');
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_count FROM NhanVien WHERE MaNV=p_MaNV;
    IF v_count=0 THEN
        DBMS_OUTPUT.PUT_LINE('MaNV khong ton tai');
        RETURN;
    END IF;

    SELECT SoLuong INTO v_soluong
    FROM SanPham
    WHERE MaSP=p_MaSP;

    IF p_SoLuongX > v_soluong THEN
        DBMS_OUTPUT.PUT_LINE('Khong du hang');
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_count FROM PXuat WHERE SoHDX=p_SoHDX;

    IF v_count>0 THEN

        UPDATE Xuat
        SET SoLuongX=p_SoLuongX
        WHERE SoHDX=p_SoHDX AND MaSP=p_MaSP;

    ELSE

        INSERT INTO PXuat VALUES(p_SoHDX,p_NgayXuat,p_MaNV);

        INSERT INTO Xuat VALUES(p_SoHDX,p_MaSP,p_SoLuongX);

    END IF;

END;

---Câu g: Thủ tục xóa NhanVien
CREATE OR REPLACE PROCEDURE sp_XoaNhanVien(
    p_MaNV VARCHAR2
)
AS
    v_count NUMBER;
BEGIN

    SELECT COUNT(*) INTO v_count
    FROM NhanVien
    WHERE MaNV=p_MaNV;

    IF v_count=0 THEN
        DBMS_OUTPUT.PUT_LINE('Nhan vien khong ton tai');
        RETURN;
    END IF;

    DELETE FROM Nhap
    WHERE SoHDN IN (SELECT SoHDN FROM PNhap WHERE MaNV=p_MaNV);

    DELETE FROM PNhap WHERE MaNV=p_MaNV;

    DELETE FROM Xuat
    WHERE SoHDX IN (SELECT SoHDX FROM PXuat WHERE MaNV=p_MaNV);

    DELETE FROM PXuat WHERE MaNV=p_MaNV;

    DELETE FROM NhanVien WHERE MaNV=p_MaNV;

END;

---Câu h: Thủ tục xóa SanPham
CREATE OR REPLACE PROCEDURE sp_XoaSanPham(
    p_MaSP VARCHAR2
)
AS
    v_count NUMBER;
BEGIN

    SELECT COUNT(*) INTO v_count
    FROM SanPham
    WHERE MaSP=p_MaSP;

    IF v_count=0 THEN
        DBMS_OUTPUT.PUT_LINE('San pham khong ton tai');
        RETURN;
    END IF;

    DELETE FROM Nhap WHERE MaSP=p_MaSP;

    DELETE FROM Xuat WHERE MaSP=p_MaSP;

    DELETE FROM SanPham WHERE MaSP=p_MaSP;

END;

---a. Thủ tục sp_ThemNhanVien (có OUT)
CREATE OR REPLACE PROCEDURE sp_ThemNhanVien(
    MaNV VARCHAR2,
    TenNV VARCHAR2,
    GioiTinh VARCHAR2,
    DiaChi VARCHAR2,
    SoDT VARCHAR2,
    Email VARCHAR2,
    TenPhong VARCHAR2,
    Flag NUMBER,
    KQ OUT NUMBER
)
AS
    v_count NUMBER;
BEGIN

    SELECT COUNT(*) INTO v_count
    FROM NhanVien
    WHERE MaNV = sp_ThemNhanVien.MaNV;

    IF v_count = 0 AND Flag = 1 THEN
        KQ := 1;

    ELSIF Flag = 0 THEN
        INSERT INTO NhanVien
        VALUES(MaNV,TenNV,GioiTinh,DiaChi,SoDT,Email,TenPhong);
        KQ := 0;

    ELSE
        UPDATE NhanVien
        SET TenNV = TenNV,
            GioiTinh = GioiTinh,
            DiaChi = DiaChi,
            SoDT = SoDT,
            Email = Email,
            TenPhong = TenPhong
        WHERE MaNV = MaNV;

        KQ := 0;
    END IF;

END;

---b. Thủ tục sp_ThemMoiSP (có OUT)
CREATE OR REPLACE PROCEDURE sp_ThemMoiSP(
    MaSP VARCHAR2,
    TenHang VARCHAR2,
    TenSP VARCHAR2,
    SoLuong NUMBER,
    MauSac VARCHAR2,
    GiaBan NUMBER,
    DonViTinh VARCHAR2,
    MoTa VARCHAR2,
    Flag NUMBER,
    KQ OUT NUMBER
)
AS
    v_count NUMBER;
    v_mahang VARCHAR2(10);
BEGIN
    IF TenHang IS NULL THEN
        KQ := 1;
    ELSIF SoLuong < 0 THEN
        KQ := 2;
    ELSE
        SELECT MaHangSX INTO v_mahang
        FROM HangSX
        WHERE TenHang = TenHang;
        SELECT COUNT(*) INTO v_count
        FROM SanPham
        WHERE MaSP = MaSP;
        IF v_count > 0 THEN
            UPDATE SanPham
            SET MaHangSX = v_mahang,
                TenSP = TenSP,
                SoLuong = SoLuong,
                MauSac = MauSac,
                GiaBan = GiaBan,
                DonViTinh = DonViTinh,
                MoTa = MoTa
            WHERE MaSP = MaSP;
        ELSE
            INSERT INTO SanPham
            VALUES(MaSP,v_mahang,TenSP,SoLuong,MauSac,GiaBan,DonViTinh,MoTa);
        END IF;
        KQ := 0;
    END IF;
END;

---c. Thủ tục xóa NhanVien (có OUT)
CREATE OR REPLACE PROCEDURE xoaSanPham(
    MaSP VARCHAR2,
    KQ OUT NUMBER
)
AS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM SanPham
    WHERE MaSP = xoaSanPham.MaSP;
    IF v_count = 0 THEN
        KQ := 1;
    ELSE
        DELETE FROM SanPham
        WHERE MaSP = MaSP;
        KQ := 0;
    END IF;
END;

---d. Thủ tục xóa SanPham (có OUT)
CREATE OR REPLACE PROCEDURE sp_NhapHangSX(
    MaHangSX VARCHAR2,
    TenHang VARCHAR2,
    DiaChi VARCHAR2,
    SoDT VARCHAR2,
    Email VARCHAR2,
    KQ OUT NUMBER
)
AS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM HangSX
    WHERE TenHang = sp_NhapHangSX.TenHang;
    IF v_count > 0 THEN
        KQ := 1;
    ELSE
        INSERT INTO HangSX
        VALUES(MaHangSX,TenHang,DiaChi,SoDT,Email);
        KQ := 0;
    END IF;
END;

---e. Thủ tục sp_NhapHangSX (có OUT)
CREATE OR REPLACE PROCEDURE sp_NhapHangSX(
    MaHangSX VARCHAR2,
    TenHang VARCHAR2,
    DiaChi VARCHAR2,
    SoDT VARCHAR2,
    Email VARCHAR2,
    KQ OUT NUMBER
)
AS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM HangSX
    WHERE TenHang = sp_NhapHangSX.TenHang;
    IF v_count > 0 THEN
        KQ := 1;
    ELSE
        INSERT INTO HangSX
        VALUES(MaHangSX,TenHang,DiaChi,SoDT,Email);
        KQ := 0;
    END IF;
END;

---f. Thủ tục nhập bảng Nhap (có OUT)
CREATE OR REPLACE PROCEDURE sp_Nhap(
    p_SoHDN VARCHAR2,
    p_MaSP VARCHAR2,
    p_MaNV VARCHAR2,
    p_NgayNhap DATE,
    p_SoLuongN NUMBER,
    p_DonGiaN NUMBER,
    KQ OUT NUMBER
)
AS
    v_sp NUMBER;
    v_nv NUMBER;
    v_hd NUMBER;
    v_ct NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_sp
    FROM SanPham
    WHERE MaSP = p_MaSP;
    IF v_sp = 0 THEN
        KQ := 1;
        RETURN;
    END IF;
    SELECT COUNT(*) INTO v_nv
    FROM NhanVien
    WHERE MaNV = p_MaNV;
    IF v_nv = 0 THEN
        KQ := 2;
        RETURN;
    END IF;
    SELECT COUNT(*) INTO v_hd
    FROM PNhap
    WHERE SoHDN = p_SoHDN;
    IF v_hd = 0 THEN
        INSERT INTO PNhap
        VALUES(p_SoHDN,p_NgayNhap,p_MaNV);
    END IF;
    SELECT COUNT(*) INTO v_ct
    FROM Nhap
    WHERE SoHDN = p_SoHDN AND MaSP = p_MaSP;
    IF v_ct > 0 THEN
        UPDATE Nhap
        SET SoLuongN = p_SoLuongN,
            DonGiaN = p_DonGiaN
        WHERE SoHDN = p_SoHDN
        AND MaSP = p_MaSP;
    ELSE
        INSERT INTO Nhap
        VALUES(p_SoHDN,p_MaSP,p_SoLuongN,p_DonGiaN);
    END IF;
    KQ := 0;
END;

---g. Thủ tục nhập bảng Xuat (có OUT)
CREATE OR REPLACE PROCEDURE sp_Xuat(
    p_SoHDX VARCHAR2,
    p_MaSP VARCHAR2,
    p_MaNV VARCHAR2,
    p_NgayXuat DATE,
    p_SoLuongX NUMBER,
    KQ OUT NUMBER
)
AS
    v_sp NUMBER;
    v_nv NUMBER;
    v_hd NUMBER;
    v_ct NUMBER;
    v_sl NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_sp
    FROM SanPham
    WHERE MaSP = p_MaSP;
    IF v_sp = 0 THEN
        KQ := 1;
        RETURN;
    END IF;
    SELECT COUNT(*) INTO v_nv
    FROM NhanVien
    WHERE MaNV = p_MaNV;
    IF v_nv = 0 THEN
        KQ := 2;
        RETURN;
    END IF;
    SELECT SoLuong INTO v_sl
    FROM SanPham
    WHERE MaSP = p_MaSP;
    IF p_SoLuongX > v_sl THEN
        KQ := 3;
        RETURN;
    END IF;
    SELECT COUNT(*) INTO v_hd
    FROM PXuat
    WHERE SoHDX = p_SoHDX;
    IF v_hd = 0 THEN
        INSERT INTO PXuat
        VALUES(p_SoHDX,p_NgayXuat,p_MaNV);
    END IF;
    SELECT COUNT(*) INTO v_ct
    FROM Xuat
    WHERE SoHDX = p_SoHDX AND MaSP = p_MaSP;
    IF v_ct > 0 THEN
        UPDATE Xuat
        SET SoLuongX = p_SoLuongX
        WHERE SoHDX = p_SoHDX
        AND MaSP = p_MaSP;
    ELSE
        INSERT INTO Xuat
        VALUES(p_SoHDX,p_MaSP,p_SoLuongX);
    END IF;
    UPDATE SanPham
    SET SoLuong = SoLuong - p_SoLuongX
    WHERE MaSP = p_MaSP;
    KQ := 0;
END;

