import fitz
import os
import tempfile
from PIL import Image
import io


def run_pdf_reduce_v2(
    pdf_path,
    dpi=120,
    jpeg_quality=70
):

    try:

        doc = fitz.open(pdf_path)

        new_pdf = fitz.open()

        for page_num in range(len(doc)):

            page = doc[page_num]

            pix = page.get_pixmap(
                matrix=fitz.Matrix(
                    dpi / 72,
                    dpi / 72
                ),
                alpha=False
            )

            img = Image.open(
                io.BytesIO(
                    pix.tobytes("jpg")
                )
            )

            temp_img = io.BytesIO()

            img.save(
                temp_img,
                format="JPEG",
                quality=jpeg_quality,
                optimize=True
            )

            rect = fitz.Rect(
                0,
                0,
                img.width,
                img.height
            )

            pdf_page = new_pdf.new_page(
                width=img.width,
                height=img.height
            )

            pdf_page.insert_image(
                rect,
                stream=temp_img.getvalue()
            )

        output_pdf = os.path.join(
            tempfile.gettempdir(),
            "Reduced_V2.pdf"
        )

        new_pdf.save(
            output_pdf,
            garbage=4,
            deflate=True
        )

        doc.close()
        new_pdf.close()

        old_size = round(
            os.path.getsize(pdf_path)
            / 1024 / 1024,
            2
        )

        new_size = round(
            os.path.getsize(output_pdf)
            / 1024 / 1024,
            2
        )

        return (
            output_pdf,
            f"✅ {old_size} MB → {new_size} MB"
        )

    except Exception as e:

        return None, str(e)