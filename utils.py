import cdsapi
import os
import zipfile
import re
from osgeo import gdal
import netCDF4
from datetime import datetime
from dateutil.relativedelta import relativedelta

#pip install GDAL-3.4.3-cp39-cp39-win_amd64.whl

#standard project home directory
PROJECT_HOME = './cordex'

#Install/update OSGeo4W gdal and proj libraries
#Set OSGeo4W environment variables for GDAL and PROJ
os.environ['PROJ_LIB'] = r'C:\OSGeo4W\share\proj'
os.environ['GDAL_DATA'] = r'C:\OSGeo4W\share\gdal'

#subdirectories for data processing steps
ZIP_DIR = os.path.join(PROJECT_HOME, 'netcdf_zip')
EXTRACT_DIR = os.path.join(PROJECT_HOME, 'netcdf')
CONVERTED_DIR = os.path.join(PROJECT_HOME, 'netcdf_Celsius')
REPROJECTED_DIR = os.path.join(PROJECT_HOME, 'reprojected_tif')
SEASONAL_DIR = os.path.join(PROJECT_HOME, '320_seasonal_tifs')
COG_DIR = os.path.join(PROJECT_HOME, 'cog')

# Ensure that the project structure is created
os.makedirs(ZIP_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)
os.makedirs(REPROJECTED_DIR, exist_ok=True)
os.makedirs(SEASONAL_DIR, exist_ok=True)
os.makedirs(COG_DIR, exist_ok=True)

# Download CORDEX data from the CDS API
def download_cordex_data(start_year=2020, end_year=2100, step=10):

    api_key = '9b956db2-fd01-482d-b264-f26a7e2986aa'  # CDS API key
    api_url = 'https://cds.climate.copernicus.eu/api/'

    # Create a CDS API client
    c = cdsapi.Client(url=api_url, key=api_key)

    # Loop over each decade
    # for this dataset with selected seasonal temporal resolution min start_year = 2010, max end_year = 2100, step must be multiple of 10
    for year in range(start_year, end_year, step):
        # Specify the file path to save the data
        file_path_cordex = os.path.join(ZIP_DIR, f'cordex_tas_{year}_{year+10}.zip')

        # parameters for the CDS API request
        c.retrieve(
            'projections-cordex-domains-single-levels',
            {
                'format': 'zip',
                'domain': 'europe',
                'experiment': 'rcp_4_5', #Representative Concentration Pathway 4.5 - intermediate scenario of greenhouse gas concentration in the atmosphere
                'horizontal_resolution': '0_11_degree_x_0_11_degree',
                'temporal_resolution': 'seasonal_mean', #Selected time period over which the data is averaged (seasonal=3 months)
                'variable': '2m_air_temperature', #temperature of the air at 2m above the surface (mean over the aggregation period)
                'rcm_model': 'mpi_csc_remo2009', #Regional Climate Model
                'gcm_model': 'mpi_m_mpi_esm_lr', #Global Climate Model - provides lateral boundary conditions for the RCM
                'ensemble_member': 'r1i1p1', #Control ensemble member: Realization 1, Initialisation 1, Physics 1
                'start_year': str(year),
                'end_year': str(year+10),
            },
            file_path_cordex
        )
        print('Downloading file to:', file_path_cordex)


# Extract CORDEX data from zip files
def extract_cordex_data(zip_dir=ZIP_DIR, extract_dir=EXTRACT_DIR, delete_zip=False):
    os.makedirs(extract_dir, exist_ok=True)

    # loop over each file in the zip directory
    for filename in os.listdir(zip_dir):
        if filename.endswith('.zip'):
            # construct the full file path
            file_path = os.path.join(zip_dir, filename)

            # open the zip file
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # extract all files to the extract directory
                zip_ref.extractall(extract_dir)

            #Option to delete zip file after extraction
            if delete_zip:
                os.remove(file_path)
                print(f"Deleted zip file: {file_path}")

    # loop over each file in the extract directory
    for filename in os.listdir(extract_dir):
        # check if the file name matches the specified pattern
        match = re.match(r'tas_EUR-11_MPI-M-MPI-ESM-LR_rcp45_r1i1p1_MPI-CSC-REMO2009_v1_sem_(\d{6}-\d{6}).nc', filename)
        if match:
            # construct the old and new file paths
            old_file_path = os.path.join(extract_dir, filename)
            new_file_path = os.path.join(extract_dir, f'tas_{match.group(1)}.nc')

            # check if the new file path already exists
            if os.path.exists(new_file_path):
                # if it does, remove it
                os.remove(new_file_path)

            # rename the file
            os.rename(old_file_path, new_file_path)
    print('Extraction completed')

# Convert temperature from Kelvin to Celsius in NetCDF files
def convert_kelvin_celsius(src_dir=EXTRACT_DIR, dst_dir=CONVERTED_DIR, delete_kelvin=False):
    os.makedirs(dst_dir, exist_ok=True)

    # loop over each netcdf file in the source directory
    for filename in os.listdir(src_dir):
        if filename.endswith('.nc'):
            # construct the source and destination file paths
            src_file_path = os.path.join(src_dir, filename)
            dst_file_path = os.path.join(dst_dir, filename[:-3] + '_Cels.nc')

            # copy file from source to destination
            with open(src_file_path, 'rb') as src_file:
                with open(dst_file_path, 'wb') as dst_file:
                    dst_file.write(src_file.read())

    # loop over each NetCDF file in the destination directory
    for filename in os.listdir(dst_dir):
        if filename.endswith('.nc'):
            # construct file path
            file_path = os.path.join(dst_dir, filename)

            # open NetCDF file for reading and writing
            dataset = netCDF4.Dataset(file_path, 'r+')

            # check if the 'tas' variable exists in the file
            if 'tas' in dataset.variables:
                # read the original temperature data in Kelvin
                tas = dataset.variables['tas'][:]

                # convert temperature from Kelvin to Celsius
                tas_C = tas - 273.15

                # update the 'tas' variable in the original NetCDF file with the new values
                dataset.variables['tas'][:] = tas_C

                # Update the metadata to reflect the unit change
                dataset.variables['tas'].units = 'Celsius'

            dataset.close()

            print(f"{filename} converted from Kelvin to Celsius.")

        # Optionally delete original files after conversion
        if delete_kelvin:
            for filename in os.listdir(src_dir):
                if filename.endswith('.nc'):
                    file_path = os.path.join(src_dir, filename)
                    os.remove(file_path)
                    print(f"Deleted original NetCDF file: {file_path}")

# Reproject NetCDF files to WGS84
def reproject_netcdf(src_dir=CONVERTED_DIR, dst_dir=REPROJECTED_DIR, dst_srs='EPSG:4326'):
    # Enable GDAL error messages for debugging
    gdal.UseExceptions()

    #Source CRS - Rotated Latitude Longitude Projection: North Pole lat: 39.25, lon: 0, Central Meridian: 18 (180-162)
    src_srs = '+proj=ob_tran +o_proj=longlat +o_lon_p=0 +o_lat_p=39.25 +lon_0=18 +to_meter=0.01745329' #USE GDAL wheel 3.4.3

    # Loop through NetCDF files in the source directory
    for filename in os.listdir(src_dir):
        if filename.endswith('.nc'):
            src_file = os.path.join(src_dir, filename)
            dst_file = os.path.join(dst_dir, filename.replace('.nc', '.tif'))

            try:
                # Perform the warp (reprojection) operation
                gdal.Warp(dst_file, src_file, format='GTiff', outputType=gdal.GDT_Float32, srcSRS=src_srs, dstSRS=dst_srs, xRes=0.11, yRes=0.11, resampleAlg='near') # 0.11 degree resolution as in original netcdf file
                print(f"Reprojected and saved: {dst_file}")

            except Exception as e:
                print(f"Error reprojecting {src_file}: {e}")

# Create a Cloud-Optimized GeoTIFF from reprojected GeoTIFF files
def cloud_optimized_geotiff(input_directory=REPROJECTED_DIR, output_directory=COG_DIR):
    # Collect all GeoTIFF files from the input directory
    input_files = [os.path.join(input_directory, f) for f in os.listdir(input_directory) if f.endswith('.tif')]

    # Temporary merged output file path
    merged_temp_path = os.path.join(output_directory, "merged_temp.tif")
    cog_output_path = os.path.join(output_directory, "cloud_geotiff.tif")

    # Step 1: Create a virtual dataset (VRT) from input files
    vrt_options = gdal.BuildVRTOptions(separate=True) #USE GDAL wheel 3.8.2
    vrt = gdal.BuildVRT("/vsimem/merged.vrt", input_files, options=vrt_options)

    # Step 2: Translate VRT to GeoTIFF with metadata preservation
    translate_options = gdal.TranslateOptions(format="GTiff", creationOptions=["TILED=YES", "COMPRESS=LZW"])
    gdal.Translate(merged_temp_path, vrt, options=translate_options)

    # Convert the base date to a datetime object
    base_date = "2020-12-01"
    time_interval = 3  #3 months
    start_date = datetime.strptime(base_date, "%Y-%m-%d")

    # Step 3: Add a date label as the band description for each time interval
    ds = gdal.Open(merged_temp_path, gdal.GA_Update)

    for i in range(ds.RasterCount):
        band = ds.GetRasterBand(i + 1)
        interval_start = start_date + relativedelta(months=i * time_interval)
        interval_end = interval_start + relativedelta(months=time_interval)
        band_description = f"{interval_start.strftime('%Y-%m-%d')} - {interval_end.strftime('%Y-%m-%d')}"
        band.SetDescription(band_description)

    ds = None  # Close the dataset to save changes

    # Step 4: Convert the merged GeoTIFF to Cloud-Optimized GeoTIFF (COG)
    cog_translate_options = gdal.TranslateOptions(
        format="COG",
        creationOptions=["COMPRESS=DEFLATE", "RESAMPLING=AVERAGE"]
    )
    gdal.Translate(cog_output_path, merged_temp_path, options=cog_translate_options)

    # Clean up the temporary merged file
    os.remove(merged_temp_path)

    print(f"Cloud-Optimized GeoTIFF created at: {cog_output_path}")

# Split reprojected tif files to individual seasonal tif files
def seasonal_tif_files(input_dir=REPROJECTED_DIR, output_dir=SEASONAL_DIR):
    # Get all .tif files in the input directory
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]

    if input_files:
        first_file = os.path.join(input_dir, input_files[0])
        dataset = gdal.Open(first_file)
        bands = list(range(1, dataset.RasterCount + 1))
        dataset = None #close dataset

    # Loop through input files
    for input_file in input_files:
        input_path = os.path.join(input_dir, input_file)

        # Get the initial date from the input file name
        start_year = int(input_file[4:8])
        current_date = datetime(start_year, 12, 1)

        # Loop through bands
        for band in bands:
            # Format the date as "YYYY_MM_DD"
            date_str = current_date.strftime('%Y_%m_%d')

            # Create the output file name based on the date and band
            output_file = os.path.join(output_dir, f'{date_str}.tif')

            # Translate the band to a new file
            gdal.Translate(output_file, input_path, bandList=[band])

            print(f"Translated band {band} to {output_file}")

            # Increment the date by 3 months using relativedelta
            current_date += relativedelta(months=3)