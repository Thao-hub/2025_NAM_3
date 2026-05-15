CREATE TABLE Mathang (
    Mahang   VARCHAR2(5)   CONSTRAINT pk_mathang PRIMARY KEY,
    Tenhang  VARCHAR2(50)  NOT NULL,
    Soluong  NUMBER(10)
);

CREATE TABLE Nhatkybanhang (
    Stt      NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Ngay     DATE,
    Nguoimua VARCHAR2(50),
    Mahang   VARCHAR2(5) REFERENCES Mathang(Mahang),
    Soluong  NUMBER(10),
    Giaban   NUMBER(15,2)
);

INSERT INTO Mathang VALUES ('1', 'Hang A', 100);
INSERT INTO Mathang VALUES ('2', 'Hang B', 200);
INSERT INTO Mathang VALUES ('3', 'Hang C', 150);
COMMIT;

--a. Trigger trg_nhatkybanhang_insert
CREATE OR REPLACE TRIGGER trg_nhatkybanhang_insert
AFTER INSERT ON Nhatkybanhang
FOR EACH ROW
BEGIN
    UPDATE Mathang
    SET Soluong = Soluong - :NEW.Soluong
    WHERE Mahang = :NEW.Mahang;
END trg_nhatkybanhang_insert;
--kiem tra
INSERT INTO Nhatkybanhang (Ngay, Nguoimua, Mahang, Soluong, Giaban)
VALUES (SYSDATE, 'Nguyen Van A', '1', 10, 15000);
SELECT * FROM Nhatkybanhang;

--b. Trigger trg_nhatkybanhang_update_soluong
CREATE OR REPLACE TRIGGER trg_nhatkybanhang_update_soluong
AFTER UPDATE OF Soluong ON Nhatkybanhang
FOR EACH ROW
BEGIN
    UPDATE Mathang
    SET Soluong = Soluong - (:NEW.Soluong - :OLD.Soluong)
    WHERE Mahang = :NEW.Mahang;
END trg_nhatkybanhang_update_soluong;
--kiem tra
UPDATE Nhatkybanhang SET Soluong = 15 WHERE Stt = 1;
SELECT * FROM Nhatkybanhang WHERE Stt = 1;

--c. Trigger INSERT có kiểm tra số lượng hợp lệ
CREATE OR REPLACE TRIGGER trg_nkbh_before_insert_check
BEFORE INSERT ON Nhatkybanhang
FOR EACH ROW
DECLARE
    v_tonkho NUMBER := 0;
BEGIN
    SELECT Soluong INTO v_tonkho
    FROM Mathang
    WHERE Mahang = :NEW.Mahang
    FOR UPDATE;
    IF :NEW.Soluong > v_tonkho THEN
        RAISE_APPLICATION_ERROR(-20011, 'So luong ban vuot qua ton kho');
    END IF;
    UPDATE Mathang
    SET Soluong = Soluong - :NEW.Soluong
    WHERE Mahang = :NEW.Mahang;
END trg_nkbh_before_insert_check;

-- Chuyen sang test c tat trigger a de tranh tru ton 2 lan
ALTER TRIGGER trg_nhatkybanhang_insert DISABLE;
ALTER TRIGGER trg_nhatkybanhang_insert ENABLE;
--Kiem tra
INSERT INTO Nhatkybanhang (Ngay, Nguoimua, Mahang, Soluong, Giaban)
VALUES (SYSDATE, 'Le Thi B', '2', 5, 22000);
SELECT * FROM Nhatkybanhang

--d. Trigger UPDATE kiểm soát số dòng (Compound Trigger)
CREATE OR REPLACE PACKAGE pkg_nkbh_state AS
    g_row_count NUMBER := 0;
END pkg_nkbh_state;
/
CREATE OR REPLACE TRIGGER trg_nkbh_update_compound
FOR UPDATE ON Nhatkybanhang
COMPOUND TRIGGER
    BEFORE STATEMENT IS
    BEGIN
        pkg_nkbh_state.g_row_count := 0;
    END BEFORE STATEMENT;
    BEFORE EACH ROW IS
    BEGIN
        pkg_nkbh_state.g_row_count := pkg_nkbh_state.g_row_count + 1;
        IF pkg_nkbh_state.g_row_count > 1 THEN
            RAISE_APPLICATION_ERROR(-20021, 'Chi duoc UPDATE 1 dong');
        END IF;
    END BEFORE EACH ROW;
    AFTER EACH ROW IS
    BEGIN
        UPDATE Mathang
        SET Soluong = Soluong - (:NEW.Soluong - :OLD.Soluong)
        WHERE Mahang = :NEW.Mahang;
    END AFTER EACH ROW;
END trg_nkbh_update_compound;
/
---kiem tra
--UPDATE 1 dong
UPDATE Nhatkybanhang SET Soluong = Soluong + 1 WHERE Stt = 1;
SELECT * FROM Nhatkybanhang WHERE Stt = 1;
--UPDATE nhieu dong
UPDATE Nhatkybanhang SET Soluong = Soluong + 1;
SELECT * FROM Nhatkybanhang ORDER BY Stt;

--e. Trigger DELETE kiểm soát số dòng
CREATE OR REPLACE TRIGGER trg_nkbh_delete_compound
FOR DELETE ON Nhatkybanhang
COMPOUND TRIGGER
    BEFORE STATEMENT IS
    BEGIN
        pkg_nkbh_state.g_row_count := 0;
    END BEFORE STATEMENT;
    BEFORE EACH ROW IS
    BEGIN
        pkg_nkbh_state.g_row_count := pkg_nkbh_state.g_row_count + 1;
        IF pkg_nkbh_state.g_row_count > 1 THEN
            RAISE_APPLICATION_ERROR(-20031, 'Chi duoc DELETE 1 dong');
        END IF;
    END BEFORE EACH ROW;
    AFTER EACH ROW IS
    BEGIN
        UPDATE Mathang
        SET Soluong = Soluong + :OLD.Soluong
        WHERE Mahang = :OLD.Mahang;
    END AFTER EACH ROW;
END trg_nkbh_delete_compound;
--kiem tra
--DELETE 1 dong
DELETE FROM Nhatkybanhang WHERE Stt = 1;
SELECT * FROM Nhatkybanhang ORDER BY Stt;

--f. Trigger UPDATE nâng cao – Kiểm tra nhiều điều kiện
CREATE OR REPLACE TRIGGER trg_nkbh_update_nangcao
FOR UPDATE OF Soluong ON Nhatkybanhang
COMPOUND TRIGGER
    v_row_count NUMBER := 0;
    v_tonkho    NUMBER := 0;
    BEFORE STATEMENT IS
    BEGIN
        v_row_count := 0;
    END BEFORE STATEMENT;
    BEFORE EACH ROW IS
    BEGIN
        v_row_count := v_row_count + 1;
        IF v_row_count > 1 THEN
            RAISE_APPLICATION_ERROR(-20041, 'UPDATE qua 1 ban ghi, khong hop le');
        END IF;
        SELECT Soluong INTO v_tonkho
        FROM Mathang
        WHERE Mahang = :NEW.Mahang
        FOR UPDATE;
        IF :NEW.Soluong < v_tonkho THEN
            RAISE_APPLICATION_ERROR(-20042, 'So luong cap nhat < ton kho, sai cap nhat theo yeu cau de');
        ELSIF :NEW.Soluong = v_tonkho THEN
            RAISE_APPLICATION_ERROR(-20043, 'So luong bang ton kho, khong can cap nhat');
        END IF;
    END BEFORE EACH ROW;
    AFTER EACH ROW IS
    BEGIN
        UPDATE Mathang
        SET Soluong = Soluong - (:NEW.Soluong - :OLD.Soluong)
        WHERE Mahang = :NEW.Mahang;
    END AFTER EACH ROW;
END trg_nkbh_update_nangcao;
--kiem tra
UPDATE NhatkybanhangSET Soluong = 500 WHERE Stt = 2;
SELECT * FROM NhatkybanhangSET WHERE Stt = 2;
--g. Thủ tục xóa MATHANG (có tác động 2 bảng)
CREATE OR REPLACE PROCEDURE sp_xoa_mathang (
    p_mahang IN VARCHAR2
) AS
    v_dem NUMBER := 0;
BEGIN
    SELECT COUNT(*) INTO v_dem
    FROM Mathang
    WHERE Mahang = p_mahang;

    IF v_dem = 0 THEN
        DBMS_OUTPUT.PUT_LINE('Mahang khong ton tai: ' || p_mahang);
        RETURN;
    END IF;

    DELETE FROM Nhatkybanhang
    WHERE Mahang = p_mahang;

    DELETE FROM Mathang
    WHERE Mahang = p_mahang;

    DBMS_OUTPUT.PUT_LINE('Da xoa Mahang: ' || p_mahang);
END sp_xoa_mathang;
--kiem tra
BEGIN
    sp_xoa_mathang('3');
END;
SELECT * FROM Mathang;
--h. Hàm tính tổng tiền theo tên hàng
CREATE OR REPLACE FUNCTION fn_tongtien_theo_tenhang (
    p_tenhang IN VARCHAR2
) RETURN NUMBER AS
    v_tong NUMBER := 0;
BEGIN
    SELECT SUM(nk.Soluong * nk.Giaban)
    INTO v_tong
    FROM Nhatkybanhang nk
    JOIN Mathang mh ON nk.Mahang = mh.Mahang
    WHERE mh.Tenhang = p_tenhang;

    RETURN NVL(v_tong, 0);
END fn_tongtien_theo_tenhang;

--kiem tra
SELECT fn_tongtien_theo_tenhang('Hang B') AS TongTien FROM DUAL;
COMMIT;

