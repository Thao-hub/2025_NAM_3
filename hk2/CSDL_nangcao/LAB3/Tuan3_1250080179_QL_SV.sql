SET DEFINE OFF;

ALTER SESSION SET NLS_DATE_FORMAT = 'DD/MM/YYYY';

CREATE TABLE COURSE (
    CourseNo        NUMBER(8,0)    CONSTRAINT PK_COURSE PRIMARY KEY,
    Description     VARCHAR2(50),
    Cost            NUMBER(9,2),
    Prerequisite    NUMBER(8,0),
    CreatedBy       VARCHAR2(30)   NOT NULL,
    CreatedDate     DATE           NOT NULL,
    ModifiedBy      VARCHAR2(30)   NOT NULL,
    ModifiedDate    DATE           NOT NULL,
    CONSTRAINT FK_COURSE_PREREQUISITE FOREIGN KEY (Prerequisite) REFERENCES COURSE (CourseNo)
);

CREATE TABLE INSTRUCTOR (
    InstructorID    NUMBER(8,0)    CONSTRAINT PK_INSTRUCTOR PRIMARY KEY,
    Salutation      VARCHAR2(5),
    FirstName       VARCHAR2(25),
    LastName        VARCHAR2(25),
    Address         VARCHAR2(50),
    Phone           VARCHAR2(15),
    CreatedBy       VARCHAR2(30)   NOT NULL,
    CreatedDate     DATE           NOT NULL,
    ModifiedBy      VARCHAR2(30)   NOT NULL,
    ModifiedDate    DATE           NOT NULL
);

CREATE TABLE STUDENT (
    StudentID           NUMBER(8,0)    CONSTRAINT PK_STUDENT PRIMARY KEY,
    Salutation          VARCHAR2(5),
    FirstName           VARCHAR2(25),
    LastName            VARCHAR2(25)   NOT NULL,
    Address             VARCHAR2(50),
    Phone               VARCHAR2(15),
    Employer            VARCHAR2(50),
    RegistrationDate    DATE           NOT NULL,
    CreatedBy           VARCHAR2(30)   NOT NULL,
    CreatedDate         DATE           NOT NULL,
    ModifiedBy          VARCHAR2(30)   NOT NULL,
    ModifiedDate        DATE           NOT NULL
);

CREATE TABLE CLASS (
    ClassID          NUMBER(8,0)    CONSTRAINT PK_CLASS PRIMARY KEY,
    CourseNo         NUMBER(8,0)    NOT NULL,
    ClassNo          NUMBER(3,0)    NOT NULL,
    StartDateTime    DATE,
    Location         VARCHAR2(50),
    InstructorID     NUMBER(8,0)    NOT NULL,
    Capacity         NUMBER(3,0),
    CreatedBy        VARCHAR2(30)   NOT NULL,
    CreatedDate      DATE           NOT NULL,
    ModifiedBy       VARCHAR2(30)   NOT NULL,
    ModifiedDate     DATE           NOT NULL,
    CONSTRAINT FK_CLASS_COURSE FOREIGN KEY (CourseNo) REFERENCES COURSE (CourseNo),
    CONSTRAINT FK_CLASS_INSTRUCTOR FOREIGN KEY (InstructorID) REFERENCES INSTRUCTOR (InstructorID)
);

CREATE TABLE ENROLLMENT (
    StudentID        NUMBER(8,0)    NOT NULL,
    ClassID          NUMBER(8,0)    NOT NULL,
    EnrollDate       DATE           NOT NULL,
    FinalGrade       NUMBER(3,0),
    CreatedBy        VARCHAR2(30)   NOT NULL,
    CreatedDate      DATE           NOT NULL,
    ModifiedBy       VARCHAR2(30)   NOT NULL,
    ModifiedDate     DATE           NOT NULL,
    CONSTRAINT PK_ENROLLMENT PRIMARY KEY (StudentID, ClassID),
    CONSTRAINT FK_ENROLLMENT_STUDENT FOREIGN KEY (StudentID) REFERENCES STUDENT (StudentID),
    CONSTRAINT FK_ENROLLMENT_CLASS FOREIGN KEY (ClassID) REFERENCES CLASS (ClassID)
);

CREATE TABLE GRADE (
    StudentID        NUMBER(8,0)    NOT NULL,
    ClassID          NUMBER(8,0)    NOT NULL,
    Grade            NUMBER(3,0)    NOT NULL,
    Comments         VARCHAR2(2000),
    CreatedBy        VARCHAR2(30)   NOT NULL,
    CreatedDate      DATE           NOT NULL,
    ModifiedBy       VARCHAR2(30)   NOT NULL,
    ModifiedDate     DATE           NOT NULL,
    CONSTRAINT PK_GRADE PRIMARY KEY (StudentID, ClassID),
    CONSTRAINT FK_GRADE_ENROLLMENT FOREIGN KEY (StudentID, ClassID) REFERENCES ENROLLMENT (StudentID, ClassID)
);

INSERT INTO COURSE VALUES (101, 'Nhập môn cơ sở dữ liệu', 1500000, NULL, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO COURSE VALUES (102, 'Lập trình Oracle', 1800000, 101, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO COURSE VALUES (103, 'Phân tích dữ liệu', 2200000, 101, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO COURSE VALUES (104, 'Hệ quản trị cơ sở dữ liệu', 2000000, 101, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO COURSE VALUES (105, 'Lập trình Java', 1700000, NULL, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO COURSE VALUES (106, 'Phát triển Web', 1900000, 105, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');

INSERT INTO INSTRUCTOR VALUES (201, 'TS.', 'Nguyễn', 'An', 'Quận 1, TP. Hồ Chí Minh', '0909000001', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO INSTRUCTOR VALUES (202, 'ThS.', 'Trần', 'Bình', 'Quận 3, TP. Hồ Chí Minh', '0909000002', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO INSTRUCTOR VALUES (203, 'ThS.', 'Lê', 'Cúc', 'Thủ Đức, TP. Hồ Chí Minh', '0909000003', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO INSTRUCTOR VALUES (204, 'TS.', 'Phạm', 'Dũng', 'Biên Hòa, Đồng Nai', '0909000004', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO INSTRUCTOR VALUES (205, 'ThS.', 'Võ', 'Hạnh', 'Dĩ An, Bình Dương', '0909000005', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO INSTRUCTOR VALUES (206, 'ThS.', 'Đỗ', 'Khánh', 'Nha Trang, Khánh Hòa', '0909000006', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');

INSERT INTO STUDENT VALUES (3001, 'Mr.', 'Nguyễn', 'Minh', 'Quận 10, TP. Hồ Chí Minh', '0911000001', 'Công ty Sao Việt', DATE '2026-01-05', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3002, 'Ms.', 'Trần', 'Lan', 'Quận 7, TP. Hồ Chí Minh', '0911000002', 'FPT Software', DATE '2026-01-06', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3003, 'Mr.', 'Lê', 'Quang', 'Thủ Đức, TP. Hồ Chí Minh', '0911000003', 'TMA Solutions', DATE '2026-01-07', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3004, 'Ms.', 'Phạm', 'Mai', 'Biên Hòa, Đồng Nai', '0911000004', 'VNPT', DATE '2026-01-08', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3005, 'Mr.', 'Hoàng', 'Nam', 'Dĩ An, Bình Dương', '0911000005', 'VNG', DATE '2026-01-09', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3006, 'Ms.', 'Võ', 'Ngọc', 'Quận 12, TP. Hồ Chí Minh', '0911000006', 'Công ty Misa', DATE '2026-01-10', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3007, 'Mr.', 'Đặng', 'Khoa', 'Bình Thạnh, TP. Hồ Chí Minh', '0911000007', 'CMC Global', DATE '2026-01-11', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3008, 'Ms.', 'Bùi', 'Thảo', 'Gò Vấp, TP. Hồ Chí Minh', '0911000008', 'Shopee', DATE '2026-01-12', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3009, 'Mr.', 'Phan', 'Huy', 'Tân Bình, TP. Hồ Chí Minh', '0911000009', 'Viettel', DATE '2026-01-13', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3010, 'Ms.', 'Đoàn', 'Vy', 'Tân Phú, TP. Hồ Chí Minh', '0911000010', 'MoMo', DATE '2026-01-14', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3011, 'Mr.', 'Ngô', 'Hiếu', 'Quận 5, TP. Hồ Chí Minh', '0911000011', 'Công ty Phần mềm Á Châu', DATE '2026-01-15', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3012, 'Ms.', 'Dương', 'Linh', 'Quận 11, TP. Hồ Chí Minh', '0911000012', 'KMS Technology', DATE '2026-01-16', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3013, 'Mr.', 'Lý', 'Sơn', 'Thủ Dầu Một, Bình Dương', '0911000013', 'Becamex IDC', DATE '2026-01-17', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3014, 'Ms.', 'Huỳnh', 'Chi', 'Bến Lức, Long An', '0911000014', 'Công ty Tiên Phong', DATE '2026-01-18', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3015, 'Mr.', 'Mai', 'Phúc', 'Mỹ Tho, Tiền Giang', '0911000015', 'Công ty Minh Tâm', DATE '2026-01-19', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3016, 'Ms.', 'Tạ', 'Nhi', 'Long Xuyên, An Giang', '0911000016', 'FIS', DATE '2026-01-20', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3017, 'Mr.', 'Cao', 'Tùng', 'Cần Thơ', '0911000017', 'Rikkeisoft', DATE '2026-01-21', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3018, 'Ms.', 'Trịnh', 'Yến', 'Vũng Tàu', '0911000018', 'NashTech', DATE '2026-01-22', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3019, 'Mr.', 'Kiều', 'Phong', 'Phan Thiết, Bình Thuận', '0911000019', 'Công ty Dữ liệu Việt', DATE '2026-01-23', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO STUDENT VALUES (3020, 'Ms.', 'Đinh', 'Xuân', 'Bảo Lộc, Lâm Đồng', '0911000020', 'Tự do', DATE '2026-01-24', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');

INSERT INTO CLASS VALUES (1001, 101, 1, TO_DATE('15/04/2026 08:00', 'DD/MM/YYYY HH24:MI'), 'Phòng A101', 201, 35, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1002, 101, 2, TO_DATE('16/04/2026 13:30', 'DD/MM/YYYY HH24:MI'), 'Phòng A102', 202, 35, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1003, 102, 1, TO_DATE('20/04/2026 08:00', 'DD/MM/YYYY HH24:MI'), 'Phòng B201', 201, 30, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1004, 102, 2, TO_DATE('21/04/2026 13:30', 'DD/MM/YYYY HH24:MI'), 'Phòng B202', 203, 30, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1005, 103, 1, TO_DATE('22/04/2026 08:00', 'DD/MM/YYYY HH24:MI'), 'Phòng C301', 201, 30, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1006, 104, 1, TO_DATE('23/04/2026 13:30', 'DD/MM/YYYY HH24:MI'), 'Phòng C302', 204, 25, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1007, 105, 1, TO_DATE('24/04/2026 08:00', 'DD/MM/YYYY HH24:MI'), 'Phòng D401', 201, 30, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1008, 106, 1, TO_DATE('25/04/2026 13:30', 'DD/MM/YYYY HH24:MI'), 'Phòng D402', 205, 30, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1009, 106, 2, TO_DATE('26/04/2026 08:00', 'DD/MM/YYYY HH24:MI'), 'Phòng D403', 201, 30, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO CLASS VALUES (1010, 103, 2, TO_DATE('27/04/2026 13:30', 'DD/MM/YYYY HH24:MI'), 'Phòng C303', 206, 25, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');

INSERT INTO ENROLLMENT VALUES (3001, 1001, DATE '2026-04-01', 92, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3002, 1001, DATE '2026-04-01', 85, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3003, 1001, DATE '2026-04-01', 78, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3006, 1001, DATE '2026-04-02', 88, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3007, 1001, DATE '2026-04-02', 69, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3009, 1001, DATE '2026-04-02', 74, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3010, 1001, DATE '2026-04-02', 91, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3011, 1002, DATE '2026-04-03', 83, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3012, 1002, DATE '2026-04-03', 87, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3013, 1002, DATE '2026-04-03', 72, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3014, 1002, DATE '2026-04-03', 95, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3015, 1002, DATE '2026-04-03', 81, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3016, 1002, DATE '2026-04-04', 76, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3004, 1002, DATE '2026-04-04', 89, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3005, 1002, DATE '2026-04-04', 67, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3008, 1002, DATE '2026-04-04', 93, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3017, 1002, DATE '2026-04-04', 84, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3018, 1002, DATE '2026-04-05', 77, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3019, 1002, DATE '2026-04-05', 90, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3001, 1003, DATE '2026-04-05', 94, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3005, 1003, DATE '2026-04-05', 82, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3012, 1003, DATE '2026-04-05', 79, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3004, 1004, DATE '2026-04-06', 86, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3008, 1004, DATE '2026-04-06', 91, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3014, 1004, DATE '2026-04-06', 75, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3001, 1005, DATE '2026-04-06', 96, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3007, 1005, DATE '2026-04-06', 80, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3015, 1005, DATE '2026-04-07', 73, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3017, 1005, DATE '2026-04-07', 88, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3018, 1005, DATE '2026-04-07', 84, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3005, 1006, DATE '2026-04-07', 71, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3009, 1006, DATE '2026-04-07', 66, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3002, 1007, DATE '2026-04-08', 93, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3011, 1007, DATE '2026-04-08', 78, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3013, 1007, DATE '2026-04-08', 81, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3019, 1007, DATE '2026-04-08', 87, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3006, 1008, DATE '2026-04-09', 90, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3010, 1008, DATE '2026-04-09', 86, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3017, 1008, DATE '2026-04-09', 82, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3016, 1009, DATE '2026-04-10', 74, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3018, 1009, DATE '2026-04-10', 89, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3003, 1010, DATE '2026-04-10', 85, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3019, 1010, DATE '2026-04-10', 92, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO ENROLLMENT VALUES (3020, 1010, DATE '2026-04-10', 68, 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');

INSERT INTO GRADE VALUES (3001, 1001, 92, 'Nắm chắc kiến thức nền tảng.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3002, 1001, 85, 'Thực hành tốt, cần cải thiện phần chuẩn hóa.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3003, 1001, 78, 'Hoàn thành đầy đủ bài tập.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3006, 1001, 88, 'Tư duy tốt, trình bày rõ ràng.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3007, 1001, 69, 'Cần luyện thêm phần truy vấn.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3009, 1001, 74, 'Có tiến bộ trong các buổi cuối.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3010, 1001, 91, 'Kết quả rất tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3011, 1002, 83, 'Hiểu bài, thao tác ổn định.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3012, 1002, 87, 'Thực hành hiệu quả.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3013, 1002, 72, 'Cần chú ý thêm về mô hình dữ liệu.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3014, 1002, 95, 'Xuất sắc ở phần thiết kế.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3015, 1002, 81, 'Đạt yêu cầu tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3016, 1002, 76, 'Cần luyện thêm PL/SQL.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3004, 1002, 89, 'Tiếp thu nhanh và chủ động.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3005, 1002, 67, 'Cần bổ sung phần thực hành.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3008, 1002, 93, 'Làm bài tốt và trình bày sạch.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3017, 1002, 84, 'Đạt yêu cầu khá.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3018, 1002, 77, 'Cần cải thiện tốc độ làm bài.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3019, 1002, 90, 'Hoàn thành tốt phần truy vấn.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3001, 1003, 94, 'Thành thạo cú pháp Oracle.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3005, 1003, 82, 'Có tiến bộ rõ rệt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3012, 1003, 79, 'Nắm bài ở mức khá.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3004, 1004, 86, 'Làm tốt phần thủ tục.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3008, 1004, 91, 'Vận dụng tốt trigger.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3014, 1004, 75, 'Đạt yêu cầu.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3001, 1005, 96, 'Phân tích dữ liệu rất tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3007, 1005, 80, 'Biết cách đọc và xử lý dữ liệu.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3015, 1005, 73, 'Cần cải thiện trực quan hóa.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3017, 1005, 88, 'Thực hành ổn định.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3018, 1005, 84, 'Kết quả khá tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3005, 1006, 71, 'Đạt mức trung bình khá.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3009, 1006, 66, 'Cần ôn tập thêm.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3002, 1007, 93, 'Lập trình tốt, cú pháp chính xác.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3011, 1007, 78, 'Nắm căn bản tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3013, 1007, 81, 'Tư duy logic tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3019, 1007, 87, 'Hoàn thành tốt đồ án nhỏ.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3006, 1008, 90, 'Thiết kế giao diện và xử lý ổn.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3010, 1008, 86, 'Làm tốt phần frontend.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3017, 1008, 82, 'Đạt yêu cầu tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3016, 1009, 74, 'Cần tối ưu thêm ứng dụng.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3018, 1009, 89, 'Có khả năng triển khai tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3003, 1010, 85, 'Phân tích dữ liệu đúng hướng.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3019, 1010, 92, 'Kết quả rất tốt.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');
INSERT INTO GRADE VALUES (3020, 1010, 68, 'Cần rèn luyện thêm kỹ năng thực hành.', 'ADMIN', DATE '2026-04-13', 'ADMIN', DATE '2026-04-13');

COMMIT;


SET SERVEROUTPUT ON;

-- BAI 1 - Cau 1a, 1b
CREATE TABLE cau1 (
    id   NUMBER,
    name VARCHAR2(20)
);
CREATE SEQUENCE Cau1Seq
START WITH 5
INCREMENT BY 5;

-- BAI 1 - Cau 1c den 1j
DECLARE
    v_name VARCHAR2(50);
    v_id   NUMBER;
BEGIN
    -- [d] Them sinh vien dang ki nhieu mon nhat
    SELECT firstname || ' ' || lastname
    INTO   v_name
    FROM   student
    WHERE  studentid = (
        SELECT studentid
        FROM   enrollment
        GROUP  BY studentid
        HAVING COUNT(*) = (
            SELECT MAX(cnt)
            FROM (
                SELECT COUNT(*) cnt
                FROM enrollment
                GROUP BY studentid
            )
        )
        FETCH FIRST 1 ROWS ONLY
    );

    INSERT INTO cau1 (id, name)
    VALUES (cau1seq.NEXTVAL, v_name);

    SAVEPOINT sp_a;

    -- [e] Them sinh vien dang ki it mon nhat
    SELECT firstname || ' ' || lastname
    INTO   v_name
    FROM   student
    WHERE  studentid = (
        SELECT studentid
        FROM   enrollment
        GROUP  BY studentid
        HAVING COUNT(*) = (
            SELECT MIN(cnt)
            FROM (
                SELECT COUNT(*) cnt
                FROM enrollment
                GROUP BY studentid
            )
        )
        FETCH FIRST 1 ROWS ONLY
    );

    INSERT INTO cau1 (id, name)
    VALUES (cau1seq.NEXTVAL, v_name);

    SAVEPOINT sp_b;

    -- [f] Them giao vien day nhieu lop nhat
    SELECT i.firstname || ' ' || i.lastname
    INTO   v_name
    FROM   instructor i
    WHERE  i.instructorid = (
        SELECT instructorid
        FROM   class
        GROUP  BY instructorid
        HAVING COUNT(*) = (
            SELECT MAX(cnt)
            FROM (
                SELECT COUNT(*) cnt
                FROM class
                GROUP BY instructorid
            )
        )
        FETCH FIRST 1 ROWS ONLY
    );

    INSERT INTO cau1 (id, name)
    VALUES (cau1seq.NEXTVAL, v_name);

    SAVEPOINT sp_c;

    -- [g] Lay ID cua giao vien vua them vao bien v_id
    SELECT id
    INTO   v_id
    FROM   cau1
    WHERE  name = v_name
    FETCH FIRST 1 ROWS ONLY;

    DBMS_OUTPUT.PUT_LINE('ID giao vien day nhieu lop nhat: ' || v_id);

    -- [h] Rollback giao vien vua them
    ROLLBACK TO sp_b;

    -- [i] Them giao vien it lop nhat, dung v_id da luu
    SELECT i.firstname || ' ' || i.lastname
    INTO   v_name
    FROM   instructor i
    WHERE  i.instructorid = (
        SELECT instructorid
        FROM   class
        GROUP  BY instructorid
        HAVING COUNT(*) = (
            SELECT MIN(cnt)
            FROM (
                SELECT COUNT(*) cnt
                FROM class
                GROUP BY instructorid
            )
        )
        FETCH FIRST 1 ROWS ONLY
    );

    INSERT INTO cau1 (id, name)
    VALUES (v_id, v_name);

    -- [j] Them lai giao vien nhieu lop nhat, dung sequence
    SELECT i.firstname || ' ' || i.lastname
    INTO   v_name
    FROM   instructor i
    WHERE  i.instructorid = (
        SELECT instructorid
        FROM   class
        GROUP  BY instructorid
        HAVING COUNT(*) = (
            SELECT MAX(cnt)
            FROM (
                SELECT COUNT(*) cnt
                FROM class
                GROUP BY instructorid
            )
        )
        FETCH FIRST 1 ROWS ONLY
    );

    INSERT INTO cau1 (id, name)
    VALUES (cau1seq.NEXTVAL, v_name);

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Hoan tat! Kiem tra: SELECT * FROM Cau1;');
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        DBMS_OUTPUT.PUT_LINE('Loi: Khong tim thay du lieu!');
        ROLLBACK;
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Loi: ' || SQLERRM);
        ROLLBACK;
END;
/

-- BAI 1 - Cau 2
DECLARE
    v_sid     NUMBER := &ma_sinh_vien;
    v_fname   VARCHAR2(25) := '&ho_sinh_vien';
    v_lname   VARCHAR2(25) := '&ten_sinh_vien';
    v_addr    VARCHAR2(50) := '&dia_chi';
    v_found   VARCHAR2(50);
    v_classes NUMBER;
BEGIN
-- Thu tim sinh vien theo ma vua nhap
    SELECT
        firstname
        || ' '
        || lastname
    INTO v_found
    FROM
        student
    WHERE
        studentid = v_sid;
-- Neu tim thay: dem so lop dang hoc
    SELECT
        COUNT(*)
    INTO v_classes
    FROM
        enrollment
    WHERE
        studentid = v_sid;

    dbms_output.put_line('Ho ten: ' || v_found);
    dbms_output.put_line('So lop dang hoc: ' || v_classes);
EXCEPTION
    WHEN no_data_found THEN
-- Sinh vien chua ton tai: them moi
        dbms_output.put_line('Sinh vien chua ton tai. Dang them moi...');
        INSERT INTO student (
            studentid,
            firstname,
            lastname,
            address,
            registrationdate,
            createdby,
            createddate,
            modifiedby,
            modifieddate
        ) VALUES ( v_sid,
                   v_fname,
                   v_lname,
                   v_addr,
                   sysdate,
                   user,
                   sysdate,
                   user,
                   sysdate );

        COMMIT;
        dbms_output.put_line('Da them sinh vien moi: '
                             || v_fname
                             || ' '
                             || v_lname);
END;
/

-- BAI 2 - Cau 1
DECLARE
    v_instructor_id NUMBER := &ma_giao_vien;
    v_so_lop        NUMBER;
BEGIN
-- Dem so lop giao vien dang day
    SELECT
        COUNT(*)
    INTO v_so_lop
    FROM
        class
    WHERE
        instructorid = v_instructor_id;
-- Phan nhanh theo ket qua
    IF v_so_lop >= 5 THEN
        dbms_output.put_line('Giao vien nay nen nghi ngoi!');
    ELSE
        dbms_output.put_line('So lop giao vien dang day: ' || v_so_lop);
    END IF;

EXCEPTION
    WHEN no_data_found THEN
        dbms_output.put_line('Khong tim thay giao vien co ma: ' || v_instructor_id);
END;
/


-- BAI 2 - Cau 2
DECLARE
    v_sid   NUMBER := &ma_sinh_vien;
    v_cid   NUMBER := &ma_lop;
    v_score NUMBER;
    v_grade VARCHAR2(2);
    v_check NUMBER;
BEGIN
-- Kiem tra sinh vien ton tai
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        student
    WHERE
        studentid = v_sid;

    IF v_check = 0 THEN
        dbms_output.put_line('Loi: Ma sinh vien '
                             || v_sid
                             || ' khong ton
tai!');
        RETURN;
    END IF;
-- Kiem tra lop ton tai
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        class
    WHERE
        classid = v_cid;

    IF v_check = 0 THEN
        dbms_output.put_line('Loi: Ma lop '
                             || v_cid
                             || ' khong ton tai!');
        RETURN;
    END IF;
-- Lay diem cua sinh vien trong lop
    SELECT
        finalgrade
    INTO v_score
    FROM
        enrollment
    WHERE
            studentid = v_sid
        AND classid = v_cid;
-- Quy doi diem so sang diem chu bang CASE
    CASE
        WHEN v_score >= 90 THEN
            v_grade := 'A';
        WHEN v_score >= 80 THEN
            v_grade := 'B';
        WHEN v_score >= 70 THEN
            v_grade := 'C';
        WHEN v_score >= 50 THEN
            v_grade := 'D';
        ELSE
            v_grade := 'F';
    END CASE;

    dbms_output.put_line('Diem so: '
                         || v_score
                         || ' -> Diem chu: '
                         || v_grade);
EXCEPTION
    WHEN no_data_found THEN
        dbms_output.put_line('Sinh vien chua dang ky lop nay hoac chua co
diem!');
END;
/
-- BAI 3 - Cursor
DECLARE
-- Cursor 1: Duyet tung mon hoc
    CURSOR cur_course IS
    SELECT
        courseno,
        description
    FROM
        course
    ORDER BY
        courseno;
-- Cursor 2: Lay lop hoc cua mot mon (co doi so)
    CURSOR cur_class (
        p_courseno NUMBER
    ) IS
    SELECT
        c.classno,
        COUNT(e.studentid) AS so_sv
    FROM
        class      c
        LEFT JOIN enrollment e ON c.classid = e.classid
    WHERE
        c.courseno = p_courseno
    GROUP BY
        c.classno
    ORDER BY
        c.classno;

    v_courseno course.courseno%TYPE;
    v_desc     course.description%TYPE;
    v_classno  class.classno%TYPE;
    v_count    NUMBER;
BEGIN
-- Duyet cursor ngoai: tung mon hoc
    OPEN cur_course;
    LOOP
        FETCH cur_course INTO
            v_courseno,
            v_desc;
        EXIT WHEN cur_course%notfound;
-- In ten mon hoc
        dbms_output.put_line(v_courseno
                             || ' '
                             || v_desc);
-- Mo cursor trong voi doi so la ma mon hoc hien tai
        OPEN cur_class(v_courseno);
        LOOP
            FETCH cur_class INTO
                v_classno,
                v_count;
            EXIT WHEN cur_class%notfound;
            dbms_output.put_line('Lop: '
                                 || v_classno
                                 || ' co so luong sinh vien dang ki: '
                                 || v_count);
        END LOOP;

        CLOSE cur_class;
    END LOOP;

    CLOSE cur_course;
EXCEPTION
    WHEN OTHERS THEN
        IF cur_course%isopen THEN
            CLOSE cur_course;
        END IF;
        IF cur_class%isopen THEN
            CLOSE cur_class;
        END IF;
        dbms_output.put_line('Loi: ' || sqlerrm);
END;
/

-- BAI 4 - Câu 1
CREATE OR REPLACE PROCEDURE find_sname (
    i_student_id IN student.studentid%TYPE,
    o_first_name OUT student.firstname%TYPE,
    o_last_name  OUT student.lastname%TYPE
) IS
BEGIN
    SELECT
        firstname,
        lastname
    INTO
        o_first_name,
        o_last_name
    FROM
        student
    WHERE
        studentid = i_student_id;

EXCEPTION
    WHEN no_data_found THEN
        o_first_name := NULL;
        o_last_name := NULL;
        dbms_output.put_line('Khong tim thay sinh vien ID: ' || i_student_id);
END find_sname;
/
-- Goi thu tuc de kiem tra:
DECLARE
    v_first_name student.firstname%TYPE;
    v_last_name  student.lastname%TYPE;
BEGIN
    find_sname(3001, v_first_name, v_last_name);

    DBMS_OUTPUT.PUT_LINE('First name: ' || v_first_name);
    DBMS_OUTPUT.PUT_LINE('Last name: ' || v_last_name);
END;
/

CREATE OR REPLACE PROCEDURE print_student_name (
    i_student_id IN student.studentid%TYPE
) IS
    v_first student.firstname%TYPE;
    v_last  student.lastname%TYPE;
BEGIN
-- Goi thu tuc find_sname da co san
    find_sname(i_student_id, v_first, v_last);
    IF v_first IS NOT NULL
       OR v_last IS NOT NULL THEN
        dbms_output.put_line('Ho ten sinh vien: '
                             || v_first
                             || ' '
                             || v_last);
    END IF;

END print_student_name;
/
-- Goi thu tuc de kiem tra:
BEGIN
    print_student_name(3006);
END;
/

-- BAI 4 - Câu 2
CREATE OR REPLACE PROCEDURE discount IS
BEGIN
    FOR rec IN (
        SELECT
            c.courseno,
            c.description,
            c.cost
        FROM
            course c
        WHERE
            (
                SELECT
                    COUNT(*)
                FROM
                         enrollment e
                    JOIN class cl ON e.classid = cl.classid
                WHERE
                    cl.courseno = c.courseno
            ) > 15
    ) LOOP
-- Giam gia 5%
        UPDATE course
        SET
            cost = cost * 0.95
        WHERE
            courseno = rec.courseno;

        dbms_output.put_line('Da giam gia mon hoc: '
                             || rec.description
                             || ' | Gia cu: '
                             || rec.cost
                             || ' | Gia moi: '
                             || round(rec.cost * 0.95, 2));

    END LOOP;

    COMMIT;
    dbms_output.put_line('Hoan tat giam gia.');
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        dbms_output.put_line('Loi: ' || sqlerrm);
END discount;
/
-- Goi thu tuc:
BEGIN
    discount;
END;
/



CREATE OR REPLACE FUNCTION total_cost_for_student (
    p_student_id IN student.studentid%TYPE
) RETURN NUMBER IS
    v_total NUMBER;
    v_check NUMBER;
BEGIN
-- Kiem tra sinh vien co ton tai khong
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        student
    WHERE
        studentid = p_student_id;

    IF v_check = 0 THEN
        RETURN NULL; -- Sinh vien khong ton tai
    END IF;
-- Tinh tong chi phi: sum(cost cua tung mon da dang ky)
    SELECT
        nvl(
            sum(co.cost),
            0
        )
    INTO v_total
    FROM
             enrollment e
        JOIN class  cl ON e.classid = cl.classid
        JOIN course co ON cl.courseno = co.courseno
    WHERE
        e.studentid = p_student_id;

    RETURN v_total;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END total_cost_for_student;
/
-- Goi ham de kiem tra:
SELECT
    total_cost_for_student(101) AS "Tong chi phi"
FROM
    dual;
-- Hoac trong PL/SQL:
BEGIN
    dbms_output.put_line('Tong chi phi: ' || total_cost_for_student(101));
END;
/
-- BAI 5 - Trigger
--trigger mẫu cho bảng COURSE:
CREATE OR REPLACE TRIGGER trg_course_audit BEFORE
    INSERT OR UPDATE ON course
    FOR EACH ROW
BEGIN
    IF INSERTING THEN
        :NEW.CreatedBy   := USER;
        :NEW.CreatedDate := SYSDATE;
    END IF;
-- Luon cap nhat modified (ca khi INSERT lan UPDATE)
   :NEW.ModifiedBy   := USER;
    :NEW.ModifiedDate := SYSDATE;
END trg_course_audit;
/
SHOW ERRORS TRIGGER trg_course_audit;


---Trigger tương tự cho bảng CLASS:
CREATE OR REPLACE TRIGGER trg_class_audit
    BEFORE INSERT OR UPDATE ON class
    FOR EACH ROW
BEGIN
    IF INSERTING THEN
        :NEW.CreatedBy   := USER;
        :NEW.CreatedDate := SYSDATE;
    END IF;

    :NEW.ModifiedBy   := USER;
    :NEW.ModifiedDate := SYSDATE;
END trg_class_audit;
/
SHOW ERRORS TRIGGER trg_class_audit;



---Tương tự cho STUDENT, ENROLLMENT, INSTRUCTOR, GRADE - chỉ cần đổi tên trigger và tên bảng:
-- STUDENT
CREATE OR REPLACE TRIGGER trg_student_audit
    BEFORE INSERT OR UPDATE ON student
    FOR EACH ROW
BEGIN
    IF INSERTING THEN
        :NEW.CreatedBy   := USER;
        :NEW.CreatedDate := SYSDATE;
    END IF;

    :NEW.ModifiedBy   := USER;
    :NEW.ModifiedDate := SYSDATE;
END;
/

-- ENROLLMENT
CREATE OR REPLACE TRIGGER trg_enrollment_audit
    BEFORE INSERT OR UPDATE ON enrollment
    FOR EACH ROW
BEGIN
    IF INSERTING THEN
        :NEW.CreatedBy   := USER;
        :NEW.CreatedDate := SYSDATE;
    END IF;

    :NEW.ModifiedBy   := USER;
    :NEW.ModifiedDate := SYSDATE;
END;
/

-- INSTRUCTOR
CREATE OR REPLACE TRIGGER trg_instructor_audit
    BEFORE INSERT OR UPDATE ON instructor
    FOR EACH ROW
BEGIN
    IF INSERTING THEN
        :NEW.CreatedBy   := USER;
        :NEW.CreatedDate := SYSDATE;
    END IF;

    :NEW.ModifiedBy   := USER;
    :NEW.ModifiedDate := SYSDATE;
END;
/

-- GRADE
CREATE OR REPLACE TRIGGER trg_grade_audit
    BEFORE INSERT OR UPDATE ON grade
    FOR EACH ROW
BEGIN
    IF INSERTING THEN
        :NEW.CreatedBy   := USER;
        :NEW.CreatedDate := SYSDATE;
    END IF;

    :NEW.ModifiedBy   := USER;
    :NEW.ModifiedDate := SYSDATE;
END;
/
-- Kiem tra
SELECT object_name, status
FROM user_objects
WHERE object_type = 'TRIGGER'
ORDER BY object_name;

--- Bai 5 - Cau 2
CREATE OR REPLACE TRIGGER trg_max_enrollment BEFORE
    INSERT ON enrollment
    FOR EACH ROW
DECLARE
    v_so_lop NUMBER;
BEGIN
    -- Dem so lop sinh vien nay dang dang ky
    SELECT
        COUNT(*)
    INTO v_so_lop
    FROM
        enrollment
    WHERE
        studentid = :new.studentid;

    -- Neu da co 3 lop tro len thi tu choi
    IF v_so_lop >= 3 THEN
        raise_application_error(-20001,
                                'Sinh vien '
                                || :new.studentid
                                || ' da dang ky du 3 lop! Khong the dang ky them.');
    END IF;

END trg_max_enrollment;
/
-- Kiem tra trigger:
-- Gia su sinh vien 101 da co 3 lop, thu them lop thu 4:
INSERT INTO enrollment (
    studentid,
    classid,
    enrolldate,
    createdby,
    createddate,
    modifiedby,
    modifieddate
) VALUES ( 3001,
           1007,
           sysdate,
           user,
           sysdate,
           user,
           sysdate );

-- -> Oracle se bao loi ORA-20001
--tang ung dung
SET TIMING ON;

SELECT firstname, lastname
FROM student
WHERE studentid = 3001;

-- tang stored
SET TIMING ON;

DECLARE
    v_first student.firstname%TYPE;
    v_last  student.lastname%TYPE;
BEGIN
    find_sname(3001, v_first, v_last);
    DBMS_OUTPUT.PUT_LINE(v_first || ' ' || v_last);
END;
/


----Bai tap buoi 4
---Câu 1.1: Tạo view vw_course_summary - thông tin tổng quan môn học 
CREATE OR REPLACE VIEW vw_course_summary AS
    SELECT
        co.courseno,
        co.description,
        co.cost,
        COUNT(DISTINCT cl.classid) AS so_lop,
        COUNT(e.studentid)         AS tong_sv
    FROM
        course     co
        LEFT JOIN class      cl ON co.courseno = cl.courseno
        LEFT JOIN enrollment e ON cl.classid = e.classid
    GROUP BY
        co.courseno,
        co.description,
        co.cost
    ORDER BY
        tong_sv DESC; 
-- Kiem tra view: 
SELECT
    *
FROM
    vw_course_summary;

----Câu 1.2: Tạo view vw_student_status - thông tin sinh viên và tình trạng học tập s
CREATE OR REPLACE VIEW vw_student_status AS
    SELECT
        s.studentid,
        s.firstname
        || ' '
        || s.lastname    AS ho_ten,
        COUNT(e.classid) AS so_lop_hoc,
        nvl(
            sum(co.cost),
            0
        )                AS tong_hoc_phi,
        round(
            avg(e.finalgrade),
            2
        )                AS diem_tb
    FROM
             student s
        JOIN enrollment e ON s.studentid = e.studentid
        JOIN class      cl ON e.classid = cl.classid
        JOIN course     co ON cl.courseno = co.courseno
    GROUP BY
        s.studentid,
        s.firstname,
        s.lastname
    HAVING
        COUNT(e.classid) >= 1
    ORDER BY
        s.studentid;

SELECT
    *
FROM
    vw_student_status;

---Câu 1.3: Tạo view vw_class_availability - lớp học còn chỗ trống 
CREATE OR REPLACE VIEW vw_class_availability AS
    SELECT
        cl.classid,
        cl.courseno,
        co.description,
        i.firstname
        || ' '
        || i.lastname                    AS ten_giao_vien,
        cl.capacity,
        COUNT(e.studentid)               AS so_da_dk,
        cl.capacity - COUNT(e.studentid) AS cho_trong,
        CASE
            WHEN cl.capacity - COUNT(e.studentid) > 0 THEN
                'Con cho'
            ELSE
                'Het cho'
        END                              AS trang_thai
    FROM
             class cl
        JOIN course     co ON cl.courseno = co.courseno
        JOIN instructor i ON cl.instructorid = i.instructorid
        LEFT JOIN enrollment e ON cl.classid = e.classid
    GROUP BY
        cl.classid,
        cl.courseno,
        co.description,
        i.firstname,
        i.lastname,
        cl.capacity
    HAVING
        cl.capacity - COUNT(e.studentid) > 0
    ORDER BY
        cl.classid;

SELECT
    *
FROM
    vw_class_availability;

----Câu 1.4: Tạo view vw_top_courses - chỉ đọc, top 5 môn được đăng ký nhiều nhất 
DROP VIEW vw_top_courses;
CREATE OR REPLACE VIEW vw_top_courses AS
    SELECT
        courseno,
        description,
        cost,
        tong_dk,
        hang
    FROM
        (
            SELECT
                co.courseno,
                co.description,
                co.cost,
                COUNT(e.studentid) AS tong_dk,
                RANK()
                OVER(
                    ORDER BY
                        COUNT(e.studentid) DESC
                )                  AS hang
            FROM
                course     co
                LEFT JOIN class      cl ON co.courseno = cl.courseno
                LEFT JOIN enrollment e ON cl.classid = e.classid
            GROUP BY
                co.courseno,
                co.description,
                co.cost
        )
    WHERE
        hang <= 5
WITH READ ONLY;

SELECT
    *
FROM
    vw_top_courses; 
-- Thu INSERT vao view nay (se bao loi ORA-42399): 
INSERT INTO vw_top_courses (
    courseno,
    description,
    cost
) VALUES ( 999,
           'Test',
           100 ); 
-- Oracle bao: ORA-42399: cannot perform a DML operation on a read-only  view 
---Câu 1.5: Tạo view vw_pending_enrollment với WITH CHECK OPTION và kiểm  tra
DROP VIEW vw_pending_enrollment
CREATE OR REPLACE VIEW vw_pending_enrollment AS
    SELECT
        studentid,
        classid,
        enrolldate,
        finalgrade,
        createdby,
        createddate,
        modifiedby,
        modifieddate
    FROM
        enrollment
    WHERE
        finalgrade IS NULL
WITH CHECK OPTION;

SELECT
    *
FROM
    vw_pending_enrollment; 
-- INSERT 1: FinalGrade = NULL -> THANH CONG (thoa dieu kien  WHERE) 
INSERT INTO vw_pending_enrollment (
    studentid,
    classid,
    enrolldate,
    createdby,
    createddate,
    modifiedby,
    modifieddate
) VALUES ( 3001,
           1008,
           sysdate,
           user,
           sysdate,
           user,
           sysdate );
-- INSERT 2: FinalGrade = 85 -> LOI ORA-01402 (vi pham WITH CHECK  OPTION) 
INSERT INTO vw_pending_enrollment (
    studentid,
    classid,
    enrolldate,
    finalgrade,
    createdby,
    createddate,
    modifiedby,
    modifieddate
) VALUES ( 3002,
           1008,
           sysdate,
           85,
           user,
           sysdate,
           user,
           sysdate ); -- ORA-01402: view WITH CHECK OPTION where-clause violation 
----PHẦN 3: HƯỚNG DẪN BÀI 2 - STORED PROCEDURE 
---Câu 2.1: Thủ tục enroll_student - đăng ký sinh viên vào lớp học 
CREATE OR REPLACE PROCEDURE enroll_student (
    p_studentid IN NUMBER,
    p_classid   IN NUMBER
) IS
    v_check    NUMBER;
    v_capacity NUMBER;
    v_enrolled NUMBER;
BEGIN 
 -- DK1: Sinh vien phai ton tai 
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        student
    WHERE
        studentid = p_studentid;

    IF v_check = 0 THEN
        dbms_output.put_line('[LOI] Sinh vien '
                             || p_studentid
                             || ' khong  ton tai!');
        RETURN;
    END IF; 
 -- DK2: Lop hoc phai ton tai 
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        class
    WHERE
        classid = p_classid;

    IF v_check = 0 THEN
        dbms_output.put_line('[LOI] Lop hoc '
                             || p_classid
                             || ' khong ton  tai!');
        RETURN;
    END IF;
 -- DK3: Kiem tra con cho trong 
    SELECT
        capacity
    INTO v_capacity
    FROM
        class
    WHERE
        classid = p_classid;

    SELECT
        COUNT(*)
    INTO v_enrolled
    FROM
        enrollment
    WHERE
        classid = p_classid;

    IF v_enrolled >= v_capacity THEN
        dbms_output.put_line('[LOI] Lop '
                             || p_classid
                             || ' da day! ('
                             || v_enrolled
                             || '/'
                             || v_capacity
                             || ')');

        RETURN;
    END IF; 
 -- DK4: Sinh vien chua dang ky lop nay 
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        enrollment
    WHERE
            studentid = p_studentid
        AND classid = p_classid;

    IF v_check > 0 THEN
        dbms_output.put_line('[LOI] Sinh vien da dang ky lop nay roi!');
        RETURN;
    END IF; 
 -- DK5: Sinh vien chua qua 3 lop 
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        enrollment
    WHERE
        studentid = p_studentid;

    IF v_check >= 3 THEN
        dbms_output.put_line('[LOI] Sinh vien da dang ky du 3 lop!');
        RETURN;
    END IF; 
 -- Tat ca OK: INSERT 
    INSERT INTO enrollment (
        studentid,
        classid,
        enrolldate,
        createdby,
        createddate,
        modifiedby,
        modifieddate
    ) VALUES ( p_studentid,
               p_classid,
               sysdate,
               user,
               sysdate,
               user,
               sysdate );

    COMMIT;
    dbms_output.put_line('[OK] Dang ky thanh cong! SV '
                         || p_studentid
                         || ' -> Lop '
                         || p_classid);
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        dbms_output.put_line('[LOI HE THONG] ' || sqlerrm);
END enroll_student;
/ 
-- Kiem tra: 
BEGIN
    enroll_student(3003, 1010); -- hợp lệ
    enroll_student(999, 1010);  -- SV không tồn tại
    enroll_student(3003, 999);  -- lớp không tồn tại
END;
/


---Câu 2.2: Thủ tục update_final_grade - cập nhật điểm tổng kết 

CREATE OR REPLACE PROCEDURE update_final_grade (
    p_studentid IN NUMBER,
    p_classid   IN NUMBER,
    p_grade     IN NUMBER
) IS
    v_check     NUMBER;
    v_old_grade NUMBER;
BEGIN 
    -- Kiem tra diem hop le 
    IF p_grade < 0 OR p_grade > 100 THEN
        dbms_output.put_line('[LOI] Diem khong hop le! Phai tu 0 den 100.');
        RETURN;
    END IF; 

    -- Kiem tra cap ton tai
    SELECT COUNT(*) 
    INTO v_check 
    FROM enrollment
    WHERE studentid = p_studentid 
      AND classid = p_classid;

    IF v_check = 0 THEN
        dbms_output.put_line('[LOI] Sinh vien chua dang ky lop nay!');
        RETURN;
    END IF; 

    -- Luu diem cu 
    SELECT finalgrade
    INTO v_old_grade
    FROM enrollment
    WHERE studentid = p_studentid
      AND classid = p_classid;

    -- Cap nhat ENROLLMENT 
    UPDATE enrollment
    SET finalgrade = p_grade,
        modifiedby = user,
        modifieddate = sysdate
    WHERE studentid = p_studentid
      AND classid = p_classid; 

    -- Dong bo sang GRADE
    MERGE INTO grade g
    USING (
        SELECT p_studentid AS sid,
               p_classid   AS cid
        FROM dual
    ) src
    ON (g.studentid = src.sid AND g.classid = src.cid)

    WHEN MATCHED THEN 
        UPDATE SET g.grade = p_grade,
                   g.modifiedby = user,
                   g.modifieddate = sysdate

    WHEN NOT MATCHED THEN
        INSERT (studentid, classid, grade, createdby, createddate, modifiedby, modifieddate)
        VALUES (p_studentid, p_classid, p_grade, user, sysdate, user, sysdate);

    COMMIT;

    dbms_output.put_line('[OK] Da cap nhat diem SV '
        || p_studentid || ' lop ' || p_classid
        || ': Cu=' || NVL(TO_CHAR(v_old_grade),'NULL')
        || ' -> Moi=' || p_grade);

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        dbms_output.put_line('[LOI] ' || SQLERRM);
END update_final_grade;
/

----Câu 2.3: Thủ tục transfer_student - chuyển lớp cho sinh viên 
CREATE OR REPLACE PROCEDURE transfer_student (
    p_studentid   IN NUMBER,
    p_old_classid IN NUMBER,
    p_new_classid IN NUMBER
) IS
    v_check    NUMBER;
    v_capacity NUMBER;
    v_enrolled NUMBER;
BEGIN 
 -- DK1: Sinh vien dang hoc o lop cu 
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        enrollment
    WHERE
            studentid = p_studentid
        AND classid = p_old_classid;

    IF v_check = 0 THEN
        dbms_output.put_line('[LOI] Sinh vien khong dang hoc lop ' || p_old_classid);
        RETURN;
    END IF; 
 -- DK2: Lop moi con cho trong 
    SELECT
        capacity
    INTO v_capacity
    FROM
        class
    WHERE
        classid = p_new_classid;

    SELECT
        COUNT(*)
    INTO v_enrolled
    FROM
        enrollment
    WHERE
        classid = p_new_classid;

    IF v_enrolled >= v_capacity THEN
        dbms_output.put_line('[LOI] Lop moi '
                             || p_new_classid
                             || ' da  day!');
        RETURN;
    END IF;
 -- DK3: Sinh vien chua dang ky lop moi 
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        enrollment
    WHERE
            studentid = p_studentid
        AND classid = p_new_classid;

    IF v_check > 0 THEN
        dbms_output.put_line('[LOI] Sinh vien da o trong lop moi roi!');
        RETURN;
    END IF; 
 -- Tat ca OK: thuc hien chuyen lop 
    SAVEPOINT sp_truoc_chuyen; 
 -- Buoc 1: Xoa khoi lop cu 
    DELETE FROM enrollment
    WHERE
            studentid = p_studentid
        AND classid = p_old_classid;

    SAVEPOINT sp_sau_xoa; 
 -- Buoc 2: Them vao lop moi 
    INSERT INTO enrollment (
        studentid,
        classid,
        enrolldate,
        createdby,
        createddate,
        modifiedby,
        modifieddate
    ) VALUES ( p_studentid,
               p_new_classid,
               sysdate,
               user,
               sysdate,
               user,
               sysdate );

    COMMIT;
    dbms_output.put_line('[OK] Da chuyen SV '
                         || p_studentid
                         || ' tu lop '
                         || p_old_classid
                         || ' sang lop '
                         || p_new_classid);

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK TO sp_truoc_chuyen;
        dbms_output.put_line('[LOI] Chuyen lop that bai: ' || sqlerrm);
        dbms_output.put_line('Da rollback ve trang thai ban dau.');
END transfer_student;
/

---Câu 2.4: Thủ tục report_class_detail — in báo cáo chi tiết lớp học 
DROP PROCEDURE report_class_detail
CREATE OR REPLACE PROCEDURE report_class_detail (
    p_classid IN NUMBER
) IS
    v_check     NUMBER;
    v_course    VARCHAR2(50);
    v_courseno  NUMBER;
    v_gv        VARCHAR2(50);
    v_loc       VARCHAR2(50);
    v_cap       NUMBER;
    v_stt       NUMBER := 0;
    v_tong      NUMBER := 0;
    v_sum_d     NUMBER := 0;
    v_co_d      NUMBER := 0;
    v_grade_txt VARCHAR2(15);
BEGIN

    SELECT COUNT(*) INTO v_check
    FROM class
    WHERE classid = p_classid;

    IF v_check = 0 THEN
        dbms_output.put_line('Lop hoc ' || p_classid || ' khong ton tai!');
        RETURN;
    END IF;

    SELECT
        co.description,
        co.courseno,
        i.firstname || ' ' || i.lastname,
        cl.location,
        cl.capacity
    INTO
        v_course,
        v_courseno,
        v_gv,
        v_loc,
        v_cap
    FROM class cl
    JOIN course co ON cl.courseno = co.courseno
    JOIN instructor i ON cl.instructorid = i.instructorid
    WHERE cl.classid = p_classid;

    dbms_output.put_line('=== BAO CAO LOP HOC: ' || p_classid || ' ===');
    dbms_output.put_line('Mon hoc : ' || v_courseno || ' - ' || v_course);
    dbms_output.put_line('Giao vien: ' || v_gv);
    dbms_output.put_line('Phong hoc: ' || NVL(v_loc, 'Chua xep phong'));
    dbms_output.put_line('Suc chua : ' || v_cap || ' cho');
    dbms_output.put_line(RPAD('-', 50, '-'));

    FOR rec IN (
        SELECT
            s.firstname || ' ' || s.lastname AS ho_ten,
            e.finalgrade AS finalgrade
        FROM enrollment e
        JOIN student s ON e.studentid = s.studentid
        WHERE e.classid = p_classid
        ORDER BY s.lastname, s.firstname
    ) LOOP

        v_stt := v_stt + 1;
        v_tong := v_tong + 1;

        IF rec.finalgrade IS NULL THEN
            v_grade_txt := 'Chua co diem';
        ELSIF rec.finalgrade >= 90 THEN
            v_grade_txt := 'A';
        ELSIF rec.finalgrade >= 80 THEN
            v_grade_txt := 'B';
        ELSIF rec.finalgrade >= 70 THEN
            v_grade_txt := 'C';
        ELSIF rec.finalgrade >= 50 THEN
            v_grade_txt := 'D';
        ELSE
            v_grade_txt := 'F';
        END IF;

        IF rec.finalgrade IS NOT NULL THEN
            v_sum_d := v_sum_d + rec.finalgrade;
            v_co_d := v_co_d + 1;
        END IF;

        dbms_output.put_line(
            LPAD(v_stt, 3) || ' | ' ||
            RPAD(rec.ho_ten, 20) || ' | ' ||
            LPAD(NVL(TO_CHAR(rec.finalgrade), 'NULL'), 7) || ' | ' ||
            v_grade_txt
        );

    END LOOP;

    dbms_output.put_line(RPAD('-', 50, '-'));
    dbms_output.put_line('Tong so sinh vien : ' || v_tong);

    IF v_co_d > 0 THEN
        dbms_output.put_line('Diem trung binh lop: ' || ROUND(v_sum_d / v_co_d, 2));
    ELSE
        dbms_output.put_line('Diem trung binh lop: Chua co diem');
    END IF;

END;
/
BEGIN
    report_class_detail(1001);
END;
/
----Câu 2.5: Thủ tục sync_grade_from_enrollment - đồng bộ điểm từ ENROLLMENT  sang GRADE
CREATE OR REPLACE PROCEDURE sync_grade_from_enrollment IS
    v_check      NUMBER;
    v_dem_insert NUMBER := 0;
    v_dem_update NUMBER := 0;
BEGIN
    FOR rec IN (
        SELECT
            studentid,
            classid,
            finalgrade
        FROM
            enrollment
        WHERE
            finalgrade IS NOT NULL
    ) LOOP 
 -- Kiem tra trong GRADE da co chua 
        SELECT
            COUNT(*)
        INTO v_check
        FROM
            grade
        WHERE
                studentid = rec.studentid
            AND classid = rec.classid;

        IF v_check = 0 THEN 
 -- Chua co -> INSERT moi 
            INSERT INTO grade (
                studentid,
                classid,
                grade,
                createdby,
                createddate,
                modifiedby,
                modifieddate
            ) VALUES ( rec.studentid,
                       rec.classid,
                       rec.finalgrade,
                       user,
                       sysdate,
                       user,
                       sysdate );

            v_dem_insert := v_dem_insert + 1;
        ELSE 
 -- Da co -> UPDATE 
            UPDATE grade
            SET
                grade = rec.finalgrade,
                modifiedby = user,
                modifieddate = sysdate
            WHERE
                    studentid = rec.studentid
                AND classid = rec.classid;

            v_dem_update := v_dem_update + 1;
        END IF;

    END LOOP;

    COMMIT;
    dbms_output.put_line('[OK] Dong bo hoan tat!');
    dbms_output.put_line(' So ban ghi INSERT moi : ' || v_dem_insert);
    dbms_output.put_line(' So ban ghi UPDATE : ' || v_dem_update);
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        dbms_output.put_line('[LOI] ' || sqlerrm);
END sync_grade_from_enrollment;
/

BEGIN
    sync_grade_from_enrollment;
END;
/
---PHẦN 4: HƯỚNG DẪN BÀI 3 - TRIGGER 
--Câu 3.1: Trigger trg_check_capacity - kiểm tra sức chứa khi đăng ký
CREATE OR REPLACE TRIGGER trg_check_capacity BEFORE
    INSERT ON enrollment
    FOR EACH ROW
DECLARE
    v_capacity NUMBER;
    v_enrolled NUMBER;
BEGIN 
 -- Lay suc chua lop hoc 
    SELECT
        capacity
    INTO v_capacity
    FROM
        class
    WHERE
        classid = :new.classid; 
 -- Dem so SV hien da dang ky 
    SELECT
        COUNT(*)
    INTO v_enrolled
    FROM
        enrollment
    WHERE
        classid = :new.classid; 
 -- Tu choi neu lop da day 
    IF v_enrolled >= v_capacity THEN
        raise_application_error(-20010,
                                'LOI: Lop '
                                || :new.classid
                                || ' da day! ('
                                || v_enrolled
                                || '/'
                                || v_capacity
                                || ' cho)');
    END IF;

END trg_check_capacity;
/
INSERT INTO enrollment (
    studentid,
    classid,
    enrolldate,
    createdby,
    createddate,
    modifiedby,
    modifieddate
) VALUES ( 3001,
           1001,
           sysdate,
           user,
           sysdate,
           user,
           sysdate );
----Câu 3.2: Trigger trg_grade_audit_log - ghi nhật ký thay đổi điểm 
CREATE TABLE grade_audit_log (
    log_id    NUMBER
        GENERATED ALWAYS AS IDENTITY,
    studentid NUMBER(8),
    classid   NUMBER(8),
    grade_cu  NUMBER(3),
    grade_moi NUMBER(3),
    nguoi_sua VARCHAR2(30),
    thoi_gian DATE
); 
/
CREATE OR REPLACE TRIGGER trg_grade_audit_log AFTER
    UPDATE OF finalgrade ON enrollment
    FOR EACH ROW
BEGIN 
 -- Chi ghi log khi diem THUC SU thay doi 
    IF (
        :old.finalgrade IS NULL
        AND :new.finalgrade IS NOT NULL
    )
    OR ( :old.finalgrade IS NOT NULL
         AND :new.finalgrade IS NULL )
       OR ( :old.finalgrade != :new.finalgrade ) THEN
        INSERT INTO grade_audit_log (
            studentid,
            classid,
            grade_cu,
            grade_moi,
            nguoi_sua,
            thoi_gian
        ) VALUES ( :old.studentid,
                   :old.classid,
                   :old.finalgrade,
                   :new.finalgrade,
                   user,
                   sysdate );

    END IF;
END trg_grade_audit_log;
/ 
-- Kiem tra trigger: 
UPDATE enrollment
SET
    finalgrade = 85
WHERE
        studentid = 3003
    AND classid = 1007;

COMMIT;
SELECT
    *
FROM
    grade_audit_log; 

---Câu 3.3: Trigger trg_prevent_course_delete - ngăn xóa môn học đang có lớp
CREATE OR REPLACE TRIGGER trg_prevent_course_delete BEFORE
    DELETE ON course
    FOR EACH ROW
DECLARE
    v_so_lop NUMBER;
BEGIN
    SELECT
        COUNT(*)
    INTO v_so_lop
    FROM
        class
    WHERE
        courseno = :old.courseno;

    IF v_so_lop > 0 THEN
        raise_application_error(-20020,
                                'Khong the xoa mon hoc '
                                || :old.courseno
                                || ' ('
                                || :old.description
                                || ') '
                                || 'vi con '
                                || v_so_lop
                                || ' lop hoc dang ton tai!');

    END IF;

END trg_prevent_course_delete;
/
-- Kiem tra: xoa mon co lop (se bao loi) 
DELETE FROM course WHERE courseno = 101;
-- Kiem tra: xoa mon khong co lop (thanh cong) 
INSERT INTO course (courseno, description, cost, createdby, createddate, modifiedby, modifieddate)
VALUES (999, 'Test', 1000, USER, SYSDATE, USER, SYSDATE);
DELETE FROM course WHERE courseno = 999;
ROLLBACK;
---Câu 3.4: Trigger trg_update_grade_summary - cập nhật bảng thống kê tự động 
CREATE TABLE class_grade_summary (
    classid        NUMBER(8) PRIMARY KEY,
    so_sv          NUMBER,
    diem_tb        NUMBER(5, 2),
    diem_cao_nhat  NUMBER(3),
    diem_thap_nhat NUMBER(3),
    cap_nhat_luc   DATE
); 
/ 

CREATE OR REPLACE TRIGGER trg_update_grade_summary FOR
    INSERT OR UPDATE OR DELETE ON enrollment
COMPOUND TRIGGER

    -- Lưu danh sách class bị ảnh hưởng
    TYPE t_classids IS
        TABLE OF NUMBER INDEX BY PLS_INTEGER;
    v_classids t_classids;
    v_count    NUMBER := 0;
    AFTER EACH ROW IS BEGIN
        v_count := v_count + 1;
        IF inserting
        OR updating THEN
            v_classids(v_count) := :new.classid;
        ELSE
            v_classids(v_count) := :old.classid;
        END IF;

    END AFTER EACH ROW;
    AFTER STATEMENT IS
        v_so_sv   NUMBER;
        v_diem_tb NUMBER;
        v_max_d   NUMBER;
        v_min_d   NUMBER;
    BEGIN
        FOR i IN 1..v_count LOOP
            SELECT
                COUNT(finalgrade),
                round(
                    avg(finalgrade),
                    2
                ),
                MAX(finalgrade),
                MIN(finalgrade)
            INTO
                v_so_sv,
                v_diem_tb,
                v_max_d,
                v_min_d
            FROM
                enrollment
            WHERE
                classid = v_classids(i);

            MERGE INTO class_grade_summary cgs
            USING (
                SELECT
                    v_classids(i) AS cid
                FROM
                    dual
            ) src ON ( cgs.classid = src.cid )
            WHEN MATCHED THEN UPDATE
            SET so_sv = v_so_sv,
                diem_tb = v_diem_tb,
                diem_cao_nhat = v_max_d,
                diem_thap_nhat = v_min_d,
                cap_nhat_luc = sysdate
            WHEN NOT MATCHED THEN
            INSERT (
                classid,
                so_sv,
                diem_tb,
                diem_cao_nhat,
                diem_thap_nhat,
                cap_nhat_luc )
            VALUES
                ( v_classids(i),
                  v_so_sv,
                  v_diem_tb,
                  v_max_d,
                  v_min_d,
                  sysdate );

        END LOOP;
    END AFTER STATEMENT;
END trg_update_grade_summary;
/
-- Kiem tra trigger: 
UPDATE enrollment
SET
    finalgrade = 95
WHERE
        studentid = 3001
    AND classid = 1001;

COMMIT;

SELECT
    *
FROM
    class_grade_summary
WHERE
    classid = 1001;

-----PHẦN 5: HƯỚNG DẪN BÀI 4 - TỔNG HỢP 
-----Câu 4.1: Hệ thống báo cáo hoàn chỉnh - View + Procedure + Cursor 
--Bước 1: Tạo view vw_instructor_workload: 
CREATE OR REPLACE VIEW vw_instructor_workload AS
    SELECT
        i.instructorid,
        i.firstname
        || ' '
        || i.lastname              AS ho_ten,
        COUNT(DISTINCT cl.classid) AS so_lop,
        COUNT(e.studentid)         AS tong_sv,
        round(
            avg(e.finalgrade),
            2
        )                          AS diem_tb_chung,
        CASE
            WHEN COUNT(DISTINCT cl.classid) >= 3 THEN
                'Ban nhieu'
            WHEN COUNT(DISTINCT cl.classid) = 2  THEN
                'Binh thuong'
            ELSE
                'Nhe nhang'
        END                        AS muc_ban
    FROM
        instructor i
        LEFT JOIN class      cl ON i.instructorid = cl.instructorid
        LEFT JOIN enrollment e ON cl.classid = e.classid
    GROUP BY
        i.instructorid,
        i.firstname,
        i.lastname
    ORDER BY
        so_lop DESC;

SELECT
    *
FROM
    vw_instructor_workload;
--Bước 2: Thủ tục print_system_report: 
CREATE OR REPLACE PROCEDURE print_system_report IS
    v_so_mon NUMBER;
    v_so_lop NUMBER;
    v_so_sv  NUMBER;
    v_so_gv  NUMBER;
BEGIN 
 -- Lay so lieu tong the 
 SELECT COUNT(*) INTO v_so_mon FROM course; 
 SELECT COUNT(*) INTO v_so_lop FROM class; 
 SELECT COUNT(*) INTO v_so_sv FROM student; 
 SELECT COUNT(*) INTO v_so_gv FROM instructor; 
 -- In header 
  
dbms_output.put_line('================================== ==========');

dbms_output.put_line(' BAO CAO TOAN HE THONG QUAN LY  KHOA HOC');

dbms_output.put_line('================================== ==========');

dbms_output.put_line('Tong so mon hoc : ' || v_so_mon);

dbms_output.put_line('Tong so lop hoc : ' || v_so_lop);

dbms_output.put_line('Tong so sinh vien: ' || v_so_sv);

dbms_output.put_line('Tong so giao vien: ' || v_so_gv);

dbms_output.put_line(rpad('-', 50, '-'));
 -- Phan 1: Thong ke giao vien (dung view vw_instructor_workload)  
 dbms_output.put_line('THONG KE GIAO VIEN:');

FOR rec IN (
    SELECT
        *
    FROM
        vw_instructor_workload
) LOOP
    dbms_output.put_line(' '
                         || rpad(rec.ho_ten, 25)
                         || ' | '
                         || lpad(rec.so_lop, 2)
                         || ' lop'
                         || ' | '
                         || lpad(rec.tong_sv, 3)
                         || ' SV'
                         || ' | DTB: '
                         || nvl(
        to_char(rec.diem_tb_chung),
        '--'
    )
                         || ' | '
                         || rec.muc_ban);
END LOOP;

dbms_output.put_line(rpad('-', 50, '-'));
 -- Phan 2: Top 3 mon hoc (dung view vw_top_courses) 
dbms_output.put_line('TOP 3 MON HOC DUOC DANG KY  NHIEU NHAT:');

FOR rec IN (
    SELECT
        *
    FROM
        vw_top_courses
    WHERE
        hang <= 3
) LOOP
    dbms_output.put_line(' '
                         || rec.hang
                         || '. '
                         || rpad(rec.description, 30)
                         || ' - '
                         || rec.tong_dk
                         || ' luot dang ky');
END LOOP;

dbms_output.put_line('================================== ==========');

END PRINT_SYSTEM_REPORT ; 
/ 
-- Chay bao cao: 
SET SERVEROUTPUT ON SIZE 1000000;

BEGIN
    print_system_report;
END;
/


-------------Buoi 5----------------------------------------------------------------------------
--View
---Cau1.1
CREATE OR REPLACE VIEW vw_prerequisite_check AS
    SELECT
        s.studentid,
        s.firstname
        || ' '
        || s.lastname  AS ho_ten,
        co.description AS ten_mon,
        co.courseno,
        tq.description AS ten_mon_tq,
        tq.courseno    AS courseno_tq
    FROM
             enrollment e
        JOIN student s ON e.studentid = s.studentid
        JOIN class   cl ON e.classid = cl.classid
        JOIN course  co ON cl.courseno = co.courseno
        JOIN course  tq ON co.prerequisite = tq.courseno
    WHERE
        co.prerequisite IS NOT NULL
        AND NOT EXISTS (
            SELECT
                1
            FROM
                     enrollment e2
                JOIN class cl2 ON e2.classid = cl2.classid
            WHERE
                    e2.studentid = s.studentid
                AND cl2.courseno = co.prerequisite
                AND e2.finalgrade IS NOT NULL
        );

-- Dem truong hop hoc vuot theo tung mon:
SELECT
    ten_mon,
    courseno,
    COUNT(*) AS so_sv_hoc_vuot
FROM
    vw_prerequisite_check
GROUP BY
    ten_mon,
    courseno
ORDER BY
    so_sv_hoc_vuot DESC;
----Cau1.2
CREATE OR REPLACE VIEW vw_instructor_performance AS
    SELECT
        instructorid,
        ho_ten,
        so_lop,
        tong_sv,
        sv_co_diem,
        diem_tb,
        diem_max,
        diem_min,
        round(sv_dat * 100 / nullif(sv_co_diem, 0),
              1) AS ty_le_dat_pct,
        DENSE_RANK()
        OVER(
            ORDER BY
                diem_tb DESC NULLS LAST
        )        AS hang_diem_tb,
        RANK()
        OVER(
            ORDER BY
                tong_sv DESC
        )        AS hang_so_sv
    FROM
        (
            SELECT
                i.instructorid,
                i.firstname
                || ' '
                || i.lastname              AS ho_ten,
                COUNT(DISTINCT cl.classid) AS so_lop,
                COUNT(e.studentid)         AS tong_sv,
                COUNT(e.finalgrade)        AS sv_co_diem,
                round(
                    avg(e.finalgrade),
                    2
                )                          AS diem_tb,
                MAX(e.finalgrade)          AS diem_max,
                MIN(e.finalgrade)          AS diem_min,
                SUM(
                    CASE
                        WHEN e.finalgrade >= 50 THEN
                            1
                        ELSE
                            0
                    END
                )                          AS sv_dat
            FROM
                instructor i
                LEFT JOIN class      cl ON i.instructorid = cl.instructorid
                LEFT JOIN enrollment e ON cl.classid = e.classid
            GROUP BY
                i.instructorid,
                i.firstname,
                i.lastname
        );

-- Top 3 giao vien ty le SV dat cao nhat:
SELECT
    ho_ten,
    ty_le_dat_pct,
    sv_co_diem,
    diem_tb
FROM
    vw_instructor_performance
WHERE
    hang_diem_tb <= 3
ORDER BY
    hang_diem_tb;
------Cau1.3
CREATE OR REPLACE VIEW vw_monthly_enrollment_stats AS
    SELECT
        nam,
        thang,
        so_dang_ky,
        so_sv_moi,
        so_mon,
        diem_tb_thang,
        SUM(so_dang_ky)
        OVER(
            ORDER BY
                nam, thang
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS luy_ke_dang_ky
    FROM
        (
            SELECT
                to_char(e.enrolldate, 'YYYY') AS nam,
                to_char(e.enrolldate, 'MM')   AS thang,
                COUNT(*)                      AS so_dang_ky,
                COUNT(DISTINCT e.studentid)   AS so_sv_moi,
                COUNT(DISTINCT cl.courseno)   AS so_mon,
                round(
                    avg(e.finalgrade),
                    2
                )                             AS diem_tb_thang
            FROM
                     enrollment e
                JOIN class cl ON e.classid = cl.classid
            GROUP BY
                to_char(e.enrolldate, 'YYYY'),
                to_char(e.enrolldate, 'MM')
        )
    ORDER BY
        nam DESC,
        thang ASC;

SELECT
    *
FROM
    vw_monthly_enrollment_stats;
----Cau1.4
--Bước 1 - Tạo view:
CREATE OR REPLACE VIEW vw_enrollment_full AS
    SELECT
        e.studentid,
        e.classid,
        e.enrolldate,
        e.finalgrade,
        s.firstname
        || ' '
        || s.lastname  AS ten_sv,
        co.description AS ten_mon,
        i.firstname
        || ' '
        || i.lastname  AS ten_gv
    FROM
             enrollment e
        JOIN student    s ON e.studentid = s.studentid
        JOIN class      cl ON e.classid = cl.classid
        JOIN course     co ON cl.courseno = co.courseno
        JOIN instructor i ON cl.instructorid = i.instructorid;
--Bước 2 - INSTEAD OF INSERT trigger:
CREATE OR REPLACE TRIGGER trg_iot_enrollment_full INSTEAD OF
    INSERT ON vw_enrollment_full
    FOR EACH ROW
DECLARE
    v_sv_check NUMBER;
    v_cl_check NUMBER;
    v_capacity NUMBER;
    v_enrolled NUMBER;
BEGIN
    SELECT
        COUNT(*)
    INTO v_sv_check
    FROM
        student
    WHERE
        studentid = :new.studentid;

    IF v_sv_check = 0 THEN
        raise_application_error(-20050, 'Sinh vien khong ton tai!');
        RETURN;
    END IF;
    SELECT
        COUNT(*)
    INTO v_cl_check
    FROM
        class
    WHERE
        classid = :new.classid;

    IF v_cl_check = 0 THEN
        raise_application_error(-20051, 'Lop hoc khong ton tai!');
        RETURN;
    END IF;
    SELECT
        capacity
    INTO v_capacity
    FROM
        class
    WHERE
        classid = :new.classid;

    SELECT
        COUNT(*)
    INTO v_enrolled
    FROM
        enrollment
    WHERE
        classid = :new.classid;

    IF v_enrolled >= v_capacity THEN
        raise_application_error(-20052, 'Lop da day!');
        RETURN;
    END IF;

    INSERT INTO enrollment (
        studentid,
        classid,
        enrolldate,
        createdby,
        createddate,
        modifiedby,
        modifieddate
    ) VALUES ( :new.studentid,
               :new.classid,
               nvl(:new.enrolldate,
                   sysdate),
               user,
               sysdate,
               user,
               sysdate );

    dbms_output.put_line('[OK] Da dang ky: SV '
                         || :new.studentid
                         || ' -> Lop
'
                         || :new.classid);

END trg_iot_enrollment_full;
/

-- Kiem tra INSERT qua view:
INSERT INTO vw_enrollment_full (
    studentid,
    classid
) VALUES ( 3004,
           1008 );

COMMIT;
---Cau1.5
CREATE OR REPLACE VIEW vw_grade_distribution AS
    SELECT
        classid,
        courseno,
        description,
        sv_a,
        sv_b,
        sv_c,
        sv_d,
        sv_f,
        sv_chua_co,
        p25,
        p50_median,
        p75,
        round(std_dev, 2) AS do_lech_chuan,
        round(std_dev / nullif(diem_tb, 0) * 100,
              2)          AS he_so_bt
    FROM
        (
            SELECT
                cl.classid,
                cl.courseno,
                co.description,
                SUM(
                    CASE
                        WHEN e.finalgrade >= 90 THEN
                            1
                        ELSE
                            0
                    END
                )                    AS sv_a,
                SUM(
                    CASE
                        WHEN e.finalgrade >= 80
                             AND e.finalgrade < 90 THEN
                            1
                        ELSE
                            0
                    END
                )                    AS sv_b,
                SUM(
                    CASE
                        WHEN e.finalgrade >= 70
                             AND e.finalgrade < 80 THEN
                            1
                        ELSE
                            0
                    END
                )                    AS sv_c,
                SUM(
                    CASE
                        WHEN e.finalgrade >= 50
                             AND e.finalgrade < 70 THEN
                            1
                        ELSE
                            0
                    END
                )                    AS sv_d,
                SUM(
                    CASE
                        WHEN e.finalgrade < 50
                             AND e.finalgrade IS NOT NULL THEN
                            1
                        ELSE
                            0
                    END
                )                    AS sv_f,
                SUM(
                    CASE
                        WHEN e.finalgrade IS NULL THEN
                            1
                        ELSE
                            0
                    END
                )                    AS sv_chua_co,
                PERCENTILE_CONT(0.25) WITHIN GROUP(
                    ORDER BY
                        e.finalgrade
                )                    AS p25,
                PERCENTILE_CONT(0.50) WITHIN GROUP(
                    ORDER BY
                        e.finalgrade
                )                    AS p50_median,
                PERCENTILE_CONT(0.75) WITHIN GROUP(
                    ORDER BY
                        e.finalgrade
                )                    AS p75,
                STDDEV(e.finalgrade) AS std_dev,
                AVG(e.finalgrade)    AS diem_tb
            FROM
                     class cl
                JOIN course     co ON cl.courseno = co.courseno
                LEFT JOIN enrollment e ON cl.classid = e.classid
            GROUP BY
                cl.classid,
                cl.courseno,
                co.description
            HAVING
                COUNT(e.finalgrade) >= 2
        );

SELECT
    *
FROM
    vw_grade_distribution
ORDER BY
    classid;
---Cau1.6
CREATE OR REPLACE VIEW vw_student_grade_pivot AS
    SELECT
        studentid,
        ho_ten,
        MAX(
            CASE
                WHEN classid = 1 THEN
                    finalgrade
            END
        )              AS diem_lop_1,
        MAX(
            CASE
                WHEN classid = 2 THEN
                    finalgrade
            END
        )              AS diem_lop_2,
        MAX(
            CASE
                WHEN classid = 3 THEN
                    finalgrade
            END
        )              AS diem_lop_3,
        MAX(
            CASE
                WHEN classid = 4 THEN
                    finalgrade
            END
        )              AS diem_lop_4,
        round(
            avg(finalgrade),
            2
        )              AS diem_tb_chung,
        COUNT(classid) AS tong_lop
    FROM
        (
            SELECT
                e.studentid,
                s.firstname
                || ' '
                || s.lastname AS ho_ten,
                e.classid,
                e.finalgrade
            FROM
                     enrollment e
                JOIN student s ON e.studentid = s.studentid
        )
    GROUP BY
        studentid,
        ho_ten
    ORDER BY
        studentid;

SELECT
    *
FROM
    vw_student_grade_pivot;
-- Cach 2: Dung menh de PIVOT (Oracle 11g+)
SELECT
    *
FROM
    (
        SELECT
            e.studentid,
            e.classid,
            e.finalgrade
        FROM
            enrollment e
    ) PIVOT (
        MAX(finalgrade)
        FOR classid
        IN ( 1 AS diem_lop_1, 2 AS diem_lop_2, 3 AS diem_lop_3, 4 AS diem_lop_4 )
    );
---Cau1.7
CREATE OR REPLACE VIEW vw_data_integrity_check AS
-- Loi 1: SV trong ENROLLMENT khong ton tai trong STUDENT
    SELECT
        'LOI_1: SV_KHONG_TON_TAI'                              AS loai_van_de,
        to_char(e.studentid)                                   AS ma_tham_chieu,
        'StudentID '
        || e.studentid
        || ' co trong ENROLLMENT nhung khong co
trong STUDENT' AS mo_ta
    FROM
        enrollment e
    WHERE
        NOT EXISTS (
            SELECT
                1
            FROM
                student s
            WHERE
                s.studentid = e.studentid
        )
    UNION ALL

-- Loi 2: Lop trong CLASS thieu giao vien
    SELECT
        'LOI_2: LOP_THIEU_GIAO_VIEN',
        to_char(cl.classid),
        'ClassID '
        || cl.classid
        || ' khong co InstructorID hop le'
    FROM
        class cl
    WHERE
        NOT EXISTS (
            SELECT
                1
            FROM
                instructor i
            WHERE
                i.instructorid = cl.instructorid
        )
    UNION ALL

-- Loi 3: Diem trong GRADE khong khop voi ENROLLMENT
    SELECT
        'LOI_3: DIEM_KHONG_KHOP',
        to_char(g.studentid)
        || '/'
        || to_char(g.classid),
        'GRADE.grade='
        || g.grade
        || ' khac
ENROLLMENT.finalgrade='
        || e.finalgrade
    FROM
             grade g
        JOIN enrollment e ON g.studentid = e.studentid
                             AND g.classid = e.classid
    WHERE
        g.grade != nvl(e.finalgrade, -999)
    UNION ALL

-- Loi 4: SV dang ky qua 3 lop
    SELECT
        'LOI_4: DANG_KY_QUA_3_LOP',
        to_char(studentid),
        'StudentID '
        || studentid
        || ' dang ky '
        || COUNT(*)
        || ' lop (toi da 3)'
    FROM
        enrollment
    GROUP BY
        studentid
    HAVING
        COUNT(*) > 3;

SELECT
    *
FROM
    vw_data_integrity_check;
----BÀI 2 - STORED PROCEDURE NÂNG CAO
--Cau2.1
--Thủ tục trả về cursor:
CREATE OR REPLACE PROCEDURE get_students_by_class (
    p_classid IN NUMBER,
    p_result  OUT SYS_REFCURSOR
) IS
    v_check NUMBER;
BEGIN
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        class
    WHERE
        classid = p_classid;

    IF v_check = 0 THEN
        p_result := NULL;
        dbms_output.put_line('Lop '
                             || p_classid
                             || ' khong ton tai!');
        RETURN;
    END IF;

    OPEN p_result FOR SELECT
                                          s.studentid,
                                          s.firstname
                                          || ' '
                                          || s.lastname AS ho_ten,
                                          e.finalgrade,
                                          CASE
                                              WHEN e.finalgrade >= 90 THEN
                                                  'A'
                                              WHEN e.finalgrade >= 80 THEN
                                                  'B'
                                              WHEN e.finalgrade >= 70 THEN
                                                  'C'
                                              WHEN e.finalgrade >= 50 THEN
                                                  'D'
                                              WHEN e.finalgrade IS NULL THEN
                                                  'Chua co'
                                              ELSE
                                                  'F'
                                          END           AS xep_loai,
                                          RANK()
                                          OVER(
                                              ORDER BY
                                                  e.finalgrade DESC NULLS LAST
                                          )             AS thu_hang
                                      FROM
                                               enrollment e
                                          JOIN student s ON e.studentid = s.studentid
                     WHERE
                         e.classid = p_classid
                     ORDER BY
                         thu_hang;

END get_students_by_class;
/
--Thủ tục in kết quả:
CREATE OR REPLACE PROCEDURE print_class_result (
    p_classid IN NUMBER
) IS

    v_cur  SYS_REFCURSOR;
    v_sid  NUMBER;
    v_ten  VARCHAR2(50);
    v_diem NUMBER;
    v_xep  VARCHAR2(10);
    v_hang NUMBER;
BEGIN
    get_students_by_class(p_classid, v_cur);
    IF v_cur IS NULL THEN
        RETURN;
    END IF;
    dbms_output.put_line('=== KET QUA LOP '
                         || p_classid
                         || ' ===');
    dbms_output.put_line(rpad('Hang', 5)
                         || rpad('Ho
Ten', 22)
                         || lpad('Diem', 6)
                         || ' Xep loai');

    dbms_output.put_line(rpad('-', 45, '-'));
    LOOP
        FETCH v_cur INTO
            v_sid,
            v_ten,
            v_diem,
            v_xep,
            v_hang;
        EXIT WHEN v_cur%notfound;
        dbms_output.put_line(lpad(v_hang, 4)
                             || ' '
                             || rpad(v_ten, 22)
                             || lpad(
            nvl(
                to_char(v_diem),
                '--'
            ),
            6
        )
                             || ' '
                             || v_xep);

    END LOOP;

    CLOSE v_cur;
END print_class_result;
/

BEGIN
    print_class_result(1);
END;
/
--Cau2.2
CREATE OR REPLACE PROCEDURE validate_enrollment (
    p_studentid IN NUMBER,
    p_classid   IN NUMBER
) IS

    ex_sv_not_found EXCEPTION;
    PRAGMA exception_init ( ex_sv_not_found, -20101 );
    ex_class_not_found EXCEPTION;
    PRAGMA exception_init ( ex_class_not_found, -20102 );
    ex_class_full EXCEPTION;
    PRAGMA exception_init ( ex_class_full, -20103 );
    ex_already_enrolled EXCEPTION;
    PRAGMA exception_init ( ex_already_enrolled, -20104 );
    v_check NUMBER;
    v_cap   NUMBER;
    v_enr   NUMBER;
BEGIN
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        student
    WHERE
        studentid = p_studentid;

    IF v_check = 0 THEN
        raise_application_error(-20101, 'Sinh vien '
                                        || p_studentid
                                        || ' khong
ton tai!');
    END IF;

    SELECT
        COUNT(*)
    INTO v_check
    FROM
        class
    WHERE
        classid = p_classid;

    IF v_check = 0 THEN
        raise_application_error(-20102, 'Lop hoc '
                                        || p_classid
                                        || ' khong ton
tai!');
    END IF;

    SELECT
        capacity
    INTO v_cap
    FROM
        class
    WHERE
        classid = p_classid;

    SELECT
        COUNT(*)
    INTO v_enr
    FROM
        enrollment
    WHERE
        classid = p_classid;

    IF v_enr >= v_cap THEN
        raise_application_error(-20103, 'Lop '
                                        || p_classid
                                        || ' da day
('
                                        || v_enr
                                        || '/'
                                        || v_cap
                                        || ')!');
    END IF;

    SELECT
        COUNT(*)
    INTO v_check
    FROM
        enrollment
    WHERE
            studentid = p_studentid
        AND classid = p_classid;

    IF v_check > 0 THEN
        raise_application_error(-20104, 'SV '
                                        || p_studentid
                                        || ' da dang ky lop
nay roi!');
    END IF;

    dbms_output.put_line('[OK] Tat ca dieu kien deu thoa man!');
EXCEPTION
    WHEN ex_sv_not_found THEN
        dbms_output.put_line('[KHONG TON TAI]
' || sqlerrm);
    WHEN ex_class_not_found THEN
        dbms_output.put_line('[LOP SAI]
' || sqlerrm);
    WHEN ex_class_full THEN
        dbms_output.put_line('[DAY LOP]
' || sqlerrm);
    WHEN ex_already_enrolled THEN
        dbms_output.put_line('[TRUNG LAP]
' || sqlerrm);
    WHEN OTHERS THEN
        dbms_output.put_line('[LOI KHAC] ' || sqlerrm);
END validate_enrollment;
/
---Cau2.3
CREATE OR REPLACE PROCEDURE calc_total_prerequisite_cost (
    p_courseno IN NUMBER,
    p_total    OUT NUMBER,
    p_depth    IN NUMBER DEFAULT 0
) IS

    v_cost      NUMBER;
    v_prereq    NUMBER;
    v_desc      VARCHAR2(50);
    v_sub_total NUMBER := 0;
    v_indent    VARCHAR2(40);
BEGIN
    IF p_depth >= 10 THEN
        dbms_output.put_line('CANH BAO: Dat gioi han do sau (10)!');
        p_total := 0;
        RETURN;
    END IF;

    BEGIN
        SELECT
            cost,
            prerequisite,
            description
        INTO
            v_cost,
            v_prereq,
            v_desc
        FROM
            course
        WHERE
            courseno = p_courseno;

    EXCEPTION
        WHEN no_data_found THEN
            p_total := 0;
            RETURN;
    END;

    v_indent := lpad(' ', p_depth * 4);
    IF v_prereq IS NOT NULL THEN
        calc_total_prerequisite_cost(v_prereq, v_sub_total, p_depth + 1);
    END IF;

    p_total := nvl(v_cost, 0) + v_sub_total;
    dbms_output.put_line(v_indent
                         || 'Cap '
                         || p_depth
                         || ': '
                         || p_courseno
                         || ' - '
                         || v_desc
                         || ' (phi: '
                         || nvl(v_cost, 0)
                         || ')');

END calc_total_prerequisite_cost;
/

-- Kiem tra:
DECLARE
    v_total NUMBER;
BEGIN
    calc_total_prerequisite_cost(30, v_total);
    dbms_output.put_line('Tong hoc phi can thiet: ' || v_total);
END;
/
--Cau2.4
--Package SPEC:
CREATE OR REPLACE PACKAGE pkg_student_mgmt AS
    c_max_classes CONSTANT NUMBER := 3;
    PROCEDURE enroll (
        p_sid NUMBER,
        p_cid NUMBER
    );

    PROCEDURE withdraw (
        p_sid NUMBER,
        p_cid NUMBER
    );

    FUNCTION get_student_gpa (
        p_sid NUMBER
    ) RETURN NUMBER;

    PROCEDURE print_transcript (
        p_sid NUMBER
    );

    FUNCTION count_enrolled (
        p_sid NUMBER
    ) RETURN NUMBER;

END pkg_student_mgmt;
/
--Package BODY:
CREATE OR REPLACE PACKAGE BODY pkg_student_mgmt AS
-- Bien noi bo: dem so lan goi
g_call_count NUMBER := 0;
FUNCTION count_enrolled(p_sid NUMBER) RETURN NUMBER IS
v_cnt NUMBER;
BEGIN
SELECT COUNT(*) INTO v_cnt FROM enrollment WHERE studentid=p_sid;
RETURN v_cnt;
END; PROCEDURE enroll (
    p_sid NUMBER,
    p_cid NUMBER
) IS
    v_check NUMBER;
    v_cap   NUMBER;
    v_enr   NUMBER;
BEGIN
    g_call_count := g_call_count + 1;
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        student
    WHERE
        studentid = p_sid;

    IF v_check = 0 THEN
        dbms_output.put_line('[LOI] SV khong ton tai');
        RETURN;
    END IF;
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        class
    WHERE
        classid = p_cid;

    IF v_check = 0 THEN
        dbms_output.put_line('[LOI] Lop khong ton tai');
        RETURN;
    END IF;
    IF count_enrolled(p_sid) >= c_max_classes THEN
        dbms_output.put_line('[LOI] SV da du '
                             || c_max_classes
                             || ' lop');
        RETURN;
    END IF;

    SELECT
        capacity
    INTO v_cap
    FROM
        class
    WHERE
        classid = p_cid;

    SELECT
        COUNT(*)
    INTO v_enr
    FROM
        enrollment
    WHERE
        classid = p_cid;

    IF v_enr >= v_cap THEN
        dbms_output.put_line('[LOI] Lop day');
        RETURN;
    END IF;
INSERT INTO
enrollment (
    studentid,
    classid,
    enrolldate,
    createdby,
    createddate,
    modifiedby,
    mo
difieddate)
        values ( p_sid,
        p_cid,
        sysdate,
        user,
        sysdate,
        user,
        sysdate );
        commit;
        dbms_output.put_line ( '[OK] Dang ky: SV '
        || p_sid || ' -> Lop
' || p_cid );
    end
        enroll;

    PROCEDURE withdraw (
        p_sid NUMBER,
        p_cid NUMBER
    ) IS
        v_check NUMBER;
    BEGIN
        SELECT
            COUNT(*)
        INTO v_check
        FROM
            enrollment
        WHERE
                studentid = p_sid
            AND classid = p_cid;

        IF v_check = 0 THEN
            dbms_output.put_line('[LOI] SV chua dang ky lop
nay');
            RETURN;
        END IF;
        DELETE FROM enrollment
        WHERE
                studentid = p_sid
            AND classid = p_cid;

        COMMIT;
        dbms_output.put_line('[OK] Da huy dang ky: SV '
                             || p_sid
                             || ' khoi Lop
'
                             || p_cid);
    END withdraw;

    FUNCTION get_student_gpa (
        p_sid NUMBER
    ) RETURN NUMBER IS
        v_gpa   NUMBER;
        v_check NUMBER;
    BEGIN
        SELECT
            COUNT(*)
        INTO v_check
        FROM
            student
        WHERE
            studentid = p_sid;

        IF v_check = 0 THEN
            RETURN NULL;
        END IF;
        SELECT
            round(
                avg(finalgrade),
                2
            )
        INTO v_gpa
        FROM
            enrollment
        WHERE
                studentid = p_sid
            AND finalgrade IS NOT NULL;

        RETURN v_gpa;
    END;

    PROCEDURE print_transcript (
        p_sid NUMBER
    ) IS
    BEGIN
        dbms_output.put_line('=== BANG DIEM SV: '
                             || p_sid
                             || ' ===');
        FOR rec IN (
            SELECT
                co.description,
                co.courseno,
                e.finalgrade,
                cl.classid
            FROM
                     enrollment e
                JOIN class  cl ON e.classid = cl.classid
                JOIN course co ON cl.courseno = co.courseno
            WHERE
                e.studentid = p_sid
            ORDER BY
                co.courseno
        ) LOOP
            dbms_output.put_line(' '
                                 || rec.courseno
                                 || '
'
                                 || rpad(rec.description, 25)
                                 || ' : '
                                 || nvl(
                to_char(rec.finalgrade),
                'Chua
co diem'
            ));
        END LOOP;

        dbms_output.put_line(' GPA:
'
                             || nvl(
            to_char(get_student_gpa(p_sid)),
            'N/A'
        ));

        end;
    END pkg_student_mgmt;

/

-- Kiem tra package:
BEGIN
    pkg_student_mgmt.enroll(3020, 1006);
    pkg_student_mgmt.print_transcript(3020);
END;
/
---Cau2.5
CREATE OR REPLACE PROCEDURE bulk_update_grades IS

    TYPE t_num IS
        TABLE OF NUMBER INDEX BY PLS_INTEGER;
    v_sids   t_num;
    v_cids   t_num;
    v_grades t_num;
    v_start  NUMBER;
    v_end    NUMBER;
    v_rows   NUMBER := 0;
BEGIN
    v_start := dbms_utility.get_time;
-- Doc du lieu vao mang nhanh
    SELECT
        studentid,
        classid,
        finalgrade
    BULK COLLECT
    INTO
        v_sids,
        v_cids,
        v_grades
    FROM
        enrollment
    WHERE
        finalgrade IS NOT NULL;

    dbms_output.put_line('Doc duoc '
                         || v_sids.count
                         || ' ban ghi...');
-- Cap nhat hang loat vao GRADE (MERGE thay the INSERT+UPDATE)
    FORALL i IN 1..v_sids.count SAVE EXCEPTIONS
        MERGE INTO grade g
        USING (
            SELECT
                v_sids(i)   AS sid,
                v_cids(i)   AS cid,
                v_grades(i) AS gr
            FROM
                dual
        ) src ON ( g.studentid = src.sid
                   AND g.classid = src.cid )
        WHEN MATCHED THEN UPDATE
        SET g.grade = src.gr,
            g.modifiedby = user,
            g.modifieddate = sysdate
        WHEN NOT MATCHED THEN
        INSERT (
            studentid,
            classid,
            grade,
            createdby,
            createddate,
            modifiedby,
            modifieddate )
        VALUES
            ( src.sid,
              src.cid,
              src.gr,
              user,
              sysdate,
              user,
              sysdate );

    v_rows := SQL%rowcount;
    COMMIT;
    v_end := dbms_utility.get_time;
    dbms_output.put_line('Xu ly: '
                         || v_rows
                         || ' hang | Thoi gian: '
                         || round((v_end - v_start) / 100, 2)
                         || ' giay');

EXCEPTION
    WHEN OTHERS THEN
        FOR j IN 1..SQL%bulk_exceptions.count LOOP
            dbms_output.put_line('Loi hang
'
                                 || SQL%bulk_exceptions(j).error_index
                                 || ': '
                                 || sqlerrm(-SQL%bulk_exceptions(j).error_code));
        END LOOP;

        ROLLBACK;
END bulk_update_grades;
/

BEGIN
    bulk_update_grades;
END;
/
--Cau2.6
CREATE OR REPLACE PROCEDURE generate_course_report (
    p_courseno IN NUMBER
) IS

    v_check   NUMBER;
    v_desc    VARCHAR2(50);
    v_cost    NUMBER;
    v_prereq  NUMBER;
    v_tong_sv NUMBER := 0;
    v_sum_d   NUMBER := 0;
    v_co_d    NUMBER := 0;
    v_sep     VARCHAR2(70) := rpad('=', 60, '=');
    v_sep2    VARCHAR2(70) := rpad('-', 60, '-');
BEGIN
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        course
    WHERE
        courseno = p_courseno;

    IF v_check = 0 THEN
        dbms_output.put_line('Mon hoc '
                             || p_courseno
                             || ' khong ton tai!');
        RETURN;
    END IF;

    SELECT
        description,
        cost,
        prerequisite
    INTO
        v_desc,
        v_cost,
        v_prereq
    FROM
        course
    WHERE
        courseno = p_courseno;

    dbms_output.put_line(v_sep);
    dbms_output.put_line('BAO CAO MON HOC: ' || p_courseno);
    dbms_output.put_line(v_sep2);
    dbms_output.put_line('Ten mon : ' || v_desc);
    dbms_output.put_line('Hoc phi :
'
                         || to_char(
        nvl(v_cost, 0),
        '999,990.00'
    )
                         || ' VND');

    dbms_output.put_line('Mon tien q: '
                         || nvl(
        to_char(v_prereq),
        'Khong
co'
    ));
    dbms_output.put_line(v_sep2);
    dbms_output.put_line(rpad('Lop', 5)
                         || rpad('Giao vien', 20)
                         || lpad('SVDK', 6)
                         || lpad('DTB', 7)
                         || ' Trang thai');

    dbms_output.put_line(v_sep2);
    FOR rec IN (
        SELECT
            cl.classid,
            cl.capacity,
            i.firstname
            || ' '
            || i.lastname      AS ten_gv,
            COUNT(e.studentid) AS so_sv,
            round(
                avg(e.finalgrade),
                1
            )                  AS dtb
        FROM
                 class cl
            JOIN instructor i ON cl.instructorid = i.instructorid
            LEFT JOIN enrollment e ON cl.classid = e.classid
        WHERE
            cl.courseno = p_courseno
        GROUP BY
            cl.classid,
            cl.capacity,
            i.firstname,
            i.lastname
        ORDER BY
            cl.classid
    ) LOOP
        v_tong_sv := v_tong_sv + rec.so_sv;
        IF rec.dtb IS NOT NULL THEN
            v_sum_d := v_sum_d + rec.dtb;
            v_co_d := v_co_d + 1;
        END IF;

        dbms_output.put_line(lpad(rec.classid, 4)
                             || ' '
                             || rpad(rec.ten_gv, 20)
                             || lpad(rec.so_sv, 5)
                             || lpad(
            nvl(
                to_char(rec.dtb),
                '--'
            ),
            7
        )
                             || ' '
                             || CASE
            WHEN rec.capacity - rec.so_sv > 0 THEN
                'Con '
                ||(rec.capacity - rec.so_sv)
                || ' cho'
            ELSE 'Het cho'
        END);

    END LOOP;

    dbms_output.put_line(v_sep2);
    dbms_output.put_line('Tong SV dang ky : ' || v_tong_sv);
    IF v_co_d > 0 THEN
        dbms_output.put_line('Diem TB toan mon:
'
                             || round(v_sum_d / v_co_d, 2));
    END IF;

    dbms_output.put_line(v_sep);
END generate_course_report;
/

BEGIN
    generate_course_report(10);
END;
/
--Cau2.7
CREATE OR REPLACE FUNCTION convert_to_gpa_40 (
    p_studentid IN NUMBER
) RETURN NUMBER IS
    v_check NUMBER;
    v_gpa   NUMBER;
BEGIN
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        student
    WHERE
        studentid = p_studentid;

    IF v_check = 0 THEN
        RETURN NULL;
    END IF;
    SELECT
        round(sum(CASE
            WHEN finalgrade >= 90 THEN
                4.0
            WHEN finalgrade >= 85 THEN
                3.7
            WHEN finalgrade >= 80 THEN
                3.3
            WHEN finalgrade >= 75 THEN
                3.0
            WHEN finalgrade >= 70 THEN
                2.7
            WHEN finalgrade >= 65 THEN
                2.3
            WHEN finalgrade >= 60 THEN
                2.0
            WHEN finalgrade >= 50 THEN
                1.0
            ELSE 0.0
        END * 3) / -- So tin chi = 3
         nullif(
            sum(
                CASE
                    WHEN finalgrade IS NOT NULL THEN
                        3
                    ELSE 0
                END
            ),
            0
        ),
              2)
    INTO v_gpa
    FROM
        enrollment
    WHERE
        studentid = p_studentid;

    RETURN v_gpa;
END convert_to_gpa_40;
/

CREATE OR REPLACE PROCEDURE print_gpa_report IS
BEGIN
    dbms_output.put_line(rpad('StudentID', 12)
                         || rpad('Ho Ten', 25)
                         || lpad('GPA
(4.0)', 10));

    dbms_output.put_line(rpad('-', 48, '-'));
    FOR rec IN (
        SELECT
            studentid,
            firstname
            || ' '
            || lastname AS ho_ten
        FROM
            student
        ORDER BY
            studentid
    ) LOOP
        DECLARE
            v_gpa NUMBER;
        BEGIN
            v_gpa := convert_to_gpa_40(rec.studentid);
            IF v_gpa IS NOT NULL THEN
                dbms_output.put_line(lpad(rec.studentid, 10)
                                     || ' '
                                     || rpad(rec.ho_ten, 25)
                                     || lpad(v_gpa, 9));

            END IF;

        END;
    END LOOP;

END print_gpa_report;
/

BEGIN
    print_gpa_report;
END;
/
--Cau2.8
CREATE TABLE notification_log (
    log_id     NUMBER
        GENERATED ALWAYS AS IDENTITY
    PRIMARY KEY,
    nguoi_nhan VARCHAR2(50),
    noi_dung   VARCHAR2(500),
    loai       VARCHAR2(20),
    thoi_gian  DATE DEFAULT sysdate,
    trang_thai VARCHAR2(10) DEFAULT 'SENT'
);
/

CREATE OR REPLACE PROCEDURE log_notification
(p_nguoi_nhan VARCHAR2,
p_noi_dung VARCHAR2,
p_loai VARCHAR2 DEFAULT 'INFO')
IS
PRAGMA AUTONOMOUS_TRANSACTION; -- Doc lap khoi transaction cha
BEGIN
INSERT INTO notification_log (nguoi_nhan, noi_dung, loai)
VALUES (p_nguoi_nhan, SUBSTR(p_noi_dung,1,500), p_loai);
COMMIT; -- Commit ngay, khong phu thuoc transaction cha
EXCEPTION
WHEN OTHERS THEN
ROLLBACK; -- Chi rollback autonomous transaction nay
END log_notification;
/

-- Kiem tra tinh doc lap:
BEGIN
INSERT INTO student (
    studentid,
    lastname,
    registrationdate,
    createdby,
    createddate,
    modifiedby,
    modifieddate
) VALUES ( 9999,
           'Test',
           sysdate,
           user,
           sysdate,
           user,
           sysdate );

log_notification('Admin', 'Da them SV 9999', 'ENROLL');

ROLLBACK; -- Rollback INSERT student, nhung log van con!
end;
/

SELECT
    *
FROM
    notification_log; -- Ban ghi log van con du da ROLLBACK
---BÀI 3 - TRIGGER NÂNG CAO
--Cau3.1
ALTER TABLE class ADD so_sv NUMBER DEFAULT 0;

CREATE OR REPLACE TRIGGER trg_update_class_count FOR
    INSERT OR UPDATE OR DELETE ON enrollment
COMPOUND TRIGGER
    TYPE t_ids IS
        TABLE OF NUMBER INDEX BY PLS_INTEGER;
    v_ids t_ids;
    v_idx PLS_INTEGER := 0;
    BEFORE STATEMENT IS BEGIN
        v_idx := 0;
        v_ids.DELETE;
    END BEFORE STATEMENT;
    AFTER EACH ROW IS BEGIN
        v_idx := v_idx + 1;
        v_ids(v_idx) :=
            CASE
                WHEN inserting
                OR updating THEN
                    :new.classid
                ELSE :old.classid
            END;

    END AFTER EACH ROW;
    AFTER STATEMENT IS BEGIN
        FOR i IN 1..v_idx LOOP
            UPDATE class
            SET
                so_sv = (
                    SELECT
                        COUNT(*)
                    FROM
                        enrollment
                    WHERE
                        classid = v_ids(i)
                )
            WHERE
                classid = v_ids(i);

        END LOOP;
    END AFTER STATEMENT;
END trg_update_class_count;
/

-- Kiem tra:
INSERT INTO enrollment (
    studentid,
    classid,
    enrolldate,
    createdby,
    createddate,
    modifiedby,
    modifieddate
) VALUES ( 3020,
           1006,
           sysdate,
           user,
           sysdate,
           user,
           sysdate );

COMMIT;

SELECT
    classid,
    so_sv
FROM
    class
WHERE
    classid = 1006;
--Cau3.2
CREATE OR REPLACE VIEW vw_class_enrollment_detail AS
    SELECT
        e.classid,
        e.studentid,
        s.firstname
        || ' '
        || s.lastname  AS ten_sv,
        co.description AS ten_mon,
        e.finalgrade,
        i.firstname
        || ' '
        || i.lastname  AS ten_gv
    FROM
             enrollment e
        JOIN student    s ON e.studentid = s.studentid
        JOIN class      cl ON e.classid = cl.classid
        JOIN course     co ON cl.courseno = co.courseno
        JOIN instructor i ON cl.instructorid = i.instructorid;

CREATE OR REPLACE TRIGGER trg_iot_update_grade INSTEAD OF
    UPDATE ON vw_class_enrollment_detail
    FOR EACH ROW
DECLARE
    v_old_grade NUMBER;
BEGIN
    IF
        :new.finalgrade IS NOT NULL
        AND ( :new.finalgrade < 0
        OR :new.finalgrade > 100 )
    THEN
        raise_application_error(-20060, 'Diem khong hop le (0-100)!');
    END IF;

    SELECT
        finalgrade
    INTO v_old_grade
    FROM
        enrollment
    WHERE
            studentid = :old.studentid
        AND classid = :old.classid;

    UPDATE enrollment
    SET
        finalgrade = :new.finalgrade,
        modifiedby = user,
        modifieddate = sysdate
    WHERE
            studentid = :old.studentid
        AND classid = :old.classid;

    MERGE INTO grade g
    USING (
        SELECT
            :old.studentid AS sid,
            :old.classid   AS cid
        FROM
            dual
    ) src ON ( g.studentid = src.sid
               AND g.classid = src.cid )
    WHEN MATCHED THEN UPDATE
    SET g.grade = :new.finalgrade,
        g.modifiedby = user,
        g.modifieddate = sysdate
    WHEN NOT MATCHED THEN
    INSERT (
        studentid,
        classid,
        grade,
        createdby,
        createddate,
        modifiedby,
        modifieddate )
    VALUES
        ( :old.studentid,
          :old.classid,
          :new.finalgrade,
          user,
          sysdate,
          user,
          sysdate );

    log_notification('System',
                     'Cap nhat diem SV '
                     || :old.studentid
                     || ' lop '
                     || :old.classid
                     || ': '
                     || nvl(
        to_char(v_old_grade),
        'NULL'
    )
                     || '->'
                     || :new.finalgrade,
                     'GRADE');

END trg_iot_update_grade;
/

-- Kiem tra:
UPDATE vw_class_enrollment_detail
SET
    finalgrade = 88
WHERE
        studentid = 3001
    AND classid = 1001;

COMMIT;
--Cau3.3
CREATE TABLE ddl_audit_log (
    log_id      NUMBER
        GENERATED ALWAYS AS IDENTITY,
    event_type  VARCHAR2(30),
    object_type VARCHAR2(30),
    object_name VARCHAR2(128),
    owner       VARCHAR2(30),
    event_time  DATE,
    current_usr VARCHAR2(30)
);
/

CREATE OR REPLACE TRIGGER trg_ddl_audit
AFTER DDL ON SCHEMA
DECLARE
PRAGMA
autonomous_transaction;

BEGIN
    INSERT INTO ddl_audit_log (
        event_type,
        object_type,
        object_name,
        owner,
        event_time,
        current_usr
    ) VALUES ( ora_sysevent,
               ora_dict_obj_type,
               ora_dict_obj_name,
               ora_dict_obj_owner,
               sysdate,
               ora_login_user );

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
END trg_ddl_audit;
/

-- Kiem tra:
CREATE TABLE test_ddl_track (
    id NUMBER
);

DROP TABLE test_ddl_track;

SELECT
    *
FROM
    ddl_audit_log
ORDER BY
    log_id DESC;
--Cau3.4
-- Trigger 1: BEFORE DELETE tren STUDENT - Kiem tra
CREATE OR REPLACE TRIGGER trg_prevent_student_delete BEFORE
    DELETE ON student
    FOR EACH ROW
DECLARE
    v_count NUMBER;
BEGIN
    SELECT
        COUNT(*)
    INTO v_count
    FROM
        enrollment
    WHERE
        studentid = :old.studentid;

    IF v_count > 0 THEN
        raise_application_error(-20030,
                                'Khong the xoa SV '
                                || :old.studentid
                                || ' dang co '
                                || v_count
                                || ' lop dang ky! Huy dang ky truoc.');

    END IF;

END;
/
-- Trigger 2: AFTER DELETE tren STUDENT - Cascade xoa GRADE
CREATE OR REPLACE TRIGGER trg_cascade_delete_grade AFTER
    DELETE ON student
    FOR EACH ROW
BEGIN
    DELETE FROM grade
    WHERE
        studentid = :old.studentid;

    dbms_output.put_line('Da xoa '
                         || SQL%rowcount
                         || ' ban ghi GRADE cua SV
'
                         || :old.studentid);

END;
/

-- Trigger 3: AFTER DELETE tren ENROLLMENT - Cap nhat so_sv trong CLASS
-- (Compound Trigger o cau 3.1 da xu ly dieu nay!)
-- Neu chua co compound trigger, viet them:
CREATE OR REPLACE TRIGGER trg_update_count_on_delete AFTER
    DELETE ON enrollment
    FOR EACH ROW
BEGIN
    UPDATE class
    SET
        so_sv = so_sv - 1
    WHERE
            classid = :old.classid
        AND so_sv > 0;

END;
/
-- Kiem tra chuoi trigger:
-- Thu xoa SV co enrollment (bi chan):
DELETE FROM student
WHERE
    studentid = 3001;

-- Xoa enrollment truoc, sau do xoa SV (thanh cong):
DELETE FROM enrollment
WHERE
    studentid = 3001;

DELETE FROM student
WHERE
    studentid = 3001;

ROLLBACK;
--Cau3.5
CREATE TABLE certificate (
    cert_id   NUMBER
        GENERATED ALWAYS AS IDENTITY,
    studentid NUMBER(8),
    courseno  NUMBER(8),
    cap_cc    DATE,
    loai      VARCHAR2(20)
);
/
CREATE OR REPLACE TRIGGER trg_auto_certificate AFTER
    UPDATE OF finalgrade ON enrollment
    FOR EACH ROW
    WHEN ( new.finalgrade >= 50 ) -- Chi chay khi diem >= 50
DECLARE
    v_courseno NUMBER;
    v_check    NUMBER;
    v_loai     VARCHAR2(20);
    v_ten_sv   VARCHAR2(50);
    v_ten_mon  VARCHAR2(50);
BEGIN
-- Lay thong tin
    SELECT
        cl.courseno,
        co.description,
        s.firstname
        || ' '
           || s.lastname
    INTO
        v_courseno,
        v_ten_mon,
        v_ten_sv
    FROM
             class cl
        JOIN course  co ON cl.courseno = co.courseno
        JOIN student s ON s.studentid = :new.studentid
    WHERE
        cl.classid = :new.classid;

-- Kiem tra da co chung chi chua
    SELECT
        COUNT(*)
    INTO v_check
    FROM
        certificate
    WHERE
            studentid = :new.studentid
        AND courseno = v_courseno;

    IF v_check > 0 THEN
        RETURN;
    END IF; -- Da co roi, bo qua
-- Xac dinh loai chung chi
    v_loai :=
        CASE
            WHEN :new.finalgrade >= 90 THEN
                'HIGH_DISTINCTION'
            WHEN :new.finalgrade >= 75 THEN
                'DISTINCTION'
            ELSE 'PASS'
        END;

-- Cap chung chi
    INSERT INTO certificate (
        studentid,
        courseno,
        cap_cc,
        loai
    ) VALUES ( :new.studentid,
               v_courseno,
               sysdate,
               v_loai );

    dbms_output.put_line('Chuc mung '
                         || v_ten_sv
                         || ' da hoan thanh mon '
                         || v_ten_mon
                         || ' voi '
                         || v_loai
                         || '!');

END trg_auto_certificate;
/

-- Kiem tra:
UPDATE enrollment
SET
    finalgrade = 92
WHERE
        studentid = 3001
    AND classid = 1001;

COMMIT;

SELECT
    *
FROM
    certificate;
----BAI 4 - TONG HOP
--Cau4.1
--View vw_enrollment_dashboard:
CREATE OR REPLACE VIEW vw_enrollment_dashboard AS
    SELECT
        (
            SELECT
                COUNT(*)
            FROM
                class
        )        AS so_lop_mo,
        (
            SELECT
                SUM(cl.capacity - nvl(ec.sv, 0))
            FROM
                class cl
                LEFT JOIN (
                    SELECT
                        classid,
                        COUNT(*) sv
                    FROM
                        enrollment
                    GROUP BY
                        classid
                )     ec ON cl.classid = ec.classid
        )        AS tong_cho_trong,
        round((
            SELECT
                COUNT(*)
            FROM
                enrollment
        ) * 100.0 / nullif((
            SELECT
                SUM(capacity)
            FROM
                class
        ),
                           0),
              1) AS ty_le_lap_day_pct,
        (
            SELECT
                classid
                || ' ('
                || sv
                || ' SV)'
            FROM
                (
                    SELECT
                        classid,
                        COUNT(*) sv
                    FROM
                        enrollment
                    GROUP BY
                        classid
                    ORDER BY
                        sv DESC
                    FETCH FIRST 1 ROW ONLY
                )
        )        AS lop_dong_nhat,
        (
            SELECT
                classid
                || ' ('
                || sv
                || ' SV)'
            FROM
                (
                    SELECT
                        classid,
                        COUNT(*) sv
                    FROM
                        enrollment
                    GROUP BY
                        classid
                    ORDER BY
                        sv ASC
                    FETCH FIRST 1 ROW ONLY
                )
        )        AS lop_it_nhat
    FROM
        dual;

SELECT
    *
FROM
    vw_enrollment_dashboard;
--Package pkg_enrollment_system (rút gọn phần chính):
CREATE OR REPLACE PACKAGE pkg_enrollment_system AS
    FUNCTION is_eligible (
        p_sid NUMBER,
        p_cid NUMBER
    ) RETURN BOOLEAN;

    PROCEDURE do_enroll (
        p_sid NUMBER,
        p_cid NUMBER
    );

    PROCEDURE do_withdraw (
        p_sid NUMBER,
        p_cid NUMBER
    );

    FUNCTION get_waitlist_position (
        p_sid NUMBER,
        p_cid NUMBER
    ) RETURN NUMBER;

END pkg_enrollment_system;
/

CREATE OR REPLACE PACKAGE BODY pkg_enrollment_system AS

    FUNCTION is_eligible (
        p_sid NUMBER,
        p_cid NUMBER
    ) RETURN BOOLEAN IS
        v_sv  NUMBER;
        v_cl  NUMBER;
        v_cap NUMBER;
        v_enr NUMBER;
        v_dup NUMBER;
    BEGIN
        SELECT
            COUNT(*)
        INTO v_sv
        FROM
            student
        WHERE
            studentid = p_sid;

        IF v_sv = 0 THEN
            RETURN FALSE;
        END IF;
        SELECT
            COUNT(*)
        INTO v_cl
        FROM
            class
        WHERE
            classid = p_cid;

        IF v_cl = 0 THEN
            RETURN FALSE;
        END IF;
        SELECT
            capacity
        INTO v_cap
        FROM
            class
        WHERE
            classid = p_cid;

        SELECT
            COUNT(*)
        INTO v_enr
        FROM
            enrollment
        WHERE
            classid = p_cid;

        IF v_enr >= v_cap THEN
            RETURN FALSE;
        END IF;
        SELECT
            COUNT(*)
        INTO v_dup
        FROM
            enrollment
        WHERE
                studentid = p_sid
            AND classid = p_cid;

        IF v_dup > 0 THEN
            RETURN FALSE;
        END IF;
        SELECT
            COUNT(*)
        INTO v_enr
        FROM
            enrollment
        WHERE
            studentid = p_sid;

        IF v_enr >= 3 THEN
            RETURN FALSE;
        END IF;
        RETURN TRUE;
    END is_eligible;

    PROCEDURE do_enroll (
        p_sid NUMBER,
        p_cid NUMBER
    ) IS
    BEGIN
        IF NOT is_eligible(p_sid, p_cid) THEN
            dbms_output.put_line('[TU CHOI] Khong du dieu kien dang ky!');
            RETURN;
        END IF;

        INSERT INTO enrollment (
            studentid,
            classid,
            enrolldate,
            createdby,
            createddate,
            modifiedby,
            modifieddate
        ) VALUES ( p_sid,
                   p_cid,
                   sysdate,
                   user,
                   sysdate,
                   user,
                   sysdate );

        COMMIT;
        log_notification(user, 'Dang ky: SV '
                               || p_sid
                               || ' -> Lop
'
                               || p_cid, 'ENROLL');
        dbms_output.put_line('[OK] Dang ky thanh cong!');
    END do_enroll;

    PROCEDURE do_withdraw (
        p_sid NUMBER,
        p_cid NUMBER
    ) IS
        v_check NUMBER;
    BEGIN
        SELECT
            COUNT(*)
        INTO v_check
        FROM
            enrollment
        WHERE
                studentid = p_sid
            AND classid = p_cid;

        IF v_check = 0 THEN
            dbms_output.put_line('[LOI] SV chua dang ky lop nay!');
            RETURN;
        END IF;
        DELETE FROM enrollment
        WHERE
                studentid = p_sid
            AND classid = p_cid;

        COMMIT;
        log_notification(user, 'Huy dk: SV '
                               || p_sid
                               || ' khoi Lop
'
                               || p_cid, 'WITHDRAW');
        dbms_output.put_line('[OK] Huy dang ky thanh cong!');
    END do_withdraw;

    FUNCTION get_waitlist_position (
        p_sid NUMBER,
        p_cid NUMBER
    ) RETURN NUMBER IS
        v_cap NUMBER;
        v_enr NUMBER;
    BEGIN
        SELECT
            capacity
        INTO v_cap
        FROM
            class
        WHERE
            classid = p_cid;

        SELECT
            COUNT(*)
        INTO v_enr
        FROM
            enrollment
        WHERE
            classid = p_cid;

        IF v_enr < v_cap THEN
            RETURN 0;
        END IF;
        RETURN v_enr - v_cap + 1;
    END;

END pkg_enrollment_system;
/

-- Kiem tra:
BEGIN
    pkg_enrollment_system.do_enroll(3020, 1006);
    pkg_enrollment_system.do_enroll(999, 1001); -- SV khong ton tai
END;
/
---Cau4.2
--Phần A - Phân tích hiệu năng với EXPLAIN PLAN:
-- Xem execution plan cua view
EXPLAIN PLAN
    FOR
SELECT
    *
FROM
    vw_course_summary;

SELECT
    *
FROM
    TABLE ( dbms_xplan.display );
-- Tim Full Table Scan (TABLE ACCESS FULL) trong output
-- Tao INDEX tren cac cot hay dung trong JOIN/WHERE:
CREATE INDEX idx_enrollment_classid ON
    enrollment (
        classid
    );

CREATE INDEX idx_enrollment_studentid ON
    enrollment (
        studentid
    );

CREATE INDEX idx_class_courseno ON
    class (
        courseno
    );

CREATE INDEX idx_class_instructorid ON
    class (
        instructorid
    );
-- Chay lai EXPLAIN PLAN sau khi tao INDEX de so sanh
EXPLAIN PLAN
    FOR
SELECT
    *
FROM
    vw_course_summary;

SELECT
    *
FROM
    TABLE ( dbms_xplan.display );
-- Ket qua mong doi: thay 'TABLE ACCESS FULL' bang 'INDEX RANGE SCAN'
---Phần B - Refactor cursor bằng BULK COLLECT:
CREATE OR REPLACE PROCEDURE report_class_detail_v2 (
    p_classid IN NUMBER
) IS

    TYPE t_rec IS RECORD (
            ho_ten     VARCHAR2(50),
            finalgrade NUMBER
    );
    TYPE t_recs IS
        TABLE OF t_rec INDEX BY PLS_INTEGER;
    v_data t_recs;
    v_stt  NUMBER := 0;
BEGIN
-- BULK COLLECT thay vi cursor tung hang
    SELECT
        s.firstname
        || ' '
        || s.lastname,
        e.finalgrade
    BULK COLLECT
    INTO v_data
    FROM
             enrollment e
        JOIN student s ON e.studentid = s.studentid
    WHERE
        e.classid = p_classid
    ORDER BY
        s.lastname;

    dbms_output.put_line('So SV: ' || v_data.count);
    FOR i IN 1..v_data.count LOOP
        v_stt := v_stt + 1;
        dbms_output.put_line(lpad(v_stt, 3)
                             || ' '
                             || rpad(v_data(i).ho_ten,
                                     22)
                             || lpad(
            nvl(
                to_char(v_data(i).finalgrade),
                '--'
            ),
            6
        ));

    END LOOP;

END report_class_detail_v2;
/
--Phần C - Thủ tục chạy test tự động:
CREATE OR REPLACE PROCEDURE run_all_tests IS
    v_pass NUMBER := 0;
    v_fail NUMBER := 0;

    PROCEDURE assert (
        p_test VARCHAR2,
        p_cond BOOLEAN
    ) IS
    BEGIN
        IF p_cond THEN
            v_pass := v_pass + 1;
            dbms_output.put_line('[PASS] ' || p_test);
        ELSE
            v_fail := v_fail + 1;
            dbms_output.put_line('[FAIL] ' || p_test);
        END IF;
    END;

V_CNT NUMBER ; BEGIN DBMS_OUTPUT . PUT_LINE ( '=== BAT DAU TEST ===' ) ;
-- Test 1: enroll SV ton tai vao lop ton tai
BEGIN
    pkg_enrollment_system.do_enroll(102, 2);
    SELECT
        COUNT(*)
    INTO v_cnt
    FROM
        enrollment
    WHERE
            studentid = 3020
        AND classid = 1006;

    assert('Enroll hop le', v_cnt > 0);
    ROLLBACK;
EXCEPTION
    WHEN OTHERS THEN
        assert('Enroll hop le', FALSE);
END;

-- Test 2: enroll SV khong ton tai -> phai that bai
BEGIN
    pkg_enrollment_system.do_enroll(99999, 1001);
    SELECT
        COUNT(*)
    INTO v_cnt
    FROM
        enrollment
    WHERE
        studentid = 99999;

    assert('Chon SV khong ton tai', v_cnt = 0);
    end;
    dbms_output.put_line('=== KET QUA: PASS='
                         || v_pass
                         || ' FAIL='
                         || v_fail
                         || '
===');

END run_all_tests;
/

BEGIN
    run_all_tests;
END;
/

