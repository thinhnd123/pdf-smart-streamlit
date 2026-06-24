import streamlit as st
import tempfile
import os

from services.pdf_merge_by_name_service import run_merge_by_name

from services.pdf_merge_by_excel_service import run_merge_by_excel

import pandas as pd

st.title(
    "📂 TỰ ĐỘNG HÓA HỒ SƠ"
)

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Ghép theo tên file",
        "Ghép theo Excel",
        "Đối chiếu PDF-Excel",
        "Gom hồ sơ trùng tên",
        "Tạo hồ sơ hàng loạt"
    ]
)


with tab1:

    st.subheader(
        "📎 Ghép hồ sơ theo tên file"
    )

    uploaded_a = st.file_uploader(
        "Folder A",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_a"
    )

    uploaded_b = st.file_uploader(
        "Folder B",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_b"
    )

    if uploaded_a:

        st.success(
            f"Folder A: {len(uploaded_a)} file"
        )

    if uploaded_b:

        st.success(
            f"Folder B: {len(uploaded_b)} file"
        )

    if st.button(
        "🚀 Ghép hồ sơ",
        key="merge_by_name"
    ):

        if not uploaded_a:

            st.error(
                "Chưa chọn Folder A"
            )

            st.stop()

        if not uploaded_b:

            st.error(
                "Chưa chọn Folder B"
            )

            st.stop()

        temp_a = []
        temp_b = []

        # ==================
        # Folder A
        # ==================

        for file in uploaded_a:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:

                tmp.write(file.getvalue())

                temp_a.append({
                    "name": file.name,
                    "path": tmp.name
                })

        # ==================
        # Folder B
        # ==================

        for file in uploaded_a:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as tmp:

                tmp.write(file.getvalue())

                temp_a.append({
                    "name": file.name,
                    "path": tmp.name
                })

        with st.spinner(
            "Đang ghép hồ sơ..."
        ):

            zip_path, msg = run_merge_by_name(
                temp_a,
                temp_b
            )

        if zip_path:

            st.success(msg)

            with open(
                zip_path,
                "rb"
            ) as f:

                st.download_button(
                    "📥 Tải ZIP",
                    data=f.read(),
                    file_name="Merged_By_Name.zip",
                    mime="application/zip"
                )

        else:

            st.error(msg)
            
with tab2:

    st.subheader(
        "📊 Ghép hồ sơ theo Excel"
    )

    excel_file = st.file_uploader(
        "File Excel Mapping",
        type=["xlsx"],
        key="excel_mapping"
    )

    uploaded_a = st.file_uploader(
        "Folder PDF A",
        type=["pdf"],
        accept_multiple_files=True,
        key="excel_pdf_a"
    )

    uploaded_b = st.file_uploader(
        "Folder PDF B",
        type=["pdf"],
        accept_multiple_files=True,
        key="excel_pdf_b"
    )

    if excel_file:

        df_preview = pd.read_excel(
            excel_file,
            header=None
        )

        st.markdown(
            "### Preview Excel"
        )

        st.dataframe(
            df_preview.head(10)
        )

        col1, col2 = st.columns(2)

        with col1:

            col_a = st.number_input(
                "Cột tên PDF A",
                min_value=0,
                value=0
            )

        with col2:

            col_b = st.number_input(
                "Cột tên PDF B",
                min_value=0,
                value=1
            )

        if st.button(
            "🚀 Ghép theo Excel",
            key="merge_excel_btn"
        ):

            if not uploaded_a:

                st.error(
                    "Chưa chọn PDF A"
                )

                st.stop()

            if not uploaded_b:

                st.error(
                    "Chưa chọn PDF B"
                )

                st.stop()

            temp_excel = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            )

            temp_excel.write(
                excel_file.getvalue()
            )

            temp_excel.close()

            temp_a = []

            for file in uploaded_a:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp:

                    tmp.write(
                        file.getvalue()
                    )

                    temp_a.append({
                        "name": file.name,
                        "path": tmp.name
                    })

            temp_b = []

            for file in uploaded_b:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp:

                    tmp.write(
                        file.getvalue()
                    )

                    temp_b.append({
                        "name": file.name,
                        "path": tmp.name
                    })

            with st.spinner(
                "Đang ghép..."
            ):

                zip_path, msg = run_merge_by_excel(
                    temp_excel.name,
                    temp_a,
                    temp_b,
                    col_a,
                    col_b
                )

            if zip_path:

                st.success(msg)

                with open(
                    zip_path,
                    "rb"
                ) as f:

                    st.download_button(
                        "📥 Tải ZIP",
                        data=f.read(),
                        file_name="Merged_By_Excel.zip",
                        mime="application/zip"
                    )

            else:

                st.error(msg)            