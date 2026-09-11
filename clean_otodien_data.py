import pandas as pd
import re
import unicodedata
import os
import sys

# Đảm bảo in tiếng Việt trên console Windows không lỗi charmap
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ==========================================
# 1. BỘ QUY TẮC NHẬN DIỆN MODEL & NGƯỠNG GIÁ
# ==========================================
MODEL_RULES = [
    (r'\b(vf\s?e?34)\b', 'VF e34'),
    (r'\b(vf\s?3)\b', 'VF 3'),
    (r'\b(vf\s?5)\b', 'VF 5'),
    (r'\b(vf\s?6)\b', 'VF 6'),
    (r'\b(vf\s?7)\b', 'VF 7'),
    (r'\b(vf\s?8)\b', 'VF 8'),
    (r'\b(vf\s?9)\b', 'VF 9'),
    (r'\b(vf\s?2)\b', 'VF 2'),
    (r'\b(limo\s?green|limo|mpv\s?7|mvp\s?7)\b', 'Limo Green / MPV 7'),
    (r'\b(minio\s?green|minio)\b', 'Minio Green'),
    (r'\b(ec\s?van)\b', 'EC Van'),
]

# Ngưỡng giá phân chia Thuê pin vs Kèm pin (VNĐ)
# Do xe kèm pin luôn đắt hơn xe thuê pin từ 80M - 400M+
PRICE_THRESHOLDS = {
    'VF 2': 230_000_000,               # Thuê pin: ~188M
    'VF 3': 310_000_000,               # Thuê pin: 199M - 296M | Kèm pin: 322M+
    'VF 5': 515_000_000,               # Thuê pin: 320M - 496M | Kèm pin: 540M+
    'VF e34': 520_000_000,             # Thuê pin: 349M - 480M | Kèm pin: 550M+
    'VF 6': 730_000_000,               # Thuê pin: 378M - 700M | Kèm pin: 765M+
    'VF 7': 880_000_000,               # Thuê pin: 595M - 840M | Kèm pin: 999M+
    'VF 8': 1_020_000_000,             # Thuê pin: 570M - 995M | Kèm pin: 1.079 tỷ+
    'VF 9': 1_450_000_000,             # Thuê pin: 799M - 1.395 tỷ | Kèm pin: 1.529 tỷ+
    'Limo Green / MPV 7': 800_000_000, # Thuê pin: 549M - 750M
    'Minio Green': 300_000_000,        # Thuê pin: 175M - 269M
    'EC Van': 350_000_000,             # Thuê pin: 245M
}

def classify_battery(subject_raw, price):
    """
    Phân loại tình trạng pin dựa trên từ khóa và ngưỡng giá benchmark.
    """
    # Chuẩn hóa Unicode (NFKD giúp chuyển các ký tự in đậm, in nghiêng toán học như 𝐕𝐅 𝟑 về VF 3)
    subject = unicodedata.normalize('NFKD', str(subject_raw)).lower()
    
    # Bước 1: Nhận diện từ khóa rõ ràng trong tiêu đề
    no_pin_keywords = ['thuê pin', 'không pin', 'k pin', 'ko pin', 'chưa pin', 'không kèm pin']
    if any(kw in subject for kw in no_pin_keywords):
        return 'Thuê pin'
        
    has_pin_keywords = ['kèm pin', 'bao pin', 'có pin', 'đã mua pin', 'sẵn pin', 'cả pin', 'mua đứt pin', 'mua pin']
    if any(kw in subject for kw in has_pin_keywords):
        return 'Kèm pin'
        
    # Bước 2: Nhận diện Model xe
    model = None
    for pattern, name in MODEL_RULES:
        if re.search(pattern, subject):
            model = name
            break
            
    if not model or pd.isna(price) or price <= 0:
        return 'Cần xác minh'
        
    # Bước 3: So sánh với ngưỡng giá phân tách (Price Threshold Heuristics)
    threshold = PRICE_THRESHOLDS.get(model)
    if threshold:
        return 'Thuê pin' if price < threshold else 'Kèm pin'
        
    return 'Cần xác minh'

def clean_otodien_dataset(csv_path="data/raw/otodien_raw.csv"):
    if not os.path.exists(csv_path):
        print(f"[X] Không tìm thấy file: {csv_path}")
        return
        
    print(f"[*] Đang xử lý file: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"[+] Số dòng hiện tại: {len(df)}")
    
    # Tạo bản backup nếu chưa có
    backup_path = csv_path.replace(".csv", "_backup.csv")
    if not os.path.exists(backup_path):
        df.to_csv(backup_path, index=False, encoding='utf-8-sig')
        print(f"[+] Đã tạo backup tại: {backup_path}")
        
    # Cập nhật cột battery_status
    df['battery_status'] = df.apply(
        lambda r: classify_battery(r['subject'], r['price_clean']), 
        axis=1
    )
    
    # Lưu lại file
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"[+] Đã ghi đè cập nhật vào: {csv_path}")
    
    print("\n=== THỐNG KÊ KẾT QUẢ PHÂN LOẠI PIN ===")
    print(df['battery_status'].value_counts())
    
    print("\n--- XEM TRƯỚC 10 DÒNG TIÊU BIỂU ---")
    print(df[['subject', 'price_raw', 'battery_status']].head(10).to_string())

if __name__ == "__main__":
    clean_otodien_dataset()
