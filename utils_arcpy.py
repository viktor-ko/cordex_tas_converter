import arcpy
import os

#standard project home directory
PROJECT_HOME = os.path.abspath('./cordex')

#Create esri_crf folder
esri_crf = os.path.join(PROJECT_HOME, 'esri_crf')
os.makedirs(esri_crf, exist_ok=True)

# Create geodatabase, mosaic dataset within it, and add all .nc files from netcdf_Celsius folder.
def create_mosaic_from_netcdf(mosaic_name="tas_2020_2100"):

    # Step 1: Create the geodatabase
    gdb = os.path.join(esri_crf, 'cordex_temperature.gdb')
    if not arcpy.Exists(gdb):
        arcpy.management.CreateFileGDB(esri_crf, 'cordex_temperature.gdb')
        print(f"Geodatabase created at: {gdb}")
    else:
        print(f"Geodatabase already exists at: {gdb}")

    # Step 2: Set workspace to the created geodatabase
    arcpy.env.workspace = gdb

    # Step 3: Create the mosaic dataset in the geodatabase
    if not arcpy.Exists(os.path.join(gdb, mosaic_name)):
        arcpy.management.CreateMosaicDataset(gdb, mosaic_name, arcpy.SpatialReference(4326))
        mosaic_path = os.path.join(gdb, mosaic_name)
        print(f"Mosaic dataset '{mosaic_name}' created in geodatabase.")
    else:
        mosaic_path = os.path.join(gdb, mosaic_name)
        print(f"Mosaic dataset '{mosaic_name}' already exists in geodatabase.")

    # Step 4: Add .nc files from the folder to the mosaic dataset
    netcdf_folder = os.path.abspath('./cordex/netcdf_Celsius') #absolute path needed
    nc_files = [os.path.join(netcdf_folder, f) for f in os.listdir(netcdf_folder) if f.endswith('.nc')]

    for nc_file in nc_files:
        print(f"Adding {nc_file} to the mosaic dataset...")
        arcpy.management.AddRastersToMosaicDataset(mosaic_path, "NetCDF", nc_file)

    print("All .nc files have been added to the mosaic dataset.")

def create_crf():
    in_raster = os.path.abspath('./cordex/esri_crf/cordex_temperature.gdb/tas_2020_2100')
    out_crf = os.path.abspath('./cordex/esri_crf/tas_2020_2100.crf')
    arcpy.management.CopyRaster(
        in_raster=in_raster,
        out_rasterdataset=out_crf,
        config_keyword="",
        background_value=None,
        nodata_value="",
        onebit_to_eightbit="NONE",
        colormap_to_RGB="NONE",
        pixel_type="",
        scale_pixel_value="NONE",
        RGB_to_Colormap="NONE",
        format="CRF",
        transform="NONE",
        process_as_multidimensional="ALL_SLICES",
        build_multidimensional_transpose="TRANSPOSE"
    )

    print("CRF file created successfully at:", out_crf)