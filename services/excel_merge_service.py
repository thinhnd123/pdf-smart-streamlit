import pandas as pd
import tempfile
import os


def normalize_key(series):

    return (
        series.astype(str)
        .str.strip()
        .str.upper()
    )


def run_excel_merge(
    file_a,
    file_b,
    keys_a,
    keys_b,
    selected_columns,
    join_type="left",
    force_merge=False
):

    try:

        df_a = pd.read_excel(
            file_a,
            dtype=str
        ).fillna("")

        df_b = pd.read_excel(
            file_b,
            dtype=str
        ).fillna("")

        # =========================
        # CHUẨN HÓA KEY
        # =========================

        for col in keys_a:

            df_a[col] = normalize_key(
                df_a[col]
            )

        for col in keys_b:

            df_b[col] = normalize_key(
                df_b[col]
            )

        # =========================
        # DUPLICATE A
        # =========================

        duplicate_a = df_a[
            df_a.duplicated(
                subset=keys_a,
                keep=False
            )
        ].copy()

        duplicate_b = df_b[
            df_b.duplicated(
                subset=keys_b,
                keep=False
            )
        ].copy()

        duplicate_a_count = (
            duplicate_a[keys_a]
            .drop_duplicates()
            .shape[0]
        )

        duplicate_b_count = (
            duplicate_b[keys_b]
            .drop_duplicates()
            .shape[0]
        )

        # =========================
        # BUSINESS CHECK V3
        # =========================

        business_error_summary = []
        business_error_detail = []

        if len(selected_columns):

            for value_col in selected_columns:

                check_df = (
                    df_b
                    .groupby(keys_b)[value_col]
                    .nunique()
                    .reset_index()
                )

                bad_keys = check_df[
                    check_df[value_col] > 1
                ]

                if len(bad_keys):

                    for _, row in bad_keys.iterrows():

                        key_filter = pd.Series(
                            True,
                            index=df_b.index
                        )

                        for k in keys_b:

                            key_filter &= (
                                df_b[k] == row[k]
                            )

                        detail_rows = (
                            df_b[
                                key_filter
                            ]
                            [
                                keys_b +
                                [value_col]
                            ]
                            .drop_duplicates()
                        )

                        key_text = " | ".join(
                            [
                                str(row[k])
                                for k in keys_b
                            ]
                        )

                        business_error_summary.append(
                            {
                                "Key": key_text,
                                "Column": value_col,
                                "Different Values":
                                row[value_col]
                            }
                        )

                        detail_rows = (
                            detail_rows.copy()
                        )

                        detail_rows[
                            "Error Column"
                        ] = value_col

                        business_error_detail.append(
                            detail_rows
                        )

        business_error_summary = pd.DataFrame(
            business_error_summary
        )

        business_error_detail = pd.concat(
            business_error_detail,
            ignore_index=True
        ) if business_error_detail else pd.DataFrame()

        # =========================
        # STOP IF ERROR
        # =========================

        if (
            len(business_error_summary)
            and not force_merge
        ):

            return (
                None,
                None,
                None,
                {
                    "total": 0,
                    "match": 0,
                    "not_match": 0,
                    "percent": 0,
                    "duplicate_a": duplicate_a_count,
                    "duplicate_b": duplicate_b_count,
                    "business_error": len(
                        business_error_summary
                    )
                },
                business_error_summary,
                business_error_detail,
                "⚠️ Phát hiện dữ liệu bất thường"
            )

        # =========================
        # GỘP DUPLICATE B
        # =========================

        df_b = df_b.drop_duplicates(
            subset=keys_b,
            keep="first"
        )

        keep_cols = list(keys_b)

        for col in selected_columns:

            if col not in keep_cols:

                keep_cols.append(col)

        # =========================
        # MERGE
        # =========================

        df_result = pd.merge(
            df_a,
            df_b[keep_cols],
            left_on=keys_a,
            right_on=keys_b,
            how=join_type,
            indicator=True
        )

        # =========================
        # XÓA KEY DƯ
        # =========================

        for col in keys_b:

            if (
                col in df_result.columns
                and col not in keys_a
            ):

                df_result.drop(
                    columns=[col],
                    inplace=True
                )

        # =========================
        # MATCH
        # =========================

        df_match = df_result[
            df_result["_merge"] == "both"
        ].copy()

        df_not_match = df_result[
            df_result["_merge"] != "both"
        ].copy()

        total_rows = len(df_result)

        match_rows = len(df_match)

        not_match_rows = len(df_not_match)

        percent = (
            round(
                match_rows
                * 100
                / total_rows,
                2
            )
            if total_rows
            else 0
        )

        # =========================
        # EXPORT
        # =========================

        output_file = os.path.join(
            tempfile.gettempdir(),
            "Excel_Merge_Result.xlsx"
        )

        with pd.ExcelWriter(
            output_file,
            engine="openpyxl"
        ) as writer:

            df_result.to_excel(
                writer,
                sheet_name="Merged",
                index=False
            )

            df_match.to_excel(
                writer,
                sheet_name="Match",
                index=False
            )

            df_not_match.to_excel(
                writer,
                sheet_name="NotMatch",
                index=False
            )

            duplicate_a.to_excel(
                writer,
                sheet_name="Duplicate_A",
                index=False
            )

            duplicate_b.to_excel(
                writer,
                sheet_name="Duplicate_B",
                index=False
            )

        summary = {

            "total": total_rows,

            "match": match_rows,

            "not_match": not_match_rows,

            "percent": percent,

            "duplicate_a": duplicate_a_count,

            "duplicate_b": duplicate_b_count,

            "business_error": 0
        }

        return (
            output_file,
            df_result,
            df_not_match,
            summary,
            business_error_summary,
            business_error_detail,
            "✅ Ghép dữ liệu thành công"
        )

    except Exception as e:

        return (
            None,
            None,
            None,
            None,
            str(e)
        )