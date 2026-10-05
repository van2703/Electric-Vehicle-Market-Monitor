"""
app.py — EV Market Intelligence & Smart Buyer Advisor
=====================================================
Nền tảng Phân tích Dữ liệu, Dự báo Giá xe 1 Năm tới & Tư vấn Mua sắm Xe điện
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
    get_models_by_brand,
    get_provinces,
    MODEL_CATALOG,
    normalize_model_name
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
    page_title="EV Market Intelligence & Buyer Advisor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS Styling Hiện Đại & Sang Trọng ───────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    }

    /* Gradient Background nhẹ nhàng cho body */
    .stApp {
        background-color: #f8fafc;
    }

    /* Sidebar sang trọng tông Navy đậm */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #090d16 0%, #0f172a 100%);
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label {
        color: #94a3b8 !important;
        font-weight: 600;
        font-size: 0.88rem;
    }

    /* Hero Banner ấn tượng */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%);
        border-radius: 20px;
        padding: 32px 40px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(2, 132, 199, 0.25);
        color: white;
    }
    .hero-banner h1 {
        font-size: 2.2rem;
        font-weight: 800;
        color: white !important;
        letter-spacing: -0.02em;
        margin-bottom: 8px;
    }
    .hero-banner p {
        font-size: 1.05rem;
        color: rgba(255, 255, 255, 0.9) !important;
        max-width: 900px;
        line-height: 1.5;
        margin: 0;
    }

    /* Thẻ chỉ số KPI */
    .kpi-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06);
    }
    .kpi-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 0.85rem;
        color: #10b981;
        font-weight: 600;
    }

    /* Hộp khuyến nghị thời điểm mua */
    .signal-card {
        border-radius: 16px;
        padding: 24px 28px;
        margin: 18px 0;
        border: 2px solid;
    }
    .signal-card.success {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-color: #10b981;
    }
    .signal-card.warning {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-color: #f59e0b;
    }
    .signal-card.info {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-color: #3b82f6;
    }
    .signal-badge {
        display: inline-block;
        font-size: 0.85rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 6px 14px;
        border-radius: 30px;
        color: white;
        margin-bottom: 12px;
    }
    .signal-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 8px;
    }
    .signal-desc {
        font-size: 1rem;
        color: #334155;
        line-height: 1.6;
    }

    /* Thẻ xe Showroom */
    .car-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 20px;
        transition: all 0.25s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }
    .car-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 0, 0, 0.09);
        border-color: #cbd5e1;
    }
    .car-card-img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        background: #f1f5f9;
    }
    .car-card-body {
        padding: 18px 20px;
    }
    .car-card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .car-card-seg {
        font-size: 0.82rem;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .car-card-price {
        font-size: 1.35rem;
        font-weight: 800;
        color: #2563eb;
        margin-bottom: 10px;
    }
    .car-card-specs {
        font-size: 0.85rem;
        color: #475569;
        display: flex;
        gap: 12px;
        border-top: 1px solid #f1f5f9;
        padding-top: 10px;
    }

    /* Tiêu đề mục */
    .section-header {
        font-size: 1.35rem;
        font-weight: 700;
        color: #0f172a;
        margin: 28px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
        font-weight: 600;
        color: #64748b;
        border-radius: 8px 8px 0 0;
        padding: 10px 18px;
    }
    .stTabs [aria-selected="true"] {
        color: #2563eb !important;
        border-bottom: 3px solid #2563eb !important;
        font-weight: 700;
    }

    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Nạp Dữ Liệu Toàn Cục ──────────────────────────────────────────────────────
df_screened = load_screened_listings()
df_market = load_market_cleaned()
df_bench = load_benchmark_timeline()
df_chotot = load_chotot_oto_clean()
model_pkg = load_model_package()

all_brands = get_available_brands(df_market)
all_provinces = get_provinces(df_screened)

# ─── Sidebar Điều Khiển Toàn Cục ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ EV MARKET MONITOR")
    st.markdown("<p style='font-size:0.85rem; color:#94a3b8;'>Hệ sinh thái phân tích & cố vấn mua xe điện Việt Nam</p>", unsafe_allow_html=True)
    st.divider()

    st.markdown("**⚙️ BỘ LỌC TOÀN CỤC**")
    selected_brand = st.selectbox("Hãng xe ưu tiên", ["Tất cả"] + all_brands, index=0)
    selected_province = st.selectbox("Thị trường / Tỉnh thành", ["Toàn quốc"] + all_provinces, index=0)
    condition_pref = st.radio("Tình trạng xe quan tâm", ["Xe cũ (Đã sử dụng)", "Xe mới 100%"], index=0)

    st.divider()
    st.markdown("""
    **💡 Gợi ý nhanh:**
    - Khảo sát giá xe 12 tháng tới để tìm đợt xả hàng ưu đãi.
    - So sánh chi phí thuê pin vs mua đứt pin khi vận hành thực tế.
    """)
    st.markdown("<div style='font-size:0.75rem; color:#64748b; margin-top:20px;'>Phiên bản 2.0 • Dữ liệu cập nhật 2026</div>", unsafe_allow_html=True)

# ─── Hero Banner Đầu Trang ────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero-banner">
        <h1>⚡ EV MARKET INTELLIGENCE & BUYER ADVISOR</h1>
        <p>Hệ thống dự báo xu hướng giá xe điện 1 năm tới, phân tích lịch sử biến động giá niêm yết và cố vấn thời điểm mua xe thông minh dựa trên dữ liệu lớn thị trường Việt Nam.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── KPI Metrics Bar ──────────────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_cars = len(df_market[df_market["vehicle_type"] == "car"]) if not df_market.empty else len(df_screened)
median_car_price = df_screened["price_million"].median()

with kpi1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Tổng xe khảo sát</div>
        <div class="kpi-value">{total_cars:,.0f}</div>
        <div class="kpi-sub">Tin rao C2C & Showroom B2C</div>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Giá trung vị thị trường</div>
        <div class="kpi-value">{median_car_price:,.0f} tr</div>
        <div class="kpi-sub">Khoảng 240 tr - 1.5 tỷ VNĐ</div>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">Khấu hao trung bình</div>
        <div class="kpi-value">~7.8%/năm</div>
        <div class="kpi-sub">Thấp hơn xe xăng cùng tầm</div>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown("""
    <div class="kpi-card">
        <div class="kpi-title">Mùa mua xe tốt nhất</div>
        <div class="kpi-value">Tháng 7 - 8</div>
        <div class="kpi-sub">Đáy ưu đãi kích cầu (Tháng Ngâu)</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ─── BỐ CỤC 4 TABS CHÍNH ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🔮 Dự Báo Giá & Thời Điểm Mua",
    "📈 Lịch Sử Giá & Khấu Hao",
    "🚗 Showroom & Chi Tiết Dòng Xe",
    "⚖️ So Sánh Xe, Tính TCO & AI Định Giá"
])


# ==============================================================================
# TAB 1: DỰ BÁO GIÁ 12 THÁNG & TƯ VẤN THỜI ĐIỂM MUA
# ==============================================================================
with tab1:
    st.markdown("<div class='section-header'>🔮 DỰ BÁO XU HƯỚNG GIÁ XE 12 THÁNG TỚI</div>", unsafe_allow_html=True)
    st.markdown("Chọn dòng xe bạn đang quan tâm để xem đường cong biến động giá trong 1 năm tới và nhận phân tích **Thời điểm vàng để xuống tiền**.")

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.5, 1.5, 1.5])
    with col_ctrl1:
        # Lọc danh sách model theo brand đã chọn ở sidebar
        avail_models = list(MODEL_CATALOG.keys())
        if selected_brand != "Tất cả":
            avail_models = [m for m, spec in MODEL_CATALOG.items() if spec["brand"] == selected_brand]
            if not avail_models:
                avail_models = list(MODEL_CATALOG.keys())
        selected_model = st.selectbox("Chọn dòng xe muốn dự báo", avail_models, index=0)

    # Lấy thông số mặc định của model
    catalog_item = MODEL_CATALOG.get(selected_model, MODEL_CATALOG["VF 5"])
    default_price = catalog_item["default_price"]

    # Ước lượng giá cơ sở thực tế từ screened_listings nếu có
    model_listings = df_screened[df_screened["family"] == selected_model.replace(" ", "")]
    if not model_listings.empty:
        actual_median = model_listings["price_million"].median()
        if not np.isnan(actual_median) and actual_median > 0:
            default_price = actual_median

    with col_ctrl2:
        cond_choice = st.selectbox(
            "Tình trạng xe dự báo",
            ["Xe cũ (Đã sử dụng)", "Xe mới 100%"],
            index=0 if "Cũ" in condition_pref else 1
        )

    with col_ctrl3:
        input_price = st.number_input(
            "Mức giá mốc hiện tại (Triệu VNĐ)",
            min_value=50.0,
            max_value=3000.0,
            value=float(round(default_price, 1)),
            step=5.0,
            help="Bạn có thể tự điều chỉnh mức giá mốc để dự báo theo chiếc xe cụ thể bạn nhắm tới."
        )

    # Tính toán dự báo 12 tháng
    forecast_df = calculate_12m_forecast(
        base_price=input_price,
        model_name=selected_model,
        condition=cond_choice
    )
    advice = get_best_buying_advice(forecast_df, input_price, selected_model)

    # Hiển thị Biểu đồ dự báo
    fig_fc = charts.plot_price_forecast_curve(forecast_df, input_price, selected_model)
    st.plotly_chart(fig_fc, use_container_width=True)

    # Hộp Khuyến nghị Thời điểm Vàng
    badge_bg = advice["color"]
    st.markdown(f"""
    <div class="signal-card {advice['badge_type']}">
        <span class="signal-badge" style="background-color: {badge_bg};">{advice['signal']}</span>
        <div class="signal-title">Khuyến nghị thời điểm mua: {advice['best_month']}</div>
        <div class="signal-desc">{advice['summary']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Chi tiết bảng dữ liệu dự báo theo từng tháng
    with st.expander("📊 Xem bảng chi tiết giá dự phóng 12 tháng tới"):
        display_df = forecast_df[[
            "date_str", "month_name", "pred_price", "price_min", "price_max", "saving_vs_now", "season_label"
        ]].copy()
        display_df.columns = [
            "Thời điểm", "Tháng", "Giá dự kiến (tr)", "Giá tối thiểu (tr)", "Giá tối đa (tr)", "Tiết kiệm vs Hiện tại (tr)", "Đặc điểm mùa vụ"
        ]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # PHẦN 2: SMART TIMING & BUDGET MATCHER
    st.markdown("<div class='section-header'>🎯 CỐ VẤN MUA XE THEO THỜI ĐIỂM & NGÂN SÁCH</div>", unsafe_allow_html=True)
    st.markdown("Nếu bạn đã có sẵn **Ngân sách** và **Thời điểm dự định nhận xe**, hệ thống sẽ tính giá kỳ vọng của tất cả dòng xe tại thời điểm đó và gợi ý các mẫu xe phù hợp nhất:")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        target_month_offset = st.slider(
            "Bạn dự định mua xe sau bao lâu nữa?",
            min_value=1,
            max_value=12,
            value=6,
            help="Ví dụ: 3 tháng tới, 6 tháng tới hoặc 12 tháng tới."
        )
        target_date_preview = datetime.now() + pd.DateOffset(months=target_month_offset)
        st.caption(f"📅 Thời điểm nhận xe tương ứng: **Tháng {target_date_preview.month}/{target_date_preview.year}**")

    with col_m2:
        budget_input = st.slider(
            "Ngân sách tối đa của bạn (Triệu VNĐ)",
            min_value=150,
            max_value=1800,
            value=600,
            step=10,
            help="Số tiền tối đa bạn sẵn sàng chi cho chiếc xe."
        )
        st.caption(f"💵 Ngân sách: **{budget_input:,.0f} triệu VNĐ**")

    # Quét danh sách gợi ý
    matched_candidates = match_timing_and_budget(
        target_month_offset=target_month_offset,
        budget_million=budget_input,
        brand_filter=selected_brand,
        condition="Used" if "Cũ" in cond_choice else "New"
    )

    if not matched_candidates:
        st.warning("Chưa tìm thấy dòng xe phù hợp với tầm ngân sách này. Hãy thử nới rộng khoảng ngân sách!")
    else:
        st.markdown(f"**Tìm thấy {len(matched_candidates)} mẫu xe phù hợp với ngân sách {budget_input:,.0f} triệu VNĐ vào Tháng {target_date_preview.month}/{target_date_preview.year}:**")

        # Hiển thị dạng thẻ
        cols = st.columns(3)
        for idx, car in enumerate(matched_candidates):
            with cols[idx % 3]:
                badge_color = "#10b981" if car["fit_code"] == "perfect" else ("#0284c7" if car["fit_code"] == "economical" else "#f59e0b")
                st.markdown(f"""
                <div class="car-card">
                    <img src="{car['image']}" class="car-card-img" alt="{car['model']}">
                    <div class="car-card-body">
                        <span style="background:{badge_color}; color:white; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:12px;">{car['fit_status']}</span>
                        <div class="car-card-title" style="margin-top:8px;">{car['model']}</div>
                        <div class="car-card-seg">{car['brand']} • {car['segment']}</div>
                        <div class="car-card-price">~{car['future_price']:,.0f} triệu</div>
                        <div style="font-size:0.85rem; color:#64748b; margin-bottom:8px;">
                            Dự báo tại {car['target_month_name']}<br>
                            {'Dư ngân sách: <b>' + str(car['budget_diff']) + ' tr</b>' if car['budget_diff'] >= 0 else 'Cần thêm: <b>' + str(abs(car['budget_diff'])) + ' tr</b>'}
                        </div>
                        <div class="car-card-specs">
                            <span>🔋 {car['range_km']} km</span>
                            <span>💺 {car['seats']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# TAB 2: LỊCH SỬ GIÁ & KHẤU HAO
# ==============================================================================
with tab2:
    st.markdown("<div class='section-header'>📈 LỊCH SỬ BIẾN ĐỘNG GIÁ XE QUA CÁC NĂM</div>", unsafe_allow_html=True)
    st.markdown("Theo dõi hành trình điều chỉnh giá niêm yết chính hãng từ khi mở bán đến hiện tại và phân tích đường cong rớt giá thực tế trên thị trường.")

    c_hist1, c_hist2 = st.columns([2, 1])
    with c_hist1:
        bench_models = df_bench["Model"].dropna().unique().tolist()
        hist_model_choice = st.selectbox("Chọn dòng xe xem lịch sử", bench_models, index=0)

        # Biểu đồ lịch sử giá niêm yết
        fig_hist = charts.plot_historical_timeline(df_bench, hist_model_choice)
        st.plotly_chart(fig_hist, use_container_width=True)

    with c_hist2:
        st.markdown(f"**Bảng tra cứu giá niêm yết — {hist_model_choice}**")
        df_hist_sub = df_bench[df_bench["Model"] == hist_model_choice][
            ["Year", "price_with_bat_million", "price_no_bat_million", "bat_cost_million", "Notes"]
        ].sort_values("Year", ascending=False)
        df_hist_sub.columns = ["Năm", "Kèm Pin (tr)", "Thuê Pin (tr)", "Giá Pin (tr)", "Ghi chú"]
        st.dataframe(df_hist_sub, use_container_width=True, hide_index=True)

        st.info("💡 **Nhận xét chính sách pin:** VinFast có sự điều chỉnh linh hoạt chi phí pin giữa các năm. Xe kèm pin giúp người mua sở hữu trọn gói, trong khi gói thuê pin giảm đáng kể chi phí ban đầu.")

    st.markdown("---")

    # ĐƯỜNG CONG RỚT GIÁ THEO ODO
    st.markdown("<div class='section-header'>📉 TƯƠNG QUAN GIÁ BÁN & SỐ KM ĐÃ ĐI (ODO)</div>", unsafe_allow_html=True)
    st.markdown("Biểu đồ phân tán giá bán thực tế của các tin đăng xe cũ theo số km đã lăn bánh:")

    fig_odo = charts.plot_price_vs_odo(df_screened, hist_model_choice)
    st.plotly_chart(fig_odo, use_container_width=True)

    st.markdown("---")

    # BẢNG XẾP HẠNG CHỈ SỐ GIỮ GIÁ (RESALE VALUE INDEX)
    st.markdown("<div class='section-header'>🏆 CHỈ SỐ GIỮ GIÁ CÁC MẪU XE ĐIỆN (RESALE VALUE INDEX)</div>", unsafe_allow_html=True)
    st.markdown("Xếp hạng tỷ lệ giữ giá ước tính sau 1 năm và 2 năm sử dụng (dựa trên phân tích hồi quy khấu hao thị trường):")

    resale_df = get_resale_index_table()
    st.dataframe(resale_df, use_container_width=True, hide_index=True)


# ==============================================================================
# TAB 3: SHOWROOM TRỰC TUYẾN & CHI TIẾT DÒNG XE
# ==============================================================================
with tab3:
    st.markdown("<div class='section-header'>🚗 SHOWROOM DANH MỤC XE ĐIỆN THỰC TẾ</div>", unsafe_allow_html=True)
    st.markdown("Khám phá các dòng xe điện đang lưu hành trên thị trường với thông số chi tiết, dải giá giao dịch và tin rao nổi bật:")

    # Lọc phân khúc
    seg_list = ["Tất cả", "Mini SUV", "SUV Hạng A", "SUV Hạng B", "SUV Hạng C", "SUV Hạng D", "SUV Hạng E (Full-size)", "MPV 7 chỗ", "Sedan Hạng D"]
    selected_seg = st.selectbox("Lọc theo Phân khúc xe", seg_list, index=0)

    # Hiển thị lưới xe Showroom
    filtered_catalog = {
        m: spec for m, spec in MODEL_CATALOG.items()
        if (selected_seg == "Tất cả" or spec["segment"] == selected_seg) and
           (selected_brand == "Tất cả" or spec["brand"] == selected_brand)
    }

    cols_sr = st.columns(3)
    for i, (m_name, spec) in enumerate(filtered_catalog.items()):
        # Lấy giá thực tế từ screened listings nếu có
        m_listings = df_screened[df_screened["family"] == m_name.replace(" ", "")]
        if not m_listings.empty:
            p_med = m_listings["price_million"].median()
            p_min = m_listings["price_million"].min()
            p_max = m_listings["price_million"].max()
            price_str = f"{p_med:,.0f} triệu"
            range_str = f"Dải giá: {p_min:,.0f} - {p_max:,.0f} tr"
            count_str = f"{len(m_listings)} tin đang bán"
        else:
            price_str = f"~{spec['default_price']:,.0f} triệu"
            range_str = "Giá tham chiếu niêm yết"
            count_str = "Mẫu xe mới / Showroom"

        with cols_sr[i % 3]:
            st.markdown(f"""
            <div class="car-card">
                <img src="{spec['image']}" class="car-card-img" alt="{m_name}">
                <div class="car-card-body">
                    <span style="background:#e0f2fe; color:#0369a1; font-size:0.75rem; font-weight:700; padding:3px 10px; border-radius:12px;">{spec['segment']}</span>
                    <div class="car-card-title" style="margin-top:6px;">{m_name}</div>
                    <div class="car-card-seg">{spec['brand']} • {spec['target_audience']}</div>
                    <div class="car-card-price">{price_str}</div>
                    <div style="font-size:0.82rem; color:#64748b; margin-bottom:10px;">{range_str} • {count_str}</div>
                    <div class="car-card-specs">
                        <span>🔋 {spec['battery_kwh']} kWh</span>
                        <span>⚡ {spec['range_km']} km</span>
                        <span>🐎 {spec['power_hp']} hp</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # DANH SÁCH TIN ĐĂNG THAM KHẢO GIÁ TỐT (MARKET DEALS)
    st.markdown("<div class='section-header'>🔥 TIN RAO THỊ TRƯỜNG THAM KHẢO (CHỢ TỐT)</div>", unsafe_allow_html=True)
    st.markdown("Danh sách một số tin rao ô tô điện có giá tốt đang được chào bán trên sàn giao dịch:")

    if not df_chotot.empty:
        # Lọc tin hợp lệ
        valid_deals = df_chotot[
            (df_chotot["price_million"] > 50) &
            (df_chotot["price_million"] < 2500)
        ].copy()

        if selected_brand != "Tất cả":
            valid_deals = valid_deals[valid_deals["brand_name"].str.contains(selected_brand, case=False, na=False)]

        deal_sample = valid_deals[[
            "title", "brand_name", "model_name", "price_million", "condition", "region_name", "posted_at"
        ]].head(10).copy()
        deal_sample.columns = ["Tiêu đề tin rao", "Hãng", "Dòng xe", "Giá rao (Triệu VNĐ)", "Tình trạng", "Khu vực", "Ngày đăng"]

        st.dataframe(deal_sample, use_container_width=True, hide_index=True)
    else:
        st.info("Đang kết nối dữ liệu tin rao...")


# ==============================================================================
# TAB 4: SO SÁNH XE, TÍNH TCO & AI ĐỊNH GIÁ
# ==============================================================================
with tab4:
    tool_tab1, tool_tab2, tool_tab3 = st.tabs([
        "⚖️ So Sánh Trực Diện 2 Xe",
        "⚡ Tính Chi Phí Năng Lượng & TCO",
        "🎯 AI Định Giá Xe Thông Minh"
    ])

    # ──────────────────────────────────────────────────────────────────────────
    # SUB-TAB 4.1: SO SÁNH ĐỐI ĐẦU 2 MẪU XE
    with tool_tab1:
        st.markdown("### ⚖️ SO SÁNH TRỰC DIỆN 2 MẪU XE ĐIỆN")
        col_c1, col_c2 = st.columns(2)

        models_list = list(MODEL_CATALOG.keys())
        with col_c1:
            car1_name = st.selectbox("Chọn Xe Thứ Nhất (Xe A)", models_list, index=1)  # VF 5
        with col_c2:
            car2_name = st.selectbox("Chọn Xe Thứ Hai (Xe B)", models_list, index=2)  # VF 6

        spec1 = MODEL_CATALOG[car1_name]
        spec2 = MODEL_CATALOG[car2_name]

        fc1 = calculate_12m_forecast(spec1["default_price"], car1_name, "Used")
        fc2 = calculate_12m_forecast(spec2["default_price"], car2_name, "Used")

        car1_dict = {
            "name": car1_name,
            "price": spec1["default_price"],
            "future_price": fc1.iloc[-1]["pred_price"],
            "range": spec1["range_km"],
            "power": spec1["power_hp"]
        }
        car2_dict = {
            "name": car2_name,
            "price": spec2["default_price"],
            "future_price": fc2.iloc[-1]["pred_price"],
            "range": spec2["range_km"],
            "power": spec2["power_hp"]
        }

        # Biểu đồ cột so sánh
        fig_cmp = charts.plot_head_to_head_bars(car1_dict, car2_dict)
        st.plotly_chart(fig_cmp, use_container_width=True)

        # Bảng so sánh chi tiết
        cmp_df = pd.DataFrame([
            {"Tiêu chí": "Hãng sản xuất", car1_name: spec1["brand"], car2_name: spec2["brand"]},
            {"Tiêu chí": "Phân khúc", car1_name: spec1["segment"], car2_name: spec2["segment"]},
            {"Tiêu chí": "Số chỗ ngồi", car1_name: spec1["seats"], car2_name: spec2["seats"]},
            {"Tiêu chí": "Giá niêm yết mốc (triệu VNĐ)", car1_name: f"{spec1['default_price']:,.0f}", car2_name: f"{spec2['default_price']:,.0f}"},
            {"Tiêu chí": "Giá dự báo sau 1 năm (triệu VNĐ)", car1_name: f"{fc1.iloc[-1]['pred_price']:,.0f}", car2_name: f"{fc2.iloc[-1]['pred_price']:,.0f}"},
            {"Tiêu chí": "Dung lượng pin (kWh)", car1_name: f"{spec1['battery_kwh']} kWh", car2_name: f"{spec2['battery_kwh']} kWh"},
            {"Tiêu chí": "Quãng đường 1 lần sạc", car1_name: f"~{spec1['range_km']} km", car2_name: f"~{spec2['range_km']} km"},
            {"Tiêu chí": "Công suất động cơ", car1_name: f"{spec1['power_hp']} mã lực", car2_name: f"{spec2['power_hp']} mã lực"},
            {"Tiêu chí": "Mục đích tối ưu", car1_name: spec1["target_audience"], car2_name: spec2["target_audience"]}
        ])
        st.table(cmp_df.set_index("Tiêu chí"))

    # ──────────────────────────────────────────────────────────────────────────
    # SUB-TAB 4.2: TÍNH CHI PHÍ TCO (ĐIỆN VS XĂNG)
    with tool_tab2:
        st.markdown("### ⚡ DỰ TOÁN TỔNG CHI PHÍ NĂNG LƯỢNG (ĐIỆN VS XĂNG)")
        st.markdown("Nhập số km bạn dự kiến di chuyển hàng tháng để so sánh chi phí nạp điện (mua pin hoặc thuê pin) so với đổ xăng trong 1 - 3 năm:")

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            km_input = st.slider("Quãng đường di chuyển mỗi tháng (km/tháng)", 500, 5000, 1500, step=100)
            gas_price = st.number_input("Giá xăng tham chiếu (VNĐ/lít)", value=24000, step=500)

        with col_t2:
            battery_mode = st.radio("Chính sách pin xe điện quan tâm:", ["Mua đứt pin (Chỉ tốn tiền sạc)", "Thuê pin (Phí thuê + tiền sạc)"])
            elec_price = st.number_input("Giá điện sạc trung bình (VNĐ/kWh)", value=3858, step=100)

        fig_tco = charts.plot_tco_comparison(
            monthly_km=km_input,
            ev_kwh_per_100km=14.0,
            gas_l_per_100km=7.5,
            gas_price_vnd=float(gas_price),
            elec_price_vnd=float(elec_price),
            battery_rent_monthly=1200000.0
        )
        st.plotly_chart(fig_tco, use_container_width=True)

        # Tính số tiền tiết kiệm
        annual_gas = (km_input * 12 / 100.0) * 7.5 * gas_price
        annual_ev = (km_input * 12 / 100.0) * 14.0 * elec_price
        if "Thuê pin" in battery_mode:
            annual_ev += 1200000 * 12
        saving_3y = (annual_gas - annual_ev) * 3 / 1e6

        st.success(f"🎉 Với nhu cầu chạy **{km_input:,.0f} km/tháng**, việc sử dụng xe điện giúp bạn tiết kiệm khoảng **{saving_3y:,.1f} triệu VNĐ** tiền nhiên liệu sau 3 năm so với xe xăng!")

    # ──────────────────────────────────────────────────────────────────────────
    # SUB-TAB 4.3: AI ĐỊNH GIÁ XE NHANH
    with tool_tab3:
        st.markdown("### 🎯 AI ĐỊNH GIÁ XE NHANH (MACHINE LEARNING)")
        st.markdown("Nhập thông tin chiếc xe bạn định mua hoặc bán để mô hình **Random Forest Regressor** định giá khoảng tiền hợp lý:")

        col_ai1, col_ai2, col_ai3 = st.columns(3)
        with col_ai1:
            vf_families = [f for f in ["VF3", "VF5", "VF6", "VF7", "VF8", "VF9", "VFe34"] if f in model_pkg["family_price_medians"]]
            ai_family = st.selectbox("Dòng xe VinFast", vf_families, index=1)
            ai_cond = st.selectbox("Tình trạng", ["Used", "New"], format_func=lambda x: "Xe cũ (Đã qua sử dụng)" if x == "Used" else "Xe mới 100%")

        with col_ai2:
            ai_year = st.selectbox("Năm sản xuất", [2026, 2025, 2024, 2023, 2022], index=1)
            ai_odo = st.number_input("Số ODO đã lăn bánh (km)", min_value=0, max_value=200000, value=25000 if ai_cond == "Used" else 0, step=5000)

        with col_ai3:
            ai_prov = st.selectbox("Tỉnh / Thành phố đăng kiểm", all_provinces, index=0 if "Hà Nội" not in all_provinces else all_provinces.index("Hà Nội"))

        if st.button("🚀 Định giá xe ngay với AI", type="primary", use_container_width=True):
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
                <div style="background:linear-gradient(135deg, #1e293b, #0f172a); border-radius:18px; padding:28px 32px; color:white; border:2px solid #3b82f6;">
                    <div style="font-size:0.9rem; color:#94a3b8; font-weight:600; text-transform:uppercase;">Giá Thị Trường Dự Báo Của AI</div>
                    <div style="font-size:2.8rem; font-weight:800; color:#38bdf8; margin:6px 0;">{predicted_p:,.1f} triệu VNĐ</div>
                    <div style="font-size:0.95rem; color:#cbd5e1;">
                        Khoảng giá hợp lý đàm phán: <b>{predicted_p*0.96:,.0f} - {predicted_p*1.04:,.0f} triệu VNĐ</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with res_col2:
                st.metric("Trung vị thị trường dòng xe", f"{family_med:,.1f} tr", delta=f"{diff_to_med:+,.1f} tr so với giá trung bình", delta_color="inverse")
                st.caption(f"Mô hình đạt độ chính xác R² = {model_pkg.get('rf_r2', 0.97):.3f} với sai số tuyệt đối MAE ~{model_pkg.get('rf_mae', 29.3):.1f} triệu VNĐ.")
