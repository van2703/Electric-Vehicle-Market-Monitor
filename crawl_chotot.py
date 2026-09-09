import time
import requests
import json
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def fetch_hanoi_evs(pages=2):
    all_ads = []
    base_url = "https://gateway.chotot.com/v1/public/ad-listing"
    limit = 20 # Tăng lên 20 tin 1 trang cho nhanh
    
    for page in range(pages):
        offset = page * limit
        # Đưa chính xác các tham số bạn vừa tìm được vào đây
        params = {
            "limit": limit,
            "offset": offset,
            "cg": "2020",
            "motorbiketype": "4",
            "region_v2": "12000",
            "st": "s,k"
        }
        
        print(f"[*] Đang tải trang {page + 1} (offset {offset})...")
        res = requests.get(base_url, headers=HEADERS, params=params, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            ads = data.get("ads", [])
            all_ads.extend(ads)
            print(f"[+] Lấy thành công {len(ads)} bài đăng.")
        else:
            print(f"[-] Lỗi {res.status_code}")
            
        time.sleep(2)  # Nghỉ 2 giây giữa các lần gọi để không bị chặn
        
    # Lưu file
    os.makedirs("data/raw", exist_ok=True)
    with open("data/raw/hanoi_ev_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_ads, f, ensure_ascii=False, indent=2)
    print(f"[*] XONG! Đã lưu tổng cộng {len(all_ads)} tin vào thư mục data/raw/")

if __name__ == "__main__":
    fetch_hanoi_evs(pages=3)