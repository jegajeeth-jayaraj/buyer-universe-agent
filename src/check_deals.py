"""Check data/deals.csv against the dataset rules in docs/PROJECT_BRIEF.md.

Reports problems only; it never changes the file.
Run from anywhere: python src/check_deals.py
"""

from pathlib import Path

import pandas as pd

DEALS_PATH = Path(__file__).resolve().parent.parent / "data" / "deals.csv"

EXPECTED_COLUMNS = [
    "deal_id", "target_name", "target_anon_description", "sector", "sub_sector",
    "target_revenue_gbp_m", "target_ebitda_gbp_m", "financials_source_url",
    "announce_date", "acquirer_name", "acquirer_type", "acquirer_country",
    "ev_gbp_m", "ev_ebitda", "source_url", "post_cutoff", "model_knows_answer", "notes",
]

# Allowed values per column. "" means the cell may be left blank.
ALLOWED_VALUES = {
    "acquirer_type": {"Strategic", "PE", "Other"},
    "acquirer_country": {"UK", "US", "EU", "Other"},
    "post_cutoff": {"Yes", "No", ""},
    "model_knows_answer": {"Yes", "No", ""},
}

MAX_DEALS_PER_SECTOR = 5
EV_MIN_GBP_M, EV_MAX_GBP_M = 20, 2000


def row_label(df: pd.DataFrame, i: int) -> str:
    """Name a row by its deal_id and its line number in the CSV (header is line 1)."""
    deal_id = df.at[i, "deal_id"] if "deal_id" in df.columns else ""
    return f"line {i + 2} ({deal_id or 'no deal_id'})"


def load_deals(path: Path) -> pd.DataFrame | None:
    """Read the CSV as plain text so nothing is silently converted; None if unreadable."""
    if not path.exists():
        print(f"File not found: {path}")
        return None
    try:
        # dtype=str and keep_default_na=False keep every cell as text, with blanks as "".
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        print(f"{path.name} is completely empty (not even a header row).")
        return None
    # Ignore stray spaces around values, e.g. "PE " typed by mistake.
    return df.apply(lambda col: col.str.strip())


def check_columns(df: pd.DataFrame) -> int:
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    unexpected = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    for c in missing:
        print(f"  MISSING column: {c}")
    for c in unexpected:
        print(f"  UNEXPECTED column: {c}")
    if not missing and not unexpected:
        print("  OK: all 18 expected columns present, none extra")
    return len(missing) + len(unexpected)


def check_sources(df: pd.DataFrame) -> int:
    issues = 0
    for col in ["source_url", "financials_source_url"]:
        if col not in df.columns:
            continue
        for i in df.index[df[col] == ""]:
            print(f"  {row_label(df, i)}: empty {col}")
            issues += 1
    if issues == 0:
        print("  OK: every row has both source URLs")
    return issues


def check_allowed_values(df: pd.DataFrame) -> int:
    issues = 0
    for col, allowed in ALLOWED_VALUES.items():
        if col not in df.columns:
            continue
        for i in df.index[~df[col].isin(allowed)]:
            shown = df.at[i, col] or "(blank)"
            options = ", ".join(sorted(v or "blank" for v in allowed))
            print(f"  {row_label(df, i)}: {col} = '{shown}', must be one of: {options}")
            issues += 1
    if issues == 0:
        print("  OK: all controlled columns use allowed values")
    return issues


def check_dates(df: pd.DataFrame) -> int:
    if "announce_date" not in df.columns:
        return 0
    # format= makes pandas reject anything that isn't YYYY-MM-DD; errors="coerce"
    # turns bad or impossible dates (e.g. 2025-02-30) into NaT instead of crashing.
    parsed = pd.to_datetime(df["announce_date"], format="%Y-%m-%d", errors="coerce")
    bad = df.index[parsed.isna()]
    for i in bad:
        shown = df.at[i, "announce_date"] or "(blank)"
        print(f"  {row_label(df, i)}: announce_date '{shown}' is not a valid YYYY-MM-DD date")
    if len(bad) == 0:
        print("  OK: all announce_date values are valid ISO dates")
    return len(bad)


def check_sectors(df: pd.DataFrame) -> int:
    if "sector" not in df.columns:
        return 0
    counts = df["sector"].replace("", "(blank)").value_counts()
    issues = 0
    for sector, n in counts.items():
        flag = f"  <-- more than {MAX_DEALS_PER_SECTOR}" if n > MAX_DEALS_PER_SECTOR else ""
        print(f"  {sector}: {n}{flag}")
        issues += bool(flag)
    return issues


def report_buyer_split(df: pd.DataFrame) -> None:
    """Informational only: the brief aims for roughly 50/50 Strategic vs PE."""
    if "acquirer_type" not in df.columns:
        return
    total = len(df)
    for buyer_type in ["Strategic", "PE", "Other"]:
        n = (df["acquirer_type"] == buyer_type).sum()
        print(f"  {buyer_type}: {n} ({n / total:.0%})")


def check_deal_size(df: pd.DataFrame) -> int:
    if "ev_gbp_m" not in df.columns:
        return 0
    issues = 0
    ev = pd.to_numeric(df["ev_gbp_m"], errors="coerce")
    for i in df.index:
        raw = df.at[i, "ev_gbp_m"]
        if raw == "":
            continue  # EV is often undisclosed; blank is allowed
        if pd.isna(ev[i]):
            print(f"  {row_label(df, i)}: ev_gbp_m '{raw}' is not a number")
            issues += 1
        elif not EV_MIN_GBP_M <= ev[i] <= EV_MAX_GBP_M:
            print(f"  {row_label(df, i)}: ev_gbp_m {ev[i]:g} is outside "
                  f"{EV_MIN_GBP_M}-{EV_MAX_GBP_M} (flag only; check it belongs)")
            issues += 1
    if issues == 0:
        print(f"  OK: every disclosed EV is between £{EV_MIN_GBP_M}m and £{EV_MAX_GBP_M}m")
    return issues


def check_duplicates(df: pd.DataFrame) -> int:
    if "deal_id" not in df.columns:
        return 0
    dupes = df["deal_id"][df["deal_id"].duplicated(keep=False)]
    for deal_id in sorted(set(dupes)):
        lines = [str(i + 2) for i in df.index[df["deal_id"] == deal_id]]
        print(f"  deal_id '{deal_id or '(blank)'}' appears on lines {', '.join(lines)}")
    if dupes.empty:
        print("  OK: no duplicate deal_id values")
    return dupes.nunique()


def main() -> None:
    print(f"Checking {DEALS_PATH}\n")
    df = load_deals(DEALS_PATH)
    if df is None:
        return

    print("Columns")
    issues = check_columns(df)

    if df.empty:
        print("\nNo deal rows yet: the file has a header only. Add deals, then re-run.")
        return

    print(f"\n{len(df)} deal rows found\n")
    print("Source URLs")
    issues += check_sources(df)
    print("\nAllowed values")
    issues += check_allowed_values(df)
    print("\nAnnounce dates")
    issues += check_dates(df)
    print(f"\nDeals per sector (max {MAX_DEALS_PER_SECTOR})")
    issues += check_sectors(df)
    print("\nStrategic vs PE split (target roughly 50/50)")
    report_buyer_split(df)
    print(f"\nDeal size (EV £{EV_MIN_GBP_M}m-£{EV_MAX_GBP_M}m)")
    issues += check_deal_size(df)
    print("\nDuplicate deal_id")
    issues += check_duplicates(df)

    print(f"\n{issues} issue(s) found." if issues else "\nAll checks passed.")


if __name__ == "__main__":
    main()
