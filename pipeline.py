from ultralytics import YOLO
import cv2
import pytesseract
from PIL import Image
import numpy as np

import pandas as pd

# Đường dẫn đến Tesseract (chỉ cần trên Windows nếu PATH chưa được cấu hình)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Danh sách các trường cần detect
FIELDS = [
    "Customer Name", "Address", "Order Date", "Product Name", "Sub Category", "Category",
    "Product ID", "Quatity", "Unit Cost", "Subtotal", "Discount", "Shipping Fee",
    "Total amount Payble", "Order ID"
]

model = YOLO("v1.pt")
image_path = r"C:\Users\Admin\Documents\xinkGroup\RnD_Demo\Invoice_OCR\img_yolo\invoice_Beth Fritzler_3924_page_1.jpg"
img = cv2.imread(image_path)

# Detect các trường bằng YOLO
results = model(img, conf=0.25, iou=0.75)
boxes = results[0].boxes
names = results[0].names  # class id -> label name

# Gom bbox theo label
label_boxes = {field: [] for field in FIELDS}
for box in boxes:
    class_id = int(box.cls[0])
    label = names[class_id]
    if label in FIELDS:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        label_boxes[label].append((y1, x1, y2, x2))  # lưu cả y1 để sort

# Lưu kết quả
field_results = {}

for field in FIELDS:
    bboxes = label_boxes[field]
    if bboxes:
        # Sắp xếp bbox theo y1 (từ trên xuống)
        bboxes = sorted(bboxes, key=lambda b: b[0])
        texts = []
        for y1, x1, y2, x2 in bboxes:
            crop = img[y1:y2, x1:x2]
            # Chuyển ảnh sang định dạng PIL để Tesseract xử lý
            crop_pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            # Sử dụng Tesseract để đọc text
            ocr_result = pytesseract.image_to_string(
                crop_pil, config='--psm 6').strip()
            if ocr_result:
                texts.append(ocr_result)
        field_results[field] = " ".join(texts) if texts else None
    else:
        field_results[field] = None

# In kết quả
for k, v in field_results.items():
    print(f"{k}: {v}")

# Lưu kết quả vào file CSV và Excel
df = pd.DataFrame([field_results])  # Tạo DataFrame từ dict

df.to_csv("invoice_result.csv", index=False, encoding="utf-8-sig")   # Lưu ra file CSV
df.to_excel("invoice_result.xlsx", index=False)

# Lưu ảnh kết quả (có bounding box)
result_img = results[0].plot()
cv2.imwrite("kq.jpg", result_img)
