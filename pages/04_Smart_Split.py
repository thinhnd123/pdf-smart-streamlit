import streamlit as st

st.title("🧠 Tách PDF Thông Minh")

uploaded_pdf = st.file_uploader(
    "Chọn PDF",
    type=["pdf"]
)

keyword = st.text_input(
    "Từ khóa",
    value="GIẤY CHỨNG NHẬN HIỆU CHUẨN"
)

naming_type = st.selectbox(
    "Kiểu đặt tên",
    [
        ("ma_ql", "Mã quản lý"),
        ("so_gcn", "Số GCN"),
        ("ten_tb", "Tên thiết bị + Model")
    ],
    format_func=lambda x: x[1]
)