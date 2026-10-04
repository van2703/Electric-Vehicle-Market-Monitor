import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
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

# ======================
# MODULE LÀM SẠCH GIÁ
# ======================
def clean_price_to_number(price_str):
    """
    Biến đổi chuỗi giá thành số nguyên VNĐ.
    Hỗ trợ các dạng: "11.990.000₫", "18.500.000 ₫", "695 triệu", "1 tỷ 2".
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

    # 2. Xử lý số thuần túy (VD: "11.990.000₫", "18,500,000 đ")
    clean_num = re.sub(r'[^\d]', '', price_str)
    return int(clean_num) if clean_num else None


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
                price_raw = p_tag.text.strip()
                price_clean = clean_price_to_number(price_raw)
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
    from pathlib import Path
    base_dir = Path(__file__).resolve().parents[2]
    raw_dir = base_dir / "data" / "raw" / "b2c"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    print("=== CÀO DỮ LIỆU: PHỐ XE ĐIỆN ===")
    pxd_url = "https://phoxedien.com/xe-may-dien/" 
    pxd_data = fetch_phoxedien(pxd_url, pages=30)
    
    if pxd_data:
        df_pxd = pd.DataFrame(pxd_data)
        file_path = raw_dir / "phoxedien_raw.csv"
        df_pxd.to_csv(file_path, index=False, encoding='utf-8-sig')
        print(f"[+] XONG! Lưu {len(pxd_data)} xe vào {file_path}")
        print("\n--- XEM TRƯỚC 5 DÒNG CỦA PHỐ XE ĐIỆN ---")
        print(df_pxd.head())
    else:
        print("\n[-] Không lấy được dữ liệu.")
