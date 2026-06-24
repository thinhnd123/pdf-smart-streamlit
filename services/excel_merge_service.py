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
        )

        df_b = pd.read_excel(
            file_b,
            dtype=str
        )

        df_a = df_a.fillna("")
        df_b = df_b.fillna("")

        keep_cols = list(keys_b)

        for col in selected_columns:

            if col not in keep_cols:

                keep_cols.append(col)

        df_result = pd.merge(
            df_a,
            df_b[keep_cols],
            left_on=keys_a,
            right_on=keys_b,
            how=join_type
        )

        for col in keys_b:

            if (
                col in df_result.columns
                and col not in keys_a
            ):
                df_result.drop(
                    columns=[col],
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
            df_result,
            f"✅ Ghép thành công {len(df_result)} dòng"
        )

    except Exception as e:

        return (
            None,
            None,
            str(e)
        )