"""
Clean chotot_oto_raw.json -> data/interim/chotot_oto_clean.csv

Input : data/raw/chotot_oto_raw.json
Output: data/interim/chotot_oto_clean.csv
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


BASE_DIR = Path(__file__).resolve().parents[2]
RAW_PATH = BASE_DIR / "data" / "raw" / "c2c" / "chotot_oto_raw.json"
OUT_PATH = BASE_DIR / "data" / "interim" / "chotot_oto_clean.csv"


DROP_COLUMNS = [
    # 100% null
    "ad_features", "ad_labels", "business_days", "cta_buttons",
    "fee_type", "inspection_images", "label_campaigns", "params",
    "pty_characteristics", "specific_service_offered",
    "special_display_images", "veh_ecom_product_id", "veh_ecom_shop_id",
    # hằng số vô dụng
    "account_oid", "category_id", "category_name", "type", "job_tier",
    # gần null / vô dụng
    "address", "phone_hidden", "special_display", "stickyad_feature",
    "location_id", "is_main_street", "unique_street_id", "detail_address",
    "sticky_ad_type", "sticky_ad_platinum", "veh_inspected",
    "product_id",
]


KEEP_SINGLE_VALUE = {
    "source", "vehicle_type", "cleaned_at", "is_price_valid",
    "state", "status", "company_ad", "is_shop_verified",
    "has_video", "protection_entitlement", "veh_ecom_can_buy_now",
    "is_electric",
    "fuel_id",
}


def json_safe(v):
    if v is None:
        return None
    if isinstance(v, (list, dict)):
        if len(v) == 0:
            return None
        try:
            return json.dumps(v, ensure_ascii=False)
        except (TypeError, ValueError):
            return None
    return v


def ms_to_datetime(ms):
    if ms is None:
        return None
    try:
        return pd.to_datetime(int(ms), unit="ms")
    except (TypeError, ValueError, OverflowError):
        return None


def clean_record(r: dict, cleaned_at: str) -> dict:
    seller = r.get("seller_info") or {}

    return {
        # ----- Định danh -----
        "source":                       "chotot",
        "vehicle_type":                 "car",
        "source_listing_id":            r.get("ad_id"),
        "list_id":                      r.get("list_id"),
        "cleaned_at":                   cleaned_at,

        # ----- Nội dung tin -----
        "title":                        r.get("subject"),
        "description":                  r.get("body"),
        "price_vnd":                    r.get("price"),
        "price_raw":                    r.get("price_string"),
        "is_price_valid":               not r.get("is_price_not_valid", False),
        "condition":                    r.get("condition_ad_name"),
        "condition_id":                 r.get("condition_ad"),
        "posted_at":                    ms_to_datetime(r.get("list_time")),
        "orig_posted_at":               ms_to_datetime(r.get("orig_list_time")),
        "state":                        r.get("state"),
        "status":                       r.get("status"),

        # ----- Thuộc tính xe -----
        "brand_id":                     r.get("carbrand"),
        "brand_name":                   r.get("carbrand_name"),
        "model_id":                     r.get("carmodel"),
        "model_name":                   r.get("carmodel_name"),
        "origin_id":                    r.get("carorigin"),
        "car_type_id":                  r.get("cartype"),
        "car_color_id":                 r.get("carcolor"),
        "car_seats":                    r.get("carseats"),
        "fuel_id":                      r.get("fuel"),
        "gearbox_id":                   r.get("gearbox"),
        "mfdate_year":                  r.get("mfdate"),
        "mileage_km":                   r.get("mileage_v2"),
        "mileage_km_alt":               r.get("mileage"),
        "number_of_owners":             r.get("number_of_owners"),
        "valid_registration":           r.get("valid_registration"),
        "include_accessories":          r.get("include_accessories"),
        "is_electric":                  True,

        # ----- Vị trí -----
        "region_id":                    r.get("region"),
        "region_name":                  r.get("region_name"),
        "region_name_v3":               r.get("region_name_v3"),
        "region_id_v2":                 r.get("region_v2"),
        "area_id":                      r.get("area"),
        "area_name":                    r.get("area_name"),
        "area_id_v2":                   r.get("area_v2"),
        "ward_id":                      r.get("ward"),
        "ward_name":                    r.get("ward_name"),
        "ward_name_v3":                 r.get("ward_name_v3"),
        "latitude":                     r.get("latitude"),
        "longitude":                    r.get("longitude"),

        # ----- Người bán -----
        "account_id":                   r.get("account_id"),
        "account_name":                 r.get("account_name"),
        "seller_full_name":             r.get("full_name"),
        "seller_name":                  seller.get("full_name"),
        "seller_live_ads":              seller.get("live_ads"),
        "seller_sold_ads":              seller.get("sold_ads"),
        "company_ad":                   r.get("company_ad"),
        "sold_ads":                     r.get("sold_ads"),
        "is_shop_verified":             r.get("is_shop_verified"),
        "shop_alias":                   r.get("shop_alias"),
        "shop":                         json_safe(r.get("shop")),
        "average_rating":               r.get("average_rating"),
        "total_rating":                 r.get("total_rating"),
        "average_rating_for_seller":    r.get("average_rating_for_seller"),
        "total_rating_for_seller":      r.get("total_rating_for_seller"),

        # ----- Media -----
        "main_image":                   r.get("image"),
        "n_images":                     r.get("number_of_images"),
        "has_video":                    r.get("has_video"),
        "contain_videos":               r.get("contain_videos"),
        "images":                       json_safe(r.get("images")),
        "videos":                       json_safe(r.get("videos")),

        # ----- Trạng thái / quảng cáo -----
        "is_sticky":                    r.get("is_sticky"),
        "is_zalo_show":                 r.get("is_zalo_show"),
        "protection_entitlement":       r.get("protection_entitlement"),
        "veh_ecom_can_buy_now":         r.get("veh_ecom_can_buy_now"),
    }


def main() -> None:
    print(f"[1/5] Đọc raw: {RAW_PATH}")
    with open(RAW_PATH, encoding="utf-8") as f:
        records = json.load(f)
    print(f"      Số record đầu vào: {len(records)}")

    cleaned_at = datetime.now().isoformat(timespec="seconds")

    print(f"[2/5] Clean từng record ...")
    df = pd.DataFrame([clean_record(r, cleaned_at) for r in records])

    print(f"[3/5] Lọc record lỗi & Deduplicate ...")
    before = len(df)
    df = df.dropna(subset=["source_listing_id", "list_id"])
    if before - len(df):
        print(f"      Drop {before - len(df)} record thiếu ad_id/list_id")

    before = len(df)
    df = df.drop_duplicates(subset=["source_listing_id"], keep="first")
    if before - len(df):
        print(f"      Drop {before - len(df)} record trùng ad_id")

    # Drop cột vô dụng
    drop = [c for c in DROP_COLUMNS if c in df.columns]
    before_cols = len(df.columns)
    df = df.drop(columns=drop)
    print(f"      Drop {len(drop)} cột vô dụng ({before_cols} -> {len(df.columns)})")

    # Auto-drop cột 100% null
    all_null = [c for c in df.columns if df[c].isna().all()]
    if all_null:
        df = df.drop(columns=all_null)
        print(f"      Auto-drop {len(all_null)} cột 100% null: {all_null}")

    # Auto-drop cột single-value không nằm trong whitelist
    if len(df) > 1:
        single = [
            c for c in df.columns
            if df[c].nunique(dropna=True) <= 1 and c not in KEEP_SINGLE_VALUE
        ]
        if single:
            df = df.drop(columns=single)
            print(f"      Auto-drop {len(single)} cột single-value: {single}")

    for c in ["posted_at", "orig_posted_at"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    print(f"[4/5] Ghi output: {OUT_PATH}")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

    print(f"[5/5] Summary")
    print(f"      Số record đầu ra: {len(df)}")
    print(f"      Số cột: {len(df.columns)}")

    print("\n      --- Missing per column (%) ---")
    missing = (df.isna().mean() * 100).sort_values(ascending=False)
    for col, pct in missing.items():
        if pct > 0:
            print(f"        {col:<35} {pct:>6.1f}%")
    if (missing == 0).all():
        print("        (không có cột nào missing)")

    print("\n      --- Top vùng ---")
    if "region_name" in df:
        print(df["region_name"].value_counts().head(10).to_string())

    print("\n      --- Giá (VND) ---")
    p = df["price_vnd"].dropna()
    if len(p):
        print(f"        min    : {int(p.min()):>15,}")
        print(f"        median : {int(p.median()):>15,}")
        print(f"        max    : {int(p.max()):>15,}")

    print("\n      --- posted_at ---")
    print(f"        min: {df['posted_at'].min()}")
    print(f"        max: {df['posted_at'].max()}")


if __name__ == "__main__":
    main()