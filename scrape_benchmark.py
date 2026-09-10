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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9"
}

# Các từ khóa nhận diện xe xăng VinFast cần loại bỏ (chỉ giữ xe điện EV)
GAS_CAR_KEYWORDS = ['fadil', 'lux a', 'lux sa', 'president']

def fetch_bonbanh_benchmark():
    url = "https://bonbanh.com/gia-xe-oto-vinfast"
    print(f"[*] Đang cào dữ liệu Benchmark từ: {url}")
    
    benchmark_data = []
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Quét tất cả các ô td trong bảng
            td_tags = soup.find_all('td')
            
            for td in td_tags:
                text = td.text.strip().replace('\xa0', ' ')
                text_lower = text.lower()
                
                # 1. Chỉ lấy xe VinFast
                if text_lower.startswith('vinfast'):
                    # 2. Lọc bỏ các dòng xe xăng cũ (Fadil, Lux, President)
                    if any(gas_kw in text_lower for gas_kw in GAS_CAR_KEYWORDS):
                        continue
                    
                    model_name = re.sub(r'\s+', ' ', text).strip()
                    
                    # 3. Lấy ô td chứa giá kế bên
                    price_td = td.find_next_sibling('td')
                    if price_td:
                        price_raw = price_td.text.strip()
                        
                        # Bỏ qua nếu là bảng tóm tắt chân trang (chứa chữ "triệu" gây lỗi lệch ô / sai tỷ lệ)
                        if 'triệu' in price_raw.lower():
                            continue
                            
                        # Làm sạch chữ số
                        price_clean = re.sub(r'[^\d]', '', price_raw)
                        
                        if price_clean:
                            price_val = int(price_clean)
                            # 4. Chỉ chấp nhận giá trị thực tế >= 100 triệu VNĐ (loại bỏ số tóm tắt < 10.000)
                            if price_val >= 100_000_000:
                                benchmark_data.append({
                                    "Brand": "VinFast",
                                    "Model_Raw": model_name,
                                    "Price_Benchmark": price_val
                                })
                                
    except Exception as e:
        print(f"[X] Lỗi cào dữ liệu: {e}")
        
    return benchmark_data

if __name__ == "__main__":
    print("=== BƯỚC 2: TẠO BẢNG GIÁ HÃNG (GROUND TRUTH) ===")
    data = fetch_bonbanh_benchmark()
    
    if data:
        # Chuyển thành DataFrame và lọc bỏ các dòng trùng lặp
        df_benchmark = pd.DataFrame(data).drop_duplicates().reset_index(drop=True)
        
        # Lưu file
        os.makedirs("data/raw", exist_ok=True)
        file_path = "data/raw/bonbanh_benchmark.csv"
        df_benchmark.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        print(f"[+] XONG! Đã cào được {len(df_benchmark)} phiên bản xe điện chuẩn xác.")
        print(f"[*] Lưu tại: {file_path}")
        print("\n--- XEM TOÀN BỘ BẢNG GIÁ HÃNG CHUẨN HÓA ---")
        print(df_benchmark.to_string())
    else:
        print("[-] Không lấy được dữ liệu.")