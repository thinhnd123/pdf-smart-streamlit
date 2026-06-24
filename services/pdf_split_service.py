from backend.pdf_split_range import split_pdf_by_ranges


def run_pdf_split_range(
    pdf_path,
    ranges_text
):

    return split_pdf_by_ranges(
        pdf_path,
        ranges_text
    )