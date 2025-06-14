import streamlit as st
from PyPDF2 import PdfMerger
from PIL import Image
import tempfile
import os
from pathlib import Path
import io

st.set_page_config(page_title="PDF & Image Merger", page_icon="📄", layout="centered", initial_sidebar_state="auto")

st.title("📄 PDF & Image Merger")

mode = st.radio("Select Mode", ["Merge PDFs", "Merge Images (convert to PDF)"])

uploaded_files = st.file_uploader(
    "Upload files",
    type=["pdf"] if mode == "Merge PDFs" else ["png", "jpg", "jpeg", "bmp", "tiff"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info("Drag and drop to arrange the order of files for merging.")
    file_names = [f.name for f in uploaded_files]

    # Display small icon/thumbnail for images
    if mode == "Merge Images (convert to PDF)":
        st.write("Preview of uploaded images:")
        cols = st.columns(len(uploaded_files))
        for idx, file in enumerate(uploaded_files):
            try:
                img = Image.open(file)
                cols[idx].image(img, width=60, caption=file.name)
                file.seek(0)  # Reset file pointer for later use
            except Exception:
                cols[idx].warning("Not an image")
                file.seek(0)

    order = st.multiselect(
        "Arrange files (top = first page)",
        options=file_names,
        default=file_names,
        key="arrange"
    )
    # Maintain order as per selection
    ordered_files = [next(f for f in uploaded_files if f.name == name) for name in order]

    output_name = st.text_input("Output file name (without extension)", value="merged")
    
    if st.button("Process"):
        if not order:
            st.error("Please arrange at least one file.")
        else:
            with st.spinner("Processing..."):
                output_buffer = io.BytesIO()
                if mode == "Merge PDFs":
                    merger = PdfMerger()
                    for file in ordered_files:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                            tmp.write(file.read())
                            tmp.flush()
                            merger.append(tmp.name)
                    merger.write(output_buffer)
                    merger.close()
                else:
                    images = []
                    for file in ordered_files:
                        img = Image.open(file).convert("RGB")
                        images.append(img)
                    images[0].save(
                        output_buffer,
                        format="PDF",
                        save_all=True,
                        append_images=images[1:]
                    )
                output_buffer.seek(0)
            st.success("Ready to download!")
            st.download_button("Download merged PDF", output_buffer, file_name=output_name + ".pdf", mime="application/pdf")