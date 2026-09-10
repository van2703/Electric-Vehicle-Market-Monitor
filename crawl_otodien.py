import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re  # Thêm thư viện Regex để bóc tách chữ số

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9"
}

# ======================
# MODULE LÀM SẠCH GIÁ
# ======================
def clean_price_to_number(price_str):
    """
    Biến đổi chuỗi giá tiếng Việt thành số nguyên VNĐ.
    VD: 
      - "695 triệu" -> 695000000
      - "1 tỷ 195 triệu" -> 1195000000
      - "1 tỷ 2" -> 1200000000
      - "1.5 tỷ" -> 1500000000
      - "695.000.000 đ" -> 695000000
    """
    if not price_str or price_str == "N/A": 
        return None
        
    text = price_str.lower().strip()
    
    # 1. Trường hợp có chứa đơn vị "tỷ" hoặc "triệu" / "tr"
    if 'tỷ' in text or 'triệu' in text or 'tr' in text:
        total = 0.0
        
        # Bóc tách phần "tỷ" (VD: "1 tỷ", "1.5 tỷ", "1,2 tỷ")
        ty_match = re.search(r'(\d+(?:[.,]\d+)?)\s*tỷ', text)
        if ty_match:
            total += float(ty_match.group(1).replace(',', '.')) * 1_000_000_000
            
        # Bóc tách phần "triệu" / "tr" (VD: "195 triệu", "550 triệu", "50 tr")
        trieu_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(?:triệu|tr)', text)
        if trieu_match:
            total += float(trieu_match.group(1).replace(',', '.')) * 1_000_000
            
        # Xử lý trường hợp nói tắt: "1 tỷ 2" hoặc "1 tỷ 195" (sau chữ "tỷ" có số nhưng không có chữ "triệu")
        if ty_match and not trieu_match:
            after_ty = text.split('tỷ', 1)[1].strip()
            num_after = re.search(r'^(\d+(?:[.,]\d+)?)', after_ty)
            if num_after:
                val = float(num_after.group(1).replace(',', '.'))
                # Nếu số sau tỷ < 10 (VD: "1 tỷ 2" nghĩa là 1.2 tỷ -> cộng thêm 200 triệu)
                if val < 10:
                    total += val * 100_000_000
                else:
                    # VD: "1 tỷ 195" nghĩa là 1 tỷ + 195 triệu
                    total += val * 1_000_000
                    
        return int(total) if total > 0 else None
        
    # 2. Xử lý dự phòng nếu web ghi hẳn số (VD: 695.000.000 đ, 11.990.000₫)
    clean_num = re.sub(r'[^\d]', '', price_str)
    return int(clean_num) if clean_num else None

# ======================
# HÀM CÀO Ô TÔ ĐIỆN 
# ======================
def fetch_otodien(base_url, pages=2):
    all_cars = []
    
    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"[*] [Ô Tô Điện] Đang tải trang {page}: {url}")
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code != 200: 
                print(f"[-] Lỗi truy cập trang {page} (Code: {res.status_code})")
                continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            price_tags = soup.find_all('strong', class_='feedCar__price')
            
            if not price_tags:
                print("[!] Không tìm thấy giá ô tô nào. Có thể đã lật hết trang.")
                break
                
            for p_tag in price_tags:
                # 1. Lấy text giá thô (VD: "695 triệu")
                price_raw = p_tag.text.strip()
                
                # 2. CHẠY HÀM DATA TRANSFORMATION ĐỂ LÀM SẠCH GIÁ
                price_clean = clean_price_to_number(price_raw)
                
                title_tag = p_tag.find_previous('h3')
                title = title_tag.text.strip() if title_tag else "N/A"
                
                if title and len(title) > 3:
                    # BỘ LỌC CHỐNG TRÙNG LẶP
                    if len(all_cars) > 0 and all_cars[-1]["subject"] == title:
                        all_cars[-1]["price_raw"] = price_raw
                        all_cars[-1]["price_clean"] = price_clean
                    else:
                        all_cars.append({
                            "source": "otodien_B2C",
                            "subject": title,
                            "price_raw": price_raw,
                            "price_clean": price_clean,
                            "battery_status": "Cần phân tích" 
                        })
                        
        except Exception as e:
            print(f"[X] Lỗi tại trang {page}: {e}")
            
        time.sleep(2) 
        
    return all_cars

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    
    print("=== CÀO DỮ LIỆU B2C: Ô TÔ ĐIỆN ===")
    oto_url = "https://otodien.vn/oto" 
    oto_data = fetch_otodien(oto_url, pages=20)

    if oto_data:
        df_oto = pd.DataFrame(oto_data)
        df_oto.to_csv("data/raw/otodien_raw.csv", index=False, encoding='utf-8-sig')
        print(f"[+] XONG! Lưu {len(oto_data)} ô tô vào otodien_raw.csv")
        print("\n--- XEM TRƯỚC 5 DÒNG CỦA Ô TÔ ĐIỆN ---")
        print(df_oto[['subject', 'price_raw', 'price_clean']].head())