# Dataset discovery — no source changes

All files under data/raw/ and data/processed/ were read recursively. Counts exclude CSV headers. Samples are the first three records in source order, with every field and value retained. CSV values are physically text; inferred numeric types below describe parseability, not a source schema. JSON types are native. Empty means missing, null, or empty string (empty arrays remain arrays). Confidence concerns field meaning, not seller accuracy.

## Summary

| File | Likely role | Key fields found (confidence for each guess) | Role confidence |
|---|---|---|---|
| data/processed/ev_market_cleaned.csv | Processed listings | Listing ID: list_id [high]; Price: price [high / medium]; Registration/manufacturing year: regdate [medium]; Mileage/ODO: mileage_v2 [high]; Region/location: region_name; area_name [high]; Title/description: subject; body; body_clean [high] | high for role; field-specific confidence below |
| data/raw/chotot_oto_raw.json | Raw listings — cars | Listing ID: list_id; ad_id (alternate) [high]; Price: price; price_string [high]; Brand: carbrand → carbrand_name [high]; Model: carmodel → carmodel_name [high]; Registration/manufacturing year: mfdate [high]; Mileage/ODO: mileage_v2; mileage [high / medium]; Region/location: region_name, region_name_v3, region, region_v2; area_name, area, area_v2; ward_name, ward_name_v3, ward; latitude, longitude, location; detail_address [high / medium]; Listing date/time: list_time; orig_list_time; date [high / medium]; Title/description: subject; body [high] | high for role; field-specific confidence below |
| data/raw/chotot_xemay_raw.json | Raw listings — motorbikes | Listing ID: list_id; ad_id (alternate) [high]; Price: price; price_string [high]; Brand: motorbikebrand [high]; Model: motorbikemodel [high]; Registration/manufacturing year: regdate [medium]; Mileage/ODO: mileage_v2; mileage [high / medium]; Region/location: region_name, region_name_v3, region, region_v2; area_name, area, area_v2; ward_name, ward_name_v3, ward; latitude, longitude, location; detail_address [high / medium]; Listing date/time: list_time; orig_list_time; date [high / medium]; Title/description: subject; body [high] | high for role; field-specific confidence below |
| data/raw/ev_benchmark.csv | Benchmark | Price: Price_No_Battery; Price_With_Battery; Battery_Cost [high / medium]; Brand: Brand [high]; Model: Model [high] | high for role; field-specific confidence below |
| data/raw/otodien_raw.csv | B2C reference — cars | Price: price_raw; price_clean [high]; Title/description: subject (title only) [high] | high for role; field-specific confidence below |
| data/raw/phoxedien_raw.csv | B2C reference — electric two-wheelers | Price: price_raw [high]; Title/description: subject (title only) [high] | high for role; field-specific confidence below |
| data/raw/thegioixedien_raw.csv | B2C reference — electric two-wheelers | Price: price_raw [high]; Title/description: subject (title only) [high] | high for role; field-specific confidence below |

No standalone numeric code dictionary was found. The benchmark is a product-price reference. The car JSON has embedded code/name pairs; the motorbike JSON does not have equivalent name fields. Source records have not been deduplicated, joined, standardized, or changed.

## data/processed/ev_market_cleaned.csv

Format: **csv**. Rows/records: **1,000**. Fields (union): **10**.

CSV header: `list_id`, `subject`, `price`, `body`, `regdate`, `mileage_v2`, `region_name`, `area_name`, `body_clean`, `battery_status`

### Field identification

| Semantic meaning | Candidate field(s) | Confidence | Evidence / limitation |
|---|---|---|---|
| Listing ID | list_id | high | Integer-like identifiers, but only 50 distinct values among 1,000 rows. It denotes a listing, not a unique physical row in this file. |
| Price | price | high / medium | Integer-like amounts such as 20000000 suggest asking prices; VND is likely from context but not explicitly declared in this CSV (medium). |
| Brand | absent as a dedicated field | high | Some names occur in subject/body, but there is no structured name or numeric code column; none was inferred from prose. |
| Model | absent as a dedicated field | high | Some names occur in subject/body, but there is no structured name or numeric code column; none was inferred from prose. |
| Registration/manufacturing year | regdate | medium | Four-digit numeric text such as 2024 indicates vehicle year; registration versus manufacturing meaning cannot be proven from this CSV. |
| Mileage/ODO | mileage_v2 | high | Integer-valued decimal text such as 11000.0 matches the sample title 11000 km. 76 rows are blank. |
| Region/location | region_name; area_name | high | Values such as Tp Hồ Chí Minh and Thành phố Thủ Đức indicate province/city and subprovincial location respectively. |
| Listing date/time | absent | high | No absolute timestamp or relative posting-date field; regdate is vehicle year. |
| Title/description | subject; body; body_clean | high | Short headlines and longer prose; body_clean appears to be a processed description, though the exact cleaning method is not encoded in the file. |

### Field profile (all records)

| Field | Observed/inferred type | Nonempty | Distinct nonempty | First nonempty example (up to 160 characters) |
|---|---|---:|---:|---|
| list_id | text → integer-valued numeric | 1000 | 50 | "134026009" |
| subject | text | 1000 | 50 | "Xe máy điện VinFast EVO 200 2024 Đen mờ 11000 km" |
| price | text → integer-valued numeric | 1000 | 37 | "20000000" |
| body | text | 1000 | 50 | "DƯ dùng bán lại chiếc xe máy điện VinFats EVO 200, màu đen mờ sản xuất 2024 , pin mua chạy 11 000km, pin sử dụng 100km mới sạc,xe luôn bảo dưỡng định kỳ tại hã |
| regdate | text → integer-valued numeric | 1000 | 9 | "2024" |
| mileage_v2 | text → integer-valued numeric | 924 | 31 | "11000.0" |
| region_name | text | 1000 | 7 | "Tp Hồ Chí Minh" |
| area_name | text | 1000 | 17 | "Thành phố Thủ Đức" |
| body_clean | text | 1000 | 50 | "DƯ dùng bán lại chiếc xe máy điện VinFats EVO 200, màu đen mờ sản xuất 2024 , pin mua chạy 11 000km, pin sử dụng 100km mới sạc,xe luôn bảo dưỡng định kỳ tại hã |
| battery_status | text | 1000 | 3 | "Cần xác minh" |

### Three complete sample records

CSV samples below retain text storage; JSON samples retain native types. No fields or long values are omitted.

```json
[
  {
    "list_id": "134026009",
    "subject": "Xe máy điện VinFast EVO 200 2024 Đen mờ 11000 km",
    "price": "20000000",
    "body": "DƯ dùng bán lại chiếc xe máy điện VinFats EVO 200, màu đen mờ sản xuất 2024 , pin mua chạy 11 000km, pin sử dụng 100km mới sạc,xe luôn bảo dưỡng định kỳ tại hãng , bảo đảm xe còn sử dụng tốt,ngay chủ đứng tên bán, cam ơn anh chị đả xem tin.",
    "regdate": "2024",
    "mileage_v2": "11000.0",
    "region_name": "Tp Hồ Chí Minh",
    "area_name": "Thành phố Thủ Đức",
    "body_clean": "DƯ dùng bán lại chiếc xe máy điện VinFats EVO 200, màu đen mờ sản xuất 2024 , pin mua chạy 11 000km, pin sử dụng 100km mới sạc,xe luôn bảo dưỡng định kỳ tại hãng , bảo đảm xe còn sử dụng tốt,ngay chủ đứng tên bán, cam ơn anh chị đả xem tin.",
    "battery_status": "Cần xác minh"
  },
  {
    "list_id": "134606109",
    "subject": "Xe điện XMEN Đen Đã qua sử dụng",
    "price": "3000000",
    "body": "bán xe điện XMEN đã qua sử dụng vì k dùng đến",
    "regdate": "2017",
    "mileage_v2": "50000.0",
    "region_name": "Đồng Nai",
    "area_name": "Huyện Long Thành",
    "body_clean": "bán xe điện XMEN đã qua sử dụng vì k dùng đến",
    "battery_status": "Cần xác minh"
  },
  {
    "list_id": "134606108",
    "subject": "Xe điện XMEN màu Đen",
    "price": "3000000",
    "body": "bán xe điện XMEN đã quá sử dụng vì k dùng đến",
    "regdate": "2017",
    "mileage_v2": "50000.0",
    "region_name": "Đồng Nai",
    "area_name": "Huyện Long Thành",
    "body_clean": "bán xe điện XMEN đã quá sử dụng vì k dùng đến",
    "battery_status": "Cần xác minh"
  }
]
```

## data/raw/chotot_oto_raw.json

Format: **json**. Rows/records: **1,000**. Fields (union): **100**.

Top level: array of objects (no root object keys).

First object keys: `account_id`, `account_name`, `account_oid`, `ad_features`, `ad_id`, `ad_labels`, `area`, `area_name`, `area_v2`, `avatar`, `average_rating`, `average_rating_for_seller`, `body`, `business_days`, `carbrand`, `carbrand_name`, `carcolor`, `carmodel`, `carmodel_name`, `carseats`, `cartype`, `category`, `category_name`, `company_ad`, `condition_ad`, `condition_ad_name`, `contain_videos`, `cta_buttons`, `date`, `fee_type`, `fuel`, `full_name`, `gearbox`, `image`, `image_thumbnails`, `images`, `inspection_images`, `is_price_not_valid`, `is_shop_verified`, `is_sticky`, `is_zalo_show`, `job_tier`, `label_campaigns`, `latitude`, `list_id`, `list_time`, `location`, `longitude`, `mfdate`, `mileage`, `mileage_v2`, `number_of_images`, `orig_list_time`, `params`, `price`, `price_string`, `product_id`, `protection_entitlement`, `pty_characteristics`, `region`, `region_name`, `region_name_v3`, `region_v2`, `seller_info`, `special_display_images`, `specific_service_offered`, `state`, `status`, `sticky_ad_platinum`, `subject`, `thumbnail_image`, `total_rating`, `total_rating_for_seller`, `type`, `veh_ecom_can_buy_now`, `veh_ecom_product_id`, `veh_ecom_shop_id`, `veh_inspected`, `videos`, `ward`, `ward_name`, `ward_name_v3`, `webp_image`

Full union of keys across all records: `account_id`, `account_name`, `account_oid`, `ad_features`, `ad_id`, `ad_labels`, `area`, `area_name`, `area_v2`, `avatar`, `average_rating`, `average_rating_for_seller`, `body`, `business_days`, `carbrand`, `carbrand_name`, `carcolor`, `carmodel`, `carmodel_name`, `carseats`, `cartype`, `category`, `category_name`, `company_ad`, `condition_ad`, `condition_ad_name`, `contain_videos`, `cta_buttons`, `date`, `fee_type`, `fuel`, `full_name`, `gearbox`, `image`, `image_thumbnails`, `images`, `inspection_images`, `is_price_not_valid`, `is_shop_verified`, `is_sticky`, `is_zalo_show`, `job_tier`, `label_campaigns`, `latitude`, `list_id`, `list_time`, `location`, `longitude`, `mfdate`, `mileage`, `mileage_v2`, `number_of_images`, `orig_list_time`, `params`, `price`, `price_string`, `product_id`, `protection_entitlement`, `pty_characteristics`, `region`, `region_name`, `region_name_v3`, `region_v2`, `seller_info`, `special_display_images`, `specific_service_offered`, `state`, `status`, `sticky_ad_platinum`, `subject`, `thumbnail_image`, `total_rating`, `total_rating_for_seller`, `type`, `veh_ecom_can_buy_now`, `veh_ecom_product_id`, `veh_ecom_shop_id`, `veh_inspected`, `videos`, `ward`, `ward_name`, `ward_name_v3`, `webp_image`, `carorigin`, `shop`, `shop_alias`, `sold_ads`, `include_accessories`, `detail_address`, `valid_registration`, `has_video`, `number_of_owners`, `is_main_street`, `location_id`, `unique_street_id`, `sticky_ad_type`, `special_display`, `stickyad_feature`, `phone_hidden`, `address`

### Field identification

| Semantic meaning | Candidate field(s) | Confidence | Evidence / limitation |
|---|---|---|---|
| Listing ID | list_id; ad_id (alternate) | high | Both are integer identifiers, nonempty and individually unique in all 1,000 records. account_id repeats across ads and identifies a seller instead; product_id is not the listing key. |
| Price | price; price_string | high | Integer amounts match formatted amounts ending in đ, supporting VND asking prices; is_price_not_valid is a separate validity flag. Prices are seller-entered, not verified transaction prices. |
| Brand | carbrand → carbrand_name | high | Repeated integer categories with paired explicit names such as 80 → VinFast. |
| Model | carmodel → carmodel_name | high | Integer categories paired with names such as 1112 → VF8. Use the brand/model code pair for a scoped lookup. |
| Registration/manufacturing year | mfdate | high | Four-digit integer years such as 2024/2026 and mfdate indicate manufacturing year. |
| Mileage/ODO | mileage_v2; mileage | high / medium | mileage_v2 contains kilometer-like integer odometer values, corroborated by sample descriptions (42000 vs 4.2 vạn in cars; 900 vs 900km in motorbikes). mileage instead has a small discrete value set and likely encodes legacy mileage bands; do not interpret it as kilometers without a dictionary. |
| Region/location | region_name, region_name_v3, region, region_v2; area_name, area, area_v2; ward_name, ward_name_v3, ward; latitude, longitude, location; detail_address | high / medium | Names show province/city, district/local city, and ward levels; numeric siblings are location codes. Coordinates are floating-point degrees and location is a comma-separated coordinate string. *_v3 names appear to use a different administrative version (e.g. old province names consolidated into TP Hồ Chí Minh); version semantics remain medium confidence. shop.address is a shop address, not necessarily the vehicle location. |
| Listing date/time | list_time; orig_list_time; date | high / medium | 13-digit integers behave as Unix milliseconds: 1789115863530 → 2026-09-11T08:37:43.530000+00:00. orig_list_time suggests original publication; list_time could reflect publication/refresh (exact event medium). date contains relative text such as minutes ago, not an absolute date. Nested shop creation/modification timestamps describe shops, not ads. |
| Title/description | subject; body | high | subject contains short ad headlines; body contains longer seller prose and line breaks. |

### Field profile (all records)

| Field | Observed/inferred type | Nonempty | Distinct nonempty | First nonempty example (up to 160 characters) |
|---|---|---:|---:|---|
| account_id | int: 1000 | 1000 | 326 | 18315300 |
| account_name | str: 1000 | 1000 | 349 | "Thanh Lam" |
| account_oid | str: 1000 | 1000 | 326 | "33c3a6a13d86a1e8445a502b58f9e1d1" |
| ad_features | list: 1000 | 1000 | 1 | [] |
| ad_id | int: 1000 | 1000 | 1000 | 178670503 |
| ad_labels | list: 1000 | 1000 | 1 | [] |
| area | int: 1000 | 1000 | 67 | 81 |
| area_name | str: 1000 | 1000 | 92 | "Quận Long Biên" |
| area_v2 | int: 1000 | 1000 | 92 | 12081 |
| avatar | str: 1000 | 1000 | 326 | "https://cdn.chotot.com/uac2/18315300" |
| average_rating | int: 306, float: 229 | 535 | 15 | 5 |
| average_rating_for_seller | int: 266, float: 209 | 475 | 14 | 5 |
| body | str: 1000 | 1000 | 972 | "🔥 VF8 sx 2024  – MUA PIN CATL, GIÁ NÀY KHÔNG CHỐT THÌ CHỐT GÌ? 🔥\n\n🚘 Xe lăn bánh 4,2 vạn km\n✅ Full lịch sử – xe sạch đẹp\n🔋 Đã mua pin CATL, khỏi lăn tăn tiề |
| business_days | list: 1000 | 1000 | 1 | [] |
| carbrand | int: 1000 | 1000 | 10 | 80 |
| carbrand_name | str: 1000 | 1000 | 10 | "VinFast" |
| carcolor | int: 936 | 936 | 12 | 1 |
| carmodel | int: 1000 | 1000 | 39 | 1112 |
| carmodel_name | str: 1000 | 1000 | 35 | "VF8" |
| carseats | int: 879 | 879 | 8 | 2 |
| cartype | int: 543 | 543 | 7 | 3 |
| category | int: 1000 | 1000 | 1 | 2010 |
| category_name | str: 1000 | 1000 | 1 | "Ô tô" |
| company_ad | bool: 857 | 857 | 1 | true |
| condition_ad | int: 1000 | 1000 | 2 | 1 |
| condition_ad_name | str: 1000 | 1000 | 2 | "Đã sử dụng" |
| contain_videos | int: 1000 | 1000 | 2 | 2 |
| cta_buttons | list: 1000 | 1000 | 1 | [] |
| date | str: 1000 | 1000 | 43 | "46 giây trước" |
| fee_type | list: 1000 | 1000 | 1 | [] |
| fuel | int: 1000 | 1000 | 1 | 4 |
| full_name | str: 1000 | 1000 | 321 | "Thanh Lam" |
| gearbox | int: 1000 | 1000 | 3 | 1 |
| image | str: 998 | 998 | 998 | "https://cdn.chotot.com/iCWT1wgdRmxxjo4pX_1YGDZAkxgI6OfJgnhUiGA5eDM/preset:listing/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg" |
| image_thumbnails | list: 1000 | 1000 | 999 | [{"image": "https://cdn.chotot.com/aA7HlAO-gOuQujB9XNknhh3ShzJO0VkL_Ob-8Ta1rSc/preset:view/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg", "thu |
| images | list: 1000 | 1000 | 999 | ["https://cdn.chotot.com/aA7HlAO-gOuQujB9XNknhh3ShzJO0VkL_Ob-8Ta1rSc/preset:view/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg", "https://cdn.c |
| inspection_images | list: 1000 | 1000 | 1 | [] |
| is_price_not_valid | bool: 1000 | 1000 | 1 | false |
| is_shop_verified | bool: 1000 | 1000 | 2 | false |
| is_sticky | bool: 1000 | 1000 | 2 | false |
| is_zalo_show | bool: 989 | 989 | 2 | false |
| job_tier | int: 1000 | 1000 | 1 | 0 |
| label_campaigns | list: 1000 | 1000 | 1 | [] |
| latitude | float: 1000 | 1000 | 306 | 21.057554 |
| list_id | int: 1000 | 1000 | 1000 | 134599448 |
| list_time | int: 1000 | 1000 | 999 | 1789115863530 |
| location | str: 1000 | 1000 | 306 | "21.0575538,105.9024322" |
| longitude | float: 1000 | 1000 | 273 | 105.902435 |
| mfdate | int: 1000 | 1000 | 7 | 2024 |
| mileage | int: 277 | 277 | 24 | 9 |
| mileage_v2 | int: 333 | 333 | 132 | 42000 |
| number_of_images | int: 1000 | 1000 | 21 | 5 |
| orig_list_time | int: 721 | 721 | 720 | 1788941071000 |
| params | list: 1000 | 1000 | 1 | [] |
| price | int: 1000 | 1000 | 381 | 800000000 |
| price_string | str: 1000 | 1000 | 381 | "800.000.000 đ" |
| product_id | int: 196 | 196 | 35 | 647791 |
| protection_entitlement | bool: 1000 | 1000 | 1 | false |
| pty_characteristics | list: 1000 | 1000 | 1 | [] |
| region | int: 1000 | 1000 | 11 | 12 |
| region_name | str: 1000 | 1000 | 29 | "Hà Nội" |
| region_name_v3 | str: 1000 | 1000 | 19 | "TP Hà Nội" |
| region_v2 | int: 1000 | 1000 | 29 | 12000 |
| seller_info | dict: 1000 | 1000 | 326 | {"avatar": "https://cdn.chotot.com/uac2/18315300", "full_name": "Thanh Lam", "live_ads": 14} |
| special_display_images | list: 1000 | 1000 | 13 | [] |
| specific_service_offered | list: 1000 | 1000 | 1 | [] |
| state | str: 1000 | 1000 | 1 | "accepted" |
| status | str: 1000 | 1000 | 1 | "active" |
| sticky_ad_platinum | int: 1000 | 1000 | 2 | 0 |
| subject | str: 1000 | 1000 | 988 | "VF8 mua pin CALT chạy hơn 4v đen quyền lực" |
| thumbnail_image | str: 998 | 998 | 998 | "https://cdn.chotot.com/iCWT1wgdRmxxjo4pX_1YGDZAkxgI6OfJgnhUiGA5eDM/preset:listing/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg" |
| total_rating | int: 535 | 535 | 18 | 1 |
| total_rating_for_seller | int: 475 | 475 | 14 | 1 |
| type | str: 1000 | 1000 | 1 | "s" |
| veh_ecom_can_buy_now | bool: 1000 | 1000 | 1 | false |
| veh_ecom_product_id | empty | 0 | 0 |  |
| veh_ecom_shop_id | empty | 0 | 0 |  |
| veh_inspected | int: 1000 | 1000 | 1 | 2 |
| videos | list: 1000 | 1000 | 247 | [] |
| ward | int: 1000 | 1000 | 270 | 45 |
| ward_name | str: 1000 | 1000 | 211 | "Phường Việt Hưng" |
| ward_name_v3 | str: 1000 | 1000 | 181 | "Phường Việt Hưng" |
| webp_image | str: 998 | 998 | 998 | "https://cdn.chotot.com/FhM2vo5SWiKaf2pbfp1Oh9RsfdSzBUjS-jypY7AAiXc/preset:listing/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.webp" |
| carorigin | int: 850 | 850 | 6 | 1 |
| shop | dict: 413 | 413 | 49 | {"address": "Hoàng mai, hà nội", "alias": "NUIxXqyQaxi1oe4", "createdDate": "1784794053", "modifiedDate": 1787471699, "name": "Ô Tô Điện Hà Nội", "profileImageU |
| shop_alias | str: 413 | 413 | 49 | "NUIxXqyQaxi1oe4" |
| sold_ads | int: 580 | 580 | 53 | 4 |
| include_accessories | int: 198 | 198 | 2 | 1 |
| detail_address | str: 236 | 236 | 112 | "Đường Kinh Dương Vương" |
| valid_registration | int: 187 | 187 | 2 | 1 |
| has_video | bool: 246 | 246 | 1 | true |
| number_of_owners | int: 180 | 180 | 2 | 1 |
| is_main_street | bool: 68 | 68 | 2 | false |
| location_id | str: 68 | 68 | 40 | "osm:W839663172" |
| unique_street_id | str: 68 | 68 | 38 | "2f12d88d1d1a5c3b58e95cf8d250a1c1" |
| sticky_ad_type | str: 12 | 12 | 1 | "default" |
| special_display | bool: 12 | 12 | 1 | true |
| stickyad_feature | str: 46 | 46 | 1 | "special_display" |
| phone_hidden | bool: 11 | 11 | 1 | true |
| address | str: 1 | 1 | 1 | "3A quang trung" |

### Embedded code/name lookup structure

This is a listing file with embedded mappings, not a standalone dictionary. Observed pairs cover this sample only; car mappings must not be reused for motorbike codes. To look up brand b, match carbrand=b and read carbrand_name. For model m within b, match (carbrand, carmodel)=(b,m) and read carmodel_name.

Lookup `('carbrand', 'carbrand_name')`: 10 observed keys; 0 keys with conflicting names.

| carbrand | carbrand_name |
|---|---|
| 9 | BMW |
| 16 | Mercedes Benz |
| 23 | Volkswagen |
| 24 | Hãng khác |
| 32 | BYD |
| 35 | Chery |
| 42 | Geely |
| 63 | Porsche |
| 80 | VinFast |
| 87 | Wuling |
Lookup `('carbrand', 'carmodel', 'carmodel_name')`: 39 observed keys; 0 keys with conflicting names.

| carbrand | carmodel | carmodel_name |
|---|---|---|
| 9 | 327 | i8 |
| 16 | 1241 | EQB |
| 16 | 1243 | EQS |
| 16 | 1291 | EQS SUV |
| 23 | 631 | Dòng khác |
| 24 | 979 | Dòng khác |
| 32 | 720 | Dòng khác |
| 32 | 1244 | Atto 3 |
| 32 | 1245 | Seal |
| 32 | 1246 | Dolphin |
| 32 | 1247 | Han |
| 32 | 1270 | M6 |
| 32 | 1307 | Sealion 6 |
| 35 | 739 | Dòng khác |
| 42 | 797 | Dòng khác |
| 42 | 1312 | EX5 |
| 42 | 1342 | EX2 |
| 63 | 1100 | Taycan |
| 80 | 1032 | President |
| 80 | 1082 | Fadil |
| 80 | 1084 | Dòng khác |
| 80 | 1104 | VFe34 |
| 80 | 1112 | VF8 |
| 80 | 1113 | VF9 |
| 80 | 1131 | Lux SA2.0 |
| 80 | 1133 | VF5 |
| 80 | 1183 | VF3 |
| 80 | 1184 | VF5 Plus |
| 80 | 1185 | VF6 |
| 80 | 1189 | VF7 |
| 80 | 1255 | VF8 Lux |
| 80 | 1279 | Limo Green |
| 80 | 1280 | Minio Green |
| 80 | 1281 | Herio Green |
| 80 | 1282 | Nerio Green |
| 80 | 1310 | EC VAN |
| 80 | 1335 | MPV 7 |
| 80 | 1348 | VF2 |
| 87 | 1237 | Hongguang Mini EV |

### Three complete sample records

CSV samples below retain text storage; JSON samples retain native types. No fields or long values are omitted.

```json
[
  {
    "account_id": 18315300,
    "account_name": "Thanh Lam",
    "account_oid": "33c3a6a13d86a1e8445a502b58f9e1d1",
    "ad_features": [],
    "ad_id": 178670503,
    "ad_labels": [],
    "area": 81,
    "area_name": "Quận Long Biên",
    "area_v2": 12081,
    "avatar": "https://cdn.chotot.com/uac2/18315300",
    "average_rating": 5,
    "average_rating_for_seller": 5,
    "body": "🔥 VF8 sx 2024  – MUA PIN CATL, GIÁ NÀY KHÔNG CHỐT THÌ CHỐT GÌ? 🔥\n\n🚘 Xe lăn bánh 4,2 vạn km\n✅ Full lịch sử – xe sạch đẹp\n🔋 Đã mua pin CATL, khỏi lăn tăn tiền thuê pin\n\n💥 ĐẶC BIỆT:\n👉 Có xe xăng: GIẢM NGAY 120 TRIỆU\n👉 Không có xe xăng: VẪN GIẢM 80 TRIỆU\n\n⚠️ Xe đẹp + pin CATL + ưu đãi khủng thế này mà còn “để em suy nghĩ” là người khác suy nghĩ hộ đấy 😎\n\n📲 Inbox/chốt lịch xem xe ngay!",
    "business_days": [],
    "carbrand": 80,
    "carbrand_name": "VinFast",
    "carcolor": 1,
    "carmodel": 1112,
    "carmodel_name": "VF8",
    "carseats": 2,
    "cartype": 3,
    "category": 2010,
    "category_name": "Ô tô",
    "company_ad": true,
    "condition_ad": 1,
    "condition_ad_name": "Đã sử dụng",
    "contain_videos": 2,
    "cta_buttons": [],
    "date": "46 giây trước",
    "fee_type": [],
    "fuel": 4,
    "full_name": "Thanh Lam",
    "gearbox": 1,
    "image": "https://cdn.chotot.com/iCWT1wgdRmxxjo4pX_1YGDZAkxgI6OfJgnhUiGA5eDM/preset:listing/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg",
    "image_thumbnails": [
      {
        "image": "https://cdn.chotot.com/aA7HlAO-gOuQujB9XNknhh3ShzJO0VkL_Ob-8Ta1rSc/preset:view/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg",
        "thumbnail": "https://cdn.chotot.com/iCWT1wgdRmxxjo4pX_1YGDZAkxgI6OfJgnhUiGA5eDM/preset:listing/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg"
      },
      {
        "image": "https://cdn.chotot.com/I8T3FoGP61JGlg6RDfxzEykqoJo8vbX-Cqo94Jy1egQ/preset:view/plain/6180cb879f28f8596bc0a8cc4bee72ed-3001346862375439028.jpg",
        "thumbnail": "https://cdn.chotot.com/v_sHl_1s6t9ohZ2fogKq39mEFqHIuumlUpYC7P_UeI4/preset:listing/plain/6180cb879f28f8596bc0a8cc4bee72ed-3001346862375439028.jpg"
      },
      {
        "image": "https://cdn.chotot.com/cAlY_9TvJ1eLLkpHQyVElRKJtLCANze9RgIoUQfmfsI/preset:view/plain/0fd4da8ccf4dd5121d48d0769fbce41e-3001346862634181039.jpg",
        "thumbnail": "https://cdn.chotot.com/kBWK257DEXGw16GvsVbceD6RoQfJxl9WoCe19pnRuNo/preset:listing/plain/0fd4da8ccf4dd5121d48d0769fbce41e-3001346862634181039.jpg"
      },
      {
        "image": "https://cdn.chotot.com/HvGzFrreDQ9gex_Gd60cOBEZhBgkCrO28NILjS6LN0A/preset:view/plain/b57c934000876b49b73cf34d3e6cdd2c-3001346861663255748.jpg",
        "thumbnail": "https://cdn.chotot.com/Or0xEynPnYYqdI1sVkcjnQ5mPpDDUVp19V2r0JCPbGQ/preset:listing/plain/b57c934000876b49b73cf34d3e6cdd2c-3001346861663255748.jpg"
      }
    ],
    "images": [
      "https://cdn.chotot.com/aA7HlAO-gOuQujB9XNknhh3ShzJO0VkL_Ob-8Ta1rSc/preset:view/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg",
      "https://cdn.chotot.com/I8T3FoGP61JGlg6RDfxzEykqoJo8vbX-Cqo94Jy1egQ/preset:view/plain/6180cb879f28f8596bc0a8cc4bee72ed-3001346862375439028.jpg",
      "https://cdn.chotot.com/cAlY_9TvJ1eLLkpHQyVElRKJtLCANze9RgIoUQfmfsI/preset:view/plain/0fd4da8ccf4dd5121d48d0769fbce41e-3001346862634181039.jpg",
      "https://cdn.chotot.com/HvGzFrreDQ9gex_Gd60cOBEZhBgkCrO28NILjS6LN0A/preset:view/plain/b57c934000876b49b73cf34d3e6cdd2c-3001346861663255748.jpg",
      "https://cdn.chotot.com/k2pbDy-ur2933FTjCxyZ3NYHyqKTX2RH1sfS1zeogPU/preset:view/plain/be0ebe7c090d19dc3a1feeef0d316432-3001346862593205372.jpg"
    ],
    "inspection_images": [],
    "is_price_not_valid": false,
    "is_shop_verified": false,
    "is_sticky": false,
    "is_zalo_show": false,
    "job_tier": 0,
    "label_campaigns": [],
    "latitude": 21.057554,
    "list_id": 134599448,
    "list_time": 1789115863530,
    "location": "21.0575538,105.9024322",
    "longitude": 105.902435,
    "mfdate": 2024,
    "mileage": 9,
    "mileage_v2": 42000,
    "number_of_images": 5,
    "orig_list_time": 1788941071000,
    "params": [],
    "price": 800000000,
    "price_string": "800.000.000 đ",
    "product_id": 647791,
    "protection_entitlement": false,
    "pty_characteristics": [],
    "region": 12,
    "region_name": "Hà Nội",
    "region_name_v3": "TP Hà Nội",
    "region_v2": 12000,
    "seller_info": {
      "avatar": "https://cdn.chotot.com/uac2/18315300",
      "full_name": "Thanh Lam",
      "live_ads": 14
    },
    "special_display_images": [],
    "specific_service_offered": [],
    "state": "accepted",
    "status": "active",
    "sticky_ad_platinum": 0,
    "subject": "VF8 mua pin CALT chạy hơn 4v đen quyền lực",
    "thumbnail_image": "https://cdn.chotot.com/iCWT1wgdRmxxjo4pX_1YGDZAkxgI6OfJgnhUiGA5eDM/preset:listing/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg",
    "total_rating": 1,
    "total_rating_for_seller": 1,
    "type": "s",
    "veh_ecom_can_buy_now": false,
    "veh_ecom_product_id": "",
    "veh_ecom_shop_id": "",
    "veh_inspected": 2,
    "videos": [],
    "ward": 45,
    "ward_name": "Phường Việt Hưng",
    "ward_name_v3": "Phường Việt Hưng",
    "webp_image": "https://cdn.chotot.com/FhM2vo5SWiKaf2pbfp1Oh9RsfdSzBUjS-jypY7AAiXc/preset:listing/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.webp"
  },
  {
    "account_id": 26689559,
    "account_name": "Đại Hải",
    "account_oid": "88a464c6b8eb0ba091b217900b641cf8",
    "ad_features": [],
    "ad_id": 178575433,
    "ad_labels": [],
    "area": 119,
    "area_name": "Thành phố Thủ Đức",
    "area_v2": 13119,
    "avatar": "https://cdn.chotot.com/uac2/26689559",
    "body": "* VF3 Eco giá niêm yết: 285.000.000\n* VF3 Plus giá niêm yết: 296.000.000 \n• CHÍNH SÁCH ƯU ĐÃI:⚡️Miễn phí sạc đến 02/2029\n• Hỗ trợ vay trả góp lên đến 85% \n🚗 Sẵn xe đủ màu - khách chọn màu, nhận xe nhanh 💪Chính sách bảo hành, hậu mãi chính hãng\n❤️VF3 - nhỏ gọn, hiện đại, cực kỳ phù hợp đi phố \n👉Thiết kế cá tính \n👉Dễ lái, dễ đỗ \n👉Vận hành êm ái\n👉Tiết kiệm chi phí sử dụng\n🎁 Tặng nhiều phụ kiện và nhiều phần quà hấp dẫn\n☎️Inbox ngay để được tư vấn giá lăn bánh, hồ sơ trả góp và chọn màu xe phù hợp.",
    "business_days": [],
    "carbrand": 80,
    "carbrand_name": "VinFast",
    "carcolor": 12,
    "carmodel": 1183,
    "carmodel_name": "VF3",
    "carorigin": 1,
    "carseats": 1,
    "cartype": 3,
    "category": 2010,
    "category_name": "Ô tô",
    "company_ad": true,
    "condition_ad": 2,
    "condition_ad_name": "Mới",
    "contain_videos": 2,
    "cta_buttons": [],
    "date": "8 phút trước",
    "fee_type": [],
    "fuel": 4,
    "full_name": "Đại Hải",
    "gearbox": 1,
    "image": "https://cdn.chotot.com/-OUV1QVmESeDJEFll8JkdWt0sVA7lWOJS7KD6INQmEE/preset:listing/plain/6e3a411b1376d0370fe1207ad4d7d668-3000728596725807795.jpg",
    "image_thumbnails": [
      {
        "image": "https://cdn.chotot.com/3epFijRDNbwQP5bk2o8DuZrhEyg5w7tVCp7iYOy1Oe8/preset:view/plain/6e3a411b1376d0370fe1207ad4d7d668-3000728596725807795.jpg",
        "thumbnail": "https://cdn.chotot.com/-OUV1QVmESeDJEFll8JkdWt0sVA7lWOJS7KD6INQmEE/preset:listing/plain/6e3a411b1376d0370fe1207ad4d7d668-3000728596725807795.jpg"
      },
      {
        "image": "https://cdn.chotot.com/KJrjvd09LkQhX4P9dhCsDaDmYVDAbN-YoX24l72EnVY/preset:view/plain/aa9084b9c5d062769f688e7025a2df3b-3000728596811781008.jpg",
        "thumbnail": "https://cdn.chotot.com/JNHzAM9npx-sf5KfcIEv7Wb8b99W_PCMBwejQXRk3xE/preset:listing/plain/aa9084b9c5d062769f688e7025a2df3b-3000728596811781008.jpg"
      },
      {
        "image": "https://cdn.chotot.com/jrrWj6IxSkwDgStQ2ZgEYp6RYtOtBfQIr0vfWhs9flk/preset:view/plain/50fab951182f36f564271f86fb186656-3000728596563314295.jpg",
        "thumbnail": "https://cdn.chotot.com/xMGVor7qxWTssoO-ifPqgi6kdNbX0Bhz-6Z7LoExE70/preset:listing/plain/50fab951182f36f564271f86fb186656-3000728596563314295.jpg"
      },
      {
        "image": "https://cdn.chotot.com/ZD6UMHgZ68aImkmS5cJPo0KR3ROFeWl6xymuPXbemz8/preset:view/plain/fc1efb5bd00e6447552632fae748c638-3000728596676203909.jpg",
        "thumbnail": "https://cdn.chotot.com/s4fEzQcfb_lpGk-B7JzEX6QMWk0Itd8s_4eDGxGCc_4/preset:listing/plain/fc1efb5bd00e6447552632fae748c638-3000728596676203909.jpg"
      }
    ],
    "images": [
      "https://cdn.chotot.com/3epFijRDNbwQP5bk2o8DuZrhEyg5w7tVCp7iYOy1Oe8/preset:view/plain/6e3a411b1376d0370fe1207ad4d7d668-3000728596725807795.jpg",
      "https://cdn.chotot.com/KJrjvd09LkQhX4P9dhCsDaDmYVDAbN-YoX24l72EnVY/preset:view/plain/aa9084b9c5d062769f688e7025a2df3b-3000728596811781008.jpg",
      "https://cdn.chotot.com/jrrWj6IxSkwDgStQ2ZgEYp6RYtOtBfQIr0vfWhs9flk/preset:view/plain/50fab951182f36f564271f86fb186656-3000728596563314295.jpg",
      "https://cdn.chotot.com/ZD6UMHgZ68aImkmS5cJPo0KR3ROFeWl6xymuPXbemz8/preset:view/plain/fc1efb5bd00e6447552632fae748c638-3000728596676203909.jpg",
      "https://cdn.chotot.com/_KvAaOSBp85MGWqpJ7yUXx4ddx1wZ2Y9ypD6VDlzkvE/preset:view/plain/4cfd1998adbf7ae7b1a8ee70f87af8c8-3000728596631915984.jpg",
      "https://cdn.chotot.com/oFlJ5Rqq9IwjbbV0qMd2lkxgHRrVDeNiSzV1NyRWeQk/preset:view/plain/42823460043fa13f23b9de618201ee40-3000728596807199785.jpg",
      "https://cdn.chotot.com/r4h4qWIaTNq9yYxFTXE08MNDaPx2bFwRwzWYmTQGgb0/preset:view/plain/46ead22fda9a21b59b63c09055a1205d-3000728596827068302.jpg"
    ],
    "inspection_images": [],
    "is_price_not_valid": false,
    "is_shop_verified": false,
    "is_sticky": false,
    "is_zalo_show": false,
    "job_tier": 0,
    "label_campaigns": [],
    "latitude": 10.890938,
    "list_id": 134518548,
    "list_time": 1789115449095,
    "location": "10.8909381,106.8283134",
    "longitude": 106.828316,
    "mfdate": 2026,
    "number_of_images": 7,
    "orig_list_time": 1788575733000,
    "params": [],
    "price": 278000000,
    "price_string": "278.000.000 đ",
    "protection_entitlement": false,
    "pty_characteristics": [],
    "region": 13,
    "region_name": "Tp Hồ Chí Minh",
    "region_name_v3": "TP Hồ Chí Minh",
    "region_v2": 13000,
    "seller_info": {
      "avatar": "https://cdn.chotot.com/uac2/26689559",
      "full_name": "Đại Hải",
      "live_ads": 5
    },
    "special_display_images": [],
    "specific_service_offered": [],
    "state": "accepted",
    "status": "active",
    "sticky_ad_platinum": 0,
    "subject": "VinFast VF3 Eco, Plus Điện đủ mẫu mã giá sập sàn🚨",
    "thumbnail_image": "https://cdn.chotot.com/-OUV1QVmESeDJEFll8JkdWt0sVA7lWOJS7KD6INQmEE/preset:listing/plain/6e3a411b1376d0370fe1207ad4d7d668-3000728596725807795.jpg",
    "type": "s",
    "veh_ecom_can_buy_now": false,
    "veh_ecom_product_id": "",
    "veh_ecom_shop_id": "",
    "veh_inspected": 2,
    "videos": [],
    "ward": 9250,
    "ward_name": "Phường Long Bình (Quận 9 cũ)",
    "ward_name_v3": "Phường Long Bình",
    "webp_image": "https://cdn.chotot.com/9hHDSqsIlAv3ScBl38PnfvrLfdyrmCQThlZ-VxUAI2M/preset:listing/plain/6e3a411b1376d0370fe1207ad4d7d668-3000728596725807795.webp"
  },
  {
    "account_id": 2688886,
    "account_name": "Ô Tô Điện Hà Nội",
    "account_oid": "2f870ca5f48f4927d2dec700dcd1ca38",
    "ad_features": [],
    "ad_id": 178682213,
    "ad_labels": [],
    "area": 93,
    "area_name": "Huyện Thường Tín",
    "area_v2": 12093,
    "avatar": "https://cdn.chotot.com/uac2/2688886",
    "body": "🚗 VINFAST VF6 – SUV ĐIỆN HIỆN ĐẠI, THIẾT KẾ ĐẸP, VẬN HÀNH ÊM\n\nBạn đang tìm một mẫu SUV điện đô thị vừa đẹp, rộng rãi, trang bị hiện đại? VinFast VF6 là lựa chọn đáng tham khảo trong phân khúc.\n\n🔹 Thiết kế SUV trẻ trung, khỏe khoắn\n🔹 Không gian nội thất rộng rãi, tiện nghi\n🔹 Động cơ điện vận hành êm, phản hồi nhanh\n🔹 Trang bị nhiều công nghệ hỗ trợ người lái\n🔹 Phù hợp đi phố, đi làm, gia đình sử dụng hằng ngày\n🔹 Có nhiều lựa chọn màu sắc\n\n📍 Xe VinFast VF6 chính hãng\n📞 LH: ***\n🌐 *** ",
    "business_days": [],
    "carbrand": 80,
    "carbrand_name": "VinFast",
    "carcolor": 2,
    "carmodel": 1185,
    "carmodel_name": "VF6",
    "carorigin": 1,
    "carseats": 2,
    "cartype": 3,
    "category": 2010,
    "category_name": "Ô tô",
    "company_ad": true,
    "condition_ad": 2,
    "condition_ad_name": "Mới",
    "contain_videos": 2,
    "cta_buttons": [],
    "date": "9 phút trước",
    "fee_type": [],
    "fuel": 4,
    "full_name": "Ô Tô Điện Hà Nội",
    "gearbox": 1,
    "image": "https://cdn.chotot.com/6KGg9fxlFeIMtKa8afuTL7lcYChP-ND56t6HIvqCT-E/preset:listing/plain/3292d96b073f44b5effee511b43b7886-3001450546157685648.jpg",
    "image_thumbnails": [
      {
        "image": "https://cdn.chotot.com/FtlB1IytNmw_SoGmhvEe8eS0ldXJcsMAnJRbzHxYY5s/preset:view/plain/3292d96b073f44b5effee511b43b7886-3001450546157685648.jpg",
        "thumbnail": "https://cdn.chotot.com/6KGg9fxlFeIMtKa8afuTL7lcYChP-ND56t6HIvqCT-E/preset:listing/plain/3292d96b073f44b5effee511b43b7886-3001450546157685648.jpg"
      },
      {
        "image": "https://cdn.chotot.com/7elVM6kkSyCr_5WPEDD7AzM-muaLbTaT6iufncX4Yg4/preset:view/plain/345011d70f32bb91468a0d9a29424304-3001450560200543120.jpg",
        "thumbnail": "https://cdn.chotot.com/2T3TWkyYtbaZQO8juTXvef0nLeu-QGxuKH-5CUK0U-A/preset:listing/plain/345011d70f32bb91468a0d9a29424304-3001450560200543120.jpg"
      },
      {
        "image": "https://cdn.chotot.com/BG8lue8wvszqyVVPNEmlheGgknitbxAc5XdmaQBjk4Y/preset:view/plain/db653bf7b9cbeb4d9c543e45bd27a3a0-3001450561519121075.jpg",
        "thumbnail": "https://cdn.chotot.com/b59gX4DH0PkXahu-1A4d8CIKFdKb4eTHssULuitVqPM/preset:listing/plain/db653bf7b9cbeb4d9c543e45bd27a3a0-3001450561519121075.jpg"
      },
      {
        "image": "https://cdn.chotot.com/yGzguah98Htm3FSBTHxDt80xui4Npk8i15Khs9WDUEM/preset:view/plain/cdb27a775fd824c29340fcc752bdd91b-3001450561216180846.jpg",
        "thumbnail": "https://cdn.chotot.com/8c1cCjhmdXUGwAMzszWMo6nprUT05TIcL9fJvkOKZO0/preset:listing/plain/cdb27a775fd824c29340fcc752bdd91b-3001450561216180846.jpg"
      }
    ],
    "images": [
      "https://cdn.chotot.com/FtlB1IytNmw_SoGmhvEe8eS0ldXJcsMAnJRbzHxYY5s/preset:view/plain/3292d96b073f44b5effee511b43b7886-3001450546157685648.jpg",
      "https://cdn.chotot.com/7elVM6kkSyCr_5WPEDD7AzM-muaLbTaT6iufncX4Yg4/preset:view/plain/345011d70f32bb91468a0d9a29424304-3001450560200543120.jpg",
      "https://cdn.chotot.com/BG8lue8wvszqyVVPNEmlheGgknitbxAc5XdmaQBjk4Y/preset:view/plain/db653bf7b9cbeb4d9c543e45bd27a3a0-3001450561519121075.jpg",
      "https://cdn.chotot.com/yGzguah98Htm3FSBTHxDt80xui4Npk8i15Khs9WDUEM/preset:view/plain/cdb27a775fd824c29340fcc752bdd91b-3001450561216180846.jpg",
      "https://cdn.chotot.com/4UDTZAbdR7cZg2GpqvP9_zKUSqFQJ_1X9dqC1Cs7FIw/preset:view/plain/7bb5867705cded1ff88281fcee15084a-3001450561480821428.jpg"
    ],
    "inspection_images": [],
    "is_price_not_valid": false,
    "is_shop_verified": false,
    "is_sticky": false,
    "is_zalo_show": true,
    "job_tier": 0,
    "label_campaigns": [],
    "latitude": 20.87157,
    "list_id": 134609246,
    "list_time": 1789115342570,
    "location": "20.8715715,105.8627913",
    "longitude": 105.86279,
    "mfdate": 2026,
    "number_of_images": 5,
    "orig_list_time": 1789004080000,
    "params": [],
    "price": 575000000,
    "price_string": "575.000.000 đ",
    "protection_entitlement": false,
    "pty_characteristics": [],
    "region": 12,
    "region_name": "Hà Nội",
    "region_name_v3": "TP Hà Nội",
    "region_v2": 12000,
    "seller_info": {
      "avatar": "https://cdn.chotot.com/uac2/2688886",
      "full_name": "Ô Tô Điện Hà Nội",
      "live_ads": 17
    },
    "shop": {
      "address": "Hoàng mai, hà nội",
      "alias": "NUIxXqyQaxi1oe4",
      "createdDate": "1784794053",
      "modifiedDate": 1787471699,
      "name": "Ô Tô Điện Hà Nội",
      "profileImageUrl": "https://cdn.chotot.com/uac2/2688886",
      "service_type": "membership",
      "shopsCategoriesRelationships": [
        {
          "categoryId": 2000
        }
      ],
      "status": "accepted",
      "urls": [
        {
          "url": "o-to-dien-ha-noi"
        }
      ]
    },
    "shop_alias": "NUIxXqyQaxi1oe4",
    "special_display_images": [],
    "specific_service_offered": [],
    "state": "accepted",
    "status": "active",
    "sticky_ad_platinum": 0,
    "subject": "VINFAST VF6 – SUV ĐIỆN HIỆN ĐẠI, THIẾT KẾ ĐẸP",
    "thumbnail_image": "https://cdn.chotot.com/6KGg9fxlFeIMtKa8afuTL7lcYChP-ND56t6HIvqCT-E/preset:listing/plain/3292d96b073f44b5effee511b43b7886-3001450546157685648.jpg",
    "type": "s",
    "veh_ecom_can_buy_now": false,
    "veh_ecom_product_id": "",
    "veh_ecom_shop_id": "",
    "veh_inspected": 2,
    "videos": [],
    "ward": 477,
    "ward_name": "Thị trấn Thường Tín",
    "ward_name_v3": "Xã Thường Tín",
    "webp_image": "https://cdn.chotot.com/i8ik7BkYebyomag19mFui1irdSAXl8c4oT01QfNrZjQ/preset:listing/plain/3292d96b073f44b5effee511b43b7886-3001450546157685648.webp"
  }
]
```

## data/raw/chotot_xemay_raw.json

Format: **json**. Rows/records: **1,000**. Fields (union): **91**.

Top level: array of objects (no root object keys).

First object keys: `account_id`, `account_name`, `account_oid`, `ad_features`, `ad_id`, `ad_labels`, `area`, `area_name`, `area_v2`, `avatar`, `body`, `business_days`, `category`, `category_name`, `condition_ad`, `condition_ad_name`, `contain_videos`, `cta_buttons`, `date`, `fee_type`, `full_name`, `image`, `image_thumbnails`, `images`, `inspection_images`, `is_price_not_valid`, `is_shop_verified`, `is_sticky`, `is_zalo_show`, `job_tier`, `label_campaigns`, `latitude`, `list_id`, `list_time`, `location`, `longitude`, `mileage_v2`, `motorbikebrand`, `motorbikemodel`, `motorbiketype`, `number_of_images`, `orig_list_time`, `params`, `price`, `price_string`, `protection_entitlement`, `pty_characteristics`, `regdate`, `region`, `region_name`, `region_name_v3`, `region_v2`, `seller_info`, `sold_ads`, `special_display_images`, `specific_service_offered`, `state`, `status`, `sticky_ad_platinum`, `subject`, `thumbnail_image`, `type`, `veh_ecom_can_buy_now`, `veh_ecom_product_id`, `veh_ecom_shop_id`, `veh_inspected`, `videos`, `ward`, `ward_name`, `ward_name_v3`, `webp_image`

Full union of keys across all records: `account_id`, `account_name`, `account_oid`, `ad_features`, `ad_id`, `ad_labels`, `area`, `area_name`, `area_v2`, `avatar`, `body`, `business_days`, `category`, `category_name`, `condition_ad`, `condition_ad_name`, `contain_videos`, `cta_buttons`, `date`, `fee_type`, `full_name`, `image`, `image_thumbnails`, `images`, `inspection_images`, `is_price_not_valid`, `is_shop_verified`, `is_sticky`, `is_zalo_show`, `job_tier`, `label_campaigns`, `latitude`, `list_id`, `list_time`, `location`, `longitude`, `mileage_v2`, `motorbikebrand`, `motorbikemodel`, `motorbiketype`, `number_of_images`, `orig_list_time`, `params`, `price`, `price_string`, `protection_entitlement`, `pty_characteristics`, `regdate`, `region`, `region_name`, `region_name_v3`, `region_v2`, `seller_info`, `sold_ads`, `special_display_images`, `specific_service_offered`, `state`, `status`, `sticky_ad_platinum`, `subject`, `thumbnail_image`, `type`, `veh_ecom_can_buy_now`, `veh_ecom_product_id`, `veh_ecom_shop_id`, `veh_inspected`, `videos`, `ward`, `ward_name`, `ward_name_v3`, `webp_image`, `company_ad`, `evehiclemotor`, `motorbikeorigin`, `vehicleguarantee`, `mileage`, `shop`, `shop_alias`, `detail_address`, `average_rating`, `average_rating_for_seller`, `total_rating`, `total_rating_for_seller`, `is_main_street`, `location_id`, `unique_street_id`, `motorbikecapacity`, `has_video`, `phone_hidden`, `sticky_ad_type`, `giveaway`

### Field identification

| Semantic meaning | Candidate field(s) | Confidence | Evidence / limitation |
|---|---|---|---|
| Listing ID | list_id; ad_id (alternate) | high | Both are integer identifiers, nonempty and individually unique in all 1,000 records. account_id repeats across ads and identifies a seller instead; product_id is not the listing key. |
| Price | price; price_string | high | Integer amounts match formatted amounts ending in đ, supporting VND asking prices; is_price_not_valid is a separate validity flag. Prices are seller-entered, not verified transaction prices. |
| Brand | motorbikebrand | high | Repeated integer categories (52 distinct) and the motorbikebrand name identify brand codes. No structured brand-name field is present; names cannot be resolved from this file alone. |
| Model | motorbikemodel | high | Repeated integer categories (155 distinct) and motorbikemodel identify model codes. No model-name field or dictionary is present; no title/body parsing was performed. |
| Registration/manufacturing year | regdate | medium | Four-digit integer years such as 2025/2026 indicate vehicle year. regdate suggests registration year, but the distinction from manufacture/model year is not established by values alone. |
| Mileage/ODO | mileage_v2; mileage | high / medium | mileage_v2 contains kilometer-like integer odometer values, corroborated by sample descriptions (42000 vs 4.2 vạn in cars; 900 vs 900km in motorbikes). mileage instead has a small discrete value set and likely encodes legacy mileage bands; do not interpret it as kilometers without a dictionary. |
| Region/location | region_name, region_name_v3, region, region_v2; area_name, area, area_v2; ward_name, ward_name_v3, ward; latitude, longitude, location; detail_address | high / medium | Names show province/city, district/local city, and ward levels; numeric siblings are location codes. Coordinates are floating-point degrees and location is a comma-separated coordinate string. *_v3 names appear to use a different administrative version (e.g. old province names consolidated into TP Hồ Chí Minh); version semantics remain medium confidence. shop.address is a shop address, not necessarily the vehicle location. |
| Listing date/time | list_time; orig_list_time; date | high / medium | 13-digit integers behave as Unix milliseconds: 1789115227431 → 2026-09-11T08:27:07.431000+00:00. orig_list_time suggests original publication; list_time could reflect publication/refresh (exact event medium). date contains relative text such as minutes ago, not an absolute date. Nested shop creation/modification timestamps describe shops, not ads. |
| Title/description | subject; body | high | subject contains short ad headlines; body contains longer seller prose and line breaks. |

### Field profile (all records)

| Field | Observed/inferred type | Nonempty | Distinct nonempty | First nonempty example (up to 160 characters) |
|---|---|---:|---:|---|
| account_id | int: 1000 | 1000 | 556 | 30147 |
| account_name | str: 1000 | 1000 | 544 | "anh dung" |
| account_oid | str: 1000 | 1000 | 556 | "52e7852157d0a0eeb53ee2a6eb6b48f3" |
| ad_features | list: 1000 | 1000 | 1 | [] |
| ad_id | int: 1000 | 1000 | 1000 | 178620912 |
| ad_labels | list: 1000 | 1000 | 1 | [] |
| area | int: 1000 | 1000 | 77 | 11 |
| area_name | str: 1000 | 1000 | 122 | "Thành phố Dĩ An" |
| area_v2 | int: 1000 | 1000 | 124 | 201107 |
| avatar | str: 1000 | 1000 | 556 | "https://cdn.chotot.com/uac2/30147" |
| body | str: 1000 | 1000 | 997 | "Xe điện Yadea màu vàng, trắng, đen, mới đi 900km.\n- Xe còn mới, ít sử dụng.\n- Thiết kế hiện đại, động cơ bền bỉ.\n- Phù hợp di chuyển trong thành phố." |
| business_days | list: 1000 | 1000 | 1 | [] |
| category | int: 1000 | 1000 | 1 | 2020 |
| category_name | str: 1000 | 1000 | 1 | "Xe máy" |
| condition_ad | int: 1000 | 1000 | 2 | 1 |
| condition_ad_name | str: 1000 | 1000 | 2 | "Đã sử dụng" |
| contain_videos | int: 1000 | 1000 | 2 | 2 |
| cta_buttons | list: 1000 | 1000 | 1 | [] |
| date | str: 1000 | 1000 | 32 | "11 phút trước" |
| fee_type | list: 1000 | 1000 | 1 | [] |
| full_name | str: 999 | 999 | 538 | "anh dung" |
| image | str: 999 | 999 | 999 | "https://cdn.chotot.com/f7boHw2HvkLy59r7R01fNYUyGLivq8txwXl5R3u2p6A/preset:listing/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg" |
| image_thumbnails | list: 1000 | 1000 | 1000 | [{"image": "https://cdn.chotot.com/Cr62WRyfn26Xatt7ZJN9AIdnZ0dZE3zp46xMT1zojXY/preset:view/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg", "thu |
| images | list: 1000 | 1000 | 1000 | ["https://cdn.chotot.com/Cr62WRyfn26Xatt7ZJN9AIdnZ0dZE3zp46xMT1zojXY/preset:view/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg", "https://cdn.c |
| inspection_images | list: 1000 | 1000 | 1 | [] |
| is_price_not_valid | bool: 1000 | 1000 | 1 | false |
| is_shop_verified | bool: 1000 | 1000 | 2 | false |
| is_sticky | bool: 1000 | 1000 | 2 | false |
| is_zalo_show | bool: 971 | 971 | 2 | false |
| job_tier | int: 1000 | 1000 | 1 | 0 |
| label_campaigns | list: 1000 | 1000 | 1 | [] |
| latitude | float: 1000 | 1000 | 388 | 10.896463 |
| list_id | int: 1000 | 1000 | 1000 | 134560322 |
| list_time | int: 1000 | 1000 | 1000 | 1789115227431 |
| location | str: 1000 | 1000 | 388 | "10.8964635,106.7528204" |
| longitude | float: 1000 | 1000 | 331 | 106.75282 |
| mileage_v2 | int: 899 | 899 | 270 | 900 |
| motorbikebrand | int: 1000 | 1000 | 52 | 45 |
| motorbikemodel | int: 1000 | 1000 | 155 | 475 |
| motorbiketype | int: 1000 | 1000 | 1 | 4 |
| number_of_images | int: 1000 | 1000 | 21 | 6 |
| orig_list_time | int: 322 | 322 | 322 | 1788768497000 |
| params | list: 1000 | 1000 | 1 | [] |
| price | int: 1000 | 1000 | 257 | 8400000 |
| price_string | str: 1000 | 1000 | 257 | "8.400.000 đ" |
| protection_entitlement | bool: 1000 | 1000 | 1 | false |
| pty_characteristics | list: 1000 | 1000 | 1 | [] |
| regdate | int: 1000 | 1000 | 16 | 2025 |
| region | int: 1000 | 1000 | 12 | 2 |
| region_name | str: 1000 | 1000 | 39 | "Bình Dương" |
| region_name_v3 | str: 1000 | 1000 | 25 | "TP Hồ Chí Minh" |
| region_v2 | int: 1000 | 1000 | 39 | 2011 |
| seller_info | dict: 1000 | 1000 | 556 | {"avatar": "https://cdn.chotot.com/uac2/30147", "full_name": "anh dung", "live_ads": 1, "sold_ads": 2} |
| sold_ads | int: 725 | 725 | 135 | 2 |
| special_display_images | list: 1000 | 1000 | 1 | [] |
| specific_service_offered | list: 1000 | 1000 | 1 | [] |
| state | str: 1000 | 1000 | 1 | "accepted" |
| status | str: 1000 | 1000 | 1 | "active" |
| sticky_ad_platinum | int: 1000 | 1000 | 1 | 0 |
| subject | str: 1000 | 1000 | 988 | "Xe điện Yadea 900km Vàng, trắng, đen" |
| thumbnail_image | str: 999 | 999 | 999 | "https://cdn.chotot.com/f7boHw2HvkLy59r7R01fNYUyGLivq8txwXl5R3u2p6A/preset:listing/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg" |
| type | str: 1000 | 1000 | 1 | "s" |
| veh_ecom_can_buy_now | bool: 1000 | 1000 | 1 | false |
| veh_ecom_product_id | empty | 0 | 0 |  |
| veh_ecom_shop_id | empty | 0 | 0 |  |
| veh_inspected | int: 1000 | 1000 | 1 | 2 |
| videos | list: 1000 | 1000 | 146 | [] |
| ward | int: 1000 | 1000 | 364 | 8937 |
| ward_name | str: 1000 | 1000 | 302 | "Phường Dĩ An" |
| ward_name_v3 | str: 1000 | 1000 | 239 | "Phường Dĩ An" |
| webp_image | str: 999 | 999 | 999 | "https://cdn.chotot.com/DWJmu8SAhbZ_bie-yIrtS9iB7XY5T-PI895jRki8xMo/preset:listing/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.webp" |
| company_ad | bool: 607 | 607 | 1 | true |
| evehiclemotor | int: 282 | 282 | 6 | 4 |
| motorbikeorigin | int: 451 | 451 | 8 | 1 |
| vehicleguarantee | int: 307 | 307 | 6 | 5 |
| mileage | int: 177 | 177 | 13 | 1 |
| shop | dict: 116 | 116 | 17 | {"alias": "8PUbndfpsEhgfQi", "createdDate": "1786077368", "modifiedDate": 1789018505, "name": "Pink Ev Premium Quận 11", "profileImageUrl": "https://cdn.chotot. |
| shop_alias | str: 116 | 116 | 17 | "8PUbndfpsEhgfQi" |
| detail_address | str: 185 | 185 | 141 | "Đường Trần Bình Trọng" |
| average_rating | int: 249, float: 279 | 528 | 24 | 5 |
| average_rating_for_seller | int: 243, float: 231 | 474 | 25 | 5 |
| total_rating | int: 528 | 528 | 40 | 1 |
| total_rating_for_seller | int: 474 | 474 | 31 | 1 |
| is_main_street | bool: 44 | 44 | 2 | false |
| location_id | str: 44 | 44 | 38 | "osm:W502903939" |
| unique_street_id | str: 44 | 44 | 37 | "84fe4e017a31e79eb6e251b21d122ab7" |
| motorbikecapacity | int: 39 | 39 | 4 | 1 |
| has_video | bool: 145 | 145 | 1 | true |
| phone_hidden | bool: 35 | 35 | 1 | true |
| sticky_ad_type | str: 1 | 1 | 1 | "default" |
| giveaway | bool: 8 | 8 | 1 | false |

### Three complete sample records

CSV samples below retain text storage; JSON samples retain native types. No fields or long values are omitted.

```json
[
  {
    "account_id": 30147,
    "account_name": "anh dung",
    "account_oid": "52e7852157d0a0eeb53ee2a6eb6b48f3",
    "ad_features": [],
    "ad_id": 178620912,
    "ad_labels": [],
    "area": 11,
    "area_name": "Thành phố Dĩ An",
    "area_v2": 201107,
    "avatar": "https://cdn.chotot.com/uac2/30147",
    "body": "Xe điện Yadea màu vàng, trắng, đen, mới đi 900km.\n- Xe còn mới, ít sử dụng.\n- Thiết kế hiện đại, động cơ bền bỉ.\n- Phù hợp di chuyển trong thành phố.",
    "business_days": [],
    "category": 2020,
    "category_name": "Xe máy",
    "condition_ad": 1,
    "condition_ad_name": "Đã sử dụng",
    "contain_videos": 2,
    "cta_buttons": [],
    "date": "11 phút trước",
    "fee_type": [],
    "full_name": "anh dung",
    "image": "https://cdn.chotot.com/f7boHw2HvkLy59r7R01fNYUyGLivq8txwXl5R3u2p6A/preset:listing/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg",
    "image_thumbnails": [
      {
        "image": "https://cdn.chotot.com/Cr62WRyfn26Xatt7ZJN9AIdnZ0dZE3zp46xMT1zojXY/preset:view/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg",
        "thumbnail": "https://cdn.chotot.com/f7boHw2HvkLy59r7R01fNYUyGLivq8txwXl5R3u2p6A/preset:listing/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg"
      },
      {
        "image": "https://cdn.chotot.com/nPekVLvKORh5g4WftMqi12JO-cQF15IXIby7XFZ8koc/preset:view/plain/c94dfdd91f1ac9cebc53ef9cc8426e63-3001043386357212638.jpg",
        "thumbnail": "https://cdn.chotot.com/0t7ccSyTbiGCgVZL7ExGDkMOPjkLacMmixuCq-tQ2TE/preset:listing/plain/c94dfdd91f1ac9cebc53ef9cc8426e63-3001043386357212638.jpg"
      },
      {
        "image": "https://cdn.chotot.com/I2BaYN6RkPlaiOQEA-4lh3D2Rm0st27XHV6-Xfc1pXA/preset:view/plain/ae7aeab2d2ae1d73fcd95433f82c5d5e-3001043387832912041.jpg",
        "thumbnail": "https://cdn.chotot.com/_yUS3LbONx9QwQ28UxqDI2XSxidBB0THHYMGMl_rkFI/preset:listing/plain/ae7aeab2d2ae1d73fcd95433f82c5d5e-3001043387832912041.jpg"
      },
      {
        "image": "https://cdn.chotot.com/wyLWM004CqVrnu1_yTM4kjDuvgytCWJt1AK4SnxC5-I/preset:view/plain/024648394ccc2451f76ba405cd05d383-3001043388048335790.jpg",
        "thumbnail": "https://cdn.chotot.com/kU3MvVBg03_0ZtjCPvbpNPbmqQrpydgvRO6cMrQMcGg/preset:listing/plain/024648394ccc2451f76ba405cd05d383-3001043388048335790.jpg"
      }
    ],
    "images": [
      "https://cdn.chotot.com/Cr62WRyfn26Xatt7ZJN9AIdnZ0dZE3zp46xMT1zojXY/preset:view/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg",
      "https://cdn.chotot.com/nPekVLvKORh5g4WftMqi12JO-cQF15IXIby7XFZ8koc/preset:view/plain/c94dfdd91f1ac9cebc53ef9cc8426e63-3001043386357212638.jpg",
      "https://cdn.chotot.com/I2BaYN6RkPlaiOQEA-4lh3D2Rm0st27XHV6-Xfc1pXA/preset:view/plain/ae7aeab2d2ae1d73fcd95433f82c5d5e-3001043387832912041.jpg",
      "https://cdn.chotot.com/wyLWM004CqVrnu1_yTM4kjDuvgytCWJt1AK4SnxC5-I/preset:view/plain/024648394ccc2451f76ba405cd05d383-3001043388048335790.jpg",
      "https://cdn.chotot.com/XsUsHXh9q-8P5kOOZO-NnmN7K7rwPHSEdCwXMfqnm_4/preset:view/plain/e3f35c152cf149a5681af7705781ad93-3001043389963749545.jpg",
      "https://cdn.chotot.com/EKe67_R8YWQrAKEpIvARWlCGdlwWoxp0kDkZpSFV28M/preset:view/plain/e70099872ce25a757c33eb867451feb4-3001043389801584694.jpg"
    ],
    "inspection_images": [],
    "is_price_not_valid": false,
    "is_shop_verified": false,
    "is_sticky": false,
    "is_zalo_show": false,
    "job_tier": 0,
    "label_campaigns": [],
    "latitude": 10.896463,
    "list_id": 134560322,
    "list_time": 1789115227431,
    "location": "10.8964635,106.7528204",
    "longitude": 106.75282,
    "mileage_v2": 900,
    "motorbikebrand": 45,
    "motorbikemodel": 475,
    "motorbiketype": 4,
    "number_of_images": 6,
    "orig_list_time": 1788768497000,
    "params": [],
    "price": 8400000,
    "price_string": "8.400.000 đ",
    "protection_entitlement": false,
    "pty_characteristics": [],
    "regdate": 2025,
    "region": 2,
    "region_name": "Bình Dương",
    "region_name_v3": "TP Hồ Chí Minh",
    "region_v2": 2011,
    "seller_info": {
      "avatar": "https://cdn.chotot.com/uac2/30147",
      "full_name": "anh dung",
      "live_ads": 1,
      "sold_ads": 2
    },
    "sold_ads": 2,
    "special_display_images": [],
    "specific_service_offered": [],
    "state": "accepted",
    "status": "active",
    "sticky_ad_platinum": 0,
    "subject": "Xe điện Yadea 900km Vàng, trắng, đen",
    "thumbnail_image": "https://cdn.chotot.com/f7boHw2HvkLy59r7R01fNYUyGLivq8txwXl5R3u2p6A/preset:listing/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.jpg",
    "type": "s",
    "veh_ecom_can_buy_now": false,
    "veh_ecom_product_id": "",
    "veh_ecom_shop_id": "",
    "veh_inspected": 2,
    "videos": [],
    "ward": 8937,
    "ward_name": "Phường Dĩ An",
    "ward_name_v3": "Phường Dĩ An",
    "webp_image": "https://cdn.chotot.com/DWJmu8SAhbZ_bie-yIrtS9iB7XY5T-PI895jRki8xMo/preset:listing/plain/35009d8ae81d1532781908845c35294d-3001043386446010422.webp"
  },
  {
    "account_id": 30226467,
    "account_name": "Huy Đồng",
    "account_oid": "f76f91eff265230f28f71323ba75df86",
    "ad_features": [],
    "ad_id": 178711662,
    "ad_labels": [],
    "area": 115,
    "area_name": "Huyện Bình Chánh",
    "area_v2": 13115,
    "avatar": "https://cdn.chotot.com/uac2/30226467",
    "body": "Xe máy điện Feliz 2n đời mới 2026\nTrả góp bao nợ xấu\nThủ tục nhanh chóng \nKo giữ CMND/CCCD\nBảo mật thông tin khách hàng\nHỗ trợ 0 trả trước\nBảo hành chính hãng 2 năm",
    "business_days": [],
    "category": 2020,
    "category_name": "Xe máy",
    "company_ad": true,
    "condition_ad": 2,
    "condition_ad_name": "Mới",
    "contain_videos": 2,
    "cta_buttons": [],
    "date": "15 phút trước",
    "evehiclemotor": 4,
    "fee_type": [],
    "full_name": "Huy Đồng",
    "image": "https://cdn.chotot.com/IaPo_o2-tImpLUYlG9Mk8CIRZvqItZT5m2J_0xJHBaY/preset:listing/plain/8bdc9fa4bb94dba1497ae9f88c750b11-3001631007787695245.jpg",
    "image_thumbnails": [
      {
        "image": "https://cdn.chotot.com/pMoYpwUenikbyoKGWA4miqgS_Ns-1A87MMYB7XnOyo0/preset:view/plain/8bdc9fa4bb94dba1497ae9f88c750b11-3001631007787695245.jpg",
        "thumbnail": "https://cdn.chotot.com/IaPo_o2-tImpLUYlG9Mk8CIRZvqItZT5m2J_0xJHBaY/preset:listing/plain/8bdc9fa4bb94dba1497ae9f88c750b11-3001631007787695245.jpg"
      },
      {
        "image": "https://cdn.chotot.com/k3kFBqyAw8-vrZdbjlS-xmDZWKCx1sAF43mNM8haDgs/preset:view/plain/c4647b91cb81504bd61a955653f4b984-3001631007741899374.jpg",
        "thumbnail": "https://cdn.chotot.com/tR88AG4sTFY7pN6XoPALltAm8gEzpJ6I3sP1xqyXoSw/preset:listing/plain/c4647b91cb81504bd61a955653f4b984-3001631007741899374.jpg"
      },
      {
        "image": "https://cdn.chotot.com/wsrAeE7CPxz8_olSyeUHOuz9zyPKosmu-lVvJfQ0aYY/preset:view/plain/3d2f63d7489ee66a4ba1e47c97a88812-3001631007840915944.jpg",
        "thumbnail": "https://cdn.chotot.com/Pf4pdPwV78fm-_35N5GQZ5Se3TPjeODQ_hNIi6pmZWQ/preset:listing/plain/3d2f63d7489ee66a4ba1e47c97a88812-3001631007840915944.jpg"
      }
    ],
    "images": [
      "https://cdn.chotot.com/pMoYpwUenikbyoKGWA4miqgS_Ns-1A87MMYB7XnOyo0/preset:view/plain/8bdc9fa4bb94dba1497ae9f88c750b11-3001631007787695245.jpg",
      "https://cdn.chotot.com/k3kFBqyAw8-vrZdbjlS-xmDZWKCx1sAF43mNM8haDgs/preset:view/plain/c4647b91cb81504bd61a955653f4b984-3001631007741899374.jpg",
      "https://cdn.chotot.com/wsrAeE7CPxz8_olSyeUHOuz9zyPKosmu-lVvJfQ0aYY/preset:view/plain/3d2f63d7489ee66a4ba1e47c97a88812-3001631007840915944.jpg"
    ],
    "inspection_images": [],
    "is_price_not_valid": false,
    "is_shop_verified": false,
    "is_sticky": false,
    "is_zalo_show": false,
    "job_tier": 0,
    "label_campaigns": [],
    "latitude": 10.823866,
    "list_id": 134635643,
    "list_time": 1789114960000,
    "location": "10.8238657,106.5642998",
    "longitude": 106.5643,
    "motorbikebrand": 44,
    "motorbikemodel": 444,
    "motorbikeorigin": 1,
    "motorbiketype": 4,
    "number_of_images": 3,
    "params": [],
    "price": 1800000,
    "price_string": "1.800.000 đ",
    "protection_entitlement": false,
    "pty_characteristics": [],
    "regdate": 2026,
    "region": 13,
    "region_name": "Tp Hồ Chí Minh",
    "region_name_v3": "TP Hồ Chí Minh",
    "region_v2": 13000,
    "seller_info": {
      "avatar": "https://cdn.chotot.com/uac2/30226467",
      "full_name": "Huy Đồng",
      "live_ads": 21,
      "sold_ads": 3
    },
    "sold_ads": 3,
    "special_display_images": [],
    "specific_service_offered": [],
    "state": "accepted",
    "status": "active",
    "sticky_ad_platinum": 0,
    "subject": "Xe máy điện VinFast Feliz 2 đời mới 2026 ",
    "thumbnail_image": "https://cdn.chotot.com/IaPo_o2-tImpLUYlG9Mk8CIRZvqItZT5m2J_0xJHBaY/preset:listing/plain/8bdc9fa4bb94dba1497ae9f88c750b11-3001631007787695245.jpg",
    "type": "s",
    "veh_ecom_can_buy_now": false,
    "veh_ecom_product_id": "",
    "veh_ecom_shop_id": "",
    "veh_inspected": 2,
    "vehicleguarantee": 5,
    "videos": [],
    "ward": 9511,
    "ward_name": "Xã Vĩnh Lộc A",
    "ward_name_v3": "Xã Vĩnh Lộc",
    "webp_image": "https://cdn.chotot.com/PdTVGZqDVG7EMhHmki5-79DlT1Pq1jLpCSLh6cedIYk/preset:listing/plain/8bdc9fa4bb94dba1497ae9f88c750b11-3001631007787695245.webp"
  },
  {
    "account_id": 32274265,
    "account_name": "Pink Ev Premium Quận 11",
    "account_oid": "6b0b87db4c12cfb27eb8f61fcb0226b7",
    "ad_features": [],
    "ad_id": 178689201,
    "ad_labels": [],
    "area": 106,
    "area_name": "Quận 11",
    "area_v2": 13106,
    "avatar": "https://cdn.chotot.com/uac2/32274265",
    "body": "Fb - Tiktok : Nguyen Minh Long Pink Dragon \n==================📌📌📌==================\n❤️Nợ Sấu ko đưa trước có lãi, nếu 4tr ko lỡi sức \n❤️Nợ Sấu 4tr5 ko giữ giấy tờ khách ,ko phí hồ sơ\n❤️Giảm 3tr khi mua Gốpp ,Giá Xe Ko Đổi\n❤️Cà Thẻ Ko Tốn Phí Và Chuyển Đổi Gớp \n\nEvogrand 2026 1 pin  SG 9 Chủ Ký\n- odo 1k siêu lướt\n- Dàn áo keng đẹp 99%\n- Óc tán sáng đẹp\n\n🏠 𝟴𝟮 𝗛𝗼𝗮̀ 𝗕ì𝗻𝗵 - 𝗤𝘂𝗮̣̂𝗻 𝟭𝟭  - 𝗛𝗖𝗠\n\n__________ 𝗤𝘂𝘆𝗲̂̀𝗻 𝗟𝗼̛̣𝗶 𝗞𝗵𝗮́𝗰𝗵 𝗛𝗮̀𝗻𝗴 ________\n✅Fr//ee chạy thử , Ko Mua Cũng Ko Sao \n✅Gói Trải Nghiệm Chỉ 5% Cho 3 Ngày \n✅Đ𝗼̂̉𝗶 𝗣𝗶𝗻 𝟮𝟰/𝟮𝟰 𝗞𝗼 𝗖𝗵𝗼̛̀ 𝗦𝗮̣𝗰 Ở 𝗡𝗵𝗶𝗲̂̀𝘂 𝗖𝗼̛ 𝗦𝗼̛̉ \n✅𝗧𝗮̣̆𝗻𝗴 𝗖𝘂̛́𝘂 𝗛𝗼̣̂ 𝗫𝗲 𝗛𝘂̛ 𝗖𝗵𝗼̛̉ 𝗩𝗲̂̀ 𝗛𝗼̂̃ 𝗧𝗿𝗼̛̣ 𝗦𝘂̛̉𝗮\n✅𝗧𝗮̣̆𝗻𝗴 𝗛𝘂̛ 𝗛𝗼̂̃ 𝗧𝗿𝗼̛̣ 𝗫𝗲 𝗞𝗵𝗮́𝗰 𝗗𝘂̀𝗻𝗴 𝗞𝗵𝗶 𝗖𝗵𝗼̛̀ 𝗦𝘂̛̉𝗮\n--------------\n✅𝗚𝗼́𝗽 𝗡𝗴𝗮̂𝗻 𝗛𝗮̀𝗻𝗴 : Đưa 20% ae giữ Cavet \n✅𝗖𝗮̀ 𝗧𝗵𝗲̉ - 𝗚𝗼́𝗽: Cà thẻ ,chuyển đổi trả góp ko tốn phí\n✅𝗕𝗮𝗼 𝗤𝘂𝗮𝘆 Đ𝗮̂̀𝘂 : Từ 20% theo giá thị trường\n✅𝗠𝘂𝗮 𝗕𝗮́𝗻 𝗧𝗿𝗮𝗼 Đ𝗼̂̉𝗶 𝗫𝗲 𝗫𝗮̆𝗻𝗴, 𝗫𝗲 Đ𝗶𝗲̣̂𝗻 𝗧𝗮̣̂𝗻 𝗡𝗵𝗮̀\n\n𝗖𝗧𝗬 𝗣𝗜𝗡𝗞: 𝗫𝗘 Đ𝗜Ệ𝗡 𝗚Ố𝗣 𝗠Ợ Ấ𝗨 𝗞𝗢 ĐƯ𝗔 𝗧𝗥𝗨̛Ớ𝗖\n🏠 𝟴𝟮 𝗛𝗼𝗮̀ 𝗕ì𝗻𝗵 - 𝗤𝘂𝗮̣̂𝗻 𝟭𝟭  - 𝗛𝗖𝗠\n🏠 𝟮𝟯𝟲 𝗤𝘂𝗮𝗻𝗴 𝗧𝗿𝘂𝗻𝗴 - 𝗚𝗼̀ 𝗩𝗮̂́𝗽 - 𝗛𝗖𝗠",
    "business_days": [],
    "category": 2020,
    "category_name": "Xe máy",
    "company_ad": true,
    "condition_ad": 1,
    "condition_ad_name": "Đã sử dụng",
    "contain_videos": 2,
    "cta_buttons": [],
    "date": "23 phút trước",
    "evehiclemotor": 2,
    "fee_type": [],
    "full_name": "Pink Ev Premium Quận 11",
    "image": "https://cdn.chotot.com/TvNV9iuFdtXy14glt1uRMxMb6e0cxzQzlQI7YXNAf34/preset:listing/plain/37bdb59ce6e1e957f39098630bb5d352-3001477657876934825.jpg",
    "image_thumbnails": [
      {
        "image": "https://cdn.chotot.com/_im6vpKCkmbivSbvo74KXpEGt_kM6l_e7Usw0fRXpO8/preset:view/plain/37bdb59ce6e1e957f39098630bb5d352-3001477657876934825.jpg",
        "thumbnail": "https://cdn.chotot.com/TvNV9iuFdtXy14glt1uRMxMb6e0cxzQzlQI7YXNAf34/preset:listing/plain/37bdb59ce6e1e957f39098630bb5d352-3001477657876934825.jpg"
      },
      {
        "image": "https://cdn.chotot.com/fg-C44FsbgUdlVjkQp-WwMsjxdLIapdAwQfzkREvCgE/preset:view/plain/24a42a1a834743cd7f044be345807b39-3001477658105156360.jpg",
        "thumbnail": "https://cdn.chotot.com/DOUcMIBI9TlaPS66u3skpQPbBcap1E2Lgaqqm_RIO08/preset:listing/plain/24a42a1a834743cd7f044be345807b39-3001477658105156360.jpg"
      },
      {
        "image": "https://cdn.chotot.com/WI-6pWFYGaZ8eF8RTaBwDyBtL8oIrrz-kxZFSP_1pTc/preset:view/plain/9332172b11f9cebbbfa23270814b8d4f-3001477658202862190.jpg",
        "thumbnail": "https://cdn.chotot.com/gI_5uGxW-we59Qny5xRynl7Knk1Fp45bzMt3hooJyXg/preset:listing/plain/9332172b11f9cebbbfa23270814b8d4f-3001477658202862190.jpg"
      },
      {
        "image": "https://cdn.chotot.com/Q_VyTiHuP8f6TcFbaeeFbqgnT65wHL2M-ArHjUK6Z9c/preset:view/plain/49ef66a9c23af33f709e3b75ab9ca4af-3001477658447040423.jpg",
        "thumbnail": "https://cdn.chotot.com/P-0Bxl9VEefqa-8kvdihUIbrHVOxHTULsNqNlbUjhGA/preset:listing/plain/49ef66a9c23af33f709e3b75ab9ca4af-3001477658447040423.jpg"
      }
    ],
    "images": [
      "https://cdn.chotot.com/_im6vpKCkmbivSbvo74KXpEGt_kM6l_e7Usw0fRXpO8/preset:view/plain/37bdb59ce6e1e957f39098630bb5d352-3001477657876934825.jpg",
      "https://cdn.chotot.com/fg-C44FsbgUdlVjkQp-WwMsjxdLIapdAwQfzkREvCgE/preset:view/plain/24a42a1a834743cd7f044be345807b39-3001477658105156360.jpg",
      "https://cdn.chotot.com/WI-6pWFYGaZ8eF8RTaBwDyBtL8oIrrz-kxZFSP_1pTc/preset:view/plain/9332172b11f9cebbbfa23270814b8d4f-3001477658202862190.jpg",
      "https://cdn.chotot.com/Q_VyTiHuP8f6TcFbaeeFbqgnT65wHL2M-ArHjUK6Z9c/preset:view/plain/49ef66a9c23af33f709e3b75ab9ca4af-3001477658447040423.jpg",
      "https://cdn.chotot.com/WPOqGDKr1B4ygIC6EtAVbPZQ3bpHs3YV8qt-DyBAEho/preset:view/plain/1841d528f359b8c017b4dcf6fcf6b185-3001477658562579299.jpg",
      "https://cdn.chotot.com/-yCyaTSAc0KzRmBAicCjpXWFMnv0bj5twRLdGOL8j0k/preset:view/plain/57dab614c8bbebf8a0d4a2eb871ccf51-3001477658481658763.jpg",
      "https://cdn.chotot.com/ljn6_uQzyWGKL3XDEDM_jzb2utJEz5Hx14k7clV5Nyw/preset:view/plain/2542950fbf7591ac845b3ed922ec6528-3001477658370968244.jpg",
      "https://cdn.chotot.com/rJd0Grkkdot3Tp52RljPC18kVDf3LkoOcE0fcabCtt0/preset:view/plain/e7e6aaae757c2d78e2a1d692ef135d0f-3001477658401608098.jpg",
      "https://cdn.chotot.com/bYCONaXnSpQT45mxHjVIHriGpDwd2KqH5ibqOg4IQTo/preset:view/plain/b7b861e975e5b0d120486330597ef167-3001477658556592642.jpg",
      "https://cdn.chotot.com/qMfORtFVsmzX7dtyuAhOdJculc5RalfhxhRGecc-aqo/preset:view/plain/288d6809691cafe0262077506b0251c2-3001477658494143376.jpg"
    ],
    "inspection_images": [],
    "is_price_not_valid": false,
    "is_shop_verified": false,
    "is_sticky": false,
    "is_zalo_show": true,
    "job_tier": 0,
    "label_campaigns": [],
    "latitude": 10.771743,
    "list_id": 134615285,
    "list_time": 1789114504080,
    "location": "10.771743,106.645341",
    "longitude": 106.64534,
    "mileage": 1,
    "mileage_v2": 1000,
    "motorbikebrand": 44,
    "motorbikemodel": 455,
    "motorbikeorigin": 1,
    "motorbiketype": 4,
    "number_of_images": 10,
    "orig_list_time": 1789020393000,
    "params": [],
    "price": 19900000,
    "price_string": "19.900.000 đ",
    "protection_entitlement": false,
    "pty_characteristics": [],
    "regdate": 2026,
    "region": 13,
    "region_name": "Tp Hồ Chí Minh",
    "region_name_v3": "TP Hồ Chí Minh",
    "region_v2": 13000,
    "seller_info": {
      "avatar": "https://cdn.chotot.com/uac2/32274265",
      "full_name": "Pink Ev Premium Quận 11",
      "live_ads": 33,
      "sold_ads": 5
    },
    "shop": {
      "alias": "8PUbndfpsEhgfQi",
      "createdDate": "1786077368",
      "modifiedDate": 1789018505,
      "name": "Pink Ev Premium Quận 11",
      "profileImageUrl": "https://cdn.chotot.com/uac2/32274265",
      "service_type": "membership",
      "shopsCategoriesRelationships": [
        {
          "categoryId": 2000
        }
      ],
      "status": "accepted",
      "urls": [
        {
          "url": "pink-ev-premium-quan-11"
        }
      ]
    },
    "shop_alias": "8PUbndfpsEhgfQi",
    "sold_ads": 5,
    "special_display_images": [],
    "specific_service_offered": [],
    "state": "accepted",
    "status": "active",
    "sticky_ad_platinum": 0,
    "subject": "✅Pink Quận 11✅ Evogrand 2026 1 pin  SG 9 Chủ Ký",
    "thumbnail_image": "https://cdn.chotot.com/TvNV9iuFdtXy14glt1uRMxMb6e0cxzQzlQI7YXNAf34/preset:listing/plain/37bdb59ce6e1e957f39098630bb5d352-3001477657876934825.jpg",
    "type": "s",
    "veh_ecom_can_buy_now": false,
    "veh_ecom_product_id": "",
    "veh_ecom_shop_id": "",
    "veh_inspected": 2,
    "vehicleguarantee": 6,
    "videos": [],
    "ward": 9381,
    "ward_name": "Phường 5",
    "ward_name_v3": "Phường Hòa Bình",
    "webp_image": "https://cdn.chotot.com/Dqi2oLUo6P7RhvDoB921FDvosuSvk_SbN-UXXASvt0c/preset:listing/plain/37bdb59ce6e1e957f39098630bb5d352-3001477657876934825.webp"
  }
]
```

## data/raw/ev_benchmark.csv

Format: **csv**. Rows/records: **8**. Fields (union): **5**.

CSV header: `Brand`, `Model`, `Price_No_Battery`, `Price_With_Battery`, `Battery_Cost`

### Field identification

| Semantic meaning | Candidate field(s) | Confidence | Evidence / limitation |
|---|---|---|---|
| Listing ID | absent | high | No listing identifier; Model is unique across these eight reference rows, but is a product label, not a listing ID. |
| Price | Price_No_Battery; Price_With_Battery; Battery_Cost | high / medium | Integer-like numeric text and explicit column names distinguish price configurations and battery cost. VND is likely from dataset context, but the file has no currency column (medium). No effective date is supplied. |
| Brand | Brand | high | Explicit names include VinFast and Dat Bike. |
| Model | Model | high | Product names include Evo200, Feliz S, and Klara S (2022). This is a name-based benchmark, not numeric-code decoding. |
| Registration/manufacturing year | absent as a dedicated field | high | No matching column. A year embedded in a model label is not an independently defined registration/manufacturing field. |
| Mileage/ODO | absent as a dedicated field | high | The complete five-column schema contains only brand, model, and price/battery benchmarks. |
| Region/location | absent as a dedicated field | high | The complete five-column schema contains only brand, model, and price/battery benchmarks. |
| Listing date/time | absent as a dedicated field | high | The complete five-column schema contains only brand, model, and price/battery benchmarks. |
| Title/description | absent as a dedicated field | high | The complete five-column schema contains only brand, model, and price/battery benchmarks. |

### Field profile (all records)

| Field | Observed/inferred type | Nonempty | Distinct nonempty | First nonempty example (up to 160 characters) |
|---|---|---:|---:|---|
| Brand | text | 8 | 2 | "VinFast" |
| Model | text | 8 | 8 | "Evo200" |
| Price_No_Battery | text → integer-valued numeric | 8 | 8 | "18000000" |
| Price_With_Battery | text → integer-valued numeric | 8 | 8 | "37900000" |
| Battery_Cost | text → integer-valued numeric | 8 | 5 | "19900000" |

### Reference lookup structure

Match exact (Brand, Model) text to read Price_No_Battery, Price_With_Battery, and Battery_Cost. All eight pairs are unique. No numeric brand/model codes are present, so this cannot decode motorbikebrand/motorbikemodel.

### Three complete sample records

CSV samples below retain text storage; JSON samples retain native types. No fields or long values are omitted.

```json
[
  {
    "Brand": "VinFast",
    "Model": "Evo200",
    "Price_No_Battery": "18000000",
    "Price_With_Battery": "37900000",
    "Battery_Cost": "19900000"
  },
  {
    "Brand": "VinFast",
    "Model": "Feliz S",
    "Price_No_Battery": "27000000",
    "Price_With_Battery": "46900000",
    "Battery_Cost": "19900000"
  },
  {
    "Brand": "VinFast",
    "Model": "Klara S (2022)",
    "Price_No_Battery": "35000000",
    "Price_With_Battery": "54900000",
    "Battery_Cost": "19900000"
  }
]
```

## data/raw/otodien_raw.csv

Format: **csv**. Rows/records: **287**. Fields (union): **5**.

CSV header: `source`, `subject`, `price_raw`, `price_clean`, `battery_status`

### Field identification

| Semantic meaning | Candidate field(s) | Confidence | Evidence / limitation |
|---|---|---|---|
| Listing ID | absent | high | source is constant, not a row identifier. subject is a product/ad title and is not a reliable stable listing key, even where unique. |
| Price | price_raw; price_clean | high | Currency-formatted strings use triệu (millions), ₫, or đ; where price_clean exists, 630 triệu corresponds to 630000000, supporting numeric VND. No parsing or changes were applied. |
| Brand | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Model | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Registration/manufacturing year | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Mileage/ODO | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Region/location | absent | high | No corresponding column in the complete schema. |
| Listing date/time | absent | high | No corresponding column in the complete schema. |
| Title/description | subject (title only) | high | Human-readable product/ad headlines; no body/long-description column. source values explicitly end in _B2C, supporting the role classification. |

### Field profile (all records)

| Field | Observed/inferred type | Nonempty | Distinct nonempty | First nonempty example (up to 160 characters) |
|---|---|---:|---:|---|
| source | text | 287 | 1 | "otodien_B2C" |
| subject | text | 287 | 255 | "🔥 MPV7 – XE GIA ĐÌNH 7 CHỖ ĐANG CÓ ƯU ĐÃI CỰC TỐT - GIẢM GIÁ LÊN ĐẾN HÀNG TRĂM TRIỆU ĐỒNG!!!" |
| price_raw | text | 287 | 165 | "630 triệu" |
| price_clean | text → integer-valued numeric | 287 | 165 | "630000000" |
| battery_status | text | 287 | 1 | "Cần phân tích" |

### Three complete sample records

CSV samples below retain text storage; JSON samples retain native types. No fields or long values are omitted.

```json
[
  {
    "source": "otodien_B2C",
    "subject": "🔥 MPV7 – XE GIA ĐÌNH 7 CHỖ ĐANG CÓ ƯU ĐÃI CỰC TỐT - GIẢM GIÁ LÊN ĐẾN HÀNG TRĂM TRIỆU ĐỒNG!!!",
    "price_raw": "630 triệu",
    "price_clean": "630000000",
    "battery_status": "Cần phân tích"
  },
  {
    "source": "otodien_B2C",
    "subject": "VinFast VF8 2024 Plus - 52000 km",
    "price_raw": "799 triệu",
    "price_clean": "799000000",
    "battery_status": "Cần phân tích"
  },
  {
    "source": "otodien_B2C",
    "subject": "VinFast VF5 2024 Plus - 30000 km",
    "price_raw": "365 triệu",
    "price_clean": "365000000",
    "battery_status": "Cần phân tích"
  }
]
```

## data/raw/phoxedien_raw.csv

Format: **csv**. Rows/records: **373**. Fields (union): **4**.

CSV header: `source`, `subject`, `price_raw`, `battery_status`

### Field identification

| Semantic meaning | Candidate field(s) | Confidence | Evidence / limitation |
|---|---|---|---|
| Listing ID | absent | high | source is constant, not a row identifier. subject is a product/ad title and is not a reliable stable listing key, even where unique. |
| Price | price_raw | high | Currency-formatted strings use triệu (millions), ₫, or đ; where price_clean exists, 630 triệu corresponds to 630000000, supporting numeric VND. No parsing or changes were applied. |
| Brand | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Model | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Registration/manufacturing year | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Mileage/ODO | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Region/location | absent | high | No corresponding column in the complete schema. |
| Listing date/time | absent | high | No corresponding column in the complete schema. |
| Title/description | subject (title only) | high | Human-readable product/ad headlines; no body/long-description column. source values explicitly end in _B2C, supporting the role classification. |

### Field profile (all records)

| Field | Observed/inferred type | Nonempty | Distinct nonempty | First nonempty example (up to 160 characters) |
|---|---|---:|---:|---|
| source | text | 373 | 1 | "phoxedien_B2C" |
| subject | text | 373 | 39 | "Xe điện hotgirl Dylexe X2 ( ưu đãi trong tháng )" |
| price_raw | text | 373 | 24 | "11.990.000₫" |
| battery_status | text | 373 | 1 | "Kèm pin" |

### Three complete sample records

CSV samples below retain text storage; JSON samples retain native types. No fields or long values are omitted.

```json
[
  {
    "source": "phoxedien_B2C",
    "subject": "Xe điện hotgirl Dylexe X2 ( ưu đãi trong tháng )",
    "price_raw": "11.990.000₫",
    "battery_status": "Kèm pin"
  },
  {
    "source": "phoxedien_B2C",
    "subject": "Xe điện V3 946 ( ưu đãi trong tháng )",
    "price_raw": "11.990.000₫",
    "battery_status": "Kèm pin"
  },
  {
    "source": "phoxedien_B2C",
    "subject": "Xe điện Osakar Momo ( ưu đãi trong tháng )",
    "price_raw": "11.990.000₫",
    "battery_status": "Kèm pin"
  }
]
```

## data/raw/thegioixedien_raw.csv

Format: **csv**. Rows/records: **43**. Fields (union): **4**.

CSV header: `source`, `subject`, `price_raw`, `battery_status`

### Field identification

| Semantic meaning | Candidate field(s) | Confidence | Evidence / limitation |
|---|---|---|---|
| Listing ID | absent | high | source is constant, not a row identifier. subject is a product/ad title and is not a reliable stable listing key, even where unique. |
| Price | price_raw | high | Currency-formatted strings use triệu (millions), ₫, or đ; where price_clean exists, 630 triệu corresponds to 630000000, supporting numeric VND. No parsing or changes were applied. |
| Brand | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Model | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Registration/manufacturing year | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Mileage/ODO | absent as a dedicated field | high | Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed. |
| Region/location | absent | high | No corresponding column in the complete schema. |
| Listing date/time | absent | high | No corresponding column in the complete schema. |
| Title/description | subject (title only) | high | Human-readable product/ad headlines; no body/long-description column. source values explicitly end in _B2C, supporting the role classification. |

### Field profile (all records)

| Field | Observed/inferred type | Nonempty | Distinct nonempty | First nonempty example (up to 160 characters) |
|---|---|---:|---:|---|
| source | text | 43 | 1 | "thegioixedien_B2C" |
| subject | text | 43 | 43 | "Xe Máy Điện Dibao LS007" |
| price_raw | text | 43 | 35 | "22,990,000 đ" |
| battery_status | text | 43 | 1 | "Kèm pin" |

### Three complete sample records

CSV samples below retain text storage; JSON samples retain native types. No fields or long values are omitted.

```json
[
  {
    "source": "thegioixedien_B2C",
    "subject": "Xe Máy Điện Dibao LS007",
    "price_raw": "22,990,000 đ",
    "battery_status": "Kèm pin"
  },
  {
    "source": "thegioixedien_B2C",
    "subject": "Xe Máy Điện Dibao Shine",
    "price_raw": "22,990,000 đ",
    "battery_status": "Kèm pin"
  },
  {
    "source": "thegioixedien_B2C",
    "subject": "Xe Máy Điện Dibao Tesla E Đèn Vuông",
    "price_raw": "17,690,000 đ",
    "battery_status": "Kèm pin"
  }
]
```

Source integrity check: SHA-256 hashes of all seven input files were unchanged before versus after discovery.
