# ---------------------------------------------------------------------------
# 2_calc_change.py
# Authors: Mariel Sorlien
# Python 3.7
#
# Description:
# Combines output csv files from 1_calc_landuse.py and calculates gross, percent change between years. Outputs a
# separate csv file for each geoscale.
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
    "LANDUSE_1985_NBEP2026.csv", "LANDUSE_1990_NBEP2026.csv", "LANDUSE_1995_NBEP2026.csv", "LANDUSE_2000_NBEP2026.csv",
    "LANDUSE_2005_NBEP2026.csv", "LANDUSE_2010_NBEP2026.csv", "LANDUSE_2015_NBEP2026.csv", "LANDUSE_2020_NBEP2026.csv",
    "LANDUSE_2025_NBEP2026.csv"
]

source_year = 2026
nbep_year = 2026

split_by_geoscale = True

# Output files
out_csv = base_folder / "LANDUSE_change_2000_2025_NBEP2026.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
print("\nIMPORTING DATA")
df = pd.DataFrame()
for csv in in_csv:
    print("Reading in", csv)
    temp_csv = base_folder / csv
    df_temp = pd.read_csv(temp_csv)
    df = pd.concat([df, df_temp])
print("Sorting data by location, year")
sort_col = ["Geoscale", "Geoscale_Name", "Year"]
df.sort_values(by=sort_col, inplace=True)
df.reset_index(drop=True, inplace=True)

print("\nSPLITTING DATA BY GEOSCALE")
geoscale_list = df["Geoscale"].unique()
for geoscale in geoscale_list:
    print("By", geoscale)
    prep_csv.split_geoscale(
        in_df=df,
        geoscale=geoscale,
        nbep_year=nbep_year,
        source_year=source_year,
        out_path=base_folder,
        csv_prefix="LANDUSE_"
    )

print("\nCALCULATING CHANGE")
print("Calculating gross, percent change")
df['Prev_Year'] = df.Year.shift(1)
df['Prev_Site'] = df["Geoscale_Name"].shift(1)
df["Gross_Change_Forest_Acres"] = df["Forest_Acres"] - df["Forest_Acres"].shift(1)
df["Gross_Change_Developed_Acres"] = df["Developed_Acres"] - df["Developed_Acres"].shift(1)
df["Gross_Change_Developed_Open_Acres"] = df["Developed_Open_Acres"] - df["Developed_Open_Acres"].shift(1)
df["Gross_Change_Developed_Low_Acres"] = df["Developed_Low_Acres"] - df["Developed_Low_Acres"].shift(1)
df["Gross_Change_Developed_Medium_Acres"] = df["Developed_Medium_Acres"] - df["Developed_Medium_Acres"].shift(1)
df["Gross_Change_Developed_High_Acres"] = df["Developed_High_Acres"] - df["Developed_High_Acres"].shift(1)
df["Gross_Change_Agricultural_Acres"] = df["Agricultural_Acres"] - df["Agricultural_Acres"].shift(1)
df["Gross_Change_Barren_Acres"] = df["Barren_Acres"] - df["Barren_Acres"].shift(1)
df["Gross_Change_Grassland_Acres"] = df["Grassland_Acres"] - df["Grassland_Acres"].shift(1)
df["Gross_Change_Shrubland_Acres"] = df["Shrubland_Acres"] - df["Shrubland_Acres"].shift(1)
df["Gross_Change_Water_Acres"] = df["Water_Acres"] - df["Water_Acres"].shift(1)
df["Gross_Change_Wetland_Acres"] = df["Wetland_Acres"] - df["Wetland_Acres"].shift(1)
df["Percent_Change_Forest"] = df["Gross_Change_Forest_Acres"] / df["Forest_Acres"].shift(1) * 100
df["Percent_Change_Developed"] = df["Gross_Change_Developed_Acres"] / df["Developed_Acres"].shift(1) * 100
df["Percent_Change_Developed_Open"] = (
        df["Gross_Change_Developed_Open_Acres"] / df["Developed_Open_Acres"].shift(1) * 100
)
df["Percent_Change_Developed_Low"] = df["Gross_Change_Developed_Low_Acres"] / df["Developed_Low_Acres"].shift(1) * 100
df["Percent_Change_Developed_Medium"] = (
        df["Gross_Change_Developed_Medium_Acres"] / df["Developed_Medium_Acres"].shift(1) * 100
)
df["Percent_Change_Developed_High"] = (
        df["Gross_Change_Developed_High_Acres"] / df["Developed_High_Acres"].shift(1) * 100
)

print("Dropping extra rows")
df.drop(df[df.Year == df.Prev_Year].index, inplace=True)
df.drop(df[df.Geoscale_Name != df.Prev_Site].index, inplace=True)
print("Updating columns")
df["Year"] = df.Prev_Year.astype(str) + "-" + df.Year.astype(str)
df["Year"] = df["Year"].str.replace(".0", "", regex=False)
keep_cols = [
    "Geoscale", "Geoscale_Name", "Town", "State", "HUC12", "HUC12_Name", "HUC10", "HUC10_Name", "Basin", "Study_Area",
    "Year", "Percent_Change_Forest", "Percent_Change_Developed", "Percent_Change_Developed_Open",
    "Percent_Change_Developed_Low", "Percent_Change_Developed_Medium","Percent_Change_Developed_High",
    "Gross_Change_Forest_Acres",  "Gross_Change_Developed_Acres", "Gross_Change_Developed_Open_Acres",
    "Gross_Change_Developed_Low_Acres", "Gross_Change_Developed_Medium_Acres", "Gross_Change_Developed_High_Acres",
    "Gross_Change_Agricultural_Acres", "Gross_Change_Barren_Acres", "Gross_Change_Grassland_Acres",
    "Gross_Change_Shrubland_Acres", "Gross_Change_Water_Acres", "Gross_Change_Wetland_Acres"
]
df = df.reindex(columns=keep_cols)

print("\nSPLITTING DATA BY GEOSCALE")
geoscale_list = df["Geoscale"].unique()
for geoscale in geoscale_list:
    print("By", geoscale)
    prep_csv.split_geoscale(
        in_df=df,
        geoscale=geoscale,
        nbep_year=nbep_year,
        source_year=source_year,
        out_path=base_folder,
        csv_prefix="LANDUSE_change_"
    )

print("\nDONE")
