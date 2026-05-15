-- TRAN THI THANH THAO - 1250080179
-- BAI 10 - TRIGGER NANG CAO - ORACLE PL/SQL
-- PHIEU BAI TAP 3 - CSDL QL_KHACHSAN

SET SERVEROUTPUT ON;

PROMPT ===== TAO BANG VA DU LIEU MAU - QL_KHACHSAN =====

BEGIN EXECUTE IMMEDIATE 'DROP VIEW vw_PhongTrong'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW vw_HoaDon_Active'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE ChiPhiPhuThu CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE LichSuPhong CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE HoaDon CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE KhachHang CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE Phong CASCADE CONSTRAINTS'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP SEQUENCE SEQ_HD'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

-----Tạo bảng Phong
CREATE TABLE Phong (
    MaPhong        VARCHAR2(10) CONSTRAINT pk_phong PRIMARY KEY,
    LoaiPhong      VARCHAR2(50) NOT NULL,
    TrangThai      VARCHAR2(20) NOT NULL,
    GiaTheoGio     NUMBER(15,2) NOT NULL,
    GiaTheoNgay    NUMBER(15,2) NOT NULL,
    SoNguoiToiDa   NUMBER(3) NOT NULL,
    CONSTRAINT ck_phong_trangthai CHECK (TrangThai IN ('TRONG', 'DA_THUE', 'BAO_TRI'))
);
/

-----Tạo bảng KhachHang
CREATE TABLE KhachHang (
    MaKH       VARCHAR2(10) CONSTRAINT pk_khachhang PRIMARY KEY,
    HoTen      VARCHAR2(100) NOT NULL,
    CCCD       VARCHAR2(20) NOT NULL,
    SoDT       VARCHAR2(15),
    Email      VARCHAR2(100),
    QuocTich   VARCHAR2(50)
);
/

-----Tạo bảng HoaDon
CREATE TABLE HoaDon (
    MaHD       VARCHAR2(10) CONSTRAINT pk_hoadon PRIMARY KEY,
    MaKH       VARCHAR2(10) NOT NULL,
    MaPhong    VARCHAR2(10) NOT NULL,
    NgayNhan   DATE NOT NULL,
    NgayTra    DATE NOT NULL,
    SoNguoi    NUMBER(3) NOT NULL,
    TongTien   NUMBER(15,2),
    TrangThai  VARCHAR2(20) NOT NULL,
    CONSTRAINT fk_hd_kh FOREIGN KEY (MaKH) REFERENCES KhachHang(MaKH),
    CONSTRAINT fk_hd_phong FOREIGN KEY (MaPhong) REFERENCES Phong(MaPhong),
    CONSTRAINT ck_hd_trangthai CHECK (TrangThai IN ('CHO_NHAN', 'DANG_O', 'DA_TRA', 'HUY'))
);
/

-----Tạo bảng ChiPhiPhuThu
CREATE TABLE ChiPhiPhuThu (
    MaCP       VARCHAR2(10) CONSTRAINT pk_chiphiphuthu PRIMARY KEY,
    MaHD       VARCHAR2(10) NOT NULL,
    MoTa       VARCHAR2(200),
    SoTien     NUMBER(15,2) NOT NULL,
    ThoiGian   DATE DEFAULT SYSDATE,
    CONSTRAINT fk_cp_hd FOREIGN KEY (MaHD) REFERENCES HoaDon(MaHD)
);
/

-----Tạo bảng LichSuPhong
CREATE TABLE LichSuPhong (
    MaLS       VARCHAR2(10) CONSTRAINT pk_lichsuphong PRIMARY KEY,
    MaPhong    VARCHAR2(10) NOT NULL,
    MaHD       VARCHAR2(10) NOT NULL,
    NgayNhan   DATE,
    NgayTra    DATE,
    GhiChu     VARCHAR2(200),
    CONSTRAINT fk_ls_phong FOREIGN KEY (MaPhong) REFERENCES Phong(MaPhong),
    CONSTRAINT fk_ls_hd FOREIGN KEY (MaHD) REFERENCES HoaDon(MaHD)
);
/

-----Insert 5 dữ liệu bảng Phong
INSERT INTO Phong VALUES ('P101', 'Don', 'TRONG', 80000, 450000, 2);
INSERT INTO Phong VALUES ('P102', 'Doi', 'TRONG', 120000, 650000, 4);
INSERT INTO Phong VALUES ('P103', 'VIP', 'TRONG', 200000, 1200000, 4);
INSERT INTO Phong VALUES ('P104', 'Gia dinh', 'BAO_TRI', 150000, 900000, 5);
INSERT INTO Phong VALUES ('P105', 'Don', 'TRONG', 90000, 500000, 2);

-----Insert 5 dữ liệu bảng KhachHang
INSERT INTO KhachHang VALUES ('KH01', 'Nguyen Thi Lan', '079123456789', '0902000001', 'lan@gmail.com', 'Viet Nam');
INSERT INTO KhachHang VALUES ('KH02', 'Tran Van Minh', '079123456780', '0902000002', 'minh@gmail.com', 'Viet Nam');
INSERT INTO KhachHang VALUES ('KH03', 'Le Hoang Nam', '079123456781', '0902000003', 'nam@gmail.com', 'Thai Lan');
INSERT INTO KhachHang VALUES ('KH04', 'Pham Thu Ha', '079123456782', '0902000004', 'ha@gmail.com', 'Han Quoc');
INSERT INTO KhachHang VALUES ('KH05', 'Do Quoc Bao', '079123456783', '0902000005', 'bao@gmail.com', 'Nhat Ban');

-----Insert 5 dữ liệu bảng HoaDon
INSERT INTO HoaDon VALUES ('HD0001', 'KH01', 'P101', DATE '2026-03-23', DATE '2026-03-24', 2, 450000, 'CHO_NHAN');
INSERT INTO HoaDon VALUES ('HD0002', 'KH02', 'P102', DATE '2026-03-23', DATE '2026-03-25', 3, 1300000, 'DANG_O');
INSERT INTO HoaDon VALUES ('HD0003', 'KH03', 'P103', DATE '2026-03-20', DATE '2026-03-22', 2, 2400000, 'DA_TRA');
INSERT INTO HoaDon VALUES ('HD0004', 'KH04', 'P105', DATE '2026-03-24', DATE '2026-03-26', 2, 1000000, 'HUY');
INSERT INTO HoaDon VALUES ('HD0005', 'KH05', 'P101', DATE '2026-03-27', DATE '2026-03-28', 1, 450000, 'CHO_NHAN');

-----Cập nhật trạng thái phòng tương ứng dữ liệu mẫu HoaDon
UPDATE Phong SET TrangThai = 'DA_THUE' WHERE MaPhong IN ('P101', 'P102');

-----Insert 5 dữ liệu bảng ChiPhiPhuThu
INSERT INTO ChiPhiPhuThu VALUES ('CP001', 'HD0001', 'Nuoc uong', 50000, DATE '2026-03-23');
INSERT INTO ChiPhiPhuThu VALUES ('CP002', 'HD0002', 'Giat ui', 70000, DATE '2026-03-24');
INSERT INTO ChiPhiPhuThu VALUES ('CP003', 'HD0002', 'An sang', 120000, DATE '2026-03-24');
INSERT INTO ChiPhiPhuThu VALUES ('CP004', 'HD0003', 'Hu hong vat dung', 300000, DATE '2026-03-21');
INSERT INTO ChiPhiPhuThu VALUES ('CP005', 'HD0004', 'Dat coc huy phong', 100000, DATE '2026-03-24');

-----Insert 5 dữ liệu bảng LichSuPhong
INSERT INTO LichSuPhong VALUES ('LS0001', 'P103', 'HD0003', DATE '2026-03-20', DATE '2026-03-22', 'Da tra phong dung han');
INSERT INTO LichSuPhong VALUES ('LS0002', 'P102', 'HD0002', DATE '2026-03-23', DATE '2026-03-25', 'Dang luu tru');
INSERT INTO LichSuPhong VALUES ('LS0003', 'P101', 'HD0001', DATE '2026-03-23', DATE '2026-03-24', 'Cho nhan phong');
INSERT INTO LichSuPhong VALUES ('LS0004', 'P105', 'HD0004', DATE '2026-03-24', DATE '2026-03-26', 'Hoa don huy');
INSERT INTO LichSuPhong VALUES ('LS0005', 'P101', 'HD0005', DATE '2026-03-27', DATE '2026-03-28', 'Dat truoc');

COMMIT;

PROMPT ===== PHIEU BAI TAP 3 =====

-----a. Trigger INSERT bảng HOADON – trg_DatPhong
CREATE OR REPLACE TRIGGER trg_DatPhong
BEFORE INSERT ON HoaDon
FOR EACH ROW
DECLARE
    v_dem_kh        NUMBER := 0;
    v_dem_phong     NUMBER := 0;
    v_trang_thai    Phong.TrangThai%TYPE;
    v_gia_theo_ngay Phong.GiaTheoNgay%TYPE;
    v_so_nguoi_max  Phong.SoNguoiToiDa%TYPE;
    v_so_ngay       NUMBER := 0;
BEGIN
    SELECT COUNT(*)
      INTO v_dem_kh
      FROM KhachHang
     WHERE MaKH = :NEW.MaKH;

    IF v_dem_kh = 0 THEN
        RAISE_APPLICATION_ERROR(-20101, 'MaKH khong ton tai trong bang KhachHang');
    END IF;

    SELECT COUNT(*)
      INTO v_dem_phong
      FROM Phong
     WHERE MaPhong = :NEW.MaPhong;

    IF v_dem_phong = 0 THEN
        RAISE_APPLICATION_ERROR(-20102, 'MaPhong khong ton tai trong bang Phong');
    END IF;

    SELECT TrangThai, GiaTheoNgay, SoNguoiToiDa
      INTO v_trang_thai, v_gia_theo_ngay, v_so_nguoi_max
      FROM Phong
     WHERE MaPhong = :NEW.MaPhong
       FOR UPDATE;

    IF v_trang_thai <> 'TRONG' THEN
        RAISE_APPLICATION_ERROR(-20103, 'Phong hien tai khong o trang thai TRONG');
    END IF;

    IF NVL(:NEW.SoNguoi, 0) <= 0 OR :NEW.SoNguoi > v_so_nguoi_max THEN
        RAISE_APPLICATION_ERROR(-20104, 'SoNguoi khong hop le hoac vuot qua SoNguoiToiDa');
    END IF;

    IF :NEW.NgayNhan IS NULL OR :NEW.NgayTra IS NULL THEN
        RAISE_APPLICATION_ERROR(-20105, 'NgayNhan va NgayTra khong duoc de trong');
    END IF;

    IF :NEW.NgayNhan < TRUNC(SYSDATE) OR :NEW.NgayNhan >= :NEW.NgayTra THEN
        RAISE_APPLICATION_ERROR(-20106, 'NgayNhan phai >= ngay hien tai va nho hon NgayTra');
    END IF;

    v_so_ngay := :NEW.NgayTra - :NEW.NgayNhan;
    :NEW.TongTien := v_so_ngay * v_gia_theo_ngay;

    IF :NEW.TrangThai IS NULL THEN
        :NEW.TrangThai := 'CHO_NHAN';
    END IF;

    UPDATE Phong
       SET TrangThai = 'DA_THUE'
     WHERE MaPhong = :NEW.MaPhong;
END trg_DatPhong;
/

-----b. Trigger UPDATE TrangThai HOADON – trg_CapNhatTrangThaiHD
CREATE OR REPLACE TRIGGER trg_CapNhatTrangThaiHD
BEFORE UPDATE OF TrangThai ON HoaDon
FOR EACH ROW
DECLARE
    v_ma_ls VARCHAR2(20);
BEGIN
    IF :OLD.TrangThai = 'CHO_NHAN' THEN
        IF :NEW.TrangThai NOT IN ('DANG_O', 'HUY') THEN
            RAISE_APPLICATION_ERROR(-20111, 'CHO_NHAN chi duoc chuyen sang DANG_O hoac HUY');
        END IF;
    ELSIF :OLD.TrangThai = 'DANG_O' THEN
        IF :NEW.TrangThai <> 'DA_TRA' THEN
            RAISE_APPLICATION_ERROR(-20112, 'DANG_O chi duoc chuyen sang DA_TRA');
        END IF;
    ELSIF :OLD.TrangThai IN ('DA_TRA', 'HUY') THEN
        RAISE_APPLICATION_ERROR(-20113, 'DA_TRA va HUY khong the thay doi');
    ELSE
        RAISE_APPLICATION_ERROR(-20114, 'Trang thai cu khong hop le');
    END IF;

    IF :NEW.TrangThai = 'DA_TRA' THEN
        UPDATE Phong
           SET TrangThai = 'TRONG'
         WHERE MaPhong = :NEW.MaPhong;

        SELECT 'LS' || TO_CHAR(NVL(MAX(TO_NUMBER(SUBSTR(MaLS, 3))), 0) + 1, 'FM0000')
          INTO v_ma_ls
          FROM LichSuPhong
         WHERE REGEXP_LIKE(MaLS, '^LS[0-9]+$');

        INSERT INTO LichSuPhong (MaLS, MaPhong, MaHD, NgayNhan, NgayTra, GhiChu)
        VALUES (
            v_ma_ls,
            :NEW.MaPhong,
            :NEW.MaHD,
            :NEW.NgayNhan,
            :NEW.NgayTra,
            'Khach da tra phong'
        );
    ELSIF :NEW.TrangThai = 'HUY' THEN
        UPDATE Phong
           SET TrangThai = 'TRONG'
         WHERE MaPhong = :NEW.MaPhong;
    END IF;
END trg_CapNhatTrangThaiHD;
/

-----b. View thực hành thêm – vw_HoaDon_Active
CREATE OR REPLACE VIEW vw_HoaDon_Active AS
SELECT MaHD,
       MaKH,
       MaPhong,
       NgayNhan,
       NgayTra,
       SoNguoi,
       TongTien,
       TrangThai
  FROM HoaDon
 WHERE TrangThai IN ('CHO_NHAN', 'DANG_O');
/

-----b. INSTEAD OF Trigger trên view vw_HoaDon_Active – trg_vw_HoaDon_Active_upd
CREATE OR REPLACE TRIGGER trg_vw_HoaDon_Active_upd
INSTEAD OF UPDATE OF TrangThai ON vw_HoaDon_Active
FOR EACH ROW
BEGIN
    UPDATE HoaDon
       SET TrangThai = :NEW.TrangThai
     WHERE MaHD = :OLD.MaHD;
END trg_vw_HoaDon_Active_upd;
/

-----c. Compound Trigger UPDATE ChiPhiPhuThu – trg_SuaChiPhi
CREATE OR REPLACE TRIGGER trg_SuaChiPhi
FOR INSERT OR UPDATE ON ChiPhiPhuThu
COMPOUND TRIGGER
    TYPE t_mahd_tab IS TABLE OF HoaDon.MaHD%TYPE INDEX BY PLS_INTEGER;
    g_mahd_list t_mahd_tab;
    g_row_count NUMBER := 0;

    BEFORE STATEMENT IS
    BEGIN
        g_row_count := 0;
        g_mahd_list.DELETE;
    END BEFORE STATEMENT;

    BEFORE EACH ROW IS
    BEGIN
        g_row_count := g_row_count + 1;

        IF g_row_count > 5 THEN
            RAISE_APPLICATION_ERROR(-20121, 'Chi duoc INSERT/UPDATE toi da 5 chi phi trong 1 lenh');
        END IF;

        IF NVL(:NEW.SoTien, 0) <= 0 OR :NEW.SoTien >= 50000000 THEN
            RAISE_APPLICATION_ERROR(-20122, 'SoTien phai > 0 va < 50,000,000');
        END IF;

        IF g_mahd_list.COUNT = 0 THEN
            g_mahd_list(1) := :NEW.MaHD;
        ELSE
            FOR i IN 1 .. g_mahd_list.COUNT LOOP
                IF g_mahd_list(i) = :NEW.MaHD THEN
                    GOTO bo_qua_mahd_moi;
                END IF;
            END LOOP;
            g_mahd_list(g_mahd_list.COUNT + 1) := :NEW.MaHD;
        END IF;
        <<bo_qua_mahd_moi>>
        NULL;

        IF UPDATING AND :OLD.MaHD <> :NEW.MaHD THEN
            IF g_mahd_list.COUNT = 0 THEN
                g_mahd_list(1) := :OLD.MaHD;
            ELSE
                FOR i IN 1 .. g_mahd_list.COUNT LOOP
                    IF g_mahd_list(i) = :OLD.MaHD THEN
                        GOTO bo_qua_mahd_cu;
                    END IF;
                END LOOP;
                g_mahd_list(g_mahd_list.COUNT + 1) := :OLD.MaHD;
            END IF;
            <<bo_qua_mahd_cu>>
            NULL;
        END IF;
    END BEFORE EACH ROW;

    AFTER STATEMENT IS
        v_tien_phong NUMBER := 0;
        v_phu_thu    NUMBER := 0;
    BEGIN
        FOR i IN 1 .. g_mahd_list.COUNT LOOP
            SELECT (hd.NgayTra - hd.NgayNhan) * p.GiaTheoNgay,
                   NVL((SELECT SUM(cp.SoTien)
                          FROM ChiPhiPhuThu cp
                         WHERE cp.MaHD = hd.MaHD), 0)
              INTO v_tien_phong, v_phu_thu
              FROM HoaDon hd
              JOIN Phong p ON p.MaPhong = hd.MaPhong
             WHERE hd.MaHD = g_mahd_list(i);

            UPDATE HoaDon
               SET TongTien = v_tien_phong + v_phu_thu
             WHERE MaHD = g_mahd_list(i);
        END LOOP;
    END AFTER STATEMENT;
END trg_SuaChiPhi;
/

-----d. View phòng trống – vw_PhongTrong
CREATE OR REPLACE VIEW vw_PhongTrong AS
SELECT MaPhong,
       LoaiPhong,
       TrangThai,
       GiaTheoGio,
       GiaTheoNgay,
       SoNguoiToiDa
  FROM Phong
 WHERE TrangThai = 'TRONG';
/

-----d. Sequence tạo mã hóa đơn – SEQ_HD
CREATE SEQUENCE SEQ_HD
    START WITH 1
    INCREMENT BY 1
    NOCACHE;
/

-----d. INSTEAD OF Trigger trên View – trg_vwPhongTrong_ins
CREATE OR REPLACE TRIGGER trg_vwPhongTrong_ins
INSTEAD OF INSERT ON vw_PhongTrong
FOR EACH ROW
DECLARE
    v_ma_kh KhachHang.MaKH%TYPE;
    v_ma_hd HoaDon.MaHD%TYPE;
BEGIN
    SELECT MaKH
      INTO v_ma_kh
      FROM KhachHang
     WHERE ROWNUM = 1;

    v_ma_hd := 'HD' || TO_CHAR(SEQ_HD.NEXTVAL, 'FM0000');

    INSERT INTO HoaDon (
        MaHD, MaKH, MaPhong, NgayNhan, NgayTra, SoNguoi, TongTien, TrangThai
    )
    VALUES (
        v_ma_hd, v_ma_kh, :NEW.MaPhong, TRUNC(SYSDATE), TRUNC(SYSDATE) + 1, 1, 0, 'CHO_NHAN'
    );
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20131, 'Khong tim thay KhachHang de tao dat phong qua view');
END trg_vwPhongTrong_ins;
/
