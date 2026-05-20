# ---------------------------------------------------------------------------
# 3_map_change.py
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

# Set working directory, projection --------------------------------------------
base_folder = Path.cwd().parents[2] / "Data"
gis_folder = base_folder / "int_gisdata" / "landuse_int"
csv_folder = base_folder / "int_tabulardata" / "landuse_int"
arcpy.env.workspace = str(gis_folder)

# Define variables
source_year = 2025
nbep_year = 2026
year_range = "2000-2024"

# Input files
start_raster = "landuse_int.gdb/NLCD_2000_NBEP2025"
end_raster = "landuse_int.gdb/NLCD_2024_NBEP2025"

clip_boundaries = "landuse_int.gdb/geoscales/town_and_bay"
colormap = Path.cwd() / "colormap.clr"

basins = "landuse_int.gdb/source_copy/BASINS_NBEP2017"
basins_field = "Basin"

huc10 = "landuse_int.gdb/source_copy/HUC10_NBEP2017"
huc10_field = "HUC10_Name"

huc12 = "landuse_int.gdb/source_copy/HUC12_NBEP2017"
huc12_field = "HUC12"  # Must include ID, since multiple HUC12 with same name

studyarea = "landuse_int.gdb/source_copy/STUDYAREAS_NBEP2017"
studyarea_field = "Study_Area"

state_studyarea = "landuse_int.gdb/geoscales/states_by_studyarea"
state_field = "State_Area"  # Must include state AND study area

town = "landuse_int.gdb/geoscales/town_and_bay"
town_field = "Town_State"  # Must include town AND state

town_studyarea = "landuse_int.gdb/geoscales/towns_by_studyarea"
town_studyarea_field = "Town_Area"  # Must include town, state, AND study area

# Output files
nlcd_final = "landuse_int.gdb/NLCD_2000_2024_NBEP2026"
csv_final = "LanduseChange_2000_2024_NBEP2026.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
# temp_buffer = arcpy.env.scratchFolder + "/temp_buffer.shp"
# temp_clip = arcpy.env.scratchFolder + "/temp_boundaries.shp"
temp_nlcd = arcpy.env.scratchFolder + "/temp_nlcd.tif"
temp_raster = arcpy.env.scratchFolder + "/temp_raster.tif"

print("\nSETTING DEFAULT VALUES")
print("Setting snap raster")
arcpy.env.snapRaster = start_raster
print("Retrieving NLCD spatial reference")
spatial_ref = arcpy.Describe(start_raster).spatialReference

print("\nMAPPING LANDUSE CHANGE")
print("Generating change raster")
nlcd_change = arcpy.ia.ComputeChangeRaster(
    from_raster=start_raster,
    to_raster=end_raster,
    compute_change_method="CATEGORICAL_DIFFERENCE",
    filter_method="CHANGED_PIXELS_ONLY",
    define_transition_colors="TO_COLOR"
)
nlcd_change.save(str(gis_folder / nlcd_final))

print("Filtering raster")
nlcd_filter = arcpy.sa.ExtractByAttributes(
    in_raster=nlcd_final,
    where_clause="Class_From IN ('Dev_High', 'Dev_Low', 'Dev_Med', 'Dev_Open', 'Forest') Or "
                 "Class_To IN ('Dev_High', 'Dev_Low', 'Dev_Med', 'Dev_Open', 'Forest')"
)
nlcd_filter.save(temp_nlcd)
print("Updating fields")
with arcpy.da.UpdateCursor(temp_nlcd, field_names="Class_Name") as cursor:
    for row in cursor:
        row[0] = row[0].replace("->", "_")
        row[0] = row[0].replace("Water", "1")
        row[0] = row[0].replace("Dev_Open", "21")
        row[0] = row[0].replace("Dev_Low", "22")
        row[0] = row[0].replace("Dev_Med", "23")
        row[0] = row[0].replace("Dev_High", "24")
        row[0] = row[0].replace("Barren", "3")
        row[0] = row[0].replace("Forest", "4")
        row[0] = row[0].replace("Brushland", "5")
        row[0] = row[0].replace("Grassland", "7")
        row[0] = row[0].replace("Agriculture", "8")
        row[0] = row[0].replace("Wetland", "9")
        cursor.updateRow(row)

# QUERY: USE RAW NLCD DATA?
# QUERY: IS ACRE CALCULATION CORRECT IF NOT USING RAW NLCD DATA? (PROJECTION ISSUES)

print("\nCALCULATING AREA")
print("Per basin")
prep_raster.prep_geoscale(
    in_features=basins,
    in_field=basins_field,
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_acres = calc_area.change_area(
    in_geoscale=temp_raster,
    geoscale_field=basins_field,
    in_nlcd=temp_nlcd,
    year_range=year_range
)

print("Per HUC10")
prep_raster.prep_geoscale(
    in_features=huc10,
    in_field=huc10_field,
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.change_area(
    in_geoscale=temp_raster,
    geoscale_field=huc10_field,
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC12")
prep_raster.prep_geoscale(
    in_features=huc12,
    in_field=huc12_field,
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.change_area(
    in_geoscale=temp_raster,
    geoscale_field=huc12_field,
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_acres = pd.concat([df_acres, df_temp])

print("Per study area")
prep_raster.prep_geoscale(
    in_features=studyarea,
    in_field=studyarea_field,
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.change_area(
    in_geoscale=temp_raster,
    geoscale_field=studyarea_field,
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_acres = pd.concat([df_acres, df_temp])

print("Per state per study area")
prep_raster.prep_geoscale(
    in_features=state_studyarea,
    in_field=state_field,
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.change_area(
    in_geoscale=temp_raster,
    geoscale_field=state_field,
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_acres = pd.concat([df_acres, df_temp])

print("Per town")
prep_raster.prep_geoscale(
    in_features=town,
    in_field=town_field,
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.change_area(
    in_geoscale=temp_raster,
    geoscale_field=town_field,
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_acres = pd.concat([df_acres, df_temp])

print("Per town per study area")
prep_raster.prep_geoscale(
    in_features=town_studyarea,
    in_field=town_studyarea_field,
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.change_area(
    in_geoscale=temp_raster,
    geoscale_field=town_studyarea_field,
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_acres = pd.concat([df_acres, df_temp])

print("\nDOWNLOADING FILES")
print("Saving csv")
df_acres.to_csv(csv_folder / csv_final)
