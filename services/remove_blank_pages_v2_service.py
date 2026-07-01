import fitz
import numpy as np
import io
import zipfile
import os

def is_blank_page(page, dpi=100, threshold=0.98):
    """
    Thuật toán kiểm tra trang trống cải tiến:
    Sử dụng Numpy tốc độ cao của bạn, nhưng cắt bỏ 25% diện tích Header (Logo/Tên công ty)
    để chỉ quét nội dung lõi ở 75% phía dưới.
    """
    # 1. Lấy kích thước thực tế của trang PDF
    rect = page.rect
    width = rect.width
    height = rect.height
    
    # 2. 🔥 CẮT VÙNG (ROI): Bỏ qua 25% chiều cao tính từ đỉnh trang
    y_start = height * 0.25
    search_region = fitz.Rect(0, y_start, width, height)
    
    # TẦNG 1: Kiểm tra text thô nhanh trong vùng 75% phía dưới.
    # Nếu nửa dưới có chữ thực tế (nhiều hơn 5 ký tự), giữ lại luôn cho nhanh, đỡ phải dựng ảnh.
    text_in_region = page.get_text("text", clip=search_region).strip()
    if len(text_in_region) > 5:
        return False

    # TẦNG 2: Dựng ảnh ma trận điểm xám (colorspace=fitz.csGRAY) RIÊNG CHO VÙNG CẮT
    pix = page.get_pixmap(
        matrix=fitz.Matrix(dpi / 72, dpi / 72),
        colorspace=fitz.csGRAY,
        clip=search_region  # 🎯 Quan trọng: Chỉ lấy dữ liệu ảnh của vùng phía dưới
    )

    img = np.frombuffer(pix.samples, dtype=np.uint8)

    # Nếu vùng cắt trống (tránh lỗi chia cho 0)
    if img.size == 0:
        return True

    # Kế thừa logic xử lý mảng Numpy siêu tốc của bạn
    white_ratio = np.sum(img > 245) / img.size

    # Nếu tỷ lệ trắng của vùng dưới đạt ngưỡng (ví dụ >= 0.98 hoặc 0.99) -> Trang trống!
    return white_ratio >= threshold


def process_pdf_in_memory(uploaded_file, threshold):
    """
    Xử lý đọc và ghi lọc trang trắng trực tiếp trên luồng byte RAM,
    bảo toàn nguyên lý của hàm process_pdf cũ của bạn.
    """
    # Mở file trực tiếp từ luồng byte upload
    file_bytes = uploaded_file.getvalue()
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    
    new_doc = fitz.open()
    removed_pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Gọi hàm lọc bỏ logo thông minh
        if is_blank_page(page, threshold=threshold):
            removed_pages.append(page_num + 1)
            continue

        new_doc.insert_pdf(
            doc,
            from_page=page_num,
            to_page=page_num
        )

    # Nếu file bị xóa sạch không còn trang nào, giữ lại trang 1 để tránh lỗi PDF rỗng
    if len(new_doc) == 0 and len(doc) > 0:
        new_doc.insert_pdf(doc, from_page=0, to_page=0)
        if 1 in removed_pages:
            removed_pages.remove(1)

    # Xuất dữ liệu ra bộ nhớ RAM thay vì lưu xuống ổ cứng
    output_pdf_bytes = new_doc.tobytes()
    
    new_doc.close()
    doc.close()

    return output_pdf_bytes, removed_pages


def run_remove_blank_pages_batch(uploaded_files, threshold=0.98):
    """
    Hàm tổng điều hướng: Nhận mảng file từ Frontend Streamlit,
    xử lý nén ZIP hoàn toàn trên RAM và trả kết quả về.
    """
    zip_buffer = io.BytesIO()
    result_lines = []

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Duyệt qua danh sách các file nhị phân được upload từ UI
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            # Xử lý lọc trang trực tiếp trên RAM
            clean_bytes, removed = process_pdf_in_memory(uploaded_file, threshold)

            # Ghi trực tiếp file sạch vào file nén ZIP trên bộ nhớ đệm
            zipf.writestr(file_name, clean_bytes)

            result_lines.append(
                f"📋 {file_name} | Đã xóa các trang trống số: {removed}"
            )

    zip_buffer.seek(0)
    return zip_buffer, "\n".join(result_lines)