import os
import tempfile
import zipfile
import pandas as pd

from pypdf import PdfReader
from pypdf import PdfWriter


def run_merge_by_excel(
    files_a,
    files_b,
    excel_path
):

    try:

        output_dir = os.path.join(
            tempfile.gettempdir(),
            "merge_by_excel"
        )

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        for f in os.listdir(output_dir):

            try:
                os.remove(
                    os.path.join(
                        output_dir,
                        f
                    )
                )
            except:
                pass

        dict_a = {}

        for item in files_a:

            dict_a[
                item["name"]
            ] = item["path"]

        dict_b = {}

        for item in files_b:

            dict_b[
                item["name"]
            ] = item["path"]

        df = pd.read_excel(
            excel_path,
            dtype=str
        ).fillna("")

        report_rows = []

        success_count = 0

        for _, row in df.iterrows():

            file_a = str(
                row.iloc[0]
            ).strip()

            file_b = str(
                row.iloc[1]
            ).strip()

            if (
                file_a not in dict_a
            ):

                report_rows.append(
                    [
                        file_a,
                        file_b,
                        "Thiếu File A"
                    ]
                )

                continue

            if (
                file_b not in dict_b
            ):

                report_rows.append(
                    [
                        file_a,
                        file_b,
                        "Thiếu File B"
                    ]
                )

                continue

            writer = PdfWriter()

            reader_a = PdfReader(
                dict_a[file_a]
            )

            for page in reader_a.pages:

                writer.add_page(page)

            reader_b = PdfReader(
                dict_b[file_b]
            )

            for page in reader_b.pages:

                writer.add_page(page)

            output_pdf = os.path.join(
                output_dir,
                file_a
            )

            with open(
                output_pdf,
                "wb"
            ) as f:

                writer.write(f)

            success_count += 1

            report_rows.append(
                [
                    file_a,
                    file_b,
                    "OK"
                ]
            )

        report_path = os.path.join(
            output_dir,
            "Merge_Report.xlsx"
        )

        pd.DataFrame(
            report_rows,
            columns=[
                "File A",
                "File B",
                "Ket Qua"
            ]
        ).to_excel(
            report_path,
            index=False
        )

        zip_path = os.path.join(
            tempfile.gettempdir(),
            "Merge_By_Excel.zip"
        )

        with zipfile.ZipFile(
            zip_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for file in os.listdir(
                output_dir
            ):

                zipf.write(
                    os.path.join(
                        output_dir,
                        file
                    ),
                    file
                )

        return (
            zip_path,
            f"✅ Ghép thành công {success_count} hồ sơ"
        )

    except Exception as e:

        return (
            None,
            str(e)
        )