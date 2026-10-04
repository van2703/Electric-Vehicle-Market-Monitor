"""
app/charts.py
-------------
Chart-building functions used by the Market Overview page.
All charts return Plotly Figure objects for rendering in Streamlit.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─── Shared colour palette ─────────────────────────────────────────────────────
PALETTE = px.colors.qualitative.Bold
FONT_FAMILY = "Inter, sans-serif"

def _apply_theme(fig: go.Figure, title: str = "") -> go.Figure:
    """Apply a clean, modern dark-ish theme to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, family=FONT_FAMILY, color="#1e293b"), x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,0.8)",
        font=dict(family=FONT_FAMILY, color="#334155"),
        margin=dict(t=55, b=40, l=40, r=20),
        legend=dict(bgcolor="rgba(255,255,255,0.85)", bordercolor="#e2e8f0", borderwidth=1),
    )
    fig.update_xaxes(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    fig.update_yaxes(gridcolor="#e2e8f0", zerolinecolor="#cbd5e1")
    return fig


# ─── 1. Số lượng tin theo dòng xe ──────────────────────────────────────────────
def chart_listing_count(df: pd.DataFrame) -> go.Figure:
    counts = (
        df.groupby("family")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=True)
    )
    fig = px.bar(
        counts, x="count", y="family", orientation="h",
        color="count", color_continuous_scale="Blues",
        text="count", labels={"count": "Số tin", "family": "Dòng xe"},
    )
    fig.update_traces(textposition="outside")
    fig.update_coloraxes(showscale=False)
    return _apply_theme(fig, "📊 Số lượng tin đăng theo dòng xe")


# ─── 2. Phân phối giá (linear + log) ───────────────────────────────────────────
def chart_price_distribution(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Trục tuyến tính", "Trục log (phát hiện đuôi dài)"],
        horizontal_spacing=0.12,
    )
    prices = df["price_million"].dropna()

    # Linear
    fig.add_trace(
        go.Histogram(x=prices, nbinsx=40, marker_color="#3b82f6",
                     opacity=0.8, name="Giá (linear)"),
        row=1, col=1,
    )
    # Log
    log_prices = np.log10(prices.clip(lower=1))
    fig.add_trace(
        go.Histogram(x=log_prices, nbinsx=40, marker_color="#10b981",
                     opacity=0.8, name="Giá (log10)"),
        row=1, col=2,
    )
    fig.update_xaxes(title_text="Triệu VNĐ", row=1, col=1)
    fig.update_xaxes(title_text="log₁₀(Triệu VNĐ)", row=1, col=2)
    fig.update_yaxes(title_text="Số tin", row=1, col=1)
    fig.update_layout(showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(248,250,252,0.8)",
                      font=dict(family=FONT_FAMILY))
    fig.update_xaxes(gridcolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#e2e8f0")
    return fig


# ─── 3. Box plot giá theo dòng xe ──────────────────────────────────────────────
def chart_price_by_family(df: pd.DataFrame) -> go.Figure:
    # Sort families by median price
    medians = df.groupby("family")["price_million"].median().sort_values()
    ordered = medians.index.tolist()

    fig = px.box(
        df, x="family", y="price_million",
        category_orders={"family": ordered},
        color="family",
        color_discrete_sequence=PALETTE,
        labels={"family": "Dòng xe", "price_million": "Giá (triệu VNĐ)"},
        points="outliers",
    )
    # Overlay median markers
    for fam, med in medians.items():
        fig.add_annotation(
            x=fam, y=med,
            text=f"{med:.0f}",
            showarrow=False,
            font=dict(size=9, color="#1e293b"),
            yshift=14,
        )
    fig.update_layout(showlegend=False)
    return _apply_theme(fig, "💰 Phân phối giá theo dòng xe (kèm trung vị)")


# ─── 4. Xe mới vs. cũ theo dòng xe ────────────────────────────────────────────
def chart_new_vs_used(df: pd.DataFrame) -> go.Figure:
    counts = (
        df.groupby(["family", "condition"])
        .size()
        .reset_index(name="count")
    )
    # Order by total count
    total = counts.groupby("family")["count"].sum().sort_values(ascending=False)
    fig = px.bar(
        counts, x="family", y="count", color="condition",
        category_orders={
            "family": total.index.tolist(),
            "condition": ["New", "Used"],
        },
        color_discrete_map={"New": "#3b82f6", "Used": "#f59e0b"},
        barmode="group",
        labels={"family": "Dòng xe", "count": "Số tin", "condition": "Tình trạng"},
    )
    return _apply_theme(fig, "🆕 Xe mới vs. xe cũ theo dòng xe")


# ─── 5. Predicted vs Actual scatter (Model Performance page) ───────────────────
def chart_pred_vs_actual(
    y_test: list, y_pred: list, model_name: str, mae: float, r2: float
) -> go.Figure:
    y_test_arr = np.array(y_test)
    y_pred_arr = np.array(y_pred)

    lo = min(y_test_arr.min(), y_pred_arr.min()) - 20
    hi = max(y_test_arr.max(), y_pred_arr.max()) + 20

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=y_test_arr, y=y_pred_arr, mode="markers",
        marker=dict(color="#3b82f6", size=7, opacity=0.6,
                    line=dict(color="white", width=0.5)),
        name="Dự đoán",
    ))
    fig.add_trace(go.Scatter(
        x=[lo, hi], y=[lo, hi], mode="lines",
        line=dict(color="#ef4444", dash="dash", width=1.8),
        name="y = x (hoàn hảo)",
    ))
    fig.update_xaxes(title_text="Giá thực tế (triệu VNĐ)", range=[lo, hi])
    fig.update_yaxes(title_text="Giá dự đoán (triệu VNĐ)", range=[lo, hi])
    title = (
        f"Dự đoán vs. Thực tế — {model_name}<br>"
        f"<sup>MAE = {mae:.1f} triệu VNĐ &nbsp;|&nbsp; R² = {r2:.3f}</sup>"
    )
    return _apply_theme(fig, title)


# ─── 6. Metrics bar chart (Model Performance page) ─────────────────────────────
def chart_metrics_bars(metrics: dict) -> go.Figure:
    """metrics: {'baseline': {'mae':..,'r2':..}, 'linear_regression': {...}, 'random_forest': {...}}"""
    names = ["Baseline", "Linear Regression", "Random Forest"]
    keys  = ["baseline", "linear_regression", "random_forest"]
    maes  = [metrics[k]["mae"] for k in keys]
    r2s   = [metrics[k]["r2"]  for k in keys]
    colors = ["#94a3b8", "#3b82f6", "#10b981"]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["MAE — Thấp hơn = Tốt hơn", "R² — Cao hơn = Tốt hơn"],
        horizontal_spacing=0.15,
    )
    fig.add_trace(
        go.Bar(x=names, y=maes, marker_color=colors,
               text=[f"{v:.1f}" for v in maes], textposition="outside",
               name="MAE"),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=names, y=r2s, marker_color=colors,
               text=[f"{v:.3f}" for v in r2s], textposition="outside",
               name="R²"),
        row=1, col=2,
    )
    fig.update_yaxes(title_text="Triệu VNĐ", row=1, col=1)
    fig.update_yaxes(title_text="R²", row=1, col=2)
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248,250,252,0.8)",
        font=dict(family=FONT_FAMILY),
    )
    fig.update_xaxes(gridcolor="#e2e8f0")
    fig.update_yaxes(gridcolor="#e2e8f0")
    return fig
