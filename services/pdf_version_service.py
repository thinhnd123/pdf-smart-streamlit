import os
import tempfile
import subprocess


def find_ghostscript():

    candidates = [

        r"C:\Program Files\gs",
        r"C:\Program Files (x86)\gs"
    ]

    for base in candidates:

        if not os.path.exists(base):
            continue

        versions = sorted(
            os.listdir(base),
            reverse=True
        )

        for ver in versions:

            exe = os.path.join(
                base,
                ver,
                "bin",
                "gswin64c.exe"
            )

            if os.path.exists(exe):
                return exe

    return "gswin64c"


def run_pdf_version_downgrade(
    pdf_path,
    compatibility="1.4"
):

    try:

        gs_exe = find_ghostscript()

        output_pdf = os.path.join(
            tempfile.gettempdir(),
            f"PDF_v{compatibility.replace('.', '_')}.pdf"
        )

        cmd = [
            gs_exe,
            "-sDEVICE=pdfwrite",
            f"-dCompatibilityLevel={compatibility}",
            "-dNOPAUSE",
            "-dBATCH",
            "-dQUIET",
            f"-sOutputFile={output_pdf}",
            pdf_path
        ]

        subprocess.run(
            cmd,
            check=True
        )

        return (
            output_pdf,
            f"✅ Đã chuyển PDF về phiên bản {compatibility}"
        )

    except Exception as e:

        return None, str(e)