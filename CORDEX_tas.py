import os
from utils import download_cordex_data, extract_cordex_data, convert_kelvin_celsius, reproject_netcdf, \
      seasonal_tif_files, cloud_optimized_geotiff
# from utils_arcpy import create_mosaic_from_netcdf, create_crf

# download data
download_cordex_data()

# extract nc files, delete zips after
extract_cordex_data(delete_zip=True)

# convert to Celsius, delete original nc files after
convert_kelvin_celsius(delete_kelvin=True)

'''
If you have ArcGIS Pro installed, you can use the arcpy module to create a cloud raster from the netcdf files.
Before run the code below, change the python interpreter to the one that comes with ArcGIS Pro.
In PyCharm: Add New Interpreter - Add Local Interpreter - Virtualenv Environment - Enviroment: Existing, 
Interpreter path: "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
'''

# # Create arcgis mosaic dataset from netcdf files
# create_mosaic_from_netcdf()
#
# # create cloud raster file from mosaic dataset to publish to ArcGIS Online
# create_crf()

'''
Alternatively, if you don't use ArcGIS, you can use open source format for hosting rasters - Cloud Optimized GeoTIFF (COG)
This will require additional steps - reproject the netcdf files to WGS84, convert to tif, and then convert to COG.
Don't forget to change the python interpreter back to the default one.
'''

# #reproject netcdf to WGS84 and convert to tif
# # os.system(f'pip install GDAL-3.4.3-cp39-cp39-win_amd64.whl')
# reproject_netcdf() #USE GDAL wheel 3.4.3 to avoid error

# #Convert 8 reprojected tifs to one cloud optimized geotiff
# #os.system(f'pip install GDAL-3.8.2-cp39-cp39-win_amd64.whl')
# cloud_optimized_geotiff() #USE GDAL wheel 3.8.2 to avoid error

# #If needed, you can split reprojected tifs (each contain 40 bands) to individual seasonal tif files (1 band = 3 months)
# seasonal_tif_files()