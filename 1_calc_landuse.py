# ---------------------------------------------------------------------------
# 1_calc_landuse.py
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
csv_folder = base_folder / "int_tabulardata" / "landuse_int"
arcpy.env.workspace = str(base_folder / "int_gisdata" / "landuse_int")

# Define INPUTS
nlcd_year = 2025
nlcd = "Annual_NLCD_LndCov_" + str(nlcd_year) + "_CU_C1V2/Annual_NLCD_LndCov_" + str(nlcd_year) + "_CU_C1V2.tif"

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
bay = str(geoscale_folder / "BAYS_NBEP2017")

# Define OUTPUTS
nlcd_final = "landuse_int.gdb/NLCD_" + str(nlcd_year) + "_NBEP2026"
csv_final = "NLCD_" + str(nlcd_year) + "_NBEP2026.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
temp_union = arcpy.env.scratchFolder + "/temp_union.shp"
temp_buffer = arcpy.env.scratchFolder + "/temp_buffer.shp"
temp_clip = arcpy.env.scratchFolder + "/temp_boundaries.shp"
temp_nlcd = arcpy.env.scratchFolder + "/temp_nlcd.tif"
temp_geoscale = arcpy.env.scratchFolder + "/temp_geoscale.shp"

print("\nSETTING DEFAULT VALUES")
print("Setting snap raster")
arcpy.env.snapRaster = nlcd
print("Retrieving NLCD spatial reference")
spatial_ref = arcpy.Describe(nlcd).spatialReference

print("\nPROCESSING", nlcd_year, "NLCD DATA")
print("Setting clip boundaries")
print("\tMerging town and bay boundaries")
arcpy.analysis.Union(
    in_features=[town, bay],
    out_feature_class=temp_union
)
print("\tAdding 30m buffer")
arcpy.analysis.Buffer(
    in_features=temp_union,
    out_feature_class=temp_buffer,
    buffer_distance_or_field="30 Meters",
    dissolve_option="ALL"
)
print("\tProjecting to Albers")
arcpy.management.Project(
    in_dataset=temp_buffer,
    out_dataset=temp_clip,
    out_coor_system=spatial_ref
)
print("Formatting NLCD data")
prep_raster.prep_nlcd(
    in_features=nlcd,
    out_features=temp_nlcd,
    clip_boundaries=temp_clip,
    colormap=str(colormap)
)

print("\nCALCULATING AREA")
print("Per study area")
df_acres = calc_area.current_area(
    in_geoscale=studyarea,
    geoscale_field="Study_Area",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres["Study_Area"] = df_acres["Geoscale_Name"]

print("Per basin")
df_temp = calc_area.current_area(
    in_geoscale=basins,
    geoscale_field="Basins",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="Basins",
    ref_csv="data/basins.csv"
)
df_temp.rename(columns={"Basins": "Basin"}, inplace=True)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC10")
df_temp = calc_area.current_area(
    in_geoscale=huc10,
    geoscale_field="HUC10",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_temp = prep_csv.add_study_area(
    df=df_temp,
    geoscale_field="HUC10",
    ref_csv="data/HUC10.csv"
)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC12")
df_temp = calc_area.current_area(
    in_geoscale=huc12,
    geoscale_field="HUC12",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
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
df_temp = calc_area.current_area(
    in_geoscale=temp_geoscale,
    geoscale_field="State_Area",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
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
df_temp = calc_area.current_area(
    in_geoscale=temp_geoscale,
    geoscale_field="Town_State",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
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
df_temp = calc_area.current_area(
    in_geoscale=temp_geoscale,
    geoscale_field="Town_Area",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
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
    "Year", "Percent_Forest", "Percent_Developed", "Percent_Developed_Open", "Percent_Developed_Low", 
    "Percent_Developed_Medium", "Percent_Developed_High", "Agricultural_Acres", "Barren_Acres", "Shrubland_Acres", 
    "Grassland_Acres", "Forest_Acres", "Developed_Acres", "Developed_Open_Acres", "Developed_Low_Acres", 
    "Developed_Medium_Acres", "Developed_High_Acres", "Water_Acres", "Wetland_Acres", "Total_Acres"
]]

print("\nDOWNLOADING FILES")
print("Saving csv")
df_acres.to_csv(csv_folder / csv_final, index=False)

print("Saving raster")
print("\tProjecting to UTM Zone 19N NAD 1983")
arcpy.management.ProjectRaster(
    in_raster=temp_nlcd,
    out_raster=nlcd_final,
    out_coor_system=arcpy.SpatialReference("NAD 1983 UTM Zone 19N")
)

print("\nCLEARING SCRATCH FOLDER")
arcpy.Delete_management(arcpy.env.scratchFolder)

print("\nDONE")
