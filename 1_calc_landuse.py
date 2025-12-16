# ---------------------------------------------------------------------------
# 2_calc_landuse.py
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
import arcpy
import pandas as pd
from functions import *

arcpy.env.overwriteOutput = True

# Set working directory, projection
base_folder = Path.cwd().parents[2] / "Data"
gis_folder = base_folder / "int_gisdata" / "landuse_int"
arcpy.env.workspace = str(gis_folder)
scratch_folder = arcpy.env.scratchFolder

# Define INPUTS
nlcd_year = 2024
nlcd = "Annual_NLCD_LndCov_2024_CU_C1V1.tif"

clipbox = "landuse_int.gdb/source_copy_albers/NLCD_ClipBox_Albers"

shp_state_studyarea = "GEOSCALES_INT.gdb/STATES_byStudyArea_PROJECT_2025"
shp_town = ""
shp_town_studyarea = ""

basins = "GEOSCALES_INT.gdb/BASINS_RAS"
huc10 = "GEOSCALES_INT.gdb/HUC10_RAS"
huc12 = "GEOSCALES_INT.gdb/HUC12_RAS"
studyarea = "GEOSCALES_INT.gdb/STUDYAREA_RAS"
town = "GEOSCALES_INT.gdb/TOWNSFULL_RAS"
town_studyarea = "GEOSCALES_INT.gdb/TOWNSCLIP_RAS"

# Define OUTPUTS
raster_state_studyarea = "GEOSCALES_INT.gdb/STATES_byStudyArea_2025_RAS"
raster_town = ""
raster_town_studyarea = ""

nlcd_out = "int_gisdata.gdb/NLCD_2024_NBEP2025.tif"
csv_out = ""

# Code ----
temp_nlcd = "temp_nlcd.tif"

print("\nPROCESSING NLCD DATA")
print("Prepping", nlcd_year, "data")
prep_raster.prep_nlcd(
    in_features=nlcd,
    out_features=temp_nlcd,
    clip_boundaries=clipbox
)

print("\nSETTING EXTENT, SNAP RASTER")
arcpy.env.extent = clipbox
arcpy.env.snapRaster = temp_nlcd

print("\nCALCULATING AREA")
print("Per basin")
df_acres = calc_area.current_area(
    in_geoscale=basins,
    geoscale_field="Basins",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)

print("Per HUC10")
df_temp = calc_area.current_area(
    in_geoscale=huc10,
    geoscale_field="HUC10",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC12")
df_temp = calc_area.current_area(
    in_geoscale=huc12,
    geoscale_field="HUC12",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
print(df_temp)
df_acres = pd.concat([df_acres, df_temp])

print("Per study area")
df_temp = calc_area.current_area(
    in_geoscale=studyarea,
    geoscale_field="Study_Area",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
print(df_temp)
df_acres = pd.concat([df_acres, df_temp])

print("Per state per study area")
print("\tConverting to raster")
arcpy.conversion.PolygonToRaster(
    in_features=shp_state_studyarea,
    value_field="State_Area",
    out_rasterdataset=raster_state_studyarea,
    cell_assignment="MAXIMUM_AREA"
)
df_temp = calc_area.current_area(
    in_geoscale=raster_state_studyarea,
    geoscale_field="State_Area",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
print(df_temp)
df_acres = pd.concat([df_acres, df_temp])

print("Per town")
df_temp = calc_area.current_area(
    in_geoscale=town,
    geoscale_field="Town_Name",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres = pd.concat([df_acres, df_temp])
print(df_temp)

print("Per town per study area")
df_temp = calc_area.current_area(
    in_geoscale=town_studyarea,
    geoscale_field="Town_Name",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_temp["Geoscale"] = "Town per Study Area"
df_acres = pd.concat([df_acres, df_temp])
print(df_temp)

# print("\nSAVING RASTER")
# # Clip to towns+bays
# # Project to usual NAD
