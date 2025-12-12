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
from functions import *

arcpy.env.overwriteOutput = True

# Set working directory, projection
base_folder = Path.cwd().parents[2] / "Data"
scratch_folder = arcpy.env.scratchFolder
gis_folder = base_folder / "int_gisdata" / "landuse_int"

# Define INPUTS
nlcd_year = 2024
nlcd_raster = gis_folder / "Annual_NLCD_LndCov_2024_CU_C1V1.tif"

nlcd_clipbox = gis_folder / "landuse_int.gdb" / "source_copy_albers" / "NLCD_ClipBox_Albers"

raster_basin = ""
raster_huc10 = ""
raster_huc12 = ""
raster_studyarea = ""
raster_state_studyarea = ""
raster_town = ""
raster_town_studyarea = ""

csv_basin = ""
csv_huc10 = ""
csv_huc12 = ""
csv_studyarea = ""
csv_state = ""
csv_town = ""
csv_town_studyarea = ""

# Define OUTPUTS
nlcd_raster_hub = gis_folder / "int_gisdata.gdb" / "NLCD_2024_NBEP2025.tif"
csv_basin_out = ""
csv_huc10_out = ""
csv_huc12_out = ""
csv_studyarea_out = ""
csv_state_out = ""
csv_town_out = ""
csv_town_studyarea_out = ""

# Code ----
nlcd_temp = gis_folder / "nlcd_temp.tif"

print("\nPROCESSING", nlcd_year, "NLCD")
prep_raster.prep_nlcd(
    in_features=nlcd_raster,
    out_features=nlcd_temp,
    clip_boundaries=nlcd_clipbox
)

print("\nCALCULATING ACRES")
print("By basin")
print("\tSaving csv")
print("By HUC10")
print("\tSaving csv")
print("By HUC12")
print("\tSaving csv")
print("By study area")
print("\tSaving csv")
print("By state by study area")
print("\tSaving csv")
print("By town")
print("\tSaving csv")
print("By town by study area")
print("\tSaving csv")

print("\nSAVING RASTER")
print("Projecting to UTM Zone 19N")
# o	Resampling technique: NEAREST
# o	No registration point (Snap Raster will override)
# o	http://desktop.arcgis.com/en/arcmap/10.3/tools/data-management-toolbox/project-raster.htm
