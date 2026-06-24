import fitz
import numpy as np
import tempfile
import os
import zipfile


def is_blank_page(
    page,
    dpi=100,
    threshold=0.98
):

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

    white_ratio = np.sum(
        img > 245
    ) / img.size

    return white_ratio >= threshold


def process_pdf(
    pdf_path,
    output_folder,
    threshold
):

    doc = fitz.open(pdf_path)

    new_doc = fitz.open()

    removed_pages = []

    for page_num in range(len(doc)):

        page = doc[page_num]

        if is_blank_page(
            page,
            threshold=threshold
        ):

            removed_pages.append(
                page_num + 1
            )

            continue

        new_doc.insert_pdf(
            doc,
            from_page=page_num,
            to_page=page_num
        )

    output_file = os.path.join(
        output_folder,
        os.path.basename(pdf_path)
    )

    new_doc.save(output_file)

    new_doc.close()
    doc.close()

    return (
        output_file,
        removed_pages
    )


def run_remove_blank_pages_batch(
    pdf_paths,
    threshold=0.98
):

    temp_dir = tempfile.mkdtemp()

    result_lines = []

    for pdf_path in pdf_paths:

        output_file, removed = process_pdf(
            pdf_path,
            temp_dir,
            threshold
        )

        result_lines.append(
            f"{os.path.basename(pdf_path)} | "
            f"Removed: {removed}"
        )

    zip_path = os.path.join(
        tempfile.gettempdir(),
        "Blank_Page_Removed.zip"
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zipf:

        for file in os.listdir(temp_dir):

            full_path = os.path.join(
                temp_dir,
                file
            )

            zipf.write(
                full_path,
                file
            )

    return (
        zip_path,
        "\n".join(result_lines)
    )