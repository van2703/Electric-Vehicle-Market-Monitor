import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9"
}

def fetch_thegioixedien(base_url, pages=2):
    all_bikes = []
    
    for page in range(1, pages + 1):
        # Thiết lập URL phân trang (VD: thegioixedien.com.vn/avd33_xe-may-dien/?page=2)
        url = f"{base_url}?page={page}" if page > 1 else base_url
        print(f"[*] Đang tải trang {page}: {url}")
        
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code != 200:
                print(f"[-] Lỗi truy cập trang {page} (Code: {res.status_code})")
                continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 1. Chỉ tìm các thẻ chứa giá tiền (Mỏ neo độc nhất của sản phẩm)
            price_tags = soup.find_all('span', class_='gia_ban')
            
            if not price_tags:
                print("[!] Không tìm thấy giá nào. Có thể đã lật hết trang.")
                break
                
            for p_tag in price_tags:
                # Lấy text giá (VD: "22,990,000 đ")
                price = p_tag.text.strip()
                
                # 2. Dùng find_previous() để tìm thẻ <h3> xuất hiện NGAY TRƯỚC mức giá này
                title_tag = p_tag.find_previous('h3')
                title = title_tag.text.strip() if title_tag else "N/A"
                
                all_bikes.append({
                    "source": "thegioixedien_B2C",
                    "subject": title,
                    "price_raw": price,
                    "battery_status": "Kèm pin"
                })
                
        except Exception as e:
            print(f"[X] Lỗi tại trang {page}: {e}")
            
        time.sleep(2) # Nghỉ 2s tránh bị web chặn
        
    return all_bikes

if __name__ == "__main__":
    target_url = "https://thegioixedien.com.vn/avd33_xe-may-dien/"
    
    print("=== BẮT ĐẦU CÀO DỮ LIỆU ĐẠI LÝ (THEGIOIXEDIEN) ===")
    scraped_data = fetch_thegioixedien(target_url, pages=20)
    
    if scraped_data:
        df = pd.DataFrame(scraped_data)
        
        # Lưu thẳng ra CSV
        os.makedirs("data/raw", exist_ok=True)
        file_path = "data/raw/thegioixedien_raw.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        print(f"\n[+] XONG! Đã cào thành công {len(scraped_data)} xe.")
        print(f"[*] Dữ liệu được lưu tại: {file_path}")
        print("\n--- XEM TRƯỚC 5 DÒNG ĐẦU ---")
        print(df.head())
    else:
        print("\n[-] Không lấy được dữ liệu.")