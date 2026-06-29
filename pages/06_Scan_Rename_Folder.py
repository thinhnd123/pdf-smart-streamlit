import streamlit as st
import tempfile
import shutil
import zipfile

from pathlib import Path

from services.scan_rename_service import run_scan_rename


st.title("📂 Đổi Tên PDF Scan Theo Excel")

st.markdown("""
OCR trang đầu PDF Scan → tìm mã GCN → đối chiếu Excel → đổi tên hàng loạt.
""")

st.markdown("---")

# ==================================================
# Upload PDF Folder
# ==================================================

uploaded_pdfs = st.file_uploader(
    label="📄 Chọn các file PDF Scan",
    type=["pdf"],
    accept_multiple_files=True
)

# ==================================================
# Upload Excel
# ==================================================

uploaded_excel = st.file_uploader(
    label="📊 Chọn file Excel đối chiếu",
    type=["xlsx", "xls"]
)

# ==================================================
# Naming Options
# ==================================================

naming_options = {
    "Mã quản lý": "ma_ql",
    "Số GCN": "so_gcn",
    "Tên thiết bị + Model": "ten_tb",
    "Tên thiết bị": "ten_khong_model",
    "Model": "model_khong_ten",
    "Mã xuất xưởng": "ma_xuat_xuong",
    "Tên + Mã xuất xưởng": "ten_ma_xuat_xuong",
    "Tên + Đặc trưng": "ten_dac_trung",
    "Tên + Model + NSX": "ten_model_nsx",
    "Tên + Model + Đặc trưng": "ten_model_dac_trung",
    "Tên + Mã quản lý": "ten_ma_ql",
    "Tên trước dấu / + Mã quản lý": "ten_truoc_slash_ma_ql",
    "Tên sau dấu / + Mã quản lý": "ten_sau_slash_ma_ql",
}

selected_label = st.selectbox(
    "📝 Kiểu đặt tên",
    options=list(naming_options.keys())
)

naming_type = naming_options[selected_label]

st.markdown("---")

# ==================================================
# Run
# ==================================================

if st.button(
    "🚀 Bắt đầu OCR & Đổi Tên",
    use_container_width=True
):

    if not uploaded_pdfs:
        st.error("⚠️ Vui lòng chọn ít nhất 1 file PDF.")
        st.stop()

    if uploaded_excel is None:
        st.error("⚠️ Vui lòng chọn file Excel.")
        st.stop()

    try:

        # ==========================================
        # Folder tạm chứa PDF
        # ==========================================

        temp_folder = tempfile.mkdtemp()

        for pdf in uploaded_pdfs:

            save_path = Path(temp_folder) / pdf.name

            with open(save_path, "wb") as f:
                f.write(pdf.getvalue())

        # ==========================================
        # Save Excel Temp
        # ==========================================

        excel_suffix = Path(uploaded_excel.name).suffix

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=excel_suffix
        ) as tmp_excel:

            tmp_excel.write(uploaded_excel.getvalue())

            excel_path = tmp_excel.name

        # ==========================================
        # Execute OCR
        # ==========================================

        with st.spinner(
            f"⏳ Đang OCR {len(uploaded_pdfs)} file PDF..."
        ):

            output_folder, msg = run_scan_rename(
                folder_path=temp_folder,
                excel_path=excel_path,
                naming_type=naming_type
            )

        st.success(msg)

        # ==========================================
        # Zip output folder
        # ==========================================

        zip_path = Path(temp_folder) / "KetQua_DoiTen.zip"

        with zipfile.ZipFile(
            zip_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for file_path in Path(output_folder).rglob("*"):

                if file_path.is_file():

                    zipf.write(
                        file_path,
                        arcname=file_path.relative_to(output_folder)
                    )

        # ==========================================
        # Download
        # ==========================================

        with open(zip_path, "rb") as f:

            st.download_button(
                label="📥 Tải ZIP kết quả",
                data=f.read(),
                file_name="KetQua_DoiTen.zip",
                mime="application/zip",
                use_container_width=True
            )

    except Exception as e:

        st.exception(e)

    finally:

        try:
            shutil.rmtree(temp_folder)
        except:
            pass