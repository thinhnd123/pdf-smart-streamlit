import os
import tempfile

import fitz
import pytesseract

from PIL import Image

TESSERACT_PATH = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

if os.path.exists(TESSERACT_PATH):

    pytesseract.pytesseract.tesseract_cmd = (
        TESSERACT_PATH
    )

def run_image_to_pdf_ocr(
    image_paths
):

    try:

        output_pdf = fitz.open()

        for img_path in image_paths:

            pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                img_path,
                extension="pdf",
                lang="vie+eng"
            )

            temp_pdf = fitz.open(
                "pdf",
                pdf_bytes
            )

            output_pdf.insert_pdf(
                temp_pdf
            )

            temp_pdf.close()

        final_path = os.path.join(
            tempfile.gettempdir(),
            "Images_OCR.pdf"
        )

        output_pdf.save(
            final_path
        )

        output_pdf.close()

        return (
            final_path,
            f"✅ OCR thành công {len(image_paths)} ảnh"
        )

    except Exception as e:

        return None, str(e)