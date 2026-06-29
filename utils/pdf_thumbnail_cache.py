import fitz
from PIL import Image
import io
import streamlit as st


@st.cache_data(show_spinner=False)
def get_thumbnail(pdf_bytes, page_num, zoom=0.25):
    doc = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    page = doc.load_page(page_num)

    pix = page.get_pixmap(
        matrix=fitz.Matrix(
            zoom,
            zoom
        )
    )

    img = Image.open(
        io.BytesIO(
            pix.tobytes("png")
        )
    )

    doc.close()

    return img