"""
app.py — EV Market Intelligence & Buyer Advisor
================================================
Nền tảng Phân tích Dữ liệu, Dự báo Giá xe 1 Năm tới & Cố vấn Mua sắm Xe điện
Chạy ứng dụng: streamlit run app.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Đảm bảo import được các module trong app/
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import streamlit as st

from app.data_loader import (
    load_screened_listings,
    load_market_cleaned,
    load_benchmark_timeline,
    load_chotot_oto_clean,
    get_available_brands,
    get_provinces,
    MODEL_CATALOG
)
from app.forecaster import (
    calculate_12m_forecast,
    get_best_buying_advice,
    match_timing_and_budget,
    get_resale_index_table
)
from app.model_loader import load_model_package, predict_price
from app import charts

# ─── Cấu hình trang ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EV Market Intelligence",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Bảng dịch Đa ngôn ngữ (i18n) ──────────────────────────────────────────────
TRANSLATIONS = {
    "vi": {
        "title": "EV Market Monitor & Buyer Advisor",
        "subtitle": "Hệ thống dự báo giá 12 tháng tới, lịch sử biến động giá niêm yết và cố vấn mua xe điện tại Việt Nam.",
        "kpi_total_cars": "Tổng xe khảo sát",
        "kpi_total_cars_sub": "Tin rao C2C & Showroom B2C",
        "kpi_median_price": "Giá trung vị thị trường",
        "kpi_median_price_sub": "Khoảng 240 tr - 1.5 tỷ VNĐ",
        "kpi_avg_depr": "Khấu hao trung bình",
        "kpi_avg_depr_sub": "Thấp hơn xe xăng cùng tầm",
        "kpi_best_season": "Mùa mua xe tốt nhất",
        "kpi_best_season_sub": "Đáy ưu đãi kích cầu (Tháng 7-8)",
        "tab_forecast": "Dự Báo & Thời Điểm Mua",
        "tab_history": "Lịch Sử Giá & Khấu Hao",
        "tab_showroom": "Danh Mục Dòng Xe",
        "tab_tools": "So Sánh & Công Cụ",
        "sidebar_header": "BỘ LỌC TOÀN CỤC",
        "sidebar_brand": "Hãng xe",
        "sidebar_province": "Tỉnh thành",
        "sidebar_condition": "Tình trạng xe",
        "cond_used": "Xe cũ (Đã sử dụng)",
        "cond_new": "Xe mới 100%",
        "lang_label": "Ngôn ngữ / Language",
        "theme_label": "Giao diện / Theme",
        "sec_forecast_title": "DỰ BÁO XU HƯỚNG GIÁ 12 THÁNG TỚI",
        "sec_forecast_desc": "Chọn dòng xe để xem đường cong dự báo giá trong 1 năm tới và khuyến nghị thời điểm mua.",
        "select_model": "Chọn dòng xe",
        "cond_choice": "Tình trạng xe dự báo",
        "input_price_label": "Mức giá mốc hiện tại (Triệu VNĐ)",
        "expander_table": "Xem bảng dữ liệu chi tiết 12 tháng",
        "sec_matcher_title": "CỐ VẤN THEO THỜI ĐIỂM & NGÂN SÁCH",
        "sec_matcher_desc": "Nhập thời điểm dự kiến nhận xe và ngân sách tối đa, hệ thống sẽ đề xuất danh sách xe phù hợp nhất.",
        "slider_timing": "Bạn dự định mua xe sau bao lâu nữa?",
        "slider_budget": "Ngân sách tối đa của bạn (Triệu VNĐ)",
        "budget_prefix": "Ngân sách:",
        "sec_hist_title": "LỊCH SỬ GIÁ NIÊM YẾT CHÍNH HÃNG",
        "sec_hist_desc": "Hành trình điều chỉnh giá xe kèm pin và thuê pin qua các năm từ khi ra mắt.",
        "sec_odo_title": "TƯƠNG QUAN SỐ KM ODO & GIÁ RAO BÁN",
        "sec_resale_title": "CHỈ SỐ GIỮ GIÁ CÁC MẪU XE (RESALE VALUE INDEX)",
        "sec_showroom_title": "DANH MỤC XE ĐIỆN THỰC TẾ",
        "sec_showroom_desc": "Khám phá các dòng xe điện trên thị trường với thông số, dải giá và tin đăng tham khảo.",
        "filter_segment": "Phân khúc xe",
        "sec_deals_title": "TIN ĐĂNG THỊ TRƯỜNG THAM KHẢO",
        "subtab_compare": "So Sánh 2 Xe",
        "subtab_tco": "Tính Chi Phí TCO",
        "subtab_ai": "AI Định Giá Nhanh",
        "h2h_title": "SO SÁNH TRỰC DIỆN 2 DÒNG XE",
        "select_car1": "Chọn Xe Thứ Nhất (A)",
        "select_car2": "Chọn Xe Thứ Hai (B)",
        "tco_title": "DỰ TOÁN CHI PHÍ NĂNG LƯỢNG (ĐIỆN VS XĂNG)",
        "tco_desc": "Nhập số km di chuyển hàng tháng để so sánh chi phí nạp điện so với đổ xăng trong 1 - 3 năm.",
        "tco_monthly_km": "Quãng đường di chuyển mỗi tháng (km)",
        "tco_gas_price": "Giá xăng tham chiếu (VNĐ/lít)",
        "tco_battery_mode": "Chính sách pin xe điện quan tâm",
        "tco_elec_price": "Giá điện sạc trung bình (VNĐ/kWh)",
        "tco_saving_msg": "Ước tính tiết kiệm khoảng {saving:,.1f} triệu VNĐ tiền nhiên liệu sau 3 năm so với xe xăng.",
        "ai_title": "AI ĐỊNH GIÁ XE NHANH",
        "ai_desc": "Nhập thông số xe để mô hình Random Forest ước tính khoảng giá thị trường hợp lý.",
        "ai_btn": "Định giá xe với AI",
        "ai_result_title": "GIÁ THỊ TRƯỜNG DỰ BÁO CỦA AI",
        "ai_negotiate_range": "Khoảng giá hợp lý đàm phán:",
        "ai_median": "Trung vị thị trường dòng xe",
        "ai_diff_label": "so với giá trung bình",
        "all_brand": "Tất cả",
        "all_province": "Toàn quốc",
        "all_segment": "Tất cả",
        "deal_headers": ["Tiêu đề tin rao", "Hãng", "Dòng xe", "Giá rao (Triệu VNĐ)", "Tình trạng", "Khu vực", "Ngày đăng"]
    },
    "en": {
        "title": "EV Market Monitor & Buyer Advisor",
        "subtitle": "12-month forward pricing, historical MSRP trends, and data-driven purchasing intelligence for Vietnam.",
        "kpi_total_cars": "Surveyed Vehicles",
        "kpi_total_cars_sub": "C2C Listings & B2C Showrooms",
        "kpi_median_price": "Market Median Price",
        "kpi_median_price_sub": "Range: ~240M - 1.5B VND",
        "kpi_avg_depr": "Average Depreciation",
        "kpi_avg_depr_sub": "Below ICE equivalent tier",
        "kpi_best_season": "Optimal Buying Window",
        "kpi_best_season_sub": "Mid-Year Discount Dip (Jul-Aug)",
        "tab_forecast": "Price Forecast & Timing",
        "tab_history": "Price History & Trends",
        "tab_showroom": "Vehicle Catalog",
        "tab_tools": "Compare & Tools",
        "sidebar_header": "GLOBAL FILTERS",
        "sidebar_brand": "Brand",
        "sidebar_province": "Province / Region",
        "sidebar_condition": "Vehicle Condition",
        "cond_used": "Pre-owned / Used",
        "cond_new": "New 100%",
        "lang_label": "Language / Ngôn ngữ",
        "theme_label": "Theme / Giao diện",
        "sec_forecast_title": "12-MONTH FORWARD PRICING CURVE",
        "sec_forecast_desc": "Select a model to view 1-year price forecast and buy-timing recommendations.",
        "select_model": "Select Model",
        "cond_choice": "Forecast Condition",
        "input_price_label": "Base Reference Price (Million VND)",
        "expander_table": "View Detailed 12-Month Projection Table",
        "sec_matcher_title": "TIMING & BUDGET ADVISOR",
        "sec_matcher_desc": "Specify planned purchase timeframe and maximum budget for tailored model recommendations.",
        "slider_timing": "When do you plan to take delivery?",
        "slider_budget": "Maximum Budget (Million VND)",
        "budget_prefix": "Budget:",
        "sec_hist_title": "HISTORICAL MANUFACTURER MSRP",
        "sec_hist_desc": "Historical price adjustments for battery-included versus subscription packages since launch.",
        "sec_odo_title": "ASKING PRICE VS. MILEAGE (ODO)",
        "sec_resale_title": "RESALE VALUE INDEX",
        "sec_showroom_title": "EV MARKET CATALOG",
        "sec_showroom_desc": "Browse active electric vehicle models with real-world specifications, asking prices, and verified listings.",
        "filter_segment": "Segment",
        "sec_deals_title": "VERIFIED MARKET LISTINGS",
        "subtab_compare": "Head-to-Head Compare",
        "subtab_tco": "TCO Cost Projection",
        "subtab_ai": "AI Price Valuator",
        "h2h_title": "HEAD-TO-HEAD MODEL COMPARISON",
        "select_car1": "Select Vehicle A",
        "select_car2": "Select Vehicle B",
        "tco_title": "TOTAL COST OF OWNERSHIP (ELECTRIC VS PETROL)",
        "tco_desc": "Enter monthly mileage to project 1-year to 3-year running energy costs compared to petrol alternatives.",
        "tco_monthly_km": "Monthly distance driven (km)",
        "tco_gas_price": "Reference petrol price (VND/litre)",
        "tco_battery_mode": "EV Battery Policy",
        "tco_elec_price": "Average charging rate (VND/kWh)",
        "tco_saving_msg": "Projected 3-year fuel savings reach approximately {saving:,.1f}M VND compared to ICE equivalent.",
        "ai_title": "AI VALUATION ENGINE",
        "ai_desc": "Input vehicle attributes to evaluate fair market value using the trained Random Forest model.",
        "ai_btn": "Evaluate Fair Market Price",
        "ai_result_title": "AI FAIR MARKET VALUATION",
        "ai_negotiate_range": "Target negotiation range:",
        "ai_median": "Model market median",
        "ai_diff_label": "vs. segment average",
        "all_brand": "All",
        "all_province": "Nationwide",
        "all_segment": "All",
        "deal_headers": ["Listing Title", "Brand", "Model", "Price (M VND)", "Condition", "Region", "Posted Date"]
    }
}

# ─── Nạp Dữ Liệu ──────────────────────────────────────────────────────────────
df_screened = load_screened_listings()
df_market = load_market_cleaned()
df_bench = load_benchmark_timeline()
df_chotot = load_chotot_oto_clean()
model_pkg = load_model_package()

all_brands = get_available_brands(df_market)
all_provinces = get_provinces(df_screened)

# ─── Sidebar: Cài đặt Ngôn ngữ & Theme & Bộ lọc ────────────────────────────────
with st.sidebar:
    st.markdown("<div style='font-size:0.95rem; font-weight:700; letter-spacing:-0.01em; margin-bottom:2px;'>EV MARKET MONITOR</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem; color:#94a3b8; margin-bottom:12px;'>Decision Intelligence System</div>", unsafe_allow_html=True)

    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        lang_choice = st.selectbox("Ngôn ngữ / Lang", ["Tiếng Việt", "English"], index=0)
        lang = "en" if "English" in lang_choice else "vi"
    with col_cfg2:
        theme_choice = st.selectbox("Theme", ["Light", "Dark"], index=0)
        theme = theme_choice.lower()

    t = TRANSLATIONS[lang]

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.78rem; font-weight:700; color:#94a3b8; text-transform:uppercase; margin-bottom:8px;'>{t['sidebar_header']}</div>", unsafe_allow_html=True)

    brand_options = [t["all_brand"]] + all_brands
    selected_brand = st.selectbox(t["sidebar_brand"], brand_options, index=0)

    prov_options = [t["all_province"]] + all_provinces
    selected_province = st.selectbox(t["sidebar_province"], prov_options, index=0)

    cond_options = [t["cond_used"], t["cond_new"]]
    condition_pref = st.radio(t["sidebar_condition"], cond_options, index=0)

    st.markdown("---")
    st.markdown("<div style='font-size:0.72rem; color:#64748b;'>Automotive Data Lab • Release 2.1</div>", unsafe_allow_html=True)

# ─── Dynamic CSS: Light vs Dark & Gọn Gàng ────────────────────────────────────
if theme == "dark":
    body_bg = "#0b0f19"
    card_bg = "#161f30"
    card_border = "#26354a"
    text_primary = "#f8fafc"
    text_muted = "#94a3b8"
    accent = "#38bdf8"
    header_bg = "#111827"
    header_border = "#1f2937"
else:
    body_bg = "#f8fafc"
    card_bg = "#ffffff"
    card_border = "#e2e8f0"
    text_primary = "#0f172a"
    text_muted = "#64748b"
    accent = "#2563eb"
    header_bg = "#ffffff"
    header_border = "#e2e8f0"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .stApp {{
        background-color: {body_bg};
        color: {text_primary};
    }}

    /* Compact Header Bar */
    .top-header-bar {{
        background: {header_bg};
        border: 1px solid {header_border};
        border-radius: 10px;
        padding: 12px 18px;
        margin-bottom: 14px;
        display: flex;
        flex-direction: column;
        gap: 3px;
    }}
    .top-header-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {text_primary};
        margin: 0;
        letter-spacing: -0.01em;
    }}
    .top-header-sub {{
        font-size: 0.82rem;
        color: {text_muted};
        margin: 0;
        line-height: 1.4;
    }}

    /* Compact KPI Cards */
    .compact-kpi {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 8px;
        padding: 10px 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .compact-kpi-title {{
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        color: {text_muted};
        margin-bottom: 2px;
        letter-spacing: 0.04em;
    }}
    .compact-kpi-value {{
        font-size: 1.35rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 2px;
    }}
    .compact-kpi-sub {{
        font-size: 0.75rem;
        color: #10b981;
        font-weight: 500;
    }}

    /* Compact Section Header */
    .compact-sec-header {{
        font-size: 0.98rem;
        font-weight: 700;
        color: {text_primary};
        margin: 16px 0 8px 0;
        border-left: 3px solid {accent};
        padding-left: 8px;
        letter-spacing: -0.01em;
    }}

    /* Compact Car Cards */
    .compact-car-card {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 14px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .compact-car-card:hover {{
        border-color: {accent};
        transform: translateY(-2px);
    }}
    .compact-car-img {{
        width: 100%;
        height: 130px;
        object-fit: cover;
        background: #1e293b;
    }}
    .compact-car-body {{
        padding: 10px 14px 12px 14px;
    }}
    .compact-car-title {{
        font-size: 1rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 2px;
    }}
    .compact-car-seg {{
        font-size: 0.76rem;
        color: {text_muted};
        margin-bottom: 6px;
    }}
    .compact-car-price {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {accent};
        margin-bottom: 6px;
    }}
    .compact-car-specs {{
        font-size: 0.76rem;
        color: {text_muted};
        border-top: 1px solid {card_border};
        padding-top: 6px;
        display: flex;
        justify-content: space-between;
    }}

    /* Compact Signal Card */
    .compact-signal {{
        background: {card_bg};
        border: 1px solid {card_border};
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 12px 0;
    }}
    .compact-signal-pill {{
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        color: white;
        margin-bottom: 6px;
    }}
    .compact-signal-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {text_primary};
        margin-bottom: 4px;
    }}
    .compact-signal-desc {{
        font-size: 0.88rem;
        color: {text_muted};
        line-height: 1.5;
        margin: 0;
    }}

    /* Clean Streamlit Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 1px solid {card_border};
        padding-bottom: 2px;
    }}
    .stTabs [data-baseweb="tab"] {{
        font-size: 0.9rem;
        font-weight: 600;
        color: {text_muted};
        padding: 8px 14px;
        border-radius: 6px;
    }}
    .stTabs [aria-selected="true"] {{
        color: {accent} !important;
        background: rgba(37, 99, 235, 0.08);
        font-weight: 700;
    }}

    #MainMenu, footer {{ visibility: hidden; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Top Header Bar ───────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="top-header-bar">
        <div class="top-header-title">{t['title']}</div>
        <div class="top-header-sub">{t['subtitle']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── Compact KPI Bar ──────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_cars = len(df_market[df_market["vehicle_type"] == "car"]) if not df_market.empty else len(df_screened)
median_car_price = df_screened["price_million"].median()

with kpi1:
    st.markdown(f"""
    <div class="compact-kpi">
        <div class="compact-kpi-title">{t['kpi_total_cars']}</div>
        <div class="compact-kpi-value">{total_cars:,.0f}</div>
        <div class="compact-kpi-sub">{t['kpi_total_cars_sub']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="compact-kpi">
        <div class="compact-kpi-title">{t['kpi_median_price']}</div>
        <div class="compact-kpi-value">{median_car_price:,.0f} tr</div>
        <div class="compact-kpi-sub">{t['kpi_median_price_sub']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown(f"""
    <div class="compact-kpi">
        <div class="compact-kpi-title">{t['kpi_avg_depr']}</div>
        <div class="compact-kpi-value">~7.8%/yr</div>
        <div class="compact-kpi-sub">{t['kpi_avg_depr_sub']}</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="compact-kpi">
        <div class="compact-kpi-title">{t['kpi_best_season']}</div>
        <div class="compact-kpi-value">Jul - Aug</div>
        <div class="compact-kpi-sub">{t['kpi_best_season_sub']}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ─── 4 TABS CHÍNH ─────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    t["tab_forecast"],
    t["tab_history"],
    t["tab_showroom"],
    t["tab_tools"]
])


# ==============================================================================
# TAB 1: DỰ BÁO GIÁ & THỜI ĐIỂM MUA
# ==============================================================================
with tab1:
    st.markdown(f"<div class='compact-sec-header'>{t['sec_forecast_title']}</div>", unsafe_allow_html=True)
    st.caption(t["sec_forecast_desc"])

    c1, c2, c3 = st.columns([1.5, 1.5, 1.5])
    with c1:
        avail_models = list(MODEL_CATALOG.keys())
        if selected_brand not in [t["all_brand"], "Tất cả", "All"]:
            avail_models = [m for m, spec in MODEL_CATALOG.items() if spec["brand"] == selected_brand]
            if not avail_models:
                avail_models = list(MODEL_CATALOG.keys())
        selected_model = st.selectbox(t["select_model"], avail_models, index=0)

    cat_item = MODEL_CATALOG.get(selected_model, MODEL_CATALOG["VF 5"])
    def_price = cat_item["default_price"]
    model_listings = df_screened[df_screened["family"] == selected_model.replace(" ", "")]
    if not model_listings.empty:
        act_med = model_listings["price_million"].median()
        if not np.isnan(act_med) and act_med > 0:
            def_price = act_med

    with c2:
        cond_choice = st.selectbox(t["cond_choice"], [t["cond_used"], t["cond_new"]], index=0)

    with c3:
        input_price = st.number_input(
            t["input_price_label"],
            min_value=50.0,
            max_value=3000.0,
            value=float(round(def_price, 1)),
            step=5.0
        )

    # Tính toán dự báo 12 tháng
    forecast_df = calculate_12m_forecast(
        base_price=input_price,
        model_name=selected_model,
        condition="New" if cond_choice == t["cond_new"] else "Used",
        lang=lang
    )
    advice = get_best_buying_advice(forecast_df, input_price, selected_model, lang=lang)

    # Biểu đồ dự báo
    fig_fc = charts.plot_price_forecast_curve(forecast_df, input_price, selected_model, theme=theme, lang=lang)
    st.plotly_chart(fig_fc, use_container_width=True)

    # Thẻ tín hiệu gọn gàng
    st.markdown(f"""
    <div class="compact-signal" style="border-left-color: {advice['color']};">
        <span class="compact-signal-pill" style="background-color: {advice['color']};">{advice['signal']}</span>
        <div class="compact-signal-title">Optimal Buy Window: {advice['best_month']}</div>
        <p class="compact-signal-desc">{advice['summary']}</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(t["expander_table"]):
        disp_df = forecast_df[["date_str", "month_name", "pred_price", "price_min", "price_max", "saving_vs_now", "season_label"]].copy()
        if lang == "en":
            disp_df.columns = ["Period", "Month", "Forecast (M)", "Min (M)", "Max (M)", "Saving vs Now (M)", "Seasonality"]
        else:
            disp_df.columns = ["Thời điểm", "Tháng", "Giá dự kiến (tr)", "Tối thiểu (tr)", "Tối đa (tr)", "Tiết kiệm (tr)", "Đặc điểm mùa vụ"]
        st.dataframe(disp_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # TIMING & BUDGET MATCHER
    st.markdown(f"<div class='compact-sec-header'>{t['sec_matcher_title']}</div>", unsafe_allow_html=True)
    st.caption(t["sec_matcher_desc"])

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        target_month_offset = st.slider(t["slider_timing"], 1, 12, 6)
        target_date_preview = datetime.now() + pd.DateOffset(months=target_month_offset)
        target_month_str = f"{target_date_preview.month}/{target_date_preview.year}"
        st.caption(f"Target: **{target_month_str}**")

    with col_m2:
        budget_input = st.slider(t["slider_budget"], 150, 1800, 600, step=10)
        st.caption(f"{t['budget_prefix']} **{budget_input:,.0f}M VND**")

    matched_candidates = match_timing_and_budget(
        target_month_offset=target_month_offset,
        budget_million=budget_input,
        brand_filter=selected_brand,
        condition="New" if cond_choice == t["cond_new"] else "Used",
        lang=lang
    )

    if not matched_candidates:
        st.info("No matching models found for this budget. Try widening the budget slider.")
    else:
        cols = st.columns(3)
        for idx, car in enumerate(matched_candidates):
            with cols[idx % 3]:
                badge_col = "#10b981" if car["fit_code"] == "perfect" else ("#0284c7" if car["fit_code"] == "economical" else "#f59e0b")
                diff_label = f"Surplus: {car['budget_diff']:,.0f}M" if car['budget_diff'] >= 0 else f"Shortfall: {abs(car['budget_diff']):,.0f}M"
                if lang == "vi":
                    diff_label = f"Dư: {car['budget_diff']:,.0f} tr" if car['budget_diff'] >= 0 else f"Cần thêm: {abs(car['budget_diff']):,.0f} tr"

                st.markdown(f"""
                <div class="compact-car-card">
                    <img src="{car['image']}" class="compact-car-img" alt="{car['model']}">
                    <div class="compact-car-body">
                        <span style="background:{badge_col}; color:white; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:4px;">{car['fit_status']}</span>
                        <div class="compact-car-title" style="margin-top:6px;">{car['model']}</div>
                        <div class="compact-car-seg">{car['brand']} • {car['segment']}</div>
                        <div class="compact-car-price">~{car['future_price']:,.0f}M VND</div>
                        <div style="font-size:0.78rem; color:{text_muted}; margin-bottom:6px;">{diff_label} • @ {car['target_month_name']}</div>
                        <div class="compact-car-specs">
                            <span>Range: {car['range_km']} km</span>
                            <span>{car['seats']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: LỊCH SỬ GIÁ & KHẤU HAO
# ==============================================================================
with tab2:
    st.markdown(f"<div class='compact-sec-header'>{t['sec_hist_title']}</div>", unsafe_allow_html=True)
    st.caption(t["sec_hist_desc"])

    c_hist1, c_hist2 = st.columns([2, 1])
    with c_hist1:
        bench_models = df_bench["Model"].dropna().unique().tolist()
        hist_model_choice = st.selectbox(t["select_model"], bench_models, index=0)
        fig_hist = charts.plot_historical_timeline(df_bench, hist_model_choice, theme=theme, lang=lang)
        st.plotly_chart(fig_hist, use_container_width=True)

    with c_hist2:
        df_hist_sub = df_bench[df_bench["Model"] == hist_model_choice][
            ["Year", "price_with_bat_million", "price_no_bat_million", "bat_cost_million", "Notes"]
        ].sort_values("Year", ascending=False)
        if lang == "en":
            df_hist_sub.columns = ["Year", "Battery Incl. (M)", "Subscription (M)", "Battery (M)", "Notes"]
        else:
            df_hist_sub.columns = ["Năm", "Kèm Pin (tr)", "Thuê Pin (tr)", "Giá Pin (tr)", "Ghi chú"]
        st.dataframe(df_hist_sub, use_container_width=True, hide_index=True)

    st.markdown("---")

    st.markdown(f"<div class='compact-sec-header'>{t['sec_odo_title']}</div>", unsafe_allow_html=True)
    fig_odo = charts.plot_price_vs_odo(df_screened, hist_model_choice, theme=theme, lang=lang)
    st.plotly_chart(fig_odo, use_container_width=True)

    st.markdown("---")

    st.markdown(f"<div class='compact-sec-header'>{t['sec_resale_title']}</div>", unsafe_allow_html=True)
    resale_df = get_resale_index_table(lang=lang)
    st.dataframe(resale_df, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 3: DANH MỤC XE & THỊ TRƯỜNG
# ==============================================================================
with tab3:
    st.markdown(f"<div class='compact-sec-header'>{t['sec_showroom_title']}</div>", unsafe_allow_html=True)
    st.caption(t["sec_showroom_desc"])

    seg_list = ["Tất cả", "Mini SUV", "SUV Hạng A", "SUV Hạng B", "SUV Hạng C", "SUV Hạng D", "SUV Hạng E (Full-size)", "MPV 7 chỗ", "Sedan Hạng D"]
    selected_seg = st.selectbox(t["filter_segment"], seg_list, index=0)

    filtered_catalog = {
        m: spec for m, spec in MODEL_CATALOG.items()
        if (selected_seg == "Tất cả" or spec["segment"] == selected_seg) and
           (selected_brand in [t["all_brand"], "Tất cả", "All"] or spec["brand"] == selected_brand)
    }

    cols_sr = st.columns(3)
    for i, (m_name, spec) in enumerate(filtered_catalog.items()):
        m_listings = df_screened[df_screened["family"] == m_name.replace(" ", "")]
        if not m_listings.empty:
            p_med = m_listings["price_million"].median()
            p_min = m_listings["price_million"].min()
            p_max = m_listings["price_million"].max()
            price_str = f"{p_med:,.0f}M VND" if lang == "en" else f"{p_med:,.0f} triệu"
            range_str = f"{p_min:,.0f} - {p_max:,.0f}M ({len(m_listings)} listings)" if lang == "en" else f"{p_min:,.0f} - {p_max:,.0f} tr ({len(m_listings)} tin)"
        else:
            price_str = f"~{spec['default_price']:,.0f}M VND" if lang == "en" else f"~{spec['default_price']:,.0f} triệu"
            range_str = "MSRP Reference" if lang == "en" else "Giá niêm yết tham chiếu"

        with cols_sr[i % 3]:
            st.markdown(f"""
            <div class="compact-car-card">
                <img src="{spec['image']}" class="compact-car-img" alt="{m_name}">
                <div class="compact-car-body">
                    <span style="background:rgba(37,99,235,0.1); color:{accent}; font-size:0.7rem; font-weight:700; padding:2px 6px; border-radius:4px;">{spec['segment']}</span>
                    <div class="compact-car-title" style="margin-top:4px;">{m_name}</div>
                    <div class="compact-car-seg">{spec['brand']} • {spec['target_audience']}</div>
                    <div class="compact-car-price">{price_str}</div>
                    <div style="font-size:0.76rem; color:{text_muted}; margin-bottom:8px;">{range_str}</div>
                    <div class="compact-car-specs">
                        <span>{spec['battery_kwh']} kWh</span>
                        <span>{spec['range_km']} km</span>
                        <span>{spec['power_hp']} hp</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f"<div class='compact-sec-header'>{t['sec_deals_title']}</div>", unsafe_allow_html=True)
    if not df_chotot.empty:
        valid_deals = df_chotot[(df_chotot["price_million"] > 50) & (df_chotot["price_million"] < 2500)].copy()
        if selected_brand not in [t["all_brand"], "Tất cả", "All"]:
            valid_deals = valid_deals[valid_deals["brand_name"].str.contains(selected_brand, case=False, na=False)]

        deal_sample = valid_deals[["title", "brand_name", "model_name", "price_million", "condition", "region_name", "posted_at"]].head(10).copy()
        deal_sample.columns = t["deal_headers"]
        st.dataframe(deal_sample, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 4: SO SÁNH & CÔNG CỤ
# ==============================================================================
with tab4:
    tool_tab1, tool_tab2, tool_tab3 = st.tabs([
        t["subtab_compare"],
        t["subtab_tco"],
        t["subtab_ai"]
    ])

    # ──────────────────────────────────────────────────────────────────────────
    # SUB-TAB 4.1: SO SÁNH ĐỐI ĐẦU 2 MẪU XE
    with tool_tab1:
        st.markdown(f"<div class='compact-sec-header'>{t['h2h_title']}</div>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        models_list = list(MODEL_CATALOG.keys())
        with col_c1:
            car1_name = st.selectbox(t["select_car1"], models_list, index=1)
        with col_c2:
            car2_name = st.selectbox(t["select_car2"], models_list, index=2)

        spec1 = MODEL_CATALOG[car1_name]
        spec2 = MODEL_CATALOG[car2_name]
        fc1 = calculate_12m_forecast(spec1["default_price"], car1_name, "Used", lang=lang)
        fc2 = calculate_12m_forecast(spec2["default_price"], car2_name, "Used", lang=lang)

        car1_dict = {"name": car1_name, "price": spec1["default_price"], "future_price": fc1.iloc[-1]["pred_price"], "range": spec1["range_km"], "power": spec1["power_hp"]}
        car2_dict = {"name": car2_name, "price": spec2["default_price"], "future_price": fc2.iloc[-1]["pred_price"], "range": spec2["range_km"], "power": spec2["power_hp"]}

        fig_cmp = charts.plot_head_to_head_bars(car1_dict, car2_dict, theme=theme, lang=lang)
        st.plotly_chart(fig_cmp, use_container_width=True)

        if lang == "en":
            cmp_df = pd.DataFrame([
                {"Attribute": "Manufacturer", car1_name: spec1["brand"], car2_name: spec2["brand"]},
                {"Attribute": "Segment", car1_name: spec1["segment"], car2_name: spec2["segment"]},
                {"Attribute": "Seating Capacity", car1_name: spec1["seats"], car2_name: spec2["seats"]},
                {"Attribute": "Base Price (M VND)", car1_name: f"{spec1['default_price']:,.0f}", car2_name: f"{spec2['default_price']:,.0f}"},
                {"Attribute": "1Y Forecast Price (M)", car1_name: f"{fc1.iloc[-1]['pred_price']:,.0f}", car2_name: f"{fc2.iloc[-1]['pred_price']:,.0f}"},
                {"Attribute": "Battery Capacity", car1_name: f"{spec1['battery_kwh']} kWh", car2_name: f"{spec2['battery_kwh']} kWh"},
                {"Attribute": "Electric Range", car1_name: f"~{spec1['range_km']} km", car2_name: f"~{spec2['range_km']} km"},
                {"Attribute": "Max Power", car1_name: f"{spec1['power_hp']} hp", car2_name: f"{spec2['power_hp']} hp"},
            ])
            st.table(cmp_df.set_index("Attribute"))
        else:
            cmp_df = pd.DataFrame([
                {"Tiêu chí": "Hãng sản xuất", car1_name: spec1["brand"], car2_name: spec2["brand"]},
                {"Tiêu chí": "Phân khúc", car1_name: spec1["segment"], car2_name: spec2["segment"]},
                {"Tiêu chí": "Số chỗ ngồi", car1_name: spec1["seats"], car2_name: spec2["seats"]},
                {"Tiêu chí": "Giá mốc (triệu VNĐ)", car1_name: f"{spec1['default_price']:,.0f}", car2_name: f"{spec2['default_price']:,.0f}"},
                {"Tiêu chí": "Giá dự báo 1 năm (tr)", car1_name: f"{fc1.iloc[-1]['pred_price']:,.0f}", car2_name: f"{fc2.iloc[-1]['pred_price']:,.0f}"},
                {"Tiêu chí": "Dung lượng pin", car1_name: f"{spec1['battery_kwh']} kWh", car2_name: f"{spec2['battery_kwh']} kWh"},
                {"Tiêu chí": "Quãng đường 1 lần sạc", car1_name: f"~{spec1['range_km']} km", car2_name: f"~{spec2['range_km']} km"},
                {"Tiêu chí": "Công suất động cơ", car1_name: f"{spec1['power_hp']} mã lực", car2_name: f"{spec2['power_hp']} mã lực"},
            ])
            st.table(cmp_df.set_index("Tiêu chí"))

    # ──────────────────────────────────────────────────────────────────────────
    # SUB-TAB 4.2: TÍNH TCO
    with tool_tab2:
        st.markdown(f"<div class='compact-sec-header'>{t['tco_title']}</div>", unsafe_allow_html=True)
        st.caption(t["tco_desc"])

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            km_input = st.slider(t["tco_monthly_km"], 500, 5000, 1500, step=100)
            gas_price = st.number_input(t["tco_gas_price"], value=24000, step=500)

        with col_t2:
            battery_mode = st.radio(t["tco_battery_mode"], ["Battery Included (Mua đứt pin)", "Subscription (Thuê pin)"])
            elec_price = st.number_input(t["tco_elec_price"], value=3858, step=100)

        fig_tco = charts.plot_tco_comparison(
            monthly_km=km_input,
            ev_kwh_per_100km=14.0,
            gas_l_per_100km=7.5,
            gas_price_vnd=float(gas_price),
            elec_price_vnd=float(elec_price),
            battery_rent_monthly=1200000.0,
            theme=theme,
            lang=lang
        )
        st.plotly_chart(fig_tco, use_container_width=True)

        annual_gas = (km_input * 12 / 100.0) * 7.5 * gas_price
        annual_ev = (km_input * 12 / 100.0) * 14.0 * elec_price
        if "Subscription" in battery_mode or "Thuê pin" in battery_mode:
            annual_ev += 1200000 * 12
        saving_3y = (annual_gas - annual_ev) * 3 / 1e6

        st.success(t["tco_saving_msg"].format(saving=saving_3y))

    # ──────────────────────────────────────────────────────────────────────────
    # SUB-TAB 4.3: AI ĐỊNH GIÁ XE
    with tool_tab3:
        st.markdown(f"<div class='compact-sec-header'>{t['ai_title']}</div>", unsafe_allow_html=True)
        st.caption(t["ai_desc"])

        col_ai1, col_ai2, col_ai3 = st.columns(3)
        with col_ai1:
            vf_families = [f for f in ["VF3", "VF5", "VF6", "VF7", "VF8", "VF9", "VFe34"] if f in model_pkg["family_price_medians"]]
            ai_family = st.selectbox("VinFast Model", vf_families, index=1)
            ai_cond = st.selectbox("Condition", ["Used", "New"], format_func=lambda x: t["cond_used"] if x == "Used" else t["cond_new"])

        with col_ai2:
            ai_year = st.selectbox("Year", [2026, 2025, 2024, 2023, 2022], index=1)
            ai_odo = st.number_input("Mileage (km)", min_value=0, max_value=200000, value=25000 if ai_cond == "Used" else 0, step=5000)

        with col_ai3:
            default_prov_idx = all_provinces.index("Hà Nội") if "Hà Nội" in all_provinces else 0
            ai_prov = st.selectbox("Province", all_provinces, index=default_prov_idx)

        if st.button(t["ai_btn"], type="primary", use_container_width=True):
            predicted_p, family_med = predict_price(
                model_package=model_pkg,
                family=ai_family,
                condition=ai_cond,
                year=ai_year,
                odo_km=float(ai_odo),
                province=ai_prov
            )

            diff_to_med = predicted_p - family_med
            st.write("")
            res_col1, res_col2 = st.columns([1.5, 1])

            with res_col1:
                st.markdown(f"""
                <div style="background:{card_bg}; border:1px solid {card_border}; border-left:4px solid {accent}; border-radius:8px; padding:14px 18px;">
                    <div style="font-size:0.75rem; color:{text_muted}; font-weight:700; text-transform:uppercase;">{t['ai_result_title']}</div>
                    <div style="font-size:1.8rem; font-weight:800; color:{accent}; margin:4px 0;">{predicted_p:,.1f}M VND</div>
                    <div style="font-size:0.82rem; color:{text_muted};">
                        {t['ai_negotiate_range']} <b>{predicted_p*0.96:,.0f} - {predicted_p*1.04:,.0f}M VND</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with res_col2:
                st.metric(t["ai_median"], f"{family_med:,.1f}M", delta=f"{diff_to_med:+,.1f}M {t['ai_diff_label']}", delta_color="inverse")
