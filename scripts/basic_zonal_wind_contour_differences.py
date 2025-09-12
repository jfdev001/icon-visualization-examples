from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import mkdir
from os.path import join, exists, dirname
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import netCDF4 as nc
from numpy import ndarray, mean
import xarray as xarr

from src.conversion import (
    convert_pressure_in_hPa_to_height_in_km, convert_meters_to_kilometers)

DESCRIPTION: str = """
Plot contour differences for zonal winds to illustrate how increasing grid
resolution (i.e., R2B4 to R2B7) more accurately reflects ground truth
winds (i.e., URAP data).
"""

TIME: str = "time"
LATITUDE: str = "lat"
LONGITUDE: str = "lon"
HEIGHT: str = "height"
HEIGHT_UNITS: str = "km"
ZONAL_WIND_UNITS: str = "m s-1"
UNITS: str = "units"

N_RNBK_FULL_LEVEL_CENTER_HEIGHT_AXES: int = 3
RNBK_ZONAL_WIND: str = "u"
RNBK_FULL_LEVEL_CENTER_HEIGHT: str = "z_mc"
RNBK_FULL_LEVEL_CENTER_HEIGHT_UNITS: str = "m"
RNBK_FULL_LEVEL_CENTER_HEIGHT_LATITUDE_AXIS: int = 1
RNBK_FULL_LEVEL_CENTER_HEIGHT_LONGITUDE_AXIS: int = 2

URAP_ZONAL_WIND: str = "ua"
N_URAP_LEVEL_AXES: int = 1
URAP_LEVEL: str = "lev"
URAP_LEVEL_UNITS: str = "hPa"

N_ZONAL_WIND_AXES: int = 4
TIME_AXIS: int = 0
ZONAL_WIND_HEIGHT_OR_LEVEL_AXIS: int = 1
ZONAL_WIND_LATITUDE_AXIS: int = 2
ZONAL_WIND_LONGITUDE_AXIS: int = 3

N_MONTHS: int = 12
JANUARY_IX: int = 0
JULY_IX: int = 6


def main():
    # parse cli
    args = cli()

    # define paths
    dir_of_current_script = Path(dirname(__file__))
    project_dir = dir_of_current_script.parent
    plots_dir = join(project_dir, "plots")
    if not exists(plots_dir):
        mkdir(plots_dir)

    parent_data_dir_on_levante = "/work/bm1233/b383137/URAP-SABER-UAL120_150_F03C14L00S30-R2B7_free_30_years/data/"
    assert exists(parent_data_dir_on_levante)

    urap_dir = join(parent_data_dir_on_levante, "URAP")
    assert exists(urap_dir)
    r2b4_dir = join(parent_data_dir_on_levante, "UAL120_150_F03C14L00S30")
    assert exists(r2b4_dir)
    r2b7_dir = join(parent_data_dir_on_levante, "R2B7_free_30_years")
    assert exists(r2b7_dir)

    r2b4_levels_file = join(r2b4_dir, "hfile.nc")
    assert exists(r2b4_levels_file)
    r2b7_levels_file = join(r2b7_dir, "hfile.nc")
    assert exists(r2b7_levels_file)

    urap_zonal_wind_file = join(urap_dir, "urap_ymonmean.nc")
    assert exists(urap_zonal_wind_file)
    r2b4_zonal_wind_file = join(
        r2b4_dir,
        "daily_mean",
        "UAL120_150_F03C14L00S30_u-atm_3d_dm_ml_ymonmean_2019-2029_RM.nc")
    assert exists(r2b4_zonal_wind_file)
    r2b7_zonal_wind_file = join(
        r2b7_dir, "R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc")
    assert exists(r2b7_zonal_wind_file)

    print("LOAD DATA...")
    urap_dataset = nc.Dataset(urap_zonal_wind_file)
    urap_variables = urap_dataset.variables
    urap_level_variable = urap_variables[URAP_LEVEL]
    assert urap_level_variable.units == URAP_LEVEL_UNITS

    urap_zonal_wind: ndarray = urap_variables[URAP_ZONAL_WIND][:]
    urap_level: ndarray = urap_level_variable[:]
    urap_lat: ndarray = urap_variables[LATITUDE][:]
    urap_lon: ndarray = urap_variables[LONGITUDE][:]

    r2b4_levels_dataset = nc.Dataset(r2b4_levels_file)
    r2b4_levels_variables = r2b4_levels_dataset.variables
    r2b4_height_variable = r2b4_levels_variables[RNBK_FULL_LEVEL_CENTER_HEIGHT]
    assert r2b4_height_variable.units == RNBK_FULL_LEVEL_CENTER_HEIGHT_UNITS
    r2b4_height_in_meters: ndarray = r2b4_height_variable[:]

    r2b4_zonal_wind_dataset = nc.Dataset(r2b4_zonal_wind_file)
    r2b4_zonal_wind_variables = r2b4_zonal_wind_dataset.variables
    r2b4_zonal_wind: ndarray = r2b4_zonal_wind_variables[RNBK_ZONAL_WIND][:]

    r2b4_lat: ndarray = r2b4_zonal_wind_variables[LATITUDE][:]
    r2b4_lon: ndarray = r2b4_zonal_wind_variables[LONGITUDE][:]

    r2b7_levels_dataset = nc.Dataset(r2b7_levels_file)
    r2b7_levels_variables = r2b7_levels_dataset.variables
    r2b7_height_variable = r2b7_levels_variables[RNBK_FULL_LEVEL_CENTER_HEIGHT]
    assert r2b7_height_variable.units == RNBK_FULL_LEVEL_CENTER_HEIGHT_UNITS
    r2b7_height_in_meters: ndarray = r2b7_height_variable[:]

    r2b7_zonal_wind_dataset = nc.Dataset(r2b7_zonal_wind_file)
    r2b7_zonal_wind_variables = r2b7_zonal_wind_dataset.variables
    r2b7_zonal_wind: ndarray = r2b7_zonal_wind_variables[RNBK_ZONAL_WIND][:]

    r2b7_lat: ndarray = r2b7_zonal_wind_variables[LATITUDE][:]
    r2b7_lon: ndarray = r2b7_zonal_wind_variables[LONGITUDE][:]

    assert len(urap_level.shape) == N_URAP_LEVEL_AXES
    assert len(urap_zonal_wind.shape) == N_ZONAL_WIND_AXES
    assert urap_zonal_wind.shape[TIME_AXIS] == N_MONTHS

    assert len(r2b4_height_in_meters.shape) == N_RNBK_FULL_LEVEL_CENTER_HEIGHT_AXES
    assert len(r2b4_zonal_wind.shape) == N_ZONAL_WIND_AXES
    assert r2b4_zonal_wind.shape[TIME_AXIS] == N_MONTHS

    assert len(r2b7_height_in_meters.shape) == N_RNBK_FULL_LEVEL_CENTER_HEIGHT_AXES
    assert len(r2b7_zonal_wind.shape) == N_ZONAL_WIND_AXES
    assert r2b7_zonal_wind.shape[TIME_AXIS] == N_MONTHS

    print("TRANSFORM DATA...")
    urap_zonal_wind_jan = transform_zonal_wind(urap_zonal_wind, JANUARY_IX)
    urap_zonal_wind_jul = transform_zonal_wind(urap_zonal_wind, JULY_IX)
    urap_height_in_km = convert_pressure_in_hPa_to_height_in_km(urap_level)

    r2b4_zonal_wind_jan = transform_zonal_wind(r2b4_zonal_wind, JANUARY_IX)
    r2b4_zonal_wind_jul = transform_zonal_wind(r2b4_zonal_wind, JULY_IX)
    r2b4_height_in_km = transform_rnbk_height(r2b4_height_in_meters)

    r2b7_zonal_wind_jan = transform_zonal_wind(r2b7_zonal_wind, JANUARY_IX)
    r2b7_zonal_wind_jul = transform_zonal_wind(r2b7_zonal_wind, JULY_IX)
    r2b7_height_in_km = transform_rnbk_height(r2b7_height_in_meters)

    print("ALIGN DATA...")
    # TODO: since you need to compute differences where latitudes and heights
    # overlap, you need to do something like xarray align
    # https://tutorial.xarray.dev/fundamentals/02.3_aligning_data_objects.html#alignment-putting-data-on-the-same-grid
    urap = make_xarray_dataset(
        urap_zonal_wind, urap_height_in_km, urap_lat, urap_lon)
    r2b4 = make_xarray_dataset(
        r2b4_zonal_wind, r2b4_height_in_km, r2b4_lat, r2b4_lon)
    r2b7 = make_xarray_dataset(
        r2b7_zonal_wind, r2b7_height_in_km, r2b7_lat, r2b7_lon)

    print("PLOT DATA...")
    # fig: Figure, ax: Axes = plt.subplots()

    return


def cli():
    parser = ArgumentParser(description=DESCRIPTION,
                            formatter_class=RawDescriptionHelpFormatter)
    args = parser.parse_args()
    return args


def transform_zonal_wind(zonal_wind, time: int):
    return mean_on_longitude(zonal_wind)[time]


def transform_rnbk_height(rnbk_height):
    assert len(rnbk_height.shape) == N_RNBK_FULL_LEVEL_CENTER_HEIGHT_AXES
    rnbk_height_mean_on_lat_lon = mean(
        rnbk_height,
        axis=(
            RNBK_FULL_LEVEL_CENTER_HEIGHT_LATITUDE_AXIS,
            RNBK_FULL_LEVEL_CENTER_HEIGHT_LONGITUDE_AXIS))
    rnbk_height_mean_on_lat_lon_in_km = convert_meters_to_kilometers(
        rnbk_height_mean_on_lat_lon)
    return rnbk_height_mean_on_lat_lon_in_km


def mean_on_longitude(zonal_wind):
    assert len(zonal_wind.shape) == N_ZONAL_WIND_AXES
    return mean(zonal_wind, axis=ZONAL_WIND_LONGITUDE_AXIS)


def make_xarray_dataset(zonal_wind, height_in_km, lat, lon):
    dataset = xarr.DataArray(
        zonal_wind,
        dims=[TIME, HEIGHT, LATITUDE, LONGITUDE],
        coords={
            TIME: range(N_MONTHS),
            HEIGHT: (HEIGHT, height_in_km, {UNITS: HEIGHT_UNITS}),
            LATITUDE: lat,
            LONGITUDE: lon
        },
        name=RNBK_ZONAL_WIND,
        attrs={UNITS: ZONAL_WIND_UNITS}
    )
    return dataset


if __name__ == "__main__":
    main()
