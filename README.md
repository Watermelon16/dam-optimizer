# Công cụ tính toán tối ưu mặt cắt đập bê tông trọng lực

## Giới thiệu

Đây là ứng dụng web chuyên nghiệp để tính toán tối ưu mặt cắt kinh tế của đập bê tông trọng lực (phần không tràn) sử dụng mô hình Physics-Informed Neural Networks (PINNs). Ứng dụng được thiết kế với giao diện tối giản, hiện đại theo phong cách Apple, dễ sử dụng và có đầy đủ các tính năng cần thiết cho việc tính toán và phân tích.

## Tính năng

- **Tính toán tối ưu**: Sử dụng mô hình PINNs để tìm mặt cắt đập tối ưu với diện tích nhỏ nhất
- **Giao diện người dùng**: Thiết kế tối giản, sạch sẽ theo phong cách Apple
- **Trực quan hóa**: Hiển thị sơ đồ lực tác dụng và biểu đồ hàm mất mát tương tác
- **Báo cáo**: Xuất báo cáo dạng PDF và Excel
- **Cơ sở dữ liệu**: Lưu trữ và quản lý lịch sử tính toán
- **Triển khai miễn phí**: Hỗ trợ triển khai lên Hugging Face Spaces miễn phí lâu dài

## Cài đặt

### Yêu cầu

- Python 3.9 trở lên
- Các thư viện được liệt kê trong `requirements.txt`

### Cài đặt cục bộ

1. Clone repository:
```bash
git clone https://github.com/yourusername/dam-optimizer.git
cd dam-optimizer
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```bash
streamlit run app.py
```

### Triển khai lên Hugging Face Spaces

Xem hướng dẫn chi tiết trong file `deployment_guide.md`.

## Cấu trúc dự án

```
dam_optimizer/
├── app.py                  # Điểm vào chính của ứng dụng Streamlit
├── requirements.txt        # Các thư viện cần thiết
├── deployment_guide.md     # Hướng dẫn triển khai
├── modules/
│   ├── __init__.py
│   ├── pinns_model.py      # Mô-đun tính toán PINNs
│   ├── visualization.py    # Mô-đun vẽ biểu đồ và sơ đồ lực
│   ├── report_generator.py # Mô-đun tạo báo cáo PDF và Excel
│   └── database.py         # Mô-đun xử lý cơ sở dữ liệu
├── static/
│   ├── css/
│   │   └── style.css       # CSS tùy chỉnh cho giao diện Apple
└── data/
    └── dam_results.db      # Cơ sở dữ liệu SQLite (tự động tạo)
```

## Sử dụng

1. Nhập các thông số đầu vào:
   - Chiều cao đập `H (m)`
   - Trọng lượng riêng bê tông `γ_bt (T/m³)`
   - Trọng lượng riêng nước `γ_n (T/m³)`
   - Hệ số ma sát `f`
   - Cường độ kháng cắt `C (T/m²)`
   - Hệ số ổn định yêu cầu `Kc`
   - Hệ số áp lực thấm `α1`

2. Nhấn nút "Tính toán tối ưu" để thực hiện tính toán

3. Xem kết quả:
   - Tham số tối ưu (`n`, `m`, `xi`)
   - Diện tích mặt cắt tối ưu (`A`)
   - Hệ số ổn định (`K`)
   - Ứng suất mép thượng lưu (`σ`)
   - Sơ đồ lực tác dụng
   - Biểu đồ hàm mất mát

4. Xuất báo cáo dạng PDF hoặc Excel

5. Xem lịch sử tính toán trong tab "Lịch sử tính toán"

## Bảo trì và mở rộng

Ứng dụng được thiết kế với cấu trúc mô-đun hóa, dễ dàng bảo trì và mở rộng:

- **Thêm tính năng mới**: Tạo mô-đun mới trong thư mục `modules/` và tích hợp vào `app.py`
- **Tùy chỉnh giao diện**: Chỉnh sửa file `static/css/style.css`
- **Cập nhật mô hình tính toán**: Chỉnh sửa file `modules/pinns_model.py`

## Giấy phép

MIT License

## Liên hệ

Nếu có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ qua email: example@example.com
