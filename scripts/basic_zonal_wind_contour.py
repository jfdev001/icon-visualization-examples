"""CDO to average zonal wind `u` by month and then plot as contours.

TODO: Might need to pay attention to module load of cdo/netcdf for whether it
supports the necessary version for processing ICON data.

It is also useful to inspect netcdf files on the command line to get a quick
overview of the variables, their dimensions, units, etc.

```shell
ncdump -h <path-to-file-here>
```

# References

* https://code.mpimet.mpg.de/attachments/download/27273/python_cdo_introduction.pdf
* https://code.mpimet.mpg.de/projects/cdo/wiki/Cdo#Documentation
* https://unidata.github.io/netcdf4-python/
"""

from cdo import Cdo
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from pathlib import Path
import os

print("Loading CDO")
cdo = Cdo()

ZONAL_WIND: str = "u"

# Define paths
UAICON_dir = "/work/bm1233/m300685/UAICON"

r2b7_netcdf_path = os.path.join(
    UAICON_dir,
    "R2B7_free_30_years/R2B7_free_30_years_atm_3d_ML_20290101T000000Z.nc")

r2b7_netcdf_basename_without_file_extension = Path(
    os.path.basename(r2b7_netcdf_path)).stem

grid_file = os.path.join(
    UAICON_dir, "INPUT_R2B7_VORTEX_new/icongrid_DOM01.nc")

grid_definition = ":2"
grid_file_with_grid_definition = grid_file + grid_definition

levels_file = os.path.join(
    UAICON_dir, "R2B7_free_30_years/R2B7_free_30_years_const_ML.nc")

output_dir = "tmp"

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

r2b7_monmean_output_path = os.path.join(
    output_dir, r2b7_netcdf_monmean_basename)

# compute operations like this can take some time
if not os.path.exists(r2b7_monmean_output_path):
    print(
        "Computing monmean: ${r2b7_netcdf_path} to {r2b7_monmean_output_path}")
    cdo.monmean(  # writes ~1 GB data, may take 1-5 minutes
        input=f"-selvar,{ZONAL_WIND} {r2b7_netcdf_path}",
        output=r2b7_monmean_output_path)

# Perform a remap operation on the monthly mean data
output_grid_type = "n45"
r2b7_monmean_remapped_output_path = os.path.join(
    output_dir, Path(r2b7_monmean_output_path).stem +
    f"_{output_grid_type}_remapped.nc")

# remapping is a fast operation
if not os.path.exists(r2b7_monmean_remapped_output_path):
    print(
        f"Remapping: {r2b7_monmean_output_path} to {r2b7_monmean_remapped_output_path}")
    cdo.remapdis(
        output_grid_type,
        input=f"-setgrid,{grid_file_with_grid_definition} {r2b7_monmean_output_path}",
        output=r2b7_monmean_remapped_output_path)

# Perform a remap operation on the levels file contains topographical variables
# NOTE: The file produced by this operation need only be produced once
# since the topographical variables (e.g., height, z_mc, topography_c, etc)
# are constant throughout the simulation
levels_file_remapped_output_path = os.path.join(
    output_dir, f"levels_file_{output_grid_type}_remapped.nc")

if not os.path.exists(levels_file_remapped_output_path):
    print(
        f"Remapping: {levels_file} to {levels_file_remapped_output_path}")
    cdo.remapdis(
        output_grid_type,
        input=f"-setgrid,{grid_file_with_grid_definition} {levels_file}",
        output=levels_file_remapped_output_path)

# do some simple plotting here

