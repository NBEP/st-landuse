import arcpy


def prep_geoscale(in_features, in_field, out_features):
    """
    prep_geoscale() projects input vectors to Albers Equal Conical Area and converts them to a raster.

    :param in_features: Raster. Path and file name for input vector.
    :param in_field: String. Field used to
    :param out_features: Raster. Path and file name for output raster.
    """
    in_features = str(in_features)
    out_features = str(out_features)
    temp_shp = arcpy.env.scratchFolder + "/temp_projection.shp"

    print("\tProjecting to Albers Equal Conical Area")
    arcpy.management.Project(
        in_dataset=in_features,
        out_dataset=temp_shp,
        out_coor_system="Albers"
    )

    print("\tSaving as raster")
    arcpy.conversion.PolygonToRaster(
        in_features=temp_shp,
        value_field=in_field,
        out_rasterdataset=out_features,
        cell_assignment="MAXIMUM_AREA"
    )

    return


def prep_nlcd(in_features, out_features, clip_boundaries):
    """
    prep_nlcd() clips NLCD raster data to NBEP boundaries and reclassifies the data as 7 land types: Agricultural Land,
    Barren Land, Brushland, Forest Land, Urban or Build up, Water, and Wetland.

    :param in_features: Raster. National land cover database layer.
    :param out_features: Raster. Path and file name for output raster.
    :param clip_boundaries: Raster. Template used to clip NLCD data to appropriate boundaries.
    """
    in_features = str(in_features)
    out_features = str(out_features)
    clip_boundaries = str(clip_boundaries)
    temp_clip = arcpy.env.scratchFolder + "/temp_clip.tif"

    print("\tClipping to NBEP region")
    arcpy.management.Clip(
        in_raster=in_features,
        in_template_dataset=clip_boundaries,
        out_raster=temp_clip,
        maintain_clipping_extent="MAINTAIN_EXTENT"
    )

    print("\tReclassifying land use")
    # Reclassify land use classes
    new_class = arcpy.sa.Reclassify(
        temp_clip,
        reclass_field="Value",
        remap="0 NODATA;11 6;21 5;22 5;23 5;24 5;31 2;41 4;42 4;43 4;52 3;71 1;81 1;82 1;90 7;95 7",
        missing_values="NODATA"
    )
    new_class.save(out_features)

    arcpy.management.AddField(
        in_table=out_features,
        field_name="LAND_USE",
        field_type="TEXT",
        field_alias="LAND USE"
    )
    arcpy.management.CalculateField(
        in_table=out_features,
        field="LAND_USE",
        expression="Reclass(!Value!)",
        expression_type="PYTHON3",
        code_block="""def Reclass(Value):
            reclass = {
                1: \"Agricultural Land\",
                2: \"Barren Land\",
                3: \"Brushland\",
                4: \"Forest Land\",
                5: \"Urban or Build up\",
                6: \"Water\",
                7: \"Wetland\",
            }
            return reclass.get(Value)
            """
    )

    return
