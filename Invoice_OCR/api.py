import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from batch_pdf_pipeline import BatchPDFInvoiceProcessor

app = FastAPI()


@app.post("/process_pdfs/")
async def process_pdfs(files: list[UploadFile] = File(...)):
    # Tạo thư mục tạm để lưu file PDF
    temp_dir = "temp_api_upload"
    os.makedirs(temp_dir, exist_ok=True)
    pdf_paths = []
    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        pdf_paths.append(file_path)

    # Tạo processor và xử lý
    processor = BatchPDFInvoiceProcessor(
        yolo_model_path="v1.pt", use_easyocr=False)
    output_excel = "api_invoice_results.xlsx"
    processor.process_directory(temp_dir, output_excel)

    # Xóa thư mục tạm
    shutil.rmtree(temp_dir)

    # Trả về file excel
    return FileResponse(output_excel, filename=output_excel)
