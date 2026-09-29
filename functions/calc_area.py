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
    df["Agriculture_Acres"] = df["AGRICULTUR"] * 0.000001 * 247
    df["Barren_Acres"] = df["BARREN"] * 0.000001 * 247
    df["Shrubland_Acres"] = df["BRUSHLAND"] * 0.000001 * 247
    df["Grassland_Acres"] = df["GRASSLAND"] * 0.000001 * 247
    df["Forest_Acres"] = df["FOREST"] * 0.000001 * 247
    df["Developed_Open_Acres"] = df["DEV_OPEN"] * 0.000001 * 247
    df["Developed_Low_Acres"] = df["DEV_LOW"] * 0.000001 * 247
    df["Developed_Medium_Acres"] = df["DEV_MED"] * 0.000001 * 247
    df["Developed_High_Acres"] = df["DEV_HIGH"] * 0.000001 * 247
    df["Developed_Acres"] = (
            df["Developed_Open_Acres"] + df["Developed_Low_Acres"] + df["Developed_Medium_Acres"] +
            df["Developed_High_Acres"]
    )
    df["Water_Acres"] = df["WATER"] * 0.000001 * 247
    df["Wetland_Acres"] = df["WETLAND"] * 0.000001 * 247
    df["Total_Acres"] = (
            df["Agriculture_Acres"] + df["Barren_Acres"] + df["Shrubland_Acres"] + df["Grassland_Acres"] +
            df["Forest_Acres"] + df["Developed_Acres"] + df["Water_Acres"] + df["Wetland_Acres"]
    )
    df["Percent_Developed_Open"] = df["Developed_Open_Acres"] / df["Total_Acres"] * 100
    df["Percent_Developed_Low"] = df["Developed_Low_Acres"] / df["Total_Acres"] * 100
    df["Percent_Developed_Medium"] = df["Developed_Medium_Acres"] / df["Total_Acres"] * 100
    df["Percent_Developed_High"] = df["Developed_High_Acres"] / df["Total_Acres"] * 100
    df["Percent_Developed"] = df["Developed_Acres"] / df["Total_Acres"] * 100
    df["Percent_Forest"] = df["Forest_Acres"] / df["Total_Acres"] * 100
    df = df[[
        "Geoscale", "Geoscale_Name", "Year", "Percent_Forest", "Percent_Developed", "Percent_Developed_Open",
        "Percent_Developed_Low", "Percent_Developed_Medium", "Percent_Developed_High", "Agriculture_Acres",
        "Barren_Acres", "Shrubland_Acres", "Grassland_Acres", "Forest_Acres", "Developed_Acres", "Developed_Open_Acres",
        "Developed_Low_Acres", "Developed_Medium_Acres", "Developed_High_Acres", "Water_Acres", "Wetland_Acres",
        "Total_Acres"
    ]]

    return df


def change_area(in_geoscale, geoscale_field, nlcd_change, nlcd_same, year_range):
    """
    change_area() generates a table containing a summary of acres land that changed land use type. The data is
    summarized at the relevant geoscale.

    :param in_geoscale: Path and file name for raster geoscale.
    :param geoscale_field: String. Name of field containing geoscale names.
    :param nlcd_change: Path and file name for NLCD raster containing land use classes that changed between years.
    :param nlcd_same: Path and file for raster containing land use classes that stayed the same between years.
    :param year_range: String. Year range, eg "2000-2024"
    """
    out_table = arcpy.env.scratchFolder + "/temp_table.dbf"

    print("\tProcessing change raster")
    print("\t\tCalculating area")
    arcpy.sa.TabulateArea(
        in_zone_data=in_geoscale,
        zone_field=geoscale_field,
        in_class_data=nlcd_change,
        class_field="Class_name",
        out_table=out_table,
        processing_cell_size=nlcd_change
    )

    print("\t\tConverting to dataframe")
    df1 = arcpy.da.TableToNumPyArray(
        in_table=out_table,
        field_names="*"
    )
    df1 = pd.DataFrame(df1)

    print("\tProcessing unchanged raster")
    print("\t\tCalculating area")
    arcpy.sa.TabulateArea(
        in_zone_data=in_geoscale,
        zone_field=geoscale_field,
        in_class_data=nlcd_same,
        class_field="Class_name",
        out_table=out_table,
        processing_cell_size=nlcd_same
    )

    print("\t\tConverting to dataframe")
    df2 = arcpy.da.TableToNumPyArray(
        in_table=out_table,
        field_names="*"
    )
    df2 = pd.DataFrame(df2)

    print(df2.columns)

    print("\tJoining tables")
    df = pd.merge(df1, df2, on=geoscale_field.upper(), how='outer')

    print("\tConverting table from wide to long")
    df = pd.melt(
        df,
        id_vars=geoscale_field.upper(),
        value_vars=[
            "A_1_1", "A_1_21", "A_1_22", "A_1_23", "A_1_24", "A_1_3", "A_1_4", "A_1_5", "A_1_7", "A_1_8", "A_1_9",
            "A_21_1", "A_21_21", "A_21_22", "A_21_23", "A_21_24", "A_21_3", "A_21_4", "A_21_5", "A_21_7", "A_21_8",
            "A_21_9", "A_22_1", "A_22_21", "A_22_22", "A_22_23", "A_22_24", "A_22_3", "A_22_4", "A_22_5", "A_22_7",
            "A_22_8", "A_22_9", "A_23_1", "A_23_21", "A_23_22", "A_23_23", "A_23_24", "A_23_3", "A_23_4", "A_23_5",
            "A_23_7", "A_23_8", "A_23_9", "A_24_1", "A_24_21", "A_24_22", "A_24_23", "A_24_24", "A_24_3", "A_24_4",
            "A_24_5", "A_24_7", "A_24_8", "A_24_9", "A_3_1", "A_3_21", "A_3_22", "A_3_23", "A_3_24", "A_3_3", "A_3_4",
            "A_3_5", "A_3_7", "A_3_8", "A_3_9", "A_4_1", "A_4_21", "A_4_22", "A_4_23", "A_4_24", "A_4_3", "A_4_4",
            "A_4_5", "A_4_7", "A_4_8", "A_4_9", "A_5_1", "A_5_21", "A_5_22", "A_5_23", "A_5_24", "A_5_3", "A_5_4",
            "A_5_5", "A_5_7", "A_5_8", "A_5_9", "A_7_1", "A_7_21", "A_7_22", "A_7_23", "A_7_24", "A_7_3", "A_7_4",
            "A_7_5", "A_7_7", "A_7_8", "A_7_9", "A_8_1", "A_8_21", "A_8_22", "A_8_23", "A_8_24", "A_8_3", "A_8_4",
            "A_8_5", "A_8_7", "A_8_8", "A_8_9", "A_9_1", "A_9_21", "A_9_22", "A_9_23", "A_9_24", "A_9_3", "A_9_4",
            "A_9_5", "A_9_7", "A_9_8", "A_9_9"
        ],
        value_name="Acres"
    )

    print("\tUpdating fields")
    df["variable"] = df["variable"].replace("A_", "", regex=True)
    df["variable"] = df["variable"].replace("21", "Developed, Open Space", regex=True)
    df["variable"] = df["variable"].replace("22", "Developed, Low Intensity", regex=True)
    df["variable"] = df["variable"].replace("23", "Developed, Medium Intensity", regex=True)
    df["variable"] = df["variable"].replace("24", "Developed, High Intensity", regex=True)
    df["variable"] = df["variable"].replace("1", "Water", regex=True)
    df["variable"] = df["variable"].replace("3", "Barren", regex=True)
    df["variable"] = df["variable"].replace("4", "Forest", regex=True)
    df["variable"] = df["variable"].replace("5", "Brushland", regex=True)
    df["variable"] = df["variable"].replace("7", "Grassland", regex=True)
    df["variable"] = df["variable"].replace("8", "Agriculture", regex=True)
    df["variable"] = df["variable"].replace("9", "Wetland", regex=True)

    df[["Start_Category", "End_Category"]] = df["variable"].str.split("_", expand=True)

    print("\tCalculating acres, % land")
    df["Geoscale"] = geoscale_field
    df["Geoscale_Name"] = df[geoscale_field.upper()]
    df["Year"] = year_range
    df["Acres"] = df["Acres"] * 0.000001 * 247

    print("\tDropping extra columns")
    df = df[["Geoscale", "Geoscale_Name", "Year", "Start_Category", "End_Category", "Acres"]]

    return df
