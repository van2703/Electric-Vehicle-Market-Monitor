import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9"
}

# ==========================================
# 1. NGUỒN B2C: THẾ GIỚI XE ĐIỆN
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
                price = p_tag.text.strip()
                title_tag = p_tag.find_previous('h3')
                title = title_tag.text.strip() if title_tag else "N/A"
                
                all_bikes.append({
                    "source": "thegioixedien_B2C",
                    "subject": title,
                    "price_raw": price,
                    "battery_status": "Kèm pin"
                })
        except Exception as e:
            print(f"[X] Lỗi: {e}")
        time.sleep(2)
    return all_bikes

# ==========================================
# 2. NGUỒN B2C: PHỐ XE ĐIỆN
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
                price = p_tag.text.strip()
                title_tag = p_tag.find_previous('a')
                title = title_tag.text.strip() if title_tag else "N/A"
                
                if title and len(title) > 3:
                    # BỘ LỌC CHỐNG TRÙNG LẶP: Kiểm tra xem xe này đã có trong danh sách chưa
                    if len(all_bikes) > 0 and all_bikes[-1]["subject"] == title:
                        all_bikes[-1]["price_raw"] = price
                    else:
                        all_bikes.append({
                            "source": "phoxedien_B2C",
                            "subject": title,
                            "price_raw": price,
                            "battery_status": "Kèm pin"
                        })
        except Exception as e:
            print(f"[X] Lỗi: {e}")
        time.sleep(2)
    return all_bikes

# ==========================================
# THỰC THI PIPELINE THU THẬP B2C
# ==========================================
if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    
    # --- Chạy luồng 1 ---
    print("=== 1. CÀO DỮ LIỆU: THẾ GIỚI XE ĐIỆN ===")
    tgxd_url = "https://thegioixedien.com.vn/avd33_xe-may-dien/"
    tgxd_data = fetch_thegioixedien(tgxd_url, pages=5)
    
    if tgxd_data:
        df_tgxd = pd.DataFrame(tgxd_data)
        df_tgxd.to_csv("data/raw/thegioixedien_raw.csv", index=False, encoding='utf-8-sig')
        print(f"[+] XONG! Lưu {len(tgxd_data)} xe vào thegioixedien_raw.csv\n")

    # --- Chạy luồng 2 ---
    print("=== 2. CÀO DỮ LIỆU: PHỐ XE ĐIỆN ===")
    pxd_url = "https://phoxedien.com/xe-may-dien/" 
    pxd_data = fetch_phoxedien(pxd_url, pages=30)
    
    if pxd_data:
        df_pxd = pd.DataFrame(pxd_data)
        df_pxd.to_csv("data/raw/phoxedien_raw.csv", index=False, encoding='utf-8-sig')
        print(f"[+] XONG! Lưu {len(pxd_data)} xe vào phoxedien_raw.csv")
        print("\n--- XEM TRƯỚC 5 DÒNG CỦA PHỐ XE ĐIỆN ---")
        print(df_pxd.head())