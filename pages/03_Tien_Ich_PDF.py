import streamlit as st
import tempfile

import fitz
from PIL import Image
import io
from services.pdf_split_service import run_pdf_split_range
from services.pdf_merge_service import run_pdf_merge
from services.image_to_pdf_service import run_image_to_pdf

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

    st.subheader("✂️ Tách PDF theo điểm cắt")

    uploaded_pdf = st.file_uploader(
        "Chọn PDF",
        type=["pdf"],
        key="split_pdf"
    )

    if uploaded_pdf:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(uploaded_pdf.getvalue())

            pdf_path = tmp.name

        doc = fitz.open(pdf_path)

        total_pages = len(doc)

        st.info(
            f"Tổng số trang: {total_pages}"
        )

        st.markdown("### Chọn các trang kết thúc hồ sơ")

        cut_pages = []

        cols = st.columns(4)

        for page_num in range(total_pages):

            page = doc[page_num]

            pix = page.get_pixmap(
                matrix=fitz.Matrix(
                    0.3,
                    0.3
                )
            )

            img = Image.open(
                io.BytesIO(
                    pix.tobytes("png")
                )
            )

            with cols[page_num % 4]:

                st.image(
                    img,
                    caption=f"Trang {page_num + 1}"
                )

                checked = st.checkbox(
                    "✂ Cắt tại đây",
                    key=f"cut_{page_num}"
                )

                if checked:

                    cut_pages.append(
                        page_num + 1
                    )

        doc.close()

        st.markdown("---")

        if cut_pages:

            cut_pages = sorted(
                list(
                    set(cut_pages)
                )
            )

            ranges = []

            start_page = 1

            for end_page in cut_pages:

                ranges.append(
                    f"{start_page}-{end_page}"
                )

                start_page = end_page + 1

            if start_page <= total_pages:

                ranges.append(
                    f"{start_page}-{total_pages}"
                )

            generated_text = "\n".join(
                ranges
            )

            st.markdown(
                "### Khoảng trang tự sinh"
            )

            st.code(
                generated_text
            )

        else:

            generated_text = ""

            st.warning(
                "Chưa chọn điểm cắt nào"
            )

        st.markdown("---")

        if st.button(
            "🚀 Tách PDF",
            key="split_by_checkbox"
        ):

            if not generated_text:

                st.error(
                    "Vui lòng chọn ít nhất 1 điểm cắt"
                )

                st.stop()

            with st.spinner(
                "Đang tách PDF..."
            ):

                zip_path, msg = run_pdf_split_range(
                    pdf_path,
                    generated_text
                )

            if zip_path:

                st.success(
                    msg
                )

                with open(
                    zip_path,
                    "rb"
                ) as f:

                    st.download_button(
                        "📥 Tải ZIP",
                        data=f.read(),
                        file_name="Split.zip",
                        mime="application/zip"
                    )

            else:

                st.error(
                    msg
                )
with tab3:

    st.subheader(
        "🖼️ Ảnh → PDF"
    )

    uploaded_images = st.file_uploader(
        "Chọn ảnh",
        type=[
            "jpg",
            "jpeg",
            "png",
            "bmp",
            "webp"
        ],
        accept_multiple_files=True,
        key="image_to_pdf"
    )

    if uploaded_images:

        st.success(
            f"Đã chọn {len(uploaded_images)} ảnh"
        )

        st.markdown("### Preview")

        cols = st.columns(4)

        for i, img_file in enumerate(uploaded_images):

            image = Image.open(img_file)

            with cols[i % 4]:

                st.image(
                    image,
                    caption=f"{i+1}"
                )

        st.markdown("---")

        reverse_order = st.checkbox(
            "Đảo ngược thứ tự ảnh"
        )

        paper_size = st.selectbox(
            "Khổ giấy",
            [
                "Giữ nguyên",
                "A4",
                "A5"
            ]
        )

        orientation = st.selectbox(
            "Chiều giấy",
            [
                "Tự động",
                "Dọc",
                "Ngang"
            ]
        )

    if st.button(
        "🚀 Chuyển thành PDF",
        key="convert_image_pdf"
    ):

        if not uploaded_images:

            st.error(
                "Vui lòng chọn ảnh"
            )

            st.stop()

        temp_paths = []

        for img in uploaded_images:

            suffix = "." + img.name.split(".")[-1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as tmp:

                tmp.write(
                    img.getvalue()
                )

                temp_paths.append(
                    tmp.name
                )

        with st.spinner(
            "Đang tạo PDF..."
        ):

            pdf_path, msg = run_image_to_pdf(
                image_paths=temp_paths,
                paper_size=paper_size,
                orientation=orientation
            )

        if pdf_path:

            st.success(msg)

            with open(
                pdf_path,
                "rb"
            ) as f:

                st.download_button(
                    "📥 Tải PDF",
                    data=f.read(),
                    file_name="Images.pdf",
                    mime="application/pdf"
                )

        else:

            st.error(msg)

with tab4:
    st.info("Đang phát triển")

with tab5:
    st.info("Đang phát triển")

with tab6:
    st.info("Đang phát triển")

with tab7:
    st.info("Đang phát triển")