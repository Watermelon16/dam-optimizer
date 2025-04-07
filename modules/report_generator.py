"""
Mô-đun tạo báo cáo cho ứng dụng tính toán tối ưu mặt cắt đập bê tông
"""

import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, Any, Optional
from fpdf import FPDF
import os
import tempfile

class ReportGenerator:
    """
    Lớp tạo báo cáo PDF và Excel cho kết quả tính toán
    """
    
    @staticmethod
    def create_excel_report(result: Dict[str, Any], output_path: Optional[str] = None) -> pd.DataFrame:
        """
        Tạo báo cáo Excel từ kết quả tính toán
        
        Args:
            result: Kết quả tính toán từ mô-đun PINNs
            output_path: Đường dẫn để lưu file Excel (nếu None, không lưu)
            
        Returns:
            DataFrame chứa dữ liệu báo cáo
        """
        # Tạo DataFrame cho báo cáo
        data = {
            'Thông số': [
                'Chiều cao đập (H)',
                'Trọng lượng riêng bê tông (γ_bt)',
                'Trọng lượng riêng nước (γ_n)',
                'Hệ số ma sát (f)',
                'Cường độ kháng cắt (C)',
                'Hệ số ổn định yêu cầu (Kc)',
                'Hệ số áp lực thấm (α1)',
                'Hệ số mái thượng lưu (n)',
                'Hệ số mái hạ lưu (m)',
                'Tham số ξ',
                'Diện tích mặt cắt (A)',
                'Hệ số ổn định (K)',
                'Ứng suất mép thượng lưu (σ)',
                'Thời gian tính toán'
            ],
            'Giá trị': [
                f"{result['H']:.2f} m",
                f"{result['gamma_bt']:.2f} T/m³",
                f"{result['gamma_n']:.2f} T/m³",
                f"{result['f']:.2f}",
                f"{result['C']:.2f} T/m²",
                f"{result['Kc']:.2f}",
                f"{result['a1']:.2f}",
                f"{result['n']:.4f}",
                f"{result['m']:.4f}",
                f"{result['xi']:.4f}",
                f"{result['A']:.4f} m²",
                f"{result['K']:.4f}",
                f"{result['sigma']:.4f} T/m²",
                f"{result['computation_time']:.2f} giây"
            ]
        }
        
        df = pd.DataFrame(data)
        
        # Lưu file Excel nếu có đường dẫn
        if output_path:
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Kết quả', index=False)
                workbook = writer.book
                worksheet = writer.sheets['Kết quả']
                
                # Định dạng cột
                format1 = workbook.add_format({'num_format': '0.00'})
                worksheet.set_column('A:A', 30, format1)
                worksheet.set_column('B:B', 20, format1)
                
                # Thêm biểu đồ hàm mất mát
                loss_chart = workbook.add_chart({'type': 'line'})
                
                # Thêm sheet cho dữ liệu hàm mất mát
                loss_df = pd.DataFrame({
                    'Epoch': range(len(result['loss_history'])),
                    'Loss': result['loss_history']
                })
                loss_df.to_excel(writer, sheet_name='Loss', index=False)
                
                # Cấu hình biểu đồ
                loss_chart.add_series({
                    'name': 'Hàm mất mát',
                    'categories': '=Loss!$A$2:$A$' + str(len(result['loss_history']) + 1),
                    'values': '=Loss!$B$2:$B$' + str(len(result['loss_history']) + 1),
                    'line': {'color': 'blue', 'width': 1.5}
                })
                
                loss_chart.set_title({'name': 'Hàm mất mát trong quá trình huấn luyện'})
                loss_chart.set_x_axis({'name': 'Epoch'})
                loss_chart.set_y_axis({'name': 'Loss', 'log_base': 10})
                
                # Thêm biểu đồ vào sheet mới
                chart_sheet = workbook.add_worksheet('Biểu đồ')
                chart_sheet.insert_chart('B2', loss_chart, {'x_scale': 1.5, 'y_scale': 1.5})
        
        return df
    
    @staticmethod
    def create_pdf_report(result: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        Tạo báo cáo PDF từ kết quả tính toán
        
        Args:
            result: Kết quả tính toán từ mô-đun PINNs
            output_path: Đường dẫn để lưu file PDF (nếu None, không lưu)
            
        Returns:
            Đường dẫn đến file PDF đã tạo hoặc chuỗi rỗng nếu không lưu
        """
        from modules.visualization import create_force_diagram, plot_loss_curve
        
        # Tạo thư mục tạm để lưu hình ảnh
        temp_dir = tempfile.mkdtemp()
        
        # Tạo hình ảnh mặt cắt đập
        dam_fig = create_force_diagram(result, interactive=False)
        dam_img_path = os.path.join(temp_dir, 'dam_section.png')
        dam_fig.savefig(dam_img_path, dpi=150, bbox_inches='tight')
        plt.close(dam_fig)
        
        # Tạo biểu đồ hàm mất mát
        loss_fig = plot_loss_curve(result['loss_history'], interactive=False)
        loss_img_path = os.path.join(temp_dir, 'loss_curve.png')
        loss_fig.savefig(loss_img_path, dpi=150, bbox_inches='tight')
        plt.close(loss_fig)
        
        # Tạo PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Tiêu đề
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'BÁO CÁO TÍNH TOÁN TỐI ƯU MẶT CẮT ĐẬP BÊ TÔNG TRỌNG LỰC', 0, 1, 'C')
        pdf.ln(5)
        
        # Thông số đầu vào
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Thông số đầu vào', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 12)
        input_params = [
            ['Chiều cao đập (H)', f"{result['H']:.2f} m"],
            ['Trọng lượng riêng bê tông (γ_bt)', f"{result['gamma_bt']:.2f} T/m³"],
            ['Trọng lượng riêng nước (γ_n)', f"{result['gamma_n']:.2f} T/m³"],
            ['Hệ số ma sát (f)', f"{result['f']:.2f}"],
            ['Cường độ kháng cắt (C)', f"{result['C']:.2f} T/m²"],
            ['Hệ số ổn định yêu cầu (Kc)', f"{result['Kc']:.2f}"],
            ['Hệ số áp lực thấm (α1)', f"{result['a1']:.2f}"]
        ]
        
        for param in input_params:
            pdf.cell(90, 8, param[0], 1, 0, 'L')
            pdf.cell(90, 8, param[1], 1, 1, 'L')
        
        pdf.ln(5)
        
        # Kết quả tính toán
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Kết quả tính toán', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 12)
        output_params = [
            ['Hệ số mái thượng lưu (n)', f"{result['n']:.4f}"],
            ['Hệ số mái hạ lưu (m)', f"{result['m']:.4f}"],
            ['Tham số ξ', f"{result['xi']:.4f}"],
            ['Diện tích mặt cắt (A)', f"{result['A']:.4f} m²"],
            ['Hệ số ổn định (K)', f"{result['K']:.4f}"],
            ['Ứng suất mép thượng lưu (σ)', f"{result['sigma']:.4f} T/m²"],
            ['Thời gian tính toán', f"{result['computation_time']:.2f} giây"]
        ]
        
        for param in output_params:
            pdf.cell(90, 8, param[0], 1, 0, 'L')
            pdf.cell(90, 8, param[1], 1, 1, 'L')
        
        pdf.ln(5)
        
        # Sơ đồ lực tác dụng
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Sơ đồ lực tác dụng', 0, 1, 'L')
        pdf.ln(2)
        
        # Thêm hình ảnh mặt cắt đập
        pdf.image(dam_img_path, x=10, y=None, w=180)
        pdf.ln(5)
        
        # Biểu đồ hàm mất mát
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Biểu đồ hàm mất mát', 0, 1, 'L')
        pdf.ln(2)
        
        # Thêm biểu đồ hàm mất mát
        pdf.image(loss_img_path, x=10, y=None, w=180)
        
        # Thêm footer
        pdf.set_y(-30)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, 'Báo cáo được tạo bởi Công cụ tính toán tối ưu mặt cắt đập bê tông trọng lực', 0, 1, 'C')
        pdf.cell(0, 10, f"Ngày tạo: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, 'C')
        
        # Lưu file PDF nếu có đường dẫn
        if output_path:
            pdf.output(output_path)
            return output_path
        else:
            # Lưu vào file tạm và trả về nội dung
            temp_pdf_path = os.path.join(temp_dir, 'report.pdf')
            pdf.output(temp_pdf_path)
            return temp_pdf_path
