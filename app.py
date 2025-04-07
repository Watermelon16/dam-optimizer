"""
Ứng dụng web tính toán tối ưu mặt cắt đập bê tông trọng lực
sử dụng mô hình Physics-Informed Neural Networks (PINNs)
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os
import time
import base64
from io import BytesIO
import torch
from datetime import datetime

# Import các mô-đun tự tạo
from modules.pinns_model import optimize_dam_section, generate_force_diagram, plot_loss_history
from modules.visualization import create_force_diagram, plot_loss_curve, create_excel_report, create_pdf_report
from modules.database import DamDatabase

# Thiết lập trang
st.set_page_config(
    page_title="Tính toán tối ưu mặt cắt đập bê tông",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tải CSS tùy chỉnh
def load_css():
    with open("static/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Hàm tạo file Excel để tải xuống
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Kết quả', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Kết quả']
        format1 = workbook.add_format({'num_format': '0.00'})
        worksheet.set_column('A:Z', 18, format1)
    processed_data = output.getvalue()
    return processed_data

# Hàm tạo link tải xuống
def get_download_link(data, filename, text):
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Hàm tạo PDF để tải xuống
def get_pdf_download_link(html_content, filename):
    try:
        import pdfkit
        pdf = pdfkit.from_string(html_content, False)
        b64 = base64.b64encode(pdf).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Tải xuống báo cáo PDF</a>'
        return href
    except Exception as e:
        st.error(f"Không thể tạo PDF: {e}")
        return None

# Khởi tạo cơ sở dữ liệu
@st.cache_resource
def get_database():
    return DamDatabase("data/dam_results.db")

# Hàm chính
def main():
    # Tải CSS
    load_css()
    
    # Kết nối đến cơ sở dữ liệu
    db = get_database()
    
    # Thanh tiêu đề
    st.title("Công cụ tính toán tối ưu mặt cắt đập bê tông trọng lực")
    st.markdown("Sử dụng mô hình Physics-Informed Neural Networks (PINNs)")
    
    # Tạo tabs
    tabs = st.tabs(["Tính toán", "Lý thuyết", "Lịch sử tính toán", "Giới thiệu"])
    
    # Tab Tính toán
    with tabs[0]:
        # Chia layout thành 2 cột
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Thông số đầu vào")
            
            # Form nhập liệu
            with st.form("input_form"):
                H = st.number_input("Chiều cao đập H (m)", min_value=10.0, max_value=300.0, value=60.0, step=5.0)
                
                st.markdown("#### Thông số vật liệu và nền")
                gamma_bt = st.number_input("Trọng lượng riêng bê tông γ_bt (T/m³)", min_value=2.0, max_value=3.0, value=2.4, step=0.1)
                gamma_n = st.number_input("Trọng lượng riêng nước γ_n (T/m³)", min_value=0.9, max_value=1.1, value=1.0, step=0.1)
                f = st.number_input("Hệ số ma sát f", min_value=0.3, max_value=0.9, value=0.7, step=0.05)
                C = st.number_input("Cường độ kháng cắt C (T/m²)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)
                
                st.markdown("#### Thông số ổn định và thấm")
                Kc = st.number_input("Hệ số ổn định yêu cầu Kc", min_value=1.0, max_value=2.0, value=1.2, step=0.1)
                a1 = st.number_input("Hệ số áp lực thấm α1", min_value=0.0, max_value=1.0, value=0.6, step=0.1)
                
                st.markdown("#### Thông số tính toán")
                epochs = st.slider("Số vòng lặp tối đa", min_value=1000, max_value=10000, value=5000, step=1000)
                
                # Nút tính toán
                submitted = st.form_submit_button("Tính toán tối ưu")
            
            # Kiểm tra lịch sử tính toán
            existing_results = db.search_results(H=H)
            if not existing_results.empty:
                st.info(f"Đã có {len(existing_results)} kết quả tính toán trước đó cho H = {H}m trong cơ sở dữ liệu.")
                if st.button("Xem kết quả đã có"):
                    result_id = existing_results.iloc[0]['id']
                    st.session_state['result'] = db.get_result_by_id(result_id)
                    st.experimental_rerun()
        
        # Xử lý khi form được gửi
        if submitted:
            with st.spinner("Đang tính toán tối ưu mặt cắt đập..."):
                # Thực hiện tính toán
                result = optimize_dam_section(
                    H=H,
                    gamma_bt=gamma_bt,
                    gamma_n=gamma_n,
                    f=f,
                    C=C,
                    Kc=Kc,
                    a1=a1,
                    epochs=epochs,
                    verbose=False
                )
                
                # Lưu kết quả vào cơ sở dữ liệu
                db.save_result(result)
                
                # Lưu kết quả vào session state
                st.session_state['result'] = result
        
        # Hiển thị kết quả nếu có
        with col2:
            if 'result' in st.session_state:
                result = st.session_state['result']
                
                st.markdown("### Kết quả tính toán")
                
                # Hiển thị các tham số tối ưu
                col_params1, col_params2 = st.columns(2)
                
                with col_params1:
                    st.metric("Hệ số mái thượng lưu (n)", f"{result['n']:.4f}")
                    st.metric("Hệ số mái hạ lưu (m)", f"{result['m']:.4f}")
                    st.metric("Tham số ξ", f"{result['xi']:.4f}")
                
                with col_params2:
                    st.metric("Diện tích mặt cắt (A)", f"{result['A']:.4f} m²")
                    st.metric("Hệ số ổn định (K)", f"{result['K']:.4f}")
                    st.metric("Ứng suất mép thượng lưu (σ)", f"{result['sigma']:.4f} T/m²")
                
                # Hiển thị trạng thái
                if result['K'] >= result['Kc']:
                    st.success(f"Mặt cắt đập thỏa mãn điều kiện ổn định (K = {result['K']:.4f} ≥ Kc = {result['Kc']:.2f})")
                else:
                    st.error(f"Mặt cắt đập KHÔNG thỏa mãn điều kiện ổn định (K = {result['K']:.4f} < Kc = {result['Kc']:.2f})")
                
                if result['sigma'] <= 0:
                    st.success(f"Mặt cắt đập thỏa mãn điều kiện không kéo (σ = {result['sigma']:.4f} T/m² ≤ 0)")
                else:
                    st.warning(f"Mặt cắt đập có ứng suất kéo ở mép thượng lưu (σ = {result['sigma']:.4f} T/m² > 0)")
                
                # Hiển thị thời gian tính toán
                st.info(f"Thời gian tính toán: {result['computation_time']:.2f} giây")
                
                # Tạo tabs cho các biểu đồ
                result_tabs = st.tabs(["Mặt cắt đập", "Biểu đồ hàm mất mát", "Xuất báo cáo"])
                
                # Tab mặt cắt đập
                with result_tabs[0]:
                    # Tạo biểu đồ Plotly tương tác
                    fig = create_force_diagram(result, interactive=True)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Tab biểu đồ hàm mất mát
                with result_tabs[1]:
                    # Tạo biểu đồ Plotly tương tác
                    loss_fig = plot_loss_curve(result['loss_history'], interactive=True)
                    st.plotly_chart(loss_fig, use_container_width=True)
                
                # Tab xuất báo cáo
                with result_tabs[2]:
                    st.markdown("### Xuất báo cáo")
                    
                    # Tạo báo cáo Excel
                    excel_df = create_excel_report(result)
                    excel_data = to_excel(excel_df)
                    st.markdown(
                        get_download_link(excel_data, f"bao_cao_dam_H{int(result['H'])}.xlsx", "Tải xuống báo cáo Excel"),
                        unsafe_allow_html=True
                    )
                    
                    # Tạo báo cáo PDF
                    pdf_html = create_pdf_report(result)
                    
                    # Kiểm tra xem pdfkit đã được cài đặt chưa
                    try:
                        import pdfkit
                        pdf_link = get_pdf_download_link(pdf_html, f"bao_cao_dam_H{int(result['H'])}.pdf")
                        if pdf_link:
                            st.markdown(pdf_link, unsafe_allow_html=True)
                    except ImportError:
                        st.warning("Thư viện pdfkit chưa được cài đặt. Không thể tạo báo cáo PDF.")
                        if st.button("Cài đặt pdfkit"):
                            os.system("pip install pdfkit")
                            st.success("Đã cài đặt pdfkit. Vui lòng khởi động lại ứng dụng.")
    
    # Tab Lý thuyết
    with tabs[1]:
        st.markdown("""
        ### Lý thuyết tính toán mặt cắt đập bê tông trọng lực
        
        #### Mô hình Physics-Informed Neural Networks (PINNs)
        
        Physics-Informed Neural Networks (PINNs) là một phương pháp kết hợp giữa mạng nơ-ron và các ràng buộc vật lý để giải quyết các bài toán khoa học và kỹ thuật. Trong ứng dụng này, PINNs được sử dụng để tìm các tham số tối ưu cho mặt cắt đập bê tông trọng lực.
        
        #### Các tham số tối ưu
        
        Mặt cắt đập bê tông trọng lực được mô tả bởi ba tham số chính:
        
        - **n**: Hệ số mái thượng lưu
        - **m**: Hệ số mái hạ lưu
        - **ξ (xi)**: Tham số xác định vị trí điểm gãy khúc trên mái thượng lưu
        
        #### Các điều kiện ràng buộc
        
        Mặt cắt đập phải thỏa mãn các điều kiện sau:
        
        1. **Điều kiện ổn định trượt**: Hệ số ổn định K ≥ Kc
        2. **Điều kiện không kéo**: Ứng suất mép thượng lưu σ ≤ 0
        3. **Tối thiểu hóa diện tích mặt cắt**: Giảm thiểu lượng bê tông sử dụng
        
        #### Công thức tính toán
        
        Các công thức chính được sử dụng trong tính toán:
        
        - **Diện tích mặt cắt**: A = 0.5 * H² * (m + n * (1-ξ)²)
        - **Hệ số ổn định**: K = Fct / Fgt
            - Fct = f * (G + W2 - Wt) + C * H * (m + n * (1-ξ))
            - Fgt = 0.5 * γ_n * H²
        - **Ứng suất mép thượng lưu**: σ = P / B - 6 * M0 / B²
        
        #### Quá trình tối ưu hóa
        
        1. Mạng nơ-ron dự đoán các tham số n, m, ξ
        2. Tính toán các đại lượng vật lý (A, K, σ) dựa trên các tham số này
        3. Tính toán hàm mất mát dựa trên các ràng buộc vật lý
        4. Cập nhật mạng nơ-ron để giảm thiểu hàm mất mát
        5. Lặp lại quá trình cho đến khi hội tụ
        
        #### Hàm mất mát
        
        Hàm mất mát bao gồm các thành phần:
        
        1. Phạt nếu K < Kc (đảm bảo ổn định)
        2. Phạt nếu σ > 0 (đảm bảo không kéo)
        3. Tối thiểu hóa diện tích A
        
        #### Tài liệu tham khảo
        
        1. Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. Journal of Computational Physics, 378, 686-707.
        
        2. Nguyễn Văn Mạo, Đỗ Văn Bình (2010). Tính toán thiết kế đập bê tông trọng lực. NXB Xây dựng, Hà Nội.
        """)
    
    # Tab Lịch sử tính toán
    with tabs[2]:
        st.markdown("### Lịch sử tính toán")
        
        # Lấy tất cả kết quả từ cơ sở dữ liệu
        all_results = db.get_all_results()
        
        if all_results.empty:
            st.info("Chưa có kết quả tính toán nào được lưu trong cơ sở dữ liệu.")
        else:
            # Hiển thị bảng kết quả
            display_df = all_results[['id', 'timestamp', 'H', 'n', 'm', 'xi', 'A', 'K', 'sigma']].copy()
            display_df.columns = ['ID', 'Thời gian', 'H (m)', 'n', 'm', 'ξ', 'A (m²)', 'K', 'σ (T/m²)']
            
            # Format các cột số
            for col in ['n', 'm', 'ξ', 'A (m²)', 'K', 'σ (T/m²)']:
                display_df[col] = display_df[col].round(4)
            
            # Format cột thời gian
            display_df['Thời gian'] = pd.to_datetime(display_df['Thời gian']).dt.strftime('%d/%m/%Y %H:%M:%S')
            
            st.dataframe(display_df, use_container_width=True)
            
            # Chọn kết quả để xem chi tiết
            selected_id = st.selectbox("Chọn ID để xem chi tiết:", display_df['ID'].tolist())
            
            if st.button("Xem chi tiết"):
                result = db.get_result_by_id(selected_id)
                st.session_state['result'] = result
                st.experimental_rerun()
            
            # Xóa kết quả
            if st.button("Xóa kết quả đã chọn"):
                if db.delete_result(selected_id):
                    st.success(f"Đã xóa kết quả có ID = {selected_id}")
                    # Cập nhật lại bảng
                    st.experimental_rerun()
                else:
                    st.error("Không thể xóa kết quả")
    
    # Tab Giới thiệu
    with tabs[3]:
        st.markdown("""
        ### Giới thiệu
        
        Ứng dụng **Tính toán tối ưu mặt cắt đập bê tông trọng lực** là một công cụ chuyên nghiệp giúp kỹ sư và nhà thiết kế tìm ra mặt cắt kinh tế nhất cho đập bê tông trọng lực (phần không tràn) đồng thời đảm bảo các yêu cầu về ổn định và an toàn.
        
        #### Tính năng chính
        
        - Tính toán tối ưu mặt cắt đập bê tông trọng lực sử dụng mô hình Physics-Informed Neural Networks (PINNs)
        - Hiển thị trực quan kết quả tính toán với các biểu đồ tương tác
        - Lưu trữ và quản lý lịch sử tính toán
        - Xuất báo cáo dạng PDF và Excel
        
        #### Hướng dẫn sử dụng
        
        1. Nhập các thông số đầu vào trong tab "Tính toán"
        2. Nhấn nút "Tính toán tối ưu" để thực hiện tính toán
        3. Xem kết quả tính toán và các biểu đồ trực quan
        4. Xuất báo cáo dạng PDF hoặc Excel nếu cần
        5. Xem lịch sử tính toán trong tab "Lịch sử tính toán"
        
        #### Về tác giả
        
        Ứng dụng này được phát triển bởi nhóm nghiên cứu về ứng dụng trí tuệ nhân tạo trong kỹ thuật xây dựng công trình thủy lợi.
        
        #### Liên hệ
        
        Nếu có bất kỳ câu hỏi hoặc góp ý nào, vui lòng liên hệ qua email: example@example.com
        """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025 Công cụ tính toán tối ưu mặt cắt đập bê tông trọng lực | Phiên bản 1.0</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
