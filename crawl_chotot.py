import time
import requests
import json
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def fetch_data(params, output_filename, pages=10):
    all_ads = []
    base_url = "https://gateway.chotot.com/v1/public/ad-listing"
    limit = 50
    
    for page in range(pages):
        offset = page * limit
        params["limit"] = limit
        params["offset"] = offset
        
        print(f"[*] Đang tải trang {page + 1} (offset {offset})...")
        res = requests.get(base_url, headers=HEADERS, params=params, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            ads = data.get("ads", [])
            if not ads:
                print(f"[!] Trang {page + 1} trả về rỗng. Đã lấy hết dữ liệu.")
                break
            all_ads.extend(ads)
            print(f"[+] Lấy thành công {len(ads)} bài đăng.")
        else:
            print(f"[-] Lỗi {res.status_code} - Có thể API bị đổi hoặc IP bị chặn.")
            
        time.sleep(2)  # Nghỉ 2 giây tránh bị khóa IP
        
    # Lưu file JSON
    os.makedirs("data/raw", exist_ok=True)
    file_path = f"data/raw/{output_filename}"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_ads, f, ensure_ascii=False, indent=2)
    print(f"[*] XONG! Đã lưu {len(all_ads)} tin vào: {file_path}\n")

if __name__ == "__main__":
    # ==========================================
    # 1. CẤU HÌNH VÀ CÀO: XE MÁY ĐIỆN
    # ==========================================
    print("=== BẮT ĐẦU CÀO XE MÁY ĐIỆN ===")
    params_bike = {
        "cg": "2020",             # Danh mục: Xe máy
        "motorbiketype": "4",     # Động cơ: Điện
    }
    fetch_data(params=params_bike, output_filename="chotot_xemay_raw.json", pages=10)
    
    # ==========================================
    # 2. CẤU HÌNH VÀ CÀO: Ô TÔ ĐIỆN
    # ==========================================
    print("=== BẮT ĐẦU CÀO Ô TÔ ĐIỆN ===")
    params_car = {
        "cg": "2010",             # Danh mục: Ô tô
        "fuel": "4"               # Động cơ: Điện
    }
    fetch_data(params=params_car, output_filename="chotot_oto_raw.json", pages=10)