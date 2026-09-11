"""
Clean chotot_xemay_raw.json -> data/interim/chotot_xemay_clean.csv

Input : data/raw/chotot_xemay_raw.json
Output: data/interim/chotot_xemay_clean.csv

Nguyên tắc:
- Giữ nhiều cột nhất có thể, kể cả list rỗng (lưu JSON string).
- Chỉ bỏ các cột trùng lặp hoàn toàn về nội dung (thumbnail/webp của ảnh chính)
  và cột `date` (chỉ là "22 phút trước", không dùng cho phân tích).
- Không filter record theo bất kỳ tiêu chí nào (kể cả giá).
- Chỉ drop record thiếu ad_id/list_id hoặc trùng ad_id.
"""

import json
from pathlib import Path
from datetime import datetime

import pandas as pd


# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "chotot_xemay_raw.json"
OUT_PATH = BASE_DIR / "data" / "interim" / "chotot_xemay_clean.csv"


# ---------- Helpers ----------
def json_safe(v):
    """List/dict -> JSON string. Rỗng -> None. Còn lại giữ nguyên."""
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
    """Epoch ms -> pandas Timestamp. None nếu không parse được."""
    if ms is None:
        return None
    try:
        return pd.to_datetime(int(ms), unit="ms")
    except (TypeError, ValueError, OverflowError):
        return None


# ---------- Clean one record ----------
def clean_record(r: dict, cleaned_at: str) -> dict:
    seller = r.get("seller_info") or {}

    return {
        # ----- Định danh -----
        "source":                       "chotot",
        "vehicle_type":                 "motorbike",
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
        "regdate_year":                 r.get("regdate"),
        "state":                        r.get("state"),
        "status":                       r.get("status"),
        "category_id":                  r.get("category"),
        "category_name":                r.get("category_name"),
        "type":                         r.get("type"),
        "job_tier":                     r.get("job_tier"),

        # ----- Thuộc tính xe -----
        "brand_id":                     r.get("motorbikebrand"),
        "model_id":                     r.get("motorbikemodel"),
        "origin_id":                    r.get("motorbikeorigin"),
        "motorbike_type_id":            r.get("motorbiketype"),
        "mileage_km":                   r.get("mileage_v2"),
        "mileage_km_alt":               r.get("mileage"),
        "motorbike_capacity":           r.get("motorbikecapacity"),
        "evehiclemotor_flag":           r.get("evehiclemotor"),
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
        "detail_address":               r.get("detail_address"),
        "location_id":                  r.get("location_id"),
        "unique_street_id":             r.get("unique_street_id"),
        "is_main_street":               r.get("is_main_street"),
        "latitude":                     r.get("latitude"),
        "longitude":                    r.get("longitude"),

        # ----- Người bán -----
        "account_id":                   r.get("account_id"),
        "account_name":                 r.get("account_name"),
        "account_oid":                  r.get("account_oid"),
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
        "inspection_images":            json_safe(r.get("inspection_images")),
        "special_display_images":       json_safe(r.get("special_display_images")),

        # ----- Trạng thái / quảng cáo -----
        "is_sticky":                    r.get("is_sticky"),
        "sticky_ad_platinum":           r.get("sticky_ad_platinum"),
        "sticky_ad_type":               r.get("sticky_ad_type"),
        "is_zalo_show":                 r.get("is_zalo_show"),
        "protection_entitlement":       r.get("protection_entitlement"),

        # ----- E-commerce -----
        "veh_ecom_can_buy_now":         r.get("veh_ecom_can_buy_now"),
        "veh_ecom_product_id":          r.get("veh_ecom_product_id"),
        "veh_ecom_shop_id":             r.get("veh_ecom_shop_id"),
        "veh_inspected":                r.get("veh_inspected"),
        "vehicleguarantee":             r.get("vehicleguarantee"),
        "product_id":                   r.get("product_id"),

        # ----- List fields -> JSON string -----
        "ad_features":                  json_safe(r.get("ad_features")),
        "ad_labels":                    json_safe(r.get("ad_labels")),
        "business_days":                json_safe(r.get("business_days")),
        "cta_buttons":                  json_safe(r.get("cta_buttons")),
        "fee_type":                     json_safe(r.get("fee_type")),
        "label_campaigns":              json_safe(r.get("label_campaigns")),
        "specific_service_offered":     json_safe(r.get("specific_service_offered")),
        "params":                       json_safe(r.get("params")),
        "pty_characteristics":          json_safe(r.get("pty_characteristics")),
    }


# ---------- Main ----------
def main() -> None:
    print(f"[1/5] Đọc raw: {RAW_PATH}")
    with open(RAW_PATH, encoding="utf-8") as f:
        records = json.load(f)
    print(f"      Số record đầu vào: {len(records)}")

    cleaned_at = datetime.now().isoformat(timespec="seconds")

    print(f"[2/5] Clean từng record ...")
    rows = [clean_record(r, cleaned_at) for r in records]
    df = pd.DataFrame(rows)

    print(f"[3/5] Loại record lỗi ...")
    before = len(df)
    df = df.dropna(subset=["source_listing_id", "list_id"])
    dropped_missing = before - len(df)
    if dropped_missing:
        print(f"      Drop {dropped_missing} record thiếu ad_id/list_id")

    before = len(df)
    df = df.drop_duplicates(subset=["source_listing_id"], keep="first")
    dropped_dup = before - len(df)
    if dropped_dup:
        print(f"      Drop {dropped_dup} record trùng ad_id")

    # Cast datetime cho gọn khi ghi CSV
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