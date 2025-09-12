from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import mkdir
from os.path import join, exists, dirname
from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.colors import TwoSlopeNorm
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedFormatter
import netCDF4 as nc
from numpy import ndarray, mean, linspace, hstack
import xarray as xarr

from src.consts import MONTHS, N_MONTHS
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

JANUARY_IX: int = 0
JULY_IX: int = 6


def main():
    # parse cli
    args = cli()

    plots_dir: str = args.plots_dir
    if not exists(plots_dir):
        mkdir(plots_dir)

    width: int = args.figsize_width_in_inches
    height: int = args.figsize_height_in_inches
    dpi: int = args.dpi

    # check directories
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

    # loading and checking data
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

    # preparing data for difference plotting
    print("TRANSFORM DATA...")
    urap_height_in_km = convert_pressure_in_hPa_to_height_in_km(urap_level)
    r2b4_height_in_km = transform_rnbk_height(r2b4_height_in_meters)
    r2b7_height_in_km = transform_rnbk_height(r2b7_height_in_meters)

    urap = (
        make_xarray_dataset(
            urap_zonal_wind, urap_height_in_km, urap_lat, urap_lon)
        .mean(dim=LONGITUDE))

    r2b4 = (
        make_xarray_dataset(
            r2b4_zonal_wind, r2b4_height_in_km, r2b4_lat, r2b4_lon)
        .mean(dim=LONGITUDE)
    )

    r2b7 = (
        make_xarray_dataset(
            r2b7_zonal_wind, r2b7_height_in_km, r2b7_lat, r2b7_lon)
        .mean(dim=LONGITUDE)
    )

    # interpolate to target datasets -- where interpolation occurs from
    # higher resolution to lower resolution dataset
    r2b4_to_urap = r2b4.interp({HEIGHT: urap.height, LATITUDE: urap.lat})

    r2b7_to_urap = r2b7.interp({HEIGHT: urap.height, LATITUDE: urap.lat})

    r2b7_to_r2b4 = r2b7.interp({HEIGHT: r2b4.height, LATITUDE: r2b4.lat})

    # plot difference contours for desired grid resolutions
    print(f"PLOT DATA TO {plots_dir}...")
    plot_difference_contours(
        reference=urap, other=r2b4_to_urap, plots_dir=plots_dir,
        savefig_path_annotation="r2b4_minus_urap",
        figsize=(width, height), dpi=dpi)
    plot_difference_contours(
        reference=urap, other=r2b7_to_urap, plots_dir=plots_dir,
        savefig_path_annotation="r2b7_minus_urap",
        figsize=(width, height), dpi=dpi)
    plot_difference_contours(
        reference=r2b4, other=r2b7_to_r2b4, plots_dir=plots_dir,
        savefig_path_annotation="r2b7_minus_r2b4",
        figsize=(width, height), dpi=dpi)

    return


def cli():
    parser = ArgumentParser(description=DESCRIPTION,
                            formatter_class=RawDescriptionHelpFormatter)

    dir_of_current_script = Path(dirname(__file__))
    project_dir = dir_of_current_script.parent
    plots_dir = join(project_dir, "plots_contour_difference")
    parser.add_argument(
        "--plots-dir", type=str, default=plots_dir,
        help=f"Directory to write contour difference plots. (default: {plots_dir})")
    parser.add_argument(
        "--figsize-width-in-inches", type=int, default=15,
        help="width in (width, height) for matplotlib plot. (default: 15)")
    parser.add_argument(
        "--figsize-height-in-inches", type=int, default=8,
        help="height in (width, height) for matplotlib plot. (default: 8)")
    parser.add_argument("--dpi", type=int, default=300,
                        help="(default: 300)")
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


def plot_difference_contours(
        reference: xarr.DataArray,
        other: xarr.DataArray,
        plots_dir: str,
        savefig_path_annotation: str,
        vmin: float = -80,
        vmax: float = 80,
        min_contour_fill: float = -100,
        max_contour_fill: float = 100,
        figsize: tuple[int, int] = (15, 8),
        dpi: int = 300):

    fig: Figure
    ax: Axes
    fig, ax = plt.subplots(figsize=figsize)

    difference = other - reference
    zonal_wind = difference.values

    # Define contour plotting configuration
    n_contourf_levels = 32
    contourf_levels = linspace(
        min_contour_fill, max_contour_fill, n_contourf_levels)
    norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
    contourf_kwargs = dict(
        levels=contourf_levels,
        extend="both",
        cmap="bwr",
        vmin=vmin,
        vmax=vmax,
        norm=norm
    )

    colorbar_ticks = range(vmin, vmax+10, 20)
    colorbar_kwargs = dict(
        label="zonal wind difference (m s-1)",
        ticks=colorbar_ticks)

    # define contour lines even beyond the vmin and vmax
    n_contour_lines = 20
    contour_levels = hstack((
        linspace(min_contour_fill, max_contour_fill, n_contour_lines),
    ))
    contour_kwargs = dict(
        levels=contour_levels, linewidths=0.5, colors="k")

    clabel_kwargs = dict(inline=True, fmt="%d", fontsize=10)

    ax_set_ylim_kwargs = dict(bottom=0, top=150)
    ax_set_xlim_kwargs = dict(left=-90, right=90)

    print(f"Difference Plot: {savefig_path_annotation}")
    for t in range(N_MONTHS):
        print(f"Month: {t+1:02d}")

        zonal_wind_at_t = zonal_wind[t]
        contour_fill = ax.contourf(
            difference.lat, difference.height, zonal_wind_at_t,
            **contourf_kwargs)
        colorbar = fig.colorbar(contour_fill, ax=ax, **colorbar_kwargs)
        contour_lines = ax.contour(
            difference.lat, difference.height, zonal_wind_at_t,
            **contour_kwargs)

        month = MONTHS[t]
        ax.clabel(contour_lines, **clabel_kwargs)
        ax.set_title(f"{savefig_path_annotation} {month}")
        ax.set_xlabel("Latitude")
        ax.set_ylabel("Height (km)")
        ax.set_xlim(**ax_set_xlim_kwargs)
        ax.set_ylim(**ax_set_ylim_kwargs)

        fig.tight_layout()
        fig.savefig(
            join(plots_dir, f"{t:02d}_{month}_{savefig_path_annotation}.png"),
            dpi=dpi)
        colorbar.remove()
        ax.clear()

    return fig, ax


if __name__ == "__main__":
    main()
