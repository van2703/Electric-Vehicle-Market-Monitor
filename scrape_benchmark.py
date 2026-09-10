import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import sys

# Đảm bảo console Windows in tiếng Việt UTF-8 không lỗi charmap
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9"
}

GAS_CAR_KEYWORDS = ['fadil', 'lux a', 'lux sa', 'president']

def clean_price_to_number(price_str):
    """Làm sạch chuỗi giá về số nguyên VNĐ."""
    if not price_str or price_str == "N/A":
        return None
    text = str(price_str).lower().strip()
    if 'tỷ' in text or 'triệu' in text or 'tr' in text:
        total = 0.0
        ty_match = re.search(r'(\d+(?:[.,]\d+)?)\s*tỷ', text)
        if ty_match:
            total += float(ty_match.group(1).replace(',', '.')) * 1_000_000_000
        trieu_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:triệu|tr)', text)
        if trieu_match:
            total += float(trieu_match.group(1).replace(',', '.')) * 1_000_000
        if ty_match and not trieu_match:
            after_ty = text.split('tỷ', 1)[1].strip()
            num_after = re.search(r'^(\d+(?:[.,]\d+)?)', after_ty)
            if num_after:
                val = float(num_after.group(1).replace(',', '.'))
                total += val * 100_000_000 if val < 10 else val * 1_000_000
        return int(total) if total > 0 else None
    clean_num = re.sub(r'[^\d]', '', text)
    return int(clean_num) if clean_num else None

# ==========================================
# 1. CÀO Ô TÔ ĐIỆN VINFAST TỪ BONBANH
# ==========================================
def fetch_bonbanh_benchmark():
    url = "https://bonbanh.com/gia-xe-oto-vinfast"
    print(f"[*] [1/3] Đang cào dữ liệu ô tô VinFast từ BonBanh: {url}")
    benchmark_data = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            td_tags = soup.find_all('td')
            for td in td_tags:
                text = td.text.strip().replace('\xa0', ' ')
                text_lower = text.lower()
                if text_lower.startswith('vinfast'):
                    if any(gas_kw in text_lower for gas_kw in GAS_CAR_KEYWORDS):
                        continue
                    model_name = re.sub(r'\s+', ' ', text).strip()
                    price_td = td.find_next_sibling('td')
                    if price_td:
                        price_raw = price_td.text.strip()
                        if 'triệu' in price_raw.lower():
                            continue
                        price_val = clean_price_to_number(price_raw)
                        if price_val and price_val >= 100_000_000:
                            benchmark_data.append({
                                "Category": "Ô tô",
                                "Brand": "VinFast",
                                "Model_Raw": model_name,
                                "Price_Benchmark": price_val
                            })
    except Exception as e:
        print(f"[X] Lỗi cào BonBanh: {e}")
    print(f"    -> Thu thập được {len(benchmark_data)} phiên bản ô tô từ BonBanh.")
    return benchmark_data

# ==========================================
# 2. CÀO XE MÁY ĐIỆN TỪ XE ĐIỆN VIỆT THANH
# ==========================================
def fetch_vietthanh_benchmark():
    url = "https://xedienvietthanh.com/tin-tuc/bang-gia-cac-loai-xe-may-dien-hien-nay/"
    print(f"[*] [2/3] Đang cào bảng giá xe máy điện từ Việt Thanh: {url}")
    bike_data = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = [td.text.strip().replace('\xa0', ' ') for td in row.find_all(['td', 'th'])]
                    if len(cols) >= 3 and cols[0] not in ['Mẫu xe', 'Tên mẫu xe']:
                        model_name = cols[0]
                        brand_name = cols[1] if cols[1] else "Khác"
                        price_str = cols[2]
                        price_val = clean_price_to_number(price_str)
                        if price_val and price_val >= 5_000_000:
                            # Chuẩn hóa tên thương hiệu
                            b_lower = brand_name.lower()
                            if 'vinfast' in b_lower: brand_name = "VinFast"
                            elif 'yadea' in b_lower: brand_name = "Yadea"
                            elif 'datbike' in b_lower or 'dat bike' in b_lower: brand_name = "Dat Bike"
                            elif 'espero' in b_lower: brand_name = "Espero"
                            bike_data.append({
                                "Category": "Xe máy",
                                "Brand": brand_name,
                                "Model_Raw": model_name,
                                "Price_Benchmark": price_val
                            })
    except Exception as e:
        print(f"[X] Lỗi cào Việt Thanh: {e}")
    print(f"    -> Thu thập được {len(bike_data)} phiên bản xe máy điện từ Việt Thanh.")
    return bike_data

# ==========================================
# 3. BỔ SUNG GIÁ NIÊM YẾT CHÍNH HÃNG CỦA CÁC MODEL CÒN LẠI
# ==========================================
def get_known_benchmark_data():
    """
    Bổ sung các mức giá niêm yết chính hãng uy tín cho BYD và các dòng xe máy
    phổ biến (VinFast, Dat Bike, Dibao, Osakar, Daelim, Tailg) từ các đại lý lớn.
    """
    known_data = [
        # --- BYD Ô tô điện chính hãng tại VN ---
        {"Category": "Ô tô", "Brand": "BYD", "Model_Raw": "BYD Seal Advanced", "Price_Benchmark": 1119000000},
        {"Category": "Ô tô", "Brand": "BYD", "Model_Raw": "BYD Seal Performance", "Price_Benchmark": 1359000000},
        {"Category": "Ô tô", "Brand": "BYD", "Model_Raw": "BYD Atto 3 Dynamic", "Price_Benchmark": 766000000},
        {"Category": "Ô tô", "Brand": "BYD", "Model_Raw": "BYD Dolphin GLX", "Price_Benchmark": 659000000},

        # --- VinFast Xe máy điện chính hãng ---
        {"Category": "Xe máy", "Brand": "VinFast", "Model_Raw": "VinFast Evo 200", "Price_Benchmark": 18000000},
        {"Category": "Xe máy", "Brand": "VinFast", "Model_Raw": "VinFast Feliz S", "Price_Benchmark": 27000000},
        {"Category": "Xe máy", "Brand": "VinFast", "Model_Raw": "VinFast Klara S", "Price_Benchmark": 35000000},
        {"Category": "Xe máy", "Brand": "VinFast", "Model_Raw": "VinFast Vento S", "Price_Benchmark": 50000000},
        {"Category": "Xe máy", "Brand": "VinFast", "Model_Raw": "VinFast Ludo", "Price_Benchmark": 12900000},

        # --- Dat Bike ---
        {"Category": "Xe máy", "Brand": "Dat Bike", "Model_Raw": "Dat Bike Weaver++", "Price_Benchmark": 65900000},
        {"Category": "Xe máy", "Brand": "Dat Bike", "Model_Raw": "Dat Bike Weaver 200", "Price_Benchmark": 54900000},

        # --- Dibao (Giá niêm yết Thế Giới Xe Điện) ---
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Pansy Neo S4", "Price_Benchmark": 17190000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Pansy Neo S3", "Price_Benchmark": 15490000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Gogo Moon", "Price_Benchmark": 14500000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Creer E", "Price_Benchmark": 14990000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Creer Nile", "Price_Benchmark": 15190000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Tesla Dio E", "Price_Benchmark": 14490000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Tesla Chic", "Price_Benchmark": 16990000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Xman Neo", "Price_Benchmark": 16500000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao LS007", "Price_Benchmark": 22990000},
        {"Category": "Xe máy", "Brand": "Dibao", "Model_Raw": "Dibao Shine", "Price_Benchmark": 22990000},

        # --- Yadea (Bổ sung thêm) ---
        {"Category": "Xe máy", "Brand": "Yadea", "Model_Raw": "Yadea Voltguard 72V", "Price_Benchmark": 25990000},
        {"Category": "Xe máy", "Brand": "Yadea", "Model_Raw": "Yadea Ossy", "Price_Benchmark": 18490000},

        # --- Osakar, Daelim, Tailg ---
        {"Category": "Xe máy", "Brand": "Osakar", "Model_Raw": "Osakar Nispa SV", "Price_Benchmark": 16990000},
        {"Category": "Xe máy", "Brand": "Osakar", "Model_Raw": "Osakar Momo", "Price_Benchmark": 11990000},
        {"Category": "Xe máy", "Brand": "Daelim", "Model_Raw": "Daelim Nova Luna", "Price_Benchmark": 13990000},
        {"Category": "Xe máy", "Brand": "Daelim", "Model_Raw": "Daelim Nova Revo", "Price_Benchmark": 20990000},
        {"Category": "Xe máy", "Brand": "Tailg", "Model_Raw": "Tailg R60", "Price_Benchmark": 16840000},
        {"Category": "Xe máy", "Brand": "Tailg", "Model_Raw": "Tailg T61", "Price_Benchmark": 28840000},
        {"Category": "Xe máy", "Brand": "Tailg", "Model_Raw": "Tailg T72", "Price_Benchmark": 36750000},
    ]
    return known_data

# ==========================================
# 4. MAPPING VÀ HOÀN THIỆN KHUNG BENCHMARK
# ==========================================
def map_prices_to_benchmark_frame(all_benchmark_data):
    frame_path = "data/raw/benchmark_frame.csv"
    if not os.path.exists(frame_path):
        print("[-] Không tìm thấy benchmark_frame.csv")
        return None

    df_frame = pd.read_csv(frame_path)
    df_frame['Benchmark_Price'] = None

    print(f"[*] Đang ánh xạ giá Benchmark vào {len(df_frame)} Model trong khung...")

    # Từ điển ánh xạ từ khóa Model sang giá
    for idx, row in df_frame.iterrows():
        brand = str(row['Brand']).strip().lower()
        model = str(row['Model']).strip()
        m_lower = model.lower()

        matched = []
        for item in all_benchmark_data:
            i_brand = str(item['Brand']).strip().lower()
            i_raw = str(item['Model_Raw']).lower()

            # Khớp hãng
            if brand in i_brand or i_brand in brand:
                # Khớp dòng xe
                # Xử lý các trường hợp đặc biệt
                if m_lower == "yadea (khác)" or m_lower == "dat bike (khác)":
                    matched.append(item['Price_Benchmark'])
                elif m_lower == "tailg series" and "tailg" in i_raw:
                    matched.append(item['Price_Benchmark'])
                elif m_lower.replace(" ", "") in i_raw.replace(" ", ""):
                    matched.append(item['Price_Benchmark'])
                elif m_lower in i_raw:
                    matched.append(item['Price_Benchmark'])

        if matched:
            # Chọn giá thấp nhất làm giá khởi điểm (Base Price)
            df_frame.at[idx, 'Benchmark_Price'] = min(matched)

    return df_frame

def run():
    print("=== TỔNG HỢP TOÀN DIỆN BẢNG GIÁ BENCHMARK XE ĐIỆN ===")
    os.makedirs("data/raw", exist_ok=True)

    # 1. Thu thập từ các nguồn
    bonbanh_data = fetch_bonbanh_benchmark()
    vietthanh_data = fetch_vietthanh_benchmark()
    known_data = get_known_benchmark_data()

    # Tổng hợp toàn bộ danh sách chi tiết
    all_records = bonbanh_data + vietthanh_data + known_data
    df_all = pd.DataFrame(all_records).drop_duplicates(subset=['Brand', 'Model_Raw']).reset_index(drop=True)

    # Lưu file danh sách chi tiết bonbanh_benchmark.csv
    bonbanh_file = "data/raw/bonbanh_benchmark.csv"
    df_all.to_csv(bonbanh_file, index=False, encoding='utf-8-sig')
    print(f"\n[+] Đã lưu {len(df_all)} phiên bản chi tiết vào: {bonbanh_file}")

    # 2. Hoàn thiện khung Benchmark Dimension Table
    df_final = map_prices_to_benchmark_frame(all_records)
    if df_final is not None:
        final_file = "data/raw/final_benchmark.csv"
        df_final.to_csv(final_file, index=False, encoding='utf-8-sig')
        print(f"[+] Hoàn thiện 100% Khung Benchmark lưu tại: {final_file}")

        print("\n--- BẢNG GIÁ BENCHMARK HOÀN THIỆN THEO FRAME (34 MODELS) ---")
        print(df_final.to_string())

        # Kiểm tra tỷ lệ phủ giá
        filled = df_final['Benchmark_Price'].notnull().sum()
        print(f"\n[*] Tỷ lệ có giá: {filled}/{len(df_final)} ({filled/len(df_final)*100:.1f}%)")

if __name__ == "__main__":
    run()