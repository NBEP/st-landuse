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

from functions import prep_csv

# Set working directory, projection --------------------------------------------
base_folder = Path.cwd().parents[2] / "Data" / "int_tabulardata" / "landuse_int"

# Define variables
in_csv = [
    "NLCD_2000_NBEP2025.csv", "NLCD_2005_NBEP2025.csv", "NLCD_2010_NBEP2025.csv", "NLCD_2015_NBEP2025.csv",
    "NLCD_2020_NBEP2025.csv", "NLCD_2024_NBEP2025.csv"
]
group_col = "Geoscale_Name"
sort_col = ["Geoscale", group_col, "Year"]

source_year = 2025
nbep_year = 2025

split_by_geoscale = True

# Output files
out_csv = base_folder / "NLCD_change_2001_2024_NBEP2025.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
if "Year" not in sort_col:
    sort_col.append("Year")

print("\nIMPORTING DATA")
df = pd.DataFrame()
for csv in in_csv:
    print("Reading in", csv)
    temp_csv = base_folder / csv
    df_temp = pd.read_csv(temp_csv)
    df = pd.concat([df, df_temp])
print("Sorting data by", sort_col)
df.sort_values(by=sort_col, inplace=True)
df.reset_index(drop=True, inplace=True)

if split_by_geoscale is True:
    print("\nSPLITTING DATA BY GEOSCALE")
    geoscale_list = df["Geoscale"].unique()
    for geoscale in geoscale_list:
        print("By", geoscale)
        prep_csv.split_geoscale(
            in_df=df,
            geoscale=geoscale,
            nbep_year=nbep_year,
            source_year=source_year,
            out_path=base_folder
        )

print("\nCALCULATING CHANGE")
print("Calculating change")
df['Prev_Year'] = df.Year.shift(1)
df['Prev_Site'] = df[group_col].shift(1)
df["Gross_Change_Forest_Acres"] = df["Forest_Acres"] - df["Forest_Acres"].shift(1)
df["Percent_Change_Forest"] = df["Gross_Change_Forest_Acres"] / df["Forest_Acres"].shift(1) * 100
df["Gross_Change_Developed_Acres"] = df["Developed_Acres"] - df["Developed_Acres"].shift(1)
df["Percent_Change_Developed"] = df["Gross_Change_Developed_Acres"] / df["Developed_Acres"].shift(1) * 100
print("Trimming data")
df.drop(df[df.Year == df.Prev_Year].index, inplace=True)
df.drop(df[df[group_col] != df.Prev_Site].index, inplace=True)
print("Updating columns")
df["Year"] = df.Prev_Year.astype(str) + "-" + df.Year.astype(str)
df["Year"] = df["Year"].str.replace(".0", "", regex=False)
keep_cols = sort_col + [
    "Gross_Change_Forest_Acres", "Percent_Change_Forest", "Gross_Change_Developed_Acres", "Percent_Change_Developed"
]
df = df.reindex(columns=keep_cols)

print("\nSAVING CSV")
print("Saving summary file")
df.to_csv(out_csv)
if split_by_geoscale is True:
    print("Splitting data")
    geoscale_list = df["Geoscale"].unique()
    for geoscale in geoscale_list:
        print("By", geoscale)
        prep_csv.split_geoscale(
            in_df=df,
            geoscale=geoscale,
            nbep_year=nbep_year,
            source_year=source_year,
            out_path=base_folder,
            csv_prefix="NLCD_change_"
        )

print("\nDONE")