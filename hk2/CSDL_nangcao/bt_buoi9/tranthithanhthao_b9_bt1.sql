CREATE TABLE Hang (
    Mahang   VARCHAR2(10) CONSTRAINT pk_hang PRIMARY KEY,
    Tenhang  VARCHAR2(100) NOT NULL,
    Soluong  NUMBER(10)    NOT NULL,
    Giaban   NUMBER(15,2)  NOT NULL
);

CREATE TABLE Hoadon (
    Mahd       VARCHAR2(10) CONSTRAINT pk_hoadon PRIMARY KEY,
    Mahang     VARCHAR2(10) NOT NULL,
    Soluongban NUMBER(10)   NOT NULL,
    Ngayban    DATE,
    CONSTRAINT fk_hoadon_hang FOREIGN KEY (Mahang) REFERENCES Hang(Mahang)
);

INSERT INTO Hang (Mahang, Tenhang, Soluong, Giaban) VALUES ('H01', 'Hang A', 100, 12000);
INSERT INTO Hang (Mahang, Tenhang, Soluong, Giaban) VALUES ('H02', 'Hang B', 50,  25000);
INSERT INTO Hang (Mahang, Tenhang, Soluong, Giaban) VALUES ('H03', 'Hang C', 20,  18000);
COMMIT;

--Bai 1 - Trigger INSERT tren HOADON
CREATE OR REPLACE TRIGGER trg_hoadon_insert
BEFORE INSERT ON Hoadon
FOR EACH ROW
DECLARE
    v_dem      NUMBER := 0;
    v_tonkho   NUMBER := 0;
BEGIN
    SELECT COUNT(*)
    INTO v_dem
    FROM Hang
    WHERE Mahang = :NEW.Mahang;
    IF v_dem = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Mahang khong ton tai trong bang HANG');
    END IF;
    SELECT Soluong
    INTO v_tonkho
    FROM Hang
    WHERE Mahang = :NEW.Mahang
    FOR UPDATE;
    IF :NEW.Soluongban > v_tonkho THEN
        RAISE_APPLICATION_ERROR(-20002, 'So luong ban vuot qua so luong ton kho');
    END IF;
    UPDATE Hang
    SET Soluong = Soluong - :NEW.Soluongban
    WHERE Mahang = :NEW.Mahang;
END trg_hoadon_insert;

---kiem tra 
---nhap dung
INSERT INTO Hoadon (Mahd, Mahang, Soluongban, Ngayban)
VALUES ('HD01', 'H01', 10, SYSDATE);
SELECT * FROM Hang;
SELECT * FROM Hoadon;
---nhap sai Mahang
INSERT INTO Hoadon (Mahd, Mahang, Soluongban, Ngayban)
VALUES ('HD02', 'H99', 5, SYSDATE);

---nhap vuot so luong ton kho
INSERT INTO Hoadon (Mahd, Mahang, Soluongban, Ngayban)
VALUES ('HD03', 'H03', 100, SYSDATE);

-- Bai 2 - Trigger DELETE tren HOADON
CREATE OR REPLACE TRIGGER trg_hoadon_delete
AFTER DELETE ON Hoadon
FOR EACH ROW
BEGIN
    UPDATE Hang
    SET Soluong = Soluong + :OLD.Soluongban
    WHERE Mahang = :OLD.Mahang;
END trg_hoadon_delete;
---kiem tra
DELETE FROM Hoadon
WHERE Mahd = 'HD01';
COMMIT;
SELECT * FROM Hoadon WHERE Mahd = 'HD01'
-- Bai 3 - Trigger UPDATE tren HOADON
CREATE OR REPLACE TRIGGER trg_hoadon_update
BEFORE UPDATE ON Hoadon
FOR EACH ROW
DECLARE
    v_tonkho_hientai NUMBER := 0;
    v_chenhlech      NUMBER := 0;
BEGIN
    IF :NEW.Mahang <> :OLD.Mahang THEN
        UPDATE Hang
        SET Soluong = Soluong + :OLD.Soluongban
        WHERE Mahang = :OLD.Mahang;
        SELECT Soluong
        INTO v_tonkho_hientai
        FROM Hang
        WHERE Mahang = :NEW.Mahang
        FOR UPDATE;
        IF :NEW.Soluongban > v_tonkho_hientai THEN
            RAISE_APPLICATION_ERROR(-20003, 'Khong du ton kho cho ma hang moi');
        END IF;
        UPDATE Hang
        SET Soluong = Soluong - :NEW.Soluongban
        WHERE Mahang = :NEW.Mahang;
    ELSE
        v_chenhlech := :NEW.Soluongban - :OLD.Soluongban;
        IF v_chenhlech > 0 THEN
            SELECT Soluong
            INTO v_tonkho_hientai
            FROM Hang
            WHERE Mahang = :NEW.Mahang
            FOR UPDATE;
            IF v_chenhlech > v_tonkho_hientai THEN
                RAISE_APPLICATION_ERROR(-20004, 'Khong du ton kho de cap nhat so luong ban');
            END IF;
        END IF;
        UPDATE Hang
        SET Soluong = Soluong - v_chenhlech
        WHERE Mahang = :NEW.Mahang;
    END IF;
END trg_hoadon_update;
---kiem tra
UPDATE Hoadon
SET Soluongban = 15
WHERE Mahd = 'HD02';
SELECT * FROM Hoadon WHERE Mahd = 'HD02'
INSERT INTO Hoadon (Mahd, Mahang, Soluongban, Ngayban)
VALUES ('HD02', 'H01', 10, SYSDATE);