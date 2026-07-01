import fitz  # PyMuPDF
import os
import re
import zipfile
import pandas as pd
import numpy as np
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image, ImageEnhance, ImageFilter
import io
import cv2
import pytesseract
import sys

# ============================================================
# CẤU HÌNH TESSERACT
# ============================================================
# Đường dẫn đến Tesseract (sửa nếu cần)
# 🎯 ĐOẠN CẤU HÌNH ĐƯỜNG DẪN SCAN TỰ ĐỘNG:
if getattr(sys, 'frozen', False):
    # Nếu đang chạy từ file .EXE đã đóng gói cài vào máy khách
    base_path = sys._MEIPASS
    tesseract_exe_path = os.path.join(base_path, 'Tesseract-OCR', 'tesseract.exe')
    pytesseract.pytesseract.tesseract_cmd = tesseract_exe_path
else:
    # Nếu đang chạy Local bằng lệnh streamlit run ở máy của bạn
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ============================================================
# CẤU HÌNH LOGGING
# ============================================================
logging.getLogger("PIL").setLevel(logging.ERROR)
import warnings
warnings.filterwarnings("ignore")


# ============================================================
# HÀM CLEAN FILENAME - LOẠI BỎ KÝ TỰ ĐẶC BIỆT
# ============================================================
def clean_filename(text):
    """Loại bỏ các ký tự không hợp lệ trong tên file"""
    if not text:
        return ""
    return re.sub(r'[\/\\\:\*\?\"\<\>\|]', '_', text).strip()


# ============================================================
# TIỀN XỬ LÝ ẢNH OCR - TỐI ƯU CHO TESSERACT
# ============================================================
def preprocess_image_for_ocr(page, dpi=300, top_percent=0.6):
    """
    Tối ưu ảnh OCR cho Tesseract:
    - Tăng vùng crop lên 60% để an toàn hơn
    - Tăng chất lượng ảnh
    """
    rect = page.rect

    # Tăng vùng crop lên 60% để không bỏ sót mã GCN
    crop_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + rect.height * top_percent)

    # Tăng DPI lên 300
    mat = fitz.Matrix(dpi / 72, dpi / 72)

    # Render ảnh
    pix = page.get_pixmap(matrix=mat, clip=crop_rect)
    img_data = pix.tobytes("png")

    # Chuyển thành PIL Image
    pil_img = Image.open(io.BytesIO(img_data))

    # ============================================================
    # TĂNG CHẤT LƯỢNG ẢNH CHO TESSERACT
    # ============================================================
    # Chuyển sang ảnh xám
    if pil_img.mode != 'L':
        pil_img = pil_img.convert('L')

    # Tăng độ tương phản
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(2.5)

    # Tăng độ sắc nét
    enhancer = ImageEnhance.Sharpness(pil_img)
    pil_img = enhancer.enhance(2.5)

    # Resize ảnh lên 2x để Tesseract đọc rõ hơn
    width, height = pil_img.size
    pil_img = pil_img.resize((width * 2, height * 2), Image.Resampling.LANCZOS)

    # Chuyển sang numpy array
    img_array = np.array(pil_img)

    # Áp dụng threshold
    _, img_array = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return img_array


# ============================================================
# LOGIC TÌM MÃ GCN - TĂNG ĐỘ CHÍNH XÁC
# ============================================================
def extract_gcn_intelligent(text, excel_gcn_list):
    """
    Logic tìm GCN - ƯU TIÊN ĐỊNH DẠNG C202606-L0211
    """
    if not text or len(text.strip()) < 3:
        return None

    # Chuẩn hóa text
    cleaned = re.sub(r'\s+', ' ', text.strip())

    # ============================================================
    # PATTERN TÌM MÃ GCN - ƯU TIÊN CHÍNH XÁC
    # ============================================================
    gcn_patterns = [
        # Format chính xác: C202606-L0211 (có dấu gạch nối)
        r'(C[12][09]\d{2}[0-1][0-9][\s\-\.]*[A-Z]{1,2}[\s\-\.]*\d{4,6})',
        # Format: C202606L0211 (không dấu gạch nối)
        r'(C[12][09]\d{2}[0-1][0-9][A-Z]{1,2}\d{4,6})',
        # Format: C202606-0211-L
        r'(C[12][09]\d{2}[0-1][0-9][\s\-\.]*\d{4,6}[\s\-\.]*[A-Z]{1,2})',
        # Format tổng quát
        r'(C[12][09]\d{2}[0-1][0-9][\s\-\.]*[A-Z0-9]{4,8})',
    ]

    found_candidates = []
    for pattern in gcn_patterns:
        matches = re.findall(pattern, cleaned, re.IGNORECASE)
        if matches:
            found_candidates.extend(matches)

    # Dự phòng - tìm các mã dạng C2025-xxxx
    if not found_candidates:
        backup_patterns = [
            r'(C[12][09]\d{2}[\s\-\.]*\d{4,6})',
            r'(C[12][09]\d{2}[\s\-\.]*[A-Z0-9]{4,8})',
            r'(C[12][09]\d{2}\s+\d{4,6})',
        ]
        for pattern in backup_patterns:
            matches = re.findall(pattern, cleaned, re.IGNORECASE)
            if matches:
                found_candidates.extend(matches)

    # ============================================================
    # SO SÁNH VỚI DANH SÁCH EXCEL - ƯU TIÊN EXACT MATCH
    # ============================================================
    normalized_candidates = []
    for cand in found_candidates:
        # Chuẩn hóa: bỏ dấu cách, gạch nối, dấu chấm
        norm = re.sub(r'[-\s\.]', '', cand).upper().strip()
        if len(norm) >= 7:
            normalized_candidates.append((cand, norm))

    # ƯU TIÊN 1: EXACT MATCH (sau khi chuẩn hóa)
    for original, norm_candidate in normalized_candidates:
        for gcn_excel in excel_gcn_list:
            if pd.isna(gcn_excel) or not gcn_excel:
                continue

            gcn_excel_clean = re.sub(r'[-\s\.]', '', str(gcn_excel)).upper().strip()

            if norm_candidate == gcn_excel_clean:
                print(f"      ✅ EXACT MATCH: {original} -> {gcn_excel}")
                return str(gcn_excel).strip().upper()

    # ƯU TIÊN 2: KIỂM TRA NĂM + THÁNG KHỚP (7 ký tự đầu)
    for original, norm_candidate in normalized_candidates:
        for gcn_excel in excel_gcn_list:
            if pd.isna(gcn_excel) or not gcn_excel:
                continue

            gcn_excel_clean = re.sub(r'[-\s\.]', '', str(gcn_excel)).upper().strip()

            if len(norm_candidate) >= 7 and len(gcn_excel_clean) >= 7:
                if norm_candidate[:7] == gcn_excel_clean[:7]:
                    print(f"      ✅ YEAR-MONTH MATCH: {original} -> {gcn_excel}")
                    return str(gcn_excel).strip().upper()

    # ƯU TIÊN 3: FUZZY MATCH (nếu trên 80% giống nhau)
    for original, norm_candidate in normalized_candidates:
        for gcn_excel in excel_gcn_list:
            if pd.isna(gcn_excel) or not gcn_excel:
                continue

            gcn_excel_clean = re.sub(r'[-\s\.]', '', str(gcn_excel)).upper().strip()

            if len(norm_candidate) >= 7 and len(gcn_excel_clean) >= 7:
                # So sánh từng ký tự
                matches = sum(1 for a, b in zip(norm_candidate, gcn_excel_clean) if a == b)
                ratio = matches / max(len(norm_candidate), len(gcn_excel_clean))
                if ratio > 0.8:
                    print(f"      ✅ FUZZY MATCH ({ratio:.0%}): {original} -> {gcn_excel}")
                    return str(gcn_excel).strip().upper()

    # FALLBACK: Trả về candidate đầu tiên có format đúng
    for original, norm_candidate in normalized_candidates:
        if re.match(r'C[12][09]\d{2}[0-1][0-9]', norm_candidate):
            print(f"      ⚠️ FALLBACK: {original}")
            return original.strip().upper()

    return None


# ============================================================
# XỬ LÝ OCR CHO 1 TRANG
# ============================================================
def process_page_ocr(page_num, page, excel_gcn_list, dpi=300, top_percent=0.6, lang='vie+eng'):
    """
    Xử lý OCR cho 1 trang
    """
    try:
        start_time = time.time()

        # Tiền xử lý ảnh
        img_array = preprocess_image_for_ocr(page, dpi=dpi, top_percent=top_percent)

        # ============================================================
        # OCR BẰNG TESSERACT - CẤU HÌNH TỐI ƯU
        # ============================================================
        # - psm 6: Nhận dạng khối văn bản
        # - oem 3: Sử dụng LSTM + Legacy
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-. '
        page_text = pytesseract.image_to_string(img_array, lang=lang, config=custom_config)

        # Làm sạch text
        page_text = re.sub(r'\n+', ' ', page_text).strip()

        # Debug
        if page_text:
            print(f"📄 Trang {page_num+1}: Đọc được {len(page_text)} ký tự")
            preview = page_text[:200].replace('\n', ' ')
            print(f"   Text mẫu: {preview}...")
        else:
            print(f"📄 Trang {page_num+1}: Không đọc được text nào")

        # Tìm GCN
        detected_gcn = extract_gcn_intelligent(page_text, excel_gcn_list)

        if detected_gcn:
            print(f"   ✅ -> GCN TÌM THẤY: {detected_gcn}")
        else:
            # Debug tìm pattern
            found = re.findall(r'C[12][09]\d{2}[0-1][0-9][\s\-\.]*[A-Z0-9]+', page_text, re.IGNORECASE)
            if found:
                print(f"   ⚠️ Candidate GCN (không khớp Excel): {found[:3]}")
            else:
                found_any = re.findall(r'C\d{4,}', page_text, re.IGNORECASE)
                if found_any:
                    print(f"   ⚠️ Tìm thấy chuỗi chứa C + số: {found_any[:3]}")
                else:
                    print(f"   ❌ Không tìm thấy GCN nào")

        elapsed = time.time() - start_time
        return {
            'page_num': page_num,
            'gcn': detected_gcn,
            'text': page_text,
            'time': elapsed
        }

    except Exception as e:
        print(f"⚠️ Lỗi trang {page_num+1}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'page_num': page_num,
            'gcn': None,
            'text': '',
            'time': 0
        }


# ============================================================
# HÀM CHÍNH: XỬ LÝ SCAN PDF + EXCEL
# ============================================================
def smart_split_scan_pdf_with_excel(pdf_path, excel_path, naming_type="ten_tb", max_workers=4, dpi=300, top_percent=0.6):
    """
    THUẬT TOÁN OCR TỐI ƯU VỚI ĐA LUỒNG - DÙNG TESSERACT
    """
    global_start = time.time()
    print("="*60)
    print("🚀 [OCR BACKEND] BẮT ĐẦU XỬ LÝ SCAN PDF (TESSERACT - ĐA LUỒNG)")
    print("="*60)

    # 1. Mở file PDF
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"📑 Tổng số trang: {total_pages}")
    print(f"⚙️ Cấu hình: DPI={dpi}, Crop={top_percent*100}%, Số luồng={max_workers}")

    # 2. Đọc file Excel
    try:
        print("📊 Đọc file Excel đối chiếu...")
        df = pd.read_excel(excel_path, header=None, dtype=str)
        df[25] = df[25].fillna("").str.strip().str.upper()
        excel_gcn_list = df[25].unique().tolist()
        excel_gcn_list = [x for x in excel_gcn_list if x and len(x) > 2]
        print(f"✅ Loaded {len(excel_gcn_list)} mã GCN từ Excel")

        if len(excel_gcn_list) > 0:
            print(f"📌 Mẫu mã GCN trong Excel: {excel_gcn_list[:5]}")
    except Exception as e:
        doc.close()
        return None, f"❌ Lỗi đọc Excel: {str(e)}"

    # 3. Xử lý song song các trang
    print(f"⚡ Bắt đầu xử lý {total_pages} trang với {max_workers} luồng...")

    page_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_page_ocr, i, doc[i], excel_gcn_list, dpi, top_percent): i
            for i in range(total_pages)
        }

        for future in as_completed(futures):
            result = future.result()
            page_results.append(result)

            if result['gcn']:
                print(f"✅ Trang {result['page_num']+1}: TÌM THẤY GCN = {result['gcn']} (tốc độ {result['time']:.2f}s)")
            else:
                print(f"⏭️ Trang {result['page_num']+1}: Không tìm thấy GCN ({result['time']:.2f}s)")

    page_results.sort(key=lambda x: x['page_num'])

    # 4. Gom nhóm các trang
    print("\n📦 Gom nhóm các trang theo mã GCN...")
    page_groups = []
    current_group = None

    for result in page_results:
        gcn = result['gcn']
        page_num = result['page_num']

        if gcn:
            # Nếu có GCN
            if current_group is None:
                # Chưa có nhóm nào -> tạo nhóm mới
                current_group = {'gcn': gcn, 'pages': [page_num]}
                print(f"   📌 NHÓM MỚI: GCN={gcn} (trang {page_num+1})")
            elif current_group['gcn'] == gcn:
                # Cùng GCN với nhóm hiện tại -> gộp vào
                current_group['pages'].append(page_num)
                print(f"   ➕ Thêm trang {page_num+1} vào nhóm {gcn}")
            else:
                # GCN khác -> lưu nhóm cũ, tạo nhóm mới
                page_groups.append(current_group)
                current_group = {'gcn': gcn, 'pages': [page_num]}
                print(f"   📌 NHÓM MỚI: GCN={gcn} (trang {page_num+1})")
        else:
            # Không có GCN
            if current_group is None:
                # Chưa có nhóm -> tạo nhóm UNKNOWN
                current_group = {'gcn': f"UNKNOWN_{page_num+1}", 'pages': [page_num]}
                print(f"   ⚠️ Trang {page_num+1} không thuộc nhóm nào")
            else:
                # Thêm vào nhóm hiện tại
                current_group['pages'].append(page_num)
                print(f"   ➕ Thêm trang {page_num+1} vào nhóm {current_group['gcn']}")

    # Thêm nhóm cuối cùng
    if current_group:
        page_groups.append(current_group)

    print(f"📊 Tổng số nhóm: {len(page_groups)}")

    # 5. Tạo file PDF và ZIP
    print("\n💾 Tạo file PDF và đóng gói ZIP...")

    base_dir = os.path.dirname(pdf_path)
    if not base_dir:
        base_dir = os.getcwd()

    output_folder = os.path.join(base_dir, "output_split_scan")
    os.makedirs(output_folder, exist_ok=True)

    # Xóa file cũ
    for f in os.listdir(output_folder):
        try:
            os.remove(os.path.join(output_folder, f))
        except:
            pass

    zip_name = f"Tach_Scan_Excel_{naming_type}_{int(time.time())}.zip"
    zip_path = os.path.join(output_folder, zip_name)

    used_names = {}

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for group in page_groups:
            gcn_key = group['gcn']
            pages = group['pages']

            new_doc = fitz.open()
            for p_idx in pages:
                new_doc.insert_pdf(doc, from_page=p_idx, to_page=p_idx)

            if "UNKNOWN" in gcn_key:
                final_filename = f"Khong_Xac_Dinh_{pages[0]+1}"
            else:
                # Tra cứu Excel
                matched_rows = df[df[25].astype(str).str.strip().str.upper() == gcn_key]

                if not matched_rows.empty:
                    row = matched_rows.iloc[0]

                    # ============================================================
                    # LẤY TẤT CẢ DỮ LIỆU TỪ EXCEL
                    # ============================================================
                    # Các cột trong Excel (chỉ số từ 0)
                    # Cột F (5): Tên thiết bị
                    # Cột G (6): Kiểu máy / Loại (Model)
                    # Cột H (7): Nhà sản xuất
                    # Cột I (8): Đặc trưng kỹ thuật
                    # Cột AA (26): Mã xuất xưởng / Seri
                    # Cột AB (27): Mã quản lý

                    ten_tb = str(row[5]).strip() if pd.notna(row[5]) else ""       # Cột F - Tên thiết bị
                    kieu_tb = str(row[6]).strip() if pd.notna(row[6]) else ""      # Cột G - Kiểu máy (Model)
                    nha_sx = str(row[7]).strip() if pd.notna(row[7]) else ""       # Cột H - Nhà sản xuất
                    dac_trung = str(row[8]).strip() if pd.notna(row[8]) else ""    # Cột I - Đặc trưng kỹ thuật
                    ma_xuat_xuong = str(row[26]).strip() if pd.notna(row[26]) else ""  # Cột AA - Mã xuất xưởng/Seri
                    ma_ql = str(row[27]).strip() if pd.notna(row[27]) else ""      # Cột AB - Mã quản lý

                    # ============================================================
                    # XỬ LÝ TÊN FILE THEO TỪNG CASE
                    # ============================================================
                    if naming_type == "ten_tb":
                        # Tên + Kiểu máy (F + G)
                        ten_clean = clean_filename(ten_tb)
                        kieu_clean = clean_filename(kieu_tb)
                        # Nếu kiểu máy nằm trong tên -> bỏ kiểu máy để tránh trùng lặp
                        if kieu_clean and kieu_clean in ten_clean:
                            ten_clean = ten_clean.replace(kieu_clean, "").strip()
                        if ten_clean and kieu_clean:
                            final_filename = f"{ten_clean}_{kieu_clean}"
                        else:
                            final_filename = ten_clean if ten_clean else (kieu_clean if kieu_clean else f"ThietBi_{gcn_key}")

                    elif naming_type == "ten_khong_model":
                        # Chỉ lấy tên (không model) - Cột F
                        ten_clean = clean_filename(ten_tb)
                        # Loại bỏ model khỏi tên nếu có
                        kieu_clean = clean_filename(kieu_tb)
                        if kieu_clean and kieu_clean in ten_clean:
                            ten_clean = ten_clean.replace(kieu_clean, "").strip()
                        final_filename = ten_clean if ten_clean else f"Khong_Ten_{gcn_key}"

                    elif naming_type == "model_khong_ten":
                        # Chỉ lấy kiểu máy (không tên) - Cột G
                        kieu_clean = clean_filename(kieu_tb)
                        final_filename = kieu_clean if kieu_clean else f"Khong_Model_{gcn_key}"

                    elif naming_type == "ma_xuat_xuong":
                        # Mã xuất xưởng / Seri - Cột AA
                        ma_xuat_xuong_clean = clean_filename(ma_xuat_xuong)
                        if ma_xuat_xuong_clean and ma_xuat_xuong_clean not in ["/", "nan", ""]:
                            final_filename = ma_xuat_xuong_clean
                        else:
                            final_filename = f"Khong_MaXuatXuong_{gcn_key}"

                    elif naming_type == "ten_ma_xuat_xuong":
                        # Tên + Mã xuất xưởng (F + AA)
                        ten_clean = clean_filename(ten_tb)
                        ma_xuat_xuong_clean = clean_filename(ma_xuat_xuong)
                        if ten_clean and ma_xuat_xuong_clean:
                            final_filename = f"{ten_clean}_{ma_xuat_xuong_clean}"
                        else:
                            final_filename = ten_clean if ten_clean else (ma_xuat_xuong_clean if ma_xuat_xuong_clean else f"ThietBi_{gcn_key}")

                    elif naming_type == "ten_dac_trung":
                        # Tên + Đặc trưng kỹ thuật (F + I)
                        ten_clean = clean_filename(ten_tb)
                        dac_trung_clean = clean_filename(dac_trung)
                        if ten_clean and dac_trung_clean:
                            final_filename = f"{ten_clean}_{dac_trung_clean}"
                        else:
                            final_filename = ten_clean if ten_clean else (dac_trung_clean if dac_trung_clean else f"ThietBi_{gcn_key}")

                    elif naming_type == "ten_model_nsx":
                        # Tên + Model + Nhà sản xuất (F + G + H)
                        ten_clean = clean_filename(ten_tb)
                        kieu_clean = clean_filename(kieu_tb)
                        nha_sx_clean = clean_filename(nha_sx)

                        # Nếu kiểu máy nằm trong tên -> bỏ kiểu máy
                        if kieu_clean and kieu_clean in ten_clean:
                            ten_clean = ten_clean.replace(kieu_clean, "").strip()

                        # Ghép các phần không rỗng
                        parts = [p for p in [ten_clean, kieu_clean, nha_sx_clean] if p]
                        if parts:
                            final_filename = "_".join(parts)
                        else:
                            final_filename = f"ThietBi_{gcn_key}"

                    elif naming_type == "ten_model_dac_trung":
                        # Tên + Model + Đặc trưng kỹ thuật (F + G + I)
                        ten_clean = clean_filename(ten_tb)
                        kieu_clean = clean_filename(kieu_tb)
                        dac_trung_clean = clean_filename(dac_trung)

                        # Nếu kiểu máy nằm trong tên -> bỏ kiểu máy
                        if kieu_clean and kieu_clean in ten_clean:
                            ten_clean = ten_clean.replace(kieu_clean, "").strip()

                        # Ghép các phần không rỗng
                        parts = [p for p in [ten_clean, kieu_clean, dac_trung_clean] if p]
                        if parts:
                            final_filename = "_".join(parts)
                        else:
                            final_filename = f"ThietBi_{gcn_key}"

                    elif naming_type == "ma_ql":
                        # Mã quản lý (cột AB)
                        ma_ql_clean = clean_filename(ma_ql)
                        if ma_ql_clean and ma_ql_clean not in ["/", "nan", ""]:
                            final_filename = ma_ql_clean
                        else:
                            final_filename = f"Khong_MaQL_{gcn_key}"

                    else:  # so_gcn (mặc định)
                        final_filename = f"GCN_{gcn_key}"

                else:
                    final_filename = f"Khong_Excel_{gcn_key}"

            # Xử lý trùng tên
            final_filename = re.sub(r'\s+', ' ', final_filename).strip()
            if final_filename in used_names:
                used_names[final_filename] += 1
                filename = f"{final_filename}_{used_names[final_filename]}.pdf"
            else:
                used_names[final_filename] = 0
                filename = f"{final_filename}.pdf"

            save_path = os.path.join(output_folder, filename)
            new_doc.save(save_path)
            zipf.write(save_path, filename)
            new_doc.close()

    doc.close()

    total_time = time.time() - global_start
    print(f"\n{'='*60}")
    print(f"✅ HOÀN THÀNH trong {total_time:.2f} giây!")
    print(f"📦 ZIP file: {zip_path}")
    print(f"📄 Số nhóm: {len(page_groups)}")
    print("="*60)

    return zip_path, f"🎉 Xử lý thành công {len(page_groups)} nhóm trong {total_time:.2f} giây!"


# ============================================================
# TEST FUNCTION
# ============================================================
if __name__ == "__main__":
    print("="*60)
    print("🧪 CHẾ ĐỘ TEST SCAN SPLITTER (TESSERACT)")
    print("="*60)

    test_pdf = r"D:\path\to\your\test_scan.pdf"
    test_excel = r"D:\path\to\your\test_data.xlsx"

    if os.path.exists(test_pdf) and os.path.exists(test_excel):
        print(f"📄 Test PDF: {test_pdf}")
        print(f"📊 Test Excel: {test_excel}")

        result, msg = smart_split_scan_pdf_with_excel(
            test_pdf,
            test_excel,
            naming_type="so_gcn",
            max_workers=4,
            dpi=300,
            top_percent=0.6
        )
        print(f"\n📌 Kết quả: {msg}")
    else:
        print("❌ Vui lòng cập nhật đường dẫn test!")