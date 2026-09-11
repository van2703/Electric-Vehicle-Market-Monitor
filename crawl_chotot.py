import time
import requests
import json
import os
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def fetch_data(params, output_filename, pages=20):
    all_ads = []
    seen_ids = set()
    base_url = "https://gateway.chotot.com/v1/public/ad-listing"
    limit = 50
    
    for page in range(pages):
        o = page * limit
        params["limit"] = limit
        params["o"] = o
        if "offset" in params:
            del params["offset"]
        
        print(f"[*] Đang tải trang {page + 1}/{pages} (o={o})...")
        try:
            res = requests.get(base_url, headers=HEADERS, params=params, timeout=12)
            if res.status_code == 200:
                data = res.json()
                ads = data.get("ads", [])
                if not ads:
                    print(f"[!] Trang {page + 1} trả về rỗng. Đã lấy hết dữ liệu.")
                    break
                
                new_count = 0
                for ad in ads:
                    ad_id = ad.get("list_id") or ad.get("ad_id")
                    if ad_id and ad_id not in seen_ids:
                        seen_ids.add(ad_id)
                        all_ads.append(ad)
                        new_count += 1
                print(f"[+] Nhận {len(ads)} tin (mới {new_count}, tích lũy {len(all_ads)} unique).")
            else:
                print(f"[-] Lỗi {res.status_code} tại trang {page + 1}.")
        except Exception as e:
            print(f"[X] Ngoại lệ tại trang {page + 1}: {e}")
            
        time.sleep(1.5)  # Nghỉ tránh bị giới hạn tần suất
        
    # Lưu file JSON
    os.makedirs("data/raw", exist_ok=True)
    file_path = f"data/raw/{output_filename}"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_ads, f, ensure_ascii=False, indent=2)
    print(f"[*] XONG! Đã lưu {len(all_ads)} tin duy nhất vào: {file_path}\n")

if __name__ == "__main__":
    # ==========================================
    # 1. CẤU HÌNH VÀ CÀO: XE MÁY ĐIỆN
    # ==========================================
    print("=== BẮT ĐẦU CÀO XE MÁY ĐIỆN ===")
    params_bike = {
        "cg": "2020",             # Danh mục: Xe máy
        "motorbiketype": "4",     # Động cơ: Điện
    }
    fetch_data(params=params_bike, output_filename="chotot_xemay_raw.json", pages=20)
    
    # ==========================================
    # 2. CẤU HÌNH VÀ CÀO: Ô TÔ ĐIỆN
    # ==========================================
    print("=== BẮT ĐẦU CÀO Ô TÔ ĐIỆN ===")
    params_car = {
        "cg": "2010",             # Danh mục: Ô tô
        "fuel": "4"               # Động cơ: Điện
    }
    fetch_data(params=params_car, output_filename="chotot_oto_raw.json", pages=20)