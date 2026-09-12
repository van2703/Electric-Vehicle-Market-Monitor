"""
Liệt kê toàn bộ field có trong file JSON crawl từ Chợ Tốt (Xe máy & Ô tô).
Chạy: python scripts/cleaning/list_features.py
"""
import json
from pathlib import Path
from collections import Counter
import sys

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def list_fields(json_path: Path) -> None:
    if not json_path.exists():
        print(f"[-] Không tìm thấy file: {json_path}")
        return

    with open(json_path, encoding="utf-8") as f:
        records = json.load(f)

    print("\n" + "=" * 80)
    print(f"File: {json_path.name}")
    print(f"Số record: {len(records)}")
    print("=" * 80)

    # Union toàn bộ key
    counter = Counter()
    for r in records:
        if isinstance(r, dict):
            counter.update(r.keys())

    print(f"\nTổng số field duy nhất: {len(counter)}\n")
    print(f"{'Field':<35} {'Coverage':>12}   {'Kiểu':<10}")
    print("-" * 65)

    # Lấy kiểu dữ liệu từ record đầu tiên có field đó
    for field, count in sorted(counter.items()):
        # Tìm record đầu tiên có field này
        sample = None
        for r in records:
            if field in r:
                sample = r[field]
                break
        dtype = type(sample).__name__ if sample is not None else "?"
        print(f"{field:<35} {count:>5}/{len(records):<6}   {dtype:<10}")

    # Field chỉ xuất hiện ở một số record
    partial = {k: v for k, v in counter.items() if v < len(records)}
    if partial:
        print(f"\n--- Field không phủ 100% ({len(partial)} field) ---")
        for k, v in sorted(partial.items(), key=lambda x: -x[1]):
            print(f"  {k:<35} {v:>5}/{len(records)}")


if __name__ == "__main__":
    RAW = Path(__file__).resolve().parents[2] / "data" / "raw" / "c2c"
    list_fields(RAW / "chotot_xemay_raw.json")
    list_fields(RAW / "chotot_oto_raw.json")