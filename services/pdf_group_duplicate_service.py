import os
import re
import shutil
import tempfile
import zipfile
from collections import defaultdict


def get_base_name(filename):

    name = os.path.splitext(
        filename
    )[0]

    # ABC_1
    match = re.match(
        r"^(.*?)_(\d{1,3})$",
        name
    )

    if match:

        return match.group(1)

    # ABC(1)
    match = re.match(
        r"^(.*?)\((\d{1,3})\)$",
        name
    )

    if match:

        return match.group(1)

    return name


def run_group_duplicate_files(
    uploaded_files
):

    try:

        output_root = os.path.join(
            tempfile.gettempdir(),
            "group_duplicate_result"
        )

        if os.path.exists(
            output_root
        ):

            shutil.rmtree(
                output_root
            )

        os.makedirs(
            output_root,
            exist_ok=True
        )

        groups = defaultdict(
            list
        )

        # =====================
        # PHÂN NHÓM
        # =====================

        for file in uploaded_files:

            base_name = get_base_name(
                file.name
            )

            groups[
                base_name
            ].append(
                file
            )

        largest_group = ""
        largest_count = 0

        total_files = 0

        # =====================
        # TẠO THƯ MỤC
        # =====================

        for group_name, files in groups.items():

            folder_path = os.path.join(
                output_root,
                group_name
            )

            os.makedirs(
                folder_path,
                exist_ok=True
            )

            count = 0

            for file in files:

                save_path = os.path.join(
                    folder_path,
                    file.name
                )

                with open(
                    save_path,
                    "wb"
                ) as f:

                    f.write(
                        file.getvalue()
                    )

                count += 1
                total_files += 1

            if count > largest_count:

                largest_count = count
                largest_group = group_name

        # =====================
        # ZIP
        # =====================

        zip_path = os.path.join(
            tempfile.gettempdir(),
            "HoSo_Gom.zip"
        )

        if os.path.exists(
            zip_path
        ):

            os.remove(
                zip_path
            )

        with zipfile.ZipFile(
            zip_path,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for root, dirs, files in os.walk(
                output_root
            ):

                for file in files:

                    full_path = os.path.join(
                        root,
                        file
                    )

                    arcname = os.path.relpath(
                        full_path,
                        output_root
                    )

                    zipf.write(
                        full_path,
                        arcname
                    )

        stats = {

            "total_groups": len(
                groups
            ),

            "total_files": total_files,

            "largest_group": largest_group,

            "largest_count": largest_count

        }

        return (
            zip_path,
            stats,
            "OK"
        )

    except Exception as e:

        return (
            None,
            None,
            str(e)
        )