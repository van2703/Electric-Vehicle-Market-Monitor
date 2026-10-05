"""
app/charts.py
-------------
Khởi tạo biểu đồ Plotly tương tác, hỗ trợ Dark/Light theme và đa ngôn ngữ:
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

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"


def _apply_theme(fig: go.Figure, title: str = "", theme: str = "light") -> go.Figure:
    """Áp dụng theme Light hoặc Dark hiện đại, tối giản, chuyên nghiệp."""
    is_dark = (theme.lower() == "dark")

    title_color = "#f8fafc" if is_dark else "#0f172a"
    font_color = "#94a3b8" if is_dark else "#475569"
    plot_bg = "rgba(15, 23, 42, 0.5)" if is_dark else "rgba(248, 250, 252, 0.85)"
    grid_color = "#1e293b" if is_dark else "#e2e8f0"
    zero_color = "#334155" if is_dark else "#cbd5e1"
    border_color = "#334155" if is_dark else "#e2e8f0"
    legend_bg = "rgba(15, 23, 42, 0.85)" if is_dark else "rgba(255, 255, 255, 0.85)"

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>" if title else "",
            font=dict(size=14, family=FONT_FAMILY, color=title_color),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=plot_bg,
        font=dict(family=FONT_FAMILY, color=font_color, size=12),
        margin=dict(t=45, b=35, l=45, r=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor=legend_bg,
            bordercolor=border_color,
            borderwidth=1,
            font=dict(size=11, color=font_color)
        ),
        hoverlabel=dict(
            bgcolor="#0f172a" if not is_dark else "#1e293b",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color="white"
        )
    )
    fig.update_xaxes(
        gridcolor=grid_color,
        zerolinecolor=zero_color,
        showline=True,
        linecolor=zero_color
    )
    fig.update_yaxes(
        gridcolor=grid_color,
        zerolinecolor=zero_color,
        showline=True,
        linecolor=zero_color
    )
    return fig


def plot_price_forecast_curve(
    forecast_df: pd.DataFrame,
    current_price: float,
    model_name: str,
    theme: str = "light",
    lang: str = "vi"
) -> go.Figure:
    """Đường giá dự phóng 12 tháng kèm dải tin cậy 90%."""
    fig = go.Figure()
    is_dark = (theme.lower() == "dark")

    # Dải tin cậy
    fill_col = "rgba(56, 189, 248, 0.12)" if is_dark else "rgba(37, 99, 235, 0.10)"
    ci_label = "90% Confidence Band" if lang == "en" else "Dải tin cậy 90%"
    line_label = "Forecast Median" if lang == "en" else "Giá dự báo trung bình"
    best_label = "Lowest Point" if lang == "en" else "Điểm chạm đáy"
    curr_label = "Current" if lang == "en" else "Hiện tại"
    title_text = f"12-Month Price Forecast — {model_name}" if lang == "en" else f"Dự báo Giá 12 Tháng — {model_name}"
    x_title = "Forecast Period" if lang == "en" else "Thời điểm"
    y_title = "Price (Million VND)" if lang == "en" else "Giá xe (Triệu VNĐ)"

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
        fillcolor=fill_col,
        name=ci_label,
        hoverinfo="skip"
    ))

    # Đường giá chính
    line_col = "#38bdf8" if is_dark else "#2563eb"
    fig.add_trace(go.Scatter(
        x=forecast_df["date_str"],
        y=forecast_df["pred_price"],
        mode="lines+markers",
        line=dict(color=line_col, width=2.5),
        marker=dict(size=6, color=line_col),
        name=line_label,
        hovertemplate="<b>%{x}</b><br>" + f"{line_label}: <b>" + "%{y:,.1f} tr</b><extra></extra>"
    ))

    # Điểm đáy
    best_row = forecast_df[forecast_df["is_best_time"]].iloc[0]
    fig.add_trace(go.Scatter(
        x=[best_row["date_str"]],
        y=[best_row["pred_price"]],
        mode="markers+text",
        marker=dict(size=10, color="#10b981", symbol="circle", line=dict(color="#047857", width=2)),
        text=[f"[{best_label}]"],
        textposition="bottom center",
        textfont=dict(color="#10b981", size=11, family=FONT_FAMILY),
        name=best_label,
        hovertemplate="<b>%{x}</b><br>" + f"{best_label}: <b>" + "%{y:,.1f} tr</b><extra></extra>"
    ))

    # Đường tham chiếu mốc hiện tại
    fig.add_hline(
        y=current_price,
        line_dash="dot",
        line_color="#64748b" if is_dark else "#94a3b8",
        line_width=1.2,
        annotation_text=f"{curr_label}: {current_price:,.0f} tr",
        annotation_position="top left",
        annotation_font=dict(size=10, color="#94a3b8" if is_dark else "#64748b")
    )

    _apply_theme(fig, title_text, theme=theme)
    fig.update_xaxes(title=dict(text=x_title, font=dict(size=11)))
    fig.update_yaxes(title=dict(text=y_title, font=dict(size=11)))
    return fig


def plot_historical_timeline(bench_df: pd.DataFrame, selected_model: str, theme: str = "light", lang: str = "vi") -> go.Figure:
    """Lịch sử giá niêm yết qua các năm."""
    fig = go.Figure()

    df_sub = bench_df[bench_df["Model"] == selected_model].sort_values("Year")
    if df_sub.empty:
        return fig

    lbl_battery = "With Battery" if lang == "en" else "Kèm Pin"
    lbl_nobat = "Battery Subscription (No Battery)" if lang == "en" else "Thuê Pin (Không pin)"
    title_text = f"MSRP Timeline — {selected_model}" if lang == "en" else f"Lịch sử Giá Niêm yết — {selected_model}"
    x_title = "Model Year" if lang == "en" else "Năm sản xuất / Mở bán"
    y_title = "List Price (Million VND)" if lang == "en" else "Giá niêm yết (Triệu VNĐ)"

    fig.add_trace(go.Scatter(
        x=df_sub["Year"],
        y=df_sub["price_with_bat_million"],
        mode="lines+markers+text",
        line=dict(color="#10b981", width=2.5),
        marker=dict(size=7, color="#059669"),
        text=[f"{v:,.0f}" for v in df_sub["price_with_bat_million"]],
        textposition="top center",
        name=lbl_battery,
        hovertemplate="Year: %{x}<br>" + f"{lbl_battery}: <b>" + "%{y:,.0f} tr</b><extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=df_sub["Year"],
        y=df_sub["price_no_bat_million"],
        mode="lines+markers+text",
        line=dict(color="#f59e0b", width=2.5, dash="dash"),
        marker=dict(size=7, color="#d97706"),
        text=[f"{v:,.0f}" for v in df_sub["price_no_bat_million"]],
        textposition="bottom center",
        name=lbl_nobat,
        hovertemplate="Year: %{x}<br>" + f"{lbl_nobat}: <b>" + "%{y:,.0f} tr</b><extra></extra>"
    ))

    _apply_theme(fig, title_text, theme=theme)
    fig.update_xaxes(title=dict(text=x_title, font=dict(size=11)), dtick=1)
    fig.update_yaxes(title=dict(text=y_title, font=dict(size=11)))
    return fig


def plot_price_vs_odo(df_listings: pd.DataFrame, model_name: str, theme: str = "light", lang: str = "vi") -> go.Figure:
    """Tương quan ODO vs Giá chào bán thực tế."""
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

    lbl_data = "Market Listings" if lang == "en" else "Tin rao thực tế"
    lbl_trend = "Depreciation Trendline" if lang == "en" else "Đường xu hướng trượt giá"
    title_text = f"Asking Price vs. Mileage — {model_name}" if lang == "en" else f"Tương quan Số Km ODO & Giá Rao — {model_name}"
    x_title = "Mileage (km)" if lang == "en" else "Số km đã lăn bánh (ODO)"
    y_title = "Price (Million VND)" if lang == "en" else "Giá rao bán (Triệu VNĐ)"

    fig.add_trace(go.Scatter(
        x=df_used["odo_km"],
        y=df_used["price_million"],
        mode="markers",
        marker=dict(
            size=6,
            color="#38bdf8" if theme.lower() == "dark" else "#2563eb",
            opacity=0.6
        ),
        name=lbl_data,
        hovertemplate="ODO: <b>%{x:,.0f} km</b><br>Price: <b>%{y:,.0f} tr</b><extra></extra>"
    ))

    try:
        m, b = np.polyfit(df_used["odo_km"], df_used["price_million"], 1)
        x_trend = np.linspace(df_used["odo_km"].min(), df_used["odo_km"].max(), 50)
        y_trend = m * x_trend + b
        fig.add_trace(go.Scatter(
            x=x_trend,
            y=y_trend,
            mode="lines",
            line=dict(color="#f43f5e", width=2, dash="dot"),
            name=lbl_trend,
            hoverinfo="skip"
        ))
    except Exception:
        pass

    _apply_theme(fig, title_text, theme=theme)
    fig.update_xaxes(title=dict(text=x_title, font=dict(size=11)), tickformat=",.0f")
    fig.update_yaxes(title=dict(text=y_title, font=dict(size=11)))
    return fig


def plot_head_to_head_bars(car1: dict, car2: dict, theme: str = "light", lang: str = "vi") -> go.Figure:
    """So sánh trực quan hai dòng xe trên nhiều chỉ số."""
    if lang == "en":
        categories = ["Current Price (M)", "1Y Forecast (M)", "Range (km)", "Power (hp)"]
    else:
        categories = ["Giá hiện tại (tr)", "Giá dự báo 1 năm (tr)", "Tầm vận hành (km)", "Công suất (hp)"]

    v1 = [car1["price"], car1["future_price"], car1["range"], car1["power"]]
    v2 = [car2["price"], car2["future_price"], car2["range"], car2["power"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=categories,
        y=v1,
        name=car1["name"],
        marker_color="#2563eb" if theme.lower() != "dark" else "#38bdf8",
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
    title_text = f"Comparison: {car1['name']} vs {car2['name']}" if lang == "en" else f"So Sánh: {car1['name']} vs {car2['name']}"
    _apply_theme(fig, title_text, theme=theme)
    return fig


def plot_tco_comparison(
    monthly_km: int,
    ev_kwh_per_100km: float = 14.0,
    gas_l_per_100km: float = 7.5,
    gas_price_vnd: float = 24000.0,
    elec_price_vnd: float = 3858.0,
    battery_rent_monthly: float = 1200000.0,
    theme: str = "light",
    lang: str = "vi"
) -> go.Figure:
    """So sánh tổng chi phí năng lượng tích lũy sau 1 năm và 3 năm."""
    annual_gas = (monthly_km * 12 / 100.0) * gas_l_per_100km * gas_price_vnd / 1e6
    annual_ev_bought = (monthly_km * 12 / 100.0) * ev_kwh_per_100km * elec_price_vnd / 1e6
    annual_ev_rent = annual_ev_bought + (battery_rent_monthly * 12 / 1e6)

    periods = ["1 Year", "2 Years", "3 Years"] if lang == "en" else ["1 Năm", "2 Năm", "3 Năm"]
    gas_totals = [round(annual_gas * i, 1) for i in [1, 2, 3]]
    ev_bought_totals = [round(annual_ev_bought * i, 1) for i in [1, 2, 3]]
    ev_rent_totals = [round(annual_ev_rent * i, 1) for i in [1, 2, 3]]

    lbl_gas = "ICE Petrol Vehicle" if lang == "en" else "Xe Xăng tương đương"
    lbl_rent = "EV (Battery Subscription)" if lang == "en" else "Xe Điện (Thuê Pin)"
    lbl_bought = "EV (Battery Included)" if lang == "en" else "Xe Điện (Mua Đứt Pin)"
    title_text = f"Cumulative Energy Costs ({monthly_km:,.0f} km/month)" if lang == "en" else f"Dự Toán Chi Phí Năng Lượng ({monthly_km:,.0f} km/tháng)"
    y_title = "Cumulative Cost (Million VND)" if lang == "en" else "Tổng chi phí nhiên liệu (Triệu VNĐ)"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=periods,
        y=gas_totals,
        name=lbl_gas,
        marker_color="#f43f5e",
        text=[f"{v:,.1f}" for v in gas_totals],
        textposition="outside"
    ))
    fig.add_trace(go.Bar(
        x=periods,
        y=ev_rent_totals,
        name=lbl_rent,
        marker_color="#f59e0b",
        text=[f"{v:,.1f}" for v in ev_rent_totals],
        textposition="outside"
    ))
    fig.add_trace(go.Bar(
        x=periods,
        y=ev_bought_totals,
        name=lbl_bought,
        marker_color="#10b981",
        text=[f"{v:,.1f}" for v in ev_bought_totals],
        textposition="outside"
    ))

    fig.update_layout(barmode="group")
    _apply_theme(fig, title_text, theme=theme)
    fig.update_yaxes(title=dict(text=y_title, font=dict(size=11)))
    return fig
