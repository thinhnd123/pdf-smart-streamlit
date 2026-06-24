import pandas as pd
import tempfile
import os
import re


def normalize_phone(phone):

    if pd.isna(phone):
        return ""

    phone = str(phone)

    phone = re.sub(
        r"\s+",
        "",
        phone
    )

    phone = phone.replace(
        ".0",
        ""
    )

    if phone.startswith("+84"):
        phone = "0" + phone[3:]

    elif phone.startswith("84"):
        phone = "0" + phone[2:]

    return phone


def normalize_name(name):

    if pd.isna(name):
        return ""

    return str(name).strip().title()


def validate_email(email):

    if pd.isna(email):
        return False

    pattern = (
        r"^[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}$"
    )

    return bool(
        re.match(
            pattern,
            str(email)
        )
    )


def normalize_text(text):

    if pd.isna(text):
        return ""

    return (
        str(text)
        .strip()
        .replace("\n", " ")
        .replace("\t", " ")
    )


def run_excel_cleaner(
    excel_path,
    phone_col=None,
    email_col=None,
    name_col=None,
    gcn_col=None,
    maql_col=None,
    serial_col=None,
    model_col=None
):

    try:

        df = pd.read_excel(
            excel_path,
            dtype=str
        )

        df_before = df.copy()

        stats = {
            "phones": 0,
            "names": 0,
            "duplicates": 0,
            "email_errors": 0,
            "gcn_duplicates": 0,
            "maql_duplicates": 0,
            "serial_duplicates": 0,
            "model_duplicates": 0
        }

        # ======================
        # Trim toàn bộ
        # ======================

        for col in df.columns:

            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
            )

        # ======================
        # Phone
        # ======================

        if phone_col:

            old = df[phone_col].copy()

            df[phone_col] = df[
                phone_col
            ].apply(
                normalize_phone
            )

            stats["phones"] = (
                old != df[phone_col]
            ).sum()

        # ======================
        # Name
        # ======================

        if name_col:

            old = df[name_col].copy()

            df[name_col] = df[
                name_col
            ].apply(
                normalize_name
            )

            stats["names"] = (
                old != df[name_col]
            ).sum()

        # ======================
        # Email
        # ======================

        invalid_email = pd.DataFrame()

        if email_col:

            invalid_email = df[
                ~df[email_col]
                .apply(validate_email)
            ]

            stats["email_errors"] = (
                len(invalid_email)
            )

        # ======================
        # Remove duplicate phone
        # ======================

        if phone_col:

            before = len(df)

            df = df.drop_duplicates(
                subset=[phone_col]
            )

            stats["duplicates"] = (
                before - len(df)
            )

        # ======================
        # GCN duplicate
        # ======================

        gcn_dup = pd.DataFrame()

        if gcn_col:

            gcn_dup = df[
                df[gcn_col]
                .duplicated(
                    keep=False
                )
            ]

            stats["gcn_duplicates"] = (
                len(gcn_dup)
            )

        # ======================
        # Mã quản lý duplicate
        # ======================

        maql_dup = pd.DataFrame()

        if maql_col:

            maql_dup = df[
                df[maql_col]
                .duplicated(
                    keep=False
                )
            ]

            stats["maql_duplicates"] = (
                len(maql_dup)
            )

        # ======================
        # Serial duplicate
        # ======================

        serial_dup = pd.DataFrame()

        if serial_col:

            serial_dup = df[
                df[serial_col]
                .duplicated(
                    keep=False
                )
            ]

            stats["serial_duplicates"] = (
                len(serial_dup)
            )

        # ======================
        # Model duplicate
        # ======================

        model_dup = pd.DataFrame()

        if model_col:

            model_dup = df[
                df[model_col]
                .duplicated(
                    keep=False
                )
            ]

            stats["model_duplicates"] = (
                len(model_dup)
            )

        output_file = os.path.join(
            tempfile.gettempdir(),
            "Excel_Cleaned.xlsx"
        )

        with pd.ExcelWriter(
            output_file,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False,
                sheet_name="Cleaned"
            )

            invalid_email.to_excel(
                writer,
                index=False,
                sheet_name="Email_Error"
            )

            gcn_dup.to_excel(
                writer,
                index=False,
                sheet_name="GCN_Duplicate"
            )

            maql_dup.to_excel(
                writer,
                index=False,
                sheet_name="MaQL_Duplicate"
            )

            serial_dup.to_excel(
                writer,
                index=False,
                sheet_name="Serial_Duplicate"
            )

            model_dup.to_excel(
                writer,
                index=False,
                sheet_name="Model_Duplicate"
            )

        return (
            output_file,
            df.head(100),
            stats,
            "✅ Làm sạch dữ liệu thành công"
        )

    except Exception as e:

        return (
            None,
            None,
            None,
            str(e)
        )