from PIL import Image
import tempfile
import os


def run_image_to_pdf(
    image_paths
):

    try:

        images = []

        for path in image_paths:

            img = Image.open(path)

            if img.mode != "RGB":

                img = img.convert("RGB")

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