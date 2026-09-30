# ---------------------------------------------------------------------------
# 3_map_change.py
# Authors: Mariel Sorlien
# Python 3.7
#
# Description:
# Compares the output rasters from 1_calc_landuse.py for two years and tracks how each pixel has changed. Generates a
# raster map of all the changed pixels in addition to a csv file for each geoscale. Each csv can be used to generate a
# sankey diagram.
#
# REQUIRES GIS/ARCPY
# ---------------------------------------------------------------------------

# Import modules
from pathlib import Path
import arcpy
import pandas as pd
from functions import *

arcpy.env.overwriteOutput = True

# Set working directory, projection --------------------------------------------
base_folder = Path.cwd().parents[2] / "Data" / "land_use"
csv_folder = base_folder / "int_tabulardata"
arcpy.env.workspace = str(base_folder / "int_gisdata")

# Define variables
source_year = 2026
nbep_year = 2026
year_range = "1985-2025"

# Input files
start_raster = "landuse_int.gdb/LANDUSE_1985_NBEP2026"
end_raster = "landuse_int.gdb/LANDUSE_2025_NBEP2026"

colormap = Path.cwd() / "colormap.clr"

# Define INPUTS - GEOSCALES
geoscale_folder = base_folder / "int_gisdata" / "geoscale_int.gdb"

studyarea = str(geoscale_folder / "STUDYAREAS_NBEP2017")
basins = str(geoscale_folder / "BASINS_NBEP2017")
huc10 = str(geoscale_folder / "HUC10_NBEP2017")
huc12 = str(geoscale_folder / "HUC12_NBEP2017")

# Output files
nlcd_final = "landuse_int.gdb/LANDUSE_1985_2025_NBEP2026"
csv_final = "LanduseChange_1985_2025_NBEP2026.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
temp_raster = arcpy.env.scratchFolder + "/temp_no_change.tif"

# MERGING RASTERS REMOVES DATA :(
# CALC EACH SEPARATELY, THEN COMBINE DATAFRAMES INSTEAD
# Need to update calculation function........

print("\nMAPPING LANDUSE CHANGE")
print("Generating change raster")
nlcd_change = arcpy.ia.ComputeChangeRaster(
    from_raster=start_raster,
    to_raster=end_raster,
    compute_change_method="CATEGORICAL_DIFFERENCE",
    filter_method="CHANGED_PIXELS_ONLY",
    define_transition_colors="TO_COLOR"
)
print("\tSaving")
nlcd_change.save(nlcd_final)
print("\tUpdating fields")
with arcpy.da.UpdateCursor(nlcd_final, field_names="Class_Name") as cursor:
    for row in cursor:
        row[0] = row[0].replace("->", "_")
        row[0] = row[0].replace("Water", "1")
        row[0] = row[0].replace("Developed, Open Space", "21")
        row[0] = row[0].replace("Developed, Low Intensity", "22")
        row[0] = row[0].replace("Developed, Medium Intensity", "23")
        row[0] = row[0].replace("Developed, High Intensity", "24")
        row[0] = row[0].replace("Barren", "3")
        row[0] = row[0].replace("Forest", "4")
        row[0] = row[0].replace("Brushland", "5")
        row[0] = row[0].replace("Grassland", "7")
        row[0] = row[0].replace("Agriculture", "8")
        row[0] = row[0].replace("Wetland", "9")
        cursor.updateRow(row)

print("Generating no change raster")
nlcd_no_change = arcpy.ia.ComputeChangeRaster(
    from_raster=start_raster,
    to_raster=end_raster,
    compute_change_method="CATEGORICAL_DIFFERENCE",
    filter_method="UNCHANGED_PIXELS_ONLY",
    define_transition_colors="TO_COLOR"
)
nlcd_no_change.save(temp_raster)
print("\tUpdating fields")
with arcpy.da.UpdateCursor(temp_raster, field_names="Class_Name") as cursor:
    for row in cursor:
        row[0] = row[0].replace("Water", "1_1")
        row[0] = row[0].replace("Developed, Open Space", "21_21")
        row[0] = row[0].replace("Developed, Low Intensity", "22_22")
        row[0] = row[0].replace("Developed, Medium Intensity", "23_23")
        row[0] = row[0].replace("Developed, High Intensity", "24_24")
        row[0] = row[0].replace("Barren", "3_3")
        row[0] = row[0].replace("Forest", "4_4")
        row[0] = row[0].replace("Brushland", "5_5")
        row[0] = row[0].replace("Grassland", "7_7")
        row[0] = row[0].replace("Agriculture", "8_8")
        row[0] = row[0].replace("Wetland", "9_9")
        cursor.updateRow(row)

print("\nCALCULATING AREA")
print("Per study area")
df_acres = calc_area.change_area(
    in_geoscale=studyarea,
    geoscale_field="Study_Area",
    nlcd_change=nlcd_final,
    nlcd_same=temp_raster,
    year_range=year_range
)
df_acres["Study_Area"] = df_acres["Geoscale_Name"]

print("Per basin")
df_temp = calc_area.change_area(
    in_geoscale=basins,
    geoscale_field="Basins",
    nlcd_change=nlcd_final,
    nlcd_same=temp_raster,
    year_range=year_range
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="Basins",
    ref_csv="data/basins.csv"
)
df_temp.rename(columns={"Basins": "Basin"}, inplace=True)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC10")
df_temp = calc_area.change_area(
    in_geoscale=huc10,
    geoscale_field="HUC10",
    nlcd_change=nlcd_final,
    nlcd_same=temp_raster,
    year_range=year_range
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="HUC10",
    ref_csv="data/HUC10.csv"
)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC12")
df_temp = calc_area.change_area(
    in_geoscale=huc12,
    geoscale_field="HUC12",
    nlcd_change=nlcd_final,
    nlcd_same=temp_raster,
    year_range=year_range
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="HUC12",
    ref_csv="data/HUC12.csv"
)
df_acres = pd.concat([df_acres, df_temp])

print("Dropping extra columns")
df_acres = df_acres[[
    "Geoscale", "Geoscale_Name", "HUC10", "HUC10_Name", "HUC12", "HUC12_Name", "Basin", "Study_Area", "Year",
    "Start_Category", "End_Category", "Acres"
]]

print("\nSPLITTING DATA BY GEOSCALE")
geoscale_list = df_acres["Geoscale"].unique()
for geoscale in geoscale_list:
    print("By", geoscale)
    prep_csv.split_geoscale(
        in_df=df_acres,
        geoscale=geoscale,
        nbep_year=nbep_year,
        source_year=source_year,
        out_path=csv_folder,
        csv_prefix="LANDUSE_sankey_"
    )

print("\nCLEARING SCRATCH FOLDER")
arcpy.Delete_management(arcpy.env.scratchFolder)

print("\nDONE")
