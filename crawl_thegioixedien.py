import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re

HEADERS = {
    "User-Agent": "Mozilla/50 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9"
}

# ======================
# MODULE LÀM SẠCH GIÁ
# ======================
def clean_price_to_number(price_str):
    """
    Biến đổi chuỗi giá thành số nguyên VNĐ.
    Hỗ trợ các dạng: "22,990,000 đ", "11.990.000₫", "695 triệu", "1 tỷ 2".
    """
    if not price_str or price_str == "N/A":
        return None

    text = price_str.lower().strip()

    # 1. Trường hợp có đơn vị "tỷ" hoặc "triệu" / "tr"
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
                if val < 10:
                    total += val * 100_000_000
                else:
                    total += val * 1_000_000
        return int(total) if total > 0 else None

    # 2. Xử lý số thuần túy (VD: "22,990,000 đ", "11.990.000₫")
    clean_num = re.sub(r'[^\d]', '', price_str)
    return int(clean_num) if clean_num else None


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
                price_raw = p_tag.text.strip()
                price_clean = clean_price_to_number(price_raw)
                title_tag = p_tag.find_previous('h3')
                title = title_tag.text.strip() if title_tag else "N/A"
                
                # BỘ LỌC CHỐNG TRÙNG LẶP
                if len(all_bikes) > 0 and all_bikes[-1]["subject"] == title:
                    all_bikes[-1]["price_raw"] = price_raw
                    all_bikes[-1]["price_clean"] = price_clean
                else:
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
