# Hướng dẫn triển khai ứng dụng lên Streamlit Cloud

## Giới thiệu

Tài liệu này hướng dẫn cách triển khai ứng dụng tính toán tối ưu mặt cắt đập bê tông trọng lực lên Streamlit Cloud - một nền tảng miễn phí lâu dài, dễ sử dụng và không yêu cầu bảo trì phức tạp.

## Yêu cầu

- Tài khoản GitHub (có thể đăng nhập bằng passkey)
- Mã nguồn ứng dụng (đã được cung cấp trong file dam_optimizer.tar.gz)

## Các bước triển khai

### 1. Tạo repository trên GitHub

1. Đăng nhập vào GitHub bằng passkey của bạn
2. Nhấp vào nút "+" ở góc trên bên phải và chọn "New repository"
3. Điền thông tin:
   - **Repository name**: `dam-optimizer`
   - **Description** (tùy chọn): `Công cụ tính toán tối ưu mặt cắt đập bê tông trọng lực`
   - **Visibility**: Chọn "Public"
   - **Initialize this repository with**: Không chọn gì
4. Nhấp vào "Create repository"

### 2. Tải mã nguồn lên GitHub

1. Giải nén file `dam_optimizer.tar.gz` mà tôi đã gửi cho bạn
2. Mở terminal/command prompt và di chuyển đến thư mục đã giải nén:
   ```bash
   cd đường_dẫn_đến_thư_mục/dam_optimizer
   ```
3. Khởi tạo Git repository và đẩy mã nguồn lên GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/username_của_bạn/dam-optimizer.git
   git push -u origin main
   ```

   Thay `username_của_bạn` bằng tên người dùng GitHub của bạn.

### 3. Đăng ký tài khoản Streamlit Cloud

1. Truy cập [Streamlit Cloud](https://streamlit.io/cloud)
2. Nhấp vào "Sign up" nếu bạn chưa có tài khoản
3. Chọn "Continue with GitHub" để đăng nhập bằng tài khoản GitHub của bạn
4. Làm theo các bước để hoàn tất đăng ký

### 4. Triển khai ứng dụng lên Streamlit Cloud

1. Sau khi đăng nhập vào Streamlit Cloud, nhấp vào "New app"
2. Trong phần "Repository", chọn repository `dam-optimizer` của bạn
3. Trong phần "Branch", chọn `main`
4. Trong phần "Main file path", nhập `app.py`
5. Nhấp vào "Deploy"

### 5. Cấu hình ứng dụng (nếu cần)

1. Sau khi ứng dụng được triển khai, nhấp vào "Settings" trong menu của ứng dụng
2. Trong phần "Packages", Streamlit sẽ tự động cài đặt các gói từ `requirements.txt`
3. Trong phần "Secrets", bạn có thể thêm các biến môi trường nếu cần

### 6. Truy cập ứng dụng

1. Ứng dụng của bạn sẽ có URL dạng: `https://username-dam-optimizer.streamlit.app`
2. Bạn có thể chia sẻ URL này cho bất kỳ ai muốn sử dụng ứng dụng
3. Ứng dụng sẽ luôn hoạt động và miễn phí

## Bảo trì và cập nhật

### Cập nhật mã nguồn

1. Khi bạn muốn cập nhật ứng dụng, chỉ cần thay đổi mã nguồn trên máy tính của bạn
2. Commit và push các thay đổi lên GitHub:
   ```bash
   git add .
   git commit -m "Cập nhật mã nguồn"
   git push
   ```
3. Streamlit Cloud sẽ tự động phát hiện các thay đổi và cập nhật ứng dụng

### Sao lưu dữ liệu

1. Dữ liệu được lưu trong file SQLite (`data/dam_results.db`)
2. Để sao lưu dữ liệu, bạn có thể tải xuống file này từ ứng dụng
3. Lưu ý rằng Streamlit Cloud không đảm bảo lưu trữ dữ liệu vĩnh viễn, vì vậy nên thường xuyên sao lưu dữ liệu quan trọng

## Xử lý sự cố

### Ứng dụng không khởi động

1. Kiểm tra logs trong Streamlit Cloud để xem lỗi
2. Đảm bảo tất cả các thư viện cần thiết đã được liệt kê trong `requirements.txt`
3. Kiểm tra xem đường dẫn đến file chính (`app.py`) đã chính xác chưa

### Lỗi khi sử dụng ứng dụng

1. Kiểm tra logs trong Streamlit Cloud
2. Cập nhật mã nguồn để sửa lỗi và push lên GitHub

## Liên hệ hỗ trợ

Nếu bạn gặp bất kỳ vấn đề nào trong quá trình triển khai hoặc sử dụng ứng dụng, vui lòng liên hệ qua email: example@example.com

---

Chúc bạn thành công trong việc triển khai ứng dụng tính toán tối ưu mặt cắt đập bê tông trọng lực!
