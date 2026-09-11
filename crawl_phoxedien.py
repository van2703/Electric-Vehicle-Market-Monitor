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
# NGUỒN B2C: PHỐ XE ĐIỆN
# ==========================================
def fetch_phoxedien(base_url, pages=2):
    all_bikes = []
    for page in range(1, pages + 1):
        url = f"{base_url}page/{page}/" if page > 1 else base_url
        print(f"[*] [Phố Xe Điện] Đang tải trang {page}: {url}")
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code != 200: continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            price_tags = soup.find_all('bdi')
            
            if not price_tags: break
                
            for p_tag in price_tags:
                price_text = p_tag.text.strip()
                # Làm sạch giá: loại bỏ chữ đ, ₫
                price_raw = re.sub(r'[đ₫]', '', price_text).strip()
                clean_digits = re.sub(r'[^\d]', '', price_raw)
                price_clean = int(clean_digits) if clean_digits else None

                title_tag = p_tag.find_previous('a')
                title = title_tag.text.strip() if title_tag else "N/A"
                
                if title and len(title) > 3:
                    # BỘ LỌC CHỐNG TRÙNG LẶP: Kiểm tra xem xe này đã có trong danh sách chưa
                    if len(all_bikes) > 0 and all_bikes[-1]["subject"] == title:
                        all_bikes[-1]["price_raw"] = price_raw
                        all_bikes[-1]["price_clean"] = price_clean
                    else:
                        all_bikes.append({
                            "source": "phoxedien_B2C",
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
    
    print("=== CÀO DỮ LIỆU: PHỐ XE ĐIỆN ===")
    pxd_url = "https://phoxedien.com/xe-may-dien/" 
    pxd_data = fetch_phoxedien(pxd_url, pages=30)
    
    if pxd_data:
        df_pxd = pd.DataFrame(pxd_data)
        file_path = "data/raw/phoxedien_raw.csv"
        df_pxd.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"[+] XONG! Lưu {len(pxd_data)} xe vào {file_path}")
        print("\n--- XEM TRƯỚC 5 DÒNG CỦA PHỐ XE ĐIỆN ---")
        print(df_pxd.head())
    else:
        print("\n[-] Không lấy được dữ liệu.")
