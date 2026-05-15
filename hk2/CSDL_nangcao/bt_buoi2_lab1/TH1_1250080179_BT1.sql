create user BT1 identified by 123;
grant connect, resource to BT1;

CREATE USER is01 IDENTIFIED BY password123;
CREATE USER is02 IDENTIFIED BY password123;
GRANT CONNECT, RESOURCE TO is01, is02;
ALTER USER is01 QUOTA UNLIMITED ON USERS;
ALTER USER is02 QUOTA UNLIMITED ON USERS;

CREATE TABLE SanPham (ID INT PRIMARY KEY, TenSP VARCHAR2(50));
INSERT INTO SanPham VALUES (1, 'Laptop');
COMMIT;
GRANT SELECT, INSERT, UPDATE ON SanPham TO is02;

SELECT * FROM is01.SanPham;
INSERT INTO is01.SanPham VALUES (2, 'Mouse');


create table HANGHANGKHONG (
    MAHANG varchar2(10) primary key,
    TENHANG varchar2(100),
    NGTL date,
    DUONGBAY number
);

create table CHUYENBAY (
    MACB varchar2(10) primary key,
    MAHANG varchar2(10),
    XUATPHAT varchar2(50),
    DIEMDEN varchar2(50),
    BATDAU date,
    TGBAY number,
    constraint FK_CB_HHK foreign key (MAHANG) references HANGHANGKHONG(MAHANG)
);

create table NHANVIEN (
    MANV varchar2(10) primary key,
    HOTEN varchar2(100),
    GIOITINH varchar2(10),
    NGSINH date,
    NGVL date,
    CHUYENMON varchar2(50),
    constraint CK_CHUYENMON check (CHUYENMON in ('Phi công', 'Tiếp viên'))
);

create table PHANCONG (
    MACB varchar2(10),
    MANV varchar2(10),
    NHIEMVU varchar2(50),
    constraint PK_PC primary key (MACB, MANV),
    constraint FK_PC_CB foreign key (MACB) references CHUYENBAY(MACB),
    constraint FK_PC_NV foreign key (MANV) references NHANVIEN(MANV)
);

insert into HANGHANGKHONG values ('VN', 'Vietnam Airlines', to_date('15/01/1956', 'dd/mm/yyyy'), 52);
insert into HANGHANGKHONG values ('VJ', 'Vietjet Air', to_date('25/12/2011', 'dd/mm/yyyy'), 33);
insert into HANGHANGKHONG values ('BL', 'Jetstar Pacific Airlines', to_date('01/12/1990', 'dd/mm/yyyy'), 13);

insert into CHUYENBAY values ('VN550', 'VN', 'TP.HCM', 'Singapore', to_date('20/12/2025 13:15', 'dd/mm/yyyy hh24:mi'), 2);
insert into CHUYENBAY values ('VJ331', 'VJ', 'Đà Nẵng', 'Vinh', to_date('28/12/2025 22:30', 'dd/mm/yyyy hh24:mi'), 1);
insert into CHUYENBAY values ('BL696', 'BL', 'TP.HCM', 'Đà Lạt', to_date('24/12/2025 06:00', 'dd/mm/yyyy hh24:mi'), 0.5);

create or replace trigger TRG_CHECK_DATE
before insert on CHUYENBAY
for each row
declare
    v_ngtl date;
begin
    select NGTL into v_ngtl from HANGHANGKHONG where MAHANG = :new.MAHANG;
    if :new.BATDAU <= v_ngtl then
        raise_application_error(-20001, 'Ngay bat dau phai lon hon ngay thanh lap hang');
    end if;
end;


select * from NHANVIEN where extract(month from NGSINH) = 7;

select MACB from (select MACB from PHANCONG group by MACB order by count(MANV) desc) where rownum = 1;

select H.MAHANG, H.TENHANG, count(C.MACB) as SO_LUONG
from HANGHANGKHONG H
left join CHUYENBAY C on H.MAHANG = C.MAHANG and C.XUATPHAT = 'Đà Nẵng'
where C.MACB in (select MACB from PHANCONG group by MACB having count(MANV) < 2)
group by H.MAHANG, H.TENHANG;

select * from NHANVIEN NV
where not exists (
    select MACB from CHUYENBAY CB
    where not exists (
        select * from PHANCONG PC where PC.MANV = NV.MANV and PC.MACB = CB.MACB
    )
);

