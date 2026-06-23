from backend.scan_rename_folder import (
    rename_scan_folder
)


def run_scan_rename(
    folder_path,
    excel_path,
    naming_type
):
    return rename_scan_folder(
        folder_path=folder_path,
        excel_path=excel_path,
        naming_type=naming_type
    )