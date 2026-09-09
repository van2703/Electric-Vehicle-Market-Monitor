import pandas as pd
import json
import re
import os

# ==========================================
# MODULE 1: LEGAL & ANONYMIZER (PDPD)
# ==========================================
def anonymize_text(text):
    if not isinstance(text, str):
        return text
    
    # 1. Che số nhà, ngõ ngách (VD: "389 Đội Cấn", "Số 12 ngõ 4")
    # Thay thế các cụm số đứng trước các từ chỉ đường phố thành "***"
    address_pattern = r'\b(\d+)\s+(đội cấn|ngõ|ngách|hẻm|đường|phố|quận|phường)\b'
    text = re.sub(address_pattern, r'*** \2', text, flags=re.IGNORECASE)
    
    # 2. Đảm bảo che các SĐT còn sót lại (nếu hệ thống Chợ Tốt bỏ sót)
    phone_pattern = r'\b(0[3|5|7|8|9])+([0-9]{8})\b'
    text = re.sub(phone_pattern, r'\1***', text)
    
    return text

# ==========================================
# MODULE 2: NORMALIZATION (BÓC TÁCH PIN)
# ==========================================
def extract_battery_status(text):
    if not isinstance(text, str):
        return "Không rõ"
    
    text_lower = text.lower()
    
    # Keyword nhận diện xe KHÔNG PIN (Thuê pin)
    no_battery_keywords = ['thuê pin', 'không kèm pin', 'không pin', 'k pin', 'ko pin', 'chưa pin']
    if any(kw in text_lower for kw in no_battery_keywords):
        return "Thuê pin"
        
    # Keyword nhận diện xe KÈM PIN (Bao pin)
    with_battery_keywords = ['kèm pin', 'bao pin', 'có pin', 'đã mua pin', 'sẵn pin', 'cả pin', 'zin']
    if any(kw in text_lower for kw in with_battery_keywords):
        return "Kèm pin"
        
    # Nếu không nhắc đến, mặc định tạm xếp vào nhóm nghi vấn để EDA
    return "Cần xác minh"

# ==========================================
# PIPELINE CHÍNH (DATA TRANSFORMATION)
# ==========================================
def process_raw_data(input_path, output_path):
    print(f"[*] Đang đọc dữ liệu từ: {input_path}")
    
    # 1. Đọc file JSON raw
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Chuyển đổi thành Pandas DataFrame
    df = pd.DataFrame(data)
    
    # 2. Chỉ giữ lại các cột quan trọng
    cols_to_keep = ['list_id', 'subject', 'price', 'body', 'regdate', 'mileage_v2', 'region_name', 'area_name']

    df = df[[c for c in cols_to_keep if c in df.columns]]
    
    print("[*] Đang thực thi Legal Anonymization (Che thông tin)...")
    df['body_clean'] = df['body'].apply(anonymize_text)
    
    print("[*] Đang thực thi Price Normalization (Bóc tách Pin)...")

    df['full_text'] = df['subject'] + " " + df['body_clean']
    df['battery_status'] = df['full_text'].apply(extract_battery_status)
    
    df = df.drop(columns=['full_text'])
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"[+] Hoàn tất! File sạch đã lưu tại: {output_path}")
    print(df[['subject', 'price', 'battery_status']].head())

if __name__ == "__main__":
    INPUT_FILE = "data/raw/ev_raw.json"  
    OUTPUT_FILE = "data/processed/ev_market_cleaned.csv"
    
    process_raw_data(INPUT_FILE, OUTPUT_FILE)