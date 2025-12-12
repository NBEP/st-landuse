import arcpy
from arcpy.sa import *

# Check out any necessary licenses.
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("spatial")

__all__ = ["prep_raster"]