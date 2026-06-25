import streamlit as st
import tempfile
import pandas as pd

from services.excel_merge_service import (
    run_excel_merge
)

from services.excel_cleaner_service import (
    run_excel_cleaner
)

from services.excel_compare_service import (
    run_excel_compare
)

from services.excel_smart_search_service import (
    run_smart_search
)

st.title(
    "📊 TIỆN ÍCH EXCEL"
)

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "VLOOKUP Siêu Tốc",
        "Data Cleaner",
        "So Sánh Excel",
        "🔎 Smart Search Excel"
    ]
)

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
                    "Số lượng khóa phải giống nhau"
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

            (
                result_file,
                df_preview,
                df_not_match,
                summary,
                msg
            ) = run_excel_merge(
                path_a,
                path_b,
                keys_a,
                keys_b,
                selected_columns,
                join_type
            )

            if result_file:

                st.success(msg)

                # =====================
                # KPI
                # =====================

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "Tổng dòng",
                    summary["total"]
                )

                c2.metric(
                    "Khớp",
                    summary["match"]
                )

                c3.metric(
                    "Không khớp",
                    summary["not_match"]
                )

                c4.metric(
                    "Tỷ lệ",
                    f"{summary['percent']}%"
                )

                st.markdown("---")

                st.subheader(
                    "👀 Preview kết quả"
                )

                st.dataframe(
                    df_preview.head(100),
                    use_container_width=True
                )

                st.info(
                    f"Hiển thị 100 dòng đầu tiên / {summary['total']} dòng"
                )

                # =====================
                # NOT MATCH
                # =====================

                if len(df_not_match):

                    st.warning(
                        f"Có {len(df_not_match)} dòng không khớp"
                    )

                    st.dataframe(
                        df_not_match.head(100),
                        use_container_width=True
                    )

                else:

                    st.success(
                        "100% dữ liệu khớp"
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
                
                
# ==================================================
# TAB 2
# ==================================================

with tab2:

    st.subheader(
        "🧹 Data Cleaner & Validator"
    )

    excel_file = st.file_uploader(
        "Chọn Excel",
        type=["xlsx", "xls"],
        key="clean_excel"
    )

    if excel_file:

        df_preview = pd.read_excel(
            excel_file,
            nrows=5
        )

        cols = list(
            df_preview.columns
        )

        st.dataframe(
            df_preview
        )

        phone_col = st.selectbox(
            "Cột SĐT",
            [""] + cols
        )

        email_col = st.selectbox(
            "Cột Email",
            [""] + cols
        )

        name_col = st.selectbox(
            "Cột Họ tên",
            [""] + cols
        )

        gcn_col = st.selectbox(
            "Cột GCN",
            [""] + cols
        )

        maql_col = st.selectbox(
            "Cột Mã quản lý",
            [""] + cols
        )

        serial_col = st.selectbox(
            "Cột Serial",
            [""] + cols
        )

        model_col = st.selectbox(
            "Cột Model",
            [""] + cols
        )

        if st.button(
            "🚀 Làm sạch dữ liệu"
        ):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            ) as tmp:

                tmp.write(
                    excel_file.getvalue()
                )

                path = tmp.name

            (
                output_file,
                preview,
                stats,
                msg
            ) = run_excel_cleaner(
                path,
                phone_col or None,
                email_col or None,
                name_col or None,
                gcn_col or None,
                maql_col or None,
                serial_col or None,
                model_col or None
            )

            if output_file:

                st.success(msg)

                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    "SĐT sửa",
                    stats["phones"]
                )

                c2.metric(
                    "Tên sửa",
                    stats["names"]
                )

                c3.metric(
                    "Email lỗi",
                    stats["email_errors"]
                )

                c4.metric(
                    "Trùng SĐT",
                    stats["duplicates"]
                )

                st.markdown("---")

                st.write(
                    "### Preview"
                )

                st.dataframe(
                    preview,
                    use_container_width=True
                )

                st.markdown("---")

                st.info(
                    f"GCN trùng: {stats['gcn_duplicates']} | "
                    f"Mã QL trùng: {stats['maql_duplicates']} | "
                    f"Serial trùng: {stats['serial_duplicates']} | "
                    f"Model trùng: {stats['model_duplicates']}"
                )

                with open(
                    output_file,
                    "rb"
                ) as f:

                    st.download_button(
                        "📥 Tải Excel sạch",
                        data=f.read(),
                        file_name="Excel_Cleaned.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            else:

                st.error(msg)
                
                
# ==================================================
# TAB 3
# ==================================================

with tab3:

    st.subheader(
        "🔍 So sánh 2 file Excel"
    )

    file_a = st.file_uploader(
        "File A",
        type=["xlsx", "xls"],
        key="compare_a"
    )

    file_b = st.file_uploader(
        "File B",
        type=["xlsx", "xls"],
        key="compare_b"
    )

    if file_a and file_b:

        preview_a = pd.read_excel(
            file_a,
            nrows=5
        )

        preview_b = pd.read_excel(
            file_b,
            nrows=5
        )

        col1, col2 = st.columns(2)

        with col1:

            keys_a = st.multiselect(
                "Cột khóa File A",
                preview_a.columns,
                default=[preview_a.columns[0]]
            )

        with col2:

            keys_b = st.multiselect(
                "Cột khóa File B",
                preview_b.columns,
                default=[preview_b.columns[0]]
            )

        if st.button(
            "🚀 So sánh dữ liệu"
        ):

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            ) as tmp1:

                tmp1.write(
                    file_a.getvalue()
                )

                path_a = tmp1.name

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            ) as tmp2:

                tmp2.write(
                    file_b.getvalue()
                )

                path_b = tmp2.name

            (
                output_file,
                df_match,
                df_only_a,
                df_only_b,
                df_detail,
                summary,
                msg
            ) = run_excel_compare(
                path_a,
                path_b,
                keys_a,
                keys_b
            )

            if output_file:

                st.success(msg)

                c1, c2, c3, c4, c5 = st.columns(5)

                c1.metric(
                    "Khớp",
                    summary["match"]
                )

                c2.metric(
                    "Chỉ File A",
                    summary["only_a"]
                )

                c3.metric(
                    "Chỉ File B",
                    summary["only_b"]
                )

                c4.metric(
                    "Ô dữ liệu thay đổi",
                    summary["differences"]
                )

                c5.metric(
                    "Hồ sơ thay đổi",
                    summary["changed_keys"]
                )

                st.markdown("---")

                st.subheader(
                    "✅ Dữ liệu khớp"
                )

                st.dataframe(
                    df_match.head(100)
                )

                st.subheader(
                    "⚠️ Chỉ có trong File A"
                )

                st.dataframe(
                    df_only_a.head(100)
                )

                st.subheader(
                    "⚠️ Chỉ có trong File B"
                )

                st.dataframe(
                    df_only_b.head(100)
                )

                with open(
                    output_file,
                    "rb"
                ) as f:
                    
                    st.subheader(
                        "🔍 Sai khác chi tiết"
                    )

                    if len(df_detail):

                        st.info(
                            f"Phát hiện {summary['changed_keys']} Key bị thay đổi dữ liệu"
                        )

                        audit_df = (

                            df_detail

                            .groupby("Column")

                            .size()

                            .reset_index(
                                name="Số lần thay đổi"
                            )

                            .sort_values(
                                "Số lần thay đổi",
                                ascending=False
                            )
                        )

                        st.subheader(
                            "📊 Audit Report"
                        )

                        st.dataframe(
                            audit_df,
                            use_container_width=True
                        )

                    st.download_button(
                        "📥 Tải Excel kết quả",
                        data=f.read(),
                        file_name="Excel_Compare.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            else:

                st.error(msg) 

with tab4:

    st.subheader(
        "🔎 Smart Search Excel"
    )

    uploaded_file = st.file_uploader(
        "Excel nguồn",
        type=["xlsx", "xls"],
        key="search_excel"
    )

    if uploaded_file:

        preview_df = pd.read_excel(
            uploaded_file,
            nrows=5
        )

        columns = list(
            preview_df.columns
        )

        search_columns = st.multiselect(
            "Các cột tham gia tìm kiếm",
            columns,
            default=columns
        )

        search_text = st.text_input(
            "🔎 Từ khóa"
        )

        if st.button(
            "🚀 Tìm kiếm",
            key="search_btn"
        ):

            if not search_columns:

                st.error(
                    "Chọn ít nhất 1 cột"
                )

                st.stop()

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".xlsx"
            ) as tmp:

                tmp.write(
                    uploaded_file.getvalue()
                )

                excel_path = tmp.name

            (
                output_file,
                result_df,
                msg
            ) = run_smart_search(
                excel_path,
                search_text,
                search_columns
            )

            if output_file:

                st.success(msg)

                st.metric(
                    "Kết quả",
                    len(result_df)
                )

                st.dataframe(
                    result_df,
                    use_container_width=True
                )

                with open(
                    output_file,
                    "rb"
                ) as f:

                    st.download_button(
                        "📥 Tải kết quả",
                        data=f.read(),
                        file_name="Search_Result.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            else:

                st.error(msg)