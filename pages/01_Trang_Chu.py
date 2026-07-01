import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from security import check_security

# Gọi hàm kiểm tra ngay đầu trang!
check_security()

st.title("🚀 HỆ THỐNG QUẢN TRỊ & XỬ LÝ HỒ SƠ THÔNG MINH")

st.divider()

st.markdown("""
Chào mừng bạn đến với ứng dụng tự động hóa nội bộ.

### Hướng dẫn nhanh

- Sử dụng menu bên trái để chuyển đổi chức năng.
- Hệ thống chạy offline.
- Không giới hạn lượt sử dụng.
- Toàn bộ dữ liệu được xử lý nội bộ.
""")