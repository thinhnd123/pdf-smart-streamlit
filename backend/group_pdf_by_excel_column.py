import os
import shutil
import tempfile
import zipfile
import pandas as pd
import time

def group_pdf_by_excel_column(uploaded_pdfs, excel_path, match_col_idx, target_col_idx):
    """
    uploaded_pdfs: Danh sách các file PDF người dùng upload từ Streamlit
    excel_path: Đường dẫn file Excel tạm
    match_col_idx: Chỉ số cột chứa Mã GCN (0, 1, 2...) để đối chiếu tên file
    target_col_idx: Chỉ số cột chứa giá trị để phân loại Gom nhóm (0, 1, 2...)
    """
    try:
        # 1. Đọc file Excel
        df = pd.read_excel(excel_path, header=None, dtype=str)
        df = df.fillna("").astype(str)

        # Tạo map: { Mã_GCN_Chuẩn_Hóa: Giá_Trị_Cột_Trả_Về }
        excel_map = {}
        for _, row in df.iterrows():
            gcn_raw = row[match_col_idx].strip().upper()
            target_val = row[target_col_idx].strip()
            if gcn_raw:
                excel_map[gcn_raw] = target_val

        # 2. Tạo thư mục tạm để gom nhóm file
        base_tmp_dir = tempfile.mkdtemp()
        
        success_count = 0
        fail_count = 0
        log_lines = []

        # 3. Duyệt qua từng file PDF được upload
        for pdf_file in uploaded_pdfs:
            # Lấy tên file không bao gồm đuôi .pdf và viết hoa để đối chiếu
            pdf_name = pdf_file.name
            gcn_key = os.path.splitext(pdf_name)[0].strip().upper()

            if gcn_key in excel_map and excel_map[gcn_key]:
                # Tìm thấy nhóm tương ứng
                group_name = excel_map[gcn_key]
                # Clean tên folder (loại bỏ ký tự đặc biệt nếu có)
                group_folder_name = "".join([c for c in group_name if c.isalpha() or c.isdigit() or c in ' _-']).strip()
                if not group_folder_name:
                    group_folder_name = "Nhom_Khong_Ten"
                
                target_folder = os.path.join(base_tmp_dir, group_folder_name)
                success_count += 1
                log_lines.append(f"Khớp thành công: {pdf_name} -> Thư mục [{group_folder_name}]")
            else:
                # Không khớp hoặc cột trả về trống
                target_folder = os.path.join(base_tmp_dir, "Khong_Tim_Thay")
                fail_count += 1
                log_lines.append(f"Không khớp: {pdf_name} -> Thư mục [Khong_Tim_Thay]")

            # Tạo thư mục con và lưu file vào
            os.makedirs(target_folder, exist_ok=True)
            with open(os.path.join(target_folder, pdf_name), "wb") as f:
                f.write(pdf_file.getvalue())

        # Ghi log file nhét vào ZIP luôn cho người dùng đối chiếu
        with open(os.path.join(base_tmp_dir, "LOG_Doi_Chieu.txt"), "w", encoding="utf-8") as log_f:
            log_f.write("\n".join(log_lines))

        # 4. Nén toàn bộ thư mục tạm thành file ZIP
        zip_output_path = os.path.join(tempfile.gettempdir(), f"Gom_Nhom_PDF_{int(time.time())}.zip")
        with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(base_tmp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Giữ nguyên cấu trúc thư mục con trong file ZIP
                    arcname = os.path.relpath(file_path, base_tmp_dir)
                    zipf.write(file_path, arcname)

        # Xóa thư mục tạm sau khi nén xong
        shutil.rmtree(base_tmp_dir)

        msg = f"✅ Hoàn thành phân loại! Khớp thành công: {success_count} file. Thất bại: {fail_count} file."
        return zip_output_path, msg

    except Exception as e:
        return None, f"❌ Đã xảy ra lỗi: {str(e)}"