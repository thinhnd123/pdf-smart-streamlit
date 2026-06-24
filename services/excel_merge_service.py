import pandas as pd
import tempfile
import os


def run_excel_merge(
    file_a,
    file_b,
    keys_a,
    keys_b,
    selected_columns,
    join_type="left"
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

        keep_cols = list(keys_b)

        for col in selected_columns:

            if col not in keep_cols:

                keep_cols.append(col)

        df_result = pd.merge(
            df_a,
            df_b[keep_cols],
            left_on=keys_a,
            right_on=keys_b,
            how=join_type,
            indicator=True
        )

        # =========================
        # Xóa khóa dư
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
        # Match / Not Match
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
                match_rows * 100 / total_rows,
                2
            )
            if total_rows
            else 0
        )

        # =========================
        # Xuất Excel
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

        summary = {
            "total": total_rows,
            "match": match_rows,
            "not_match": not_match_rows,
            "percent": percent
        }

        return (
            output_file,
            df_result,
            df_not_match,
            summary,
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