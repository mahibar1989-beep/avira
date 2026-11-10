import io
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ExifTags

st.set_page_config(page_title="Avira Image Studio", page_icon="🛏️", layout="wide")

st.title("🛏️ Avira Image Studio")
st.caption("Meesho product-photo preparation • Free • Mobile & desktop")

st.info(
    "This tool prepares product images; it does not remove or conceal SynthID/C2PA provenance. "
    "Keep product appearance truthful and compare the result with the real item before listing."
)

with st.sidebar:
    st.header("Export settings")
    max_side = st.selectbox("Maximum image side", [1200, 1600, 2000, 2400, 3000], index=2)
    output_format = st.selectbox("Download format", ["JPEG", "PNG"], index=0)
    jpeg_quality = st.slider("JPEG quality", 75, 100, 92)
    crop_mode = st.selectbox(
        "Image framing",
        ["Keep original ratio", "Square – fit with background", "Square – center crop"],
        index=0
    )
    bg_color = st.color_picker("Background for square fit", "#FFFFFF")
    st.caption("Tip: Keep original ratio unless your marketplace image template requires a square.")

st.subheader("1. Upload product photos")
files = st.file_uploader(
    "Choose one or more bedsheet, clothing or home-product images",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

st.subheader("2. Adjust carefully")
c1, c2, c3 = st.columns(3)
with c1:
    brightness = st.slider("Brightness", 0.90, 1.10, 1.00, 0.01)
with c2:
    contrast = st.slider("Contrast", 0.90, 1.10, 1.00, 0.01)
with c3:
    sharpness = st.slider("Sharpness", 0.90, 1.15, 1.00, 0.01)

st.caption("All adjustments default to 1.00 (unchanged). Avoid changing colour/contrast if it makes the fabric differ from the actual product.")

def hex_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))

def process_image(im):
    im = ImageOps.exif_transpose(im).convert("RGB")
    if brightness != 1.0:
        im = ImageEnhance.Brightness(im).enhance(brightness)
    if contrast != 1.0:
        im = ImageEnhance.Contrast(im).enhance(contrast)
    if sharpness != 1.0:
        im = ImageEnhance.Sharpness(im).enhance(sharpness)

    if crop_mode == "Square – fit with background":
        side = max(im.size)
        canvas = Image.new("RGB", (side, side), hex_rgb(bg_color))
        canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
        im = canvas
    elif crop_mode == "Square – center crop":
        w, h = im.size
        side = min(w, h)
        left = (w - side) // 2
        top = (h - side) // 2
        im = im.crop((left, top, left + side, top + side))

    im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return im

def basic_metadata(uploaded_file, image):
    result = {
        "Filename": uploaded_file.name,
        "File type": uploaded_file.type or "Unknown",
        "File size (KB)": round(uploaded_file.size / 1024, 1),
        "Dimensions": f"{image.width} × {image.height}",
        "EXIF fields found": 0,
    }
    try:
        exif = image.getexif()
        result["EXIF fields found"] = len(exif)
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, str(tag_id))
            if tag in ("DateTime", "Make", "Model", "Software", "Orientation"):
                result[f"EXIF: {tag}"] = str(value)[:160]
    except Exception:
        pass
    # A basic text scan can flag possible C2PA markers but cannot verify a manifest.
    try:
        raw = uploaded_file.getvalue()
        markers = [m for m in (b"c2pa", b"content credentials", b"jumb") if m in raw.lower()]
        result["Possible C2PA marker (basic scan)"] = "Found" if markers else "Not found in basic scan"
    except Exception:
        result["Possible C2PA marker (basic scan)"] = "Unable to scan"
    result["SynthID status"] = "Not detectable by this tool"
    return result

if files:
    st.subheader("3. Preview and inspect")
    previews = st.columns(2)
    processed_items = []
    for idx, uploaded in enumerate(files):
        try:
            uploaded.seek(0)
            original = Image.open(uploaded)
            metadata = basic_metadata(uploaded, original)
            original_for_preview = ImageOps.exif_transpose(original).convert("RGB")
            output = process_image(original.copy())

            with st.container(border=True):
                st.markdown(f"**{idx+1}. {uploaded.name}**")
                left, right = st.columns(2)
                with left:
                    st.image(original_for_preview, caption=f"Original · {original_for_preview.width}×{original_for_preview.height}", use_container_width=True)
                with right:
                    st.image(output, caption=f"Prepared · {output.width}×{output.height}", use_container_width=True)
                with st.expander("Basic file information / metadata"):
                    st.json(metadata)
                    st.caption(
                        "This is only a basic metadata inspection. 'Not found' does not prove that C2PA is absent, "
                        "and this app cannot detect or verify SynthID."
                    )

            buf = io.BytesIO()
            if output_format == "JPEG":
                output.save(buf, format="JPEG", quality=jpeg_quality, optimize=True)
                suffix = ".jpg"
            else:
                output.save(buf, format="PNG", optimize=True)
                suffix = ".png"
            processed_items.append((Path(uploaded.name).stem + "_avira" + suffix, buf.getvalue()))
        except Exception as exc:
            st.error(f"Could not process {uploaded.name}: {exc}")

    if processed_items:
        st.subheader("4. Download")
        if len(processed_items) == 1:
            name, data = processed_items[0]
            st.download_button(
                f"⬇️ Download {name}", data=data, file_name=name,
                mime="image/jpeg" if name.endswith(".jpg") else "image/png",
                use_container_width=True
            )
        else:
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for name, data in processed_items:
                    zf.writestr(name, data)
            st.download_button(
                "⬇️ Download all photos (ZIP)", data=zip_buf.getvalue(),
                file_name="avira_meesho_photos.zip", mime="application/zip",
                use_container_width=True
            )
else:
    st.markdown(
        """
        **Suggested workflow**
        1. Upload your original product photos.
        2. Keep brightness, contrast and sharpness at 1.00 initially.
        3. Choose original ratio or square framing as needed.
        4. Compare the prepared image against the actual bedsheet/garment.
        5. Download the result and check it on your phone before listing.
        """
    )

st.divider()
st.caption("Avira Image Studio • Images are processed in this app session. Avoid uploading private or sensitive photos.")
