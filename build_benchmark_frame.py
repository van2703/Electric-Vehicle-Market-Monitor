import pandas as pd
import json
import os
import re
import sys

# Đảm bảo console Windows in tiếng Việt UTF-8 không lỗi charmap
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def load_all_raw_data():
    all_titles = []
    
    # 1. Đọc dữ liệu JSON (C2C Chợ Tốt)
    for file_name in ["chotot_xemay_raw.json", "chotot_oto_raw.json"]:
        path = f"data/raw/{file_name}"
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Lấy cột subject (Tiêu đề)
                titles = [item.get('subject', '') for item in data if item.get('subject')]
                all_titles.extend(titles)
                
    # 2. Đọc dữ liệu CSV (B2C Đại lý)
    for file_name in ["thegioixedien_raw.csv", "otodien_raw.csv", "phoxedien_raw.csv", "b2c_oto_raw.csv"]:
        path = f"data/raw/{file_name}"
        if os.path.exists(path):
            df = pd.read_csv(path)
            if 'subject' in df.columns:
                all_titles.extend(df['subject'].dropna().tolist())
                
    return list(set(all_titles)) # Loại bỏ các tiêu đề trùng lặp y hệt nhau

def extract_brand_and_model(title):
    title_lower = title.lower()
    
    # DANH SÁCH PATTERNS NHẬN DIỆN HÃNG VÀ DÒNG XE
    # Thứ tự ưu tiên: từ chi tiết/đặc thù tới khái quát
    model_patterns = [
        # ==========================================
        # 1. Ô TÔ ĐIỆN
        # ==========================================
        # --- VinFast (Ô tô) ---
        (r'\b(vf\s?e?34)\b', 'VinFast', 'VF e34'),
        (r'\b(vf\s?3)\b', 'VinFast', 'VF 3'),
        (r'\b(vf\s?5)\b', 'VinFast', 'VF 5'),
        (r'\b(vf\s?6)\b', 'VinFast', 'VF 6'),
        (r'\b(vf\s?7)\b', 'VinFast', 'VF 7'),
        (r'\b(vf\s?8)\b', 'VinFast', 'VF 8'),
        (r'\b(vf\s?9)\b', 'VinFast', 'VF 9'),
        (r'\b(limo\s?green)\b', 'VinFast', 'Limo Green'),

        # --- BYD ---
        (r'\b(atto\s?3)\b', 'BYD', 'Atto 3'),
        (r'\b(dolphin)\b', 'BYD', 'Dolphin'),
        (r'\b(byd\s?seal|seal\s?ev)\b', 'BYD', 'Seal'),
        (r'\b(sealion\s?6?)\b', 'BYD', 'Sealion 6'),
        (r'\b(byd\s?m6)\b', 'BYD', 'M6'),
        (r'\b(byd\s?han)\b', 'BYD', 'Han'),
        (r'\b(byd\s?tang)\b', 'BYD', 'Tang'),
        (r'\b(byd\s?song)\b', 'BYD', 'Song'),
        (r'\b(seagull)\b', 'BYD', 'Seagull'),
        (r'\bbyd\b', 'BYD', 'BYD (Khác)'),

        # --- Các hãng ô tô khác (Wuling, Hyundai, Tesla, MG) ---
        (r'\b(hongguang|hong\s?guang|mini\s?ev)\b', 'Wuling', 'HongGuang Mini EV'),
        (r'\b(bingo|binguo)\b', 'Wuling', 'Bingo'),
        (r'\b(ioniq\s?5)\b', 'Hyundai', 'Ioniq 5'),
        (r'\b(ioniq\s?6)\b', 'Hyundai', 'Ioniq 6'),
        (r'\b(model\s?3)\b', 'Tesla', 'Model 3'),
        (r'\b(model\s?y)\b', 'Tesla', 'Model Y'),
        (r'\b(model\s?s)\b', 'Tesla', 'Model S'),
        (r'\b(model\s?x)\b', 'Tesla', 'Model X'),
        (r'\b(taycan)\b', 'Porsche', 'Taycan'),
        (r'\b(mg4\s?ev|mg4)\b', 'MG', 'MG4 EV'),

        # ==========================================
        # 2. XE MÁY ĐIỆN
        # ==========================================
        # --- VinFast (Xe máy) ---
        (r'\b(evo\s?200|evo200)\b', 'VinFast', 'Evo 200'),
        (r'\b(feliz\s?s?)\b', 'VinFast', 'Feliz'),
        (r'\b(klara\s?s?|klara\s?a2|klara\s?a1)\b', 'VinFast', 'Klara'),
        (r'\b(theon\s?s?)\b', 'VinFast', 'Theon'),
        (r'\b(vento\s?s?)\b', 'VinFast', 'Vento'),
        (r'\b(impes)\b', 'VinFast', 'Impes'),
        (r'\b(ludo)\b', 'VinFast', 'Ludo'),
        (r'\b(tempest)\b', 'VinFast', 'Tempest'),

        # --- Dat Bike ---
        (r'\b(quantum\s?s?)\b', 'Dat Bike', 'Quantum'),
        (r'\b(weaver\s?\+\+|weaver\s?200|weaver)\b', 'Dat Bike', 'Weaver'),
        (r'\b(dat\s?bike|datbike)\b', 'Dat Bike', 'Dat Bike (Khác)'),

        # --- Yadea ---
        (r'\b(yadea\s?voltguard|voltguard)\b', 'Yadea', 'Voltguard'),
        (r'\b(yadea\s?orla|orla)\b', 'Yadea', 'Orla'),
        (r'\b(yadea\s?ossy|ossy)\b', 'Yadea', 'Ossy'),
        (r'\b(yadea\s?osta|osta)\b', 'Yadea', 'Osta'),
        (r'\b(yadea\s?odora|odora)\b', 'Yadea', 'Odora'),
        (r'\b(yadea\s?ocean|ocean)\b', 'Yadea', 'Ocean'),
        (r'\b(yadea\s?buye|buye)\b', 'Yadea', 'BuyE'),
        (r'\b(yadea\s?ulike|ulike)\b', 'Yadea', 'Ulike'),
        (r'\b(yadea\s?g5|g5)\b', 'Yadea', 'G5'),
        (r'\b(yadea\s?i8|i8)\b', 'Yadea', 'I8'),
        (r'\b(yadea\s?i-cute|i-cute|icute)\b', 'Yadea', 'i-Cute'),
        (r'\b(yadea\s?velax|velax)\b', 'Yadea', 'Velax'),
        (r'\byadea\b', 'Yadea', 'Yadea (Khác)'),

        # --- Dibao ---
        (r'\b(dibao\s?pansy|pansy)\b', 'Dibao', 'Pansy'),
        (r'\b(dibao\s?gogo|gogo)\b', 'Dibao', 'Gogo'),
        (r'\b(dibao\s?creer|creer)\b', 'Dibao', 'Creer'),
        (r'\b(dibao\s?tesla|tesla\s?chic|tesla\s?dio|tesla\s?e|tesla\s?g)\b', 'Dibao', 'Tesla'),
        (r'\b(dibao\s?xman|dibao\s?xmen|xman\s?neo|xmen\s?neo)\b', 'Dibao', 'Xman'),
        (r'\b(dibao\s?ls007|ls007)\b', 'Dibao', 'LS007'),
        (r'\b(dibao\s?shine|shine)\b', 'Dibao', 'Shine'),
        (r'\b(dibao\s?r1)\b', 'Dibao', 'R1'),
        (r'\b(dibao\s?diamond)\b', 'Dibao', 'Diamond'),
        (r'\bdibao\b', 'Dibao', 'Dibao (Khác)'),

        # --- Các hãng xe máy điện khác (Pega, Osakar, Espero, Daelim, Tailg) ---
        (r'\b(pega\s?aura|aura)\b', 'Pega', 'Aura'),
        (r'\b(pega\s?cap\s?a|cap\s?a)\b', 'Pega', 'Cap A'),
        (r'\b(pega\s?s9|pega)\b', 'Pega', 'Pega (Khác)'),
        (r'\b(osakar\s?momo|momo)\b', 'Osakar', 'Momo'),
        (r'\b(osakar\s?nispa|nispa)\b', 'Osakar', 'Nispa'),
        (r'\b(osakar\s?classy|classy)\b', 'Osakar', 'Classy'),
        (r'\b(espero\s?velia|velia)\b', 'Espero', 'Velia'),
        (r'\b(daelim\s?nova|nova\s?revo|nova\s?luna)\b', 'Daelim', 'Nova'),
        (r'\b(tailg\s?t72|tailg\s?t61|tailg\s?r60|tailg\s?t71|tailg\s?venus)\b', 'Tailg', 'Tailg Series'),
    ]
    
    for pattern, brand, model in model_patterns:
        if re.search(pattern, title_lower):
            return brand, model
            
    return "Khác", "Không phân loại"

def build_frame():
    print("[*] Đang quét toàn bộ kho dữ liệu Raw...")
    raw_titles = load_all_raw_data()
    print(f"[*] Tìm thấy tổng cộng {len(raw_titles)} tiêu đề bài đăng khác nhau.")
    
    print("[*] Đang bóc tách Hãng và Dòng xe...")
    extracted_data = [extract_brand_and_model(t) for t in raw_titles]
    
    # Tạo DataFrame từ list kết quả
    df_models = pd.DataFrame(extracted_data, columns=['Brand', 'Model'])
    
    # Lọc bỏ các tin rác không thuộc diện xe điện đã định nghĩa
    df_models = df_models[df_models['Brand'] != "Khác"]
    
    # Bóc tách ra các Dòng xe duy nhất (Unique)
    unique_models = df_models.drop_duplicates().reset_index(drop=True)
    
    # Lưu ra file để làm khung (Frame) cho bước cào giá Benchmark
    output_path = "data/raw/benchmark_frame.csv"
    unique_models.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n[+] XONG! Đã trích xuất được {len(unique_models)} Model xe thực tế.")
    print("--- DANH SÁCH MODEL ĐÃ TÌM THẤY ---")
    print(unique_models)

if __name__ == "__main__":
    build_frame()