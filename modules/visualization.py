"""
Mô-đun trực quan hóa cho ứng dụng tính toán tối ưu mặt cắt đập bê tông
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from matplotlib.patches import FancyArrow
from typing import Dict, List, Tuple, Optional, Any
import io
import base64

def create_force_diagram(result: Dict[str, Any], interactive: bool = False) -> Any:
    """
    Tạo sơ đồ lực tác dụng lên đập
    
    Args:
        result: Kết quả tính toán từ mô-đun PINNs
        interactive: Nếu True, trả về biểu đồ Plotly tương tác, ngược lại trả về biểu đồ Matplotlib
        
    Returns:
        Đối tượng biểu đồ (Matplotlib Figure hoặc Plotly Figure)
    """
    H = result['H']
    n = result['n']
    m = result['m']
    xi = result['xi']
    
    B = H * (m + n * (1 - xi))
    lG1 = H * (m / 6 - n * (1 - xi) / 2)
    lG2 = H * (m / 2 - n * (1 - xi) / 6)
    lt  = H * (m + n * (1 - xi)) / 6
    l2  = H * m / 2
    l22 = H * m / 2 + H * n * (1 - xi) / 6
    l1  = H / 3
    mid = B / 2

    x0 = 0
    x1 = n * H * (1 - xi)
    x3 = x1
    x4 = x3 + m * H
    y0 = 0
    y3 = H
    
    if interactive:
        # Tạo biểu đồ Plotly tương tác
        fig = go.Figure()
        
        # Vẽ hình dạng đập
        fig.add_trace(go.Scatter(
            x=[x0, x1, x1, x1, x4, x0],
            y=[y0, H * (1 - xi), H, H, y0, y0],
            fill="toself",
            fillcolor="rgba(200, 200, 200, 0.5)",
            line=dict(color="black", width=2),
            name="Mặt cắt đập"
        ))
        
        # Vẽ các mũi tên lực
        arrow_length = H / 3
        
        # G1
        fig.add_trace(go.Scatter(
            x=[mid - lG1, mid - lG1],
            y=[H / 3, H / 3 - arrow_length],
            mode="lines+markers",
            marker=dict(symbol="arrow-down", size=15, color="red"),
            line=dict(color="red", width=2),
            name="G1"
        ))
        
        # G2
        fig.add_trace(go.Scatter(
            x=[mid - lG2, mid - lG2],
            y=[H * (1 - xi) / 3, H * (1 - xi) / 3 - arrow_length],
            mode="lines+markers",
            marker=dict(symbol="arrow-down", size=15, color="red"),
            line=dict(color="red", width=2),
            name="G2"
        ))
        
        # Wt
        fig.add_trace(go.Scatter(
            x=[mid - lt, mid - lt],
            y=[0, arrow_length],
            mode="lines+markers",
            marker=dict(symbol="arrow-up", size=15, color="red"),
            line=dict(color="red", width=2),
            name="Wt"
        ))
        
        # W'2
        fig.add_trace(go.Scatter(
            x=[mid - l2, mid - l2],
            y=[H * (1 - xi) + xi * H / 2, H * (1 - xi) + xi * H / 2 - arrow_length],
            mode="lines+markers",
            marker=dict(symbol="arrow-down", size=15, color="red"),
            line=dict(color="red", width=2),
            name="W'2"
        ))
        
        # W"2
        fig.add_trace(go.Scatter(
            x=[mid - l22, mid - l22],
            y=[2/3 * H * (1 - xi), 2/3 * H * (1 - xi) - arrow_length],
            mode="lines+markers",
            marker=dict(symbol="arrow-down", size=15, color="red"),
            line=dict(color="red", width=2),
            name="W\"2"
        ))
        
        # W1
        fig.add_trace(go.Scatter(
            x=[x0 - arrow_length, x0],
            y=[l1, l1],
            mode="lines+markers",
            marker=dict(symbol="arrow-right", size=15, color="red"),
            line=dict(color="red", width=2),
            name="W1"
        ))
        
        # Thêm chú thích
        annotations = [
            dict(x=mid - lG1, y=H / 3 - arrow_length/2, text="G1", showarrow=False),
            dict(x=mid - lG2, y=H * (1 - xi) / 3 - arrow_length/2, text="G2", showarrow=False),
            dict(x=mid - lt, y=arrow_length/2, text="Wt", showarrow=False),
            dict(x=mid - l2, y=H * (1 - xi) + xi * H / 2 - arrow_length/2, text="W'2", showarrow=False),
            dict(x=mid - l22, y=2/3 * H * (1 - xi) - arrow_length/2, text="W\"2", showarrow=False),
            dict(x=x0 - arrow_length/2, y=l1, text="W1", showarrow=False)
        ]
        
        fig.update_layout(
            title=f"Sơ đồ lực tác dụng lên đập H = {H} m",
            xaxis_title="Chiều rộng (m)",
            yaxis_title="Chiều cao (m)",
            annotations=annotations,
            xaxis=dict(range=[-5, B + 5]),
            yaxis=dict(range=[0, H + 5]),
            yaxis_scaleanchor="x",
            yaxis_scaleratio=1,
            showlegend=True,
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
            plot_bgcolor="white",
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig
    else:
        # Tạo biểu đồ Matplotlib
        fig, ax = plt.subplots(figsize=(8, 10))
        x = [x0, x1, x1, x1, x4, x0]
        y = [y0, H * (1 - xi), H, H, y0, y0]
        ax.plot(x, y, 'k-', lw=1.5)
        ax.fill(x, y, color='lightgrey', alpha=0.5)

        def draw_arrow(x, y, dx, dy, label):
            ax.add_patch(FancyArrow(x, y, dx, dy, width=0.3, head_width=1.2, head_length=1.5, color='red'))
            ax.text(x + dx * 0.6, y + dy * 0.6, label, fontsize=12, color='black')

        draw_arrow(mid - lG1, H / 3, 0, -4, 'G1')
        draw_arrow(mid - lG2, H * (1 - xi) / 3, 0, -3.5, 'G2')
        draw_arrow(mid - lt, 0, 0, 3.5, 'Wt')
        draw_arrow(mid - l2, H * (1 - xi) + xi * H / 2, 0, -2.8, "W'2")
        draw_arrow(mid - l22, 2/3 * H * (1 - xi), 0, -2.8, 'W\"2')
        draw_arrow(x0 - 3, l1, 2.5, 0, 'W1')

        ax.set_title(f"Sơ đồ lực tác dụng lên đập H = {H} m")
        ax.set_xlabel("Chiều rộng (m)")
        ax.set_ylabel("Chiều cao (m)")
        ax.axis("equal")
        ax.set_xlim(-5, B + 5)
        ax.set_ylim(0, H + 5)
        ax.grid(True)
        
        return fig

def plot_loss_curve(loss_history: List[float], interactive: bool = False) -> Any:
    """
    Vẽ biểu đồ hàm mất mát
    
    Args:
        loss_history: Lịch sử giá trị hàm mất mát
        interactive: Nếu True, trả về biểu đồ Plotly tương tác, ngược lại trả về biểu đồ Matplotlib
        
    Returns:
        Đối tượng biểu đồ (Matplotlib Figure hoặc Plotly Figure)
    """
    if interactive:
        # Tạo biểu đồ Plotly tương tác
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(len(loss_history))),
            y=loss_history,
            mode='lines',
            name='Loss',
            line=dict(color='royalblue', width=2)
        ))
        
        fig.update_layout(
            title='Hàm mất mát trong quá trình huấn luyện',
            xaxis_title='Epoch',
            yaxis_title='Loss',
            yaxis_type='log',  # Sử dụng thang logarit cho trục y
            showlegend=True,
            plot_bgcolor='white',
            margin=dict(l=20, r=20, t=60, b=20),
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                showline=True,
                linecolor='black'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgray',
                showline=True,
                linecolor='black'
            )
        )
        
        return fig
    else:
        # Tạo biểu đồ Matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(loss_history)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_title("Hàm mất mát trong quá trình huấn luyện")
        ax.set_yscale('log')  # Sử dụng thang logarit cho trục y
        ax.grid(True)
        
        return fig

def get_dam_section_image(result: Dict[str, Any]) -> str:
    """
    Tạo hình ảnh mặt cắt đập và trả về dưới dạng base64 để hiển thị trong HTML
    
    Args:
        result: Kết quả tính toán từ mô-đun PINNs
        
    Returns:
        Chuỗi base64 của hình ảnh
    """
    fig = create_force_diagram(result, interactive=False)
    
    # Lưu hình ảnh vào buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    
    # Chuyển đổi sang base64
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    
    # Đóng figure để tránh rò rỉ bộ nhớ
    plt.close(fig)
    
    return img_str

def create_excel_report(result: Dict[str, Any]) -> pd.DataFrame:
    """
    Tạo báo cáo Excel từ kết quả tính toán
    
    Args:
        result: Kết quả tính toán từ mô-đun PINNs
        
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
    return df

def create_pdf_report(result: Dict[str, Any]) -> str:
    """
    Tạo báo cáo PDF từ kết quả tính toán
    
    Args:
        result: Kết quả tính toán từ mô-đun PINNs
        
    Returns:
        HTML string cho báo cáo PDF
    """
    # Tạo hình ảnh mặt cắt đập
    dam_img = get_dam_section_image(result)
    
    # Tạo biểu đồ hàm mất mát
    loss_fig = plot_loss_curve(result['loss_history'], interactive=False)
    loss_buf = io.BytesIO()
    loss_fig.savefig(loss_buf, format='png', dpi=100)
    loss_buf.seek(0)
    loss_img = base64.b64encode(loss_buf.read()).decode('utf-8')
    plt.close(loss_fig)
    
    # Tạo HTML cho báo cáo
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Báo cáo tính toán tối ưu mặt cắt đập bê tông</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1, h2, h3 {{
                color: #000;
                margin-top: 30px;
            }}
            h1 {{
                text-align: center;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f8f8f8;
            }}
            .result-highlight {{
                font-weight: bold;
                color: #0066cc;
            }}
            .image-container {{
                text-align: center;
                margin: 30px 0;
            }}
            img {{
                max-width: 100%;
                height: auto;
                border: 1px solid #eee;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                font-size: 0.9em;
                color: #666;
                border-top: 1px solid #eee;
                padding-top: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Báo cáo tính toán tối ưu mặt cắt đập bê tông trọng lực</h1>
        
        <h2>Thông số đầu vào</h2>
        <table>
            <tr>
                <th>Thông số</th>
                <th>Giá trị</th>
            </tr>
            <tr>
                <td>Chiều cao đập (H)</td>
                <td>{result['H']:.2f} m</td>
            </tr>
            <tr>
                <td>Trọng lượng riêng bê tông (γ_bt)</td>
                <td>{result['gamma_bt']:.2f} T/m³</td>
            </tr>
            <tr>
                <td>Trọng lượng riêng nước (γ_n)</td>
                <td>{result['gamma_n']:.2f} T/m³</td>
            </tr>
            <tr>
                <td>Hệ số ma sát (f)</td>
                <td>{result['f']:.2f}</td>
            </tr>
            <tr>
                <td>Cường độ kháng cắt (C)</td>
                <td>{result['C']:.2f} T/m²</td>
            </tr>
            <tr>
                <td>Hệ số ổn định yêu cầu (Kc)</td>
                <td>{result['Kc']:.2f}</td>
            </tr>
            <tr>
                <td>Hệ số áp lực thấm (α1)</td>
                <td>{result['a1']:.2f}</td>
            </tr>
        </table>
        
        <h2>Kết quả tính toán</h2>
        <table>
            <tr>
                <th>Thông số</th>
                <th>Giá trị</th>
            </tr>
            <tr>
                <td>Hệ số mái thượng lưu (n)</td>
                <td class="result-highlight">{result['n']:.4f}</td>
            </tr>
            <tr>
                <td>Hệ số mái hạ lưu (m)</td>
                <td class="result-highlight">{result['m']:.4f}</td>
            </tr>
            <tr>
                <td>Tham số ξ</td>
                <td class="result-highlight">{result['xi']:.4f}</td>
            </tr>
            <tr>
                <td>Diện tích mặt cắt (A)</td>
                <td class="result-highlight">{result['A']:.4f} m²</td>
            </tr>
            <tr>
                <td>Hệ số ổn định (K)</td>
                <td class="result-highlight">{result['K']:.4f}</td>
            </tr>
            <tr>
                <td>Ứng suất mép thượng lưu (σ)</td>
                <td class="result-highlight">{result['sigma']:.4f} T/m²</td>
            </tr>
            <tr>
                <td>Thời gian tính toán</td>
                <td>{result['computation_time']:.2f} giây</td>
            </tr>
        </table>
        
        <h2>Sơ đồ lực tác dụng</h2>
        <div class="image-container">
            <img src="data:image/png;base64,{dam_img}" alt="Sơ đồ lực tác dụng lên đập">
        </div>
        
        <h2>Biểu đồ hàm mất mát</h2>
        <div class="image-container">
            <img src="data:image/png;base64,{loss_img}" alt="Biểu đồ hàm mất mát">
        </div>
        
        <div class="footer">
            <p>Báo cáo được tạo bởi Công cụ tính toán tối ưu mặt cắt đập bê tông trọng lực</p>
            <p>Sử dụng mô hình Physics-Informed Neural Networks (PINNs)</p>
            <p>Ngày tạo: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    </body>
    </html>
    """
    
    return html
