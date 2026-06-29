import streamlit as st
import tempfile
import math
import fitz
from PIL import Image
import io
from services.pdf_split_service import run_pdf_split_range
from services.pdf_merge_service import run_pdf_merge
from services.image_to_pdf_service import run_image_to_pdf

from services.image_to_pdf_ocr_service import (
    run_image_to_pdf_ocr
)

from services.pdf_compress_service import (
    run_pdf_compress
)

from services.pdf_reduce_v2_service import (
    run_pdf_reduce_v2
)

from services.pdf_version_service import (
    run_pdf_version_downgrade
)

from services.remove_blank_page_service import (
    run_remove_blank_last_page
)

from services.remove_blank_pages_v2_service import (
    run_remove_blank_pages_batch
)

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
# Giữ nguyên hàm cache của bạn
@st.cache_data(show_spinner=False)
def get_thumbnail(pdf_bytes, page_num, zoom=0.25):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(page_num)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    doc.close()
    return img

def next_thumb_page():
    if st.session_state.thumb_page < st.session_state.total_thumb_pages:
        st.session_state.thumb_page += 1


def prev_thumb_page():
    if st.session_state.thumb_page > 1:
        st.session_state.thumb_page -= 1
        
        
# ==========================================
#  ĐOẠN CODE TRONG TAB 2
# ==========================================
with tab2:
    st.subheader("✂️ Tách PDF theo điểm cắt")

    uploaded_pdf = st.file_uploader(
        "Chọn PDF",
        type=["pdf"],
        key="split_pdf"
    )

    if uploaded_pdf:
        if "split_pdf_path" not in st.session_state:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_pdf.getvalue())
                st.session_state.split_pdf_path = tmp.name

        pdf_path = st.session_state.split_pdf_path
        pdf_bytes = uploaded_pdf.getvalue()

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        total_pages = len(doc)
        doc.close()

        st.info(f"Tổng số trang: {total_pages}")

        if "cut_pages" not in st.session_state:
            st.session_state.cut_pages = []

        # ==========================
        # PAGINATION THUMBNAIL
        # ==========================
        thumb_per_page = 50
        total_thumb_pages = max(1, math.ceil(total_pages / thumb_per_page))
        st.session_state.total_thumb_pages = total_thumb_pages

        col1, col2, col3 = st.columns([2, 2, 6])

        if "thumb_page" not in st.session_state:
            st.session_state.thumb_page = 1

        with col1:
            st.number_input(
                "Trang preview",
                min_value=1,
                max_value=total_thumb_pages,
                key="thumb_page"
            )

        thumb_page = st.session_state.thumb_page

        with col2:
            st.markdown(
                f"<div style='margin-top:32px'>{total_thumb_pages} trang preview</div>",
                unsafe_allow_html=True
            )

        start_idx = (thumb_page - 1) * thumb_per_page
        end_idx = min(start_idx + thumb_per_page, total_pages)

        # =============================================================
        # BỌC LƯỚI ẢNH VÀ TOGGLE VÀO TRONG ST.FORM
        # Người dùng có thể bấm thoải mái 50 toggle mà không bị load lại trang
        # =============================================================
        with st.form(key="pdf_cut_nodes_form"):
            st.markdown("### Chọn các trang kết thúc hồ sơ")
            cols = st.columns(4)
            
            # Tạo một dictionary tạm để lưu trạng thái toggle hiện tại trong form
            current_form_states = {}

            for idx in range(start_idx, end_idx):
                from utils.pdf_thumbnail_cache import get_thumbnail
                img = get_thumbnail(pdf_bytes, idx)

                with cols[(idx - start_idx) % 4]:
                    st.image(img, caption=f"Trang {idx + 1}")

                    # Lưu trạng thái toggle vào dictionary tạm, key là số trang thực tế (idx + 1)
                    current_form_states[idx + 1] = st.toggle(
                        "✂ Cắt tại đây",
                        value=(idx + 1 in st.session_state.cut_pages),
                        key=f"cut_{idx}"
                    )

            st.markdown("<br>", unsafe_allow_html=True)
            # Nút submit bắt buộc của Form để áp dụng các điểm cắt
            submit_cuts = st.form_submit_button("💾 Xác nhận & Lưu điểm cắt của trang này")

            if submit_cuts:
                # Duyệt qua các toggle trong form và cập nhật chính xác vào cut_pages gốc
                for page_num, checked in current_form_states.items():
                    if checked:
                        if page_num not in st.session_state.cut_pages:
                            st.session_state.cut_pages.append(page_num)
                    else:
                        if page_num in st.session_state.cut_pages:
                            st.session_state.cut_pages.remove(page_num)
                
                # Ép ứng dụng rerun một lần duy nhất để cập nhật bảng "Khoảng trang tự sinh" bên dưới
                st.rerun()

        # =============================================================
        # KẾT THÚC VÙNG FORM
        # =============================================================

        st.markdown("---")

        # Nút chuyển trang preview lớn (Nằm ngoài form)
        col_prev, col_next = st.columns(2)
        with col_prev:
            st.button(
                "⬅ Previous",
                on_click=prev_thumb_page,
                key="prev_thumb_page"
            )
        with col_next:
            st.button(
                "Next ➡",
                on_click=next_thumb_page,
                key="next_thumb_page"
            )
                    
        # Xử lý hiển thị khoảng trang tự sinh (Giữ nguyên logic của bạn)
        cut_pages = sorted(st.session_state.cut_pages)
        
        if cut_pages:
            cut_pages = sorted(list(set(cut_pages)))
            ranges = []
            start_page = 1

            for end_page in cut_pages:
                ranges.append(f"{start_page}-{end_page}")
                start_page = end_page + 1

            if start_page <= total_pages:
                ranges.append(f"{start_page}-{total_pages}")

            generated_text = "\n".join(ranges)

            st.markdown("### Khoảng trang tự sinh")
            st.code(generated_text)
        else:
            generated_text = ""
            st.warning("Chưa chọn điểm cắt nào")

        st.markdown("---")

        # Nút bấm tiến hành Tách PDF (Giữ nguyên logic của bạn)
        if st.button("🚀 Tách PDF", key="split_by_checkbox"):
            if not generated_text:
                st.error("Vui lòng chọn ít nhất 1 điểm cắt")
                st.stop()

            with st.spinner("Đang tách PDF..."):
                zip_path, msg = run_pdf_split_range(
                    pdf_path,
                    generated_text
                )

            if zip_path:
                st.session_state.cut_pages = []
                st.success(msg)

                with open(zip_path, "rb") as f:
                    st.download_button(
                        "📥 Tải ZIP",
                        data=f.read(),
                        file_name="Split.zip",
                        mime="application/zip"
                    )
            else:
                st.error(msg)
                
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

        ocr_mode = st.checkbox(
            "🔍 OCR PDF (tìm kiếm được)"
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

            if ocr_mode:

                pdf_path, msg = run_image_to_pdf_ocr(
                    temp_paths
                )

            else:

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

    st.subheader(
        "📦 Nén PDF"
    )

    uploaded_pdf = st.file_uploader(
        "Chọn PDF",
        type=["pdf"],
        key="compress_pdf"
    )

    if st.button(
        "🚀 Nén PDF",
        key="compress_btn"
    ):

        if not uploaded_pdf:

            st.error(
                "Vui lòng chọn PDF"
            )

            st.stop()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(
                uploaded_pdf.getvalue()
            )

            pdf_path = tmp.name

        output_pdf, msg = run_pdf_compress(
            pdf_path,
            mode="normal"
        )

        st.success(msg)

        with open(
            output_pdf,
            "rb"
        ) as f:

            st.download_button(
                "📥 Tải PDF",
                f.read(),
                "Compressed.pdf",
                "application/pdf"
            )

with tab5:

    st.subheader(
        "🪶 Giảm dung lượng PDF"
    )

    uploaded_pdf = st.file_uploader(
        "Chọn PDF",
        type=["pdf"],
        key="reduce_pdf"
    )

    dpi = st.selectbox(
        "Mức giảm",
        [
            150,
            120,
            100
        ]
    )

    quality = st.selectbox(
        "Chất lượng ảnh",
        [
            80,
            70,
            60
        ]
    )

    if st.button(
        "🚀 Giảm dung lượng",
        key="reduce_btn_v2"
    ):

        if not uploaded_pdf:

            st.error(
                "Vui lòng chọn PDF"
            )

            st.stop()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(
                uploaded_pdf.getvalue()
            )

            pdf_path = tmp.name

        with st.spinner(
            "Đang giảm dung lượng..."
        ):

            output_pdf, msg = run_pdf_reduce_v2(
                pdf_path,
                dpi=dpi,
                jpeg_quality=quality
            )

        if output_pdf:

            st.success(msg)

            with open(
                output_pdf,
                "rb"
            ) as f:

                st.download_button(
                    "📥 Tải PDF",
                    f.read(),
                    "Reduced_V2.pdf",
                    "application/pdf"
                )

        else:

            st.error(msg)
with tab6:

    st.subheader(
        "📄 Hạ phiên bản PDF"
    )

    uploaded_pdf = st.file_uploader(
        "Chọn PDF",
        type=["pdf"],
        key="pdf_version"
    )

    compatibility = st.selectbox(
        "Phiên bản PDF đích",
        [
            "1.3",
            "1.4",
            "1.5",
            "1.6",
            "1.7"
        ]
    )

    st.info(
        "PDF 1.4 tương thích rất tốt với các phần mềm cũ."
    )

    if st.button(
        "🚀 Hạ phiên bản PDF",
        key="version_btn"
    ):

        if not uploaded_pdf:

            st.error(
                "Vui lòng chọn PDF"
            )

            st.stop()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(
                uploaded_pdf.getvalue()
            )

            pdf_path = tmp.name

        with st.spinner(
            "Đang chuyển đổi..."
        ):

            output_pdf, msg = (
                run_pdf_version_downgrade(
                    pdf_path,
                    compatibility
                )
            )

        if output_pdf:

            st.success(msg)

            with open(
                output_pdf,
                "rb"
            ) as f:

                st.download_button(
                    "📥 Tải PDF",
                    data=f.read(),
                    file_name=f"PDF_v{compatibility}.pdf",
                    mime="application/pdf"
                )

        else:

            st.error(msg)

with tab7:

    st.subheader(
        "🧹 Xoá trang trắng (Hàng loạt)"
    )

    uploaded_pdfs = st.file_uploader(
        "Chọn PDF",
        type=["pdf"],
        accept_multiple_files=True,
        key="remove_blank_batch"
    )

    threshold = st.slider(
        "Độ nhạy",
        0.90,
        1.00,
        0.98,
        0.01
    )

    if uploaded_pdfs:

        st.info(
            f"Đã chọn {len(uploaded_pdfs)} file"
        )

    if st.button(
        "🚀 Xử lý hàng loạt",
        key="remove_blank_batch_btn"
    ):

        if not uploaded_pdfs:

            st.error(
                "Vui lòng chọn file"
            )

            st.stop()

        temp_paths = []

        for file in uploaded_pdfs:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:

                tmp.write(
                    file.getvalue()
                )

                temp_paths.append(
                    tmp.name
                )

        with st.spinner(
            "Đang xử lý..."
        ):

            zip_path, report = (
                run_remove_blank_pages_batch(
                    temp_paths,
                    threshold
                )
            )

        st.success(
            "Hoàn thành"
        )

        st.text_area(
            "Kết quả",
            report,
            height=250
        )

        with open(
            zip_path,
            "rb"
        ) as f:

            st.download_button(
                "📥 Tải ZIP",
                data=f.read(),
                file_name="BlankRemoved.zip",
                mime="application/zip"
            )