import pandas as pd
import tempfile
import os


def run_consistency_check(
    excel_path,
    key_column,
    value_column
):

    try:

        df = pd.read_excel(
            excel_path,
            dtype=str
        ).fillna("")

        summary = (
            df.groupby(key_column)[value_column]
            .nunique()
            .reset_index()
        )

        summary = summary.rename(
            columns={
                value_column:
                "Unique_Count"
            }
        )

        issue_df = summary[
            summary["Unique_Count"] > 1
        ]

        if len(issue_df) == 0:

            return (
                None,
                None,
                None,
                "✅ Không phát hiện bất thường"
            )

        bad_keys = set(
            issue_df[key_column]
        )

        detail_df = df[
            df[key_column]
            .isin(bad_keys)
        ]

        output_file = os.path.join(
            tempfile.gettempdir(),
            "Consistency_Check.xlsx"
        )

        with pd.ExcelWriter(
            output_file,
            engine="openpyxl"
        ) as writer:

            issue_df.to_excel(
                writer,
                sheet_name="Summary",
                index=False
            )

            detail_df.to_excel(
                writer,
                sheet_name="Details",
                index=False
            )

        return (
            output_file,
            issue_df,
            detail_df,
            f"⚠️ Phát hiện {len(issue_df)} giá trị bất thường"
        )

    except Exception as e:

        return (
            None,
            None,
            None,
            str(e)
        )