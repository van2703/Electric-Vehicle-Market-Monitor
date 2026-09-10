import pandas as pd
import os

def create_benchmark_data():
    print("=== TẠO DỮ LIỆU NGUỒN 3: BẢNG GIÁ HÃNG (BENCHMARK) ===")
    
    # Dữ liệu Ground Truth: Giá niêm yết chính hãng (VNĐ)
    benchmark_data = [
        # --- XE MÁY ĐIỆN ---
        {"Brand": "VinFast", "Model": "Evo200", "Price_No_Battery": 18000000, "Price_With_Battery": 37900000, "Battery_Cost": 19900000},
        {"Brand": "VinFast", "Model": "Feliz S", "Price_No_Battery": 27000000, "Price_With_Battery": 46900000, "Battery_Cost": 19900000},
        {"Brand": "VinFast", "Model": "Klara S (2022)", "Price_No_Battery": 35000000, "Price_With_Battery": 54900000, "Battery_Cost": 19900000},
        {"Brand": "Dat Bike", "Model": "Weaver++", "Price_No_Battery": 65900000, "Price_With_Battery": 65900000, "Battery_Cost": 0}, # Dat Bike mặc định kèm pin
        
        # --- Ô TÔ ĐIỆN ---
        {"Brand": "VinFast", "Model": "VF 5 Plus", "Price_No_Battery": 468000000, "Price_With_Battery": 548000000, "Battery_Cost": 80000000},
        {"Brand": "VinFast", "Model": "VF e34", "Price_No_Battery": 710000000, "Price_With_Battery": 830000000, "Battery_Cost": 120000000},
        {"Brand": "VinFast", "Model": "VF 8 Eco", "Price_No_Battery": 1090000000, "Price_With_Battery": 1290000000, "Battery_Cost": 200000000},
        {"Brand": "VinFast", "Model": "VF 8 Plus", "Price_No_Battery": 1270000000, "Price_With_Battery": 1470000000, "Battery_Cost": 200000000}
    ]
    
    df_benchmark = pd.DataFrame(benchmark_data)
    
    os.makedirs("data/raw", exist_ok=True)
    file_path = "data/raw/ev_benchmark.csv"
    df_benchmark.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    print(f"[+] XONG! Đã tạo thành công {len(benchmark_data)} dòng dữ liệu Benchmark.")
    print(f"[*] File lưu tại: {file_path}")
    print("\n--- XEM TRƯỚC 5 DÒNG BENCHMARK ---")
    print(df_benchmark.head())

if __name__ == "__main__":
    create_benchmark_data()