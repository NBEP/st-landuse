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
nlcd_year = 2016
nlcd = "Annual_NLCD_LndCov_2016_CU_C1V1.tif"

clip_boundaries = "landuse_int.gdb/source_copy/Town_Bay_Merge"  # Set bounding box
clip_final = "landuse_int.gdb/source_copy/ALL_STUDYAREAS_NBEP2017"  # Clip NLCD for hub

basins = "landuse_int.gdb/source_copy/BASINS_NBEP2017"
huc10 = "landuse_int.gdb/source_copy/HUC10_NBEP2017"
huc12 = "landuse_int.gdb/source_copy/HUC12_NBEP2017"
studyarea = "landuse_int.gdb/source_copy/STUDYAREAS_NBEP2017"
state_studyarea = "landuse_int.gdb/geoscales/states_by_studyarea"
town = "landuse_int.gdb/source_copy/Town_Bay_Merge"
town_studyarea = "landuse_int.gdb/geoscales/towns_by_studyarea"

# Define OUTPUTS
nlcd_final = "landuse_int.gdb/NLCD_" + str(nlcd_year) + "_NBEP2025"
csv_final = "NLCD_" + str(nlcd_year) + "_NBEP2025.csv"

# RUN SCRIPT ----------------------------------------------------------------------------------------------------------
temp_buffer = arcpy.env.scratchFolder + "/temp_buffer.shp"
temp_clip = arcpy.env.scratchFolder + "/temp_boundaries.shp"
temp_nlcd = arcpy.env.scratchFolder + "/temp_nlcd.tif"
temp_raster = arcpy.env.scratchFolder + "/temp_raster.tif"

print("\nSETTING DEFAULT VALUES")
print("Setting snap raster")
arcpy.env.snapRaster = nlcd
print("Retrieving NLCD spatial reference")
spatial_ref = arcpy.Describe(nlcd).spatialReference

print("\nPROCESSING", nlcd_year, "NLCD DATA")
print("Setting clip boundaries")
print("\tAdding 100m buffer")
arcpy.analysis.Buffer(
    in_features=clip_boundaries,
    out_feature_class=temp_buffer,
    buffer_distance_or_field="100 Meters",
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
    clip_boundaries=temp_clip
)

print("\nCALCULATING AREA")
print("Per basin")
prep_raster.prep_geoscale(
    in_features=basins,
    in_field="Basin",
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_acres = calc_area.current_area(
    in_geoscale=temp_raster,
    geoscale_field="Basin",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)

print("Per HUC10")
prep_raster.prep_geoscale(
    in_features=huc10,
    in_field="HUC10_Name",
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.current_area(
    in_geoscale=temp_raster,
    geoscale_field="HUC10_Name",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per HUC12")
prep_raster.prep_geoscale(
    in_features=huc12,
    in_field="HUC12_Name",
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.current_area(
    in_geoscale=temp_raster,
    geoscale_field="HUC12_Name",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per study area")
prep_raster.prep_geoscale(
    in_features=studyarea,
    in_field="Study_Area",
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.current_area(
    in_geoscale=temp_raster,
    geoscale_field="Study_Area",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per state per study area")
prep_raster.prep_geoscale(
    in_features=state_studyarea,
    in_field="State_Area",
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.current_area(
    in_geoscale=temp_raster,
    geoscale_field="State_Area",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per town")
prep_raster.prep_geoscale(
    in_features=town,
    in_field="Town_Name",
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.current_area(
    in_geoscale=temp_raster,
    geoscale_field="Town_Name",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres = pd.concat([df_acres, df_temp])

print("Per town per study area")
prep_raster.prep_geoscale(
    in_features=town_studyarea,
    in_field="Town_Area",
    out_features=temp_raster,
    out_coor_system=spatial_ref
)
df_temp = calc_area.current_area(
    in_geoscale=temp_raster,
    geoscale_field="Town_Area",
    in_nlcd=temp_nlcd,
    nlcd_year=nlcd_year
)
df_acres = pd.concat([df_acres, df_temp])

print("\nDOWNLOADING FILES")
print("Saving csv")
df_acres.to_csv(csv_folder / csv_final)

print("Saving raster")
print("\tProjecting to UTM Zone 19N NAD 1983")
arcpy.management.ProjectRaster(
    in_raster=temp_nlcd,
    out_raster=temp_raster,
    out_coor_system=arcpy.SpatialReference("NAD 1983 UTM Zone 19N")
)
print("\tClipping data")
arcpy.management.Clip(
    in_raster=temp_raster,
    out_raster=nlcd_final,
    in_template_dataset=clip_final,
    clipping_geometry="ClippingGeometry"
)
print("\nDONE")
