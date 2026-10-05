"""
app/charts.py
-------------
Các hàm khởi tạo biểu đồ Plotly tương tác cho ứng dụng:
1. plot_price_forecast_curve(): Đường giá dự báo 12 tháng kèm dải tin cậy và điểm chạm đáy.
2. plot_historical_timeline(): Lịch sử giá niêm yết qua các năm (Kèm pin vs Thuê pin).
3. plot_price_vs_odo(): Tương quan Giá rao bán vs Số km ODO thực tế.
4. plot_head_to_head_bars(): So sánh trực quan đối đầu giữa 2 mẫu xe.
5. plot_tco_comparison(): Biểu đồ chi phí vận hành xe điện vs xe xăng trong 1 - 3 năm.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def _apply_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """Áp dụng theme hiện đại, tinh tế cho biểu đồ Plotly."""
    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=16, family=FONT_FAMILY, color="#0f172a"),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 250, 252, 0.7)",
        font=dict(family=FONT_FAMILY, color="#334155"),
        margin=dict(t=50, b=40, l=45, r=25),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="#e2e8f0",
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color="white"
        )
    )
    fig.update_xaxes(
        gridcolor="#e2e8f0",
        zerolinecolor="#cbd5e1",
        showline=True,
        linecolor="#cbd5e1"
    )
    fig.update_yaxes(
        gridcolor="#e2e8f0",
        zerolinecolor="#cbd5e1",
        showline=True,
        linecolor="#cbd5e1"
    )
    return fig


def plot_price_forecast_curve(
    forecast_df: pd.DataFrame,
    current_price: float,
    model_name: str
) -> go.Figure:
    """Biểu đồ dự phóng giá 12 tháng tới kèm dải tin cậy 90%."""
    fig = go.Figure()

    # Dải tin cậy trên và dưới (Shaded Area)
    fig.add_trace(go.Scatter(
        x=forecast_df["date_str"],
        y=forecast_df["price_max"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df["date_str"],
        y=forecast_df["price_min"],
        mode="lines",
        line=dict(width=0),
        fill="tonexty",
        fillcolor="rgba(59, 130, 246, 0.12)",
        name="Dải tin cậy 90%",
        hoverinfo="skip"
    ))

    # Đường giá dự báo chính
    fig.add_trace(go.Scatter(
        x=forecast_df["date_str"],
        y=forecast_df["pred_price"],
        mode="lines+markers",
        line=dict(color="#2563eb", width=3.5),
        marker=dict(size=7, color="#1d4ed8"),
        name="Giá dự báo trung bình",
        hovertemplate="<b>%{x}</b><br>Giá dự báo: <b>%{y:,.1f} triệu VNĐ</b><extra></extra>"
    ))

    # Điểm chạm đáy (Thời điểm vàng để mua)
    best_row = forecast_df[forecast_df["is_best_time"]].iloc[0]
    fig.add_trace(go.Scatter(
        x=[best_row["date_str"]],
        y=[best_row["pred_price"]],
        mode="markers+text",
        marker=dict(size=14, color="#10b981", symbol="star", line=dict(color="#047857", width=2)),
        text=["🌟 Đáy giá"],
        textposition="bottom center",
        textfont=dict(color="#047857", size=12, family=FONT_FAMILY),
        name="Thời điểm mua tốt nhất",
        hovertemplate="<b>THỜI ĐIỂM VÀNG (%{x})</b><br>Giá đáy: <b>%{y:,.1f} triệu VNĐ</b><br>Tiết kiệm: <b>" + f"{best_row['saving_vs_now']:,.1f} tr</b><extra></extra>"
    ))

    # Đường tham chiếu giá hiện tại
    fig.add_hline(
        y=current_price,
        line_dash="dot",
        line_color="#94a3b8",
        line_width=1.5,
        annotation_text=f"Hiện tại: {current_price:,.0f} tr",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#64748b")
    )

    _apply_theme(fig, f"Dự báo Xu hướng Giá 12 Tháng Tới — {model_name}")
    fig.update_xaxes(title="Tháng dự báo")
    fig.update_yaxes(title="Giá xe (Triệu VNĐ)")
    return fig


def plot_historical_timeline(bench_df: pd.DataFrame, selected_model: str) -> go.Figure:
    """Biểu đồ lịch sử giá niêm yết qua các năm (Kèm pin vs Thuê pin)."""
    fig = go.Figure()

    df_sub = bench_df[bench_df["Model"] == selected_model].sort_values("Year")
    if df_sub.empty:
        return fig

    # Đường giá kèm pin
    fig.add_trace(go.Scatter(
        x=df_sub["Year"],
        y=df_sub["price_with_bat_million"],
        mode="lines+markers+text",
        line=dict(color="#059669", width=3),
        marker=dict(size=9, color="#047857"),
        text=[f"{v:,.0f} tr" for v in df_sub["price_with_bat_million"]],
        textposition="top center",
        name="Giá Kèm Pin",
        hovertemplate="Năm: %{x}<br>Kèm Pin: <b>%{y:,.0f} triệu</b><extra></extra>"
    ))

    # Đường giá thuê pin
    fig.add_trace(go.Scatter(
        x=df_sub["Year"],
        y=df_sub["price_no_bat_million"],
        mode="lines+markers+text",
        line=dict(color="#d97706", width=3, dash="dash"),
        marker=dict(size=9, color="#b45309"),
        text=[f"{v:,.0f} tr" for v in df_sub["price_no_bat_million"]],
        textposition="bottom center",
        name="Giá Thuê Pin (Không pin)",
        hovertemplate="Năm: %{x}<br>Thuê Pin: <b>%{y:,.0f} triệu</b><extra></extra>"
    ))

    _apply_theme(fig, f"Lịch sử Biến động Giá Niêm yết Chính hãng — {selected_model}")
    fig.update_xaxes(title="Năm sản xuất / Mở bán", dtick=1)
    fig.update_yaxes(title="Giá niêm yết (Triệu VNĐ)")
    return fig


def plot_price_vs_odo(df_listings: pd.DataFrame, model_name: str) -> go.Figure:
    """Biểu đồ phân tán ODO vs Giá chào bán thực tế trên thị trường."""
    fig = go.Figure()
    if df_listings.empty or "odo_km" not in df_listings.columns:
        return fig

    df_used = df_listings[
        (df_listings["condition"] == "Used") &
        (df_listings["odo_km"] > 0) &
        (df_listings["odo_km"] < 150000)
    ].copy()

    if df_used.empty:
        return fig

    fig.add_trace(go.Scatter(
        x=df_used["odo_km"],
        y=df_used["price_million"],
        mode="markers",
        marker=dict(
            size=8,
            color="#3b82f6",
            opacity=0.65,
            line=dict(color="#1d4ed8", width=1)
        ),
        name="Tin rao thực tế",
        hovertemplate="ODO: <b>%{x:,.0f} km</b><br>Giá: <b>%{y:,.0f} tr</b><extra></extra>"
    ))

    # Đường hồi quy xu hướng
    try:
        m, b = np.polyfit(df_used["odo_km"], df_used["price_million"], 1)
        x_trend = np.linspace(df_used["odo_km"].min(), df_used["odo_km"].max(), 50)
        y_trend = m * x_trend + b
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=y_trend,
            mode="lines",
            line=dict(color="#ef4444", width=2.5, dash="dot"),
            name="Đường trượt giá theo ODO",
            hoverinfo="skip"
        ))
    except Exception:
        pass

    _apply_theme(fig, f"Tương quan Số Km Đã Đi (ODO) và Giá Rao Bán — {model_name}")
    fig.update_xaxes(title="Số km đã lăn bánh (ODO)", tickformat=",.0f")
    fig.update_yaxes(title="Giá chào bán (Triệu VNĐ)")
    return fig


def plot_head_to_head_bars(car1: dict, car2: dict) -> go.Figure:
    """So sánh trực quan hai dòng xe trên nhiều chỉ số."""
    categories = ["Giá hiện tại (tr)", "Giá dự báo 1 năm (tr)", "Tầm vận hành (km)", "Công suất (hp)"]
    v1 = [car1["price"], car1["future_price"], car1["range"], car1["power"]]
    v2 = [car2["price"], car2["future_price"], car2["range"], car2["power"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=v1,
        name=car1["name"],
        marker_color="#2563eb",
        text=[f"{x:,.0f}" for x in v1],
        textposition="outside"
    ))
    fig.add_trace(go.Bar(
        x=categories,
        y=v2,
        name=car2["name"],
        marker_color="#10b981",
        text=[f"{x:,.0f}" for x in v2],
        textposition="outside"
    ))

    fig.update_layout(barmode="group")
    _apply_theme(fig, f"So Sánh Trực Diện: {car1['name']} vs {car2['name']}")
    fig.update_yaxes(title="Giá trị tương đối")
    return fig


def plot_tco_comparison(
    monthly_km: int,
    ev_kwh_per_100km: float = 14.0,
    gas_l_per_100km: float = 7.5,
    gas_price_vnd: float = 24000.0,
    elec_price_vnd: float = 3858.0,
    battery_rent_monthly: float = 1200000.0
) -> go.Figure:
    """So sánh tổng chi phí năng lượng tích lũy sau 1 năm và 3 năm."""
    # Chi phí xe xăng / năm
    annual_gas = (monthly_km * 12 / 100.0) * gas_l_per_100km * gas_price_vnd / 1e6
    # Chi phí điện (mua đứt pin) / năm
    annual_ev_bought = (monthly_km * 12 / 100.0) * ev_kwh_per_100km * elec_price_vnd / 1e6
    # Chi phí điện (thuê pin) / năm = tiền sạc + tiền thuê pin
    annual_ev_rent = annual_ev_bought + (battery_rent_monthly * 12 / 1e6)

    periods = ["1 Năm", "2 Năm", "3 Năm"]
    gas_totals = [round(annual_gas * i, 1) for i in [1, 2, 3]]
    ev_bought_totals = [round(annual_ev_bought * i, 1) for i in [1, 2, 3]]
    ev_rent_totals = [round(annual_ev_rent * i, 1) for i in [1, 2, 3]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=periods,
        y=gas_totals,
        name="Xe Xăng cùng phân khúc",
        marker_color="#ef4444",
        text=[f"{v:,.1f} tr" for v in gas_totals],
        textposition="outside"
    ))
    fig.add_trace(go.Bar(
        x=periods,
        y=ev_rent_totals,
        name="Xe Điện (Thuê Pin)",
        marker_color="#f59e0b",
        text=[f"{v:,.1f} tr" for v in ev_rent_totals],
        textposition="outside"
    ))
    fig.add_trace(go.Bar(
        x=periods,
        y=ev_bought_totals,
        name="Xe Điện (Mua Pin)",
        marker_color="#10b981",
        text=[f"{v:,.1f} tr" for v in ev_bought_totals],
        textposition="outside"
    ))

    fig.update_layout(barmode="group")
    _apply_theme(fig, f"Dự Toán Chi Phí Năng Lượng Tích Lũy (Chạy {monthly_km:,.0f} km/tháng)")
    fig.update_yaxes(title="Tổng chi phí nhiên liệu (Triệu VNĐ)")
    return fig
