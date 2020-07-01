#!/usr/bin/env python

# Wind Mapper
# Copyright (C) 2020 Vincent Vionnet & Christopher Marsh
# Script to build wind maps for CHM based on the Wind Ninja diagnostic wind model
# Take an existing DEM or download it from SRTM-30m the Web
# Split the DEM into several subdomain suitable for WindNinja
# Execute the WN simulations
# Combine the outputs into a single vrt file covering the initial DEM extent


import elevation
import pdb, os, shutil
import subprocess
from osgeo import gdal, ogr, osr
from pyproj import Proj, transform
import numpy as np
import sys
import importlib
from functools import partial
import itertools
from scipy import ndimage
from os import environ
from concurrent import futures
from tqdm import tqdm

gdal.UseExceptions()  # Enable exception support


def main():
    #######  load user configurable paramters here    #######
    # Check user defined configuration file

    if len(sys.argv) == 1:
        print(
            'ERROR: wind_mapper.py requires one argument [configuration file] (i.e. wind_mapper.py '
            'param_existing_DEM.py)')
        exit(-1)

    # Get name of configuration file/module
    configfile = sys.argv[-1]

    # Load in configuration file as module
    X = importlib.machinery.SourceFileLoader('config', configfile)
    X = X.load_module()

    # Resolution of WindNinja simulations (in m)
    res_wind = X.res_wind

    # path to Wind Ninja executable

    # default path assumes we are running out of pip or we have a symlink @ ./bin/WindNinja_cli
    wn_exe = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)), 'bin', 'WindNinja_cli')

    if hasattr(X, 'wn_exe'):
        wn_exe = X.wn_exe

    if not os.path.exists(wn_exe):
        print('ERROR: Invalid path for WindNinja_cli. Consider specifying a `wn_exe` config option or confirm it is correct.')
        print(f'Path = {wn_exe}')
        exit(-1)

    environ["WINDNINJA_DATA"] = os.path.join(os.path.dirname(wn_exe), '..', 'share', 'windninja')

    # Parameter for atmospheric stability in Wind Ninja mass conserving (default value)
    alpha = 1

    # Number of wind speed categories (every 360/ncat degrees)
    ncat = 4
    if hasattr(X, 'ncat'):
        ncat = X.ncat

    if ncat < 1:
        print('ERROR ncat must be > 0 ')
        exit(-1)

    use_existing_dem = True

    lat_min = -9999
    lon_min = -9999
    lat_max = -9999
    lon_max = -9999
    if hasattr(X, 'use_existing_dem'):
        use_existing_dem = X.use_existing_dem
    if use_existing_dem:
        dem_filename = X.dem_filename
    else:
        lat_min = X.lat_min
        lat_max = X.lat_max
        lon_min = X.lon_min
        lon_max = X.lon_max

    if not use_existing_dem:
        if lat_min == -9999 or lon_min == -9999 or lat_max == -9999 or lon_max == -9999:
            print('Coordinates of the bounding box must be specified to download SRTM DEM.')
            exit(-1)

    # Method to compute average wind speed used to derive transfert function
    wind_average = 'mean_tile'
    targ_res = 1000
    if hasattr(X, 'wind_average'):
        wind_average = X.wind_average
        if wind_average == 'grid':
            targ_res = X.targ_res

    list_options_average = ['mean_tile', 'grid']
    if wind_average not in list_options_average:
        print('wind average must be "mean_tile" or "grid"')

        exit(-1)

    if targ_res < 0:
        print('Target resolution must be>0')
        exit(-1)

    # output to the specific directory, instead of the root dir of the calling python script
    user_output_dir = os.getcwd() + '/' + configfile[:-3] + '/'  # use the config filename as output path

    if hasattr(X, 'user_output_dir'):
        user_output_dir = X.user_output_dir
        if user_output_dir[-1] is not os.path.sep:
            user_output_dir += os.path.sep

    # Delete previous dir (if exists)
    if os.path.isdir(user_output_dir):
        shutil.rmtree(user_output_dir, ignore_errors=True)

    # make new output dir
    os.makedirs(user_output_dir)

    # Setup file containing WN configuration
    nworkers = os.cpu_count() or 1

    # on linux we can ensure that we respect cpu affinity
    if 'sched_getaffinity' in dir(os):
        nworkers = len(os.sched_getaffinity(0))

    # ensure correct formatting on the output
    fic_config = F"""num_threads = {nworkers}  
initialization_method = domainAverageInitialization 
units_mesh_resolution = m 
input_speed = 10.0 
input_speed_units = mps 
input_wind_height = 40.0 
units_input_wind_height = m 
output_wind_height = 40.0 
units_output_wind_height = m 
output_speed_units = mps 
vegetation = grass 
diurnal_winds = false 
write_goog_output = false 
write_shapefile_output = false 
write_ascii_output = true 
write_farsite_atm = false """

    if hasattr(X, 'fic_config_WN'):
        fic_config_WN = X.fic_config_WN

        if not os.path.exists(fic_config_WN):
            print('ERROR: Invalid path for cli_massSolver.cfg given in `fic_config_WN` config options.')
            exit(-1)
    else:
        fic_config_WN = os.path.join(user_output_dir, 'default_cli_massSolver.cfg')
        with open(fic_config_WN, 'w') as fic_file:
            fic_file.write(fic_config)

    # we need to make sure we pickup the right paths to all the gdal scripts
    gdal_prefix = ''
    try:
        gdal_prefix = subprocess.run(["gdal-config", "--prefix"], stdout=subprocess.PIPE).stdout.decode()
        gdal_prefix = gdal_prefix.replace('\n', '')
        gdal_prefix += '/bin/'
    except:
        raise BaseException(""" ERROR: Could not find gdal-config, please ensure it is installed and on $PATH """)

    # Wind direction increment
    delta_wind = 360. / ncat

    # List of variable to transform from asc into tif
    var_transform = ['ang', 'vel']
    if wind_average == 'grid':
        list_tif_2_vrt = ['U', 'V', 'spd_up_' + str(targ_res)]
    elif wind_average == 'mean_tile':
        list_tif_2_vrt = ['U', 'V', 'spd_up_tile']

    # Optimal size for wind ninja
    nres = 600

    # Additional grid point to ensure correct tile overlap
    nadd = 25

    # Define DEM file to use for WN
    fic_download = user_output_dir + 'ref-DEM.tif'

    name_utm = 'ref-DEM-utm'
    fic_utm = user_output_dir + '/' + name_utm + '.tif'

    if use_existing_dem:

        # if we are using a user-provided dem, ensure there are no NoData values that border the
        # DEM which will cause issues

        # mask data values
        exec_str = """%sgdal_calc.py -A %s --outfile %s --NoDataValue 0 --calc="1*(A>0)" """ % (gdal_prefix,
            dem_filename, user_output_dir + 'out.tif')
        subprocess.check_call([exec_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # convert to shp file
        exec_str = """%sgdal_polygonize.py -8 -b 1 -f "ESRI Shapefile" %s %s/pols """ % (gdal_prefix,
            user_output_dir + 'out.tif', user_output_dir)
        subprocess.check_call([exec_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # clip original with the shpfile
        exec_str = """%sgdalwarp -of GTiff -cutline %s/pols/out.shp -crop_to_cutline -dstalpha %s %s """ % (gdal_prefix,
            user_output_dir, dem_filename, fic_utm)
        subprocess.check_call([exec_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        shutil.rmtree("%s/pols" % user_output_dir)
        os.remove("%s/out.tif" % user_output_dir)

    else:

        # Properties of the bounding box
        delta_lat = lat_max - lat_min
        delta_lon = lon_max - lon_min

        fac = 0.1  # Expansion factor to make sure that the downloaded SRTM tile is large enough

        lon_mid = (lon_min + lon_max) / 2.
        lat_mid = (lat_min + lat_max) / 2.

        # Download reference SRTM data
        elevation.clip(bounds=(
            lon_min - delta_lon * fac, lat_min - delta_lat * fac, lon_max + delta_lon * fac, lat_max + delta_lat * fac),
            output=fic_download)

        # Get corresponding UTM zone (center of the zone to extract)
        nepsg_utm = int(32700 - round((45 + lat_mid) / 90, 0) * 100 + round((183 + lon_mid) / 6, 0))
        srs_out = osr.SpatialReference()
        srs_out.ImportFromEPSG(nepsg_utm)

        # Get bounding box to extract in utm using pyproj
        WGS84 = Proj(init='EPSG:4326')
        inp = Proj(init='EPSG:' + str(nepsg_utm))
        xmin, ymin = transform(WGS84, inp, lon_min, lat_min)
        xmax, ymax = transform(WGS84, inp, lon_max, lat_max)

        # Extract a rectangular region of interest in utm at 30 m
        exec_str = '%sgdalwarp %s %s -overwrite -dstnodata -9999 -t_srs "%s" -te %.30f %.30f %.30f %.30f  -tr %.30f ' \
                   '%.30f -r bilinear '
        com_string = exec_str % (gdal_prefix, fic_download, fic_utm, srs_out.ExportToProj4(), xmin, ymin, xmax, ymax, 30, 30)
        subprocess.check_call([com_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    # Get informations on projected file
    ds = gdal.Open(fic_utm)
    band = ds.GetRasterBand(1)
    gt = ds.GetGeoTransform()
    xmin = gt[0]
    ymax = gt[3]

    pixel_width = gt[1]
    pixel_height = -gt[5]

    xmax = xmin + pixel_width * ds.RasterXSize
    ymin = ymax - pixel_height * ds.RasterYSize

    lenx = band.XSize * pixel_width
    leny = band.YSize * pixel_height
    len_wn = res_wind * nres

    # Number of Wind Ninja tiles
    nopt_x = int(lenx // len_wn + 1)
    nopt_y = int(leny // len_wn + 1)

    nx = band.XSize / nopt_x
    ny = band.YSize / nopt_y

    if nopt_x == 1 and nopt_y == 1:
        # DEM is small enough for WN
        name_tmp = 'tmp_0_0'
        fic_tmp = user_output_dir + name_tmp + ".tif"
        shutil.copy(fic_utm, fic_tmp)
    else:
        # Split the DEM into smaller DEM for Wind Ninja
        for i in range(0, nopt_x):
            for j in range(0, nopt_y):

                xbeg = xmin + i * nx * pixel_width - nadd * pixel_width
                ybeg = ymin + j * ny * pixel_height - nadd * pixel_height

                delx = nx * pixel_width + 2 * nadd * pixel_width
                dely = ny * pixel_height + 2 * nadd * pixel_height

                if i == 0.:
                    xbeg = xmin
                if i == 0. or i == (nopt_x - 1):
                    delx = nx * pixel_width + nadd * pixel_width

                if j == 0.:
                    ybeg = ymin
                if j == 0. or j == (nopt_y - 1):
                    dely = ny * pixel_height + nadd * pixel_height

                name_tmp = 'tmp_' + str(i) + "_" + str(j)
                fic_tmp = user_output_dir + name_tmp + ".tif"
                clip_tif(fic_utm, fic_tmp, xbeg, xbeg + delx, ybeg, ybeg + dely, gdal_prefix)

    # Build WindNinja winds maps
    x_y_wdir = itertools.product(range(0, nopt_x),
                                 range(0, nopt_y),
                                 np.arange(0, 360., delta_wind))
    x_y_wdir = [p for p in x_y_wdir]

    for d in x_y_wdir:
        i,j,k = d
        dir_tmp = user_output_dir + 'tmp_dir' + "_" + str(i) + "_" + str(j)
        if not os.path.isdir(dir_tmp):
            os.makedirs(dir_tmp)

    print(f'Running WindNinja on {len(x_y_wdir)} combinations of direction and sub-area. Please be patient...')
    with futures.ProcessPoolExecutor(max_workers=nworkers) as executor:
        res = list(tqdm(executor.map(partial(call_WN_1dir, gdal_prefix, user_output_dir, fic_config_WN,
                                             list_tif_2_vrt, nopt_x, nopt_y, nx, ny,
                                             pixel_height, pixel_width, res_wind, targ_res, var_transform, wind_average,
                                             wn_exe,
                                             xmin, ymin), x_y_wdir), total=len(x_y_wdir)))

    print('Building VRTs...')
    # Loop on wind direction to build reference vrt file to be used by mesher
    nwind = np.arange(0, 360., delta_wind)
    with tqdm(total=len(nwind)) as pbar:
        for wdir in nwind:
            for var in list_tif_2_vrt:
                name_vrt = user_output_dir + name_utm + '_' + str(int(wdir)) + '_' + var + '.vrt'
                cmd = "find " + user_output_dir[0:-1] + " -type f -name '*_" + str(int(wdir)) + "_10_" + str(
                    res_wind) + "m_" + var + "*.tif' -exec " + gdal_prefix+ "gdalbuildvrt " + name_vrt + " {} +"
                subprocess.check_call([cmd], stdout=subprocess.PIPE,
                                      shell=True)
            pbar.update(1)


def call_WN_1dir(gdal_prefix, user_output_dir, fic_config_WN, list_tif_2_vrt, nopt_x, nopt_y, nx, ny,
                 pixel_height, pixel_width, res_wind, targ_res, var_transform, wind_average, wn_exe, xmin, ymin,
                 ijwdir):
    i, j, wdir = ijwdir

    # Out directory
    dir_tmp = user_output_dir + 'tmp_dir' + "_" + str(i) + "_" + str(j)
    name_tmp = 'tmp_' + str(i) + "_" + str(j)
    fic_dem_in = user_output_dir + name_tmp + ".tif"

    name_base = dir_tmp + '/' + name_tmp + '_' + str(int(wdir)) + '_10_' + str(res_wind) + 'm_'
    subprocess.check_call([wn_exe + ' ' +
                           fic_config_WN + ' --elevation_file ' + fic_dem_in + ' --mesh_resolution ' + str(
        res_wind) + ' --input_direction ' + str(int(wdir)) + ' --output_path ' + dir_tmp],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          shell=True)
    for var in var_transform:
        name_gen = name_base + var
        subprocess.check_call([gdal_prefix + 'gdal_translate ' + name_gen + '.asc ' + name_gen + '.tif'],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              shell=True)

        os.remove(name_gen + '.asc')
        os.remove(name_gen + '.prj')
    # Read geotif for angle and velocity to compute speed up
    gtif = gdal.Open(name_base + 'ang.tif')
    ang = gtif.GetRasterBand(1).ReadAsArray()
    vel_tif = gdal.Open(name_base + 'vel.tif')
    vel = vel_tif.GetRasterBand(1).ReadAsArray()
    # Compute and save wind components
    uu = -vel * np.sin(ang * np.pi / 180.)
    fic_tif = name_base + 'U_large.tif'
    save_tif(uu, vel_tif, fic_tif)
    vv = -vel * np.cos(ang * np.pi / 180.)
    fic_tif = name_base + 'V_large.tif'
    save_tif(vv, vel_tif, fic_tif)
    # Compute smooth wind speed
    if wind_average == 'grid':
        nsize = targ_res / res_wind
        vv_large = ndimage.uniform_filter(vel, size=nsize, mode='nearest')
        fic_tif = name_base + 'spd_up_' + str(targ_res) + '_large.tif'
    elif wind_average == 'mean_tile':
        vv_large = np.mean(vel)
        fic_tif = name_base + 'spd_up_tile_large.tif'
    # Compute local speed up and save
    loc_speed_up = vel / vv_large
    save_tif(loc_speed_up, vel_tif, fic_tif)
    # Reduce the extent of the final tif
    xbeg = xmin + i * nx * pixel_width
    ybeg = ymin + j * ny * pixel_height
    delx = nx * pixel_width
    dely = ny * pixel_height
    for var in list_tif_2_vrt:
        fic_tif = name_base + var + '_large.tif'
        fic_tif_fin = name_base + var + '.tif'
        if nopt_x == 1 and nopt_y == 1:
            shutil.copy(fic_tif, fic_tif_fin)
        else:
            clip_tif(fic_tif, fic_tif_fin, xbeg, xbeg + delx, ybeg, ybeg + dely, gdal_prefix)
        os.remove(fic_tif)


def clip_tif(fic_in, fic_out, xmin, xmax, ymin, ymax, gdal_prefix):
    com_string = gdal_prefix + "gdal_translate -of GTIFF -projwin " + str(xmin) + ", " + str(ymax) + ", " + str(xmax) + ", " + str(
        ymin) + " " + fic_in + " " + fic_out
    subprocess.check_call([com_string], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def save_tif(var, inDs, fic):
    # Create the geotif
    driver = inDs.GetDriver()
    rows = inDs.RasterYSize
    cols = inDs.RasterXSize
    outDs = driver.Create(fic, cols, rows, 1, gdal.GDT_Float32)
    # Create new band
    outBand = outDs.GetRasterBand(1)
    outBand.WriteArray(var, 0, 0)

    # Flush data to disk
    outBand.FlushCache()

    # Georeference the image and set the projection
    outDs.SetGeoTransform(inDs.GetGeoTransform())
    outDs.SetProjection(inDs.GetProjection())

    outDs = None


if __name__ == "__main__":
    main()
