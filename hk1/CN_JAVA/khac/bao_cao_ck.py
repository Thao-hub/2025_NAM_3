src
└── main
    ├── java
    │   └── com.tenban.quanlysv
    │       │
    │       ├── Model
    │       │   ├── CSDL.java        // "Siêu file" chứa *tất cả* logic CSDL:
    │       │   │                  // - Kết nối DB
    │       │   │                  // - CRUD cho SinhVien, TaiKhoan, Khoa, Lop, Diem
    │       │   │                  // - Hàm checkLogin, checkSignup (với mã hóa mật khẩu)
    │       │   │                  // - Hàm searchStudentByName(keyword)
    │       │   │                  // - Hàm getStudentsPaging(pageIndex)
    │       │   │                  // - Hàm getTotalStudents() (để phân trang)
    │       │   │                  // - Hàm getGradesByStudentID(maSV)
    │       │   │
    │       │   ├── SinhVien.java    // (Thêm thuộc tính String avatarURL)
    │       │   ├── TaiKhoan.java    // (Thêm thuộc tính String role: "admin" hoặc "student")
    │       │   ├── Khoa.java        // (Mới) POJO cho Khoa (maKhoa, tenKhoa)
    │       │   ├── Lop.java         // (Mới) POJO cho Lớp (maLop, tenLop, maKhoa)
    │       │   ├── MonHoc.java      // (Mới) POJO cho Môn học (maMH, tenMH, soTinChi)
    │       │   └── Diem.java        // (Mới) POJO cho Điểm (id, maSV, maMH, diem)
    │       │
    │       ├── Servlets (Controller)
    │       │   │ //--- Servlets xác thực ---
    │       │   ├── LoginServlet.java
    │       │   ├── LogoutServlet.java
    │       │   ├── SignupServlet.java
    │       │   │
    │       │   │ //--- Servlets chức năng Admin ---
    │       │   ├── AdminDashboardServlet.java   // Trang chủ của Admin
    │       │   ├── StudentManageServlet.java    // Xử lý (GET) hiển thị DS Sinh Viên (có Phân Trang + Tìm Kiếm)
    │       │   ├── AddStudentServlet.java       // Xử lý (POST) thêm SV (có Upload ảnh)
    │       │   ├── EditStudentServlet.java      // Xử lý (POST) sửa SV (có Upload ảnh)
    │       │   ├── DeleteStudentServlet.java    // Xử lý (GET/POST) xóa SV
    │       │   │
    │       │   ├── DepartmentManageServlet.java // (Mới) CRUD cho Khoa
    │       │   ├── ClassManageServlet.java      // (Mới) CRUD cho Lớp
    │       │   ├── GradeManageServlet.java      // (Mới) CRUD cho Điểm
    │       │   │
    │       │   │ //--- Servlets chức năng Student ---
    │       │   ├── StudentDashboardServlet.java // (Mới) Trang chủ của Sinh Viên
    │       │   ├── StudentViewInfoServlet.java  // (Mới) Xem thông tin cá nhân
    │       │   └── StudentViewGradeServlet.java // (Mới) Xem bảng điểm cá nhân
    │       │
    │       └── Utils (Nên có)
    │           └── PasswordHashing.java // (Mới) Chứa hàm băm và xác thực mật khẩu
    │
    └── webapp
        ├── css
        │   └── style.css
        ├── Images
        ├── js
        │   └── main.js
        │
        ├── uploads         // (MỚI) Thư mục chứa ảnh avatar do người dùng upload lên
        │   └── avatars
        │
        ├── META-INF
        ├── WEB-INF
        │   └── web.xml
        │
        │ //--- Trang chung ---
        ├── login.jsp
        ├── signin.jsp
        ├── index.jsp       // Trang chủ (thường sẽ tự điều hướng nếu đã login)
        │
        │ //--- Trang của Admin ---
        ├── admin_dashboard.jsp
        ├── admin_manage_student.jsp  // (Nâng cấp) Có ô Search, có nút Phân Trang
        ├── admin_add_student.jsp     // (Nâng cấp) Có <select> chọn Khoa/Lớp, có <input type="file">
        ├── admin_edit_student.jsp    // (Nâng cấp) Tương tự trang add
        ├── admin_manage_department.jsp // (Mới)
        ├── admin_manage_class.jsp      // (Mới)
        ├── admin_manage_grades.jsp     // (Mới)
        │
        │ //--- Trang của Sinh Viên (Role: student) ---
        ├── student_dashboard.jsp     // (Mới)
        ├── student_info.jsp          // (Mới)
        └── student_grades.jsp        // (Mới)
        │
        └── (Optional)
            ├── admin_header.jsp      // (Tách file) Dùng <%@include ... %> để nhúng
            ├── admin_sidebar.jsp     // (Tách file)
            └── footer.jsp