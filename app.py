"""
app.py — VinFast EV Market Monitor · Streamlit Application
============================================================
Chạy: streamlit run app.py

Giao diện gồm 3 trang:
  1. Tổng quan thị trường   — biểu đồ EDA tương tác
  2. Ước tính giá xe        — dự đoán từ mô hình Random Forest đã huấn luyện
  3. Hiệu năng mô hình      — bảng MAE/R² và biểu đồ predicted vs. actual
"""

import sys
from pathlib import Path

# Ensure the app/ sub-package is importable
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from app.data_loader import load_screened_listings, get_families, get_provinces, get_conditions
from app.model_loader import load_model_package, predict_price
from app import charts

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VinFast EV Market Monitor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0f172a 0%, #1e293b 100%);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label { color: #94a3b8 !important; }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
    }
    [data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 700; }

    /* Hero header */
    .hero-header {
        background: linear-gradient(135deg, #1e40af 0%, #0ea5e9 50%, #10b981 100%);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        color: white;
    }
    .hero-header h1 { color: white; margin: 0; font-size: 2rem; font-weight: 700; }
    .hero-header p  { color: rgba(255,255,255,0.85); margin: 6px 0 0; font-size: 1rem; }

    /* Section dividers */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        border-left: 4px solid #3b82f6;
        padding-left: 10px;
        margin: 24px 0 12px;
    }

    /* Prediction result card */
    .pred-card {
        border-radius: 16px;
        padding: 24px 30px;
        text-align: center;
    }
    .pred-card.cheap  { background: linear-gradient(135deg, #d1fae5, #a7f3d0); border: 2px solid #10b981; }
    .pred-card.fair   { background: linear-gradient(135deg, #dbeafe, #bfdbfe); border: 2px solid #3b82f6; }
    .pred-card.pricey { background: linear-gradient(135deg, #fee2e2, #fecaca); border: 2px solid #ef4444; }
    .pred-card h2 { font-size: 2.4rem; font-weight: 700; margin: 8px 0; color: #0f172a; }
    .pred-card p  { font-size: 1rem; color: #334155; margin: 4px 0; }

    /* Warning box */
    .limitation-box {
        background: #fffbeb;
        border: 1px solid #fcd34d;
        border-radius: 10px;
        padding: 14px 18px;
        font-size: 0.85rem;
        color: #78350f;
        margin-top: 16px;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Load data & model ────────────────────────────────────────────────────────
df = load_screened_listings()
model_pkg = load_model_package()

families   = get_families(df)
provinces  = get_provinces(df)
conditions = get_conditions()

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div style='text-align:center; padding: 16px 0 8px;'>"
        "<span style='font-size:2.4rem'>⚡</span>"
        "<div style='font-size:1.1rem; font-weight:700; margin-top:6px;'>VinFast EV Monitor</div>"
        "<div style='font-size:0.78rem; color:#94a3b8;'>Chợ Tốt · Dữ liệu xe điện</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    page = st.radio(
        "📑 Chọn trang",
        ["🏠 Tổng quan thị trường", "🔮 Ước tính giá xe", "📈 Hiệu năng mô hình"],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown(
        "<div class='limitation-box'>"
        "<strong>⚠️ Lưu ý dữ liệu & hạn chế</strong><br><br>"
        "• Giá <em>niêm yết</em> (asking price), không phải giá giao dịch thực tế.<br>"
        "• Nguồn: mẫu tin đăng Chợ Tốt — không đại diện toàn thị trường.<br>"
        "• Số km bị thiếu ở ~67% tin (chủ yếu xe mới).<br>"
        "• Mô hình học từ snapshot tĩnh; giá thị trường biến động theo thời gian."
        "</div>",
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 · Tổng quan thị trường
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Tổng quan thị trường":

    st.markdown(
        "<div class='hero-header'>"
        "<h1>⚡ Tổng quan thị trường xe điện VinFast</h1>"
        "<p>Phân tích dữ liệu tin đăng từ Chợ Tốt — dữ liệu đã qua kiểm duyệt</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Bộ lọc toàn cục ──────────────────────────────────────────────────────
    col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
    with col_f1:
        sel_families = st.multiselect(
            "Lọc theo dòng xe",
            options=families,
            default=families,
            help="Chọn một hoặc nhiều dòng xe để lọc tất cả biểu đồ",
        )
    with col_f2:
        sel_cond = st.multiselect(
            "Lọc theo tình trạng",
            options=conditions,
            default=conditions,
        )
    with col_f3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"Tổng: **{len(df):,}** tin hợp lệ")

    filtered = df[df["family"].isin(sel_families) & df["condition"].isin(sel_cond)]

    if filtered.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc đã chọn.")
        st.stop()

    # ── KPI cards ─────────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Chỉ số tổng hợp</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📋 Tổng tin đăng", f"{len(filtered):,}")
    m2.metric("💰 Giá trung vị", f"{filtered['price_million'].median():.0f} tr. VNĐ")
    m3.metric("🚗 Số dòng xe", filtered["family"].nunique())
    m4.metric(
        "🆕 Tỷ lệ xe mới",
        f"{(filtered['condition']=='New').mean()*100:.0f}%",
    )

    # ── Charts row 1 ──────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Phân bố tin đăng & Giá</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.chart_listing_count(filtered), use_container_width=True)
    with c2:
        st.plotly_chart(charts.chart_price_distribution(filtered), use_container_width=True)

    # ── Charts row 2 ──────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Giá theo dòng xe & Tình trạng</div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(charts.chart_price_by_family(filtered), use_container_width=True)
    with c4:
        st.plotly_chart(charts.chart_new_vs_used(filtered), use_container_width=True)

    # ── Data table ────────────────────────────────────────────────────────────
    with st.expander("🔍 Xem dữ liệu thô (đã lọc)"):
        display_cols = ["family", "condition", "year", "odo_km", "province", "price_million"]
        st.dataframe(
            filtered[display_cols]
            .rename(columns={
                "family": "Dòng xe", "condition": "Tình trạng",
                "year": "Năm SX", "odo_km": "Số km",
                "province": "Tỉnh/Thành", "price_million": "Giá (triệu VNĐ)",
            })
            .sort_values("Giá (triệu VNĐ)", ascending=False)
            .reset_index(drop=True),
            use_container_width=True,
            height=300,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 · Ước tính giá xe
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔮 Ước tính giá xe":

    st.markdown(
        "<div class='hero-header'>"
        "<h1>🔮 Ước tính giá xe VinFast</h1>"
        "<p>Nhập thông tin xe bên dưới để xem mức giá dự đoán từ mô hình học máy</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # ── Input form ────────────────────────────────────────────────────────────
    with st.form("price_estimator_form", border=True):
        st.markdown("<div class='section-title'>Thông tin xe cần ước tính</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            inp_family = st.selectbox(
                "🚗 Dòng xe",
                options=families,
                help="Chọn dòng xe VinFast",
            )
            inp_condition = st.selectbox(
                "🔧 Tình trạng",
                options=conditions,
                format_func=lambda x: "Xe mới" if x == "New" else "Xe cũ / đã qua sử dụng",
            )
            inp_year = st.selectbox(
                "📅 Năm sản xuất",
                options=list(range(2026, 2020, -1)),
                help="Năm sản xuất của xe",
            )

        with col2:
            inp_province = st.selectbox(
                "📍 Tỉnh / Thành phố",
                options=provinces,
                index=provinces.index("Ho Chi Minh City") if "Ho Chi Minh City" in provinces else 0,
            )
            odo_disabled = (inp_condition == "New")
            inp_odo = st.number_input(
                "🛣️ Số km đã đi",
                min_value=0,
                max_value=500_000,
                value=0,
                step=1000,
                disabled=odo_disabled,
                help="Để trống (= 0) nếu xe mới. Xe cũ: để trống sẽ dùng giá trị trung vị theo dòng xe.",
            )

        submitted = st.form_submit_button(
            "⚡ Ước tính giá ngay", use_container_width=True, type="primary"
        )

    if submitted:
        odo_val = float(inp_odo) if not odo_disabled else np.nan
        predicted, family_median = predict_price(
            model_pkg,
            family=inp_family,
            condition=inp_condition,
            year=int(inp_year),
            odo_km=odo_val,
            province=inp_province,
        )

        # Tính độ lệch so với trung vị dòng xe
        diff_pct = (predicted - family_median) / family_median * 100

        # Phán xét
        if diff_pct < -10:
            verdict = "cheap"
            verdict_icon = "✅"
            verdict_text = "Rẻ hơn mức trung bình"
            verdict_sub  = f"Thấp hơn {abs(diff_pct):.1f}% so với trung vị dòng {inp_family}"
        elif diff_pct > 10:
            verdict = "pricey"
            verdict_icon = "⚠️"
            verdict_text = "Đắt hơn mức trung bình"
            verdict_sub  = f"Cao hơn {diff_pct:.1f}% so với trung vị dòng {inp_family}"
        else:
            verdict = "fair"
            verdict_icon = "ℹ️"
            verdict_text = "Giá tương đương thị trường"
            verdict_sub  = f"Chênh lệch {diff_pct:+.1f}% so với trung vị dòng {inp_family}"

        # ── Kết quả ──────────────────────────────────────────────────────────
        st.markdown("<div class='section-title'>Kết quả dự đoán</div>", unsafe_allow_html=True)

        r1, r2, r3 = st.columns([2, 1, 1])
        with r1:
            st.markdown(
                f"<div class='pred-card {verdict}'>"
                f"<p>{verdict_icon} <strong>{verdict_text}</strong></p>"
                f"<h2>{predicted:,.0f} tr.</h2>"
                f"<p style='font-size:0.85rem'>triệu VNĐ</p>"
                f"<p style='margin-top:8px; font-size:0.82rem; color:#475569;'>{verdict_sub}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with r2:
            st.metric("Trung vị dòng xe", f"{family_median:,.0f} tr.")
        with r3:
            sign = "+" if diff_pct >= 0 else ""
            st.metric("Chênh lệch so với trung vị", f"{sign}{diff_pct:.1f}%")

        # ── Thông tin tóm tắt ─────────────────────────────────────────────────
        st.markdown("<div class='section-title'>Thông tin đầu vào đã dùng</div>", unsafe_allow_html=True)
        summary = pd.DataFrame({
            "Thông số": ["Dòng xe", "Tình trạng", "Năm SX", "Số km", "Tỉnh/Thành"],
            "Giá trị": [
                inp_family,
                "Xe mới" if inp_condition == "New" else "Xe cũ",
                str(inp_year),
                f"{int(inp_odo):,} km" if not odo_disabled else "0 km (xe mới)",
                inp_province,
            ],
        })
        st.table(summary.set_index("Thông số"))

        # Phân phối giá dòng xe này
        family_prices = df[df["family"] == inp_family]["price_million"].dropna()
        if len(family_prices) > 0:
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Histogram(
                x=family_prices, nbinsx=20,
                marker_color="#3b82f6", opacity=0.75, name="Phân phối giá",
            ))
            fig_dist.add_vline(
                x=predicted, line_dash="solid", line_color="#10b981",
                annotation_text=f"Dự đoán: {predicted:.0f} tr.",
                annotation_position="top right",
            )
            fig_dist.add_vline(
                x=family_median, line_dash="dash", line_color="#f59e0b",
                annotation_text=f"Trung vị: {family_median:.0f} tr.",
                annotation_position="top left",
            )
            fig_dist.update_layout(
                title=f"Phân phối giá dòng {inp_family} trong tập dữ liệu",
                xaxis_title="Giá (triệu VNĐ)", yaxis_title="Số tin",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(248,250,252,0.8)",
                font=dict(family="Inter, sans-serif"),
                showlegend=False,
                height=320,
            )
            st.plotly_chart(fig_dist, use_container_width=True)

    # Disclaimer nhỏ
    st.markdown(
        "<div class='limitation-box'>"
        "⚠️ <strong>Lưu ý:</strong> Đây là ước tính từ mô hình học máy dựa trên giá niêm yết trên Chợ Tốt. "
        "Giá thực tế có thể khác đáng kể do đàm phán, tình trạng xe, phụ kiện và biến động thị trường."
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 · Hiệu năng mô hình
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Hiệu năng mô hình":

    st.markdown(
        "<div class='hero-header'>"
        "<h1>📈 Hiệu năng mô hình dự đoán giá</h1>"
        "<p>So sánh Baseline · Linear Regression · Random Forest — minh bạch về độ chính xác</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    metrics = model_pkg["metrics"]
    best_name = model_pkg["best_model_name"]

    # ── KPI metrics ───────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Chỉ số đánh giá — Tập kiểm định (20%)</div>", unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)
    with k1:
        st.metric(
            "Baseline · MAE",
            f"{metrics['baseline']['mae']:.1f} tr.",
            help="Dự đoán bằng trung vị giá dòng xe",
        )
        st.metric("Baseline · R²", f"{metrics['baseline']['r2']:.3f}")
    with k2:
        st.metric(
            "Linear Regression · MAE",
            f"{metrics['linear_regression']['mae']:.1f} tr.",
            delta=f"{metrics['linear_regression']['mae'] - metrics['baseline']['mae']:+.1f} vs. Baseline",
            delta_color="inverse",
        )
        st.metric(
            "Linear Regression · R²",
            f"{metrics['linear_regression']['r2']:.3f}",
            delta=f"{metrics['linear_regression']['r2'] - metrics['baseline']['r2']:+.3f}",
        )
    with k3:
        st.metric(
            "Random Forest · MAE",
            f"{metrics['random_forest']['mae']:.1f} tr.",
            delta=f"{metrics['random_forest']['mae'] - metrics['baseline']['mae']:+.1f} vs. Baseline",
            delta_color="inverse",
        )
        st.metric(
            "Random Forest · R²",
            f"{metrics['random_forest']['r2']:.3f}",
            delta=f"{metrics['random_forest']['r2'] - metrics['baseline']['r2']:+.3f}",
        )

    # ── Metrics bar chart ─────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Biểu đồ so sánh</div>", unsafe_allow_html=True)
    st.plotly_chart(charts.chart_metrics_bars(metrics), use_container_width=True)

    # ── Pred vs Actual scatter ────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Biểu đồ dự đoán vs. thực tế — Mô hình tốt nhất</div>", unsafe_allow_html=True)

    # Let user pick which model to show
    model_choice = st.selectbox(
        "Chọn mô hình để hiển thị",
        options=["Random Forest", "Linear Regression", "Baseline"],
        index=0,
    )
    choice_map = {
        "Random Forest":      ("y_pred_rf",       metrics["random_forest"]),
        "Linear Regression":  ("y_pred_lr",        metrics["linear_regression"]),
        "Baseline":           ("y_pred_baseline",  metrics["baseline"]),
    }
    pred_key, chosen_metrics = choice_map[model_choice]
    y_test = model_pkg["y_test"]
    y_pred = model_pkg[pred_key]

    fig_scatter = charts.chart_pred_vs_actual(
        y_test, y_pred,
        model_name=model_choice,
        mae=chosen_metrics["mae"],
        r2=chosen_metrics["r2"],
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # ── Metrics table ─────────────────────────────────────────────────────────
    st.markdown("<div class='section-title'>Bảng kết quả đầy đủ</div>", unsafe_allow_html=True)
    results_table = pd.DataFrame([
        {"Mô hình": "Baseline (Median/Family)",
         "MAE (triệu VNĐ)": f"{metrics['baseline']['mae']:.2f}",
         "R²": f"{metrics['baseline']['r2']:.4f}",
         "Ghi chú": "Ngưỡng tham chiếu đơn giản"},
        {"Mô hình": "Linear Regression",
         "MAE (triệu VNĐ)": f"{metrics['linear_regression']['mae']:.2f}",
         "R²": f"{metrics['linear_regression']['r2']:.4f}",
         "Ghi chú": "OneHot encoding, hồi quy tuyến tính"},
        {"Mô hình": "Random Forest ⭐",
         "MAE (triệu VNĐ)": f"{metrics['random_forest']['mae']:.2f}",
         "R²": f"{metrics['random_forest']['r2']:.4f}",
         "Ghi chú": f"200 cây, depth=10 — {'🏆 Mô hình tốt nhất' if best_name == 'Random Forest' else ''}"},
    ])
    st.dataframe(results_table.set_index("Mô hình"), use_container_width=True)

    # ── Interpretation note ───────────────────────────────────────────────────
    st.markdown(
        "<div class='limitation-box'>"
        "<strong>📝 Cách đọc kết quả:</strong><br>"
        "• <strong>MAE</strong> (Mean Absolute Error): Trung bình sai số tuyệt đối — mô hình dự đoán lệch bao nhiêu triệu VNĐ so với giá niêm yết thực tế.<br>"
        "• <strong>R²</strong>: Hệ số xác định — tỷ lệ phương sai giá được giải thích bởi mô hình (1.0 = hoàn hảo, 0 = không tốt hơn dự đoán bằng trung bình).<br>"
        "• Mô hình được đánh giá trên <strong>tập kiểm định độc lập</strong> (20% dữ liệu, không tham gia huấn luyện)."
        "</div>",
        unsafe_allow_html=True,
    )
