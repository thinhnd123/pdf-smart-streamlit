# run_app.py
import os
import sys
import time
import threading
import webbrowser
import streamlit.web.cli as stcli

def open_browser():
    """Hàm chạy ngầm: Đợi 3 giây cho Server mở cổng rồi mới bật trình duyệt"""
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

if __name__ == "__main__":
    # 🎯 ĐÃ SỬA: Xác định chính xác vị trí file app.py nằm bên trong bộ cài
    if getattr(sys, 'frozen', False):
        # Khi chạy từ file EXE, lấy thư mục tạm hệ thống (nơi chứa _internal)
        base_path = sys._MEIPASS 
    else:
        # Khi chạy dev local bình thường ở máy nhà
        base_path = os.path.dirname(__file__)
        
    app_path = os.path.join(base_path, "app.py")
    
    sys.argv = [
        "streamlit", 
        "run", 
        app_path, 
        "--global.developmentMode=false",
        "--server.headless=true",          
        "--server.port=8501"               
    ]
    
    # KÍCH HOẠT BỘ HẸN GIỜ: Chạy ngầm việc mở trình duyệt sau 3 giây
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Kích hoạt máy chủ Streamlit ngay lập tức
    sys.exit(stcli.main())