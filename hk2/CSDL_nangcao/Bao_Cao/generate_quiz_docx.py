from __future__ import annotations

import os
import zipfile
from xml.sax.saxutils import escape


OUTPUT_PATH = r"D:\2025_NAM_3\hk2\AI\Ly_Thuyet\100_cau_hoi_trac_nghiem_AI.docx"


QUESTIONS = [
    ("Least Squares trong Linear Regression dùng để làm gì?", ["Tối đa hóa khoảng cách", "Tối thiểu hóa tổng bình phương sai số", "Tăng số chiều", "Giảm số mẫu"], "B"),
    ("Mô hình hồi quy tuyến tính đơn có dạng nào?", ["y=b0+b1x+e", "y=1/x", "y=log x", "y=x^2+e"], "A"),
    ("Trong hồi quy tuyến tính đơn, b1 biểu diễn gì?", ["Tung độ gốc", "Độ dốc", "Phương sai", "Xác suất"], "B"),
    ("Giá trị dự đoán trong Linear Regression thường ký hiệu là gì?", ["x_hat", "y_bar", "y_hat", "e_hat"], "C"),
    ("Sai số residual được tính bằng?", ["y_hat-y", "y-y_hat", "x-y", "x-y_hat"], "B"),
    ("Multiple Linear Regression dùng khi nào?", ["Có nhiều biến mục tiêu", "Có nhiều biến đầu vào", "Không có nhãn", "Chỉ có dữ liệu ảnh"], "B"),
    ("Công thức OLS ma trận đúng là?", ["Xy", "(X^T X)^(-1)X^T y", "X^-1 y", "X^T y^-1"], "B"),
    ("Điều kiện quan trọng để dùng (X^T X)^(-1) là gì?", ["X vuông", "X^T X khả nghịch", "y dương", "X chuẩn hóa"], "B"),
    ("Trang ceb nào đúng với Multiple Linear Regression?", ["meanShift.html", "matrix.html", "linearRegression.html", "dbscan.html"], "C"),
    ("Trang ceb nào hỗ trợ phần ma trận nghịch đảo?", ["matrix.html", "classify.html", "pca.html", "knn.html"], "A"),
    ("LDA là viết tắt của gì?", ["Latent Data Approximation", "Linear Discriminant Analysis", "Logistic Discrete Algorithm", "Linear Distance Analysis"], "B"),
    ("Mục tiêu chính của LDA là gì?", ["Phân cụm không giám sát", "Tách lớp tốt nhất giữa các nhóm", "Dự báo chuỗi thời gian", "Tìm luật kết hợp"], "B"),
    ("Trong LDA, mỗi lớp được đặc trưng bởi gì?", ["Mean vector", "Cây quyết định", "Mạng nơ-ron", "Luật Apriori"], "A"),
    ("LDA giả thiết điều gì về covariance?", ["Mỗi lớp có covariance khác nhau hoàn toàn", "Tất cả lớp dùng chung covariance", "Covariance bằng 0", "Không dùng covariance"], "B"),
    ("Trong công thức LDA, pi_k là gì?", ["Learning rate", "Prior probability", "Loss function", "Bandwidth"], "B"),
    ("Luật dự đoán của LDA là gì?", ["Chọn lớp có khoảng cách lớn nhất", "Chọn lớp có delta_k(x) lớn nhất", "Chọn lớp có phương sai nhỏ nhất", "Chọn ngẫu nhiên"], "B"),
    ("Link ceb tương ứng với LDA là?", ["linearDescriminantAnalysis.html", "simpleLinearRegression.html", "adaboost.html", "kmean.html"], "A"),
    ("Multiple-Class LDA nghĩa là gì?", ["Chỉ áp dụng cho 2 lớp", "Áp dụng cho từ 3 lớp trở lên", "Chỉ cho dữ liệu văn bản", "Chỉ cho hồi quy"], "B"),
    ("Theo tài liệu scikit-learn, LDA vừa là classifier vừa có thể dùng để làm gì?", ["Mã hóa ảnh", "Giảm chiều", "Tăng dữ liệu", "Gắn nhãn thủ công"], "B"),
    ("QDA khác LDA chủ yếu ở điểm nào?", ["QDA không dùng xác suất", "QDA cho phép covariance riêng cho từng lớp", "QDA chỉ dùng cho 2 lớp", "QDA là phân cụm"], "B"),
    ("One-vs-Rest trong multiclass nghĩa là gì?", ["So từng cặp lớp", "Mỗi lần một lớp so với tất cả lớp còn lại", "Chỉ dùng cho 2 lớp", "Bỏ qua lớp hiếm"], "B"),
    ("One-vs-One nghĩa là gì?", ["Gộp tất cả lớp", "So từng cặp lớp với nhau", "Chỉ dùng cho hồi quy", "Chỉ dùng cho KNN"], "B"),
    ("Với 4 lớp, One-vs-One cần bao nhiêu bộ phân loại?", ["4", "5", "6", "8"], "C"),
    ("Với 5 lớp, One-vs-Rest cần bao nhiêu bộ phân loại?", ["3", "4", "5", "10"], "C"),
    ("Logistic Regression chủ yếu dùng cho bài toán nào?", ["Clustering", "Classification", "Matrix inversion", "Sampling"], "B"),
    ("Hàm kích hoạt cơ bản trong Logistic Regression là?", ["ReLU", "Softmax", "Sigmoid", "Tanh"], "C"),
    ("Giá trị đầu ra của sigmoid nằm trong khoảng nào?", ["(-inf, inf)", "(0,1)", "[-1,1]", "[0,100]"], "B"),
    ("Nếu xác suất dự đoán là 0.83 và ngưỡng là 0.5, mô hình logistic thường dự đoán gì?", ["Lớp 0", "Lớp 1", "Không dự đoán được", "Ngoại lệ"], "B"),
    ("Trang ceb nào có nhắc trực tiếp LogisticRegression?", ["classify.html", "matrix.html", "meanShift.html", "apriori.html"], "A"),
    ("sgcClassifier.html trên ceb mô tả mô hình gần với gì?", ["Logistic classifier dùng sigmoid", "K-means", "Decision Tree", "PCA"], "A"),
    ("Confusion Matrix cho bài toán nhị phân có bao nhiêu thành phần cơ bản?", ["2", "3", "4", "5"], "C"),
    ("TP là gì?", ["Dự đoán âm sai", "Dự đoán dương đúng", "Dự đoán âm đúng", "Tổng mẫu dương"], "B"),
    ("Precision được tính bằng?", ["TP/(TP+FP)", "TP/(TP+FN)", "TN/(TN+FP)", "(TP+TN)/N"], "A"),
    ("Recall được tính bằng?", ["TP/(TP+FP)", "TP/(TP+FN)", "TN/(TN+FN)", "FP/(TP+FP)"], "B"),
    ("Accuracy là gì?", ["Tỉ lệ dự đoán đúng trên tổng số mẫu", "Tỉ lệ dương đúng trên mẫu dương", "Trung bình precision và recall", "Tỉ lệ âm đúng"], "A"),
    ("F1-score là trung bình gì?", ["Cộng", "Hình học", "Điều hòa giữa Precision và Recall", "Có trọng số theo lớp luôn luôn"], "C"),
    ("ROC curve biểu diễn mối quan hệ giữa?", ["Precision và Recall", "TPR và FPR", "Accuracy và Loss", "SSE và MSE"], "B"),
    ("AUC càng lớn thì thường có nghĩa gì?", ["Mô hình phân biệt lớp tốt hơn", "Mô hình tệ hơn", "Dữ liệu ít hơn", "Mô hình overfit chắc chắn"], "A"),
    ("Giá trị AUC của mô hình ngẫu nhiên xấp xỉ bao nhiêu?", ["0", "0.25", "0.5", "1.0"], "C"),
    ("Nếu tăng ngưỡng phân loại trong logistic, thường điều gì xảy ra?", ["Recall tăng mạnh mọi lúc", "Số mẫu dự đoán dương giảm", "AUC về 0", "Dữ liệu đổi nhãn"], "B"),
    ("Mean Shift thuộc nhóm nào?", ["Supervised classification", "Supervised regression", "Unsupervised clustering", "Reinforcement learning"], "C"),
    ("Mean Shift dùng tham số quan trọng nào?", ["Depth", "Bandwidth", "Epoch", "Lambda"], "B"),
    ("Trong Mean Shift, điểm mới được cập nhật theo gì?", ["Trung bình các điểm lân cận", "Median toàn cục", "Gradient âm", "Nhãn lớp"], "A"),
    ("Link ceb tương ứng với Mean Shift là?", ["dbscan.html", "clustering.html", "meanShift.html", "classify.html"], "C"),
    ("Mean Shift có cần biết trước số cụm như K-Means không?", ["Có, luôn luôn", "Không nhất thiết", "Chỉ khi dữ liệu lớn", "Chỉ khi 2 chiều"], "B"),
    ("Dữ liệu nào phù hợp với bài toán regression hơn classification?", ["Dự đoán giá nhà", "Phân loại email spam", "Nhận diện mèo/chó", "Phân loại bệnh có/không"], "A"),
    ("Dữ liệu nào phù hợp với classification hơn regression?", ["Dự đoán doanh thu", "Dự đoán nhiệt độ", "Dự đoán đậu/rớt", "Dự đoán giá cổ phiếu"], "C"),
    ("Khi số lớp lớn hơn 2, confusion matrix sẽ?", ["Vẫn luôn 2x2", "Thành ma trận K x K", "Không dùng được", "Chỉ còn 1 hàng"], "B"),
    ("Weighted F1 trong multiclass dùng để làm gì?", ["Bỏ qua lớp lớn", "Tính F1 có xét trọng số số mẫu từng lớp", "Thay accuracy bằng recall", "Chỉ dùng cho regression"], "B"),
    ("Trong chuỗi tài liệu đã cho, chủ đề nào là tài liệu tham khảo chuẩn nhất cho Multiple-Class LDA?", ["Video Mean Shift", "scikit-learn lda_qda", "Video ROC AUC", "matrix.html"], "B"),
    ("Trong hồi quy tuyến tính đơn, beta0 thường được gọi là gì?", ["Hệ số góc", "Intercept", "Residual", "Threshold"], "B"),
    ("Nếu beta1 > 0 thì khi x tăng, y dự đoán thường sẽ?", ["Giảm", "Không đổi", "Tăng", "Bằng 0"], "C"),
    ("Nếu beta1 < 0 thì mối quan hệ giữa x và y là?", ["Đồng biến", "Nghịch biến", "Phi tuyến", "Ngẫu nhiên"], "B"),
    ("Mục tiêu của OLS là tối thiểu hóa đại lượng nào?", ["MAE", "Tổng bình phương phần dư", "Độ lệch chuẩn của x", "Số biến độc lập"], "B"),
    ("Trong multiple linear regression, p thường là gì?", ["Số lớp", "Số quan sát", "Số biến đầu vào", "Số cụm"], "C"),
    ("R-squared càng gần 1 thì thường biểu thị điều gì?", ["Mô hình khớp dữ liệu tốt hơn", "Dữ liệu sai", "Mô hình chắc chắn overfit", "Biến mục tiêu âm"], "A"),
    ("Adjusted R-squared được dùng để?", ["Loại bỏ mọi lỗi", "Điều chỉnh theo số biến đầu vào", "Thay precision", "Chuẩn hóa dữ liệu"], "B"),
    ("Residual Standard Error phản ánh gì?", ["Độ lớn sai số dự đoán điển hình", "Số lớp", "Tốc độ học", "Khoảng cách giữa các cụm"], "A"),
    ("Khoảng tin cậy 95% của hệ số hồi quy dùng để?", ["Ước lượng miền giá trị hợp lý của hệ số", "Tính số cụm", "Tăng accuracy", "Chuẩn hóa nhãn"], "A"),
    ("Trong ma trận thiết kế X của hồi quy đa biến, cột đầu toàn số 1 dùng cho?", ["Giảm chiều", "Hệ số chặn beta0", "Chuẩn hóa", "Kiểm tra null"], "B"),
    ("Nếu hai biến đầu vào gần như tuyến tính phụ thuộc mạnh, hồi quy có thể gặp vấn đề gì?", ["Multicollinearity", "Underfitting chắc chắn", "Clustering", "Sampling bias"], "A"),
    ("Matrix transpose của X thường ký hiệu là?", ["X^-1", "X^2", "X^T", "det(X)"], "C"),
    ("Matrix inverse chỉ tồn tại khi nào?", ["Ma trận khả nghịch", "Ma trận toàn số 0", "Ma trận luôn vuông ảo", "Mọi ma trận đều có"], "A"),
    ("Determinant bằng 0 thì ma trận vuông thường?", ["Khả nghịch", "Không khả nghịch", "Đối xứng", "Đơn vị"], "B"),
    ("Trong LDA, dữ liệu huấn luyện thường gồm?", ["Chỉ X", "Chỉ y", "Các cặp (X_i, y_i)", "Chỉ covariance"], "C"),
    ("Trong LDA, n_k là gì?", ["Số biến", "Số mẫu của lớp k", "Số cụm", "Số vòng lặp"], "B"),
    ("Mean vector mu_k đại diện cho?", ["Trung tâm đặc trưng của lớp k", "Sai số lớp k", "Ngưỡng lớp k", "Độ chính xác lớp k"], "A"),
    ("Pooled covariance trong LDA kết hợp thông tin gì?", ["Covariance của các lớp", "Chỉ covariance lớp 1", "Chỉ mean vector", "Chỉ prior"], "A"),
    ("Trong LDA, w_k = Sigma^-1 mu_k là gì?", ["Ngẫu nhiên hóa dữ liệu", "Hệ số tuyến tính cho lớp k", "Xác suất hậu nghiệm", "Đạo hàm loss"], "B"),
    ("Bias b_k trong LDA phụ thuộc vào gì?", ["Mu_k và prior", "Chỉ bandwidth", "Chỉ F1-score", "Chỉ số lớp"], "A"),
    ("Predict_proba trong LDA trả về gì?", ["Khoảng cách Euclid", "Xác suất hậu nghiệm theo lớp", "Hệ số góc", "Số cụm"], "B"),
    ("Nếu bài toán có K lớp, LDA trả về dự đoán bằng cách?", ["Chọn lớp có loss nhỏ nhất", "Chọn lớp có delta_k lớn nhất", "Chọn lớp có prior nhỏ nhất", "Chọn lớp bất kỳ"], "B"),
    ("QDA tạo biên quyết định như thế nào so với LDA?", ["Luôn tuyến tính hơn", "Có thể phi tuyến dạng bậc hai", "Không có biên", "Giống hệt KNN"], "B"),
    ("One-vs-One thường tạo số bộ phân loại bằng?", ["K", "K-1", "K(K-1)/2", "2K"], "C"),
    ("One-vs-Rest thường tạo số bộ phân loại bằng?", ["K", "K^2", "K/2", "2"], "A"),
    ("Multiclass classification là gì?", ["Bài toán chỉ có 1 lớp", "Bài toán có từ 3 lớp trở lên", "Bài toán không nhãn", "Bài toán hồi quy"], "B"),
    ("Logistic Regression mô hình hóa trực tiếp đại lượng nào?", ["Xác suất của lớp", "Khoảng cách cụm", "Giá trị trung bình", "Ma trận hiệp phương sai"], "A"),
    ("Đầu ra của logistic regression trước khi qua sigmoid thường ký hiệu là?", ["z", "mu", "pi", "h"], "A"),
    ("Nếu z = 0 thì sigmoid(z) bằng bao nhiêu?", ["0", "0.25", "0.5", "1"], "C"),
    ("Ngưỡng mặc định phổ biến để đổi xác suất thành nhãn trong logistic là?", ["0.1", "0.3", "0.5", "0.9"], "C"),
    ("Log loss trong logistic regression phạt mạnh nhất khi nào?", ["Dự đoán sai với độ tin cao", "Dự đoán đúng chắc chắn", "Dữ liệu cân bằng", "Có ít biến"], "A"),
    ("Trong bài toán mất cân bằng lớp, accuracy có thể?", ["Luôn đáng tin", "Dễ gây hiểu lầm", "Bằng F1", "Bằng AUC"], "B"),
    ("Precision cao thường có nghĩa là?", ["Ít false positive hơn", "Ít false negative hơn", "Nhiều true negative hơn tuyệt đối", "AUC thấp"], "A"),
    ("Recall cao thường có nghĩa là?", ["Ít false negative hơn", "Ít false positive hơn", "R-squared cao", "Bandwidth nhỏ"], "A"),
    ("F1-score phù hợp khi nào?", ["Khi muốn cân bằng precision và recall", "Khi chỉ quan tâm TN", "Khi làm clustering", "Khi tính ma trận nghịch đảo"], "A"),
    ("Specificity là gì?", ["TPR", "TNR", "FPR", "FNR"], "B"),
    ("FPR được tính bằng?", ["FP/(FP+TN)", "TP/(TP+FN)", "TN/(TN+FP)", "FN/(TP+FP)"], "A"),
    ("TPR còn được gọi là gì?", ["Recall", "Precision", "Specificity", "Support"], "A"),
    ("ROC curve tốt hơn thường nằm ở đâu?", ["Gần đường chéo", "Gần góc trên bên trái", "Gần trục hoành", "Gần gốc tọa độ"], "B"),
    ("Đường chéo trong ROC thường biểu diễn?", ["Bộ phân loại ngẫu nhiên", "Bộ phân loại hoàn hảo", "Mô hình overfit", "K-means"], "A"),
    ("AUC = 1 biểu thị?", ["Mô hình rất kém", "Mô hình phân biệt hoàn hảo", "Mô hình ngẫu nhiên", "Dữ liệu lỗi"], "B"),
    ("Confusion matrix của bài toán 3 lớp có kích thước?", ["2x2", "3x3", "3x2", "1x3"], "B"),
    ("Support trong báo cáo phân loại là gì?", ["Số mẫu thực của từng lớp", "Số biến", "Số epoch", "Số cụm"], "A"),
    ("Macro average trong multiclass thường là?", ["Trung bình không trọng số giữa các lớp", "Chỉ lấy lớp lớn nhất", "Trung bình có trọng số theo support", "Bỏ lớp nhỏ"], "A"),
    ("Weighted average trong multiclass thường là?", ["Trung bình có xét support", "Trung bình hình học", "Chỉ lớp hiếm", "Chỉ lớp đa số"], "A"),
    ("Mean Shift dựa trên ý tưởng gì?", ["Dịch chuyển điểm về vùng mật độ cao", "Tách bằng siêu phẳng", "Tối thiểu hóa SSE toàn cục", "Xây cây nhị phân"], "A"),
    ("Bandwidth trong Mean Shift ảnh hưởng trực tiếp đến?", ["Kích thước lân cận", "Số nhãn", "Hàm sigmoid", "R-squared"], "A"),
    ("Bandwidth quá nhỏ trong Mean Shift có thể dẫn đến?", ["Quá nhiều cụm", "Quá ít cụm", "Không cần tính khoảng cách", "Độ chính xác luôn cao"], "A"),
    ("Bandwidth quá lớn trong Mean Shift có thể dẫn đến?", ["Nhiều cụm nhỏ", "Ít cụm hơn do gộp", "Không tính được mean", "Tăng số chiều"], "B"),
    ("Khoảng cách thường dùng trong Mean Shift ví dụ trên ceb là?", ["Manhattan", "Cosine", "Euclidean", "Hamming"], "C"),
    ("KNN thuộc nhóm bài toán nào khi dùng dự đoán nhãn?", ["Classification", "Regression tuyến tính", "Association rules", "Dimension reduction"], "A"),
    ("Decision boundary của logistic regression nhị phân thường là?", ["Tuyến tính trong không gian đặc trưng gốc", "Cây phân cấp", "Cụm tròn", "Không xác định"], "A"),
    ("Trong phân loại, false negative là gì?", ["Dự đoán dương nhưng thực âm", "Dự đoán âm nhưng thực dương", "Dự đoán dương và thực dương", "Dự đoán âm và thực âm"], "B"),
    ("Trong phân loại, false positive là gì?", ["Dự đoán dương nhưng thực âm", "Dự đoán âm nhưng thực dương", "Dự đoán âm và thực âm", "Dự đoán đúng lớp"], "A"),
    ("Nếu precision = 1 thì điều gì đúng?", ["Không có false positive", "Không có false negative", "Accuracy = 1", "Recall = 1"], "A"),
    ("Nếu recall = 1 thì điều gì đúng?", ["Không có false positive", "Không có false negative", "Precision = 1", "AUC = 1"], "B"),
    ("Bài toán dự đoán giá bán là ví dụ của?", ["Clustering", "Classification", "Regression", "LDA"], "C"),
    ("Bài toán dự đoán khách hàng rời bỏ hay không là ví dụ của?", ["Regression", "Classification", "Clustering", "Matrix factorization"], "B"),
    ("Dữ liệu không có nhãn thường phù hợp hơn với?", ["Supervised classification", "Supervised regression", "Unsupervised learning", "Logistic regression"], "C"),
    ("Trong LDA, prior probability của lớp phản ánh?", ["Tỉ lệ xuất hiện lớp trong dữ liệu", "Khoảng cách trung bình", "Độ lớn bandwidth", "Số biến đầu vào"], "A"),
    ("LDA và Logistic Regression đều có thể dùng cho?", ["Phân loại", "Phân cụm", "Nghịch đảo ma trận", "Luật kết hợp"], "A"),
    ("Khác biệt lớn giữa LDA và Logistic Regression là?", ["LDA có giả định phân phối theo lớp", "Logistic không cần dữ liệu", "LDA là unsupervised", "Logistic là clustering"], "A"),
    ("Trong scikit-learn, LDA có thể dùng làm transformer vì lý do gì?", ["Có thể chiếu dữ liệu sang không gian phân biệt", "Có thể tạo văn bản", "Có thể nhân ma trận ngẫu nhiên", "Có thể tìm luật"], "A"),
    ("Nếu số chiều lớn và số mẫu ít, việc tính covariance có thể gặp?", ["Bài toán suy biến", "AUC tăng", "Precision = 1", "Không ảnh hưởng"], "A"),
    ("Mô hình nào trong danh sách của bạn là thuật toán phân cụm?", ["Mean Shift", "Logistic Regression", "LDA", "Confusion Matrix"], "A"),
    ("Mô hình nào trong danh sách của bạn là thước đo đánh giá chứ không phải thuật toán học?", ["ROC-AUC", "Mean Shift", "LDA", "Multiple Linear Regression"], "A"),
    ("Confusion Matrix dùng để?", ["Đánh giá kết quả phân loại", "Chuẩn hóa dữ liệu", "Tạo biến mới", "Giảm chiều"], "A"),
    ("AUC viết tắt của gì?", ["Area Under Curve", "Average Unit Class", "Automatic Update Criterion", "Area Upper Class"], "A"),
    ("ROC viết tắt của gì?", ["Rate of Classification", "Receiver Operating Characteristic", "Regression Output Curve", "Relative Optimal Classifier"], "B"),
    ("Khi dữ liệu rất mất cân bằng, chỉ số nào thường hữu ích hơn accuracy?", ["Precision, Recall, F1, ROC-AUC", "Chỉ R-squared", "Chỉ MSE", "Chỉ SSE"], "A"),
    ("Trong hồi quy, SSE là viết tắt của?", ["Sum of Squared Errors", "Sample Standard Estimate", "Scaled Squared Euclid", "Sequential Score Error"], "A"),
    ("Trong hồi quy, phần dư e được định nghĩa là?", ["y_hat - y", "y - y_hat", "x - y", "y / x"], "B"),
    ("Nếu R-squared âm trên tập kiểm tra, điều đó thường gợi ý?", ["Mô hình kém hơn dự đoán bằng giá trị trung bình", "Mô hình hoàn hảo", "Dữ liệu không có y", "Ma trận luôn khả nghịch"], "A"),
    ("Trong logistic regression đa lớp, một mở rộng phổ biến là?", ["Softmax regression", "DBSCAN", "Apriori", "PCA whitening"], "A"),
    ("Trong multiclass, weighted F1 bị ảnh hưởng nhiều hơn bởi?", ["Lớp có nhiều mẫu", "Lớp có ít mẫu", "Chỉ lớp đầu tiên", "Chỉ lớp cuối cùng"], "A"),
    ("Mean Shift có ưu điểm nào so với K-Means?", ["Không cần chỉ định trước số cụm", "Luôn nhanh hơn", "Không cần khoảng cách", "Chỉ dùng cho dữ liệu nhị phân"], "A"),
    ("K-Means và Mean Shift đều thuộc nhóm nào?", ["Regression", "Clustering", "Classification", "Recommendation"], "B"),
    ("Trong LDA đa lớp, số trục phân biệt tối đa thường là?", ["K", "K-1", "d+K", "N"], "B"),
    ("Trong báo cáo phân loại, precision thấp thường gợi ý gì?", ["Nhiều false positive", "Nhiều true positive", "Không có false negative", "AUC rất cao"], "A"),
    ("Recall thấp thường gợi ý gì?", ["Nhiều false negative", "Nhiều true negative", "Không có false positive", "R-squared cao"], "A"),
    ("Nếu mô hình dự đoán toàn bộ là lớp âm trong dữ liệu mất cân bằng, accuracy có thể?", ["Vẫn cao", "Luôn bằng 0", "Bằng AUC", "Bằng F1"], "A"),
    ("Tài liệu chính thức bạn đã đưa cho Multiple-Class LDA đến từ đâu?", ["Mahesh Huddar", "scikit-learn", "ceb matrix", "StatQuest ROC"], "B"),
    ("Video tiếng Việt về LDA trong danh sách là link nào?", ["GGZTgjvtsbw", "4jRBRDbJemM", "Kdsp6soqA7o", "OrfOXGeVyE4"], "A"),
    ("Video về Mean Shift trong danh sách là của kênh nào?", ["StatQuest", "Intellipaat", "OVNE", "Thai Le Hoang"], "B"),
    ("Video logistic regression tiếng Việt của OVNE trong danh sách là?", ["PVM7P6qXz-4", "3lwicUTEgHs", "JvS2triCgOY", "5vDGsDd0_K8"], "A"),
    ("Confusion Matrix solved example trong danh sách do ai đăng?", ["Josh Starmer", "Mahesh Huddar", "Intellipaat", "OVNE"], "B"),
    ("ROC and AUC clearly explained trong danh sách do ai đăng?", ["Mahesh Huddar", "Thai Le Hoang", "StatQuest with Josh Starmer", "Tiệp Nguyễn Vinh"], "C"),
    ("Trong ceb, trang classify.html nhấn mạnh thuật toán nhóm 2 cần thêm bước gì?", ["Scale dữ liệu", "Tính nghịch đảo ma trận tay", "Chỉ dùng LabelEncoder", "Không cần tiền xử lý"], "A"),
    ("Trong ceb, classify.html nhắc trực quan hóa gì khi đánh giá mô hình?", ["Confusion matrix", "Dendrogram", "Silhouette plot", "Scree plot"], "A"),
    ("Trong ceb, linearRegression.html mô tả mô hình nào?", ["Simple Linear Regression", "Multiple Linear Regression", "Logistic Regression", "LDA"], "B"),
    ("Trong ceb, simpleLinearRegression.html mô tả mô hình nào?", ["Simple Linear Regression", "Multiple Linear Regression", "Mean Shift", "QDA"], "A"),
    ("Trong ceb, matrix.html phục vụ trực tiếp nhất cho phần nào?", ["Hồi quy đa biến dùng ma trận nghịch đảo", "Confusion Matrix", "ROC curve", "Mean Shift"], "A"),
]


def p(text: str) -> str:
    return (
        "<w:p><w:r><w:t xml:space=\"preserve\">"
        + escape(text)
        + "</w:t></w:r></w:p>"
    )


def build_document_xml() -> str:
    blocks = [
        p("BO CAU HOI TRAC NGHIEM AI"),
        p("Chu de: Linear Regression, Multiple Linear Regression, Matrix Inverse, LDA, Multiclass, Logistic Regression, Confusion Matrix, ROC-AUC, Mean Shift"),
        p(""),
    ]
    for idx, (question, options, answer) in enumerate(QUESTIONS, start=1):
        blocks.append(p(f"Cau {idx}. {question}"))
        for label, option in zip(("A", "B", "C", "D"), options):
            blocks.append(p(f"{label}. {option}"))
        blocks.append(p(f"Dap an: {answer}"))
        blocks.append(p(""))

    body = "".join(blocks)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:wpc=\"http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas\" "
        "xmlns:mc=\"http://schemas.openxmlformats.org/markup-compatibility/2006\" "
        "xmlns:o=\"urn:schemas-microsoft-com:office:office\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\" "
        "xmlns:m=\"http://schemas.openxmlformats.org/officeDocument/2006/math\" "
        "xmlns:v=\"urn:schemas-microsoft-com:vml\" "
        "xmlns:wp14=\"http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing\" "
        "xmlns:wp=\"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing\" "
        "xmlns:w10=\"urn:schemas-microsoft-com:office:word\" "
        "xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\" "
        "xmlns:w14=\"http://schemas.microsoft.com/office/word/2010/wordml\" "
        "xmlns:wpg=\"http://schemas.microsoft.com/office/word/2010/wordprocessingGroup\" "
        "xmlns:wpi=\"http://schemas.microsoft.com/office/word/2010/wordprocessingInk\" "
        "xmlns:wne=\"http://schemas.microsoft.com/office/word/2006/wordml\" "
        "xmlns:wps=\"http://schemas.microsoft.com/office/word/2010/wordprocessingShape\" "
        "mc:Ignorable=\"w14 wp14\">"
        f"<w:body>{body}<w:sectPr><w:pgSz w:w=\"11906\" w:h=\"16838\"/><w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" w:header=\"708\" w:footer=\"708\" w:gutter=\"0\"/></w:sectPr></w:body></w:document>"
    )


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""

APP_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Codex</Application>
</Properties>
"""

CORE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>50 cau hoi trac nghiem AI</dc:title>
  <dc:creator>Codex</dc:creator>
</cp:coreProperties>
"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""


def main() -> None:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with zipfile.ZipFile(OUTPUT_PATH, "w", compression=zipfile.ZIP_DEFLATED) as docx:
        docx.writestr("[Content_Types].xml", CONTENT_TYPES)
        docx.writestr("_rels/.rels", RELS)
        docx.writestr("docProps/app.xml", APP_XML)
        docx.writestr("docProps/core.xml", CORE_XML)
        docx.writestr("word/document.xml", build_document_xml())
        docx.writestr("word/_rels/document.xml.rels", DOC_RELS)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
