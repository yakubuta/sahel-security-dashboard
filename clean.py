import pandas as pd
import os

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_FILE  = "data/raw/ucdp_lake_chad.csv"
OUTPUT_FILE = "data/processed/ucdp_lake_chad_clean.csv"

os.makedirs("data/processed", exist_ok=True)

# ── LOAD ──────────────────────────────────────────────────────────────────────
def load(path):
    print(f"Loading {path}...")
    df = pd.read_csv(path, low_memory=False)
    print(f"Loaded {len(df)} rows\n")
    return df

# ── CLEAN ─────────────────────────────────────────────────────────────────────
def clean(df):

    # 1. Keep only columns we need
    keep = [
        "id", "year", "date_start", "country", "adm_1", "adm_2",
        "dyad_name", "side_a", "side_b",
        "type_of_violence", "conflict_name",
        "deaths_a", "deaths_b", "deaths_civilians", "deaths_unknown", "best",
        "latitude", "longitude", "where_description", "source_headline"
    ]
    df = df[[c for c in keep if c in df.columns]].copy()

    # 2. Rename columns to friendly names
    df.rename(columns={
        "best":              "deaths_total",
        "adm_1":             "state_province",
        "adm_2":             "district",
        "dyad_name":         "actors",
        "where_description": "location_name",
        "source_headline":   "headline",
        "conflict_name":     "conflict",
    }, inplace=True)

    # 3. Parse date
    df["date"] = pd.to_datetime(df["date_start"], errors="coerce")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%b")
    df["year_month"] = df["date"].dt.to_period("M").astype(str)
    df.drop(columns=["date_start"], inplace=True)

    # 4. Map violence type numbers to labels
    violence_map = {
        1: "State-based conflict",
        2: "Non-state conflict",
        3: "One-sided (civilians)",
    }
    df["violence_type"] = df["type_of_violence"].map(violence_map)
    df.drop(columns=["type_of_violence"], inplace=True)

    # 5. Fill missing death counts with 0
    death_cols = ["deaths_a", "deaths_b", "deaths_civilians",
                  "deaths_unknown", "deaths_total"]
    for col in death_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # 6. Drop rows with missing coordinates (can't map them)
    before = len(df)
    df = df.dropna(subset=["latitude", "longitude"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"Dropped {dropped} rows with missing coordinates")

    # 7. Drop rows with missing dates
    before = len(df)
    df = df.dropna(subset=["date"])
    dropped = before - len(df)
    if dropped > 0:
        print(f"Dropped {dropped} rows with missing dates")

    # 8. Add severity label based on deaths
    def severity(d):
        if d == 0:   return "No deaths recorded"
        if d <= 5:   return "Low (1–5)"
        if d <= 20:  return "Medium (6–20)"
        if d <= 50:  return "High (21–50)"
        return "Severe (50+)"

    df["severity"] = df["deaths_total"].apply(severity)

    # 9. Sort by date
    df = df.sort_values("date").reset_index(drop=True)

    return df

# ── SAVE ──────────────────────────────────────────────────────────────────────
def save(df, path):
    df.to_csv(path, index=False)
    print(f"Saved cleaned data to {path}")

# ── SUMMARY ───────────────────────────────────────────────────────────────────
def summary(df):
    print("\n═══════════════════════════════════════")
    print("         CLEAN DATA SUMMARY")
    print("═══════════════════════════════════════")

    print(f"\nTotal events   : {len(df):,}")
    print(f"Date range     : {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"Total deaths   : {df['deaths_total'].sum():,}")
    print(f"Civilian deaths: {df['deaths_civilians'].sum():,}")

    print("\n── Events by Country ──")
    print(df["country"].value_counts().to_string())

    print("\n── Events by Violence Type ──")
    print(df["violence_type"].value_counts().to_string())

    print("\n── Events by Severity ──")
    order = ["Severe (50+)", "High (21–50)", "Medium (6–20)",
             "Low (1–5)", "No deaths recorded"]
    sev = df["severity"].value_counts()
    for s in order:
        if s in sev:
            print(f"  {s}: {sev[s]:,}")

    print("\n── Top 10 Conflicts ──")
    print(df["conflict"].value_counts().head(10).to_string())

    print("\n── Top 10 Most Affected States/Provinces ──")
    print(df["state_province"].value_counts().head(10).to_string())

    print("\n── Columns in cleaned file ──")
    print(df.columns.tolist())

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== UCDP Lake Chad Basin — Data Cleaner ===\n")
    df = load(INPUT_FILE)
    df = clean(df)
    save(df, OUTPUT_FILE)
    summary(df)
    print("\nDone. Ready for dashboard.")
