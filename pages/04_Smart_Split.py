import streamlit as st
import tempfile

from pathlib import Path

from backend.smart_splitter import smart_split_pdf


st.title("🧠 Tách PDF Thông Minh")

st.markdown("---")

uploaded_pdf = st.file_uploader(
    "Chọn file PDF",
    type=["pdf"]
)

keyword = st.text_input(
    "Từ khóa nhận diện điểm cắt",
    value="GIẤY CHỨNG NHẬN HIỆU CHUẨN"
)

naming_options = {
    "Mã quản lý": "ma_ql",
    "Số GCN": "so_gcn",
    "Tên thiết bị + Model": "ten_tb"
}

selected_label = st.selectbox(
    "Kiểu đặt tên",
    list(naming_options.keys())
)

naming_type = naming_options[selected_label]


if st.button("🚀 Bắt đầu tách"):

    if uploaded_pdf is None:
        st.error("Vui lòng chọn file PDF")
        st.stop()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
    ) as tmp:

        tmp.write(uploaded_pdf.getvalue())

        pdf_path = tmp.name

    with st.spinner("Đang xử lý PDF..."):

        zip_path, msg = smart_split_pdf(
            pdf_path=pdf_path,
            keyword=keyword,
            naming_type=naming_type
        )

    st.success(msg)

    if zip_path and Path(zip_path).exists():

        with open(zip_path, "rb") as f:

            st.download_button(
                label="📥 Tải ZIP kết quả",
                data=f.read(),
                file_name=Path(zip_path).name,
                mime="application/zip"
            )