SQL> create user LAB1 indentified by 123;
create user LAB1 indentified by 123
                 *
ERROR at line 1:
ORA-00922: missing or invalid option 


SQL> SHOW CON_NAME;
CDB$ROOT                                                                        
SQL> SHOW PDBS;
         2 PDB$SEED                       READ ONLY  NO                         
         3 XEPDB1                         READ WRITE NO                         
SQL> ALTER SESSION SET CONTAINER = XEPDB1;
SQL> create user LAB1 indentified by 123;
create user LAB1 indentified by 123
                 *
ERROR at line 1:
ORA-00922: missing or invalid option 


SQL> SHOW CON_NAME;
XEPDB1                                                                          
SQL> ALTER SESSION SET CONTAINER = ORCLPDB;
ERROR:
ORA-65011: Pluggable database ORCLPDB does not exist. 


SQL> SHOW CON_NAME;
XEPDB1                                                                          
SQL> SHOW USER;
USER is "SYS"
SQL> create user LAB1 indentified by 123;
create user LAB1 indentified by 123
                 *
ERROR at line 1:
ORA-00922: missing or invalid option 


SQL> create user LAB1 identified by 123;
SQL> grant create session, create table to LAB1;
SQL> alter LAB1 quota unlimited on users;
alter LAB1 quota unlimited on users
      *
ERROR at line 1:
ORA-00940: invalid ALTER command 


SQL> alter user LAB1 quota unlimited on users;
SQL> create table HANGHANGKHONG(
  2  MAHANG varchar2(10) primary key,
  3  TENHANG nvarchar2(100) not null,
  4  NGTL date not null,
  5  DUONGBAY number
  6  );
SQL> create table CHUYENBAY(
  2  MACB varchar2(10) primary key,
  3  M
  4  
SQL> create table CHUYENBAY(
  2  MACB varchar2(10) primary key,
  3  MAHANG varchar2(10) not null,
  4  XUATPHAT nvarchar2(100) not null,
  5  DIEMDEN nvarchar2(100) not null,
  6  BATDAU date not null,
  7  TGBAY number(4,1) check(TGBAY > 0) not null);
SQL> create table NHANVIEN(
  2  MANV varchar2(10) primary key,
  3  HOTEN nvarchar2(100) not null,
  4  GIOITINH varchar2(3),
  5  NGSINH date not null,
  6  NGVL date,
  7  CHUYENMON nvarchar2(50));
SQL> create table PHANCONG(
  2  MACB varchar2(10) not null,
  3  MANV varchar2(10) not null,
  4  NHIEMVU nvarchar2(50));
SQL> alter table CHUYENBAY add constraint fk_cb_hhk foreign key (MAHANG) references HANGHANGKHONG(MAHANG);
SQL> alter table PHANCONG add constraint fk_cb_hhk primary key (MACB, MANV);
alter table PHANCONG add constraint fk_cb_hhk primary key (MACB, MANV)
                                    *
ERROR at line 1:
ORA-02264: name already used by an existing constraint 


SQL> alter table PHANCONG add constraint fk_pc_cb_nv primary key (MACB, MANV);
SQL> alter table CHUYENBAY add constraint fk_pc_cb foreign key (MACB) references CHUYENBAY(MACB);
SQL> alter table CHUYENBAY add constraint fk_pc_nv foreign key (MANV) references NHANVIEN(MANV);
alter table CHUYENBAY add constraint fk_pc_nv foreign key (MANV) references NHANVIEN(MANV)
                                                           *
ERROR at line 1:
ORA-00904: "MANV": invalid identifier 


SQL> alter table CHUYENBAY delete constraint fk_pc_cb foreign key (MACB) references CHUYENBAY(MACB);
alter table CHUYENBAY delete constraint fk_pc_cb foreign key (MACB) references CHUYENBAY(MACB)
                      *
ERROR at line 1:
ORA-01735: invalid ALTER TABLE option 


SQL> alter table drop constraint fk_pc_cb;
alter table drop constraint fk_pc_cb
            *
ERROR at line 1:
ORA-00903: invalid table name 


SQL> alter table CHUYENBAY drop constraint fk_pc_cb;
SQL> alter table PHANCONG add constraint fk_pc_cb foreign key (MACB) references CHUYENBAY(MACB);
SQL> alter table PHANCONG add constraint fk_pc_nv foreign key (MANV) references NHANVIEN(MANV);
SQL> insert into HANGHANGKHONG
  2  values ('VN', N'Vietnam Airlines', to_date('15/01/1956', 'dd/mm/yyyy')),
  3  values ('VN', N'Vietnam Airlines', to_date('15/01/1956', 'dd/mm/yyyy')),
  4  ddd;
values ('VN', N'Vietnam Airlines', to_date('15/01/1956', 'dd/mm/yyyy')),
                                                                       *
ERROR at line 2:
ORA-00933: SQL command not properly ended 


SQL> insert into HANGHANGKHONG
  2  values ('VN', N'Vietnam Airlines', to_date('15/01/1956', 'dd/mm/yyyy'), 52),
  3  values ('VJ', N'Vietjet Air', to_date('25/12/2011', 'dd/mm/yyyy'), 33),
  4  values ('BL', N'Jetstar Pacific Airlines', to_date('01/12/1990', 'dd/mm/yyyy'), 13);
values ('VN', N'Vietnam Airlines', to_date('15/01/1956', 'dd/mm/yyyy'), 52),
                                                                           *
ERROR at line 2:
ORA-00933: SQL command not properly ended 


SQL> INSERT INTO HANGHANGKHONG (MAHANG, TENHANG, NGTL, DUONGBAY)
  2  VALUES ('VN', N'Vietnam Airlines', DATE '1956-01-15', 52);
SQL> 
SQL> INSERT INTO HANGHANGKHONG (MAHANG, TENHANG, NGTL, DUONGBAY)
  2  VALUES ('VJ', N'Vietjet Air', DATE '2011-12-25', 33);
SQL> 
SQL> INSERT INTO HANGHANGKHONG (MAHANG, TENHANG, NGTL, DUONGBAY)
  2  VALUES ('BL', N'Jetstar Pacific Airlines', DATE '1990-12-05', 13);
SQL> INSERT INTO CHUYENBAY
  2  (MACB, MAHANG, XUATPHAT, DIEMDEN, BATDAU, TGBAY)
  3  VALUES
  4  ('VN550', 'VN', N'TP. HCM', N'Singapore',
  5   TO_DATE('13:15 20/12/2025', 'HH24:MI DD/MM/YYYY'), 2);
SQL> 
SQL> INSERT INTO CHUYENBAY
  2  (MACB, MAHANG, XUATPHAT, DIEMDEN, BATDAU, TGBAY)
  3  VALUES
  4  ('VJ331', 'VJ', N'D… N?ng', N'Vinh',
  5   TO_DATE('22:30 28/12/2025', 'HH24:MI DD/MM/YYYY'), 1);
SQL> 
SQL> INSERT INTO CHUYENBAY
  2  (MACB, MAHANG, XUATPHAT, DIEMDEN, BATDAU, TGBAY)
  3  VALUES
  4  ('BL696', 'BL', N'TP. HCM', N'D… L?t',
  5   TO_DATE('06:00 24/12/2025', 'HH24:MI DD/MM/YYYY'), 0.5);
SQL> INSERT INTO NHANVIEN
  2  (MANV, HOTEN, GIOITINH, NGSINH, NGVL, CHUYENMON)
  3  VALUES
  4  ('NV01', N'Lƒm Van B?n', N'Nam',
  5   DATE '1991-09-10', DATE '2021-06-05', N'Phi c“ng');
SQL> 
SQL> INSERT INTO NHANVIEN
  2  (MANV, HOTEN, GIOITINH, NGSINH, NGVL, CHUYENMON)
  3  VALUES
  4  ('NV02', N'Duong Th? L?c', N'N?',
  5   DATE '1989-03-22', DATE '2020-11-12', N'Ti?p viˆn');
SQL> 
SQL> INSERT INTO NHANVIEN
  2  (MANV, HOTEN, GIOITINH, NGSINH, NGVL, CHUYENMON)
  3  VALUES
  4  ('NV03', N'Ho…ng Thanh T—ng', N'Nam',
  5   DATE '1995-07-29', DATE '2022-04-11', N'Ti?p viˆn');
SQL> INSERT INTO PHANCONG (MACB, MANV, NHIEMVU)
  2  VALUES ('VN550', 'NV01', N'Co tru?ng');
SQL> 
SQL> INSERT INTO PHANCONG (MACB, MANV, NHIEMVU)
  2  VALUES ('VN550', 'NV02', N'Ti?p viˆn');
SQL> 
SQL> INSERT INTO PHANCONG (MACB, MANV, NHIEMVU)
  2  VALUES ('BL696', 'NV03', N'Ti?p viˆn tru?ng');
SQL> COMMIT;
SQL> alter table NHANHVIEN add check(CHUYENMON in ('Phi cong', 'Tiep vien')) from CHUYENMON;
alter table NHANHVIEN add check(CHUYENMON in ('Phi cong', 'Tiep vien')) from CHUYENMON
                                                                        *
ERROR at line 1:
ORA-01735: invalid ALTER TABLE option 


SQL> alter table NHANHVIEN add constraint ck_nv_chuyenmon check(CHUYENMON in (N'Phi c“ng', N'Ti?p viˆn'));
alter table NHANHVIEN add constraint ck_nv_chuyenmon check(CHUYENMON in (N'Phi c“ng', N'Ti?p viˆn'))
*
ERROR at line 1:
ORA-00942: table or view does not exist 


SQL> alter table NHANHVIEN add constraint ck_nv_chuyenmon check(CHUYENMON in (N'Phi cong', N'Tiep vien'));
alter table NHANHVIEN add constraint ck_nv_chuyenmon check(CHUYENMON in (N'Phi cong', N'Tiep vien'))
*
ERROR at line 1:
ORA-00942: table or view does not exist 


SQL> alter table NHANHVIEN add constraint ck_nv_chuyenmon check(CHUYENMON in (N'Phi cong', N'Tiep vien'));
alter table NHANHVIEN add constraint ck_nv_chuyenmon check(CHUYENMON in (N'Phi cong', N'Tiep vien'))
*
ERROR at line 1:
ORA-00942: table or view does not exist 


SQL> alter table NHANVIEN add constraint ck_nv_chuyenmon check(CHUYENMON in (N'Phi c“ng', N'Ti?p viˆn'));
SQL> create or replace trigger trg_cb_ngay
  2  before insert or update on CHUYENBAY
  3  for each row
  4  declare
  5  	v_ngtl date;
  6  begin
  7  	select NGTL
  8  	into v_ngtl
  9  	from HANGHANGKHONG
 10  	where MAHANG = :NEW.MAHANG;
 11  	if :NEW.BATDAU <= v_ngtl then
 12  		raise_application_error(
 13  			-20001,
 14  			'Ngay bat dau chuyen bay phai lon hon ngay thanh lap hang hang khong'
 15  		);
 16  	end if;
 17  end;
 18  /
create or replace trigger trg_cb_ngay
                          *
ERROR at line 1:
ORA-04089: cannot create triggers on objects owned by SYS 


SQL> EXIT;
