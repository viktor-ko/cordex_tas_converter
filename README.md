![](https://github.com/viktor-ko/cordex_tas_converter/blob/master/temperature%202020-2100.gif)
# CORDEX Data Processing

This script automatizes the handling of Coordinated Regional Climate Downscaling Experiment [(CORDEX) temperature data from Copernicus CDS](https://cds.climate.copernicus.eu/datasets/projections-cordex-domains-single-levels?tab=overview): downloading zips, extracting netcdf, unit conversion (from Kelvin to Celsius), reprojecting, and storing in ESRI-compatible multidimensional Cloud Raster Format (CRF) or as Cloud-Optimized GeoTIFF (COG). The resulting CRF file is ready for animated visualisation of seasonal data and hosting in ArcGIS online.

## Project Structure
- `CORDEX_tas.py`: Main file
- `utils.py`: Functions for data processing
- `utils_arcpy.py`: Functions for data processing involved arcpy module

## References
1. [CDS Toolbox documentation - Retrieving data](https://cds.climate.copernicus.eu/toolbox/doc/how-to/1_how_to_retrieve_data/1_how_to_retrieve_data.html)
2. [Choosing CRS / PROJ4 string for EURO-Cordex rotated pole projection?](https://gis.stackexchange.com/questions/272483/choosing-crs-proj4-string-for-euro-cordex-rotated-pole-projection)
3. [CORDEX documentation](https://confluence.ecmwf.int/display/CKB/CORDEX%3A+Regional+climate+projections)
4. [CORDEX regional climate model data on single levels in the Copernicus Climate Data Store](https://cds.climate.copernicus.eu/cdsapp#!/dataset/projections-cordex-domains-single-levels?tab=doc)
5. [GDAL gdalwarp documentation](https://gdal.org/programs/gdalwarp.html)
7. [PROJ 9.3.1 documentation — General Oblique Transformation](https://proj.org/operations/projections/ob_tran.html)
8. [Working with Multidimensional Scientific Data Using Python](https://www.esri.com/content/dam/esrisites/en-us/events/conferences/2020/developer-summit/working-with-multi-dimensional-scientific-data-using-python.pdf)
