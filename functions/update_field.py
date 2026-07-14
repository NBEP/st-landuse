import arcpy


def merge_field(in_table, out_table, new_field, expression):
    """
    calc_area() generates a table containing a breakdown of acres and percent land cover for all land classes at the
    relevant geoscale.

    :param in_table: The input shapefile.
    :param out_table: The output shapefile.
    :param new_field: String. Name of new field.
    :param expression: The simple calculation expression that will be used to create a value that will populate
    new_field.
    """

    print("\tMerging fields")
    arcpy.management.CopyFeatures(
        in_features=in_table,
        out_feature_class=out_table
    )
    arcpy.management.AddField(
        in_table=out_table,
        field_name=new_field,
        field_type="TEXT"
    )
    arcpy.management.CalculateField(
        in_table=out_table,
        field=new_field,
        expression=expression
    )

    return
