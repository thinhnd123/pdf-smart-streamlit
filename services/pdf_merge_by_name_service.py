import os
import tempfile
import zipfile

from pypdf import PdfReader
from pypdf import PdfWriter


def run_merge_by_name(
    files_a,
    files_b
):
    try:

        output_dir = os.path.join(
            tempfile.gettempdir(),
            "merge_by_name"
        )

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        # Xóa file cũ
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

        dict_b = {}

        for item in files_b:

            dict_b[
                item["name"].lower()
            ] = item["path"]

        merged_count = 0
        skipped_count = 0

        for item_a in files_a:

            file_name = item_a["name"]

            path_a = item_a["path"]

            key = file_name.lower()

            if key not in dict_b:

                skipped_count += 1
                continue

            path_b = dict_b[key]

            writer = PdfWriter()

            reader_a = PdfReader(path_a)

            for page in reader_a.pages:

                writer.add_page(page)

            reader_b = PdfReader(path_b)

            for page in reader_b.pages:

                writer.add_page(page)

            output_pdf = os.path.join(
                output_dir,
                file_name
            )

            with open(
                output_pdf,
                "wb"
            ) as f:

                writer.write(f)

            merged_count += 1

        zip_path = os.path.join(
            tempfile.gettempdir(),
            "Merged_By_Name.zip"
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
            f"✅ Ghép thành công {merged_count} file | Bỏ qua {skipped_count} file"
        )

    except Exception as e:

        return (
            None,
            str(e)
        )