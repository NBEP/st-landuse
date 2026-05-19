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
temp_buffer = arcpy.env.scratchFolder + "/temp_buffer.shp"
temp_clip = arcpy.env.scratchFolder + "/temp_boundaries.shp"
temp_nlcd = arcpy.env.scratchFolder + "/temp_nlcd.tif"
temp_raster = arcpy.env.scratchFolder + "/temp_raster.tif"

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
nlcd_filter.save(temp_raster)

# QUERY: USE RAW NLCD DATA?

# Rename class name to code system - eg 2_3 for class 2 to class 3
# Rewrite calc_acre function for this use case
# For output csv - one for to/from forest and one for to/from dev? To keep # columns SLIGHTLY manageable?
# (~20 for forest, ~45 for dev)
# could flatten further by grouping dev as 1 category except when looking at changes from dev to dev?
# Then it's 14 columns for forest, 7 + 7 + 4 * 4 = 14 + 16 = 30 columns for dev
