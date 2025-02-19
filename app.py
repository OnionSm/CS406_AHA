import sys
import os
sys.path.append(os.path.abspath("../"))
import streamlit as st
from PIL import Image
import cv2
import numpy as np
from ultralytics import YOLO
from common import CV2ImageLuminanceSource
from common import HybridBinarizer
from qrcode import BinaryBitmap
from qrcode import QRCodeReader, BitMatrix
import random
from typing import List
import math
from pyzbar.pyzbar import decode

# Hàm load model YOLO với caching
@st.cache_resource
def load_model(model_path):
    return YOLO(model_path)

def localization_image(img):
    model_path = "models\\best2.pt"
    model = load_model(model_path)
    results = model.predict(source=img, conf=0.8, save=False, device='cpu')

    detected_images = [] 
    cropped_images = []  

    if len(results) > 0 and len(results[0].boxes) > 0:
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0]  
            img_crop = img[int(y1):int(y2), int(x1):int(x2)]  
            cropped_images.append(img_crop) 
         
            detected_images.append(results[0].plot())  
            
        return detected_images, cropped_images
    else:
        print("No object detected in the image.")
        return [img], [] 
    

def binarizer_img(img):
    C = 15
    mean_filter = cv2.boxFilter(img, ddepth=-1, ksize=(50,50))
    threshold = mean_filter - C
    binary_img = np.where(img> threshold, 255, 0).astype(np.uint8)
    return binary_img

def crop_image(image, results):
    for result in results:
        if len(result.boxes) > 0:
            best_box = sorted(result.boxes, key=lambda box: box.conf[0], reverse=True)[0]
            x_min, y_min, x_max, y_max = map(int, best_box.xyxy[0])
            return cv2.cvtColor(image[y_min:y_max, x_min:x_max], cv2.COLOR_BGR2RGB)
    print("No bounding box detected.")
    return None

def connect_component(binary_img):
    width = binary_img.shape[1]
    height = binary_img.shape[0]
    print(width, height)
    min_area = (8 / 177**2) * (width * height)
    max_area = (25 / 21**2) * (width * height)
    
    black_mask = (binary_img == 0).astype(np.uint8)
    num_labels, labels = cv2.connectedComponents(black_mask, connectivity=8)  # Liên thông 8 hướng

    output_image = np.ones((binary_img.shape[0], binary_img.shape[1]), dtype=np.uint8) * 255  # Màu nền là trắng

    filtered_centroids = []
    filtered_moments = []
    bounding_box = []
    list_index = []

    for label in np.unique(labels):
        if label == 0: 
            continue

        color = np.random.randint(0, 256, size=(1,), dtype=np.uint8)  
        output_image[labels == label] = color
        mask = (labels == label).astype(np.uint8)
        moments = cv2.moments(mask)

        if moments['m00'] >= min_area and moments['m00'] <= max_area:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
            x, y, w, h = cv2.boundingRect(mask)
            aspect_ratio = w / h
            if 0.6 <= aspect_ratio <= 1.7:
                list_index.append(label)
                bounding_box.append([x, y, w, h])
                filtered_moments.append(moments)
                filtered_centroids.append([cx, cy])
                cv2.circle(output_image, (cx, cy), 2, random.randint(0, 255), -1) 
                cv2.rectangle(output_image, (x, y), (x + w, y + h), 0, 1) 
            else:
                print(f"Thành phần {label} bị loại vì tỷ lệ khung hình Aspect Ratio = {aspect_ratio:.2f}")
        else:
            print(f"Không thể tính centroid cho thành phần {label} vì m00 < 20")
    print("LEN CENTROID ", len(filtered_centroids))
    return filtered_moments, filtered_centroids, bounding_box


def sort_connected_component(filtered_moments, filtered_centroids, bounding_box):
    combined = list(zip(filtered_moments, filtered_centroids, bounding_box))
    sorted_combined = sorted(combined, key=lambda x: x[0]['m00'], reverse=False)
 
    moments_list, centroids_list, bounding_box_list = zip(*sorted_combined)
    return moments_list, centroids_list, bounding_box_list

def is_within_bounding_box(ra, rc):
    ra_left = ra[0]
    ra_right = ra[0] + ra[2]
    ra_top = ra[1] 
    ra_bottom = ra[1] + ra[3] 

    rc_left = rc[0]
    rc_right = rc[0] + rc[2]
    rc_top = rc[1] 
    rc_bottom = rc[1] + rc[3] 
    
    res =  (ra_left >= rc_left and ra_right <= rc_right 
            and ra_top >= rc_top and ra_bottom <= rc_bottom)
    return res

def find_similar_centroids(centroids, areas, bounding_box, img,  centroid_tolerance=3, area_ratio_threshold=4):
    """Tìm các cặp vùng có centroid gần nhau và kiểm tra các điều kiện diện tích."""
    width = img.shape[1]
    height = img.shape[0]
    min_dis_centroid = (3 / 177 ** 2) * width * height
    max_dis_centroid = (3 / 21 ** 2) * width * height
    regions = []
    for i in range(len(centroids)):
        for j in range(i + 1, len(centroids)):
            centroid_ra = centroids[i]
            centroid_rc = centroids[j]
            area_ra = areas[i]["m00"]
            area_rc = areas[j]["m00"]
            if area_rc > area_ra and (area_rc / area_ra) <= area_ratio_threshold and (area_rc / area_ra) >= 1.333:
                dist_centroid = np.sqrt((centroid_rc[0] - centroid_ra[0]) ** 2 + (centroid_rc[1] - centroid_ra[1]) ** 2)
                # if dist_centroid >= min_dis_centroid and dist_centroid <= max_dis_centroid:
                bounding_box_ra = bounding_box[i]
                bounding_box_rc = bounding_box[j]
                if is_within_bounding_box(bounding_box_ra, bounding_box_rc):
                    regions.append([i, j]) 
    return regions
          

def handle_img(img_crop, solution_type):
    if solution_type == "Solution 1":
        return handle_img_solution_1(img_crop)
    elif solution_type == "Solution 2":
        return handle_img_solution_2(img_crop)

def handle_img_solution_1(img_crop):
    result = {}
    source = CV2ImageLuminanceSource(img_crop)
    binarizer:HybridBinarizer = HybridBinarizer(source)
    bitmap = BinaryBitmap(binarizer)
    binary_img = bitmap.get_black_matrix().bitmatrix_to_image()
    binary_img = binary_img * 255
    result["binary_image"] = binary_img 
    reader = QRCodeReader()
    res = reader.decode(bitmap)
    if res is not None and res.get_bits() is not None:
        img_result = res.bits.bitmatrix_to_image()
        high_res_img = cv2.resize(img_result, None, fx=100, fy=100, interpolation=cv2.INTER_AREA)
        high_res_img = high_res_img * 255
        result["qr_code"] = high_res_img
        decoded_objects = decode(high_res_img)

        for obj in decoded_objects:
            result["data"] = obj.data.decode("utf-8")
    return result

def handle_img_solution_2(img):
    result = {}
    from common import CV2ImageLuminanceSource
    source = CV2ImageLuminanceSource(img)
    from common import HybridBinarizer
    binarizer = HybridBinarizer(source)
    from qrcode import BinaryBitmap
    bitmap = BinaryBitmap(binarizer)
    binary_img = bitmap.get_black_matrix().bitmatrix_to_image()
    result["binary_image"] = binary_img * 255

    filtered_moments, filtered_centroids, bounding_box = connect_component(binary_img)
    moments_list, centroids_list, bounding_box_list = sort_connected_component(filtered_moments, filtered_centroids, bounding_box)
    found_regions = find_similar_centroids(centroids_list, moments_list, bounding_box_list, img)[:3]
    from qr_patterns import FinderPattern
    pattern_info: List[FinderPattern] = []
    for item in found_regions:
        ra = moments_list[item[0]]
        rc = moments_list[item[1]]
        dividor = ra["m00"] + rc["m00"]
        C_x = int((ra["m10"] +  rc["m10"]) / dividor)
        C_y = int((ra["m01"] + rc["m01"]) / dividor)
        mw = ((ra["m00"] + rc["m00"]) / 33)**0.5
        finder_pattern = FinderPattern(C_x, C_y, mw)
        pattern_info.append(finder_pattern)
        print(f"Centroid {(C_x, C_y)} , Module Estimate {mw}")

    from qr_patterns import ResultPoint, FinderPatternInfo, DetectorResult
    if len(pattern_info) == 3:
        ResultPoint.order_best_patterns(pattern_info)
        finder_pattern_info: FinderPatternInfo = FinderPatternInfo(pattern_info)
        
        top_left = finder_pattern_info.get_top_left()
        top_right = finder_pattern_info.get_top_right()
        bottom_left = finder_pattern_info.get_bottom_left()

        print(top_left.get_x(), top_left.get_y())
        print(top_right.get_x(),top_right.get_y())
        print(bottom_left.get_x(), bottom_left.get_y())
        reader = QRCodeReader()
        res = reader.decode2(bitmap ,finder_pattern_info)
        if res is not None:
            if res.get_bits() is not None:
                img_result = res.get_bits().bitmatrix_to_image()
                high_res_img = cv2.resize(img_result, None, fx=100, fy=100, interpolation=cv2.INTER_AREA)
                high_res_img = high_res_img * 255
                result["qr_code"] = high_res_img
                decoded_objects = decode(high_res_img)

                for obj in decoded_objects:
                    result["data"] = obj.data.decode("utf-8")
    return result


def scale_image(image):
    width = image.shape[1]  
    height = image.shape[0]  

    if height > 1024 or width > 1024:
        scale = 1024 / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        image = cv2.resize(image, (new_width, new_height))
        return image
    return image

st.markdown(
    """
    <style>
    .main {
        max-width: 1200px; /* Tăng chiều rộng trang */
        margin: auto;     /* Căn giữa nội dung */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("QR Decoder")

options = ["Solution 1", "Solution 2"]

selected_option = st.selectbox("Chọn phương pháp detect", options)

st.caption("""
**Solution 1** sử dụng các nguyên lý cơ bản của **QRCode**, 
áp dụng công thức **1:1:3:1:1** để phát hiện **Finder Pattern** 🧩
""")
st.caption("""
**Solution 2** áp dụng phương pháp **tìm miền liên thông** 
để phát hiện **Finder Pattern** 🔍
""")

# Tải lên nhiều file ảnh
uploaded_files = st.file_uploader("Chọn một hoặc nhiều file ảnh", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Mở từng ảnh
        image = Image.open(uploaded_file)

        st.image(image, caption=f"Ảnh đã tải lên: {uploaded_file.name}", width=200)
        st.write(f"Tên file: {uploaded_file.name}")

        # Chuyển đổi ảnh thành numpy array
        image = np.array(image)

        # Kiểm tra nếu ảnh có 4 kênh (RGBA), loại bỏ kênh alpha
        if image.shape[2] == 4: 
            image = image[:, :, :3]  

        # Gọi hàm xử lý ảnh
        detected_images, cropped_images = localization_image(image)
        for row in range(len(cropped_images)):
            res_data = handle_img(cropped_images[row], selected_option)
            
            # Hiển thị ảnh với các kết quả
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.image(detected_images[row], caption="Localization", use_container_width=True)
            col2.image(cropped_images[row], caption="Crop Image", use_container_width=True)
            col3.image(res_data["binary_image"], caption="Binary Image", use_container_width=True)
            
            # Hiển thị QR Code nếu có
            if "qr_code" in res_data and res_data["qr_code"] is not None:
                col4.image(res_data["qr_code"], caption="QR Code", use_container_width=True)
                
                # Hiển thị dữ liệu nếu có
                if "data" in res_data and res_data["data"] is not None:
                    col5.markdown(
                        f'<div style="display: flex; justify-content: center; align-items: center; height: 100%;">'
                        f'<p style="font-size: 20px; color: red; text-align: center;">{res_data["data"]}</p>'
                        '</div>',
                        unsafe_allow_html=True
                    )   
            else:
                col5.write("Không thể nhận dạng QR Code")
else:
    st.write("Chưa có ảnh nào được tải lên.")