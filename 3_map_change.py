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
source_year = 2026
nbep_year = 2026
year_range = "2000-2025"

# Input files
start_raster = "landuse_int.gdb/NLCD_2000_NBEP2026"
end_raster = "landuse_int.gdb/NLCD_2025_NBEP2026"

colormap = Path.cwd() / "colormap.clr"

# Define INPUTS - GEOSCALES
geoscale_folder = base_folder / "int_gisdata" / "geoscale_int" / "geoscale_int.gdb"

studyarea = str(geoscale_folder / "STUDYAREAS_NBEP2017")
basins = str(geoscale_folder / "BASINS_NBEP2017")
huc10 = str(geoscale_folder / "HUC10_NBEP2017")
huc12 = str(geoscale_folder / "HUC12_NBEP2017")
state_studyarea = str(geoscale_folder / "STATES_ByStudyArea_NBEP2017")
town = str(geoscale_folder / "TOWNS_NBEP2017")
town_studyarea = str(geoscale_folder / "TOWNS_ByStudyArea_NBEP2017")

# Output files
nlcd_final = "landuse_int.gdb/NLCD_2000_2025_NBEP2026"
csv_final = "LanduseChange_2000_2025_NBEP2026.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
temp_nlcd = arcpy.env.scratchFolder + "/temp_nlcd.tif"
temp_geoscale = arcpy.env.scratchFolder + "/temp_geoscale.shp"

# print("\nSETTING DEFAULT VALUES")
# print("Setting snap raster")
# arcpy.env.snapRaster = start_raster
# print("Retrieving NLCD spatial reference")
# spatial_ref = arcpy.Describe(start_raster).spatialReference

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
print("Per study area")
df_acres = calc_area.change_area(
    in_geoscale=studyarea,
    geoscale_field="Study_Area",
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_acres["Study_Area"] = df_acres["Geoscale_Name"]

print("Per basin")
df_temp = calc_area.change_area(
    in_geoscale=basins,
    geoscale_field="Basins",
    in_nlcd=temp_nlcd,
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
    in_nlcd=temp_nlcd,
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
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="HUC12",
    ref_csv="data/HUC12.csv"
)
df_acres = pd.concat([df_acres, df_temp])

print("Per state per study area")
update_field.merge_field(
    in_table=state_studyarea,
    out_table=temp_geoscale,
    new_field="State_Area",
    expression='!State! + "-" + !Study_Area!'
)
df_temp = calc_area.change_area(
    in_geoscale=temp_geoscale,
    geoscale_field="State_Area",
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_temp[["State", "Study_Area"]] = df_temp["Geoscale_Name"].str.split("-", expand=True)
df_acres = pd.concat([df_acres, df_temp])

print("Per town")
update_field.merge_field(
    in_table=town,
    out_table=temp_geoscale,
    new_field="Town_State",
    expression='!Town_Name! + "-" + !State!'
)
df_temp = calc_area.change_area(
    in_geoscale=temp_geoscale,
    geoscale_field="Town_State",
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_temp[["Town", "State"]] = df_temp["Geoscale_Name"].str.split("-", expand=True)
df_acres = pd.concat([df_acres, df_temp])

print("Per town per study area")
update_field.merge_field(
    in_table=town_studyarea,
    out_table=temp_geoscale,
    new_field="Town_Area",
    expression='!Town_Name! + "-" + !State! + "-" + !Study_Area!'
)
df_temp = calc_area.change_area(
    in_geoscale=temp_geoscale,
    geoscale_field="Town_Area",
    in_nlcd=temp_nlcd,
    year_range=year_range
)
df_temp[["Town", "State", "Study_Area"]] = df_temp["Geoscale_Name"].str.split("-", expand=True)
df_acres = pd.concat([df_acres, df_temp])

print("Updating columns")
df_acres.replace(
    to_replace={
        "State": {"CT": "Connecticut", "RI": "Rhode Island", "MA": "Massachusetts"}
    },
    inplace=True
)
df_acres = df_acres[[
    "Geoscale", "Geoscale_Name", "Town", "State", "HUC10", "HUC10_Name", "HUC12", "HUC12_Name", "Basin", "Study_Area",
    "Year", "Water_to_Forest_Acres", "Water_to_Developed_Acres", "Barren_to_Forest_Acres", "Barren_to_Developed_Acres",
    "Forest_to_Water_Acres", "Forest_to_Barren_Acres", "Forest_to_Brushland_Acres", "Forest_to_Grassland_Acres",
    "Forest_to_Agriculture_Acres", "Forest_to_Wetland_Acres", "Forest_to_Developed_Acres", "Brushland_to_Forest_Acres",
    "Brushland_to_Developed_Acres", "Grassland_to_Forest_Acres", "Grassland_to_Developed_Acres",
    "Agriculture_to_Forest_Acres", "Agriculture_to_Developed_Acres", "Wetland_to_Forest_Acres",
    "Wetland_to_Developed_Acres", "Developed_to_Water_Acres", "Developed_to_Barren_Acres",
    "Developed_to_Forest_Acres", "Developed_to_Brushland_Acres", "Developed_to_Grassland_Acres",
    "Developed_to_Agriculture_Acres", "Developed_to_Wetland_Acres", "Developed_Open_to_Developed_Low_Acres",
    "Developed_Open_to_Developed_Medium_Acres", "Developed_Open_to_Developed_High_Acres",
    "Developed_Low_to_Developed_Open_Acres", "Developed_Low_to_Developed_Medium_Acres",
    "Developed_Low_to_Developed_High_Acres", "Developed_Medium_to_Developed_Open_Acres",
    "Developed_Medium_to_Developed_Low_Acres", "Developed_Medium_to_Developed_High_Acres",
    "Developed_High_to_Developed_Open_Acres", "Developed_High_to_Developed_Low_Acres",
    "Developed_High_to_Developed_Medium_Acres"
]]

print("\nDOWNLOADING FILES")
print("Saving csv")
df_acres.to_csv(csv_folder / csv_final, index=False)

print("\nCLEARING SCRATCH FOLDER")
arcpy.Delete_management(arcpy.env.scratchFolder)

print("\nDONE")
