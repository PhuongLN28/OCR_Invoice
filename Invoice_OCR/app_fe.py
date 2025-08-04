import streamlit as st
import requests
import os
import glob

st.title("Batch Invoice OCR - Upload PDF Folder")

# Chọn thư mục chứa PDF
input_dir = st.text_input("Nhập đường dẫn thư mục chứa các file PDF:")

if input_dir and os.path.isdir(input_dir):
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    st.write(f"Đã tìm thấy {len(pdf_files)} file PDF.")

    if st.button("Xử lý và tải kết quả"):
        files = [("files", (os.path.basename(f), open(f, "rb"),
                  "application/pdf")) for f in pdf_files]
        with st.spinner("Đang xử lý..."):
            response = requests.post(
                "http://localhost:8000/process_pdfs/", files=files)
        if response.status_code == 200:
            st.success("Xử lý thành công!")
            st.download_button(
                label="Tải file Excel kết quả",
                data=response.content,
                file_name="batch_invoice_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Có lỗi xảy ra khi xử lý.")
else:
    st.info("Vui lòng nhập đúng đường dẫn thư mục chứa các file PDF.")
