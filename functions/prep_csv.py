import pandas as pd


def split_geoscale(in_df, geoscale, source_year, nbep_year, out_path, csv_prefix="NLCD_"):
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

    print("\tAdding metadata columns")
    df["Data_Source"] = "NLCD"
    df["Source_Year"] = source_year
    df["NBEP_Year"] = nbep_year

    print("\tSaving csv")
    csv_name = csv_prefix + geoscale + "_NBEP" + str(nbep_year) + ".csv"
    out_csv = out_path / csv_name
    df.to_csv(out_csv)

    return
