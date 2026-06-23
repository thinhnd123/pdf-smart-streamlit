from backend.smart_splitter import smart_split_pdf

pdf_path = r"D:\Giai nen rar\Cert-GST_VN2026050306HF_2237.pdf"

zip_path, msg = smart_split_pdf(
    pdf_path,
    keyword="GIẤY CHỨNG NHẬN HIỆU CHUẨN",
    naming_type="ma_ql"
)

print(msg)
print(zip_path)