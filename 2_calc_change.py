# ---------------------------------------------------------------------------
# 2_calc_change.py
# Authors: Mariel Sorlien
# Python 3.7
#
# Description:
# TEXT HERE
#
# REQUIRES GIS/ARCPY
# ---------------------------------------------------------------------------

# Import modules
from pathlib import Path
import pandas as pd

# Set working directory, projection --------------------------------------------
base_folder = Path.cwd().parents[2] / "Data" / "int_tabulardata" / "landuse_int"

# Define variables
in_csv = base_folder / "NLCD_2024_NBEP2025.csv"
group_col = "Geoscale_Name"
sort_col = ["Geoscale", group_col]

out_csv = base_folder / "NLCD_change_2001_2024_NBEP2025"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
if "Year" not in sort_col:
    sort_col.append("Year")

print("\nIMPORTING DATA")
df = pd.read_csv(in_csv)

print("\nCALCULATING CHANGE")
print("Sorting data by", sort_col)
df.sort_values(by=sort_col, inplace=True)
df.reset_index(drop=True, inplace=True)
print("Calculating change")
df['Prev_Year'] = df.Year.shift(1)
df['Prev_Site'] = df[group_col].shift(1)
df["Gross_Change_Forest_Acres"] = df["Forest_Acres"] - df["Forest_Acres"].shift(1)
df["Percent_Change_Forest"] = df["Gross_Change_Forest_Acres"] / df["Forest_Acres"] * 100
df["Gross_Change_Developed_Acres"] = df["Developed_Acres"] - df["Developed_Acres"].shift(1)
df["Percent_Change_Developed"] = df["Gross_Change_Developed_Acres"] / df["Developed_Acres"] * 100
print("Trimming data")
df.drop(df[df.Year == df.Prev_Year].index, inplace=True)
df.drop(df[df[group_col] != df.Prev_Site].index, inplace=True)
print("Updating columns")
df["Year"] = df.Year.astype(str) + "-" + df.Prev_Year.astype(str)
keep_cols = sort_col + [
    "Gross_Change_Forest_Acres", "Percent_Change_Forest", "Gross_Change_Developed_Acres", "Percent_Change_Developed"
]
df = df.reindex(columns=keep_cols)

print("\nSAVING CSV")
df.to_csv(out_csv)

print("\nDONE")