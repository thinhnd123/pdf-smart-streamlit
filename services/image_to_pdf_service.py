from PIL import Image
import tempfile
import os


A4_PORTRAIT = (2480, 3508)
A4_LANDSCAPE = (3508, 2480)

A5_PORTRAIT = (1748, 2480)
A5_LANDSCAPE = (2480, 1748)


def resize_to_page(
    img,
    page_size
):

    page = Image.new(
        "RGB",
        page_size,
        "white"
    )

    img.thumbnail(
        page_size
    )

    x = (
        page_size[0] - img.width
    ) // 2

    y = (
        page_size[1] - img.height
    ) // 2

    page.paste(
        img,
        (x, y)
    )

    return page


def run_image_to_pdf(
    image_paths,
    paper_size="Giữ nguyên",
    orientation="Tự động"
):

    try:

        images = []

        for path in image_paths:

            img = Image.open(path)

            if img.mode != "RGB":

                img = img.convert("RGB")

            # =====================
            # A4 / A5
            # =====================

            if paper_size != "Giữ nguyên":

                if paper_size == "A4":

                    if orientation == "Ngang":

                        size = A4_LANDSCAPE

                    elif orientation == "Dọc":

                        size = A4_PORTRAIT

                    else:

                        if img.width > img.height:

                            size = A4_LANDSCAPE

                        else:

                            size = A4_PORTRAIT

                else:

                    if orientation == "Ngang":

                        size = A5_LANDSCAPE

                    elif orientation == "Dọc":

                        size = A5_PORTRAIT

                    else:

                        if img.width > img.height:

                            size = A5_LANDSCAPE

                        else:

                            size = A5_PORTRAIT

                img = resize_to_page(
                    img,
                    size
                )

            images.append(img)

        output_pdf = os.path.join(
            tempfile.gettempdir(),
            "Images_To_PDF.pdf"
        )

        images[0].save(
            output_pdf,
            save_all=True,
            append_images=images[1:]
        )

        return (
            output_pdf,
            f"✅ Đã tạo PDF từ {len(images)} ảnh"
        )

    except Exception as e:

        return None, str(e)