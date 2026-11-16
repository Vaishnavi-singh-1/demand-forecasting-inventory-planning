"""
Step 0 - Create the dataset.

Generates 36 months (Jan 2023 - Dec 2025) of SIMULATED monthly unit sales for
15 SKUs of a packaging & shipping-supplies distributor. Each SKU has its own
base volume, growth trend, Q4 holiday-season peak and random noise, plus a unit
cost and supplier lead time used later for inventory planning.

The data is simulated (not real company data) - say so if asked in an interview.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)  # fixed seed -> same data every run

# sku, description, category, base monthly units, annual growth, seasonal strength, noise, unit cost $, lead time (weeks)
SKUS = [
    ("BOX-1210", "Corrugated Box 12x10x8",      "Corrugated Boxes", 5200, 0.08, 0.35, 0.08, 0.62, 3),
    ("BOX-1812", "Corrugated Box 18x12x12",     "Corrugated Boxes", 3100, 0.06, 0.30, 0.09, 1.05, 3),
    ("BOX-2420", "Heavy-Duty Box 24x20x20",     "Corrugated Boxes", 1400, 0.04, 0.25, 0.12, 2.40, 4),
    ("TAPE-2CL", "Packing Tape 2in Clear",      "Tape",             4600, 0.05, 0.30, 0.07, 1.15, 2),
    ("TAPE-3BR", "Carton Tape 3in Brown",       "Tape",             1800, 0.03, 0.20, 0.10, 1.60, 2),
    ("BUB-1224", "Bubble Roll 12in x 250ft",    "Protective Pkg",    950, 0.07, 0.40, 0.11, 18.50, 5),
    ("BUB-PCH",  "Bubble Pouch 6x8 (case)",     "Protective Pkg",    700, 0.10, 0.35, 0.13, 22.00, 5),
    ("FILM-18",  "Stretch Film 18in x 1500ft",  "Stretch Film",     2300, 0.02, 0.10, 0.08, 14.75, 4),
    ("FILM-HD",  "Hand Stretch Film 80ga",      "Stretch Film",      850, 0.01, 0.10, 0.12, 19.90, 4),
    ("MAIL-1013","Poly Mailer 10x13",           "Mailers",          6800, 0.12, 0.45, 0.09, 0.14, 3),
    ("MAIL-BUB", "Bubble Mailer #2",            "Mailers",          3900, 0.09, 0.40, 0.10, 0.32, 3),
    ("LBL-4X6",  "Thermal Shipping Label 4x6",  "Labels",           2600, 0.11, 0.30, 0.08, 9.80, 2),
    ("VOID-AIR", "Air Pillow Void Fill (case)", "Protective Pkg",    600, 0.05, 0.35, 0.15, 26.00, 6),
    ("PAL-4840", "Plastic Pallet 48x40",        "Warehouse",         180, 0.02, 0.05, 0.18, 89.00, 8),
    ("GLV-NIT",  "Nitrile Gloves (case)",       "Warehouse",         520, 0.00, 0.05, 0.14, 34.00, 6),
]

# Monthly seasonal shape for a shipping-supplies business:
# quiet Jan-Feb, steady mid-year, build-up in Sep-Oct, peak Nov-Dec (holiday shipping)
SEASON_SHAPE = np.array([-0.55, -0.45, -0.15, -0.10, -0.05, -0.10,
                         -0.15, -0.05,  0.15,  0.35,  0.55,  0.55])

dates = pd.date_range("2023-01-01", "2025-12-01", freq="MS")
rows = []
for sku, desc, cat, base, growth, seas, noise, cost, lt in SKUS:
    for t, d in enumerate(dates):
        trend = (1 + growth) ** (t / 12)
        season = 1 + seas * SEASON_SHAPE[d.month - 1]
        shock = rng.normal(1, noise)
        units = max(0, round(base * trend * season * shock))
        rows.append({"month": d.strftime("%Y-%m"), "sku": sku, "description": desc,
                     "category": cat, "units_sold": units, "unit_cost": cost,
                     "lead_time_weeks": lt})

df = pd.DataFrame(rows)
df.to_csv("data/packaging_sales_history.csv", index=False)
print(f"Saved {len(df)} rows ({df.sku.nunique()} SKUs x {df.month.nunique()} months) "
      f"to data/packaging_sales_history.csv")
