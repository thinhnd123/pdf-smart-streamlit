import pandas as pd
import tempfile
import os


def run_smart_search(
    excel_path,
    search_text,
    search_columns
):

    try:

        df = pd.read_excel(
            excel_path,
            dtype=str
        ).fillna("")

        if not search_text:

            return (
                None,
                None,
                "Vui lòng nhập từ khóa"
            )

        keywords = [
            x.strip().lower()
            for x in search_text.split()
            if x.strip()
        ]

        search_series = (
            df[search_columns]
            .astype(str)
            .agg(
                " ".join,
                axis=1
            )
            .str.lower()
        )

        mask = True

        for kw in keywords:

            mask = mask & search_series.str.contains(
                kw,
                na=False
            )

        result_df = df[mask]

        output_file = os.path.join(
            tempfile.gettempdir(),
            "Search_Result.xlsx"
        )

        result_df.to_excel(
            output_file,
            index=False
        )

        return (
            output_file,
            result_df,
            f"✅ Tìm thấy {len(result_df)} dòng"
        )

    except Exception as e:

        return (
            None,
            None,
            str(e)
        )