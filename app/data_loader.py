"""
app/data_loader.py
------------------
Cung cấp các hàm nạp dữ liệu và trích xuất đặc trưng cho ứng dụng Streamlit:
1. load_screened_listings(): Dữ liệu ô tô VinFast đã lọc sạch phục vụ ML & EDA
2. load_market_cleaned(): Dữ liệu toàn bộ thị trường xe điện đã tính khấu hao
3. load_benchmark_timeline(): Ma trận timeline giá niêm yết qua các năm
4. load_chotot_oto_clean(): Dữ liệu tin rao Chợ Tốt đầy đủ ảnh và mô tả
5. MODEL_CATALOG: Danh mục thông số kỹ thuật chuẩn và ảnh đại diện xe
"""

from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"
SCREENED_PATH = DATA_DIR / "processed" / "buyer_eda" / "screened_listings.csv"
MARKET_PATH = DATA_DIR / "processed" / "ev_market_cleaned.csv"
BENCHMARK_PATH = DATA_DIR / "benchmark" / "ev_benchmark_timeline.csv"
CHOTOT_PATH = DATA_DIR / "interim" / "chotot_oto_clean.csv"

# ─── Model Catalog & Specifications ───────────────────────────────────────────
MODEL_CATALOG = {
    "VF 3": {
        "brand": "VinFast",
        "segment": "Mini SUV",
        "seats": "4 chỗ",
        "battery_kwh": 18.64,
        "range_km": 210,
        "power_hp": 43,
        "target_audience": "Đi phố, cá nhân, đô thị linh hoạt",
        "image": "https://cdn.chotot.com/-OUV1QVmESeDJEFll8JkdWt0sVA7lWOJS7KD6INQmEE/preset:listing/plain/6e3a411b1376d0370fe1207ad4d7d668-3000728596725807795.jpg",
        "default_price": 285.0
    },
    "VF 5": {
        "brand": "VinFast",
        "segment": "SUV Hạng A",
        "seats": "5 chỗ",
        "battery_kwh": 37.23,
        "range_km": 326,
        "power_hp": 134,
        "target_audience": "Gia đình trẻ, dịch vụ Xanh SM, kinh tế",
        "image": "https://cdn.chotot.com/8jIHif_to2xNLCKUzOVZd_PjXuS1q9S1-VM0Dk6G6h0/preset:listing/plain/38bd50e1cbc64d59afdb3394f94917e8-2998693450697083597.jpg",
        "default_price": 468.0
    },
    "VF 6": {
        "brand": "VinFast",
        "segment": "SUV Hạng B",
        "seats": "5 chỗ",
        "battery_kwh": 59.6,
        "range_km": 399,
        "power_hp": 201,
        "target_audience": "Gia đình hiện đại, thể thao, tiện nghi",
        "image": "https://cdn.chotot.com/6KGg9fxlFeIMtKa8afuTL7lcYChP-ND56t6HIvqCT-E/preset:listing/plain/3292d96b073f44b5effee511b43b7886-3001450546157685648.jpg",
        "default_price": 646.0
    },
    "VF 7": {
        "brand": "VinFast",
        "segment": "SUV Hạng C",
        "seats": "5 chỗ",
        "battery_kwh": 75.3,
        "range_km": 496,
        "power_hp": 348,
        "target_audience": "Doanh nhân trẻ, thiết kế phi thuyền, hiệu suất cao",
        "image": "https://cdn.chotot.com/JaL6ev1sMmrIbBbEi5DJd-IREyiWq1LjUcUH4UIWq5k/preset:listing/plain/164812460517b3c26674e2c1e734e8a4-3001460965104296152.jpg",
        "default_price": 740.0
    },
    "VF 8": {
        "brand": "VinFast",
        "segment": "SUV Hạng D",
        "seats": "5 chỗ",
        "battery_kwh": 87.7,
        "range_km": 471,
        "power_hp": 402,
        "target_audience": "Gia đình đông người, đường trường, công nghệ ADAS",
        "image": "https://cdn.chotot.com/iCWT1wgdRmxxjo4pX_1YGDZAkxgI6OfJgnhUiGA5eDM/preset:listing/plain/fc9a8b3666e76ef823125a74a40658c2-3001346862507414090.jpg",
        "default_price": 898.0
    },
    "VF 9": {
        "brand": "VinFast",
        "segment": "SUV Hạng E (Full-size)",
        "seats": "6-7 chỗ",
        "battery_kwh": 123.0,
        "range_km": 626,
        "power_hp": 402,
        "target_audience": "Ghế cơ trưởng, doanh nhân, thương gia, sang trọng",
        "image": "https://cdn.chotot.com/j02WtHLRDRZu36Xtt0uJWRdPmM85Qi6BJa159ipkZbk/preset:listing/plain/f721728ddd29ad1b7a4499226b685568-2997051732508335229.jpg",
        "default_price": 1348.0
    },
    "VF e34": {
        "brand": "VinFast",
        "segment": "Crossover C-",
        "seats": "5 chỗ",
        "battery_kwh": 42.0,
        "range_km": 318,
        "power_hp": 147,
        "target_audience": "Đô thị, taxi công nghệ, xe tiên phong bền bỉ",
        "image": "https://cdn.chotot.com/qxbumYjy4f_xiOumce5VEsjCi8fqelHNUhHqM-w6RvE/preset:listing/plain/49816dc271650028081bf61898a4ea79-3001376151328700014.jpg",
        "default_price": 710.0
    },
    "Limo Green": {
        "brand": "VinFast",
        "segment": "MPV 7 chỗ",
        "seats": "7 chỗ",
        "battery_kwh": 65.0,
        "range_km": 420,
        "power_hp": 175,
        "target_audience": "Dịch vụ chuyên chở cao cấp, vận chuyển sân bay, du lịch",
        "image": "https://cdn.chotot.com/uD3xHOEEvc4eVqr8qU4ERQO7MGZpKdpl5uTDno3ngZg/preset:listing/plain/255cdd8234077cecc93d4d1d89978bda-3001382027658265805.jpg",
        "default_price": 699.0
    },
    "Seal": {
        "brand": "BYD",
        "segment": "Sedan Hạng D",
        "seats": "5 chỗ",
        "battery_kwh": 82.5,
        "range_km": 570,
        "power_hp": 313,
        "target_audience": "Sedan thể thao cao cấp, công nghệ pin Blade, bứt tốc",
        "image": "https://cdn.chotot.com/cKJlJ1ni9dFcL6pZ0MzQVrtsAd0TFXlK-Hks_CuiT-8/preset:listing/plain/7468799f6262ed0ab159dfbea168cad0-2998188095859855663.jpg",
        "default_price": 1119.0
    },
    "Dolphin": {
        "brand": "BYD",
        "segment": "Hatchback B",
        "seats": "5 chỗ",
        "battery_kwh": 44.9,
        "range_km": 405,
        "power_hp": 94,
        "target_audience": "Nữ giới, gia đình nhỏ, di chuyển nội đô thanh lịch",
        "image": "https://cdn.chotot.com/8O9f3-W0ZHDBuD9pKnuWPBLH3d8t2e5PmrEQkpOmLOw/preset:listing/plain/9d38bd48532d1d3faf97549e95f754e0-2999753246245434306.jpg",
        "default_price": 499.0
    },
    "Hongguang Mini EV": {
        "brand": "Wuling",
        "segment": "Micro EV",
        "seats": "4 chỗ",
        "battery_kwh": 13.9,
        "range_km": 170,
        "power_hp": 27,
        "target_audience": "Che mưa nắng, đô thị chật hẹp, chi phí siêu rẻ",
        "image": "https://cdn.chotot.com/iJZhG-KC1drgyLf6zdBA1ik1fgGBfqYHoQpA0RAA10M/preset:listing/plain/4d352774295e607793b53d6a436f3cda-3000882033079668479.jpg",
        "default_price": 239.0
    }
}


def normalize_model_name(name: str) -> str:
    """Chuẩn hóa tên model về tên chuẩn trong Catalog."""
    if not isinstance(name, str):
        return "Khác"
    s = name.strip()
    mapping = {
        "VF3": "VF 3",
        "VF 3": "VF 3",
        "VF5": "VF 5",
        "VF 5": "VF 5",
        "VF5 Plus": "VF 5",
        "VF6": "VF 6",
        "VF 6": "VF 6",
        "VF7": "VF 7",
        "VF 7": "VF 7",
        "VF8": "VF 8",
        "VF 8": "VF 8",
        "VF8 Lux": "VF 8",
        "VF9": "VF 9",
        "VF 9": "VF 9",
        "VFe34": "VF e34",
        "VF e34": "VF e34",
        "Limo Green": "Limo Green",
        "Seal": "Seal",
        "Dolphin": "Dolphin",
        "Hongguang Mini EV": "Hongguang Mini EV",
    }
    return mapping.get(s, s)


@st.cache_data(show_spinner=False)
def load_screened_listings() -> pd.DataFrame:
    """Nạp danh sách tin đã lọc sạch của VinFast."""
    df = pd.read_csv(SCREENED_PATH)
    eligible = df[df["price_eligible"] == True].copy()
    eligible["price_million"] = eligible["price_vnd"] / 1_000_000
    eligible = eligible.rename(columns={"region": "province"})
    return eligible


@st.cache_data(show_spinner=False)
def load_market_cleaned() -> pd.DataFrame:
    """Nạp dữ liệu toàn bộ thị trường xe điện đã chuẩn hóa và tính khấu hao."""
    if not MARKET_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(MARKET_PATH)
    df["price_million"] = df["price_vnd"] / 1_000_000
    df["norm_model"] = df["model"].apply(normalize_model_name)
    return df


@st.cache_data(show_spinner=False)
def load_benchmark_timeline() -> pd.DataFrame:
    """Nạp ma trận giá niêm yết tham chiếu theo năm."""
    if not BENCHMARK_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(BENCHMARK_PATH)
    df["price_million"] = df["Price_Benchmark"] / 1_000_000
    df["price_no_bat_million"] = df["Price_No_Battery"] / 1_000_000
    df["price_with_bat_million"] = df["Price_With_Battery"] / 1_000_000
    df["bat_cost_million"] = df["Battery_Cost"] / 1_000_000
    return df


@st.cache_data(show_spinner=False)
def load_chotot_oto_clean() -> pd.DataFrame:
    """Nạp dữ liệu interim ô tô Chợ Tốt để lấy hình ảnh và mô tả."""
    if not CHOTOT_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(CHOTOT_PATH)
    df["price_million"] = df["price_vnd"] / 1_000_000
    df["norm_model"] = df["model_name"].apply(normalize_model_name)
    return df


def get_available_brands(df_market: pd.DataFrame) -> list[str]:
    """Lấy danh sách các hãng ô tô có trong dữ liệu."""
    if df_market.empty:
        return ["VinFast", "BYD", "Wuling"]
    car_df = df_market[df_market["vehicle_type"] == "car"]
    brands = car_df["brand"].dropna().unique().tolist()
    # Ưu tiên VinFast, BYD, Wuling lên đầu
    priority = ["VinFast", "BYD", "Wuling"]
    res = [b for b in priority if b in brands] + [b for b in brands if b not in priority and b != "Khác"]
    return res if res else ["VinFast", "BYD", "Wuling"]


def get_models_by_brand(brand: str) -> list[str]:
    """Lấy danh sách các dòng xe theo hãng."""
    models = [m for m, spec in MODEL_CATALOG.items() if spec["brand"] == brand]
    return models if models else ["VF 5"]


def get_provinces(df: pd.DataFrame) -> list[str]:
    """Danh sách tỉnh thành."""
    col = "province" if "province" in df.columns else "region_name"
    if col in df.columns:
        return sorted(df[col].dropna().unique().tolist())
    return ["Toàn quốc", "Hà Nội", "Tp Hồ Chí Minh", "Đà Nẵng", "Bình Dương"]


def get_conditions() -> list[str]:
    return ["Tất cả", "Xe cũ (Đã sử dụng)", "Xe mới (Chưa lăn bánh)"]
