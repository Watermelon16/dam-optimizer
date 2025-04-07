# Hướng dẫn triển khai ứng dụng tính toán tối ưu mặt cắt đập bê tông

## Giới thiệu

Tài liệu này hướng dẫn cách triển khai ứng dụng tính toán tối ưu mặt cắt đập bê tông trọng lực lên Hugging Face Spaces - một nền tảng miễn phí lâu dài, dễ sử dụng và không yêu cầu bảo trì phức tạp.

## Yêu cầu

- Tài khoản Hugging Face (miễn phí)
- Mã nguồn ứng dụng (đã được cung cấp)

## Các bước triển khai

### 1. Đăng ký tài khoản Hugging Face

1. Truy cập [Hugging Face](https://huggingface.co/)
2. Nhấp vào "Sign Up" để đăng ký tài khoản mới
3. Điền thông tin và xác nhận email

### 2. Tạo Space mới

1. Đăng nhập vào tài khoản Hugging Face
2. Truy cập [Hugging Face Spaces](https://huggingface.co/spaces)
3. Nhấp vào nút "Create new Space"
4. Điền thông tin:
   - **Owner**: Chọn tài khoản cá nhân của bạn
   - **Space name**: `dam-optimizer` (hoặc tên khác bạn muốn)
   - **License**: Chọn "MIT" hoặc license phù hợp
   - **SDK**: Chọn "Streamlit"
   - **Space hardware**: Chọn "CPU" (miễn phí)
   - **Visibility**: Chọn "Public" để mọi người có thể truy cập

5. Nhấp vào "Create Space"

### 3. Tải mã nguồn lên Space

Có hai cách để tải mã nguồn lên Space:

#### Cách 1: Sử dụng giao diện web

1. Sau khi tạo Space, bạn sẽ được chuyển đến trang quản lý Space
2. Nhấp vào tab "Files"
3. Tải lên từng file trong thư mục `dam_optimizer` bằng cách kéo thả hoặc sử dụng nút "Upload file"
4. Đảm bảo giữ nguyên cấu trúc thư mục:
   - `app.py` (ở thư mục gốc)
   - `requirements.txt` (ở thư mục gốc)
   - Thư mục `modules/` với các file Python bên trong
   - Thư mục `static/css/` với file `style.css`
   - Thư mục `data/` (sẽ được tạo tự động khi ứng dụng chạy)

#### Cách 2: Sử dụng Git (khuyến nghị)

1. Cài đặt Git trên máy tính của bạn (nếu chưa có)
2. Clone repository của Space về máy:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/dam-optimizer
   ```
3. Sao chép tất cả file từ thư mục `dam_optimizer` vào thư mục đã clone
4. Commit và push các thay đổi:
   ```bash
   cd dam-optimizer
   git add .
   git commit -m "Initial commit"
   git push
   ```

### 4. Cấu hình Space

1. Trên trang quản lý Space, nhấp vào tab "Settings"
2. Trong phần "Repository", đảm bảo:
   - **Application file**: `app.py`
   - **Python version**: 3.9 hoặc cao hơn

3. Lưu các thay đổi

### 5. Khởi động ứng dụng

1. Sau khi tải lên tất cả file và cấu hình Space, ứng dụng sẽ tự động được xây dựng và khởi động
2. Quá trình này có thể mất vài phút
3. Bạn có thể theo dõi tiến trình trong tab "Factory logs"
4. Khi ứng dụng đã sẵn sàng, bạn sẽ thấy giao diện Streamlit hiển thị trong Space

### 6. Truy cập ứng dụng

1. Ứng dụng của bạn sẽ có URL dạng: `https://huggingface.co/spaces/YOUR_USERNAME/dam-optimizer`
2. Bạn có thể chia sẻ URL này cho bất kỳ ai muốn sử dụng ứng dụng
3. Ứng dụng sẽ luôn hoạt động và miễn phí

## Bảo trì và cập nhật

### Cập nhật mã nguồn

1. Nếu bạn muốn cập nhật ứng dụng, chỉ cần tải lên các file mới hoặc chỉnh sửa trực tiếp trên giao diện web
2. Ứng dụng sẽ tự động được xây dựng lại sau mỗi thay đổi

### Sao lưu dữ liệu

1. Dữ liệu được lưu trong file SQLite (`data/dam_results.db`)
2. Để sao lưu dữ liệu, bạn có thể tải xuống file này từ tab "Files"
3. Để khôi phục dữ liệu, chỉ cần tải lên file đã sao lưu

## Xử lý sự cố

### Ứng dụng không khởi động

1. Kiểm tra "Factory logs" để xem lỗi
2. Đảm bảo tất cả các file đã được tải lên đúng vị trí
3. Kiểm tra `requirements.txt` có đầy đủ các thư viện cần thiết

### Lỗi khi sử dụng ứng dụng

1. Nếu gặp lỗi khi sử dụng ứng dụng, hãy kiểm tra "App logs"
2. Cập nhật mã nguồn để sửa lỗi và tải lên lại

## Liên hệ hỗ trợ

Nếu bạn gặp bất kỳ vấn đề nào trong quá trình triển khai hoặc sử dụng ứng dụng, vui lòng liên hệ qua email: example@example.com

---

Chúc bạn thành công trong việc triển khai ứng dụng tính toán tối ưu mặt cắt đập bê tông trọng lực!
