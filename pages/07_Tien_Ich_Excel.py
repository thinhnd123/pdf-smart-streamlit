import streamlit as st
import tempfile
import pandas as pd

from services.excel_merge_service import (
    run_excel_merge
)

st.title(
    "📊 TIỆN ÍCH EXCEL"
)

tab1 = st.tabs(
    [
        "VLOOKUP Siêu Tốc"
    ]
)[0]

# ==================================================
# TAB 1
# ==================================================

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

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            keys_a = st.multiselect(
                "Cột khóa File A",
                df_a.columns,
                default=[df_a.columns[0]]
            )

        with col2:

            keys_b = st.multiselect(
                "Cột khóa File B",
                df_b.columns,
                default=[df_b.columns[0]]
            )

        join_type = st.selectbox(
            "Kiểu ghép dữ liệu",
            {
                "Left Join (giữ toàn bộ File A)": "left",
                "Inner Join (chỉ giữ dữ liệu khớp)": "inner",
                "Full Join (giữ tất cả)": "outer"
            }
        )

        selected_columns = st.multiselect(
            "Các cột muốn lấy từ File B",
            [
                c
                for c in df_b.columns
                if c not in keys_b
            ]
        )

        if st.button(
            "🚀 Ghép dữ liệu"
        ):

            if len(keys_a) != len(keys_b):

                st.error(
                    "Số cột khóa A và B phải bằng nhau"
                )

                st.stop()

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

            result_file, df_preview, msg = run_excel_merge(
                path_a,
                path_b,
                keys_a,
                keys_b,
                selected_columns,
                join_type=join_type
            )

            if result_file:

                st.success(msg)

                st.markdown(
                    "### 👀 Preview kết quả"
                )

                st.dataframe(
                    df_preview.head(100),
                    use_container_width=True
                )

                st.info(
                    f"Hiển thị 100 dòng đầu tiên / Tổng {len(df_preview)} dòng"
                )

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