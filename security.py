# security.py
import streamlit as st

# Mật mã bí mật bằng bàn phím của bạn (Viết liền, không dấu, ví dụ: 'open')
SECRET_HOTKEY = "famille123"

def check_security():
    # Tạo biến trạng thái kiểm tra xem trình duyệt đã được bạn kích hoạt chưa
    if "is_unlocked" not in st.session_state:
        st.session_state["is_unlocked"] = False

    # Nếu chưa kích hoạt, hiện màn hình lỗi mạng 100% nguyên bản
    if not st.session_state["is_unlocked"]:
        
        # Giao diện lỗi mạng y như thật, hoàn toàn không có nút bấm hay ô nhập liệu nào
        st.error("❌ ERR_CONNECTION_TIMED_OUT: Mạng Internet quá yếu!")
        st.warning("""
        ### 🌐 Kết nối thất bại... hixhix! 😭
        Đường truyền Internet tại khu vực của bạn hiện tại **không đủ băng thông** để gánh ứng dụng này. 🐌💨
        * **Lời khuyên :** Bạn vui lòng liên hệ công ty đổi mạng, hoặc nâng cấp gói mạng xem sao nhé! 🔌🤪
        * **Thời gian chờ:** Vui lòng đợi mạng mạnh rồi quay lại sau nha! ⏱️🛌
        """)
        #st.info("🔄 Hệ thống đang cố gắng kết nối lại với vệ tinh NASA... xin vui lòng chờ đợi vô thời hạn...")
        
        # 🕵️‍♂️ KHU VỰC BẪY PHÍM ẨN:
        # Chúng ta dùng st.chat_input (ô nhập liệu góc dưới màn hình) nhưng NGỤY TRANG nhãn của nó thành một dòng chữ hệ thống xám mờ. 
        # Người ngoài nhìn vào sẽ tưởng đây là ô hiển thị trạng thái log hệ thống hoặc thanh tiến trình bị đơ.
        trigger = st.chat_input("System Status: Attempting to reconnect...")
        
        # Nếu BẠN là người ngồi trước máy và gõ đúng chữ 'open' vào thanh này rồi nhấn Enter
        if trigger == SECRET_HOTKEY:
            st.session_state["is_unlocked"] = True
            st.rerun()
            
        st.stop() # Khóa cứng ứng dụng!