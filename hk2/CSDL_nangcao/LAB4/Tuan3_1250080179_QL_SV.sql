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

