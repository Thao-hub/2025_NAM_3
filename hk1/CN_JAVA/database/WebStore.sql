create database WebStore;
use WebStore;
-- Tạo bảng Category
CREATE TABLE Category (
    CategoryId SMALLINT NOT NULL IDENTITY(1,1) PRIMARY KEY,
    CategoryName VARCHAR(64) NOT NULL
);

-- Thêm dữ liệu mẫu
INSERT INTO Category (CategoryName) 
VALUES('Men shoes'),
    ('Women shoes'),
    ('Hand bag'),
    ('Fashion accessories');

-- Lưu ý: không cần chỉ định CategoryId khi dùng AUTO_INCREMENT
-- Nếu muốn xem dữ liệu trong bảng:
SELECT * FROM Category;
