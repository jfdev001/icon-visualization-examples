"""TODO plotting and data analyssi for local area

* ignore the cdo monmean if you want 
* focus on remapped files 
* slice the lat/lon that you need... to do this try 

```python
zonal_wind_remapped_netcdf.variables["u"][put your slice indices here...]
# todo: do the same levels 
```

plot as you need ...

"""

from cdo import Cdo
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
from pathlib import Path
import os

print("Loading CDO")
cdo = Cdo()

ZONAL_WIND: str = "u"
LATITUDE: str = "lat"
FULL_LEVEL_CENTER_HEIGHT: str = "z_mc"

# Define paths
UAICON_dir = "/work/bm1233/m300685/UAICON"
R2B7_free_30_years_dir = os.path.join(UAICON_dir, "R2B7_free_30_years")

r2b7_netcdf_path = os.path.join(
    R2B7_free_30_years_dir, "R2B7_free_30_years_atm_3d_ML_20290101T000000Z.nc")

r2b7_netcdf_basename_without_file_extension = Path(
    os.path.basename(r2b7_netcdf_path)).stem

grid_file = os.path.join(
    UAICON_dir, "INPUT_R2B7_VORTEX_new/icongrid_DOM01.nc")

grid_definition = ":2"
grid_file_with_grid_definition = grid_file + grid_definition

levels_file = os.path.join(
    UAICON_dir, "R2B7_free_30_years/R2B7_free_30_years_const_ML.nc")

output_dir = "data"

assert os.path.exists(UAICON_dir)
assert os.path.exists(r2b7_netcdf_path)
assert os.path.exists(grid_file)
assert os.path.exists(levels_file)

#
# uncomment below to load the data and inspect variable names
#
# r2b7_dataset = Dataset(r2b7_netcdf_path)
# print(r2b7_dataset.variables)

# Compute the mean of the zonal wind over a month and write results
r2b7_netcdf_monmean_basename = r2b7_netcdf_basename_without_file_extension +\
    "_monmean.nc"

r2b7_zonal_wind_monmean_output_path = os.path.join(
    output_dir, r2b7_netcdf_monmean_basename)

# compute operations like this can take some time
if not os.path.exists(r2b7_zonal_wind_monmean_output_path):
    print(
        "Computing monmean: ${r2b7_netcdf_path} to {r2b7_zonal_wind_monmean_output_path}")
    cdo.monmean(  # writes ~1 GB data, may take 1-5 minutes
        input=f"-selvar,{ZONAL_WIND} {r2b7_netcdf_path}",
        output=r2b7_zonal_wind_monmean_output_path)

# Perform a remap operation on the monthly mean data
output_grid_type = "n45"
r2b7_zonal_wind_monmean_remapped_output_path = os.path.join(
    output_dir, Path(r2b7_zonal_wind_monmean_output_path).stem +
    f"_{output_grid_type}_remapped.nc")

# remapping is a fast operation
if not os.path.exists(r2b7_zonal_wind_monmean_remapped_output_path):
    print(
        f"Remapping: {r2b7_zonal_wind_monmean_output_path} to {r2b7_zonal_wind_monmean_remapped_output_path}")
    cdo.remapdis(
        output_grid_type,
        input=f"-setgrid,{grid_file_with_grid_definition} {r2b7_zonal_wind_monmean_output_path}",
        output=r2b7_zonal_wind_monmean_remapped_output_path)

# Perform a remap operation on the levels file contains topographical variables
# NOTE: The file produced by this operation need only be produced once
# since the topographical variables (e.g., height, z_mc, topography_c, etc)
# are constant throughout the simulation
levels_file_remapped_output_path = os.path.join(
    output_dir,
    Path(os.path.basename(levels_file)).stem + f"_{output_grid_type}_remapped.nc")

if not os.path.exists(levels_file_remapped_output_path):
    print(
        f"Remapping: {levels_file} to {levels_file_remapped_output_path}")
    cdo.remapdis(
        output_grid_type,
        input=f"-setgrid,{grid_file_with_grid_definition} {levels_file}",
        output=levels_file_remapped_output_path)

# Load the processed and remapped data
# NOTE: the Dataset defines variables and dimensions for that variable
# e.g., 'u' with dimensions (time, height, lat, lon). The dimensions
# for such a variable also have values, e.g., one can extract 'lat' which
# has dimensions (lat) where lat = 90 as defined in the dimensions: field
# from ncdump -h
zonal_wind_remapped_netcdf = Dataset(
    r2b7_zonal_wind_monmean_remapped_output_path)
levels_remapped_netcdf = Dataset(levels_file_remapped_output_path)

# Extract values that you wish to plot from the netcdf datasets
# NOTE: also some sanity (assert) checks on dims of variables
zonal_wind_arr: np.ndarray = zonal_wind_remapped_netcdf.variables[
    ZONAL_WIND][:]

time_dimension = 1  # the netcdf file is just one month
height_dimension = 180  # the generalized height, Z axis
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
contourf_levels = np.linspace(-100, 100, 32)
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
contour_levels = np.hstack((
    np.linspace(zonal_wind_arr.min(), zonal_wind_arr.max(), 15),
))
contour_kwargs = dict(
    levels=contour_levels, linewidths=0.5, colors="k")

clabel_kwargs = dict(inline=True, fmt="%d", fontsize=10)

ax_set_ylim_kwargs = dict(bottom=0, top=150)
ax_set_xlim_kwargs = dict(left=-90, right=90)

# Plot the zonal wind contours for a single month
fig, ax = plt.subplots(figsize=(15, 8))

# since time dimension length is 1, then 0'th index gets the zonal wind
# for a given month and then the mean over the last dimension (-1) is longitude
# resulting dim: (height, lat)
mean_on_longitude_for_zonal_wind_in_month_arr = np.mean(
    zonal_wind_arr[0], axis=-1)

# resulting dim: (height,)
meter_per_kilometer = 1000
mean_on_lat_lon_for_full_level_center_height_in_km_arr = np.mean(
    full_level_center_height_arr, axis=(1, 2)) / meter_per_kilometer

contourf = ax.contourf(
    lat_arr,  # (lat,)
    mean_on_lat_lon_for_full_level_center_height_in_km_arr,  # (height,)
    mean_on_longitude_for_zonal_wind_in_month_arr,    # (height, lat)
    **contourf_kwargs)

fig.colorbar(
    contourf,
    ax=ax,
    **colorbar_kwargs)

contour = ax.contour(
    lat_arr,
    mean_on_lat_lon_for_full_level_center_height_in_km_arr,
    mean_on_longitude_for_zonal_wind_in_month_arr,
    **contour_kwargs)

ax.clabel(contour, **clabel_kwargs)

ax.set_xlabel("Latitude")
ax.set_ylabel("Height (km)")
ax.set_title(
    "Monmean+Remapped Zonal Wind for"
    f"\n{os.path.basename(r2b7_zonal_wind_monmean_remapped_output_path)}")

fig_output_path = os.path.join(output_dir, "zonal_wind_contour.png")
fig.tight_layout()
fig.savefig(fig_output_path)
