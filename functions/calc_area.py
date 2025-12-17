import arcpy
import pandas as pd


def current_area(in_geoscale, geoscale_field, in_nlcd, nlcd_year):
    """
    calc_area() does BLA BLA BLA

    :param in_geoscale: Path and file name for raster geoscale.
    :param geoscale_field: String. Name of field containing geoscale names.
    :param in_nlcd: Path and file name for NLCD raster.
    :param nlcd_year: Integer. Source year for NLCD data.
    """
    out_table = arcpy.env.scratchFolder + "/temp_table.dbf"

    print("\tCalculating area")
    arcpy.sa.TabulateArea(
        in_zone_data=in_geoscale,
        zone_field=geoscale_field,
        in_class_data=in_nlcd,
        class_field="LAND_USE",
        out_table=out_table,
        processing_cell_size=in_nlcd
    )

    print("\tConverting to dataframe")
    df = arcpy.da.TableToNumPyArray(
        in_table=out_table,
        field_names="*"
    )
    df = pd.DataFrame(df)

    print("\tCalculating acres, % land")
    df['Geoscale'] = geoscale_field
    df['Geoscale_Name'] = df[geoscale_field.upper()]
    df['Year'] = nlcd_year
    df['Agricultural_Acres'] = df['AGRICULTUR'] * 0.000001 * 247
    df['Barren_Acres'] = df['BARREN_LAN'] * 0.000001 * 247
    df['Shrubland_Acres'] = df['BRUSHLAND'] * 0.000001 * 247
    df['Forest_Acres'] = df['FOREST_LAN'] * 0.000001 * 247
    df['Developed_Acres'] = df['URBAN_OR_B'] * 0.000001 * 247
    df['Water_Acres'] = df['WATER'] * 0.000001 * 247
    df['Wetland_Acres'] = df['WETLAND'] * 0.000001 * 247
    df["Total_Acres"] = (
            df['Agricultural_Acres'] + df['Barren_Acres'] + df['Shrubland_Acres'] + df['Forest_Acres'] +
            df['Developed_Acres'] + df['Water_Acres'] + df['Wetland_Acres']
    )
    df["Percent_Developed"] = df["Developed_Acres"] / df["Total_Acres"] * 100
    df["Percent_Forest"] = df["Forest_Acres"] / df["Total_Acres"] * 100
    df = df[[
        "Geoscale", "Geoscale_Name", "Year", "Percent_Developed", "Percent_Forest", "Agricultural_Acres",
        "Barren_Acres", "Shrubland_Acres", "Forest_Acres", "Developed_Acres", "Water_Acres", "Wetland_Acres",
        "Total_Acres"
    ]]

    return df
