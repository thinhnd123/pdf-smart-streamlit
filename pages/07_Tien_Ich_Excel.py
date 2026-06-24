import streamlit as st
import tempfile

from services.excel_merge_service import (
    run_excel_merge
)

import pandas as pd

st.title(
    "📊 TIỆN ÍCH EXCEL"
)

tab1 = st.tabs(
    [
        "VLOOKUP Siêu Tốc"
    ]
)[0]

# =====================================
# TAB 1
# =====================================

with tab1:

    st.subheader(
        "⚡ VLOOKUP / Merge Siêu Tốc"
    )

    file_a = st.file_uploader(
        "File chính",
        type=["xlsx", "xls"],
        key="file_a"
    )

    file_b = st.file_uploader(
        "File tham chiếu",
        type=["xlsx", "xls"],
        key="file_b"
    )

    if file_a and file_b:

        df_a = pd.read_excel(
            file_a,
            nrows=5
        )

        df_b = pd.read_excel(
            file_b,
            nrows=5
        )

        col1, col2 = st.columns(2)

        with col1:

            key_a = st.selectbox(
                "Cột khóa File A",
                df_a.columns
            )

        with col2:

            key_b = st.selectbox(
                "Cột khóa File B",
                df_b.columns
            )

        selected_columns = st.multiselect(
            "Các cột muốn lấy từ File B",
            [
                c
                for c in df_b.columns
                if c != key_b
            ]
        )

        if st.button(
            "🚀 Ghép dữ liệu"
        ):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            ) as tmp_a:

                tmp_a.write(
                    file_a.getvalue()
                )

                path_a = tmp_a.name

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            ) as tmp_b:

                tmp_b.write(
                    file_b.getvalue()
                )

                path_b = tmp_b.name

            result_file, msg = run_excel_merge(
                path_a,
                path_b,
                key_a,
                key_b,
                selected_columns
            )

            if result_file:

                st.success(msg)

                with open(
                    result_file,
                    "rb"
                ) as f:

                    st.download_button(
                        "📥 Tải Excel kết quả",
                        data=f.read(),
                        file_name="Merged.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            else:

                st.error(msg)