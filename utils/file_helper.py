from pathlib import Path
import tempfile


def save_uploaded_file(uploaded_file):

    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:

        tmp.write(uploaded_file.getvalue())

        return tmp.name