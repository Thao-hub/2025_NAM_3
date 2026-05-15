---phieu bai tap 1
--tao bang
CREATE TABLE KHOA (
    Makhoa     VARCHAR2(10) PRIMARY KEY,
    Tenkhoa    VARCHAR2(100) UNIQUE,
    Dienthoai  VARCHAR2(15)
);
CREATE TABLE LOP (
    Malop        VARCHAR2(10) PRIMARY KEY,
    Tenlop       VARCHAR2(100) UNIQUE,
    Khoa         VARCHAR2(50),
    Hedt         VARCHAR2(20),
    Namnhaphoc   NUMBER(4),
    Makhoa       VARCHAR2(10),
    CONSTRAINT fk_lop_khoa 
        FOREIGN KEY (Makhoa)
        REFERENCES KHOA(Makhoa)
);
COMMIT;
--thu tuc them khoa
CREATE OR REPLACE PROCEDURE sp_them_khoa (
    p_makhoa    IN VARCHAR2,
    p_tenkhoa   IN VARCHAR2,
    p_dienthoai IN VARCHAR2
) AS
    v_dem NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_dem
    FROM KHOA
    WHERE Tenkhoa = p_tenkhoa;

    IF v_dem > 0 THEN
        DBMS_OUTPUT.PUT_LINE('Ten khoa da ton tai');
    ELSE
        INSERT INTO KHOA VALUES (p_makhoa, p_tenkhoa, p_dienthoai);
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Them khoa thanh cong');
    END IF;
END sp_them_khoa;
--kiem tra
SET SERVEROUTPUT ON;
BEGIN
    sp_them_khoa('CNTT', 'Cong nghe thong tin', '0123456789');
END;
BEGIN
    sp_them_khoa('CNTT2', 'Cong nghe thong tin', '0999999999');
END;
--cau 2
CREATE OR REPLACE PROCEDURE sp_them_lop (
    p_malop       IN VARCHAR2,
    p_tenlop      IN VARCHAR2,
    p_khoa        IN VARCHAR2,
    p_hedt        IN VARCHAR2,
    p_namnhaphoc  IN NUMBER,
    p_makhoa      IN VARCHAR2
) AS
    v_demlop NUMBER := 0;
    v_demkhoa NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_demlop
    FROM LOP
    WHERE Tenlop = p_tenlop;

    IF v_demlop > 0 THEN
        DBMS_OUTPUT.PUT_LINE('Ten lop da ton tai');
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_demkhoa
    FROM KHOA
    WHERE Makhoa = p_makhoa;

    IF v_demkhoa = 0 THEN
        DBMS_OUTPUT.PUT_LINE('Ma khoa khong ton tai');
        RETURN;
    END IF;

    INSERT INTO LOP VALUES 
    (p_malop, p_tenlop, p_khoa, p_hedt, p_namnhaphoc, p_makhoa);

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Them lop thanh cong');
END sp_them_lop;
--cau 3
CREATE OR REPLACE PROCEDURE sp_them_khoa2 (
    p_makhoa    IN VARCHAR2,
    p_tenkhoa   IN VARCHAR2,
    p_dienthoai IN VARCHAR2,
    p_kq        OUT NUMBER
) AS
    v_dem NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_dem
    FROM KHOA
    WHERE Tenkhoa = p_tenkhoa;

    IF v_dem > 0 THEN
        p_kq := 0;
    ELSE
        INSERT INTO KHOA VALUES (p_makhoa, p_tenkhoa, p_dienthoai);
        COMMIT;
        p_kq := 1;
    END IF;
END sp_them_khoa2;
--cau 4
CREATE OR REPLACE PROCEDURE sp_them_lop2 (
    p_malop       IN VARCHAR2,
    p_tenlop      IN VARCHAR2,
    p_khoa        IN VARCHAR2,
    p_hedt        IN VARCHAR2,
    p_namnhaphoc  IN NUMBER,
    p_makhoa      IN VARCHAR2,
    p_kq          OUT NUMBER
) AS
    v_demlop NUMBER := 0;
    v_demkhoa NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_demlop
    FROM LOP
    WHERE Tenlop = p_tenlop;

    IF v_demlop > 0 THEN
        p_kq := 0;
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_demkhoa
    FROM KHOA
    WHERE Makhoa = p_makhoa;

    IF v_demkhoa = 0 THEN
        p_kq := 1;
        RETURN;
    END IF;

    INSERT INTO LOP VALUES
    (p_malop, p_tenlop, p_khoa, p_hedt, p_namnhaphoc, p_makhoa);

    COMMIT;
    p_kq := 2;
END sp_them_lop2;

---bai tap 2
--tao bang
CREATE TABLE tblChucVu (
    MaCV VARCHAR2(10) PRIMARY KEY,
    TenCV VARCHAR2(50)
);

CREATE TABLE tblNhanVien (
    MaNV VARCHAR2(10) PRIMARY KEY,
    MaCV VARCHAR2(10),
    TenNV VARCHAR2(50),
    NgaySinh DATE,
    LuongCanBan NUMBER(10,2),
    NgayCong NUMBER,
    PhuCap NUMBER(10,2),
    CONSTRAINT fk_cv FOREIGN KEY (MaCV)
        REFERENCES tblChucVu(MaCV)
);
--Cau C tao du lieu mau
INSERT INTO tblChucVu VALUES ('CV01','Giam doc');
INSERT INTO tblChucVu VALUES ('CV02','Pho giam doc');
INSERT INTO tblChucVu VALUES ('CV03','Truong phong');
INSERT INTO tblChucVu VALUES ('CV04','Nhan vien');

INSERT INTO tblNhanVien VALUES
('NV01','CV04','Nguyen Van A',
TO_DATE('01/01/1995','DD/MM/YYYY'),
5000000,26,500000);

INSERT INTO tblNhanVien VALUES
('NV02','CV03','Tran Thi B',
TO_DATE('02/02/1990','DD/MM/YYYY'),
7000000,25,700000);

INSERT INTO tblNhanVien VALUES
('NV03','CV02','Le Van C',
TO_DATE('03/03/1988','DD/MM/YYYY'),
9000000,24,1000000);

COMMIT;
--Thủ tục SP_Them_Nhan_Vien
CREATE OR REPLACE PROCEDURE SP_Them_Nhan_Vien (
    p_MaNV IN VARCHAR2,
    p_MaCV IN VARCHAR2,
    p_TenNV IN VARCHAR2,
    p_NgaySinh IN DATE,
    p_LuongCB IN NUMBER,
    p_NgayCong IN NUMBER,
    p_PhuCap IN NUMBER
) AS
    v_dem NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_dem
    FROM tblChucVu
    WHERE MaCV = p_MaCV;

    IF v_dem = 0 THEN
        DBMS_OUTPUT.PUT_LINE('MaCV khong ton tai');
    ELSE
        INSERT INTO tblNhanVien
        VALUES (p_MaNV,p_MaCV,p_TenNV,
                p_NgaySinh,p_LuongCB,
                p_NgayCong,p_PhuCap);
        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Them nhan vien thanh cong');
    END IF;
END;
--Thủ tục SP_CapNhat_Nhan_Vien
CREATE OR REPLACE PROCEDURE SP_CapNhat_Nhan_Vien (
    p_MaNV IN VARCHAR2,
    p_MaCV IN VARCHAR2,
    p_TenNV IN VARCHAR2,
    p_NgaySinh IN DATE,
    p_LuongCB IN NUMBER,
    p_NgayCong IN NUMBER,
    p_PhuCap IN NUMBER
) AS
    v_dem NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_dem
    FROM tblChucVu
    WHERE MaCV = p_MaCV;

    IF v_dem = 0 THEN
        DBMS_OUTPUT.PUT_LINE('MaCV khong ton tai');
    ELSE
        UPDATE tblNhanVien
        SET MaCV = p_MaCV,
            TenNV = p_TenNV,
            NgaySinh = p_NgaySinh,
            LuongCanBan = p_LuongCB,
            NgayCong = p_NgayCong,
            PhuCap = p_PhuCap
        WHERE MaNV = p_MaNV;

        COMMIT;
        DBMS_OUTPUT.PUT_LINE('Cap nhat thanh cong');
    END IF;
END;
--SP_LuongLN
CREATE OR REPLACE PROCEDURE SP_LuongLN AS
    v_luong NUMBER;
BEGIN
    FOR rec IN (SELECT TenNV,
                       LuongCanBan*NgayCong+PhuCap AS Luong
                FROM tblNhanVien)
    LOOP
        DBMS_OUTPUT.PUT_LINE('Nhan vien: ' || rec.TenNV ||
                             ' - Luong: ' || rec.Luong);
    END LOOP;
END;

---bai tap 3
--Thủ tục sp_them_nhan_vien1 (có tham số OUT)
CREATE OR REPLACE PROCEDURE sp_them_nhan_vien1 (
    p_MaNV IN VARCHAR2,
    p_MaCV IN VARCHAR2,
    p_TenNV IN VARCHAR2,
    p_NgaySinh IN DATE,
    p_LuongCB IN NUMBER,
    p_NgayCong IN NUMBER,
    p_PhuCap IN NUMBER,
    p_kq OUT NUMBER
) AS
    v_dem NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_dem
    FROM tblChucVu
    WHERE MaCV = p_MaCV;

    IF v_dem = 0 THEN
        p_kq := 0;
    ELSE
        INSERT INTO tblNhanVien
        VALUES (p_MaNV,p_MaCV,p_TenNV,
                p_NgaySinh,p_LuongCB,
                p_NgayCong,p_PhuCap);
        COMMIT;
        p_kq := 2;
    END IF;
END;
--Sửa thủ tục – kiểm tra thêm MaNV trùng lặp
CREATE OR REPLACE PROCEDURE sp_them_nhan_vien2 (
    p_MaNV IN VARCHAR2,
    p_MaCV IN VARCHAR2,
    p_TenNV IN VARCHAR2,
    p_NgaySinh IN DATE,
    p_LuongCB IN NUMBER,
    p_NgayCong IN NUMBER,
    p_PhuCap IN NUMBER,
    p_kq OUT NUMBER
) AS
    v_demNV NUMBER := 0;
    v_demCV NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_demNV
    FROM tblNhanVien
    WHERE MaNV = p_MaNV;

    IF v_demNV > 0 THEN
        p_kq := 0;
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_demCV
    FROM tblChucVu
    WHERE MaCV = p_MaCV;

    IF v_demCV = 0 THEN
        p_kq := 1;
        RETURN;
    END IF;

    INSERT INTO tblNhanVien
    VALUES (p_MaNV,p_MaCV,p_TenNV,
            p_NgaySinh,p_LuongCB,
            p_NgayCong,p_PhuCap);

    COMMIT;
    p_kq := 2;
END;
--Thủ tục cập nhật NgaySinh cho nhân viên
CREATE OR REPLACE PROCEDURE sp_capnhat_ngaysinh (
    p_MaNV IN VARCHAR2,
    p_NgaySinh IN DATE,
    p_kq OUT NUMBER
) AS
BEGIN
    UPDATE tblNhanVien
    SET NgaySinh = p_NgaySinh
    WHERE MaNV = p_MaNV;

    IF SQL%ROWCOUNT = 0 THEN
        p_kq := 0;
    ELSE
        COMMIT;
        p_kq := 1;
    END IF;
END;
