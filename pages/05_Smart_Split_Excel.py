import streamlit as st
import tempfile

from pathlib import Path

from backend.smart_splitter import smart_split_pdf_with_excel


st.set_page_config(
    page_title="Tách PDF Theo Excel",
    layout="wide"
)

st.title("📊 TÁCH PDF THEO EXCEL")

st.markdown("""
Tách PDF tổng → Bóc mã GCN → Đối chiếu Excel → Đổi tên file tự động.
""")

st.markdown("---")

# =========================
# Upload PDF
# =========================

uploaded_pdf = st.file_uploader(
    label="📄 Chọn file PDF tổng",
    type=["pdf"]
)

# =========================
# Upload Excel
# =========================

uploaded_excel = st.file_uploader(
    label="📊 Chọn file Excel đối chiếu",
    type=["xlsx", "xls"]
)

# =========================
# Keyword
# =========================

keyword = st.text_input(
    label="🔍 Từ khóa nhận diện điểm cắt",
    value="GIẤY CHỨNG NHẬN HIỆU CHUẨN"
)

# =========================
# Naming options
# =========================

naming_options = {
    "Tên thiết bị + Model": "ten_tb",
    "Mã quản lý": "ma_ql"
}

selected_label = st.selectbox(
    label="📝 Kiểu đặt tên file",
    options=list(naming_options.keys())
)

naming_type = naming_options[selected_label]

st.markdown("---")

# =========================
# Run button
# =========================

if st.button("🚀 Tách PDF & Đối Chiếu Excel", use_container_width=True):

    if uploaded_pdf is None:
        st.error("⚠️ Vui lòng chọn file PDF.")
        st.stop()

    if uploaded_excel is None:
        st.error("⚠️ Vui lòng chọn file Excel.")
        st.stop()

    try:

        # =========================
        # Save PDF temp
        # =========================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp_pdf:

            tmp_pdf.write(uploaded_pdf.getvalue())

            pdf_path = tmp_pdf.name

        # =========================
        # Save Excel temp
        # =========================

        excel_suffix = Path(uploaded_excel.name).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=excel_suffix
        ) as tmp_excel:

            tmp_excel.write(uploaded_excel.getvalue())

            excel_path = tmp_excel.name

        # =========================
        # Execute
        # =========================

        with st.spinner("⏳ Đang tách PDF và đối chiếu Excel..."):

            zip_path, msg = smart_split_pdf_with_excel(
                pdf_path=pdf_path,
                excel_path=excel_path,
                keyword=keyword,
                naming_type=naming_type
            )

        # =========================
        # Result
        # =========================

        if zip_path and Path(zip_path).exists():

            st.success(msg)

            with open(zip_path, "rb") as f:

                st.download_button(
                    label="📥 Tải ZIP kết quả",
                    data=f.read(),
                    file_name=Path(zip_path).name,
                    mime="application/zip",
                    use_container_width=True
                )

        else:

            st.error(msg)

    except Exception as e:

        st.exception(e)