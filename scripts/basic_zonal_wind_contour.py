"""CDO to average zonal wind `u` by month and then plot as contours.

TODO: Might need to pay attention to module load of cdo/netcdf for whether it
supports the necessary version for processing ICON data.

It is also useful to inspect netcdf files on the command line to get a quick
overview of the variables, their dimensions, units, etc.

```shell
ncdump -h <path-to-file-here>
```
"""

import matplotlib.pyplot as plt
from netCDF4 import Dataset

ZONAL_WIND: str = "u"

# Arbitrary r2b7 file path
r2b7_netcdf_path = "/work/bm1233/m300685/UAICON/R2B7_free_30_years/R2B7_free_30_years_ua_3d_ML_20290101T000000Z.nc"

# Load the data and inspect variable names
r2b7_dataset = Dataset(r2b7_netcdf_path)

print(r2b7_dataset.variables)

# Perform a mean operation

# Perform a remap operation on the monthly mean data

# Perform a remap operation on the height file contains topographical variables
# NOTE: The file produced by this operation need only be produced once
# since the topographical variables (e.g., height, z_mc, topography_c, etc)
# are constant throughout the simulation

#
