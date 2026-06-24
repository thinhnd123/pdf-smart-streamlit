import fitz
import tempfile
import time
import zipfile
import os


def merge_pdfs(pdf_files):

    if not pdf_files:
        return None, "Không có file PDF"

    merged_pdf = fitz.open()

    try:

        for pdf_path in pdf_files:

            doc = fitz.open(pdf_path)

            merged_pdf.insert_pdf(doc)

            doc.close()

        timestamp = int(time.time())

        output_pdf = os.path.join(
            tempfile.gettempdir(),
            f"Merged_{timestamp}.pdf"
        )

        merged_pdf.save(output_pdf)

        merged_pdf.close()

        return (
            output_pdf,
            f"✅ Ghép thành công {len(pdf_files)} file PDF"
        )

    except Exception as e:

        return None, str(e)