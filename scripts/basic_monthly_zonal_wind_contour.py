"""Contour plot zonal wind for each month where data averaged from 2019-2029.

Example:

```shell
python scripts/basic_monthly_zonal_wind_contour.py
```

References:

* https://unidata.github.io/netcdf4-python/
"""

from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from pathlib import Path
import os

# Define constants
ZONAL_WIND: str = "u"
LATITUDE: str = "lat"
FULL_LEVEL_CENTER_HEIGHT: str = "z_mc"
N_MONTHS: int = 12
METERS_PER_KILOMETER: int = 1000

# Define paths
dir_of_current_script = Path(os.path.dirname(__file__))
project_dir = dir_of_current_script.parent
data_dir = "data/"

r2b7_netcdf_file = os.path.join(
    data_dir, "R2B7_free_30_years_u-atm_3d_ML_ymonmean_2019-2029_RM.nc")

r2b7_netcdf_basename_without_file_extension = Path(
    os.path.basename(r2b7_netcdf_file)).stem

levels_file = os.path.join(data_dir, "hfile.nc")

output_dir = os.path.join(project_dir, "plots")
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

assert os.path.exists(r2b7_netcdf_file)
assert os.path.exists(levels_file)

#
# uncomment below to load the data and inspect variable names
#
# r2b7_dataset = Dataset(r2b7_netcdf_file)
# print(r2b7_dataset.variables)


# Load the processed and remapped data
# NOTE: the Dataset defines variables and dimensions for that variable
# e.g., 'u' with dimensions (time, height, lat, lon). The dimensions
# for such a variable also have values, e.g., one can extract 'lat' which
# has dimensions (lat) where lat = 90 as defined in the dimensions: field
# from ncdump -h
zonal_wind_remapped_netcdf = Dataset(r2b7_netcdf_file)
levels_remapped_netcdf = Dataset(levels_file)

# Extract values that you wish to plot from the netcdf datasets
# NOTE: also some sanity (assert) checks on dims of variables
zonal_wind_arr: np.ndarray = zonal_wind_remapped_netcdf.variables[
    ZONAL_WIND][:]

time_dimension = N_MONTHS     # the netcdf file is over 12 months
height_dimension = 180        # the generalized height, Z axis
latitude_dimension = 90
longitude_dimension = 180

assert len(zonal_wind_arr.shape) == 4
assert zonal_wind_arr.shape[0] == time_dimension
assert zonal_wind_arr.shape[1] == height_dimension
assert zonal_wind_arr.shape[2] == latitude_dimension
assert zonal_wind_arr.shape[3] == longitude_dimension

lat_arr: np.ndarray = zonal_wind_remapped_netcdf.variables[LATITUDE][:]
assert len(lat_arr.shape) == 1
assert lat_arr.shape[0] == latitude_dimension

full_level_center_height_arr: np.ndarray = levels_remapped_netcdf.variables[
    FULL_LEVEL_CENTER_HEIGHT][:]
assert len(full_level_center_height_arr.shape) == 3
assert full_level_center_height_arr.shape[0] == height_dimension
assert full_level_center_height_arr.shape[1] == latitude_dimension
assert full_level_center_height_arr.shape[2] == longitude_dimension

# Define contour plotting configuration
n_contourf_levels = 32
contourf_levels = np.linspace(-100, 100, n_contourf_levels)
contourf_kwargs = dict(
    levels=contourf_levels,
    # vmin and vmax mean that contour levels beyond these ranges are a single
    # color
    vmin=-100,
    vmax=100,
    cmap="bwr",
    extend="both"
)

colorbar_ticks = range(-100, 110, 10)
colorbar_kwargs = dict(
    ticks=colorbar_ticks, label="zonal wind (m s-1)")

# define contour lines even beyond the vmin and vmax
n_contour_lines = 20
contour_levels = np.hstack((
    np.linspace(zonal_wind_arr.min(), zonal_wind_arr.max(), n_contour_lines),
))
contour_kwargs = dict(
    levels=contour_levels, linewidths=0.5, colors="k")

clabel_kwargs = dict(inline=True, fmt="%d", fontsize=10)

ax_set_ylim_kwargs = dict(bottom=0, top=150)
ax_set_xlim_kwargs = dict(left=-90, right=90)

# Plot the zonal wind contours for a single month
fig: Figure
ax: Axes
fig, ax = plt.subplots(figsize=(15, 8))

# Iterate through each month in the data
n_months = zonal_wind_arr.shape[0]
for month in range(n_months):
    print(f"Zonal plot for month: {month+1:02d}")
    # average zonal wind over longitude
    # result dim: (time, height, lat, lon) --> (height, lat)
    mean_on_longitude_for_zonal_wind_in_month_arr = np.mean(
        zonal_wind_arr[month], axis=-1)

    # average vertical value over latitude and longitude and convert to km
    # resulting dim: (height, lat, lon) --> (height,)
    mean_on_lat_lon_for_full_level_center_height_in_km_arr = np.mean(
        full_level_center_height_arr, axis=(1, 2)) / METERS_PER_KILOMETER

    # Write the contour "colors" on the plot
    contourf = ax.contourf(
        lat_arr,  # (lat,)
        mean_on_lat_lon_for_full_level_center_height_in_km_arr,  # (height,)
        mean_on_longitude_for_zonal_wind_in_month_arr,    # (height, lat)
        **contourf_kwargs)

    cb = fig.colorbar(
        contourf,
        ax=ax,
        **colorbar_kwargs)

    # Write the contour lines onto the plot
    contour = ax.contour(
        lat_arr,
        mean_on_lat_lon_for_full_level_center_height_in_km_arr,
        mean_on_longitude_for_zonal_wind_in_month_arr,
        **contour_kwargs)

    # Label elements of plot
    ax.clabel(contour, **clabel_kwargs)
    ax.set_xlabel("Latitude")
    ax.set_ylabel("Height (km)")
    ax.set_title(
        f"Zonal Wind Contour: Month {month+1:02d} Averaged Over 2019-2029")

    # Save plot
    fig_output_path = os.path.join(
        output_dir, f"{month+1:02d}_monthly_r2b7_zonal_wind_contour.png")
    fig.tight_layout()
    fig.savefig(fig_output_path)

    # Clear the previous plot of its element so you can reuse it to write
    # new plot data
    # NOTE: order is important here, if you try to cb.remove() after
    # ax.clear(), then error
    cb.remove()
    ax.clear()

print(f"Results written to: {output_dir}")
