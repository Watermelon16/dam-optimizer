# Kiến trúc ứng dụng web tính toán tối ưu mặt cắt đập bê tông

## 1. Lựa chọn framework

Sau khi cân nhắc các yêu cầu về giao diện tối giản kiểu Apple, khả năng triển khai miễn phí lâu dài, và dễ dàng bảo trì, tôi quyết định sử dụng **Streamlit** làm framework chính cho ứng dụng web vì những lý do sau:

- **Dễ phát triển**: Streamlit cho phép tạo ứng dụng web Python nhanh chóng với ít code
- **Tích hợp trực quan hóa**: Hỗ trợ tốt các thư viện như Matplotlib, Plotly để tạo biểu đồ tương tác
- **Triển khai miễn phí**: Dễ dàng triển khai trên Streamlit Cloud, Hugging Face Spaces hoặc Render
- **Giao diện hiện đại**: Có thể tùy chỉnh CSS để tạo giao diện theo phong cách Apple
- **Hỗ trợ tương tác**: Cung cấp các widget tương tác như sliders, input fields, buttons
- **Cộng đồng lớn**: Nhiều tài liệu hướng dẫn và hỗ trợ từ cộng đồng

## 2. Cấu trúc thư mục

```
dam_optimizer/
├── app.py                  # Điểm vào chính của ứng dụng Streamlit
├── requirements.txt        # Các thư viện cần thiết
├── README.md               # Hướng dẫn sử dụng và triển khai
├── modules/
│   ├── __init__.py
│   ├── pinns_model.py      # Mô-đun tính toán PINNs
│   ├── visualization.py    # Mô-đun vẽ biểu đồ và sơ đồ lực
│   ├── report_generator.py # Mô-đun tạo báo cáo PDF và Excel
│   └── database.py         # Mô-đun xử lý cơ sở dữ liệu
├── static/
│   ├── css/
│   │   └── style.css       # CSS tùy chỉnh cho giao diện Apple
│   ├── js/
│   │   └── custom.js       # JavaScript tùy chỉnh (nếu cần)
│   └── images/             # Hình ảnh và biểu tượng
├── templates/
│   └── report_template.html # Mẫu báo cáo PDF
└── data/
    └── dam_results.db      # Cơ sở dữ liệu SQLite
```

## 3. Luồng dữ liệu và tương tác người dùng

1. **Nhập liệu**:
   - Người dùng nhập các tham số đầu vào qua form
   - Các giá trị mặc định được lấy từ cấu hình

2. **Tính toán**:
   - Khi người dùng nhấn nút "Tính toán", dữ liệu được chuyển đến mô-đun PINNs
   - Mô hình PINNs thực hiện tính toán tối ưu
   - Kết quả được trả về ứng dụng chính

3. **Hiển thị kết quả**:
   - Kết quả tính toán được hiển thị trực quan
   - Sơ đồ lực và biểu đồ hàm mất mát được tạo và hiển thị
   - Người dùng có thể tương tác với biểu đồ

4. **Lưu trữ và truy xuất**:
   - Kết quả được tự động lưu vào cơ sở dữ liệu SQLite
   - Người dùng có thể xem lịch sử tính toán
   - Có thể xuất kết quả dưới dạng PDF hoặc Excel

## 4. Thiết kế cơ sở dữ liệu

### Bảng `calculation_results`

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| id | INTEGER | Khóa chính, tự động tăng |
| timestamp | DATETIME | Thời gian tính toán |
| H | REAL | Chiều cao đập (m) |
| gamma_bt | REAL | Trọng lượng riêng bê tông (T/m³) |
| gamma_n | REAL | Trọng lượng riêng nước (T/m³) |
| f | REAL | Hệ số ma sát |
| C | REAL | Cường độ kháng cắt (T/m²) |
| Kc | REAL | Hệ số ổn định yêu cầu |
| a1 | REAL | Hệ số áp lực thấm |
| n | REAL | Tham số tối ưu n |
| m | REAL | Tham số tối ưu m |
| xi | REAL | Tham số tối ưu xi |
| A | REAL | Diện tích mặt cắt tối ưu (m²) |
| K | REAL | Hệ số ổn định |
| sigma | REAL | Ứng suất mép thượng lưu (T/m²) |
| loss_chart_path | TEXT | Đường dẫn đến biểu đồ hàm mất mát |
| force_diagram_path | TEXT | Đường dẫn đến sơ đồ lực |

## 5. API mô-đun tính toán

```python
# Ví dụ API cho mô-đun tính toán
def optimize_dam_section(
    H: float,           # Chiều cao đập (m)
    gamma_bt: float,    # Trọng lượng riêng bê tông (T/m³)
    gamma_n: float,     # Trọng lượng riêng nước (T/m³)
    f: float,           # Hệ số ma sát
    C: float,           # Cường độ kháng cắt (T/m²)
    Kc: float,          # Hệ số ổn định yêu cầu
    a1: float,          # Hệ số áp lực thấm
    epochs: int = 5000, # Số vòng lặp tối đa
    device: str = None  # Thiết bị tính toán (CPU/GPU)
) -> dict:
    """
    Tính toán tối ưu mặt cắt đập bê tông trọng lực sử dụng PINNs.
    
    Returns:
        dict: Kết quả tính toán bao gồm các tham số tối ưu và các giá trị liên quan
    """
    # Triển khai thuật toán PINNs
    # ...
    
    return {
        'n': n_value,
        'm': m_value,
        'xi': xi_value,
        'A': area,
        'K': stability_factor,
        'sigma': stress,
        'loss_history': loss_values,
        'computation_time': elapsed_time
    }
```

## 6. Giao diện người dùng

Giao diện người dùng sẽ được thiết kế theo phong cách Apple với các đặc điểm:
- Nền sáng, chữ đen
- Viền mỏng, góc bo nhẹ
- Bố cục rõ ràng, tối giản
- Khoảng cách hợp lý giữa các thành phần
- Sử dụng font sans-serif hiện đại
- Màu sắc chủ đạo: trắng, xám nhạt, xanh dương nhạt

### Bố cục chính:
1. **Thanh tiêu đề**: Logo và tên ứng dụng
2. **Sidebar**: Chứa form nhập liệu và các tùy chọn
3. **Khu vực chính**: Hiển thị kết quả, biểu đồ và sơ đồ lực
4. **Thanh tab**: Chuyển đổi giữa các chế độ xem khác nhau
5. **Footer**: Thông tin về ứng dụng và liên kết hữu ích

## 7. Kế hoạch triển khai

1. **Phát triển cục bộ**:
   - Phát triển và kiểm thử ứng dụng trên môi trường cục bộ
   - Đảm bảo tất cả các tính năng hoạt động như mong đợi

2. **Đóng gói**:
   - Tạo file requirements.txt với các phụ thuộc cần thiết
   - Tạo file README.md với hướng dẫn triển khai và sử dụng

3. **Triển khai**:
   - Triển khai lên Hugging Face Spaces (ưu tiên vì miễn phí lâu dài)
   - Cấu hình để đảm bảo ứng dụng hoạt động ổn định

4. **Bảo trì**:
   - Cung cấp hướng dẫn để người dùng có thể tự triển khai
   - Thiết kế mã nguồn dễ bảo trì và mở rộng
