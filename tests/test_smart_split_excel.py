from backend.smart_splitter import smart_split_pdf_with_excel

zip_path, msg = smart_split_pdf_with_excel(
    pdf_path=r"D:\Giai nen rar\Cert-GST_VN2026050306HF_2237.pdf",
    excel_path=r"D:\Giai nen rar\est vina.xlsx",
    keyword="GIẤY CHỨNG NHẬN HIỆU CHUẨN",
    naming_type="ten_tb"
)

print(msg)
print(zip_path)