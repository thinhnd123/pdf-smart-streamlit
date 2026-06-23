from backend.smart_splitter import smart_split_pdf


def run_smart_split(
    pdf_path: str,
    keyword: str,
    naming_type: str
):
    return smart_split_pdf(
        pdf_path=pdf_path,
        keyword=keyword,
        naming_type=naming_type
    )