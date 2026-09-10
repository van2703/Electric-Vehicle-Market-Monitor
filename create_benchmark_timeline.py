import pandas as pd
import os
import sys

# Đảm bảo in tiếng Việt trên console Windows không lỗi charmap
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def build_benchmark_timeline_data():
    print("=== XÂY DỰNG BỘ DỮ LIỆU BENCHMARK 2 DIMENSIONS (MODEL x TIMELINE) ===")

    # Dữ liệu Ground Truth: Lịch sử giá niêm yết chính hãng qua các năm (2021 - 2026)
    # Giá tính bằng VNĐ
    timeline_records = [
        # ==========================================
        # 1. VINFAST - Ô TÔ ĐIỆN
        # ==========================================
        # --- VF 3 (Mở cọc 2024, giao xe 2024-2026) ---
        {"Brand": "VinFast", "Model": "VF 3", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 240000000, "Price_No_Battery": 240000000, "Price_With_Battery": 322000000, "Battery_Cost": 82000000, "Notes": "Ưu đãi mở cọc tiên phong 240tr"},
        {"Brand": "VinFast", "Model": "VF 3", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 240000000, "Price_No_Battery": 240000000, "Price_With_Battery": 322000000, "Battery_Cost": 82000000, "Notes": "Bán đại trà"},
        {"Brand": "VinFast", "Model": "VF 3", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 285000000, "Price_No_Battery": 285000000, "Price_With_Battery": 365000000, "Battery_Cost": 80000000, "Notes": "Giá niêm yết 2026"},

        # --- VF 5 Plus (Mở bán từ 2023) ---
        {"Brand": "VinFast", "Model": "VF 5", "Category": "Ô tô", "Year": 2023, "Price_Benchmark": 458000000, "Price_No_Battery": 458000000, "Price_With_Battery": 538000000, "Battery_Cost": 80000000, "Notes": "Ra mắt mở bán"},
        {"Brand": "VinFast", "Model": "VF 5", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 468000000, "Price_No_Battery": 468000000, "Price_With_Battery": 548000000, "Battery_Cost": 80000000, "Notes": "Điều chỉnh giá niêm yết"},
        {"Brand": "VinFast", "Model": "VF 5", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 468000000, "Price_No_Battery": 468000000, "Price_With_Battery": 548000000, "Battery_Cost": 80000000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "VF 5", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 496000000, "Price_No_Battery": 496000000, "Price_With_Battery": 576000000, "Battery_Cost": 80000000, "Notes": "Cập nhật 2026"},

        # --- VF 6 (Mở bán cuối 2023) ---
        {"Brand": "VinFast", "Model": "VF 6", "Category": "Ô tô", "Year": 2023, "Price_Benchmark": 675000000, "Price_No_Battery": 675000000, "Price_With_Battery": 765000000, "Battery_Cost": 90000000, "Notes": "Ra mắt Eco/Plus"},
        {"Brand": "VinFast", "Model": "VF 6", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 675000000, "Price_No_Battery": 675000000, "Price_With_Battery": 765000000, "Battery_Cost": 90000000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "VF 6", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 646000000, "Price_No_Battery": 646000000, "Price_With_Battery": 736000000, "Battery_Cost": 90000000, "Notes": "Ưu đãi giá mới"},
        {"Brand": "VinFast", "Model": "VF 6", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 646000000, "Price_No_Battery": 646000000, "Price_With_Battery": 736000000, "Battery_Cost": 90000000, "Notes": "Giá niêm yết 2026"},

        # --- VF 7 (Mở bán cuối 2023) ---
        {"Brand": "VinFast", "Model": "VF 7", "Category": "Ô tô", "Year": 2023, "Price_Benchmark": 850000000, "Price_No_Battery": 850000000, "Price_With_Battery": 999000000, "Battery_Cost": 149000000, "Notes": "Ra mắt mở bán"},
        {"Brand": "VinFast", "Model": "VF 7", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 850000000, "Price_No_Battery": 850000000, "Price_With_Battery": 999000000, "Battery_Cost": 149000000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "VF 7", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 740000000, "Price_No_Battery": 740000000, "Price_With_Battery": 889000000, "Battery_Cost": 149000000, "Notes": "Ưu đãi điều chỉnh"},
        {"Brand": "VinFast", "Model": "VF 7", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 740000000, "Price_No_Battery": 740000000, "Price_With_Battery": 889000000, "Battery_Cost": 149000000, "Notes": "Giá niêm yết 2026"},

        # --- VF 8 (Ra mắt 2022) ---
        {"Brand": "VinFast", "Model": "VF 8", "Category": "Ô tô", "Year": 2022, "Price_Benchmark": 1057000000, "Price_No_Battery": 1057000000, "Price_With_Battery": 1443000000, "Battery_Cost": 386000000, "Notes": "Tiên phong đợt đầu"},
        {"Brand": "VinFast", "Model": "VF 8", "Category": "Ô tô", "Year": 2023, "Price_Benchmark": 1090000000, "Price_No_Battery": 1090000000, "Price_With_Battery": 1290000000, "Battery_Cost": 200000000, "Notes": "Chính sách pin mới"},
        {"Brand": "VinFast", "Model": "VF 8", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 1090000000, "Price_No_Battery": 1090000000, "Price_With_Battery": 1290000000, "Battery_Cost": 200000000, "Notes": "Bản nâng cấp Lux"},
        {"Brand": "VinFast", "Model": "VF 8", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 898000000, "Price_No_Battery": 898000000, "Price_With_Battery": 1079000000, "Battery_Cost": 181000000, "Notes": "Chương trình Mãnh Liệt Tinh Thần VN"},
        {"Brand": "VinFast", "Model": "VF 8", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 898000000, "Price_No_Battery": 898000000, "Price_With_Battery": 1079000000, "Battery_Cost": 181000000, "Notes": "Giá niêm yết 2026"},

        # --- VF 9 (Ra mắt 2022) ---
        {"Brand": "VinFast", "Model": "VF 9", "Category": "Ô tô", "Year": 2022, "Price_Benchmark": 1443000000, "Price_No_Battery": 1443000000, "Price_With_Battery": 1936000000, "Battery_Cost": 493000000, "Notes": "Mở bán đợt đầu"},
        {"Brand": "VinFast", "Model": "VF 9", "Category": "Ô tô", "Year": 2023, "Price_Benchmark": 1491000000, "Price_No_Battery": 1491000000, "Price_With_Battery": 1991000000, "Battery_Cost": 500000000, "Notes": "Cập nhật chính sách"},
        {"Brand": "VinFast", "Model": "VF 9", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 1491000000, "Price_No_Battery": 1491000000, "Price_With_Battery": 1991000000, "Battery_Cost": 500000000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "VF 9", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 1348000000, "Price_No_Battery": 1348000000, "Price_With_Battery": 1529000000, "Battery_Cost": 181000000, "Notes": "Ưu đãi giá mới"},
        {"Brand": "VinFast", "Model": "VF 9", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 1348000000, "Price_No_Battery": 1348000000, "Price_With_Battery": 1529000000, "Battery_Cost": 181000000, "Notes": "Giá niêm yết 2026"},

        # --- VF e34 (Ra mắt 2021) ---
        {"Brand": "VinFast", "Model": "VF e34", "Category": "Ô tô", "Year": 2021, "Price_Benchmark": 690000000, "Price_No_Battery": 690000000, "Price_With_Battery": 810000000, "Battery_Cost": 120000000, "Notes": "Mở cọc 590tr, niêm yết 690tr"},
        {"Brand": "VinFast", "Model": "VF e34", "Category": "Ô tô", "Year": 2022, "Price_Benchmark": 710000000, "Price_No_Battery": 710000000, "Price_With_Battery": 830000000, "Battery_Cost": 120000000, "Notes": "Tăng giá niêm yết"},
        {"Brand": "VinFast", "Model": "VF e34", "Category": "Ô tô", "Year": 2023, "Price_Benchmark": 710000000, "Price_No_Battery": 710000000, "Price_With_Battery": 830000000, "Battery_Cost": 120000000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "VF e34", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 710000000, "Price_No_Battery": 710000000, "Price_With_Battery": 830000000, "Battery_Cost": 120000000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "VF e34", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 710000000, "Price_No_Battery": 710000000, "Price_With_Battery": 830000000, "Battery_Cost": 120000000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "VF e34", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 710000000, "Price_No_Battery": 710000000, "Price_With_Battery": 830000000, "Battery_Cost": 120000000, "Notes": "Duy trì giá"},

        # --- Limo Green (Dòng dịch vụ Taxi / B2C) ---
        {"Brand": "VinFast", "Model": "Limo Green", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 699000000, "Price_No_Battery": 699000000, "Price_With_Battery": 799000000, "Battery_Cost": 100000000, "Notes": "Dòng xe MPV Green"},
        {"Brand": "VinFast", "Model": "Limo Green", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 699000000, "Price_No_Battery": 699000000, "Price_With_Battery": 799000000, "Battery_Cost": 100000000, "Notes": "Bản thương mại"},
        {"Brand": "VinFast", "Model": "Limo Green", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 699000000, "Price_No_Battery": 699000000, "Price_With_Battery": 799000000, "Battery_Cost": 100000000, "Notes": "Duy trì giá"},

        # ==========================================
        # 2. BYD - Ô TÔ ĐIỆN CHÍNH HÃNG TẠI VN
        # ==========================================
        {"Brand": "BYD", "Model": "Seal", "Category": "Ô tô", "Year": 2024, "Price_Benchmark": 1119000000, "Price_No_Battery": 1119000000, "Price_With_Battery": 1119000000, "Battery_Cost": 0, "Notes": "Ra mắt chính hãng Advanced (Kèm pin)"},
        {"Brand": "BYD", "Model": "Seal", "Category": "Ô tô", "Year": 2025, "Price_Benchmark": 1119000000, "Price_No_Battery": 1119000000, "Price_With_Battery": 1119000000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "BYD", "Model": "Seal", "Category": "Ô tô", "Year": 2026, "Price_Benchmark": 1119000000, "Price_No_Battery": 1119000000, "Price_With_Battery": 1119000000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # ==========================================
        # 3. VINFAST - XE MÁY ĐIỆN
        # ==========================================
        # --- Evo 200 ---
        {"Brand": "VinFast", "Model": "Evo 200", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 22000000, "Price_No_Battery": 22000000, "Price_With_Battery": 41900000, "Battery_Cost": 19900000, "Notes": "Ra mắt pin LFP"},
        {"Brand": "VinFast", "Model": "Evo 200", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 18000000, "Price_No_Battery": 18000000, "Price_With_Battery": 37900000, "Battery_Cost": 19900000, "Notes": "Giảm giá kích cầu"},
        {"Brand": "VinFast", "Model": "Evo 200", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 18000000, "Price_No_Battery": 18000000, "Price_With_Battery": 37900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Evo 200", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 18000000, "Price_No_Battery": 18000000, "Price_With_Battery": 37900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Evo 200", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 18000000, "Price_No_Battery": 18000000, "Price_With_Battery": 37900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},

        # --- Feliz / Feliz S ---
        {"Brand": "VinFast", "Model": "Feliz", "Category": "Xe máy", "Year": 2021, "Price_Benchmark": 24900000, "Price_No_Battery": 24900000, "Price_With_Battery": 24900000, "Battery_Cost": 0, "Notes": "Bản ắc quy chì"},
        {"Brand": "VinFast", "Model": "Feliz", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 29900000, "Price_No_Battery": 29900000, "Price_With_Battery": 49800000, "Battery_Cost": 19900000, "Notes": "Nâng cấp pin LFP Feliz S"},
        {"Brand": "VinFast", "Model": "Feliz", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 27000000, "Price_No_Battery": 27000000, "Price_With_Battery": 46900000, "Battery_Cost": 19900000, "Notes": "Điều chỉnh giá"},
        {"Brand": "VinFast", "Model": "Feliz", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 27000000, "Price_No_Battery": 27000000, "Price_With_Battery": 46900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Feliz", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 27000000, "Price_No_Battery": 27000000, "Price_With_Battery": 46900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Feliz", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 27000000, "Price_No_Battery": 27000000, "Price_With_Battery": 46900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},

        # --- Klara / Klara S ---
        {"Brand": "VinFast", "Model": "Klara", "Category": "Xe máy", "Year": 2021, "Price_Benchmark": 39900000, "Price_No_Battery": 39900000, "Price_With_Battery": 39900000, "Battery_Cost": 0, "Notes": "Klara S bản cũ"},
        {"Brand": "VinFast", "Model": "Klara", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 36900000, "Price_No_Battery": 36900000, "Price_With_Battery": 56800000, "Battery_Cost": 19900000, "Notes": "Klara S pin LFP"},
        {"Brand": "VinFast", "Model": "Klara", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 35000000, "Price_No_Battery": 35000000, "Price_With_Battery": 54900000, "Battery_Cost": 19900000, "Notes": "Điều chỉnh giá"},
        {"Brand": "VinFast", "Model": "Klara", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 35000000, "Price_No_Battery": 35000000, "Price_With_Battery": 54900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Klara", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 35000000, "Price_No_Battery": 35000000, "Price_With_Battery": 54900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Klara", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 35000000, "Price_No_Battery": 35000000, "Price_With_Battery": 54900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},

        # --- Vento / Vento S ---
        {"Brand": "VinFast", "Model": "Vento", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 56000000, "Price_No_Battery": 56000000, "Price_With_Battery": 75900000, "Battery_Cost": 19900000, "Notes": "Ra mắt Vento S"},
        {"Brand": "VinFast", "Model": "Vento", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 50000000, "Price_No_Battery": 50000000, "Price_With_Battery": 69900000, "Battery_Cost": 19900000, "Notes": "Điều chỉnh giá"},
        {"Brand": "VinFast", "Model": "Vento", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 50000000, "Price_No_Battery": 50000000, "Price_With_Battery": 69900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Vento", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 50000000, "Price_No_Battery": 50000000, "Price_With_Battery": 69900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Vento", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 50000000, "Price_No_Battery": 50000000, "Price_With_Battery": 69900000, "Battery_Cost": 19900000, "Notes": "Duy trì giá"},

        # --- Ludo ---
        {"Brand": "VinFast", "Model": "Ludo", "Category": "Xe máy", "Year": 2021, "Price_Benchmark": 12900000, "Price_No_Battery": 12900000, "Price_With_Battery": 12900000, "Battery_Cost": 0, "Notes": "Dòng xe học sinh"},
        {"Brand": "VinFast", "Model": "Ludo", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 12900000, "Price_No_Battery": 12900000, "Price_With_Battery": 12900000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Ludo", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 12900000, "Price_No_Battery": 12900000, "Price_With_Battery": 12900000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Ludo", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 12900000, "Price_No_Battery": 12900000, "Price_With_Battery": 12900000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Ludo", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 12900000, "Price_No_Battery": 12900000, "Price_With_Battery": 12900000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "VinFast", "Model": "Ludo", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 12900000, "Price_No_Battery": 12900000, "Price_With_Battery": 12900000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # ==========================================
        # 4. DAT BIKE
        # ==========================================
        # --- Quantum ---
        {"Brand": "Dat Bike", "Model": "Quantum", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 46000000, "Price_No_Battery": 46000000, "Price_With_Battery": 46000000, "Battery_Cost": 0, "Notes": "Ra mắt Quantum thế hệ 1"},
        {"Brand": "Dat Bike", "Model": "Quantum", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 49900000, "Price_No_Battery": 49900000, "Price_With_Battery": 49900000, "Battery_Cost": 0, "Notes": "Ra mắt dòng Quantum S1"},
        {"Brand": "Dat Bike", "Model": "Quantum", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 34900000, "Price_No_Battery": 34900000, "Price_With_Battery": 34900000, "Battery_Cost": 0, "Notes": "Bổ sung bản S3 giá 34.9tr, S2 giá 42.9tr"},
        {"Brand": "Dat Bike", "Model": "Quantum", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 34900000, "Price_No_Battery": 34900000, "Price_With_Battery": 34900000, "Battery_Cost": 0, "Notes": "Quantum S-Series"},

        # --- Dat Bike (Khác) (Weaver, Weaver 200, Weaver++) ---
        {"Brand": "Dat Bike", "Model": "Dat Bike (Khác)", "Category": "Xe máy", "Year": 2021, "Price_Benchmark": 54900000, "Price_No_Battery": 54900000, "Price_With_Battery": 54900000, "Battery_Cost": 0, "Notes": "Weaver 200"},
        {"Brand": "Dat Bike", "Model": "Dat Bike (Khác)", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 65900000, "Price_No_Battery": 65900000, "Price_With_Battery": 65900000, "Battery_Cost": 0, "Notes": "Weaver++"},
        {"Brand": "Dat Bike", "Model": "Dat Bike (Khác)", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 65900000, "Price_No_Battery": 65900000, "Price_With_Battery": 65900000, "Battery_Cost": 0, "Notes": "Weaver++"},
        {"Brand": "Dat Bike", "Model": "Dat Bike (Khác)", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 65900000, "Price_No_Battery": 65900000, "Price_With_Battery": 65900000, "Battery_Cost": 0, "Notes": "Weaver++"},
        {"Brand": "Dat Bike", "Model": "Dat Bike (Khác)", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 65900000, "Price_No_Battery": 65900000, "Price_With_Battery": 65900000, "Battery_Cost": 0, "Notes": "Weaver++"},
        {"Brand": "Dat Bike", "Model": "Dat Bike (Khác)", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 65900000, "Price_No_Battery": 65900000, "Price_With_Battery": 65900000, "Battery_Cost": 0, "Notes": "Weaver++"},

        # ==========================================
        # 5. DIBAO - XE MÁY ĐIỆN
        # ==========================================
        # --- Pansy ---
        {"Brand": "Dibao", "Model": "Pansy", "Category": "Xe máy", "Year": 2021, "Price_Benchmark": 16500000, "Price_No_Battery": 16500000, "Price_With_Battery": 16500000, "Battery_Cost": 0, "Notes": "Pansy S"},
        {"Brand": "Dibao", "Model": "Pansy", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 16500000, "Price_No_Battery": 16500000, "Price_With_Battery": 16500000, "Battery_Cost": 0, "Notes": "Pansy S2"},
        {"Brand": "Dibao", "Model": "Pansy", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 15900000, "Price_No_Battery": 15900000, "Price_With_Battery": 15900000, "Battery_Cost": 0, "Notes": "Pansy S3"},
        {"Brand": "Dibao", "Model": "Pansy", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 15490000, "Price_No_Battery": 15490000, "Price_With_Battery": 15490000, "Battery_Cost": 0, "Notes": "Pansy S3/S4"},
        {"Brand": "Dibao", "Model": "Pansy", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 15490000, "Price_No_Battery": 15490000, "Price_With_Battery": 15490000, "Battery_Cost": 0, "Notes": "Pansy Dio"},
        {"Brand": "Dibao", "Model": "Pansy", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 15490000, "Price_No_Battery": 15490000, "Price_With_Battery": 15490000, "Battery_Cost": 0, "Notes": "Pansy Neo"},

        # --- Gogo ---
        {"Brand": "Dibao", "Model": "Gogo", "Category": "Xe máy", "Year": 2021, "Price_Benchmark": 15900000, "Price_No_Battery": 15900000, "Price_With_Battery": 15900000, "Battery_Cost": 0, "Notes": "Gogo SS"},
        {"Brand": "Dibao", "Model": "Gogo", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 15900000, "Price_No_Battery": 15900000, "Price_With_Battery": 15900000, "Battery_Cost": 0, "Notes": "Gogo Cross"},
        {"Brand": "Dibao", "Model": "Gogo", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 14900000, "Price_No_Battery": 14900000, "Price_With_Battery": 14900000, "Battery_Cost": 0, "Notes": "Gogo S4"},
        {"Brand": "Dibao", "Model": "Gogo", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 14500000, "Price_No_Battery": 14500000, "Price_With_Battery": 14500000, "Battery_Cost": 0, "Notes": "Gogo Moon"},
        {"Brand": "Dibao", "Model": "Gogo", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 14500000, "Price_No_Battery": 14500000, "Price_With_Battery": 14500000, "Battery_Cost": 0, "Notes": "Gogo Moon"},
        {"Brand": "Dibao", "Model": "Gogo", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 14500000, "Price_No_Battery": 14500000, "Price_With_Battery": 14500000, "Battery_Cost": 0, "Notes": "Gogo Moon"},

        # --- Creer ---
        {"Brand": "Dibao", "Model": "Creer", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 15500000, "Price_No_Battery": 15500000, "Price_With_Battery": 15500000, "Battery_Cost": 0, "Notes": "Creer E"},
        {"Brand": "Dibao", "Model": "Creer", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 15190000, "Price_No_Battery": 15190000, "Price_With_Battery": 15190000, "Battery_Cost": 0, "Notes": "Creer Nile"},
        {"Brand": "Dibao", "Model": "Creer", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 14990000, "Price_No_Battery": 14990000, "Price_With_Battery": 14990000, "Battery_Cost": 0, "Notes": "Creer E"},
        {"Brand": "Dibao", "Model": "Creer", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 14990000, "Price_No_Battery": 14990000, "Price_With_Battery": 14990000, "Battery_Cost": 0, "Notes": "Creer E"},
        {"Brand": "Dibao", "Model": "Creer", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 14990000, "Price_No_Battery": 14990000, "Price_With_Battery": 14990000, "Battery_Cost": 0, "Notes": "Creer E"},

        # --- Tesla ---
        {"Brand": "Dibao", "Model": "Tesla", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 16900000, "Price_No_Battery": 16900000, "Price_With_Battery": 16900000, "Battery_Cost": 0, "Notes": "Tesla SD"},
        {"Brand": "Dibao", "Model": "Tesla", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 16900000, "Price_No_Battery": 16900000, "Price_With_Battery": 16900000, "Battery_Cost": 0, "Notes": "Tesla Chic"},
        {"Brand": "Dibao", "Model": "Tesla", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 14490000, "Price_No_Battery": 14490000, "Price_With_Battery": 14490000, "Battery_Cost": 0, "Notes": "Tesla Dio E"},
        {"Brand": "Dibao", "Model": "Tesla", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 14490000, "Price_No_Battery": 14490000, "Price_With_Battery": 14490000, "Battery_Cost": 0, "Notes": "Tesla Dio E"},
        {"Brand": "Dibao", "Model": "Tesla", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 14490000, "Price_No_Battery": 14490000, "Price_With_Battery": 14490000, "Battery_Cost": 0, "Notes": "Tesla Dio E"},

        # --- Xman ---
        {"Brand": "Dibao", "Model": "Xman", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 16500000, "Price_No_Battery": 16500000, "Price_With_Battery": 16500000, "Battery_Cost": 0, "Notes": "Xman Neo"},
        {"Brand": "Dibao", "Model": "Xman", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 16500000, "Price_No_Battery": 16500000, "Price_With_Battery": 16500000, "Battery_Cost": 0, "Notes": "Xman Neo"},
        {"Brand": "Dibao", "Model": "Xman", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 16500000, "Price_No_Battery": 16500000, "Price_With_Battery": 16500000, "Battery_Cost": 0, "Notes": "Xman Neo"},
        {"Brand": "Dibao", "Model": "Xman", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 16500000, "Price_No_Battery": 16500000, "Price_With_Battery": 16500000, "Battery_Cost": 0, "Notes": "Xman Neo"},
        {"Brand": "Dibao", "Model": "Xman", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 16500000, "Price_No_Battery": 16500000, "Price_With_Battery": 16500000, "Battery_Cost": 0, "Notes": "Xman Neo"},

        # --- LS007 ---
        {"Brand": "Dibao", "Model": "LS007", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 22990000, "Price_No_Battery": 22990000, "Price_With_Battery": 22990000, "Battery_Cost": 0, "Notes": "Bản thể thao"},
        {"Brand": "Dibao", "Model": "LS007", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 22990000, "Price_No_Battery": 22990000, "Price_With_Battery": 22990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Dibao", "Model": "LS007", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 22990000, "Price_No_Battery": 22990000, "Price_With_Battery": 22990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Shine ---
        {"Brand": "Dibao", "Model": "Shine", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 22990000, "Price_No_Battery": 22990000, "Price_With_Battery": 22990000, "Battery_Cost": 0, "Notes": "Bản cao cấp"},
        {"Brand": "Dibao", "Model": "Shine", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 22990000, "Price_No_Battery": 22990000, "Price_With_Battery": 22990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Dibao", "Model": "Shine", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 22990000, "Price_No_Battery": 22990000, "Price_With_Battery": 22990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # ==========================================
        # 6. YADEA - XE MÁY ĐIỆN
        # ==========================================
        # --- Voltguard ---
        {"Brand": "Yadea", "Model": "Voltguard", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 25990000, "Price_No_Battery": 25990000, "Price_With_Battery": 25990000, "Battery_Cost": 0, "Notes": "Ra mắt Voltguard 72V"},
        {"Brand": "Yadea", "Model": "Voltguard", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 25990000, "Price_No_Battery": 25990000, "Price_With_Battery": 25990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Yadea", "Model": "Voltguard", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 25990000, "Price_No_Battery": 25990000, "Price_With_Battery": 25990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Yadea", "Model": "Voltguard", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 25990000, "Price_No_Battery": 25990000, "Price_With_Battery": 25990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Ossy ---
        {"Brand": "Yadea", "Model": "Ossy", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 18490000, "Price_No_Battery": 18490000, "Price_With_Battery": 18490000, "Battery_Cost": 0, "Notes": "Ra mắt Ossy TTFAR"},
        {"Brand": "Yadea", "Model": "Ossy", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 18490000, "Price_No_Battery": 18490000, "Price_With_Battery": 18490000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Yadea", "Model": "Ossy", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 18490000, "Price_No_Battery": 18490000, "Price_With_Battery": 18490000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Orla ---
        {"Brand": "Yadea", "Model": "Orla", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 17990000, "Price_No_Battery": 17990000, "Price_With_Battery": 17990000, "Battery_Cost": 0, "Notes": "Ra mắt Orla"},
        {"Brand": "Yadea", "Model": "Orla", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 20490000, "Price_No_Battery": 20490000, "Price_With_Battery": 20490000, "Battery_Cost": 0, "Notes": "Bản Orla P"},
        {"Brand": "Yadea", "Model": "Orla", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 20490000, "Price_No_Battery": 20490000, "Price_With_Battery": 20490000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Yadea", "Model": "Orla", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 20490000, "Price_No_Battery": 20490000, "Price_With_Battery": 20490000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Osta ---
        {"Brand": "Yadea", "Model": "Osta", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 28990000, "Price_No_Battery": 28990000, "Price_With_Battery": 28990000, "Battery_Cost": 0, "Notes": "Ra mắt Osta H+"},
        {"Brand": "Yadea", "Model": "Osta", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 28990000, "Price_No_Battery": 28990000, "Price_With_Battery": 28990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Yadea", "Model": "Osta", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 28990000, "Price_No_Battery": 28990000, "Price_With_Battery": 28990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Ocean ---
        {"Brand": "Yadea", "Model": "Ocean", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 16990000, "Price_No_Battery": 16990000, "Price_With_Battery": 16990000, "Battery_Cost": 0, "Notes": "Ra mắt Yadea Ocean"},
        {"Brand": "Yadea", "Model": "Ocean", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 16990000, "Price_No_Battery": 16990000, "Price_With_Battery": 16990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Yadea", "Model": "Ocean", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 16990000, "Price_No_Battery": 16990000, "Price_With_Battery": 16990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Yadea (Khác) (Odora, Vekoo, X-Sky) ---
        {"Brand": "Yadea", "Model": "Yadea (Khác)", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 16500000, "Price_No_Battery": 16500000, "Price_With_Battery": 16500000, "Battery_Cost": 0, "Notes": "Odora"},
        {"Brand": "Yadea", "Model": "Yadea (Khác)", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 14990000, "Price_No_Battery": 14990000, "Price_With_Battery": 14990000, "Battery_Cost": 0, "Notes": "Vekoo"},
        {"Brand": "Yadea", "Model": "Yadea (Khác)", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 9990000, "Price_No_Battery": 9990000, "Price_With_Battery": 9990000, "Battery_Cost": 0, "Notes": "X-Sky"},
        {"Brand": "Yadea", "Model": "Yadea (Khác)", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 9990000, "Price_No_Battery": 9990000, "Price_With_Battery": 9990000, "Battery_Cost": 0, "Notes": "X-Sky"},
        {"Brand": "Yadea", "Model": "Yadea (Khác)", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 9990000, "Price_No_Battery": 9990000, "Price_With_Battery": 9990000, "Battery_Cost": 0, "Notes": "X-Sky"},

        # ==========================================
        # 7. CÁC HÃNG XE MÁY ĐIỆN KHÁC
        # ==========================================
        # --- Espero Velia ---
        {"Brand": "Espero", "Model": "Velia", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 23500000, "Price_No_Battery": 23500000, "Price_With_Battery": 23500000, "Battery_Cost": 0, "Notes": "Velia E"},
        {"Brand": "Espero", "Model": "Velia", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 23500000, "Price_No_Battery": 23500000, "Price_With_Battery": 23500000, "Battery_Cost": 0, "Notes": "Velia E"},
        {"Brand": "Espero", "Model": "Velia", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 23500000, "Price_No_Battery": 23500000, "Price_With_Battery": 23500000, "Battery_Cost": 0, "Notes": "Velia E"},
        {"Brand": "Espero", "Model": "Velia", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 23500000, "Price_No_Battery": 23500000, "Price_With_Battery": 23500000, "Battery_Cost": 0, "Notes": "Velia E"},

        # --- Osakar Nispa ---
        {"Brand": "Osakar", "Model": "Nispa", "Category": "Xe máy", "Year": 2022, "Price_Benchmark": 16990000, "Price_No_Battery": 16990000, "Price_With_Battery": 16990000, "Battery_Cost": 0, "Notes": "Nispa SV"},
        {"Brand": "Osakar", "Model": "Nispa", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 16990000, "Price_No_Battery": 16990000, "Price_With_Battery": 16990000, "Battery_Cost": 0, "Notes": "Nispa Vera"},
        {"Brand": "Osakar", "Model": "Nispa", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 16990000, "Price_No_Battery": 16990000, "Price_With_Battery": 16990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Osakar", "Model": "Nispa", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 16990000, "Price_No_Battery": 16990000, "Price_With_Battery": 16990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Osakar", "Model": "Nispa", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 16990000, "Price_No_Battery": 16990000, "Price_With_Battery": 16990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Osakar Momo ---
        {"Brand": "Osakar", "Model": "Momo", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 11990000, "Price_No_Battery": 11990000, "Price_With_Battery": 11990000, "Battery_Cost": 0, "Notes": "Momo Hot Girl"},
        {"Brand": "Osakar", "Model": "Momo", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 11990000, "Price_No_Battery": 11990000, "Price_With_Battery": 11990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Osakar", "Model": "Momo", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 11990000, "Price_No_Battery": 11990000, "Price_With_Battery": 11990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Osakar", "Model": "Momo", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 11990000, "Price_No_Battery": 11990000, "Price_With_Battery": 11990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Daelim Nova ---
        {"Brand": "Daelim", "Model": "Nova", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 13990000, "Price_No_Battery": 13990000, "Price_With_Battery": 13990000, "Battery_Cost": 0, "Notes": "Nova Luna"},
        {"Brand": "Daelim", "Model": "Nova", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 13990000, "Price_No_Battery": 13990000, "Price_With_Battery": 13990000, "Battery_Cost": 0, "Notes": "Nova Revo"},
        {"Brand": "Daelim", "Model": "Nova", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 13990000, "Price_No_Battery": 13990000, "Price_With_Battery": 13990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Daelim", "Model": "Nova", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 13990000, "Price_No_Battery": 13990000, "Price_With_Battery": 13990000, "Battery_Cost": 0, "Notes": "Duy trì giá"},

        # --- Tailg Series ---
        {"Brand": "Tailg", "Model": "Tailg Series", "Category": "Xe máy", "Year": 2023, "Price_Benchmark": 16840000, "Price_No_Battery": 16840000, "Price_With_Battery": 16840000, "Battery_Cost": 0, "Notes": "Tailg R60 / T61"},
        {"Brand": "Tailg", "Model": "Tailg Series", "Category": "Xe máy", "Year": 2024, "Price_Benchmark": 16840000, "Price_No_Battery": 16840000, "Price_With_Battery": 16840000, "Battery_Cost": 0, "Notes": "Tailg T72"},
        {"Brand": "Tailg", "Model": "Tailg Series", "Category": "Xe máy", "Year": 2025, "Price_Benchmark": 16840000, "Price_No_Battery": 16840000, "Price_With_Battery": 16840000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
        {"Brand": "Tailg", "Model": "Tailg Series", "Category": "Xe máy", "Year": 2026, "Price_Benchmark": 16840000, "Price_No_Battery": 16840000, "Price_With_Battery": 16840000, "Battery_Cost": 0, "Notes": "Duy trì giá"},
    ]

    df_timeline = pd.DataFrame(timeline_records)

    # 1. Lưu dạng Long Format (Tidy format để query và nạp Pipeline)
    os.makedirs("data/raw", exist_ok=True)
    long_path = "data/raw/ev_benchmark_timeline.csv"
    df_timeline.to_csv(long_path, index=False, encoding="utf-8-sig")
    print(f"[+] [1/2] Đã lưu bảng Long Format ({len(df_timeline)} dòng) tại: {long_path}")

    # 2. Tạo dạng Wide Format (Pivot Matrix Timeline để theo dõi dạng bảng Excel)
    df_pivot = df_timeline.pivot_table(
        index=['Brand', 'Model', 'Category'],
        columns='Year',
        values='Price_Benchmark'
    ).reset_index()

    # Format hiển thị số nguyên
    for col in df_pivot.columns:
        if isinstance(col, (int, float)):
            df_pivot[col] = df_pivot[col].fillna(0).astype('int64')

    wide_path = "data/raw/ev_benchmark_matrix.csv"
    df_pivot.to_csv(wide_path, index=False, encoding="utf-8-sig")
    print(f"[+] [2/2] Đã lưu bảng Ma trận Wide Format ({len(df_pivot)} models) tại: {wide_path}")

    print("\n--- XEM TRƯỚC MA TRẬN LỊCH SỬ GIÁ THEO NĂM (10 MODELS TIÊU BIỂU) ---")
    print(df_pivot.head(10).to_string())

    return df_timeline, df_pivot

if __name__ == "__main__":
    build_benchmark_timeline_data()
