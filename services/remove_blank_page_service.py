import fitz
import numpy as np
import tempfile
import os


def is_blank_page(
    page,
    dpi=100,
    threshold=0.98
):
    """
    Kiểm tra trang trắng
    """

    pix = page.get_pixmap(
        matrix=fitz.Matrix(
            dpi / 72,
            dpi / 72
        ),
        colorspace=fitz.csGRAY
    )

    img = np.frombuffer(
        pix.samples,
        dtype=np.uint8
    )

    white_pixels = np.sum(
        img > 245
    )

    total_pixels = img.size

    white_ratio = (
        white_pixels /
        total_pixels
    )

    return (
        white_ratio >= threshold,
        white_ratio
    )


def run_remove_blank_last_page(
    pdf_path,
    threshold=0.98
):

    try:

        doc = fitz.open(pdf_path)

        total_pages = len(doc)

        if total_pages <= 1:

            return (
                None,
                "PDF chỉ có 1 trang"
            )

        last_page = doc[-1]

        blank, ratio = is_blank_page(
            last_page,
            threshold=threshold
        )

        output_pdf = os.path.join(
            tempfile.gettempdir(),
            "BlankRemoved.pdf"
        )

        if blank:

            new_doc = fitz.open()

            for i in range(
                total_pages - 1
            ):
                new_doc.insert_pdf(
                    doc,
                    from_page=i,
                    to_page=i
                )

            new_doc.save(
                output_pdf
            )

            new_doc.close()

            doc.close()

            return (
                output_pdf,
                f"✅ Đã xoá trang trắng cuối (White ratio = {ratio:.2%})"
            )

        else:

            doc.save(
                output_pdf
            )

            doc.close()

            return (
                output_pdf,
                f"ℹ️ Không phát hiện trang trắng (White ratio = {ratio:.2%})"
            )

    except Exception as e:

        return (
            None,
            str(e)
        )