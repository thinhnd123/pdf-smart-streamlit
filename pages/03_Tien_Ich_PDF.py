import streamlit as st
import tempfile

from services.pdf_merge_service import run_pdf_merge


st.title("🛠️ TIỆN ÍCH PDF")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Ghép PDF",
    "Tách PDF",
    "Ảnh → PDF",
    "Nén PDF",
    "Giảm dung lượng",
    "Hạ phiên bản PDF",
    "Xoá trang trắng"
])

# ==================================================
# TAB 1 - GHÉP PDF
# ==================================================

with tab1:

    st.subheader("📎 Ghép nhiều file PDF")

    uploaded_files = st.file_uploader(
        "Chọn các file PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

    st.info(
        "Thứ tự file trong danh sách sẽ là thứ tự ghép."
    )

    if st.button(
        "🚀 Ghép PDF",
        key="merge_pdf"
    ):

        if not uploaded_files:

            st.error("Vui lòng chọn file PDF")

            st.stop()

        temp_paths = []

        for file in uploaded_files:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:

                tmp.write(file.getvalue())

                temp_paths.append(tmp.name)

        with st.spinner("Đang ghép PDF..."):

            output_pdf, msg = run_pdf_merge(
                temp_paths
            )

        if output_pdf:

            st.success(msg)

            with open(output_pdf, "rb") as f:

                st.download_button(
                    label="📥 Tải PDF đã ghép",
                    data=f.read(),
                    file_name="Merged.pdf",
                    mime="application/pdf"
                )

        else:

            st.error(msg)

# ==================================================
# TAB 2-7 (tạm thời placeholder)
# ==================================================

with tab2:
    st.info("Đang phát triển")

with tab3:
    st.info("Đang phát triển")

with tab4:
    st.info("Đang phát triển")

with tab5:
    st.info("Đang phát triển")

with tab6:
    st.info("Đang phát triển")

with tab7:
    st.info("Đang phát triển")