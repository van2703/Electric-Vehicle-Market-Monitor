import requests
import json
import os
import sys
import pandas as pd

# Đảm bảo console Windows in tiếng Việt UTF-8 không lỗi charmap
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

def fetch_params_for_category(category_id):
    """
    Cào toàn bộ Metadata và Từ điển tham số của một danh mục (Xe máy: 2020, Ô tô: 2010)
    từ Gateway API chính thức của Chợ Tốt.
    """
    url = f"https://gateway.chotot.com/v1/public/trans/params?category={category_id}"
    print(f"[*] Đang tải từ điển cho Category {category_id} từ: {url}")
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"[-] Lỗi HTTP {res.status_code}")
    except Exception as e:
        print(f"[X] Lỗi kết nối: {e}")
    return None

def fetch_regions():
    """
    Cào từ điển Tỉnh/Thành phố (Region) và Quận/Huyện (Area)
    """
    url = "https://gateway.chotot.com/v1/public/web-proxy-api/loadRegionsV2"
    print(f"[*] Đang tải từ điển Tỉnh thành / Quận huyện từ: {url}")
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        print(f"[X] Lỗi tải Regions: {e}")
    return None

def parse_param_dictionary(raw_data, model_param_key):
    """
    Phân rã cấu trúc ad_params của Chợ Tốt thành các dict tra cứu trực tiếp.
    """
    params_dict = {}
    models_list = []
    
    s_data = raw_data.get("ad_params", {}).get("s", {})
    groups = s_data.get("params", [])
    
    brand_map = {}
    
    # 1. Trích xuất các tham số phẳng (flat parameters)
    for group in groups:
        for p in group.get("params", []):
            pkey = p.get("param")
            plabel = p.get("label")
            options = p.get("options", [])
            
            if options:
                opt_map = {str(opt["id"]): opt["label"] for opt in options if "id" in opt and "label" in opt}
                params_dict[pkey] = {
                    "label": plabel,
                    "options": opt_map
                }
                
                # Lưu lại brand_map để ghép tên thương hiệu cho models
                if pkey in ["motorbikebrand", "carbrand"]:
                    brand_map = opt_map
                    
            # 2. Trích xuất cây Model phân cấp (carmodel hoặc motorbikemodel)
            if model_param_key in p:
                model_tree = p[model_param_key]
                for brand_id, b_data in model_tree.items():
                    b_id_str = str(brand_id)
                    brand_name = brand_map.get(b_id_str, f"Brand_{b_id_str}")
                    for m_opt in b_data.get("options", []):
                        m_id = str(m_opt["id"])
                        m_name = m_opt["label"]
                        models_list.append({
                            "Brand_ID": b_id_str,
                            "Brand_Name": brand_name,
                            "Model_ID": m_id,
                            "Model_Name": m_name
                        })
                        
    return params_dict, models_list

def crawl_all_chotot_dictionaries():
    print("=== TỰ ĐỘNG CÀO TỪ ĐIỂN CHỢ TỐT CHO DATA PIPELINE ===")
    from pathlib import Path
    base_dir = Path(__file__).resolve().parents[2]
    dict_dir = base_dir / "data" / "dictionaries"
    dict_dir.mkdir(parents=True, exist_ok=True)
    
    full_dictionary = {
        "xemay": {},
        "oto": {},
        "regions": {},
        "areas": {}
    }
    
    all_models_rows = []
    
    # ==========================================
    # 1. TỪ ĐIỂN XE MÁY (Category 2020)
    # ==========================================
    raw_xemay = fetch_params_for_category("2020")
    if raw_xemay:
        params_xemay, models_xemay = parse_param_dictionary(raw_xemay, "motorbikemodel")
        full_dictionary["xemay"] = params_xemay
        
        # Tạo map nhanh model_id -> model_name
        model_id_to_name = {}
        for item in models_xemay:
            model_id_to_name[item["Model_ID"]] = item["Model_Name"]
            all_models_rows.append({
                "Category": "Xe máy",
                **item
            })
        full_dictionary["xemay"]["model_id_map"] = model_id_to_name
        print(f"[+] Xe máy: Đã lấy {len(params_xemay)} loại tham số và {len(models_xemay)} models.")

    # ==========================================
    # 2. TỪ ĐIỂN Ô TÔ (Category 2010)
    # ==========================================
    raw_oto = fetch_params_for_category("2010")
    if raw_oto:
        params_oto, models_oto = parse_param_dictionary(raw_oto, "carmodel")
        full_dictionary["oto"] = params_oto
        
        model_id_to_name = {}
        for item in models_oto:
            model_id_to_name[item["Model_ID"]] = item["Model_Name"]
            all_models_rows.append({
                "Category": "Ô tô",
                **item
            })
        full_dictionary["oto"]["model_id_map"] = model_id_to_name
        print(f"[+] Ô tô: Đã lấy {len(params_oto)} loại tham số và {len(models_oto)} models.")

    # ==========================================
    # 3. TỪ ĐIỂN ĐỊA LÝ (Regions & Areas)
    # ==========================================
    raw_regions = fetch_regions()
    if raw_regions:
        reg_map = {}
        area_map = {}
        regions_dict = raw_regions.get("regionFollowId", {}).get("entities", {}).get("regions", {})
        if isinstance(regions_dict, dict):
            for reg_id, reg_info in regions_dict.items():
                if isinstance(reg_info, dict):
                    reg_name = reg_info.get("name")
                    if reg_name:
                        reg_map[str(reg_id)] = reg_name
                    areas = reg_info.get("area", {})
                    if isinstance(areas, dict):
                        for area_id, area_info in areas.items():
                            if isinstance(area_info, dict) and "name" in area_info:
                                area_map[str(area_id)] = area_info["name"]
                
        full_dictionary["regions"] = reg_map
        full_dictionary["areas"] = area_map
        print(f"[+] Địa lý: Đã lấy {len(reg_map)} Tỉnh/Thành và {len(area_map)} Quận/Huyện.")

    # ==========================================
    # 4. LƯU CÁC FILE OUTPUT
    # ==========================================
    # File 1: JSON toàn diện để import trực tiếp vào Data Pipeline
    dict_json_path = dict_dir / "chotot_dictionary.json"
    with open(dict_json_path, "w", encoding="utf-8") as f:
        json.dump(full_dictionary, f, ensure_ascii=False, indent=2)
    print(f"\n[+] Lưu Từ điển JSON hoàn chỉnh tại: {dict_json_path}")
    
    # File 2: CSV Danh sách toàn bộ Hãng & Dòng xe để tra cứu trực quan
    if all_models_rows:
        df_models = pd.DataFrame(all_models_rows)
        models_csv_path = dict_dir / "chotot_models_dictionary.csv"
        df_models.to_csv(models_csv_path, index=False, encoding="utf-8-sig")
        print(f"[+] Lưu Bảng Model CSV ({len(df_models)} dòng) tại: {models_csv_path}")

    print("\n=== DEMO TRA CỨU TỪ ĐIỂN TRONG PIPELINE ===")
    # Demo tra cứu xe máy VinFast Feliz (Brand 44, Model 707)
    b_name = full_dictionary["xemay"].get("motorbikebrand", {}).get("options", {}).get("44", "Unknown")
    m_name = full_dictionary["xemay"].get("model_id_map", {}).get("707", "Unknown")
    fuel_name = full_dictionary["oto"].get("fuel", {}).get("options", {}).get("4", "Unknown")
    cond_name = full_dictionary["xemay"].get("condition_ad", {}).get("options", {}).get("1", "Unknown")
    
    print(f"[*] Mã xe máy: brand 44 -> '{b_name}', model 707 -> '{m_name}'")
    print(f"[*] Mã ô tô: fuel 4 -> '{fuel_name}'")
    print(f"[*] Tình trạng: condition_ad 1 -> '{cond_name}'")

if __name__ == "__main__":
    crawl_all_chotot_dictionaries()
