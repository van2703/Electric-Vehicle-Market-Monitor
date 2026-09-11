import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9"
}

# ==========================================
# NGUỒN B2C: THẾ GIỚI XE ĐIỆN
# ==========================================
def fetch_thegioixedien(base_url, pages=2):
    all_bikes = []
    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"[*] [Thế Giới Xe Điện] Đang tải trang {page}: {url}")
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code != 200: continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            price_tags = soup.find_all('span', class_='gia_ban')
            
            if not price_tags: break
                
            for p_tag in price_tags:
                price_text = p_tag.text.strip()
                # Loại bỏ ký tự đ, ₫
                price_raw = re.sub(r'[đ₫]', '', price_text).strip()
                clean_digits = re.sub(r'[^\d]', '', price_raw)
                price_clean = int(clean_digits) if clean_digits else None

                title_tag = p_tag.find_previous('h3')
                title = title_tag.text.strip() if title_tag else "N/A"
                
                all_bikes.append({
                    "source": "thegioixedien_B2C",
                    "subject": title,
                    "price_raw": price_raw,
                    "price_clean": price_clean,
                    "battery_status": "Kèm pin"
                })
        except Exception as e:
            print(f"[X] Lỗi: {e}")
        time.sleep(2)
    return all_bikes

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    
    print("=== CÀO DỮ LIỆU: THẾ GIỚI XE ĐIỆN ===")
    tgxd_url = "https://thegioixedien.com.vn/avd33_xe-may-dien/"
    tgxd_data = fetch_thegioixedien(tgxd_url, pages=5)
    
    if tgxd_data:
        df_tgxd = pd.DataFrame(tgxd_data)
        file_path = "data/raw/thegioixedien_raw.csv"
        df_tgxd.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"[+] XONG! Lưu {len(tgxd_data)} xe vào {file_path}")
        print("\n--- XEM TRƯỚC 5 DÒNG ĐẦU ---")
        print(df_tgxd.head())
    else:
        print("\n[-] Không lấy được dữ liệu.")
