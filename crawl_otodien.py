import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

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
                if val < 10:
                    total += val * 100_000_000
                else:
                    total += val * 1_000_000
                    
        return int(total) if total > 0 else None
        
    # 2. Xử lý dự phòng nếu web ghi hẳn số (VD: 695.000.000 đ, 11.990.000₫)
    clean_num = re.sub(r'[^\d]', '', price_str)
    return int(clean_num) if clean_num else None

# ==========================================
# MODULE BÓC TÁCH PIN TỪ LỜI NGƯỜI BÁN
# ==========================================
def extract_battery_status(text):
    """
    Phân loại tình trạng pin dựa trực tiếp trên từ khóa người bán viết 
    trong Tiêu đề và phần Thông tin mô tả chi tiết.
    """
    if not text:
        return "Chưa rõ"
        
    text_norm = unicodedata.normalize('NFKC', str(text)).lower()
    
    # Từ khóa xác định thuê pin
    rent_patterns = [
        r'\bthuê pin\b', r'\bbản thuê pin\b', r'\bxe thuê pin\b',
        r'\bcọc pin\b', r'\bkhông kèm pin\b', r'\bchưa kèm pin\b',
        r'\bchưa bao gồm pin\b', r'\bk kèm pin\b', r'\bko kèm pin\b',
        r'\bkhông pin\b', r'\bchưa pin\b', r'\bk pin\b', r'\bko pin\b'
    ]
    
    # Từ khóa xác định mua đứt pin / kèm pin
    buy_patterns = [
        r'\bmua đứt pin\b', r'\bbản mua đứt pin\b', r'\bbản mua pin\b',
        r'\bxe mua pin\b', r'\bđã mua pin\b', r'\bmua pin\b',
        r'\bkèm pin\b', r'\bđã kèm pin\b', r'\bbao pin\b',
        r'\bsẵn pin\b', r'\bcả pin\b', r'\bbao gồm pin\b', r'\bđã bao gồm pin\b'
    ]
    
    has_rent = any(re.search(p, text_norm) for p in rent_patterns)
    has_buy = any(re.search(p, text_norm) for p in buy_patterns)
    
    if has_buy and not has_rent:
        return "Kèm pin"
    elif has_rent and not has_buy:
        return "Thuê pin"
    elif has_buy and has_rent:
        # Nếu bài viết nhắc cả hai, ưu tiên cụm từ chỉ bản chất xe
        if re.search(r'\b(bản thuê pin|xe thuê pin|thuê pin tiên phong)\b', text_norm):
            return "Thuê pin"
        if re.search(r'\b(bản mua pin|xe mua pin|mua đứt pin)\b', text_norm):
            return "Kèm pin"
        return "Thuê pin"
        
    return "Chưa rõ"

def fetch_car_detail(session, detail_url):
    """
    Tải trang chi tiết của xe để lấy phần 'Thông tin mô tả' của người bán.
    """
    if not detail_url:
        return ""
    try:
        res = session.get(detail_url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for b in soup.find_all('div', class_='block-listings-item'):
                h = b.find(['h2', 'h3', 'h4'])
                if h and 'mô tả' in h.text.lower():
                    # Lấy text mô tả, bỏ chữ 'Thông tin mô tả' ở đầu
                    desc_text = b.get_text(separator=' ', strip=True)
                    desc_text = re.sub(r'^thông tin mô tả\s*', '', desc_text, flags=re.IGNORECASE)
                    return desc_text
    except Exception:
        pass
    return ""

# ======================
# HÀM CÀO Ô TÔ ĐIỆN 
# ======================
def fetch_otodien(base_url, pages=20):
    session = requests.Session()
    session.headers.update(HEADERS)
    
    raw_car_list = []
    
    # 1. Thu thập danh sách thẻ xe từ các trang
    for page in range(1, pages + 1):
        url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"[*] [Ô Tô Điện] Đang tải danh sách trang {page}: {url}")
        
        try:
            res = session.get(url, timeout=10)
            if res.status_code != 200: 
                print(f"[-] Lỗi truy cập trang {page} (Code: {res.status_code})")
                continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            price_tags = soup.find_all('strong', class_='feedCar__price')
            
            if not price_tags:
                print("[!] Không tìm thấy giá ô tô nào. Có thể đã lật hết trang.")
                break
                
            for p_tag in price_tags:
                price_raw = p_tag.text.strip()
                price_clean = clean_price_to_number(price_raw)
                
                title_tag = p_tag.find_previous('h3')
                title = title_tag.text.strip() if title_tag else "N/A"
                
                # Bóc tách link chi tiết
                card = p_tag.find_parent('div', class_='listing-car-item') or p_tag.find_parent('div', class_='rmv_txt_drctn')
                a_tag = card.find('a') if card else None
                href = a_tag.get('href') if a_tag else ""
                detail_url = f"https://otodien.vn{href}" if href.startswith('/') else href
                
                if title and len(title) > 3:
                    # Chống trùng lặp tiêu đề liền kề
                    if len(raw_car_list) > 0 and raw_car_list[-1]["subject"] == title:
                        continue
                    raw_car_list.append({
                        "subject": title,
                        "price_raw": price_raw,
                        "price_clean": price_clean,
                        "detail_url": detail_url
                    })
                        
        except Exception as e:
            print(f"[X] Lỗi tại trang {page}: {e}")
            
        time.sleep(1)
        
    print(f"\n[+] Đã tìm thấy {len(raw_car_list)} xe. Bắt đầu cào chi tiết 'Thông tin mô tả'...")
    
    # 2. Cào mô tả chi tiết bằng ThreadPoolExecutor (đa luồng an toàn, 5 workers)
    all_cars = []
    current_year = 2026
    
    def process_item(item):
        subject = item["subject"]
        desc = fetch_car_detail(session, item["detail_url"]) if item["detail_url"] else ""
        full_text = unicodedata.normalize('NFKC', subject + " " + desc).lower()
        battery = extract_battery_status(full_text)
        
        # 1. Bóc tách năm sản xuất
        year = None
        m_yr = re.search(r'\b(202[0-6])\b', subject + " " + desc)
        if m_yr:
            year = int(m_yr.group(1))
        else:
            m_vin = re.search(r'vin\s?(?:20)?(2[1-6])\b', subject + " " + desc, re.IGNORECASE)
            if m_vin:
                year = int('20' + m_vin.group(1))

        # 2. Bóc tách ODO (số km đã đi)
        odo = None
        m_sub = re.search(r'(\d+(?:[.,]\d+)?)\s*km\b', subject, re.IGNORECASE)
        if m_sub:
            try:
                odo = int(m_sub.group(1).replace('.', '').replace(',', ''))
            except:
                pass
        if odo is None and desc:
            m_v = re.search(r'odo\s*(\d+(?:[.,]\d+)?)\s*(?:v|vạn)\b', desc, re.IGNORECASE)
            if m_v:
                try:
                    odo = int(float(m_v.group(1).replace(',', '.')) * 10000)
                except:
                    pass
            else:
                m_km_desc = re.search(r'odo\s*(\d+(?:[.,]\d+)?)\s*km\b', desc, re.IGNORECASE)
                if m_km_desc:
                    try:
                        odo = int(m_km_desc.group(1).replace('.', '').replace(',', ''))
                    except:
                        pass

        # 3. Tình trạng xe (Mới vs Đã sử dụng)
        is_new = bool(re.search(r'(mới 100%|new 100%|xe mới\b|sẵn xe giao ngay|chính thức ra mắt|ưu đãi khủng)', full_text))
        if odo is not None and odo > 0:
            condition = "Đã sử dụng"
        elif is_new or (odo is not None and odo == 0):
            condition = "Mới"
            if odo is None:
                odo = 0
        else:
            condition = "Đã sử dụng"

        if year is None and condition == "Mới":
            year = current_year
            age = 0
        elif year is not None:
            age = current_year - year
        else:
            age = 0

        # 4. Cường độ chạy (km/năm)
        km_per_year = None
        if odo is not None:
            if condition == "Mới" or odo == 0:
                km_per_year = 0
            else:
                km_per_year = int(round(odo / max(age, 1)))

        return {
            "source": "otodien_B2C",
            "subject": subject,
            "price_raw": item["price_raw"],
            "price_clean": item["price_clean"],
            "odo": odo,
            "year": year,
            "age": age,
            "condition": condition,
            "km_per_year": km_per_year,
            "battery_status": battery,
            "description": desc
        }

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_item = {executor.submit(process_item, item): item for item in raw_car_list}
        completed_count = 0
        for future in as_completed(future_to_item):
            car_data = future.result()
            all_cars.append(car_data)
            completed_count += 1
            if completed_count % 30 == 0 or completed_count == len(raw_car_list):
                print(f"  -> Đã cào chi tiết: {completed_count}/{len(raw_car_list)} xe")
                
    return all_cars

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    
    print("=== CÀO DỮ LIỆU B2C: Ô TÔ ĐIỆN (KÈM MÔ TẢ & BÓC TÁCH PIN) ===")
    oto_url = "https://otodien.vn/oto" 
    oto_data = fetch_otodien(oto_url, pages=20)

    if oto_data:
        df_oto = pd.DataFrame(oto_data)
        df_oto.to_csv("data/raw/otodien_raw.csv", index=False, encoding='utf-8-sig')
        print(f"\n[+] XONG! Đã lưu {len(oto_data)} ô tô vào data/raw/otodien_raw.csv")
        print("\n=== THỐNG KÊ TÌNH TRẠNG PIN TỪ MÔ TẢ THỰC TẾ ===")
        print(df_oto['battery_status'].value_counts())
        print("\n--- XEM TRƯỚC 5 DÒNG CÓ ĐỦ MÔ TẢ & PIN ---")
        cols_preview = ['subject', 'price_raw', 'battery_status']
        print(df_oto[cols_preview].head(10).to_string())