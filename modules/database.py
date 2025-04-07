"""
Mô-đun cơ sở dữ liệu cho ứng dụng tính toán tối ưu mặt cắt đập bê tông
"""

import sqlite3
import pandas as pd
import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

class DamDatabase:
    """
    Lớp quản lý cơ sở dữ liệu SQLite cho ứng dụng tính toán tối ưu mặt cắt đập bê tông
    """
    
    def __init__(self, db_path: str = "data/dam_results.db"):
        """
        Khởi tạo kết nối đến cơ sở dữ liệu
        
        Args:
            db_path: Đường dẫn đến file cơ sở dữ liệu SQLite
        """
        # Đảm bảo thư mục tồn tại
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Tạo các bảng cần thiết nếu chưa tồn tại"""
        cursor = self.conn.cursor()
        
        # Tạo bảng lưu kết quả tính toán
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculation_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            H REAL,
            gamma_bt REAL,
            gamma_n REAL,
            f REAL,
            C REAL,
            Kc REAL,
            a1 REAL,
            n REAL,
            m REAL,
            xi REAL,
            A REAL,
            K REAL,
            sigma REAL,
            loss_history TEXT,
            computation_time REAL
        )
        ''')
        
        self.conn.commit()
    
    def save_result(self, result: Dict[str, Any]) -> int:
        """
        Lưu kết quả tính toán vào cơ sở dữ liệu
        
        Args:
            result: Kết quả tính toán từ mô-đun PINNs
            
        Returns:
            ID của bản ghi vừa thêm
        """
        cursor = self.conn.cursor()
        
        # Chuyển đổi loss_history thành chuỗi JSON
        loss_history_json = json.dumps(result['loss_history'])
        
        # Thêm timestamp hiện tại
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
        INSERT INTO calculation_results (
            timestamp, H, gamma_bt, gamma_n, f, C, Kc, a1,
            n, m, xi, A, K, sigma, loss_history, computation_time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp, result['H'], result['gamma_bt'], result['gamma_n'],
            result['f'], result['C'], result['Kc'], result['a1'],
            result['n'], result['m'], result['xi'], result['A'],
            result['K'], result['sigma'], loss_history_json, result['computation_time']
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_result_by_id(self, result_id: int) -> Optional[Dict[str, Any]]:
        """
        Lấy kết quả tính toán theo ID
        
        Args:
            result_id: ID của kết quả cần lấy
            
        Returns:
            Dictionary chứa kết quả tính toán hoặc None nếu không tìm thấy
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM calculation_results WHERE id = ?', (result_id,))
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        # Lấy tên các cột
        columns = [description[0] for description in cursor.description]
        
        # Tạo dictionary từ kết quả truy vấn
        result = dict(zip(columns, row))
        
        # Chuyển đổi chuỗi JSON thành list
        result['loss_history'] = json.loads(result['loss_history'])
        
        return result
    
    def get_all_results(self) -> pd.DataFrame:
        """
        Lấy tất cả kết quả tính toán
        
        Returns:
            DataFrame chứa tất cả kết quả tính toán
        """
        query = 'SELECT * FROM calculation_results ORDER BY timestamp DESC'
        df = pd.read_sql_query(query, self.conn)
        
        # Chuyển đổi chuỗi JSON thành list
        if not df.empty and 'loss_history' in df.columns:
            df['loss_history'] = df['loss_history'].apply(json.loads)
        
        return df
    
    def search_results(self, H: Optional[float] = None, min_K: Optional[float] = None) -> pd.DataFrame:
        """
        Tìm kiếm kết quả tính toán theo các tiêu chí
        
        Args:
            H: Chiều cao đập (nếu None, không lọc theo chiều cao)
            min_K: Hệ số ổn định tối thiểu (nếu None, không lọc theo hệ số ổn định)
            
        Returns:
            DataFrame chứa kết quả tìm kiếm
        """
        query = 'SELECT * FROM calculation_results WHERE 1=1'
        params = []
        
        if H is not None:
            # Tìm kiếm với sai số 0.01
            query += ' AND ABS(H - ?) < 0.01'
            params.append(H)
        
        if min_K is not None:
            query += ' AND K >= ?'
            params.append(min_K)
        
        query += ' ORDER BY timestamp DESC'
        
        df = pd.read_sql_query(query, self.conn, params=params)
        
        # Chuyển đổi chuỗi JSON thành list
        if not df.empty and 'loss_history' in df.columns:
            df['loss_history'] = df['loss_history'].apply(json.loads)
        
        return df
    
    def delete_result(self, result_id: int) -> bool:
        """
        Xóa kết quả tính toán theo ID
        
        Args:
            result_id: ID của kết quả cần xóa
            
        Returns:
            True nếu xóa thành công, False nếu không tìm thấy
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM calculation_results WHERE id = ?', (result_id,))
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def close(self):
        """Đóng kết nối đến cơ sở dữ liệu"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Đảm bảo đóng kết nối khi đối tượng bị hủy"""
        self.close()
