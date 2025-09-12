from numpy import log


def convert_pressure_in_hPa_to_height_in_km(pressure_in_hPa):
    """Computes the height z in km given pressure using scaled height.

    Solving `P = P0*exp(-z / H)` for `z` yields `z = H*ln(P0/P)`.

    References:
        [1] : https://en.wikipedia.org/wiki/Scale_height 
    """
    P0_pressure_at_sea_level_in_hPa = 1013.25
    H_scale_height_in_km = 7.64
    z_height_in_km = H_scale_height_in_km*log(
        P0_pressure_at_sea_level_in_hPa/pressure_in_hPa)
    return z_height_in_km
