# ⚡ Electric Vehicle Market Monitor — Vietnam

> A data-driven research project that **crawls, cleans, and analyzes electric vehicle (EV) listings** across Vietnam's major online marketplaces to provide transparent, reproducible market intelligence for both researchers and individual car buyers.

---

## Table of Contents

- [Project Goal](#project-goal)
- [Architecture Overview](#architecture-overview)
- [Data Sources](#data-sources)
- [Directory Structure](#directory-structure)
- [Pipeline Stages](#pipeline-stages)
  - [1. Data Collection (Crawlers)](#1-data-collection-crawlers)
  - [2. Data Cleaning & Transformation](#2-data-cleaning--transformation)
  - [3. Benchmark & Reference Data](#3-benchmark--reference-data)
  - [4. Dataset Discovery & Profiling](#4-dataset-discovery--profiling)
  - [5. Exploratory Data Analysis (EDA)](#5-exploratory-data-analysis-eda)
- [Key Analysis Outputs](#key-analysis-outputs)
- [Tech Stack & Requirements](#tech-stack--requirements)
- [Getting Started](#getting-started)
- [Design Principles & Limitations](#design-principles--limitations)
- [License](#license)

---


## Project Goal

Monitor and analyze the **Vietnamese electric vehicle market** — focusing primarily on VinFast cars — by:

1. **Collecting** real-time listing data from C2C (Chợ Tốt) and B2C (Ô Tô Điện, Phố Xe Điện, Thế Giới Xe Điện) platforms
2. **Cleaning** raw data with PDPD-compliant anonymization, deduplication, and battery-status extraction
3. **Benchmarking** against official manufacturer prices (scraped directly from VinFast's product pages)
4. **Analyzing** supply composition, asking-price distributions, sales messaging patterns, and buyer-decision support (budget shortlisting, new-vs-used gaps, energy cost modeling)

The project is explicitly **descriptive** — it reports what is observed in listing samples, not market share, transaction prices, or demand inference.

---

## Architecture Overview

```
                 ┌──────────────────────────────────────────────┐
                 │              DATA SOURCES                    │
                 │  Chợ Tốt API · OtoDien · PhoXeDien ·        │
                 │  TheGioiXeDien · VinFast Official Pages      │
                 └────────────┬─────────────────────────────────┘
                              │
                 ┌────────────▼─────────────────────────────────┐
                 │         CRAWLERS (data/raw/)                 │
                 │  crawl_chotot.py    → JSON (cars + bikes)    │
                 │  crawl_otodien.py   → CSV (EV cars, B2C)    │
                 │  crawl_phoxedien.py → CSV (e-bikes, B2C)    │
                 │  crawl_thegioixedien.py → CSV (e-bikes)     │
                 │  crawl_each_page_otodien.py → JSON+HTML     │
                 │  scripts/crawl_vinfast_snapshot.py → JSON    │
                 │  scripts/collect_vinfast_references.py       │
                 └────────────┬─────────────────────────────────┘
                              │
                 ┌────────────▼─────────────────────────────────┐
                 │      CLEANING & TRANSFORMATION               │
                 │  data_processing.py → Anonymize, extract     │
                 │                       battery status          │
                 │  scripts/clean_chotot_oto.py → interim CSV   │
                 │  scripts/clean_chotot_xemay.py → interim CSV │
                 └────────────┬─────────────────────────────────┘
                              │
                 ┌────────────▼─────────────────────────────────┐
                 │      ANALYSIS & REPORTING                    │
                 │  discovery_report.py → Dataset profiling     │
                 │  create_benchmark.py → Official price table  │
                 │  scripts/build_eda_notebook.py → Notebook 01 │
                 │  scripts/build_buyer_eda.py → Notebook 02    │
                 └────────────┬─────────────────────────────────┘
                              │
                 ┌────────────▼─────────────────────────────────┐
                 │           OUTPUTS                            │
                 │  data visualization/ → Executed .ipynb        │
                 │  figures/            → 19 PNG charts          │
                 │  reports/            → dataset_discovery.md   │
                 │  data/processed/     → Cleaned CSV + buyer    │
                 │                        comparison tables      │
                 └──────────────────────────────────────────────┘
```

---

## Data Sources

| Source | Type | Method | Vehicle | Output |
|--------|------|--------|---------|--------|
| **Chợ Tốt** (chotot.com) | C2C marketplace | REST API (`gateway.chotot.com`) | Electric cars + motorbikes | `chotot_oto_raw.json`, `chotot_xemay_raw.json` |
| **Ô Tô Điện** (otodien.vn) | B2C dealership aggregator | HTML scraping (BeautifulSoup) + Playwright | Electric cars | `otodien_raw.csv` |
| **Phố Xe Điện** (phoxedien.com) | B2C e-commerce | HTML scraping (BeautifulSoup) | Electric motorbikes | `phoxedien_raw.csv` |
| **Thế Giới Xe Điện** (thegioixedien.com.vn) | B2C e-commerce | HTML scraping (BeautifulSoup) | Electric motorbikes | `thegioixedien_raw.csv` |
| **VinFast Official** (shop.vinfastauto.com) | OEM pricing | `urllib` + HTML text extraction | VF3/5/6/7/8/9 | `data/external/vinfast_*/` |
| **Chợ Tốt Snapshot** | C2C marketplace | REST API (timestamped) | VinFast cars only | `data/raw/snapshots/` |

---

## Directory Structure

```
Electric-Vehicle-Market-Monitor/
│
├── data/
│   ├── raw/                         # Untouched crawled data
│   │   ├── chotot_oto_raw.json      #   1,000 electric car listings (Chợ Tốt)
│   │   ├── chotot_xemay_raw.json    #   1,000 electric motorbike listings (Chợ Tốt)
│   │   ├── otodien_raw.csv          #   B2C electric car listings
│   │   ├── phoxedien_raw.csv        #   B2C electric motorbike listings
│   │   ├── thegioixedien_raw.csv    #   B2C electric motorbike listings
│   │   ├── ev_benchmark.csv         #   Hardcoded manufacturer benchmark prices
│   │   ├── ev_market_cleaned.csv    #   Legacy processed output (50 unique IDs)
│   │   └── snapshots/               #   Timestamped Chợ Tốt VinFast snapshots
│   │       └── 20260913T022632Z/
│   │
│   ├── interim/                     # Cleaned but not yet analysis-ready
│   │   ├── chotot_oto_clean.csv     #   Cleaned car listings
│   │   └── chotot_xemay_clean.csv   #   Cleaned motorbike listings
│   │
│   ├── processed/                   # Analysis-ready datasets
│   │   ├── ev_market_cleaned.csv    #   Main cleaned dataset
│   │   ├── benchmark_frame.csv      #   Benchmark reference frame
│   │   ├── ev_benchmark_matrix.csv  #   Benchmark comparison matrix
│   │   ├── ev_benchmark_timeline.csv
│   │   ├── final_benchmark.csv
│   │   ├── bonbanh_benchmark.csv
│   │   ├── chotot_models_dictionary.csv
│   │   └── buyer_eda/              #   Buyer-focused analysis outputs
│   │       ├── official_price_reference.csv
│   │       ├── screened_listings.csv
│   │       ├── manual_review_queue.csv
│   │       ├── buyer_comparison_candidates.csv
│   │       ├── buyer_price_summary_million_vnd.csv
│   │       ├── matched_new_used_gap.csv
│   │       └── observed_price_changes.csv
│   │
│   └── external/                    # Third-party reference data
│       └── vinfast_20260913T022514Z/
│           ├── VF3.html / VF3.txt   #   Official VinFast product pages
│           ├── VF5.html / VF5.txt
│           ├── VF6.html / VF6.txt
│           ├── VF7.html / VF7.txt
│           ├── VF8.html / VF8.txt
│           ├── VF9.html / VF9.txt
│           ├── chotot_probe.json
│           ├── otodien_probe.html / .txt
│           └── manifest.json
│
├── data visualization/              # Executed Jupyter notebooks
│   ├── 01_eda_vinfast_oto.ipynb     #   Supply, pricing, messaging EDA
│   └── 02_vinfast_buyer_eda.ipynb   #   Buyer decision-support EDA
│
├── figures/                         # Generated PNG charts (19 figures)
│   ├── 01_missingness.png
│   ├── 02_car_model.png
│   ├── 02_car_region.png
│   ├── 02_car_condition.png
│   ├── 02_car_year.png
│   ├── 02_car_region_model.png
│   ├── 03_car_price_distribution.png
│   ├── 03_car_model_prices.png
│   ├── 03_car_price_odo.png
│   ├── 04_car_messages.png
│   ├── buyer_01_screening.png
│   ├── buyer_02_budget.png
│   ├── buyer_03_matched_gap.png
│   ├── buyer_04_official_context.png
│   ├── buyer_05_seller_sensitivity.png
│   ├── buyer_06_battery_terms.png
│   ├── buyer_07_energy_scenario.png
│   └── buyer_08_used_odo.png
│
├── notebooks/                       # Standalone analysis notebooks
│   └── 01_profile_chotot.ipynb
│
├── reports/                         # Generated Markdown reports
│   └── dataset_discovery.md         #   81 KB field-level dataset profile
│
├── scripts/                         # Utility & analysis scripts
│   ├── build_eda_notebook.py        #   Generates & executes Notebook 01
│   ├── build_buyer_eda.py           #   Generates & executes Notebook 02
│   ├── clean_chotot_oto.py          #   JSON → clean CSV (cars)
│   ├── clean_chotot_xemay.py        #   JSON → clean CSV (motorbikes)
│   ├── collect_vinfast_references.py #  Fetch official VinFast pricing pages
│   ├── crawl_vinfast_snapshot.py    #   Timestamped Chợ Tốt VinFast snapshot
│   └── list_features.py            #   List all fields in raw JSON files
│
├── crawl_chotot.py                  # Chợ Tốt API crawler (cars + motorbikes)
├── crawl_otodien.py                 # Ô Tô Điện HTML scraper
├── crawl_each_page_otodien.py       # Playwright-based article scraper
├── crawl_phoxedien.py               # Phố Xe Điện HTML scraper
├── crawl_thegioixedien.py           # Thế Giới Xe Điện HTML scraper
├── create_benchmark.py              # Generate manufacturer benchmark CSV
├── data_processing.py               # Main data transformation pipeline
├── discovery_report.py              # Automated dataset profiling report
│
├── requirements.txt                 # Core dependencies (crawling)
├── requirements-eda.txt             # EDA/analysis dependencies
├── .gitignore
└── README.md
```

---

## Pipeline Stages

### 1. Data Collection (Crawlers)

| Script | Target | Technique | Key Features |
|--------|--------|-----------|--------------|
| `crawl_chotot.py` | Chợ Tốt API | Paginated JSON API | Electric cars (`fuel=4`) and motorbikes (`motorbiketype=4`); 2s rate limiting |
| `crawl_otodien.py` | otodien.vn | BeautifulSoup HTML | Vietnamese price parsing (`triệu`/`tỷ` → VND integer); dedup filter |
| `crawl_each_page_otodien.py` | otodien.vn articles | Playwright (headless Chromium) | Intercepts API responses + JSON-LD structured data |
| `crawl_phoxedien.py` | phoxedien.com | BeautifulSoup HTML | Electric motorbike catalog; WooCommerce `<bdi>` tags |
| `crawl_thegioixedien.py` | thegioixedien.com.vn | BeautifulSoup HTML | `gia_ban` CSS class; 5-page default depth |
| `scripts/crawl_vinfast_snapshot.py` | Chợ Tốt API | Paginated JSON (timestamped) | National VinFast snapshot; stops on duplicate IDs |
| `scripts/collect_vinfast_references.py` | VinFast official site | `urllib` + HTML→text | SHA-256 integrity hashing; manifest with retrieval timestamps |

### 2. Data Cleaning & Transformation

| Script | Input → Output | Key Operations |
|--------|---------------|----------------|
| `data_processing.py` | `raw/ev_raw.json` → `processed/ev_market_cleaned.csv` | PDPD anonymization (phone numbers, addresses); battery status extraction from keywords (`thuê pin` / `kèm pin`); column selection |
| `scripts/clean_chotot_oto.py` | `raw/chotot_oto_raw.json` → `interim/chotot_oto_clean.csv` | Field remapping (50+ fields); epoch→datetime; null/single-value column pruning; dedup on `ad_id` |
| `scripts/clean_chotot_xemay.py` | `raw/chotot_xemay_raw.json` → `interim/chotot_xemay_clean.csv` | Same approach as car cleaner; motorbike-specific fields (brand/model codes, engine type, capacity) |

### 3. Benchmark & Reference Data

| Script | Purpose | Output |
|--------|---------|--------|
| `create_benchmark.py` | Hardcoded VinFast official prices (with/without battery) | `data/raw/ev_benchmark.csv` |
| `scripts/collect_vinfast_references.py` | Live-fetched VF3–VF9 pricing pages with SHA-256 hashes | `data/external/vinfast_*/manifest.json` + HTML/TXT snapshots |

### 4. Dataset Discovery & Profiling

`discovery_report.py` performs automated, zero-mutation profiling of all files under `data/raw/` and `data/processed/`:

- **Field identification** with semantic role mapping and confidence levels
- **Type inference** (CSV text → numeric, JSON native types)
- **Coverage statistics** (nonempty counts, distinct values, first examples)
- **Embedded lookup extraction** (brand/model code → name mappings from Chợ Tốt data)
- **Three complete sample records** per file
- **SHA-256 integrity assertion** before and after analysis

Output: `reports/dataset_discovery.md` (81 KB, 1,342 lines)

### 5. Exploratory Data Analysis (EDA)

Two programmatically-generated Jupyter notebooks provide the analytical backbone:

#### Notebook 01 — Supply & Pricing EDA (`build_eda_notebook.py`)

**Scope:** VinFast cars on Chợ Tốt only (filters `carbrand_name == VinFast`)

| Section | Analysis | Charts |
|---------|----------|--------|
| **1. Data Quality** | Missingness heatmap; outlier flags (IQR); low-price inspection; dedup audit | `01_missingness.png` |
| **2. Supply Composition** | Model distribution; new/used split; regional heatmap; year distribution | `02_car_model.png`, `02_car_region.png`, `02_car_condition.png`, `02_car_year.png`, `02_car_region_model.png` |
| **3. Asking Prices** | Linear + log histograms; boxplots by model (≥10 obs); price vs. ODO scatter | `03_car_price_distribution.png`, `03_car_model_prices.png`, `03_car_price_odo.png` |
| **4. Sales Messaging** | Keyword regex (battery, financing, promotions, trade-in, warranty); overlap audit | `04_car_messages.png` |

#### Notebook 02 — Buyer Decision Support (`build_buyer_eda.py`)

**Scope:** VinFast cars with auditable screening (ICE models, service ads, price anomalies flagged and isolated)

| Section | Analysis | Charts |
|---------|----------|--------|
| **A. Improvement matrix** | P0–P2 buyer questions mapped to data gaps | — |
| **B. Screening** | Rule-based scope/price screening; manual review queue; fresh-vs-legacy cohort | `buyer_01_screening.png` |
| **C. Budget shortlist** | Budget × model × condition matrix (≥10 listings threshold) | `buyer_02_budget.png` |
| **D. New vs. Used gap** | Matched comparison (family/year/region); seller-cluster bootstrap (300×, 90% CI) | `buyer_03_matched_gap.png` |
| **E. Official price context** | Variant-range bars vs. listing median; 12 configurations from 6 VinFast product pages | `buyer_04_official_context.png` |
| **F. Seller sensitivity** | Listing-weighted vs. seller-balanced median; threshold sensitivity (50/100/150M VND) | `buyer_05_seller_sensitivity.png` |
| **G. Battery & financing terms** | Keyword frequency; pin mua/thuê overlap detection | `buyer_06_battery_terms.png` |
| **H. Energy cost model** | VF5 scenario (13 kWh/100 km × multiplier); EV vs. ICE at 3 electricity tariffs | `buyer_07_energy_scenario.png` |
| **I. Comparison candidates** | Peer-group placement (P25/IQR/P75); exportable CSV for buyer shortlisting | `buyer_08_used_odo.png` |

---

## Key Analysis Outputs

| File | Description |
|------|-------------|
| `data/processed/buyer_eda/screened_listings.csv` | All listings with scope/price eligibility flags |
| `data/processed/buyer_eda/official_price_reference.csv` | 12 VinFast variant configurations with promo/listed prices and source URLs |
| `data/processed/buyer_eda/buyer_comparison_candidates.csv` | Listings with peer-group statistics for buyer comparison |
| `data/processed/buyer_eda/matched_new_used_gap.csv` | New-vs-used asking-price gaps with bootstrap confidence intervals |
| `data/processed/buyer_eda/manual_review_queue.csv` | Flagged listings requiring manual verification |
| `reports/dataset_discovery.md` | Comprehensive field-level profiling of all datasets |

---

## Tech Stack & Requirements

### Core (Crawling & Processing)

```
requests
beautifulsoup4
pandas
```

Install: `pip install -r requirements.txt`

### EDA & Visualization

```
pandas>=2.2
numpy>=1.26
matplotlib>=3.9
nbformat>=5.10
nbclient>=0.10
ipykernel>=6.29
```

Install: `pip install -r requirements-eda.txt`

### Optional

- **Playwright** — required for `crawl_each_page_otodien.py` (headless Chromium article scraping)

---

## Getting Started

### 1. Clone & Setup

```bash
git clone https://github.com/van2703/Electric-Vehicle-Market-Monitor.git
cd Electric-Vehicle-Market-Monitor
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-eda.txt
```

### 2. Crawl Data

```bash
# C2C marketplace (Chợ Tốt)
python crawl_chotot.py

# B2C sources
python crawl_otodien.py
python crawl_phoxedien.py
python crawl_thegioixedien.py

# Official prices & timestamped snapshot
python scripts/collect_vinfast_references.py
python scripts/crawl_vinfast_snapshot.py

# Benchmark table
python create_benchmark.py
```

### 3. Clean Data

```bash
# JSON → cleaned CSV
python scripts/clean_chotot_oto.py
python scripts/clean_chotot_xemay.py

# Main processing pipeline
python data_processing.py
```

### 4. Profile & Discover

```bash
python discovery_report.py          # → reports/dataset_discovery.md
python scripts/list_features.py     # → terminal field listing
```

### 5. Run Analysis

```bash
# Generate + execute EDA notebooks
python scripts/build_eda_notebook.py    # → data visualization/01_eda_vinfast_oto.ipynb
python scripts/build_buyer_eda.py       # → data visualization/02_vinfast_buyer_eda.ipynb
```

All figures are saved to `figures/`. Notebooks are self-contained and can be re-run from the repository root.

---

## Design Principles & Limitations

### Principles

- **No source mutation** — all scripts verify SHA-256 hashes of input files before and after processing
- **Reproducibility** — notebooks are programmatically generated with fixed random seeds (`seed=42`) and explicit screening rules
- **Transparency** — every filtering decision, keyword pattern, and screening threshold is documented inline
- **PDPD compliance** — personal information (phone numbers, addresses) is anonymized during processing
- **Separation of cohorts** — B2C sources and benchmarks are never mixed with C2C data for statistical comparisons

### Limitations

- **Not representative** — data is a convenience sample of active listings, not a census of the Vietnamese EV market
- **Asking prices only** — no transaction prices, no confirmed sales
- **No time series** — lacks recurring snapshots for trend analysis (only one timestamped snapshot exists)
- **Model labels are user-generated** — brand/model names come from seller-selected categories, not verified vehicle specs
- **Battery status is inferred** — keyword-based classification, not verified inspection
- **No TCO analysis** — energy cost models cover fuel only, excluding purchase price delta, insurance, maintenance, and resale value

---

## License

This project is for research and educational purposes. Data is sourced from publicly accessible listings and official manufacturer pages. No personal information is stored or distributed.
