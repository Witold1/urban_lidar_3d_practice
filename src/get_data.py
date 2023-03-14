import logging
#   https://docs.python.org/3/howto/logging.html
#   https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook
import datetime
import glob
import gc
import os

try:
    import whitebox
except ModuleNotFoundError:
    !pip install whitebox
    import whitebox

def _create_folders_structure():
    """Creates project structure (adds folders for data stages)

        Logic:
        - 1. CREATE FOLDER FOR [RAW] LAZ
        - 2. CREATE FOLDER FOR [RAW] LAS
        - 3. CREATE FOLDER FOR [INTERIM] TIFF
        - 4. CREATE FOLDER FOR [PROCESSED] MOSAIC OUTPUT AND FILTERED MOSAIC OUTPUT

    Parameters
    ----------
    None
    """
    import pathlib

    pathlib.Path('laz_files').mkdir(parents=True, exist_ok=True)
    pathlib.Path('las_files').mkdir(parents=True, exist_ok=True)
    pathlib.Path('tif_files').mkdir(parents=True, exist_ok=True)
    pathlib.Path('mosaic_files').mkdir(parents=True, exist_ok=True)

def download_lidar_files(links=None, unzip=True, run=True):
    """Downloads (collects) selected files in LiDAR point cloud format to local storage.

        Takes data structure with links
        Returns downloaded raw data files

        * Sometimes data is provided in compressed archive formats (f.e. ZIP format), so decompress them.

        Logic:
        - 1. DOWNLOAD
        -    1.2 IF .ZIP THEN UNZIP (DECOMPRESS ARCHIVE)

    Parameters
    ----------
    links : str
        list of links to download files from
    unzip : bool
        if unzip (unarchive) link output
    run : bool
        if run function code
    """
    if not run:
        return print('\tDownload LiDAR files manually (& unzip, if needed)')
    for indx, link in enumerate(links):
        !wget "$link"
        file_name = links.split('/')[-1] # f.e. ID2007_118754_e.zip
        if unzip:
            !unzip "$file_name" -d las_files

def decompress_laz_files(input_folder=None, run=False):
    """Decompresses (unlaz) selected files in LiDAR compressed point cloud format.

        Takes raw data files in LAZ format
        Returns (creates) unarchived files in LAS format

        * Sometimes data is provided in compressed LiDAR point clouds format (usually, .LAZ).
            Some packages/wrappers/APIs doesn't support .LAZ file format out of a box, so let's standardize file formats

        Logic:
        - 1. IF .LAZ THEN DECOMPRESS .LAZ ('UNZIP' LAZ, UNLAZ .LAZ -> .LAS)

    Parameters
    ----------
    input_folder : str
        description
        example format : "/kaggle/working/laz_files/"
    run : bool
        if run function code
    """
    if not run:
        return print('\tDecompress Compressed LiDAR files manually')

    # laspy is used in order to convert .laz to .las (unzip laz)
    try:
        import laspy
    except ModuleNotFoundError:
        !pip install laspy[lazrs,laszip]
        import laspy

    for indx, file in enumerate(glob.glob(f'{input_folder}*.laz')):

        print(f"\t{datetime.datetime.now()} {indx} \t{file} - reading .LAZ ")
        las = laspy.read(file)
        #print('\t', las.header, )

        print(f'\t\t{datetime.datetime.now()} Converting .LAZ to .LAS')
        las = laspy.convert(las)

        print(f'\t\t{datetime.datetime.now()} Saving .LAS')
        las.write(file.replace('laz', 'las'))

        print(f"\t\tdelete: {file}")
        !rm "$file"
        #if indx == 5: break

    !rm /kaggle/working/laz_files/*.laz
    del las
    gc.collect()

def filter_lidar_files(input_folder=None,
                       filter_classes=True, exclude_cls=None,
                       filter_outliers=True, filter_outliers_params=None,
                       run=True):
    """Filters LiDAR point cloud.

        Takes raw data files in LAS format (point clouds)

    Parameters
    ----------
    input_folder : str
        description
        example format : "/kaggle/working/laz_files/"
    filter_outliers : bool
        if filter (remove) outliers from a point cloud, uses `wbt.lidar_remove_outliers`
    run : bool
        if run function code
    """
    if not run:
        return print('\tFilter LiDAR files manually')

    wbt = whitebox.WhiteboxTools()
    print(wbt.version())

    wbt.verbose = False # True to see progress
    print(f"\t{datetime.datetime.now()} run filtering. {len(glob.glob('/kaggle/working/las_files/*'))} files")
    if filter_outliers:
        for indx, file in enumerate(glob.glob(f'{input_folder}*.las')):
            print(f"\t{datetime.datetime.now()} {indx} \t{file} - remove outliers")
            active_file = file
            active_file = active_file.replace('.las', '_rmv_out.las')
            wbt.lidar_remove_outliers(i=file, output=active_file, **filter_outliers_params)
            print(f"\t\tcreate: {active_file}")
            print(f"\t\tdelete: {file}")
            !rm "$file"
    gc.collect()

    if filter_classes:
        for indx, file in enumerate(glob.glob(f'{input_folder}*.las')):
            print(f"\t{datetime.datetime.now()} {indx} \t{file} - filter classes")

            active_file = file
            active_file = active_file.replace('.las', '_rmv_cls.las')
            wbt.filter_lidar_classes(i=file, output=active_file, exclude_cls=exclude_cls)
            print(f"\t\tcreate: {active_file}")
            print(f"\t\tdelete: {file}")
            !rm "$file"
        gc.collect()

def rasterize_lidar_files(input_folder=None, raster_method='surface',
                          gridding_params=None, run=True):
    """Creates a mesh (rasterizes) LiDAR point cloud.

        Takes LPC data files in LAS format (point clouds)
        Creates mesh (rasters) in tif/tiff format (Tagged Image File Format)

        We use `whitebox geo` API to handle it.
            Methods selected are
                `Delaunay triangulation` (Delaunay triangular irregular network (TIN))
                `lidar_digital_surface_model` (Delaunay triangular with additional params)

        For additional information, check
            # https://www.whiteboxgeo.com/manual/wbt_book/available_tools/lidar_tools.html#lidartingridding
            # https://docs.qgis.org/3.4/en/docs/user_manual/working_with_mesh/mesh_properties.html

        Logic:
        - 1. TRANSFORM [POINT CLOUD] .LAS -> [MESH/RASTER/GRID] .TIFF

    Parameters
    ----------
    input_folder : str
        description
        example format : "/kaggle/working/laz_files/"
    raster_method : str
        `delaunay` - uses `wbt.lidar_tin_gridding`
        `surface` uses `wbt.lidar_digital_surface_model`
    run : bool
        if run function code
    """
    if not run:
        return print('\tRasterize LiDAR files manually')

    wbt = whitebox.WhiteboxTools()
    wbt.set_working_dir(input_folder)

    # batch processing (whole folder) vs kinda stream (rasterizes every file)
    ## `batch` should note files around each other
    ## https://www.whiteboxgeo.com/manual/wbt_book/tutorials/lidar.html#i-have-many-laszlidar-files-and-want-to-interpolate-all-of-them-at-once
    ##
    ## `kinda stream` I suppose assumes each file is kinda thing-in-itself
    if raster_method == "delaunay":
        wbt.lidar_tin_gridding(**gridding_params) #2,3,4,5
    else:
        wbt.lidar_digital_surface_model(resolution=1., radius=0.8)
    !mv "$input_folder"*.tif /kaggle/working/tif_files/
    ""

def mosaic_rastersized_lidar_files(input_folder=None, output_mosaic_path=None,
                                   mosaic_backend='whitebox', mosaic_method="bilinear", run=True):
    """Merges (mosaics, appends) many selected raster files into one big raster mosaic

        Takes raster files from `input_folder`
        Creates a mosaic to `output_mosaic_path`

        Logic:
        - 1. MERGE [MANY] TIFF -> MERGED [MOSAIC] TIFF
        -    1.1 REMOVE OUTLIERS [HERE OR WHEN MOSAIC]

    Parameters
    ----------
    input_folder : str
        description
    output_mosaic_path : str
        description
    mosaic_backend : str
        - `whitebox.wbt.mosaic` for whitebox
        - `rasterio.merge.merge` for rasterio
        - manually for manual/custom/other package merge
    run : bool
        if run function code
    """
    if not run:
        return print('\tMosaic rastersized LiDAR files manually')

    wbt = whitebox.WhiteboxTools()
    print(wbt.version())

    ### WHITEBOX MOSAIC merge
    if mosaic_backend == 'whitebox':
        ### DOCUMENTATION APPROACH, WITH TEST
        ### https://www.whiteboxgeo.com/manual/wbt_book/tutorials/mosaic.html
        wbt.verbose = False
        wbt.set_working_dir(input_folder) # ('/kaggle/working/tif_files/')
        if wbt.mosaic(output=output_mosaic_path, # '/kaggle/working/mosaic_whitebox.tif'
                      method=mosaic_method) != 0:
            # Non-zero returns indicate an error.
            print('\t ERROR running mosaic')
        wbt.verbose = False

        print("\t\tComplete!")

    ### RASTERIO MOSAIC merge
    elif mosaic_backend == 'rasterio':
        try:
            import rasterio as rio
            from rasterio.merge import merge as rasterio_merge
        except:
            !pip install rasterio
            import rasterio as rio
            from rasterio.merge import merge as rasterio_merge
        # merge/append rasters (mosaic)
        rasters_to_mosiac = []
        for indx, file in enumerate(glob.glob(f'{input_folder}*.tif')):
            print(indx, '\t', file)
            raster = rio.open(file)
            rasters_to_mosiac.append(raster)
            print("The CRS of this data is:", rasters_to_mosiac[0].crs, rasters_to_mosiac[0].nodatavals)
        ## check https://gis.stackexchange.com/questions/443652/rasterio-merge-creates-white-stripes-when-rasters-overlap-and-one-of-them-has-nu
        mosaic, output = rasterio_merge(rasters_to_mosiac)

        # save mosaic, double check metadata or rewrite it if needed
        output_meta = raster.meta.copy()
        output_meta.update({"driver": "GTiff",
                            "height": mosaic.shape[1],
                            "width": mosaic.shape[2],
                            "transform": output, })
        output_path = output_mosaic_path # '/kaggle/working/mosaic_rasterio.tif'
        with rio.open(output_path, "w", **output_meta) as m:
            m.write(mosaic)

    ### MANUAL MOSAIC merge
    elif mosaic_backend == 'manual':
        print('MOSAIC TILES MANUALLY VIA PYVISTA')
        # example ... 1. read meshes, 2. append meshes to each other using their centers and sizes
        # mesh2 = mesh2.translate((mesh1.center[0] * 2, 0, 0), inplace=False)
        # mesh3 = mesh3.translate((0, mesh1.center[1] * -2, 0), inplace=False)
        # mesh4 = mesh4.translate((mesh1.center[0] * 2, mesh1.center[1] * -2, 0), inplace=False)
        # mesh = mesh1 + mesh2 + mesh3 + mesh4
        # del(mesh1, mesh2, mesh3, mesh4)
        # flip `x` and `y` axis if needed

def filter_mosaiced_raster_file(input_file=None, output_mosaic_path=None,
                                method='median', filter_params=None, run=True):
    """Filters rasters
        Selected method is `wbt.median_filter`. Feel free to experiment.

        Takes mosaic from `input_folder`
        Creates filtered mosaic to `output_mosaic_path`

        For additional information, check
            # https://www.whiteboxgeo.com/manual/wbt_book/available_tools/image_processing_tools_filters.html
            # https://www.whiteboxgeo.com/manual/wbt_book/available_tools/image_processing_tools_filters.html?highlight=Median#medianfilter

    Parameters
    ----------
    input_file : str
        description
    output_mosaic_path : str
        description
    method : str
        description
    run : bool
        if run function code
    """
    if not run:
        return print('\tFilter moasaic file(s) manually (if needed)')

    wbt = whitebox.WhiteboxTools()
    wbt.verbose = False
    print(wbt.version())

    ### identify the sample data directory of the package
    # data_dir = os.path.dirname(pkg_resources.resource_filename("whitebox", 'testdata/'))
    #
    # wbt.set_working_dir(data_dir) # wbt.set_working_dir("/kaggle/working/laz_files/")
    # wbt.verbose = False
    # # wbt.feature_preserving_smoothing("DEM.tif", "smoothed.tif", filter=9)
    # # wbt.breach_depressions("smoothed.tif", "breached.tif")
    # # wbt.d_inf_flow_accumulation("breached.tif", "flow_accum.tif")

    if method == 'median':
        wbt.median_filter(i=input_file, output=output_mosaic_path, **filter_params) # 9,9,2 or 7,7,3 ?
    elif method == 'conservative_smoothing':
        wbt.conservative_smoothing_filter(i=input_file, output=output_mosaic_path, **filter_params)
    elif method == 'bilateral':
        wbt.bilateral_filter(i=input_file, output=output_mosaic_path, **filter_params)
    else:
        return print('Method not avaliable.')

def _read_processed_rasterized_file(file_path=None, CUSTOM_READ=False):
    """Reads the raster file into a data structure needed for futher plots

        Takes path to raster mosaic
        Returns an object in `pyvista` format

        * In theory, it should preserve coordinates, but it doesn't work as intended somewhy
            Maybe the reason is test's CRS - Florida's own CRS (Florida East State Plane)
            which we need to reproject
        https://github.com/pyvista/pyvista-support/issues/394
        https://towardsdatascience.com/how-to-automate-lidar-point-cloud-processing-with-python-a027454a536c


    Parameters
    ----------
    file_path : str
        description
    CUSTOM_READ : bool
        description
    """
    ### CUSTOM APPROACH APPROACH TO READ A RASTER
    if CUSTOM_READ:
        # big function from git
        # https://banesullivan.com/pyvista/examples/geological-map.html
        # https://github.com/pyvista/pyvista-support/issues/205

        import pyvista as pv
        import xarray as xr
        import numpy as np

        """
        Helpful: http://xarray.pydata.org/en/stable/auto_gallery/plot_rasterio.html
        """
        # Read in the data
        data = xr.open_rasterio(file_path)
        values = np.asarray(data)
        nans = values == data.nodatavals
        if np.any(nans):
            # values = np.ma.masked_where(nans, values)
            values[nans] = np.nan
        # Make a mesh
        xx, yy = np.meshgrid(data['x'], data['y'])
        zz = values.reshape(xx.shape) # will make z-comp the values in the file
        # zz = np.zeros_like(xx) # or this will make it flat
        mesh = pv.StructuredGrid(xx, yy, zz)
        mesh['data'] = values.ravel(order='F')
        return mesh

    ### DEFAULT PYVISTA APPROACH TO READ A RASTER
    else:
        mesh = pv.read(file_path)
        # Example - READ and CLIP
        # mesh = pv.read("/kaggle/working/mosaic_output_whitebox_bilinear.tif")
        # try:
        #     plt.hist(mesh["Tiff Scalars"], bins=20, figsize=(14, 8))
        # except:
        #     np.median(mesh["Tiff Scalars"]);
        # clipped_mesh = mesh.clip_scalar(scalars="Tiff Scalars", value=1., invert=False, progress_bar=True) # Miami - 1.3, Dallas - 1. or 100
        # clipped_mesh
        # #del mesh
        return mesh

def _main_get_data():
    """Run through cities list
        create, filter, and mosaic rasters from point clouds
    """
    print('Create folders')
    _create_folders_structure()

    for key in DATA_LINKS.keys():
        print(f'CITY : {key}')

        print('Download')
        download_lidar_files(links=DATA_LINKS[key], run=False)
        gc.collect()

        print('Decompress LAZ')
        decompress_laz_files(input_folder="/kaggle/working/laz_files/", run=False)
        gc.collect()

        print('Show LiDAR file information summary')
        wbt = whitebox.WhiteboxTools()
        # for lidar_file_fp in glob.glob("/kaggle/working/las_files/*"):
        #     print(lidar_file_fp)
        wbt.lidar_info(i=glob.glob("/kaggle/working/las_files/*")[1],
                       output="/kaggle/working/info.html",
                       density=True, vlr=True, geokeys=True)

        del wbt

        print('Filter outliers in point clouds)')
        filter_outliers_params = {"radius" : 4, "elev_diff" : 15, "use_median" : True, "classify" : False}
        filter_lidar_files(input_folder="/kaggle/working/las_files/",
                   filter_classes=False, exclude_cls="0,7,18", # 3,4,5 Low/Medium/High Vegetation # try 1 - ""3,5,7,14", try 2 - add 1, 18
                   filter_outliers=True, filter_outliers_params=filter_outliers_params,
                   run=True)
        gc.collect()

        print('Rasterize point clouds)')
        gridding_params = {"resolution" : 1, "exclude_cls" : "18,19"} # exclude_cls='3,4,5,7,8,9,13,14,15,16,18,19'
        gridding_params = {"resolution" : 1, "radius" : 0.8} #, minz=0, maxz=80
        rasterize_lidar_files(input_folder="/kaggle/working/las_files/", raster_method="surface",
                              gridding_params=gridding_params, run=True) # method="surface" or "delaunay"
        gc.collect()

        print('Mosaic')
        mosaic_backend = 'whitebox'
        output_mosaic_path = f'/kaggle/working/{key}_mosaic_{mosaic_backend}_bilinear.tif'
        # Uses the nearest-neighbour resampling method (i.e. nn). Cubic convolution (i.e. cc) and bilinear interpolation (i.e. bilinear) are other options.
        mosaic_rastersized_lidar_files(input_folder="/kaggle/working/tif_files/",
                               output_mosaic_path=output_mosaic_path,
                               mosaic_backend=mosaic_backend,
                               mosaic_method="nn",
                               run=True)
        gc.collect()

        print('Filter raster')
        output_filtered_mosaic_path = f'/kaggle/working/{key}_{mosaic_backend}_bilinear_filtered.tif'
        filter_params = {"filterx" : 9, "filtery" : 9, "sig_digits" : 2}
        filter_mosaiced_raster_file(input_file="/kaggle/working/riga_center.tif",
                            output_mosaic_path=output_filtered_mosaic_path,
                            method="median", filter_params=filter_params, run=True)
        gc.collect()
