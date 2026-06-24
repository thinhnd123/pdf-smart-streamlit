import fitz
import tempfile
import zipfile
import time
import os


def split_pdf_by_ranges(pdf_path, ranges_text):

    doc = fitz.open(pdf_path)

    timestamp = int(time.time())

    output_dir = os.path.join(
        tempfile.gettempdir(),
        f"split_range_{timestamp}"
    )

    os.makedirs(output_dir, exist_ok=True)

    zip_path = os.path.join(
        tempfile.gettempdir(),
        f"Split_Range_{timestamp}.zip"
    )

    parts = []

    for idx, line in enumerate(
        ranges_text.strip().splitlines(),
        start=1
    ):

        line = line.strip()

        if not line:
            continue

        start_page, end_page = map(
            int,
            line.split("-")
        )

        new_doc = fitz.open()

        new_doc.insert_pdf(
            doc,
            from_page=start_page - 1,
            to_page=end_page - 1
        )

        output_pdf = os.path.join(
            output_dir,
            f"Part_{idx}.pdf"
        )

        new_doc.save(output_pdf)

        new_doc.close()

        parts.append(output_pdf)

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for pdf_file in parts:

            zipf.write(
                pdf_file,
                os.path.basename(pdf_file)
            )

    doc.close()

    return (
        zip_path,
        f"✅ Đã tạo {len(parts)} file PDF"
    )