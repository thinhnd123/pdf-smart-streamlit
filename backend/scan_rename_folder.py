import os
import re
import time
import shutil
import fitz
import pandas as pd
import pytesseract

from backend.scan_splitter import (
    clean_filename,
    preprocess_image_for_ocr,
   
)

def extract_gcn_exact(text, excel_gcn_list):

    if not text:
        return None

    text = text.upper()

    candidates = re.findall(
        r'C\d{6}[- ]?[A-Z0-9]{1,2}[- ]?\d{4,6}',
        text
    )

    if not candidates:
        return None

    excel_map = {}

    for gcn in excel_gcn_list:

        if not gcn:
            continue

        norm = re.sub(
            r'[-\s\.]',
            '',
            str(gcn).upper()
        )

        excel_map[norm] = str(gcn).upper()

    for candidate in candidates:

        norm_candidate = re.sub(
            r'[-\s\.]',
            '',
            candidate.upper()
        )

        # =====================================
        # MATCH CHÍNH XÁC
        # =====================================

        if norm_candidate in excel_map:

            print(
                f"EXACT MATCH: "
                f"{candidate} -> "
                f"{excel_map[norm_candidate]}"
            )

            return excel_map[norm_candidate]

        # =====================================
        # OCR nhầm ký tự đầu tiên sau dấu -
        # Ví dụ:
        # C20260500097 -> C202605O0097
        # C2026050S0350 -> C202605OS0350
        # =====================================

        if re.match(r'^C\d{6}[0-9]', norm_candidate):

            fixed_candidate = (
                norm_candidate[:7]
                + "O"
                + norm_candidate[8:]
            )

            if fixed_candidate in excel_map:

                print(
                    f"FIXED MATCH (0->O): "
                    f"{candidate} -> "
                    f"{excel_map[fixed_candidate]}"
                )

                return excel_map[fixed_candidate]

    return None

# ==========================================================
# OCR TRANG ĐẦU
# ==========================================================
def ocr_first_page(pdf_path, excel_gcn_list):

    try:

        doc = fitz.open(pdf_path)

        if len(doc) == 0:
            doc.close()
            return None

        page = doc[0]

        img_array = preprocess_image_for_ocr(
            page,
            dpi=300,
            top_percent=0.6
        )

        text = pytesseract.image_to_string(
            img_array,
            lang="vie+eng",
            config='--oem 3 --psm 6'
        )
        
        print("=" * 50)
        print(os.path.basename(pdf_path))
        print(text[:500])
        print("=" * 50)

        doc.close()

        return extract_gcn_exact(
            text,
            excel_gcn_list
        )

    except Exception as e:

        print(f"OCR ERROR: {pdf_path}")
        print(str(e))

        return None


# ==========================================================
# MAIN
# ==========================================================
def rename_scan_folder(
        folder_path,
        excel_path,
        naming_type="ma_ql"
):

    start_time = time.time()

    print("=" * 60)
    print("SCAN RENAME FOLDER")
    print("=" * 60)
    
    print("TEST 1")
    print(excel_path)

    # ======================================================
    # ĐỌC EXCEL
    # ======================================================

    print("TEST 2 - BEFORE READ EXCEL")
    
    # ======================================================
    # ĐỢI FILE TEMP TAIPY ỔN ĐỊNH
    # ======================================================

    last_size = -1

    for _ in range(10):

        if not os.path.exists(excel_path):
            time.sleep(0.5)
            continue

        current_size = os.path.getsize(excel_path)

        if current_size > 0 and current_size == last_size:
            break

        last_size = current_size
        time.sleep(0.5)
    
    df = pd.read_excel(
        excel_path,
        header=None,
        dtype=str
    )
    
    print("TEST 3 - AFTER READ EXCEL")

    df[25] = df[25].fillna("").str.strip().str.upper()

    excel_gcn_list = (
        df[25]
        .unique()
        .tolist()
    )

    excel_gcn_list = [
        x for x in excel_gcn_list
        if x and len(x) > 2
    ]

    print(f"Loaded {len(excel_gcn_list)} GCN")

    # ======================================================
    # OUTPUT
    # ======================================================

    timestamp = int(time.time())

    output_folder = os.path.join(
        folder_path,
        f"Renamed_{timestamp}"
    )

    unknown_folder = os.path.join(
        output_folder,
        "Khong_Xac_Dinh"
    )

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(unknown_folder, exist_ok=True)

    # ======================================================
    # LOG
    # ======================================================

    log_path = os.path.join(
        output_folder,
        "rename_log.txt"
    )

    log_file = open(
        log_path,
        "w",
        encoding="utf-8"
    )

    # ======================================================
    # FILE PDF
    # ======================================================

    pdf_files = [
        f
        for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf")
    ]

    total_files = len(pdf_files)

    used_names = {}

    # ======================================================
    # LOOP
    # ======================================================

    for idx, pdf_name in enumerate(pdf_files, start=1):

        full_pdf_path = os.path.join(
            folder_path,
            pdf_name
        )

        print(
            f"[{idx}/{total_files}] "
            f"{pdf_name}"
        )

        # --------------------------------------------
        # OCR
        # --------------------------------------------

        gcn = ocr_first_page(
            full_pdf_path,
            excel_gcn_list
        )

        print(f"GCN = {gcn}")

        # --------------------------------------------
        # KHÔNG OCR ĐƯỢC
        # --------------------------------------------

        if not gcn:

            shutil.copy2(
                full_pdf_path,
                os.path.join(
                    unknown_folder,
                    pdf_name
                )
            )

            log_file.write(
                f"{pdf_name} | NOT FOUND\n"
            )

            continue

        # --------------------------------------------
        # TÌM EXCEL
        # --------------------------------------------

        matched_rows = df[
            df[25]
            .astype(str)
            .str.strip()
            .str.upper()
            == gcn
        ]

        if matched_rows.empty:

            shutil.copy2(
                full_pdf_path,
                os.path.join(
                    unknown_folder,
                    pdf_name
                )
            )

            log_file.write(
                f"{pdf_name} | GCN={gcn} | NOT IN EXCEL\n"
            )

            continue

        row = matched_rows.iloc[0]

        # ======================================================
        # THÔNG TIN EXCEL
        # ======================================================

        ten_tb = str(row[5]).strip() if pd.notna(row[5]) else ""
        kieu_tb = str(row[6]).strip() if pd.notna(row[6]) else ""
        nha_sx = str(row[7]).strip() if pd.notna(row[7]) else ""
        dac_trung = str(row[8]).strip() if pd.notna(row[8]) else ""
        ma_xuat_xuong = str(row[26]).strip() if pd.notna(row[26]) else ""
        ma_ql = str(row[27]).strip() if pd.notna(row[27]) else ""

        # ======================================================
        # LOGIC ĐẶT TÊN
        # ======================================================
        ten_clean = clean_filename(ten_tb)
        kieu_clean = clean_filename(kieu_tb)
        nha_sx_clean = clean_filename(nha_sx)
        dac_trung_clean = clean_filename(dac_trung)
        ma_xuat_xuong_clean = clean_filename(ma_xuat_xuong)
        ma_ql_clean = clean_filename(ma_ql)

        # tránh lặp model trong tên
        if (
            ten_clean
            and kieu_clean
            and kieu_clean.lower() in ten_clean.lower()
        ):
            ten_clean = re.sub(
                re.escape(kieu_clean),
                "",
                ten_clean,
                flags=re.IGNORECASE
            ).strip()

        # ------------------------------------------------------
        # Tên + Model
        # ------------------------------------------------------

        if naming_type == "ten_tb":

            if ten_clean and kieu_clean:
                final_filename = f"{ten_clean}_{kieu_clean}"

            elif ten_clean:
                final_filename = ten_clean

            elif kieu_clean:
                final_filename = kieu_clean

            else:
                final_filename = f"ThietBi_{gcn}"

        # ------------------------------------------------------
        # Chỉ tên thiết bị
        # ------------------------------------------------------

        elif naming_type == "ten_khong_model":

            final_filename = (
                ten_clean
                if ten_clean
                else f"Khong_Ten_{gcn}"
            )

        # ------------------------------------------------------
        # Chỉ model
        # ------------------------------------------------------

        elif naming_type == "model_khong_ten":

            final_filename = (
                kieu_clean
                if kieu_clean
                else f"Khong_Model_{gcn}"
            )

        # ------------------------------------------------------
        # Seri
        # ------------------------------------------------------

        elif naming_type == "ma_xuat_xuong":

            final_filename = (
                ma_xuat_xuong_clean
                if ma_xuat_xuong_clean
                and ma_xuat_xuong_clean.lower() != "nan"
                else f"Khong_MaXuatXuong_{gcn}"
            )

        # ------------------------------------------------------
        # Tên + Seri
        # ------------------------------------------------------

        elif naming_type == "ten_ma_xuat_xuong":

            parts = [
                p for p in [
                    ten_clean,
                    ma_xuat_xuong_clean
                ]
                if p
            ]

            final_filename = (
                "_".join(parts)
                if parts
                else f"ThietBi_{gcn}"
            )

        # ------------------------------------------------------
        # Tên + Đặc trưng
        # ------------------------------------------------------

        elif naming_type == "ten_dac_trung":

            parts = [
                p for p in [
                    ten_clean,
                    dac_trung_clean
                ]
                if p
            ]

            final_filename = (
                "_".join(parts)
                if parts
                else f"ThietBi_{gcn}"
            )

        # ------------------------------------------------------
        # Tên + Model + NSX
        # ------------------------------------------------------

        elif naming_type == "ten_model_nsx":

            parts = [
                p for p in [
                    ten_clean,
                    kieu_clean,
                    nha_sx_clean
                ]
                if p
            ]

            final_filename = (
                "_".join(parts)
                if parts
                else f"ThietBi_{gcn}"
            )

        # ------------------------------------------------------
        # Tên + Model + Đặc trưng
        # ------------------------------------------------------

        elif naming_type == "ten_model_dac_trung":

            parts = [
                p for p in [
                    ten_clean,
                    kieu_clean,
                    dac_trung_clean
                ]
                if p
            ]

            final_filename = (
                "_".join(parts)
                if parts
                else f"ThietBi_{gcn}"
            )

        # ------------------------------------------------------
        # Mã quản lý
        # ------------------------------------------------------

        elif naming_type == "ma_ql":

            final_filename = (
                ma_ql_clean
                if ma_ql_clean
                and ma_ql_clean.lower() != "nan"
                else f"Khong_MaQL_{gcn}"
            )

        # ------------------------------------------------------
        # Số GCN
        # ------------------------------------------------------

        elif naming_type == "so_gcn":

            final_filename = clean_filename(gcn)

        # ------------------------------------------------------
        # Default
        # ------------------------------------------------------

        else:

            final_filename = clean_filename(gcn)

        # ======================================================
        # CHỐNG TRÙNG
        # ======================================================

        if final_filename in used_names:

            used_names[final_filename] += 1

            final_filename = (
                f"{final_filename}_"
                f"{used_names[final_filename]}"
            )

        else:

            used_names[final_filename] = 0

        # ======================================================
        # COPY
        # ======================================================

        dest_path = os.path.join(
            output_folder,
            final_filename + ".pdf"
        )

        shutil.copy2(
            full_pdf_path,
            dest_path
        )

        log_file.write(
            f"{pdf_name}"
            f" -> "
            f"{final_filename}.pdf"
            f" | GCN={gcn}\n"
        )

    log_file.close()

    total_time = round(
        time.time() - start_time,
        2
    )

    return (
        output_folder,
        f"✅ Hoàn thành {total_files} file trong {total_time}s"
    )