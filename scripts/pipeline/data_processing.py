"""
EV Market Data Processing Pipeline
==================================
Hợp nhất dữ liệu Ô tô điện & Xe máy điện từ tầng Interim (data/interim/),
chuẩn hoá thông tin Brand, Model, Năm sản xuất, Tình trạng Pin;
áp dụng chính sách bảo vệ dữ liệu cá nhân (PDPD Legal Anonymization);
ánh xạ vào ma trận Benchmark Timeline (Brand x Model x Year x Battery)
để tính toán tỷ lệ khấu hao (Depreciation %).

Output: data/processed/ev_market_cleaned.csv
"""

import os
import sys
import re
import unicodedata
from pathlib import Path
from typing import Tuple, Optional
import pandas as pd

# Thiết lập UTF-8 Console trên Windows tránh lỗi UnicodeEncodeError
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


# ==========================================
# 1. LEGAL ANONYMIZER (PDPD COMPLIANCE)
# ==========================================
def anonymize_text(text: any) -> any:
    """
    Ẩn các thông tin định danh cá nhân nhạy cảm trong văn bản:
    - Số nhà, số ngõ/hẻm/ngách cụ thể.
    - Số điện thoại cá nhân.
    """
    if not isinstance(text, str):
        return text

    # Che số nhà, ngõ ngách (VD: "389 Đội Cấn", "Số 12 ngõ 4", "Hẻm 45/2")
    address_pattern = r'\b(\d+[A-Za-z]?(/[0-9]+)?)\s+(đội cấn|ngõ|ngách|hẻm|đường|phố|quận|phường|thị trấn|ấp)\b'
    text = re.sub(address_pattern, r'*** \3', text, flags=re.IGNORECASE)

    # Che số điện thoại di động (giữ 4 số đầu, ẩn phần còn lại)
    phone_pattern = r'\b(0[35789]\d{2})[-.\s]?\d{3}[-.\s]?\d{3}\b'
    text = re.sub(phone_pattern, r'\1******', text)

    return text


# ==========================================
# 2. PHÂN LOẠI TÌNH TRẠNG PIN (BATTERY STATUS)
# ==========================================
def extract_battery_status(text: any) -> str:
    """
    Phân loại tình trạng pin từ tiêu đề và mô tả:
    - 'Thuê pin': Xe không bán kèm pin, người mua phải tiếp tục thuê pin.
    - 'Kèm pin': Xe đã mua đứt pin hoặc bao pin.
    - 'Cần xác minh': Tin đăng không đề cập rõ ràng đến pin.
    Lưu ý: Không dùng từ 'zin' độc lập vì gây nhận diện sai (xe zin, máy zin).
    """
    if not isinstance(text, str):
        return "Cần xác minh"

    norm_text = unicodedata.normalize('NFKD', text).lower()

    # Nhận diện xe KHÔNG PIN / THUÊ PIN
    no_battery_kws = [
        'thuê pin', 'thue pin', 'không pin', 'khong pin',
        'không kèm pin', 'khong kem pin', 'chưa pin', 'chua pin',
        'k pin', 'ko pin', 'chưa bao gồm pin', 'chua bao gom pin'
    ]
    if any(kw in norm_text for kw in no_battery_kws):
        return "Thuê pin"

    # Nhận diện xe ĐÃ CÓ PIN / MUA ĐỨT PIN
    with_battery_kws = [
        'kèm pin', 'kem pin', 'bao pin', 'có pin', 'co pin',
        'đã mua pin', 'da mua pin', 'sẵn pin', 'san pin', 'cả pin', 'ca pin',
        'mua đứt pin', 'mua dut pin', 'mua pin', 'pin zin', 'ắc quy zin', 'bình zin'
    ]
    if any(kw in norm_text for kw in with_battery_kws):
        return "Kèm pin"

    return "Cần xác minh"


# ==========================================
# 3. CHUẨN HOÁ HÃNG & DÒNG XE (MODEL NORMALIZATION)
# ==========================================
# Bảng quy tắc chuẩn hóa dòng xe về tên chuẩn của Benchmark
MODEL_MAPPING_RULES = [
    # --- VinFast Ô tô ---
    (r'\b(vf\s?3|vf3)\b', 'VinFast', 'VF 3'),
    (r'\b(vf\s?5\s?plus|vf\s?5|vf5\s?plus|vf5)\b', 'VinFast', 'VF 5'),
    (r'\b(vf\s?6\s?plus|vf\s?6\s?eco|vf\s?6|vf6)\b', 'VinFast', 'VF 6'),
    (r'\b(vf\s?7\s?plus|vf\s?7\s?base|vf\s?7\s?eco|vf\s?7|vf7)\b', 'VinFast', 'VF 7'),
    (r'\b(vf\s?8\s?plus|vf\s?8\s?eco|vf\s?8\s?lux|vf\s?8|vf8)\b', 'VinFast', 'VF 8'),
    (r'\b(vf\s?9\s?plus|vf\s?9\s?eco|vf\s?9|vf9)\b', 'VinFast', 'VF 9'),
    (r'\b(vf\s?e?34|vfe34)\b', 'VinFast', 'VF e34'),
    (r'\b(limo\s?green|mpv\s?7|mvp\s?7)\b', 'VinFast', 'Limo Green'),

    # --- VinFast Xe máy ---
    (r'\b(evo\s?200\s?lite|evo\s?200|evo200\s?lite|evo200|evo\s?grand)\b', 'VinFast', 'Evo 200'),
    (r'\b(feliz\s?s|feliz\s?neo|feliz)\b', 'VinFast', 'Feliz'),
    (r'\b(klara\s?s|klara\s?a2|klara\s?a1|klara)\b', 'VinFast', 'Klara'),
    (r'\b(vento\s?s|vento)\b', 'VinFast', 'Vento'),
    (r'\b(ludo)\b', 'VinFast', 'Ludo'),
    (r'\b(theon\s?s|theon)\b', 'VinFast', 'Theon'),
    (r'\b(impes)\b', 'VinFast', 'Impes'),

    # --- Dat Bike ---
    (r'\b(quantum\s?s1|quantum\s?s2|quantum\s?s|quantum)\b', 'Dat Bike', 'Quantum'),
    (r'\b(weaver\s?\+\+|weaver\s?200|weaver)\b', 'Dat Bike', 'Dat Bike (Khác)'),

    # --- BYD ---
    (r'\b(byd\s?seal|seal)\b', 'BYD', 'Seal'),
    (r'\b(byd\s?atto\s?3|atto\s?3|atto3)\b', 'BYD', 'Atto 3'),
    (r'\b(byd\s?dolphin|dolphin)\b', 'BYD', 'Dolphin'),

    # --- Yadea ---
    (r'\b(voltguard)\b', 'Yadea', 'Voltguard'),
    (r'\b(ossy)\b', 'Yadea', 'Ossy'),
    (r'\b(orla)\b', 'Yadea', 'Orla'),
    (r'\b(osta)\b', 'Yadea', 'Osta'),
    (r'\b(ocean)\b', 'Yadea', 'Ocean'),

    # --- Dibao ---
    (r'\b(pansy)\b', 'Dibao', 'Pansy'),
    (r'\b(gogo)\b', 'Dibao', 'Gogo'),
    (r'\b(creer)\b', 'Dibao', 'Creer'),
    (r'\b(tesla)\b', 'Dibao', 'Tesla'),
    (r'\b(xman|xmen)\b', 'Dibao', 'Xman'),
    (r'\b(ls007)\b', 'Dibao', 'LS007'),
    (r'\b(shine)\b', 'Dibao', 'Shine'),

    # --- Osakar ---
    (r'\b(nispa)\b', 'Osakar', 'Nispa'),
    (r'\b(momo)\b', 'Osakar', 'Momo'),

    # --- Espero, Daelim, Tailg ---
    (r'\b(velia)\b', 'Espero', 'Velia'),
    (r'\b(nova)\b', 'Daelim', 'Nova'),
    (r'\b(tailg)\b', 'Tailg', 'Tailg Series'),
]

def normalize_brand_and_model(raw_brand: any, raw_model: any, title: any) -> Tuple[str, str]:
    """
    Chuẩn hoá Tên Hãng và Tên Dòng xe:
    1. Ưu tiên tra cứu chuỗi regex trên tiêu đề (để ánh xạ đúng mã chuẩn Benchmark).
    2. Fallback về raw_brand, raw_model đã có từ từ điển Chợ Tốt.
    """
    title_str = str(title or "").lower()
    raw_b_str = str(raw_brand or "").strip()
    raw_m_str = str(raw_model or "").strip()

    # Chuẩn hoá tên hãng phổ biến
    brand_std = raw_b_str
    if raw_b_str.lower() in ['datbike', 'dat bike']:
        brand_std = "Dat Bike"
    elif raw_b_str.lower() in ['vinfast']:
        brand_std = "VinFast"
    elif raw_b_str.lower() in ['yadea']:
        brand_std = "Yadea"
    elif raw_b_str.lower() in ['byd']:
        brand_std = "BYD"
    elif raw_b_str.lower() in ['dibao']:
        brand_std = "Dibao"

    # Kiểm tra quy tắc ánh xạ model
    for pattern, rule_brand, rule_model in MODEL_MAPPING_RULES:
        if re.search(pattern, title_str):
            return rule_brand, rule_model

    # Nếu không khớp regex, dùng thông tin từ raw/từ điển nếu có
    final_brand = brand_std if brand_std and brand_std.lower() not in ['hãng khác', 'hãng khác', 'nan', 'none', ''] else "Khác"
    final_model = raw_m_str if raw_m_str and raw_m_str.lower() not in ['dòng khác', 'nan', 'none', ''] else "Không phân loại"

    return final_brand, final_model


# ==========================================
# 4. DATA PROCESSING PIPELINE CHÍNH
# ==========================================
def process_ev_market_pipeline():
    base_dir = Path(__file__).resolve().parents[2]
    interim_dir = base_dir / "data" / "interim"
    benchmark_file = base_dir / "data" / "benchmark" / "ev_benchmark_timeline.csv"
    processed_dir = base_dir / "data" / "processed"
    output_file = processed_dir / "ev_market_cleaned.csv"

    oto_clean_path = interim_dir / "chotot_oto_clean.csv"
    xemay_clean_path = interim_dir / "chotot_xemay_clean.csv"

    print("=== BẮT ĐẦU PIPELINE XỬ LÝ & HỢP NHẤT DỮ LIỆU THỊ TRƯỜNG XE ĐIỆN ===")

    # Kiểm tra các file interim đầu vào
    if not oto_clean_path.exists() or not xemay_clean_path.exists():
        print("[-] Cảnh báo: Chưa tìm thấy đủ file trong data/interim/.")
        print("[*] Đang tự động chạy clean_chotot_oto.py và clean_chotot_xemay.py...")
        from scripts.cleaning.clean_chotot_oto import main as clean_oto_main
        from scripts.cleaning.clean_chotot_xemay import main as clean_xemay_main
        clean_oto_main()
        clean_xemay_main()

    # 1. Đọc dữ liệu Interim
    print(f"[*] [1/5] Nạp dữ liệu Ô tô điện từ: {oto_clean_path}")
    df_oto = pd.read_csv(oto_clean_path)
    df_oto['vehicle_type'] = 'car'
    # Năm của ô tô là mfdate_year
    df_oto['year'] = pd.to_numeric(df_oto.get('mfdate_year'), errors='coerce')

    print(f"[*] [2/5] Nạp dữ liệu Xe máy điện từ: {xemay_clean_path}")
    df_xemay = pd.read_csv(xemay_clean_path)
    df_xemay['vehicle_type'] = 'bike'
    # Năm của xe máy là regdate_year
    df_xemay['year'] = pd.to_numeric(df_xemay.get('regdate_year'), errors='coerce')

    # 2. Hợp nhất các cột chung
    common_cols = [
        'list_id', 'vehicle_type', 'title', 'description', 'price_vnd',
        'condition', 'year', 'mileage_km', 'brand_name', 'model_name',
        'posted_at', 'region_name', 'area_name', 'seller_name', 'company_ad'
    ]
    df_oto_sub = df_oto[[c for c in common_cols if c in df_oto.columns]].copy()
    df_xemay_sub = df_xemay[[c for c in common_cols if c in df_xemay.columns]].copy()

    df = pd.concat([df_oto_sub, df_xemay_sub], ignore_index=True)
    print(f"[+] Hợp nhất thành công: {len(df_oto_sub)} ô tô + {len(df_xemay_sub)} xe máy = {len(df)} tin.")

    # 3. Làm sạch văn bản & bảo mật thông tin (PDPD)
    print("[*] [3/5] Thực hiện PDPD Anonymization & Bóc tách Tình trạng Pin...")
    df['title'] = df['title'].apply(anonymize_text)
    df['description'] = df['description'].apply(anonymize_text)

    # Bóc tách Pin từ tiêu đề + mô tả
    full_text = df['title'].fillna('') + ' ' + df['description'].fillna('')
    df['battery_status'] = full_text.apply(extract_battery_status)

    # 4. Chuẩn hoá Brand & Model theo khung Benchmark
    print("[*] [4/5] Chuẩn hoá Hãng & Dòng xe...")
    brand_model_tuples = [
        normalize_brand_and_model(r['brand_name'], r['model_name'], r['title'])
        for _, r in df.iterrows()
    ]
    df['brand'] = [b for b, m in brand_model_tuples]
    df['model'] = [m for b, m in brand_model_tuples]

    # Xóa các cột thô ban đầu
    df = df.drop(columns=['brand_name', 'model_name'], errors='ignore')

    # 5. Ánh xạ Benchmark Timeline & Tính toán Tỷ lệ khấu hao
    print("[*] [5/5] Ánh xạ Benchmark Timeline & Tính tỷ lệ Khấu hao...")
    df['benchmark_msrp'] = None
    df['depreciation_pct'] = None

    if benchmark_file.exists():
        df_bench = pd.read_csv(benchmark_file)

        # Xây dựng bảng tra cứu Benchmark Timeline: (Brand, Model, Year)
        bench_map = {}
        bench_fallback = {}

        for _, row in df_bench.iterrows():
            b = str(row['Brand']).strip().lower()
            m = str(row['Model']).strip().lower()
            y = int(row['Year'])
            p_base = row['Price_Benchmark']
            p_no_bat = row.get('Price_No_Battery', p_base)
            p_with_bat = row.get('Price_With_Battery', p_base)

            bench_map[(b, m, y)] = {
                'base': p_base,
                'no_battery': p_no_bat,
                'with_battery': p_with_bat
            }
            # Fallback về năm mới nhất cho model này
            bench_fallback[(b, m)] = {
                'base': p_base,
                'no_battery': p_no_bat,
                'with_battery': p_with_bat
            }

        def get_benchmark_price(row):
            b = str(row['brand']).strip().lower()
            m = str(row['model']).strip().lower()
            y = row['year']
            bat_status = row['battery_status']

            prices = None
            try:
                y_int = int(y)
                if (b, m, y_int) in bench_map:
                    prices = bench_map[(b, m, y_int)]
            except (ValueError, TypeError):
                pass

            if prices is None:
                prices = bench_fallback.get((b, m))

            if prices:
                # Ưu tiên chọn đúng giá niêm yết theo trạng thái pin
                if bat_status == 'Thuê pin' and prices['no_battery'] > 0:
                    return prices['no_battery']
                elif bat_status == 'Kèm pin' and prices['with_battery'] > 0:
                    return prices['with_battery']
                return prices['base']

            return None

        df['benchmark_msrp'] = df.apply(get_benchmark_price, axis=1)

        # Tính tỷ lệ khấu hao (%) so với giá niêm yết
        def calc_depreciation(row):
            msrp = row['benchmark_msrp']
            cur_p = row['price_vnd']
            if pd.notnull(msrp) and pd.notnull(cur_p) and msrp > 0 and cur_p > 0:
                pct = round((1 - cur_p / msrp) * 100, 1)
                return pct
            return None

        df['depreciation_pct'] = df.apply(calc_depreciation, axis=1)
    else:
        print(f"[-] Không tìm thấy file Benchmark: {benchmark_file}")

    # 6. Định dạng và sắp xếp lại các cột đầu ra
    cols_order = [
        'list_id', 'vehicle_type', 'brand', 'model', 'year', 'price_vnd',
        'benchmark_msrp', 'depreciation_pct', 'battery_status', 'condition',
        'mileage_km', 'title', 'description', 'posted_at',
        'region_name', 'area_name', 'seller_name', 'company_ad'
    ]
    final_cols = [c for c in cols_order if c in df.columns]
    df = df[final_cols]

    # Lưu kết quả hoàn chỉnh
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\n[+] HOÀN THÀNH XUẤT SẮC! Đã lưu {len(df)} dòng vào: {output_file}")
    print("\n--- PHÂN BỐ PHƯƠNG TIỆN THEO LOẠI ---")
    print(df['vehicle_type'].value_counts())
    print("\n--- TOP 5 THƯƠNG HIỆU PHỔ BIẾN NHẤT ---")
    print(df['brand'].value_counts().head(5))
    print("\n--- PHÂN BỐ TÌNH TRẠNG PIN ---")
    print(df['battery_status'].value_counts())
    print("\n--- TỶ LỆ CÓ GIÁ BENCHMARK VÀ KHẤU HAO ---")
    bench_matched = df['benchmark_msrp'].notnull().sum()
    print(f"Đã khớp Benchmark: {bench_matched}/{len(df)} ({bench_matched/len(df)*100:.1f}%)")

    return df


if __name__ == "__main__":
    process_ev_market_pipeline()