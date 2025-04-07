"""
Mô-đun tính toán tối ưu mặt cắt đập bê tông trọng lực sử dụng PINNs
"""

import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import os
import time
from typing import Dict, List, Tuple, Union, Optional

class OptimalParamsNet(nn.Module):
    """
    Mạng neural network để tìm tham số tối ưu cho mặt cắt đập bê tông
    """
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 64), nn.Tanh(),
            nn.Linear(64, 64), nn.Tanh(),
            nn.Linear(64, 3), nn.Sigmoid()
        )

    def forward(self, x):
        out = self.net(x)
        # Giới hạn đầu ra
        n = out[:, 0] * 0.4             # n ∈ [0, 0.4]
        m = out[:, 1] * 3.5 + 0.5       # m ∈ [0.5, 4.0]
        xi = out[:, 2] * 0.99 + 0.01    # xi ∈ (0.01, 1]
        return n, m, xi

def compute_physics(n: torch.Tensor, xi: torch.Tensor, m: torch.Tensor, H: float, 
                   gamma_bt: float, gamma_n: float, f: float, C: float, a1: float) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Tính toán các thông số vật lý của đập
    
    Args:
        n: Tham số n
        xi: Tham số xi
        m: Tham số m
        H: Chiều cao đập (m)
        gamma_bt: Trọng lượng riêng bê tông (T/m³)
        gamma_n: Trọng lượng riêng nước (T/m³)
        f: Hệ số ma sát
        C: Cường độ kháng cắt (T/m²)
        a1: Hệ số áp lực thấm
        
    Returns:
        Tuple chứa ứng suất mép thượng lưu (sigma), hệ số ổn định (K), diện tích mặt cắt (A)
    """
    B = H * (m + n * (1 - xi))
    G1 = 0.5 * gamma_bt * m * H**2
    G2 = 0.5 * gamma_bt * n * H**2 * (1 - xi)**2
    G = G1 + G2
    W1 = 0.5 * gamma_n * H**2
    W2_1 = gamma_n * n * (1 - xi) * xi * H**2
    W2_2 = 0.5 * gamma_n * n * H**2 * (1 - xi)**2
    W2 = W2_1 + W2_2
    Wt = 0.5 * gamma_n * a1 * H * (m * H + n * H * (1 - xi))
    P = G + W2 - Wt
    lG1 = H * (m / 6 - n * (1 - xi) / 2)
    lG2 = H * (m / 2 - n * (1 - xi) / 6)
    lt  = H * (m + n * (1 - xi)) / 6
    l2  = H * m / 2
    l22 = H * m / 2 + H * n * (1 - xi) / 6
    l1  = H / 3
    M0 = -G1 * lG1 - G2 * lG2 + Wt * lt - W2_1 * l2 - W2_2 * l22 + W1 * l1
    sigma = P / B - 6 * M0 / B**2
    Fct = f * (G + W2 - Wt) + C * H * (m + n * (1 - xi))
    Fgt = 0.5 * gamma_n * H**2
    K = Fct / Fgt
    A = 0.5 * H**2 * (m + n * (1 - xi)**2)
    return sigma, K, A

def loss_function(sigma: torch.Tensor, K: torch.Tensor, A: torch.Tensor, 
                 Kc: float, factor: float = 1.0, alpha: float = 0.01) -> torch.Tensor:
    """
    Hàm mất mát để tối ưu hóa mặt cắt đập
    
    Args:
        sigma: Ứng suất mép thượng lưu
        K: Hệ số ổn định
        A: Diện tích mặt cắt
        Kc: Hệ số ổn định yêu cầu
        factor: Hệ số nhân cho Kc (mặc định: 1.0)
        alpha: Hệ số phạt diện tích (mặc định: 0.01)
        
    Returns:
        Giá trị hàm mất mát
    """
    K_min = Kc * factor
    BIG_PENALTY = 1e5
    penalty_K = torch.clamp(K_min - K, min=0)**2
    penalty_K = BIG_PENALTY * penalty_K
    penalty_sigma = sigma**2
    return penalty_K.mean() + 100 * penalty_sigma.mean() + alpha * A.mean()

def optimize_dam_section(
    H: float,
    gamma_bt: float = 2.4,
    gamma_n: float = 1.0,
    f: float = 0.7,
    C: float = 0.5,
    Kc: float = 1.2,
    a1: float = 0.6,
    alpha: float = 0.01,
    k_factor: float = 1.0,
    epochs: int = 5000,
    device: Optional[str] = None,
    verbose: bool = True
) -> Dict:
    """
    Tính toán tối ưu mặt cắt đập bê tông trọng lực sử dụng PINNs
    
    Args:
        H: Chiều cao đập (m)
        gamma_bt: Trọng lượng riêng bê tông (T/m³)
        gamma_n: Trọng lượng riêng nước (T/m³)
        f: Hệ số ma sát
        C: Cường độ kháng cắt (T/m²)
        Kc: Hệ số ổn định yêu cầu
        a1: Hệ số áp lực thấm
        alpha: Hệ số phạt diện tích
        k_factor: Hệ số nhân cho Kc
        epochs: Số vòng lặp tối đa
        device: Thiết bị tính toán (CPU/GPU)
        verbose: Hiển thị thông tin trong quá trình tính toán
        
    Returns:
        Dict: Kết quả tính toán bao gồm các tham số tối ưu và các giá trị liên quan
    """
    # Xác định thiết bị tính toán
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Khởi tạo mô hình và tối ưu hóa
    model = OptimalParamsNet().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    
    # Dữ liệu đầu vào
    data = torch.ones((1, 1), device=device)
    
    # Theo dõi quá trình huấn luyện
    loss_history = []
    start_time = time.time()
    
    # Huấn luyện mô hình
    for epoch in range(epochs):
        optimizer.zero_grad()
        n, m, xi = model(data)
        sigma, K, A = compute_physics(n, xi, m, H, gamma_bt, gamma_n, f, C, a1)
        loss = loss_function(sigma, K, A, Kc, k_factor, alpha)
        loss.backward()
        optimizer.step()
        loss_history.append(loss.item())
        
        if verbose and epoch % 500 == 0:
            print(f"Epoch {epoch}: Loss = {loss.item():.6f}")
    
    # Tính toán kết quả cuối cùng
    model.eval()
    with torch.no_grad():
        n, m, xi = model(data)
        sigma, K, A = compute_physics(n, xi, m, H, gamma_bt, gamma_n, f, C, a1)
    
    # Chuyển đổi kết quả sang numpy
    n_value = n.item()
    m_value = m.item()
    xi_value = xi.item()
    sigma_value = sigma.item()
    K_value = K.item()
    A_value = A.item()
    
    # Tính toán thời gian
    elapsed_time = time.time() - start_time
    
    # Trả về kết quả
    return {
        'n': n_value,
        'm': m_value,
        'xi': xi_value,
        'A': A_value,
        'K': K_value,
        'sigma': sigma_value,
        'loss_history': loss_history,
        'computation_time': elapsed_time,
        'H': H,
        'gamma_bt': gamma_bt,
        'gamma_n': gamma_n,
        'f': f,
        'C': C,
        'Kc': Kc,
        'a1': a1
    }

def generate_force_diagram(result: Dict, save_path: Optional[str] = None) -> plt.Figure:
    """
    Tạo sơ đồ lực tác dụng lên đập
    
    Args:
        result: Kết quả tính toán từ hàm optimize_dam_section
        save_path: Đường dẫn để lưu hình ảnh (nếu None, không lưu)
        
    Returns:
        Figure: Đối tượng Figure của matplotlib
    """
    from matplotlib.patches import FancyArrow
    
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
    
    if save_path:
        plt.savefig(save_path)
        plt.close(fig)
    
    return fig

def plot_loss_history(loss_history: List[float], save_path: Optional[str] = None) -> plt.Figure:
    """
    Vẽ biểu đồ hàm mất mát
    
    Args:
        loss_history: Lịch sử giá trị hàm mất mát
        save_path: Đường dẫn để lưu hình ảnh (nếu None, không lưu)
        
    Returns:
        Figure: Đối tượng Figure của matplotlib
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(loss_history)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Loss")
    ax.set_title("Hàm mất mát trong quá trình huấn luyện")
    ax.grid(True)
    
    if save_path:
        plt.savefig(save_path)
        plt.close(fig)
    
    return fig
