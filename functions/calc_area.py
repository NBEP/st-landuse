import arcpy
import pandas as pd


def current_area(in_geoscale, geoscale_field, in_nlcd, nlcd_year):
    """
    calc_area() generates a table containing a breakdown of acres and percent land cover for all land classes at the
    relevant geoscale.

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
    df["Geoscale"] = geoscale_field
    df["Geoscale_Name"] = df[geoscale_field.upper()]
    df["Year"] = nlcd_year
    df["Agricultural_Acres"] = df["AGRICULTUR"] * 0.000001 * 247
    df["Barren_Acres"] = df["BARREN"] * 0.000001 * 247
    df["Shrubland_Acres"] = df["BRUSHLAND"] * 0.000001 * 247
    df["Grassland_Acres"] = df["GRASSLAND"] * 0.000001 * 247
    df["Forest_Acres"] = df["FOREST"] * 0.000001 * 247
    df["Open_Developed_Acres"] = df["DEV_OPEN"] * 0.000001 * 247
    df["Low_Developed_Acres"] = df["DEV_LOW"] * 0.000001 * 247
    df["Medium_Developed_Acres"] = df["DEV_MED"] * 0.000001 * 247
    df["High_Developed_Acres"] = df["DEV_HIGH"] * 0.000001 * 247
    df["Developed_Acres"] = (
            df["Open_Developed_Acres"] + df["Low_Developed_Acres"] + df["Medium_Developed_Acres"] +
            df["High_Developed_Acres"]
    )
    df["Water_Acres"] = df["WATER"] * 0.000001 * 247
    df["Wetland_Acres"] = df["WETLAND"] * 0.000001 * 247
    df["Total_Acres"] = (
            df["Agricultural_Acres"] + df["Barren_Acres"] + df["Shrubland_Acres"] + df["Grassland_Acres"] +
            df["Forest_Acres"] + df["Developed_Acres"] + df["Water_Acres"] + df["Wetland_Acres"]
    )
    df["Percent_Open_Developed"] = df["Open_Developed_Acres"] / df["Total_Acres"] * 100
    df["Percent_Low_Developed"] = df["Low_Developed_Acres"] / df["Total_Acres"] * 100
    df["Percent_Medium_Developed"] = df["Medium_Developed_Acres"] / df["Total_Acres"] * 100
    df["Percent_High_Developed"] = df["High_Developed_Acres"] / df["Total_Acres"] * 100
    df["Percent_Developed"] = df["Developed_Acres"] / df["Total_Acres"] * 100
    df["Percent_Forest"] = df["Forest_Acres"] / df["Total_Acres"] * 100
    df = df[[
        "Geoscale", "Geoscale_Name", "Year",  "Percent_Forest", "Percent_Developed", "Percent_Open_Developed",
        "Percent_Low_Developed", "Percent_Medium_Developed", "Percent_High_Developed", "Agricultural_Acres",
        "Barren_Acres", "Shrubland_Acres", "Grassland_Acres", "Forest_Acres", "Developed_Acres", "Open_Developed_Acres",
        "Low_Developed_Acres", "Medium_Developed_Acres", "High_Developed_Acres", "Water_Acres", "Wetland_Acres",
        "Total_Acres"
    ]]

    return df


def change_area(in_geoscale, geoscale_field, in_nlcd, year_range):
    """
    change_area() generates a table containing a summary of acres land that changed land use type. The data is
    summarized at the relevant geoscale.

    :param in_geoscale: Path and file name for raster geoscale.
    :param geoscale_field: String. Name of field containing geoscale names.
    :param in_nlcd: Path and file name for NLCD raster.
    :param year_range: String. Year range, eg "2000-2024"
    """
    out_table = arcpy.env.scratchFolder + "/temp_table.dbf"

    print("\tCalculating area")
    arcpy.sa.TabulateArea(
        in_zone_data=in_geoscale,
        zone_field=geoscale_field,
        in_class_data=in_nlcd,
        class_field="Class_name",
        out_table=out_table,
        processing_cell_size=in_nlcd
    )

    print("\tConverting to dataframe")
    df = arcpy.da.TableToNumPyArray(
        in_table=out_table,
        field_names="*"
    )
    df = pd.DataFrame(df)

    print("\tChecking for missing columns")
    all_col = [
        "A_1_4", "A_1_21", "A_1_22", "A_1_23", "A_1_24", "A_3_4", "A_3_21", "A_3_22", "A_3_23", "A_3_24", "A_4_1",
        "A_4_3", "A_4_5", "A_4_7", "A_4_8", "A_4_9", "A_4_21", "A_4_22", "A_4_23", "A_4_24", "A_5_4", "A_5_21",
        "A_5_22", "A_5_23", "A_5_24", "A_7_4", "A_7_21", "A_7_22", "A_7_23", "A_7_24", "A_8_4", "A_8_21", "A_8_22",
        "A_8_23", "A_8_24", "A_9_4", "A_9_21", "A_9_22", "A_9_23", "A_9_24", "A_21_1", "A_22_1", "A_23_1", "A_24_1",
        "A_21_3", "A_22_3", "A_23_3", "A_24_3", "A_21_4", "A_22_4", "A_23_4", "A_24_4", "A_21_5", "A_22_5", "A_23_5",
        "A_24_5", "A_21_7", "A_22_7", "A_23_7", "A_24_7", "A_21_8", "A_22_8", "A_23_8", "A_24_8", "A_21_9", "A_22_9",
        "A_23_9", "A_24_9", "A_21_22", "A_21_23", "A_21_24", "A_22_21", "A_22_23", "A_22_24", "A_23_21", "A_23_22",
        "A_23_24", "A_24_21", "A_24_22", "A_24_23"
    ]
    df_col = list(df.columns)
    missing_col = list(set(all_col) - set(df_col))

    if len(missing_col) > 0:
        df[missing_col] = 0

    print("\tCalculating acres, % land")
    to_acres = 0.000001 * 247

    df["Geoscale"] = geoscale_field
    df["Geoscale_Name"] = df[geoscale_field.upper()]
    df["Year"] = year_range
    df["Water_to_Forest_Acres"] = df["A_1_4"] * to_acres
    df["Water_to_Developed_Acres"] = (df["A_1_21"] + df["A_1_22"] + df["A_1_23"] + df["A_1_24"]) * to_acres
    df["Barren_to_Forest_Acres"] = df["A_3_4"] * to_acres
    df["Barren_to_Developed_Acres"] = (df["A_3_21"] + df["A_3_22"] + df["A_3_23"] + df["A_3_24"]) * to_acres
    df["Forest_to_Water_Acres"] = df["A_4_1"] * to_acres
    df["Forest_to_Barren_Acres"] = df["A_4_3"] * to_acres
    df["Forest_to_Brushland_Acres"] = df["A_4_5"] * to_acres
    df["Forest_to_Grassland_Acres"] = df["A_4_7"] * to_acres
    df["Forest_to_Agriculture_Acres"] = df["A_4_8"] * to_acres
    df["Forest_to_Wetland_Acres"] = df["A_4_9"] * to_acres
    df["Forest_to_Developed_Acres"] = (df["A_4_21"] + df["A_4_22"] + df["A_4_23"] + df["A_4_24"]) * to_acres
    df["Brushland_to_Forest_Acres"] = df["A_5_4"] * to_acres
    df["Brushland_to_Developed_Acres"] = (df["A_5_21"] + df["A_5_22"] + df["A_5_23"] + df["A_5_24"]) * to_acres
    df["Grassland_to_Forest_Acres"] = df["A_7_4"] * to_acres
    df["Grassland_to_Developed_Acres"] = (df["A_7_21"] + df["A_7_22"] + df["A_7_23"] + df["A_7_24"]) * to_acres
    df["Agriculture_to_Forest_Acres"] = df["A_8_4"] * to_acres
    df["Agriculture_to_Developed_Acres"] = (df["A_8_21"] + df["A_8_22"] + df["A_8_23"] + df["A_8_24"]) * to_acres
    df["Wetland_to_Forest_Acres"] = df["A_9_4"] * to_acres
    df["Wetland_to_Developed_Acres"] = (df["A_9_21"] + df["A_9_22"] + df["A_9_23"] + df["A_9_24"]) * to_acres
    df["Developed_to_Water_Acres"] = (df["A_21_1"] + df["A_22_1"] + df["A_23_1"] + df["A_24_1"]) * to_acres
    df["Developed_to_Barren_Acres"] = (df["A_21_3"] + df["A_22_3"] + df["A_23_3"] + df["A_24_3"]) * to_acres
    df["Developed_to_Forest_Acres"] = (df["A_21_4"] + df["A_22_4"] + df["A_23_4"] + df["A_24_4"]) * to_acres
    df["Developed_to_Brushland_Acres"] = (df["A_21_5"] + df["A_22_5"] + df["A_23_5"] + df["A_24_5"]) * to_acres
    df["Developed_to_Grassland_Acres"] = (df["A_21_7"] + df["A_22_7"] + df["A_23_7"] + df["A_24_7"]) * to_acres
    df["Developed_to_Agriculture_Acres"] = (df["A_21_8"] + df["A_22_8"] + df["A_23_8"] + df["A_24_8"]) * to_acres
    df["Developed_to_Wetland_Acres"] = (df["A_21_9"] + df["A_22_9"] + df["A_23_9"] + df["A_24_9"]) * to_acres
    df["Developed_Open_to_Developed_Low_Acres"] = df["A_21_22"] * to_acres
    df["Developed_Open_to_Developed_Medium_Acres"] = df["A_21_23"] * to_acres
    df["Developed_Open_to_Developed_High_Acres"] = df["A_21_24"] * to_acres
    df["Developed_Low_to_Developed_Open_Acres"] = df["A_22_21"] * to_acres
    df["Developed_Low_to_Developed_Medium_Acres"] = df["A_22_23"] * to_acres
    df["Developed_Low_to_Developed_High_Acres"] = df["A_22_24"] * to_acres
    df["Developed_Medium_to_Developed_Open_Acres"] = df["A_23_21"] * to_acres
    df["Developed_Medium_to_Developed_Low_Acres"] = df["A_23_22"] * to_acres
    df["Developed_Medium_to_Developed_High_Acres"] = df["A_23_24"] * to_acres
    df["Developed_High_to_Developed_Open_Acres"] = df["A_24_21"] * to_acres
    df["Developed_High_to_Developed_Low_Acres"] = df["A_24_22"] * to_acres
    df["Developed_High_to_Developed_Medium_Acres"] = df["A_24_23"] * to_acres

    print("\tDropping extra columns")
    df = df[[
        "Geoscale", "Geoscale_Name", "Year",  "Water_to_Forest_Acres", "Water_to_Developed_Acres",
        "Barren_to_Forest_Acres", "Barren_to_Developed_Acres", "Forest_to_Water_Acres", "Forest_to_Barren_Acres",
        "Forest_to_Brushland_Acres", "Forest_to_Grassland_Acres", "Forest_to_Agriculture_Acres",
        "Forest_to_Wetland_Acres", "Forest_to_Developed_Acres", "Brushland_to_Forest_Acres",
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

    return df
