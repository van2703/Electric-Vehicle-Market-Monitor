"""
Clean chotot_xemay_raw.json -> data/interim/chotot_xemay_clean.csv

Input : data/raw/chotot_xemay_raw.json
Output: data/interim/chotot_xemay_clean.csv

Nguyên tắc lọc feature (Feature Selection for Valuation & Data Science):
- Giữ lại các cột quan trọng phục vụ định giá, phân tích hao mòn và phân tích thị trường:
  + Target: price_vnd
  + Độ hao mòn & thời gian: condition, regdate_year, mileage_km, posted_at
  + Đặc tính xe: brand_name, model_name, origin_name, evehiclemotor_flag, motorbike_capacity
  + NLP: title, description (bóc tách pin, tình trạng xe, phụ kiện)
  + Địa lý: region_name, area_name, ward_name, latitude, longitude
  + Người bán & uy tín: account_id, seller_name, company_ad, is_shop_verified, seller_live_ads, seller_sold_ads, average_rating, total_rating
  + Chất lượng tin: n_images, veh_inspected, vehicleguarantee
- Loại bỏ hoàn toàn 62 cột thừa:
  + 14 cột list rỗng 100% (params, ad_features, cta_buttons, v.v.)
  + 7 cột tính năng UI/quảng cáo nội bộ Chợ Tốt (is_sticky, is_zalo_show, job_tier, v.v.)
  + Các chuỗi URL ảnh cồng kềnh (images, videos, main_image)
  + Các ID định danh trùng lặp (source_listing_id, account_oid, region_name_v3, v.v.)
  + Các hằng số vô dụng (source, category_name, vehicle_type, v.v.)
"""

import json
from pathlib import Path
from datetime import datetime
import sys
import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "chotot_xemay_raw.json"
DICT_PATH = BASE_DIR / "data" / "raw" / "chotot_dictionary.json"
OUT_PATH = BASE_DIR / "data" / "interim" / "chotot_xemay_clean.csv"


# ---------- Load Dictionary ----------
brand_map = {}
model_map = {}
origin_map = {}

if DICT_PATH.exists():
    with open(DICT_PATH, encoding="utf-8") as f:
        dict_data = json.load(f).get("xemay", {})
        brand_map = dict_data.get("motorbikebrand", {}).get("options", {})
        model_map = dict_data.get("model_id_map", {})
        origin_map = dict_data.get("motorbikeorigin", {}).get("options", {})


# ---------- Helpers ----------
def ms_to_datetime(ms):
    """Epoch ms -> pandas Timestamp. None nếu không parse được."""
    if ms is None:
        return None
    try:
        return pd.to_datetime(int(ms), unit="ms")
    except (TypeError, ValueError, OverflowError):
        return None


# ---------- Clean one record ----------
def clean_record(r: dict) -> dict:
    seller = r.get("seller_info") or {}

    brand_id = r.get("motorbikebrand")
    model_id = r.get("motorbikemodel")
    origin_id = r.get("motorbikeorigin")

    # Ưu tiên mileage_v2, fallback về mileage nếu có
    mileage = r.get("mileage_v2")
    if mileage is None:
        mileage = r.get("mileage")

    # Tên người bán
    seller_name = r.get("full_name") or seller.get("full_name") or r.get("account_name")

    # Số tin đã bán
    sold_ads = seller.get("sold_ads")
    if sold_ads is None:
        sold_ads = r.get("sold_ads")

    return {
        # 1. Định danh bài đăng
        "list_id":                      r.get("list_id"),

        # 2. Nội dung văn bản
        "title":                        r.get("subject"),
        "description":                  r.get("body"),
        "posted_at":                    ms_to_datetime(r.get("list_time")),

        # 3. Giá bán (Biến mục tiêu định giá)
        "price_vnd":                    r.get("price"),

        # 4. Độ hao mòn & thời gian (Key Depreciation Features)
        "condition":                    r.get("condition_ad_name"),
        "regdate_year":                 r.get("regdate"),
        "mileage_km":                   mileage,

        # 5. Thông số kỹ thuật xe
        "brand_id":                     brand_id,
        "brand_name":                   brand_map.get(str(brand_id)),
        "model_id":                     model_id,
        "model_name":                   model_map.get(str(model_id)),
        "origin_id":                    origin_id,
        "origin_name":                  origin_map.get(str(origin_id)),
        "evehiclemotor_flag":           r.get("evehiclemotor"),
        "motorbike_capacity":           r.get("motorbikecapacity"),

        # 6. Vị trí địa lý
        "region_name":                  r.get("region_name"),
        "area_name":                    r.get("area_name"),
        "ward_name":                    r.get("ward_name"),
        "latitude":                     r.get("latitude"),
        "longitude":                    r.get("longitude"),

        # 7. Người bán & Uy tín
        "account_id":                   r.get("account_id"),
        "seller_name":                  seller_name,
        "company_ad":                   bool(r.get("company_ad", False)),
        "is_shop_verified":             bool(r.get("is_shop_verified", False)),
        "seller_live_ads":              seller.get("live_ads"),
        "seller_sold_ads":              sold_ads,
        "average_rating":               r.get("average_rating"),
        "total_rating":                 r.get("total_rating"),

        # 8. Chất lượng tin & Bảo hành
        "n_images":                     r.get("number_of_images"),
        "veh_inspected":                r.get("veh_inspected"),
        "vehicleguarantee":             r.get("vehicleguarantee"),
    }


# ---------- Main ----------
def main() -> None:
    print(f"[1/4] Đọc raw: {RAW_PATH}")
    with open(RAW_PATH, encoding="utf-8") as f:
        records = json.load(f)
    print(f"      Số record đầu vào: {len(records)}")

    print(f"[2/4] Trích xuất và chọn lọc features phục vụ định giá...")
    rows = [clean_record(r) for r in records]
    df = pd.DataFrame(rows)

    print(f"[3/4] Loại bỏ trùng lặp và bản ghi lỗi...")
    before = len(df)
    df = df.dropna(subset=["list_id"])
    dropped_missing = before - len(df)
    if dropped_missing:
        print(f"      Drop {dropped_missing} record thiếu list_id")

    before = len(df)
    df = df.drop_duplicates(subset=["list_id"], keep="first")
    dropped_dup = before - len(df)
    if dropped_dup:
        print(f"      Drop {dropped_dup} record trùng list_id")

    # Cast datetime cho gọn khi ghi CSV
    df["posted_at"] = pd.to_datetime(df["posted_at"], errors="coerce")

    print(f"[4/4] Ghi output: {OUT_PATH}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print(f"\n=== SUMMARY CHỢ TỐT XE MÁY ĐIỆN (INTERIM CLEANED) ===")
    print(f"Số record duy nhất: {len(df)}")
    print(f"Số cột tinh gọn: {len(df.columns)} (Đã loại bỏ hơn 60 cột rác)")
    print(f"\nDanh sách cột: {df.columns.tolist()}")

    print("\n--- Missing per column (%) ---")
    missing = (df.isna().mean() * 100).sort_values(ascending=False)
    for col, pct in missing.items():
        if pct > 0:
            print(f"  {col:<25} {pct:>6.1f}%")

    print("\n--- Top 5 Hãng xe máy điện phổ biến nhất ---")
    if "brand_name" in df:
        print(df["brand_name"].value_counts(dropna=False).head(5).to_string())

    print("\n--- Thống kê giá (VND) ---")
    p = df["price_vnd"].dropna()
    if len(p):
        print(f"  Min    : {int(p.min()):>15,}")
        print(f"  Median : {int(p.median()):>15,}")
        print(f"  Max    : {int(p.max()):>15,}")


if __name__ == "__main__":
    main()