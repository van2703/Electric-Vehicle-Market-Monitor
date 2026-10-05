"""
app/forecaster.py
-----------------
Module dự báo xu hướng giá xe điện và thuật toán tư vấn thời điểm mua thông minh:
1. calculate_12m_forecast(): Dự báo đường giá 12 tháng tới kèm dải tin cậy 90%.
2. get_best_buying_advice(): Nhận diện 'Thời điểm vàng để mua' và tín hiệu khuyến nghị.
3. match_timing_and_budget(): Gợi ý xe theo thời điểm dự kiến mua và ngân sách.
4. get_resale_index_table(): Bảng xếp hạng chỉ số giữ giá (Resale Value Index).
Hỗ trợ đa ngôn ngữ (Tiếng Việt & English).
"""

from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from app.data_loader import MODEL_CATALOG

# ─── Tỷ lệ khấu hao cơ sở năm theo từng mẫu xe ──────────────────────────────
MODEL_ANNUAL_DEPRECIATION = {
    "VF 3": 0.050,
    "VF 5": 0.065,
    "VF 6": 0.080,
    "VF 7": 0.090,
    "VF 8": 0.110,
    "VF 9": 0.120,
    "VF e34": 0.085,
    "Limo Green": 0.080,
    "Seal": 0.090,
    "Dolphin": 0.085,
    "Hongguang Mini EV": 0.070,
}

# ─── Hệ số chu kỳ thị trường ô tô Việt Nam theo tháng ────────────────────────
SEASONAL_FACTORS = {
    1: 1.012,
    2: 0.985,
    3: 0.995,
    4: 1.000,
    5: 1.000,
    6: 0.988,
    7: 0.970,
    8: 0.965,
    9: 0.995,
    10: 1.010,
    11: 1.025,
    12: 1.030,
}

EN_MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def calculate_12m_forecast(
    base_price: float,
    model_name: str,
    condition: str = "Used",
    start_date: datetime = None,
    lang: str = "vi"
) -> pd.DataFrame:
    """
    Tính toán đường giá dự phóng 12 tháng tới:
    P(t) = P0 * (1 - monthly_rate * t) * (Seasonal(t) / Seasonal(0))
    """
    if start_date is None:
        start_date = datetime.now()

    annual_rate = MODEL_ANNUAL_DEPRECIATION.get(model_name, 0.085)
    if "Mới" in condition or condition in ["New", "New 100%"]:
        annual_rate += 0.030

    monthly_rate = annual_rate / 12.0
    cur_month = start_date.month
    s0 = SEASONAL_FACTORS.get(cur_month, 1.0)

    records = []
    for i in range(1, 13):
        target_date = start_date + relativedelta(months=i)
        tm = target_date.month
        s_t = SEASONAL_FACTORS.get(tm, 1.0)

        p_t = base_price * (1.0 - monthly_rate * i) * (s_t / s0)
        ci = 0.025 + 0.0025 * i
        p_min = p_t * (1.0 - ci)
        p_max = p_t * (1.0 + ci)

        if lang == "en":
            m_name = f"{EN_MONTH_NAMES[tm-1]} {target_date.year}"
            if tm in [7, 8]:
                season_label = "Mid-year clearance dip"
            elif tm in [11, 12]:
                season_label = "Year-end high demand"
            elif tm == 2:
                season_label = "Post-Tet cool down"
            else:
                season_label = "Stable market"
        else:
            m_name = f"Tháng {tm}/{target_date.year}"
            if tm in [7, 8]:
                season_label = "Đáy ưu đãi (Tháng Ngâu)"
            elif tm in [11, 12]:
                season_label = "Cao điểm cuối năm"
            elif tm == 2:
                season_label = "Sau Tết hạ nhiệt"
            else:
                season_label = "Bình ổn"

        records.append({
            "month_idx": i,
            "date_str": target_date.strftime("%m/%Y"),
            "month_num": tm,
            "month_name": m_name,
            "pred_price": round(p_t, 1),
            "price_min": round(p_min, 1),
            "price_max": round(p_max, 1),
            "saving_vs_now": round(base_price - p_t, 1),
            "season_label": season_label
        })

    df_fc = pd.DataFrame(records)
    min_idx = df_fc["pred_price"].idxmin()
    df_fc["is_best_time"] = False
    df_fc.loc[min_idx, "is_best_time"] = True

    return df_fc


def get_best_buying_advice(forecast_df: pd.DataFrame, base_price: float, model_name: str, lang: str = "vi") -> dict:
    """Phân tích và xuất khuyến nghị thời điểm mua tốt nhất."""
    best_row = forecast_df[forecast_df["is_best_time"]].iloc[0]
    best_month_name = best_row["month_name"]
    best_price = best_row["pred_price"]
    saving = best_row["saving_vs_now"]
    wait_months = best_row["month_idx"]

    if lang == "en":
        if wait_months <= 2 or saving < 10.0:
            signal = "BUY NOW"
            badge_type = "success"
            color = "#10b981"
            summary = (
                f"Current asking price for **{model_name}** ({base_price:,.0f}M VND) is already at an attractive entry level. "
                f"Projected price variation over the next 2-3 months remains narrow (under {saving:,.0f}M VND). "
                f"Proceeding now avoids subsequent year-end price firming."
            )
        elif wait_months <= 6:
            signal = f"WAIT {wait_months} MONTHS ({best_month_name})"
            badge_type = "warning"
            color = "#f59e0b"
            summary = (
                f"If timing is flexible, consider targeting **{best_month_name}**. "
                f"The model anticipates an optimal price floor near **{best_price:,.0f}M VND**, "
                f"delivering an estimated saving of **{saving:,.0f}M VND** (~{saving/base_price*100:.1f}%) versus present rates."
            )
        else:
            signal = f"OPTIMAL WINDOW: {best_month_name}"
            badge_type = "info"
            color = "#3b82f6"
            summary = (
                f"The steepest seasonal price adjustment is expected around **{best_month_name}** ({best_row['season_label']}). "
                f"Projected valuation reaches approximately **{best_price:,.0f}M VND**, "
                f"yielding estimated savings of **{saving:,.0f}M VND**."
            )
    else:
        if wait_months <= 2 or saving < 10.0:
            signal = "NÊN MUA NGAY"
            badge_type = "success"
            color = "#10b981"
            summary = (
                f"Mức giá hiện tại của **{model_name}** ({base_price:,.0f} tr) đang ở vùng rất tốt. "
                f"Trong 2-3 tháng tới thị trường dự kiến không giảm thêm đáng kể (chênh lệch dưới {saving:,.0f} tr). "
                f"Nên xuống tiền ngay để sở hữu sớm và tránh chu kỳ tăng giá cao điểm."
            )
        elif wait_months <= 6:
            signal = f"NÊN CHỜ {wait_months} THÁNG ({best_month_name})"
            badge_type = "warning"
            color = "#f59e0b"
            summary = (
                f"Nếu chưa vội, bạn nên cân nhắc chờ đến **{best_month_name}**. "
                f"Dự báo giá xe sẽ chạm đáy đợt này còn khoảng **{best_price:,.0f} triệu VNĐ**, "
                f"tiết kiệm được khoảng **{saving:,.0f} triệu VNĐ** (~{saving/base_price*100:.1f}%) so với mua lúc này."
            )
        else:
            signal = f"THỜI ĐIỂM TỐT NHẤT: {best_month_name}"
            badge_type = "info"
            color = "#3b82f6"
            summary = (
                f"Đợt điều chỉnh giá sâu nhất sẽ rơi vào **{best_month_name}** ({best_row['season_label']}). "
                f"Mức giá dự kiến chỉ còn **{best_price:,.0f} triệu VNĐ**, "
                f"giúp bạn tối ưu ngân sách tới **{saving:,.0f} triệu VNĐ**."
            )

    return {
        "signal": signal,
        "badge_type": badge_type,
        "color": color,
        "best_month": best_month_name,
        "wait_months": wait_months,
        "best_price": best_price,
        "saving": saving,
        "summary": summary
    }


def match_timing_and_budget(
    target_month_offset: int,
    budget_million: float,
    brand_filter: str = "Tất cả",
    condition: str = "Used",
    lang: str = "vi"
) -> list[dict]:
    """
    Tìm kiếm và xếp hạng các mẫu xe theo thời điểm dự kiến mua và ngân sách.
    """
    candidates = []
    for model_name, spec in MODEL_CATALOG.items():
        if brand_filter not in ["Tất cả", "All"] and spec["brand"] != brand_filter:
            continue

        base_p = spec["default_price"]
        if "Cũ" in condition or condition in ["Used", "Pre-owned"]:
            base_p *= 0.85

        fc = calculate_12m_forecast(base_p, model_name, condition, lang=lang)
        target_row = fc[fc["month_idx"] == target_month_offset].iloc[0]
        future_price = target_row["pred_price"]
        diff = budget_million - future_price

        if 0 <= diff <= budget_million * 0.15:
            fit_status = "Phù hợp ngân sách" if lang == "vi" else "Optimal Budget Fit"
            fit_code = "perfect"
            order = 1
        elif diff > budget_million * 0.15:
            fit_status = "Tiết kiệm ngân sách" if lang == "vi" else "Budget Friendly"
            fit_code = "economical"
            order = 2
        elif -budget_million * 0.10 <= diff < 0:
            fit_status = "Cố thêm một chút" if lang == "vi" else "Slight Stretch"
            fit_code = "stretch"
            order = 3
        else:
            fit_status = "Vượt ngân sách" if lang == "vi" else "Above Budget"
            fit_code = "over"
            order = 4

        if fit_code != "over":
            candidates.append({
                "model": model_name,
                "brand": spec["brand"],
                "segment": spec["segment"],
                "image": spec["image"],
                "current_price": round(base_p, 1),
                "future_price": future_price,
                "budget_diff": round(diff, 1),
                "target_month_name": target_row["month_name"],
                "fit_status": fit_status,
                "fit_code": fit_code,
                "order": order,
                "range_km": spec["range_km"],
                "seats": spec["seats"]
            })

    candidates.sort(key=lambda x: (x["order"], abs(x["budget_diff"])))
    return candidates


def get_resale_index_table(lang: str = "vi") -> pd.DataFrame:
    """Tạo bảng xếp hạng chỉ số giữ giá (Resale Value Index)."""
    rows = []
    for model_name, spec in MODEL_CATALOG.items():
        base_p = spec["default_price"]
        rate = MODEL_ANNUAL_DEPRECIATION.get(model_name, 0.085)
        retention_1y = round((1.0 - rate) * 100, 1)
        retention_2y = round((1.0 - rate * 1.85) * 100, 1)
        est_val_1y = round(base_p * (retention_1y / 100.0), 1)

        if lang == "en":
            rating = "Excellent" if retention_1y >= 93 else ("Good" if retention_1y >= 90 else "Moderate")
            rows.append({
                "Model": model_name,
                "Brand": spec["brand"],
                "Segment": spec["segment"],
                "MSRP (M VND)": base_p,
                "1Y Retention": f"{retention_1y}%",
                "Est. Value 1Y (M)": est_val_1y,
                "2Y Retention": f"{retention_2y}%",
                "Rating": rating
            })
        else:
            rating = "Giữ giá xuất sắc" if retention_1y >= 93 else ("Khá" if retention_1y >= 90 else "Trung bình")
            rows.append({
                "Mẫu xe": model_name,
                "Hãng": spec["brand"],
                "Phân khúc": spec["segment"],
                "Giá mốc (tr)": base_p,
                "Giữ giá sau 1 năm": f"{retention_1y}%",
                "Giá sau 1 năm (tr)": est_val_1y,
                "Giữ giá sau 2 năm": f"{retention_2y}%",
                "Đánh giá": rating
            })

    df = pd.DataFrame(rows)
    sort_col = "1Y Retention" if lang == "en" else "Giữ giá sau 1 năm"
    df = df.sort_values(by=sort_col, ascending=False)
    return df
