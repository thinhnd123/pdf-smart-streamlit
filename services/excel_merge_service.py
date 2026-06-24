import pandas as pd
import tempfile
import os


def run_excel_merge(
    file_a,
    file_b,
    key_a,
    key_b,
    selected_columns
):

    try:

        df_a = pd.read_excel(
            file_a,
            dtype=str
        )

        df_b = pd.read_excel(
            file_b,
            dtype=str
        )

        keep_cols = [key_b]

        for col in selected_columns:

            if col not in keep_cols:

                keep_cols.append(col)

        df_result = pd.merge(
            df_a,
            df_b[keep_cols],
            left_on=key_a,
            right_on=key_b,
            how="left"
        )

        if key_b in df_result.columns:

            df_result.drop(
                columns=[key_b],
                inplace=True
            )

        output_file = os.path.join(
            tempfile.gettempdir(),
            "Excel_Merge_Result.xlsx"
        )

        df_result.to_excel(
            output_file,
            index=False
        )

        return (
            output_file,
            f"✅ Ghép thành công {len(df_result)} dòng"
        )

    except Exception as e:

        return (
            None,
            str(e)
        )