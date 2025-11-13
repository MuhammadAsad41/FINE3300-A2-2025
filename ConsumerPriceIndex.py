import pandas as pd
import numpy as np

# ================================================
#  Part B – Consumer Price Index (CPI) – Python
# ================================================

# ------------------------------------------------
# 0. File names and general setup
# ------------------------------------------------

# Order matters here: Canada first, then provinces
cpi_order = [
    ("Canada", "Canada.CPI.1810000401.csv"),
    ("AB", "AB.CPI.1810000401.csv"),
    ("BC", "BC.CPI.1810000401.csv"),
    ("MB", "MB.CPI.1810000401.csv"),
    ("NB", "NB.CPI.1810000401.csv"),
    ("NL", "NL.CPI.1810000401.csv"),
    ("NS", "NS.CPI.1810000401.csv"),
    ("ON", "ON.CPI.1810000401.csv"),
    ("PEI", "PEI.CPI.1810000401.csv"),
    ("QC", "QC.CPI.1810000401.csv"),
    ("SK", "SK.CPI.1810000401.csv"),
]

MONTH_COLS = [
    "24-Jan", "24-Feb", "24-Mar", "24-Apr", "24-May", "24-Jun",
    "24-Jul", "24-Aug", "24-Sep", "24-Oct", "24-Nov", "24-Dec"
]

MONTH_LABELS = [
    "Jan-24", "Feb-24", "Mar-24", "Apr-24", "May-24", "Jun-24",
    "Jul-24", "Aug-24", "Sep-24", "Oct-24", "Nov-24", "Dec-24"
]

month_to_label = dict(zip(MONTH_COLS, MONTH_LABELS))

# Categories needed in questions
ITEMS_OF_INTEREST = [
    "All-items",
    "Food",
    "Shelter",
    "Services",
    "All-items excluding food and energy"
]

# ------------------------------------------------
# 1. Combine the 11 data frames into one
#    Columns: Item, Month, Jurisdiction, CPI
# ------------------------------------------------

frames = []

for jurisdiction, filename in cpi_order:
    temp = pd.read_csv(filename)

    #   - Item order as in the CSV
    #   - Month order as in MONTH_COLS
    temp_long = temp.melt(
        id_vars="Item",
        value_vars=MONTH_COLS,
        var_name="MonthRaw",
        value_name="CPI"
    )

    temp_long["Jurisdiction"] = jurisdiction
    temp_long["Month"] = temp_long["MonthRaw"].map(month_to_label)
    temp_long = temp_long.drop(columns=["MonthRaw"])
    frames.append(temp_long)

cpi_df = pd.concat(frames, ignore_index=True)
cpi_df = cpi_df[["Item", "Month", "Jurisdiction", "CPI"]]

# Q1:
# Canada, All-items / Food / Shelter for Jan-24
print("=== First 12 lines of combined CPI data ===")
print(cpi_df.head(12))
print()

# ------------------------------------------------
# 2 & 3. Month-to-month % change and averages
# ------------------------------------------------

# Month-to-month percentage change (order within each group
# is already Jan→Dec because of the melt above)
cpi_df["MoM_pct"] = (
    cpi_df
    .groupby(["Jurisdiction", "Item"])["CPI"]
    .pct_change() * 100
)

target_items = [
    "Food",
    "Shelter",
    "Services",
    "All-items excluding food and energy",
    "All-items"
]

avg_mom = (
    cpi_df[cpi_df["Item"].isin(target_items)]
    .groupby(["Jurisdiction", "Item"])["MoM_pct"]
    .mean()
    .reset_index()
)

avg_mom["Avg_MoM_pct_change"] = avg_mom["MoM_pct"].round(1)
avg_mom = avg_mom.drop(columns=["MoM_pct"])

print("=== Average month-to-month % change in CPI (2024) ===")
avg_table = avg_mom.pivot(
    index="Jurisdiction",
    columns="Item",
    values="Avg_MoM_pct_change"
)
print(avg_table)
print()

# ------------------------------------------------
# 4. Province with highest average change
# ------------------------------------------------

avg_no_canada = avg_mom[avg_mom["Jurisdiction"] != "Canada"]
idx_max = avg_no_canada.groupby("Item")["Avg_MoM_pct_change"].idxmax()
highest_avg_change = avg_no_canada.loc[idx_max].reset_index(drop=True)

print("=== Province with highest average monthly change in each category ===")
print(highest_avg_change)
print()

# ------------------------------------------------
# 5. Equivalent salary to $100,000 in Ontario
#    using All-items CPI, Dec 2024
# ------------------------------------------------

dec_all_items = cpi_df[
    (cpi_df["Item"] == "All-items") &
    (cpi_df["Month"] == "Dec-24")
]

ontario_cpi_dec = float(
    dec_all_items.loc[dec_all_items["Jurisdiction"] == "ON", "CPI"]
)

equiv_salary_df = dec_all_items[["Jurisdiction", "CPI"]].copy()
equiv_salary_df["EquivalentSalary"] = (
    100000 * equiv_salary_df["CPI"] / ontario_cpi_dec
).round(2)

print("=== Equivalent salary to $100,000 in Ontario (Dec-24, All-items CPI) ===")
print(equiv_salary_df[["Jurisdiction", "EquivalentSalary"]])
print()

# ------------------------------------------------
# 6. Minimum wages: nominal and real
# ------------------------------------------------

min_wage_df = pd.read_csv("MinimumWages.csv")

# Adjust names to something easy
min_wage_df = min_wage_df.rename(
    columns={"Province": "Jurisdiction", "Minimum Wage": "MinWage"}
)
min_wage_df["MinWage"] = min_wage_df["MinWage"].astype(float)

# Nominal highest/lowest
max_nominal = min_wage_df.loc[min_wage_df["MinWage"].idxmax()]
min_nominal = min_wage_df.loc[min_wage_df["MinWage"].idxmin()]

print("=== Minimum wages (nominal) ===")
print(
    f"Highest nominal minimum wage: {max_nominal['Jurisdiction']} "
    f"(${max_nominal['MinWage']:.2f})"
)
print(
    f"Lowest nominal minimum wage:  {min_nominal['Jurisdiction']} "
    f"(${min_nominal['MinWage']:.2f})"
)
print()

# Real minimum wage using Dec-24 All-items CPI
dec_all_items_short = dec_all_items[["Jurisdiction", "CPI"]]
min_merge = pd.merge(min_wage_df, dec_all_items_short, on="Jurisdiction")

# Real wage index (bigger = more purchasing power)
min_merge["RealMinWage"] = min_merge["MinWage"] / (min_merge["CPI"] / 100.0)

min_merge_sorted = min_merge.sort_values("RealMinWage", ascending=False)

print("=== Minimum wages (real, using Dec-24 All-items CPI) ===")
print(min_merge_sorted[["Jurisdiction", "MinWage", "CPI", "RealMinWage"]])
print()
print(
    "Province with highest REAL minimum wage:",
    min_merge_sorted.iloc[0]["Jurisdiction"]
)
print()

# ------------------------------------------------
# 7. Annual change in CPI for services (Jan → Dec)
# ------------------------------------------------

services_df = cpi_df[cpi_df["Item"] == "Services"].copy()

# Putting months in rows and jurisdictions in index
services_pivot = services_df.pivot(
    index="Jurisdiction",
    columns="Month",
    values="CPI"
)

# Annual % change from Jan-24 to Dec-24
annual_change_services = (
    (services_pivot["Dec-24"] - services_pivot["Jan-24"])
    / services_pivot["Jan-24"] * 100
).round(1)

print("=== Annual change in CPI for services (Jan-24 to Dec-24) ===")
for jurisdiction, change in annual_change_services.items():
    print(f"{jurisdiction}: {change:.1f}%")
print()

# ------------------------------------------------
# 8. Region with highest services inflation
# ------------------------------------------------

max_services_region = annual_change_services.idxmax()
max_services_value = annual_change_services.loc[max_services_region]

print("=== Region with highest inflation in services ===")
print(
    f"{max_services_region} with an annual change of "
    f"{max_services_value:.1f}% in services CPI."
)
print()


