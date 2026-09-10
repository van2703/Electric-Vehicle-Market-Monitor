import pandas as pd
import json
import re
import os
import sys

# Đảm bảo console Windows in tiếng Việt UTF-8 không lỗi charmap
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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
# MODULE 3: BRAND & MODEL RECOGNITION
# ==========================================
MODEL_PATTERNS = [
    (r'\b(vf\s?e?34)\b', 'VinFast', 'VF e34'),
    (r'\b(vf\s?3)\b', 'VinFast', 'VF 3'),
    (r'\b(vf\s?5)\b', 'VinFast', 'VF 5'),
    (r'\b(vf\s?6)\b', 'VinFast', 'VF 6'),
    (r'\b(vf\s?7)\b', 'VinFast', 'VF 7'),
    (r'\b(vf\s?8)\b', 'VinFast', 'VF 8'),
    (r'\b(vf\s?9)\b', 'VinFast', 'VF 9'),
    (r'\b(limo\s?green)\b', 'VinFast', 'Limo Green'),
    (r'\b(byd\s?seal|seal\s?ev)\b', 'BYD', 'Seal'),
    (r'\b(evo\s?200|evo200)\b', 'VinFast', 'Evo 200'),
    (r'\b(feliz\s?s?)\b', 'VinFast', 'Feliz'),
    (r'\b(klara\s?s?|klara\s?a2|klara\s?a1)\b', 'VinFast', 'Klara'),
    (r'\b(theon\s?s?)\b', 'VinFast', 'Theon'),
    (r'\b(vento\s?s?)\b', 'VinFast', 'Vento'),
    (r'\b(ludo)\b', 'VinFast', 'Ludo'),
    (r'\b(quantum\s?s?)\b', 'Dat Bike', 'Quantum'),
    (r'\b(weaver\s?\+\+|weaver\s?200|weaver)\b', 'Dat Bike', 'Dat Bike (Khác)'),
    (r'\b(yadea\s?voltguard|voltguard)\b', 'Yadea', 'Voltguard'),
    (r'\b(yadea\s?orla|orla)\b', 'Yadea', 'Orla'),
    (r'\b(yadea\s?ossy|ossy)\b', 'Yadea', 'Ossy'),
    (r'\b(yadea\s?osta|osta)\b', 'Yadea', 'Osta'),
    (r'\b(yadea\s?ocean|ocean)\b', 'Yadea', 'Ocean'),
    (r'\byadea\b', 'Yadea', 'Yadea (Khác)'),
    (r'\b(dibao\s?pansy|pansy)\b', 'Dibao', 'Pansy'),
    (r'\b(dibao\s?gogo|gogo)\b', 'Dibao', 'Gogo'),
    (r'\b(dibao\s?creer|creer)\b', 'Dibao', 'Creer'),
    (r'\b(dibao\s?tesla|tesla\s?chic|tesla\s?dio|tesla\s?e|tesla\s?g)\b', 'Dibao', 'Tesla'),
    (r'\b(dibao\s?xman|dibao\s?xmen|xman\s?neo|xmen\s?neo)\b', 'Dibao', 'Xman'),
    (r'\b(dibao\s?ls007|ls007)\b', 'Dibao', 'LS007'),
    (r'\b(dibao\s?shine|shine)\b', 'Dibao', 'Shine'),
    (r'\b(osakar\s?momo|momo)\b', 'Osakar', 'Momo'),
    (r'\b(osakar\s?nispa|nispa)\b', 'Osakar', 'Nispa'),
    (r'\b(espero\s?velia|velia)\b', 'Espero', 'Velia'),
    (r'\b(daelim\s?nova|nova\s?revo|nova\s?luna)\b', 'Daelim', 'Nova'),
    (r'\b(tailg\s?t72|tailg\s?t61|tailg\s?r60|tailg\s?t71|tailg\s?venus)\b', 'Tailg', 'Tailg Series'),
]

def extract_brand_and_model(title):
    title_lower = str(title).lower()
    for pattern, brand, model in MODEL_PATTERNS:
        if re.search(pattern, title_lower):
            return brand, model
    return "Khác", "Không phân loại"

# ==========================================
# PIPELINE CHÍNH (DATA TRANSFORMATION)
# ==========================================
def process_raw_data(input_path, output_path, timeline_benchmark_path="data/raw/ev_benchmark_timeline.csv"):
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

    # 3. Phân loại Brand & Model từ tiêu đề
    print("[*] Đang nhận diện Hãng & Dòng xe...")
    brand_model = df['subject'].apply(extract_brand_and_model)
    df['brand'] = [b for b, m in brand_model]
    df['model'] = [m for b, m in brand_model]

    # 4. Ánh xạ Benchmark 2 Dimensions (Brand-Model x Timeline regdate)
    if os.path.exists(timeline_benchmark_path):
        print(f"[*] Đang ánh xạ Benchmark Timeline từ: {timeline_benchmark_path}")
        df_bench = pd.read_csv(timeline_benchmark_path)
        
        # Tạo lookup dictionary: (Brand, Model, Year) -> Price_Benchmark
        lookup_timeline = {}
        lookup_fallback = {} # Fallback về giá mới nhất nếu năm không khớp
        
        for _, row in df_bench.iterrows():
            key = (str(row['Brand']).strip().lower(), str(row['Model']).strip().lower(), int(row['Year']))
            lookup_timeline[key] = row['Price_Benchmark']
            
            fb_key = (str(row['Brand']).strip().lower(), str(row['Model']).strip().lower())
            lookup_fallback[fb_key] = row['Price_Benchmark']

        def map_benchmark(row):
            b = str(row['brand']).strip().lower()
            m = str(row['model']).strip().lower()
            y = row.get('regdate')
            try:
                y = int(y)
                # Tìm đúng năm đăng ký
                if (b, m, y) in lookup_timeline:
                    return lookup_timeline[(b, m, y)]
            except:
                pass
            # Fallback về giá niêm yết mới nhất
            return lookup_fallback.get((b, m), None)

        df['benchmark_msrp'] = df.apply(map_benchmark, axis=1)

        # Tính tỷ lệ khấu hao (% so với giá niêm yết cùng năm)
        def calc_depreciation(row):
            msrp = row.get('benchmark_msrp')
            cur_price = row.get('price')
            if msrp and cur_price and msrp > 0:
                return round((1 - cur_price / msrp) * 100, 1)
            return None

        df['depreciation_pct'] = df.apply(calc_depreciation, axis=1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"[+] Hoàn tất! File sạch đã lưu tại: {output_path}")
    print("\n--- XEM TRƯỚC 5 DÒNG DỮ LIỆU ĐÃ LÀM SẠCH VÀ TÍNH KHẤU HAO ---")
    cols_preview = [c for c in ['subject', 'brand', 'model', 'regdate', 'price', 'benchmark_msrp', 'depreciation_pct', 'battery_status'] if c in df.columns]
    print(df[cols_preview].head())

if __name__ == "__main__":
    INPUT_FILE = "data/raw/ev_raw.json"  
    OUTPUT_FILE = "data/processed/ev_market_cleaned.csv"
    
    # Nếu file ev_raw.json chưa có thì thử chotot_xemay_raw.json
    if not os.path.exists(INPUT_FILE) and os.path.exists("data/raw/chotot_xemay_raw.json"):
        INPUT_FILE = "data/raw/chotot_xemay_raw.json"
        
    process_raw_data(INPUT_FILE, OUTPUT_FILE)