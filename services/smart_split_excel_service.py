from backend.smart_splitter import smart_split_pdf_with_excel


def run_smart_split_excel(
    pdf_path,
    excel_path,
    keyword,
    naming_type
):

    return smart_split_pdf_with_excel(
        pdf_path=pdf_path,
        excel_path=excel_path,
        keyword=keyword,
        naming_type=naming_type
    )