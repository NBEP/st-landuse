# Land Use

Python scripts used to process and analyze land use data for the [Narragansett Bay Estuary Program](https://www.nbep.org/)'s 2027 State of the Waterways report. 

## Scripts

### 1_calc_landuse.py

Calculates acres and percent land use at seven different geoscales. Run once per land use dataset.

#### Data Sources
* [Annual NLCD Land Cover](https://www.sciencebase.gov/catalog/item/697b9279b66b0197c3043cc3), series 1, USGS 2026
* [NBEP Study Areas](https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/datasets/73cc1e5845c247e2959ac141f9b8c4b5_0/explore?location=41.835903%2C-71.334937%2C9), NBEP 2017
* [Major River Basin Boundaries](https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/datasets/218fdc6c542d46f8bb111c82e7548a5e_0/explore?location=41.835903%2C-71.334937%2C9), NBEP 2017
* [HUC10](https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/datasets/5210cd11b74f411fb41a6619bfd4a4cd_0/explore?location=41.835903%2C-71.334937%2C9), NBEP 2017
* [HUC12](https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/datasets/5305bb874b994a7e923e6cdfebc8943f_0/explore?location=41.835903%2C-71.334937%2C9), NBEP 2017
* [NBEP Study Areas with State Boundaries](https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/datasets/a311a1c484f64318a6c50235420a0ea5_0/explore?location=41.835903%2C-71.334937%2C9), NBEP 2017
* [Town Boundaries](https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/datasets/e9613c4c7cb04f8e933aed4ca06a2b25_0/explore?location=41.878702%2C-71.267013%2C9), NBEP 2017
* [Study Areas with Town Boundaries](https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/datasets/d70caca7abd74e78a23d6942d0fb4ed1_0/explore?location=41.835903%2C-71.334937%2C9), NBEP 2017
* [Bays](https://narragansett-bay-estuary-program-nbep.hub.arcgis.com/datasets/2dec09e1b4d74feab9a2c0e30bf8722b_0/explore?location=41.606530%2C-71.478778%2C10), NBEP 2017

#### Outputs
* 1 raster
* 1 csv summarizing percent, area impervious cover

### 2_calc_change.py

Combines csv output from previous step and splits data in to a separate csv for each geoscale. Also calculates net and percent change between years.

#### Data Sources
* csv output(s) from previous step

#### Outputs
* 1 csv per geoscale (7 files total)

## Use Limitations
This dataset is provided 'as is'. The producer(s) of this dataset, contributors to this dataset, and the Narragansett 
Bay Estuary Program (NBEP) do not make any warranties of any kind for this dataset, and are not liable for any loss or 
damage however and whenever caused by any use of this dataset. There are no restrictions or legal prerequisites for 
using the data. Once acquired, any modification made to the data must be noted in the metadata. Please acknowledge both 
NBEP and the primary producer(s) of this dataset or any derived products.

These data are intended for use as a tool for reference, display, and general GIS analysis purposes only. It is the 
responsibility of the data user to use the data appropriately and consistent with the limitations of geospatial data in 
general and these data in particular. The information contained in these data may be dynamic and could change over time. 
The data accuracy is checked against best available sources which may be dated. The data are not better than the 
original sources from which they are derived. These data are not designed for use as a primary regulatory tool in 
permitting or siting decisions and are not a legally authoritative source for the location of natural or manmade 
features. The depicted boundaries, interpretations, and analysis derived from have not been verified at the site level 
them and do not eliminate the need for onsite sampling, testing, and detailed study of specific sites.

This project was funded by agreements by the Environmental Protection Agency (EPA) to Roger Williams University (RWU) in 
partnership with the Narragansett Bay Estuary Program. Although the information in this document has been funded wholly 
or in part by EPA under the agreement CE00A01716 to RWU, it has not undergone the Agency’s publications review process 
and therefore, may not necessarily reflect the views of the Agency and no official endorsement should be inferred. The 
viewpoints expressed here do not necessarily represent those of the Narragansett Bay Estuary Program, RWU, or EPA nor 
does mention of trade names, commercial products, or causes constitute endorsement or recommendation for use. 
