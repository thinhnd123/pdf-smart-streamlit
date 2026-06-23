import streamlit as st

st.set_page_config(
    page_title="PDF SMART",
    layout="wide"
)

with st.sidebar:
    st.title("PDF SMART")
    st.write("Phiên bản nội bộ v1.0")

    page = st.radio(
        "MENU CHỨC NĂNG",
        [
            "Trang Chủ",
            "Tự Động Hóa Hồ Sơ",
            "Tiện Ích PDF",
            "Tách PDF Thông Minh",
            "Tách PDF theo Excel",
            "Đổi tên PDF Scan (Folder)"
        ]
    )

st.title("Trang Chủ")