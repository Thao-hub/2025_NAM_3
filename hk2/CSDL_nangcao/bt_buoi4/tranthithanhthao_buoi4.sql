
CREATE TABLE PHONGBAN (
    MaPhong INT PRIMARY KEY,
    TenPhong VARCHAR2(50),
    TruongPhong INT,
    NgayNhanChuc DATE
);
ALTER TABLE PHONGBAN
ADD CONSTRAINT FK_PB_TRUONGPHONG
FOREIGN KEY (TruongPhong) REFERENCES NHANVIEN(MaNV);
CREATE TABLE NHANVIEN (
    MaNV INT PRIMARY KEY,
    HoNV VARCHAR2(50),
    TenNV VARCHAR2(50),
    NgaySinh DATE,
    DiaChi VARCHAR2(50),
    Phai VARCHAR2(50),
    Luong INT,
    MaNQL INT,
    Phong INT
);
ALTER TABLE NHANVIEN
ADD CONSTRAINT FK_NV_PHONG
FOREIGN KEY (Phong) REFERENCES PHONGBAN(MaPhong);
ALTER TABLE NHANVIEN
ADD CONSTRAINT FK_NV_NQL
FOREIGN KEY (MaNQL) REFERENCES NHANVIEN(MaNV);
CREATE TABLE DIADIEMPHONG (
    MaPhong INT,
    DiaDiem VARCHAR2(50),
    CONSTRAINT PK_DDP PRIMARY KEY (MaPhong, DiaDiem),
    CONSTRAINT FK_DDP_PHONG FOREIGN KEY (MaPhong) REFERENCES PHONGBAN(MaPhong)
);
CREATE TABLE DEAN (
    MaDA INT PRIMARY KEY,
    TenDA VARCHAR2(50),
    DiemDA VARCHAR2(50),
    Phong INT,
    CONSTRAINT FK_DA_PHONG FOREIGN KEY (Phong) REFERENCES PHONGBAN(MaPhong)
);
CREATE TABLE PHANCONG (
    MaNV INT,
    MaDA INT,
    ThoiGian INT,
    CONSTRAINT PK_PC PRIMARY KEY (MaNV, MaDA),
    CONSTRAINT FK_PC_NV FOREIGN KEY (MaNV) REFERENCES NHANVIEN(MaNV),
    CONSTRAINT FK_PC_DA FOREIGN KEY (MaDA) REFERENCES DEAN(MaDA)
);
CREATE TABLE THANNHAN (
    MaTN INT PRIMARY KEY,
    HoTN VARCHAR2(50),
    TenTN VARCHAR2(50),
    Phai VARCHAR2(50),
    NgaySinh DATE
);
CREATE TABLE NVIEN_TNHAN (
    MaNV INT,
    MaTN INT,
    QuanHe VARCHAR2(50),
    CONSTRAINT PK_NV_TN PRIMARY KEY (MaNV, MaTN),
    CONSTRAINT FK_NV_TN_NV FOREIGN KEY (MaNV) REFERENCES NHANVIEN(MaNV),
    CONSTRAINT FK_NV_TN_TN FOREIGN KEY (MaTN) REFERENCES THANNHAN(MaTN)
);

INSERT INTO PHONGBAN VALUES (1, 'Nhan Su', 1, DATE '2020-01-01');
INSERT INTO PHONGBAN VALUES (2, 'Ky Thuat', 2, DATE '2021-03-01');

INSERT INTO NHANVIEN VALUES
(101, 'Nguyen', 'An', DATE '1995-10-10', 'Ha Noi', 'Nam', 15000000, NULL, 1);
INSERT INTO NHANVIEN VALUES
(102, 'Tran', 'Thao', DATE '1997-05-05', 'TP HCM', 'Nu', 12000000, 101, 2);

INSERT INTO DIADIEMPHONG VALUES (1, 'Tang 1');
INSERT INTO DIADIEMPHONG VALUES (2, 'Tang 2');
INSERT INTO DEAN VALUES (201, 'Phan mem A', 'Ha Noi', 2);
INSERT INTO DEAN VALUES (202, 'Website B', 'TP HCM', 1);
INSERT INTO PHANCONG VALUES (101, 201, 20);
INSERT INTO PHANCONG VALUES (102, 202, 15);
INSERT INTO THANNHAN VALUES
(301, 'Nguyen', 'Lan', 'Nu', DATE '2000-01-01');
INSERT INTO NVIEN_TNHAN VALUES (101, 301, 'Em gai');

DROP TABLE NVIEN_TNHAN;
DROP TABLE PHANCONG;
DROP TABLE DIADIEMPHONG;
DROP TABLE DEAN;
DROP TABLE THANNHAN;
DROP TABLE NHANVIEN;
DROP TABLE PHONGBAN;


--1.    Cho biết thông tin cá nhân về những nhân viên có tên ‘Thao’
SELECT * FROM NHANVIEN WHERE TenNV = 'Thao';
--2.    Tìm mã nhân viên, họ tên và địa chỉ của tất cả nhân viên làm việc phòng ‘Nhan Su’.
SELECT PB.TenPhong, NV.MaNV, NV.HoNV, NV.TenNV, NV.DiaChi
FROM NHANVIEN NV
JOIN PHONGBAN PB ON PB.MaPhong = NV.Phong
WHERE PB.TenPhong = 'Nhan Su';
--3.    Tìm mã nhân viên, họ tên và địa chỉ của tất cả nhân viên làm việc phòng ‘Nhan Su’ và ‘Ky Thuat’.
SELECT PB.TenPhong, NV.MaNV, NV.HoNV, NV.TenNV, NV.DiaChi 
FROM NHANVIEN NV
JOIN PHONGBAN PB ON PB.MaPhong = NV.Phong
WHERE PB.TenPhong IN ('Nhan Su', 'Ky Thuat');
--4.    Cho biết mã nhân viên , họ tên nhân viên và tên các đề án mà nhân viên tham gia.
SELECT NV.MaNV, NV.HoNV || ' ' || NV.TenNV AS HoTen, DA.TenDA
FROM NHANVIEN NV 
JOIN PHANCONG PC ON NV.MaNV = PC.MaNV
JOIN DEAN DA ON DA.MaDA = PC.MaDA;
--5.    Tìm mã đề án, tên đề án, tên phòng ban chủ trì đề án cùng mã trưởng phòng, tên trưởng phòng đó.
SELECT DA.MaDA, DA.TenDA, PB.TenPhong, PB.TruongPhong AS MaTruongPhong, NV.HoNV || ' ' || NV.TenNV AS TenTruongPhong
FROM DEAN DA
JOIN PHONGBAN PB 
    ON DA.Phong = PB.MaPhong
JOIN NHANVIEN NV 
    ON PB.TruongPhong = NV.MaNV;
--6.    Cho biết mã nhân viên, họ tên của những nhân viên tham gia vào đề án có mã là ‘201’ 
--và có thời gian làm việc cho đề án trên 15giờ/tuần.
SELECT NV.MaNV, NV.HoNV || ' ' || NV.TenNV AS HoTen, PC.ThoiGian
FROM NHANVIEN NV
JOIN PHANCONG PC ON NV.MaNV = PC.MaNV
WHERE PC.MaDA = 201
  AND PC.ThoiGian > 15;

--7.    Cho biết mã nhân viên, họ tên của những nhân viên có cùng tên với người thân.
SELECT DISTINCT NV.MaNV, NV.HoNV || ' ' || NV.TenNV AS HoTen
FROM NHANVIEN NV
JOIN NVIEN_TNHAN NT ON NV.MaNV = NT.MaNV
JOIN THANNHAN TN ON NT.MaTN = TN.MaTN
WHERE NV.TenNV = TN.TenTN;

--8.    Cho biết mã nhân viên, họ tên của những nhân viên có người trưởng phòng có họ tên là ‘Tran’ ‘Thao’.
SELECT NV.MaNV, NV.HoNV || ' ' || NV.TenNV AS HoTen
FROM NHANVIEN NV
JOIN PHONGBAN PB ON NV.Phong = PB.MaPhong
JOIN NHANVIEN TP ON PB.TruongPhong = TP.MaNV
WHERE TP.HoNV = 'Tran'
  AND TP.TenNV = 'Thao';

--9.    Cho biết mã nhân viên, họ tên của những nhân viên có người quản lý có họ tên là ‘Tran’ ‘Thao’.
SELECT NV.MaNV,
       NV.HoNV || ' ' || NV.TenNV AS HoTen
FROM NHANVIEN NV
JOIN NHANVIEN NQL ON NV.MaNQL = NQL.MaNV
WHERE NQL.HoNV = 'Tran'
AND NQL.TenNV = 'Thao';

--10.    Cho biết mã nhân viên, họ tên của những nhân viên tham gia mọi đề án của công ty.
SELECT NV.MaNV,
       NV.HoNV || ' ' || NV.TenNV AS HoTen
FROM NHANVIEN NV
JOIN PHANCONG PC ON NV.MaNV = PC.MaNV
GROUP BY NV.MaNV, NV.HoNV, NV.TenNV
HAVING COUNT(DISTINCT PC.MaDA) = (SELECT COUNT(*) FROM DEAN);

--11.    Cho biết mã nhân viên, họ tên của những nhân viên không tham gia đề án nào của công ty.
SELECT NV.MaNV,
       NV.HoNV || ' ' || NV.TenNV AS HoTen
FROM NHANVIEN NV
LEFT JOIN PHANCONG PC ON NV.MaNV = PC.MaNV
WHERE PC.MaNV IS NULL;

--12.    Cho biết mức lương trung bình của nhân viên trong công ty.
SELECT AVG(Luong) AS LuongTrungBinh
FROM NHANVIEN;

--13.    Cho biết mức lương trung bình của nhân viên nam trong công ty.
SELECT AVG(Luong) AS LuongTrungBinh_Nam
FROM NHANVIEN
WHERE Phai = 'Nam';

--14.    Cho biết tổng số đề án của công ty.
SELECT COUNT(*) AS TongSoDeAn
FROM DEAN;

--15.    Với mỗi đề án, cho biết tổng số nhân viên tham gia vào đề án.
SELECT DA.MaDA, DA.TenDA, COUNT(PC.MaNV) AS SoNhanVien
FROM DEAN DA
LEFT JOIN PHANCONG PC ON DA.MaDA = PC.MaDA
GROUP BY DA.MaDA, DA.TenDA;

--16.    Với mỗi đề án, cho biết tổng số nhân viên nữ tham gia vào đề án.
SELECT DA.MaDA, DA.TenDA, COUNT(NV.MaNV) AS SoNhanVienNu
FROM DEAN DA
LEFT JOIN PHANCONG PC ON DA.MaDA = PC.MaDA
LEFT JOIN NHANVIEN NV ON PC.MaNV = NV.MaNV
WHERE NV.Phai = 'Nu'
GROUP BY DA.MaDA, DA.TenDA;

--17.    Tăng thời gian tham gia đề án của các nhân viên nam thêm 4giờ/tuần
UPDATE PHANCONG
SET ThoiGian = ThoiGian + 4
WHERE MaNV IN (
    SELECT MaNV
    FROM NHANVIEN
    WHERE Phai = 'Nam'
);

--18.    Xóa tất cả những nhân viên có mức lương dưới 500000.
