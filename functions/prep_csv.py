import pandas as pd


def add_study_area(df, geoscale_field, ref_csv):
    """
    add_study_area() updates the input dataframe by adding column(s) by adding the study area and any relevant HUC
    names.

    :param df: Input dataframe.
    :param geoscale_field: String. Name of field containing geoscale name or ID.
    :param ref_csv: String. Path to reference CSV with paired columns for HUC number and HUC name.
    """

    print("\tAdding HUC name")
    df[geoscale_field] = df["Geoscale_Name"]
    if geoscale_field in ["HUC10", "HUC12"]:
        df[geoscale_field] = df[geoscale_field].astype(float)  # Set column to float
        df = df[df[geoscale_field] != 999999]  # Drop rows with no HUC
    df_ref = pd.read_csv(ref_csv)
    df = df.join(df_ref.set_index(geoscale_field), on=geoscale_field)

    return df


def split_geoscale(in_df, geoscale, source_year, nbep_year, out_path, csv_prefix="LANDUSE_"):
    """
    split_geoscale() filters the input dataframe

    :param in_df: Input dataframe.
    :param geoscale: String. Name of geoscale to filter column "Geoscale" by. Examples: "Basin", "HUC10"
    :param nbep_year: Integer. Current year.
    :param source_year: String or integer. Data source year.
    :param out_path: Path. Location to save output csv.
    :param csv_prefix: String. Prefix to csv name. Default "NLCD_".
    """

    print("\tFiltering data")
    df = in_df.copy()
    df = df[df["Geoscale"] == geoscale]

    print("\tDropping extra columns")
    df.drop(columns=["Geoscale", "Geoscale_Name"], inplace=True)  # No longer needed
    df.dropna(how='all', axis=1, inplace=True)  # Drop empty columns

    print("\tAdding metadata columns")
    df["Data_Source"] = "USGS"
    df["Source_Year"] = source_year
    df["NBEP_Year"] = nbep_year

    print("\tSaving csv")
    csv_name = csv_prefix + geoscale + "_NBEP" + str(nbep_year) + ".csv"
    out_csv = out_path / csv_name
    df.to_csv(out_csv, index=False)

    return
