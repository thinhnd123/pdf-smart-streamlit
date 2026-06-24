import os
import tempfile

import pandas as pd


def normalize(value):

    if pd.isna(value):
        return ""

    return str(value).strip().upper()


def run_compare_pdf_excel(
    pdf_files,
    excel_path,
    compare_type
):

    try:

        # ==========================
        # Mapping cột Excel
        # ==========================

        COLUMN_MAP = {

            "GCN": 25,
            "Số seri": 26,
            "Mã quản lý": 27,
            "Tên thiết bị": 5,
            "Model": 6

        }

        compare_col = COLUMN_MAP[
            compare_type
        ]

        # ==========================
        # Đọc Excel
        # ==========================

        df = pd.read_excel(
            excel_path,
            header=None,
            dtype=str
        )

        excel_values = set()

        for value in df[
            compare_col
        ].tolist():

            value = normalize(value)

            if value:

                excel_values.add(
                    value
                )

        # ==========================
        # PDF values
        # ==========================

        pdf_values = []

        for file in pdf_files:

            name = os.path.splitext(
                file.name
            )[0]

            pdf_values.append(
                normalize(name)
            )

        # ==========================
        # Thống kê
        # ==========================

        matched = []

        missing_excel = []

        duplicates = []

        seen = set()

        for value in pdf_values:

            if value in seen:

                duplicates.append(
                    value
                )

            seen.add(value)

            if value in excel_values:

                matched.append(
                    value
                )

            else:

                missing_excel.append(
                    value
                )

        missing_pdf = list(
            excel_values -
            set(pdf_values)
        )

        # ==========================
        # Export Excel
        # ==========================

        report_rows = []

        for x in matched:

            report_rows.append(
                ["OK", x]
            )

        for x in missing_pdf:

            report_rows.append(
                ["Thiếu PDF", x]
            )

        for x in missing_excel:

            report_rows.append(
                ["Thiếu Excel", x]
            )

        for x in duplicates:

            report_rows.append(
                ["Trùng PDF", x]
            )

        report_df = pd.DataFrame(
            report_rows,
            columns=[
                "Trạng thái",
                "Giá trị"
            ]
        )

        report_path = os.path.join(
            tempfile.gettempdir(),
            "PDF_Excel_Report.xlsx"
        )

        report_df.to_excel(
            report_path,
            index=False
        )

        result = {

            "matched": matched,
            "missing_pdf": missing_pdf,
            "missing_excel": missing_excel,
            "duplicates": duplicates,
            "report": report_path

        }

        return result, "OK"

    except Exception as e:

        return None, str(e)