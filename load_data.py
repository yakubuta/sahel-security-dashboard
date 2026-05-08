import pandas as pd
import os

# ── CONFIG ────────────────────────────────────────────────────────────────────
# Put the downloaded CSV filename here
CSV_FILE = "GEDEvent_v25_1.csv"   # change this to match your actual filename

# Countries we want
TARGET_COUNTRIES = ["Nigeria", "Niger", "Chad", "Cameroon"]

# Output path
os.makedirs("data/raw", exist_ok=True)

# ── LOAD & FILTER ─────────────────────────────────────────────────────────────
def load_and_filter():
    print(f"Loading {CSV_FILE}...")

    df = pd.read_csv(CSV_FILE, low_memory=False)
    print(f"Full dataset: {len(df)} rows")

    # Filter to Lake Chad Basin countries
    df = df[df["country"].isin(TARGET_COUNTRIES)]
    print(f"After filtering to Lake Chad Basin: {len(df)} rows")

    # Filter from 2015 onwards
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df[df["year"] >= 2015]
    print(f"After filtering from 2015: {len(df)} rows")

    return df


# ── SAVE ──────────────────────────────────────────────────────────────────────
def save(df):
    out = "data/raw/ucdp_lake_chad.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved to {out}")


# ── PREVIEW ───────────────────────────────────────────────────────────────────
def preview(df):
    print("\n── Columns ──")
    print(df.columns.tolist())

    print("\n── Sample ──")
    cols = ["date_start", "country", "adm_1", "dyad_name",
            "type_of_violence", "deaths_total", "latitude", "longitude"]
    available = [c for c in cols if c in df.columns]
    print(df[available].head(10).to_string())

    print("\n── Countries ──")
    print(df["country"].value_counts())

    print("\n── Violence Types ──")
    type_map = {1: "State-based", 2: "Non-state", 3: "One-sided (civilians)"}
    print(df["type_of_violence"].map(type_map).value_counts())

    print("\n── Total Deaths ──")
    print(f"{df['best'].sum():,} fatalities")

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    df = load_and_filter()
    save(df)
    preview(df)
