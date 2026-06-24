import fitz
import tempfile
import os


def run_pdf_compress(
    pdf_path,
    mode="normal"
):

    try:

        doc = fitz.open(pdf_path)

        output_path = os.path.join(
            tempfile.gettempdir(),
            f"compressed_{mode}.pdf"
        )

        if mode == "normal":

            doc.save(
                output_path,
                garbage=4,
                deflate=True,
                clean=True
            )

        else:

            doc.save(
                output_path,
                garbage=4,
                deflate=True,
                clean=True,
                deflate_images=True,
                deflate_fonts=True
            )

        old_size = round(
            os.path.getsize(pdf_path) / 1024 / 1024,
            2
        )

        new_size = round(
            os.path.getsize(output_path) / 1024 / 1024,
            2
        )

        doc.close()

        return (
            output_path,
            f"✅ {old_size} MB → {new_size} MB"
        )

    except Exception as e:

        return None, str(e)