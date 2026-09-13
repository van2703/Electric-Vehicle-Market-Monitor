import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
paths = sorted(p for folder in ('data/raw', 'data/processed') for p in (ROOT / folder).rglob('*') if p.is_file())
hashes = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
out = ['# Dataset discovery — no source changes', '', 'All files under data/raw/ and data/processed/ were read recursively. Counts exclude CSV headers. Samples are the first three records in source order, with every field and value retained. CSV values are physically text; inferred numeric types below describe parseability, not a source schema. JSON types are native. Empty means missing, null, or empty string (empty arrays remain arrays). Confidence concerns field meaning, not seller accuracy.', '']
summary = []

def cell(v):
    return str(v).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ')

def dtype(values, is_csv):
    vals = [v for v in values if v is not None and v != '']
    if not vals:
        return 'empty'
    if not is_csv:
        return ', '.join(f'{k}: {v}' for k, v in Counter(type(x).__name__ for x in vals).items())
    try:
        nums = [float(v) for v in vals]
        return 'text → integer-valued numeric' if all(n.is_integer() for n in nums) else 'text → numeric'
    except ValueError:
        return 'text'

for p in paths:
    rel = p.relative_to(ROOT).as_posix()
    is_csv = p.suffix.lower() == '.csv'
    if is_csv:
        with p.open(encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            keys = reader.fieldnames
            rows = list(reader)
        structure = 'CSV header: ' + ', '.join(f'`{k}`' for k in keys)
    else:
        data = json.loads(p.read_text(encoding='utf-8-sig'))
        assert isinstance(data, list) and all(isinstance(r, dict) for r in data)
        rows = data
        keys = list(dict.fromkeys(k for row in rows for k in row))
        structure = 'Top level: array of objects (no root object keys).\n\nFirst object keys: ' + ', '.join(f'`{k}`' for k in rows[0])
        structure += '\n\nFull union of keys across all records: ' + ', '.join(f'`{k}`' for k in keys)
    mappings = []
    def add(meaning, fields, confidence, reason):
        mappings.append((meaning, fields, confidence, reason))
    if not is_csv:
        car = 'carbrand' in keys
        role = 'Raw listings — cars' if car else 'Raw listings — motorbikes'
        add('Listing ID', 'list_id; ad_id (alternate)', 'high', 'Both are integer identifiers, nonempty and individually unique in all 1,000 records. account_id repeats across ads and identifies a seller instead; product_id is not the listing key.')
        add('Price', 'price; price_string', 'high', 'Integer amounts match formatted amounts ending in đ, supporting VND asking prices; is_price_not_valid is a separate validity flag. Prices are seller-entered, not verified transaction prices.')
        add('Brand', 'carbrand → carbrand_name' if car else 'motorbikebrand', 'high', 'Repeated integer categories with paired explicit names such as 80 → VinFast.' if car else 'Repeated integer categories (52 distinct) and the motorbikebrand name identify brand codes. No structured brand-name field is present; names cannot be resolved from this file alone.')
        add('Model', 'carmodel → carmodel_name' if car else 'motorbikemodel', 'high', 'Integer categories paired with names such as 1112 → VF8. Use the brand/model code pair for a scoped lookup.' if car else 'Repeated integer categories (155 distinct) and motorbikemodel identify model codes. No model-name field or dictionary is present; no title/body parsing was performed.')
        add('Registration/manufacturing year', 'mfdate' if car else 'regdate', 'high' if car else 'medium', 'Four-digit integer years such as 2024/2026 and mfdate indicate manufacturing year.' if car else 'Four-digit integer years such as 2025/2026 indicate vehicle year. regdate suggests registration year, but the distinction from manufacture/model year is not established by values alone.')
        add('Mileage/ODO', 'mileage_v2; mileage', 'high / medium', 'mileage_v2 contains kilometer-like integer odometer values, corroborated by sample descriptions (42000 vs 4.2 vạn in cars; 900 vs 900km in motorbikes). mileage instead has a small discrete value set and likely encodes legacy mileage bands; do not interpret it as kilometers without a dictionary.')
        add('Region/location', 'region_name, region_name_v3, region, region_v2; area_name, area, area_v2; ward_name, ward_name_v3, ward; latitude, longitude, location; detail_address', 'high / medium', 'Names show province/city, district/local city, and ward levels; numeric siblings are location codes. Coordinates are floating-point degrees and location is a comma-separated coordinate string. *_v3 names appear to use a different administrative version (e.g. old province names consolidated into TP Hồ Chí Minh); version semantics remain medium confidence. shop.address is a shop address, not necessarily the vehicle location.')
        stamp = rows[0]['list_time']
        add('Listing date/time', 'list_time; orig_list_time; date', 'high / medium', f'13-digit integers behave as Unix milliseconds: {stamp} → {datetime.fromtimestamp(stamp / 1000, timezone.utc).isoformat()}. orig_list_time suggests original publication; list_time could reflect publication/refresh (exact event medium). date contains relative text such as minutes ago, not an absolute date. Nested shop creation/modification timestamps describe shops, not ads.')
        add('Title/description', 'subject; body', 'high', 'subject contains short ad headlines; body contains longer seller prose and line breaks.')
    elif 'Brand' in keys:
        role = 'Benchmark'
        add('Listing ID', 'absent', 'high', 'No listing identifier; Model is unique across these eight reference rows, but is a product label, not a listing ID.')
        add('Price', 'Price_No_Battery; Price_With_Battery; Battery_Cost', 'high / medium', 'Integer-like numeric text and explicit column names distinguish price configurations and battery cost. VND is likely from dataset context, but the file has no currency column (medium). No effective date is supplied.')
        add('Brand', 'Brand', 'high', 'Explicit names include VinFast and Dat Bike.')
        add('Model', 'Model', 'high', 'Product names include Evo200, Feliz S, and Klara S (2022). This is a name-based benchmark, not numeric-code decoding.')
        for meaning in ('Registration/manufacturing year', 'Mileage/ODO', 'Region/location', 'Listing date/time', 'Title/description'):
            add(meaning, 'absent as a dedicated field', 'high', 'No matching column. A year embedded in a model label is not an independently defined registration/manufacturing field.' if 'year' in meaning else 'The complete five-column schema contains only brand, model, and price/battery benchmarks.')
    elif 'list_id' in keys:
        role = 'Processed listings'
        add('Listing ID', 'list_id', 'high', 'Integer-like identifiers, but only 50 distinct values among 1,000 rows. It denotes a listing, not a unique physical row in this file.')
        add('Price', 'price', 'high / medium', 'Integer-like amounts such as 20000000 suggest asking prices; VND is likely from context but not explicitly declared in this CSV (medium).')
        for meaning in ('Brand', 'Model'):
            add(meaning, 'absent as a dedicated field', 'high', 'Some names occur in subject/body, but there is no structured name or numeric code column; none was inferred from prose.')
        add('Registration/manufacturing year', 'regdate', 'medium', 'Four-digit numeric text such as 2024 indicates vehicle year; registration versus manufacturing meaning cannot be proven from this CSV.')
        add('Mileage/ODO', 'mileage_v2', 'high', 'Integer-valued decimal text such as 11000.0 matches the sample title 11000 km. 76 rows are blank.')
        add('Region/location', 'region_name; area_name', 'high', 'Values such as Tp Hồ Chí Minh and Thành phố Thủ Đức indicate province/city and subprovincial location respectively.')
        add('Listing date/time', 'absent', 'high', 'No absolute timestamp or relative posting-date field; regdate is vehicle year.')
        add('Title/description', 'subject; body; body_clean', 'high', 'Short headlines and longer prose; body_clean appears to be a processed description, though the exact cleaning method is not encoded in the file.')
    else:
        role = 'B2C reference — cars' if p.stem == 'otodien_raw' else 'B2C reference — electric two-wheelers'
        add('Listing ID', 'absent', 'high', 'source is constant, not a row identifier. subject is a product/ad title and is not a reliable stable listing key, even where unique.')
        add('Price', 'price_raw; price_clean' if 'price_clean' in keys else 'price_raw', 'high', 'Currency-formatted strings use triệu (millions), ₫, or đ; where price_clean exists, 630 triệu corresponds to 630000000, supporting numeric VND. No parsing or changes were applied.')
        for meaning in ('Brand', 'Model', 'Registration/manufacturing year', 'Mileage/ODO'):
            add(meaning, 'absent as a dedicated field', 'high', 'Product/vehicle details may occur in subject, but there is no dedicated field or code. No extraction from free text was performed.')
        for meaning in ('Region/location', 'Listing date/time'):
            add(meaning, 'absent', 'high', 'No corresponding column in the complete schema.')
        add('Title/description', 'subject (title only)', 'high', 'Human-readable product/ad headlines; no body/long-description column. source values explicitly end in _B2C, supporting the role classification.')
    summary.append((rel, role, '; '.join(f'{m}: {f} [{c}]' for m, f, c, r in mappings if not f.startswith('absent')), 'high for role; field-specific confidence below'))
    out += [f'## {rel}', '', f'Format: **{p.suffix[1:]}**. Rows/records: **{len(rows):,}**. Fields (union): **{len(keys)}**.', '', structure, '', '### Field identification', '', '| Semantic meaning | Candidate field(s) | Confidence | Evidence / limitation |', '|---|---|---|---|']
    out += ['| ' + ' | '.join(cell(x) for x in m) + ' |' for m in mappings]
    out += ['', '### Field profile (all records)', '', '| Field | Observed/inferred type | Nonempty | Distinct nonempty | First nonempty example (up to 160 characters) |', '|---|---|---:|---:|---|']
    for k in keys:
        vals = [r.get(k) for r in rows]
        present = [v for v in vals if v is not None and v != '']
        unique = len({json.dumps(v, sort_keys=True, ensure_ascii=False) for v in present})
        ex = json.dumps(present[0], ensure_ascii=False) if present else ''
        out.append('| ' + ' | '.join(cell(x) for x in (k, dtype(vals, is_csv), len(present), unique, ex[:160])) + ' |')
    if p.stem == 'chotot_oto_raw':
        out += ['', '### Embedded code/name lookup structure', '', 'This is a listing file with embedded mappings, not a standalone dictionary. Observed pairs cover this sample only; car mappings must not be reused for motorbike codes. To look up brand b, match carbrand=b and read carbrand_name. For model m within b, match (carbrand, carmodel)=(b,m) and read carmodel_name.', '']
        for fields in (('carbrand', 'carbrand_name'), ('carbrand', 'carmodel', 'carmodel_name')):
            observed = defaultdict(set)
            for r in rows:
                observed[tuple(r[k] for k in fields[:-1])].add(r[fields[-1]])
            conflicts = sum(len(v) > 1 for v in observed.values())
            out += [f'Lookup `{fields}`: {len(observed)} observed keys; {conflicts} keys with conflicting names.', '', '| ' + ' | '.join(fields) + ' |', '|' + '|'.join('---' for _ in fields) + '|']
            out += ['| ' + ' | '.join(cell(x) for x in (*k, ', '.join(sorted(v)))) + ' |' for k, v in sorted(observed.items())]
    if p.stem == 'ev_benchmark':
        out += ['', '### Reference lookup structure', '', 'Match exact (Brand, Model) text to read Price_No_Battery, Price_With_Battery, and Battery_Cost. All eight pairs are unique. No numeric brand/model codes are present, so this cannot decode motorbikebrand/motorbikemodel.']
    out += ['', '### Three complete sample records', '', 'CSV samples below retain text storage; JSON samples retain native types. No fields or long values are omitted.', '', '```json', json.dumps(rows[:3], ensure_ascii=False, indent=2), '```', '']

header = ['## Summary', '', '| File | Likely role | Key fields found (confidence for each guess) | Role confidence |', '|---|---|---|---|']
header += ['| ' + ' | '.join(cell(x) for x in row) + ' |' for row in summary]
header += ['', 'No standalone numeric code dictionary was found. The benchmark is a product-price reference. The car JSON has embedded code/name pairs; the motorbike JSON does not have equivalent name fields. Source records have not been deduplicated, joined, standardized, or changed.', '']
out[4:4] = header
assert all(hashlib.sha256(p.read_bytes()).hexdigest() == hashes[p] for p in paths)
out += ['Source integrity check: SHA-256 hashes of all seven input files were unchanged before versus after discovery.', '']
dest = ROOT / 'reports' / 'dataset_discovery.md'
dest.parent.mkdir(exist_ok=True)
dest.write_text('\n'.join(out), encoding='utf-8')
print(f'Report: {dest}; {dest.stat().st_size:,} bytes; {len(paths)} files; 3 complete samples each. Source hashes unchanged.')
