from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os import mkdir
from os.path import join, exists, dirname
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from netCDF4 import Dataset

DESCRIPTION: str = """
Plot contour differences for zonal winds to illustrate how increasing grid
resolution (i.e., R2B4 to R2B7) more accurately reflects ground truth 
winds (i.e., URAP data).
"""

LATITUDE: str = "lat"
LONGITUDE: str = "lon"

RNBK_ZONAL_WIND: str = "u"
RNBK_HEIGHT: str = "height"
RNBK_FULL_LEVEL_CENTER_HEIGHT: str = "z_mc"

URAP_ZONAL_WIND: str = "ua"
URAP_LEVEL: str = "lev"

N_AXES: int = 4
TIME_AXIS: int = 0
HEIGHT_OR_LEVEL_AXIS: int = 1
LATITUDE_AXIS: int = 2
LONGITUDE_AXIS: int = 3

METERS_PER_KILOMETER: int = 1000


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

    r2b4_zonal_wind_file = join(
        r2b4_dir,
        "daily_mean",
        "UAL120_150_F03C14L00S30_u-atm_3d_dm_ml_ymonmean_2019-2029_RM.nc")
    assert exists(r2b4_zonal_wind_file)
    r2b7_zonal_wind_file = join(
        r2b7_dir, "R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc")
    assert exists(r2b7_zonal_wind_file)
    urap_zonal_wind_file = join(urap_dir, "urap_ymonmean.nc")
    assert exists(urap_zonal_wind_file)

    print("load data...")

    # TODO: pressure level to height for URAP
    print("transform data...")

    print("plot data...")
    return


def cli():
    parser = ArgumentParser(description=DESCRIPTION,
                            formatter_class=RawDescriptionHelpFormatter)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
