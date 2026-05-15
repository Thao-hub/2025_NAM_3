create table KhachHang
(   MaKH varchar2(15) primary key,
    TenKH nvarchar2(100),
    DiaChi nvarchar2(200)
);
create table NganHang
(   MaNH varchar2(15) primary key,
    TenNH nvarchar2(100)
);
create table ChiNhanh
(   MaNH varchar2(15) not null,
    MaCN varchar2(15) primary key,
    ThanhPhoCN nvarchar2(100),
    TaiSan number,
    constraint FK_CN_NH foreign key (MaNH) references NganHang(MaNH)
);
create table TaiKhoanVay
(   MaKH varchar(15) not null,
    MaCN varchar(15) not null,
    SoTKV varchar(15) primary key,
    SoTienVay number,
    constraint FK_TKV_KH foreign key (MaKH) references KhachHang(MaKH),
    constraint FK_TKV_CN foreign key (MaCN) references ChiNhanh(MaCN)
);
create table TaiKhoanGoi
(   MaKH varchar(15) not null,
    MaCN varchar(15) not null,
    SoTKG varchar(15) primary key,
    SoTienGoi number,
    constraint FK_TKG_KH foreign key (MaKH) references KhachHang(MaKH),
    constraint FK_TKG_CN foreign key (MaCN) references ChiNhanh(MaCN)
);

//nhap lieu cho bang khach hang
insert into khachhang values ('111222333',N'Hồ Thị Thanh Thảo',N'456 Lê Duẩn, Hà Nội');
insert into khachhang values ('112233445',N'Trần Văn Tiến',N'12 Điện Biên Phủ, Q1, TP HCM');
insert into khachhang values ('123123123',N'Phan Thị Quỳnh Như',N'54 Hai Bà Trưng, Hà Nội');
insert into khachhang values ('123412341',N'Nguyễn Văn Thảo',N'34 Trần Phú, TP Nha Trang');
insert into khachhang values ('123456789',N'Nguyễn Thị Hoa',N'1/4 Hoàng Văn Thụ, Đà Lạt');
insert into khachhang values ('221133445',N'Nguyễn Thị Kim Mai',N'4 Trần Bình Trọng, Đà Lạt');
insert into khachhang values ('222111333',N'Đỗ Tiến Đông',N'123 Trần Phú, Nam Định');
insert into khachhang values ('331122445',N'Bùi Thị Đông',N'345 Trần Hưng Đạo, Thanh Hóa');
insert into khachhang values ('333111222',N'Trần Đình Hùng',N'783 Lý Thường Kiệt, Cần Thơ');
insert into khachhang values ('441122335',N'Nguyễn Đình Cường',N'P12 Thanh Xuân Nam, Q Thanh Xuân');
insert into khachhang values ('456456456',N'Trần Nam Sơn',N'5 Lê Duẩn, TP Đà Nẵng');
insert into khachhang values ('551122334',N'Trần Thị Khánh Vân',N'1A Hồ Tùng Mậu, Đà Lạt');
insert into khachhang values ('987654321',N'Hồ Thanh Sơn',N'209 Trần Hưng Đạo, Q5, TP HCM');
select * from khachhang;
//nhap lieu cho bang ngan hang
insert into nganhang values ('1', N'Ngân Hàng Công Thương');
insert into nganhang values ('2', N'Ngân Hàng Ngoại Thương');
insert into nganhang values ('3', N'Ngân Hàng Nông Nghiệp');
insert into nganhang values ('4', N'Ngân Hàng Á Châu');
insert into nganhang values ('5', N'Ngân Hàng Thương Tín');
select * from  nganhang;
//nhap lieu cho bang chi nhanh
insert into chinhanh values ('1','CN01',N'Đà Lạt',2000000000);
insert into chinhanh values ('2','CN02',N'Nha Trang',2700000000);
insert into chinhanh values ('3','CN03',N'Thanh Hóa',4500000000);
insert into chinhanh values ('4','CN04',N'TP HCM',6000000000);
insert into chinhanh values ('5','CN05',N'Đà Nẵng',7000000000);
insert into chinhanh values ('1','CN11',N'TP HCM',5000000000);
insert into chinhanh values ('2','CN12',N'Huế',1400000000);
insert into chinhanh values ('3','CN13',N'Đà Nẵng',3600000000);
insert into chinhanh values ('4','CN14',N'Hà Nội',5700000000);
insert into chinhanh values ('1','CN21',N'Hà Nội',3500000000);
insert into chinhanh values ('2','CN22',N'Hà Nội',4500000000);
insert into chinhanh values ('3','CN23',N'Đà Lạt',2400000000);
insert into chinhanh values ('1','CN31',N'Đà Nẵng',4000000000);
insert into chinhanh values ('2','CN32',N'TP HCM',5600000000);
insert into chinhanh values ('3','CN33',N'Cần Thơ',5400000000);
insert into chinhanh values ('3','CN43',N'Nam Định',3600000000);
select * from chinhanh;
//nhap lieu cho bang tai khoan vay
insert into taikhoanvay values ('111222333','CN01','10001A',10000000);
insert into taikhoanvay values ('333111222','CN02','10002A',60000000);
insert into taikhoanvay values ('551122334','CN04','10004A',20000000);
insert into taikhoanvay values ('221133445','CN05','10005G',15000000);
insert into taikhoanvay values ('987654321','CN11','10001D',45000000);
insert into taikhoanvay values ('112233445','CN12','10002D',12000000);
insert into taikhoanvay values ('441122335','CN13','10003F',55000000);
insert into taikhoanvay values ('123123123','CN14','10005A',12500000);
select * from taikhoanvay;
//nhap lieu cho bang tai khoan goi
insert into taikhoangoi values ('123123123','CN01','00001A',10000000);
insert into taikhoangoi values ('123456789','CN01','00001C',127000000);
insert into taikhoangoi values ('221133445','CN02','00002A',12500000);
insert into taikhoangoi values ('456456456','CN03','00003H',123000000);
insert into taikhoangoi values ('222111333','CN05','00005A',1200000);
insert into taikhoangoi values ('987654321','CN05','00005D',345000000);
insert into taikhoangoi values ('123412341','CN05','00005N',45000000);
insert into taikhoangoi values ('331122445','CN13','00003A',27000000);
insert into taikhoangoi values ('551122334','CN14','00004D',560000000);
insert into taikhoangoi values ('123456789','CN14','00004P',35400000);
insert into taikhoangoi values ('123412341','CN21','00001B',67000000);
insert into taikhoangoi values ('222111333','CN22','00002G',56000000);
insert into taikhoangoi values ('987654321','CN23','00004F',4500000);
insert into taikhoangoi values ('333111222','CN33','00003D',47000000);
select * from taikhoangoi;

--1. Tìm tên tất cả các ngân hàng có chi nhánh ngân hàng ở thanh phố “Da Lat”.
select nh.MaNH, nh.TenNH
from nganhang nh
join chinhanh cn on cn.MaNH = nh.MaNH
where ThanhPhoCN = 'Đà Lạt';
--2. Tìm tất cả những thành phố mà có chi nhánh của ngân hàng công thương.
select cn.ThanhPhoCN
from chinhanh cn
join nganhang nh on nh.MaNH = cn.MaNH
where TenNH = 'Ngân Hàng Công Thương';
--3. Tìm thông tin về tất cả các chi nhánh của ngân hàng công thương có địa điểm ở TPHCM.
select *
from chinhanh cn
join nganhang nh on nh.MaNH = cn.MaNH
where ThanhPhoCN = 'TP HCM';
--4. Xuất thông tin từng ngân hàng và chi nhánh của nó.
select nh.MaNH, nh.TenNH, cn.MaCN, cn.ThanhPhoCN, cn.TaiSan
from nganhang nh
join chinhanh cn on cn.MaNH = nh.MaNH
--5. Tìm khách hàng mà địa chỉ của họ ở 'Ha Noi'.
select *
from khachhang
where DiaChi like N'%Hà Nội%'
--6. Tìm các khách hàng có tên Son.
select * 
from khachhang
where TenKH like N'%Sơn%';
--7. Tìm các khách hàng mà địa chỉ của họ ở đường "Tran Hung Dao".
select *
from khachhang
where DiaChi like N'%Trần Hưng Đạo%'
--8. Tìm các khách hàng có tên "Thao".
select * 
from khachhang
where TenKH like N'%Thảo%';
--9. Tìm khách hàng có mã số bắt đầu là '11' và ở TP HCM.
select *
from khachhang
where MaKH LIKE '11%' and  DiaChi like N'%TP HCM%';
--10. Xuất thông tin về tên ngân hàng, thành phố chi nhánh và tài sản theo thứ tự tăng của tài sản của chi nhánh, nếu tài sản trùng nhau thì sắp tăng theo thành phố chi nhánh.
select nh.TenNH,
       cn.ThanhPhoCN,
       cn.TaiSan
from nganhang nh
join chinhanh cn on nh.MaNH = cn.MaNH
order by cn.TaiSan asc,
         cn.ThanhPhoCN asc;
--11. Tìm thông tin tất cả những thông tin về ngân hàng và chi nhánh ngân hàng mà tài sản 3000000000 < tài sản < 5000000000.
select nh.*, cn.*
from nganhang nh
join chinhanh cn on nh.MaNH = cn.MaNH
where cn.TaiSan between 3000000000 and 5000000000;
--12. Cho biết tài sản trung bình chi nhánh của từng ngân hàng.
select nh.MaNH,
       nh.TenNH,
       avg(cn.TaiSan) as taisan_trungbinh
from nganhang nh
join chinhanh cn on nh.MaNH = cn.MaNH
group by nh.MaNH, nh.TenNH;
--13. Tìm thông tin của khách hàng có tài khoản vay tại ngân hàng công thương và có tên là 'Thao'.
select distinct kh.*
from khachhang kh
join taikhoanvay tkv on kh.MaKH = tkv.MaKH
join chinhanh cn on tkv.MaCN = cn.MaCN
join nganhang nh on cn.MaNH = nh.MaNH
where nh.TenNH = n'Ngân Hàng Công Thương'
  and kh.TenKH like n'%Thảo%';
--14. Xuất thông tin về tên ngân hàng và tổng tài sản của các ngân hàng.
select nh.MaNH,
       nh.TenNH,
       avg(cn.TaiSan) as taisan_trungbinh
from nganhang nh
join chinhanh cn on nh.MaNH = cn.MaNH
group by nh.MaNH, nh.TenNH;
--15. Tìm MaCN và TaiSan của chi nhánh có tài sản lớn nhất.
select cn.MaCN,
       cn.TaiSan
from chinhanh cn
where cn.TaiSan = (
    select max(TaiSan)
    from chinhanh
);
--16. Liệt kê tất cả những những khách hành có tài khoản gởi tại chi nhánh ngân hàng “A Chau”.
select distinct kh.MaKH,
       kh.TenKH,
       kh.DiaChi
from khachhang kh
join taikhoangoi tkg on kh.MaKH = tkg.MaKH
join chinhanh cn on tkg.MaCN = cn.MaCN
join nganhang nh on cn.MaNH = nh.MaNH
where nh.TenNH = n'Ngân Hàng Á Châu';
--17. Tìm tất cả các số tài khoản vay thực hiện tại chi nhánh của ngân hàng ngoại thương mà số tiền vay > 1200000.
select tkv.SoTKV,
       tkv.SoTienVay
from taikhoanvay tkv
join chinhanh cn on tkv.MaCN = cn.MaCN
join nganhang nh on cn.MaNH = nh.MaNH
where nh.TenNH = n'Ngân Hàng Ngoại Thương'
  and tkv.SoTienVay > 1200000;
--18. Tính tổng số tiền mà mỗi chi nhánh ngân hàng đang được khách hàng gởi.
select cn.MaCN,
       cn.ThanhPhoCN,
       sum(tkg.SoTienGoi) as tong_tien_goi
from chinhanh cn
join taikhoangoi tkg on cn.MaCN = tkg.MaCN
group by cn.MaCN, cn.ThanhPhoCN;
--19. Xuất thông tin về tài khoản vay và tài khoản gởi hiện có của tất cả các khách hàng có tên là 'Son'.
select kh.MaKH,
       kh.TenKH,
       tkv.SoTKV,
       tkv.SoTienVay,
       tkg.SoTKG,
       tkg.SoTienGoi
from khachhang kh
left join taikhoanvay tkv on kh.MaKH = tkv.MaKH
left join taikhoangoi tkg on kh.MaKH = tkg.MaKH
where kh.TenKH like n'%Sơn%';
--20. Tìm thông tin về khách hàng có tổng số tiền vay tại tất cả các ngân hàng > 30000000.
select kh.MaKH,
       kh.TenKH,
       sum(tkv.SoTienVay) as tong_tien_vay
from khachhang kh
join taikhoanvay tkv on kh.MaKH = tkv.MaKH
group by kh.MaKH, kh.TenKH
having sum(tkv.SoTienVay) > 30000000;

