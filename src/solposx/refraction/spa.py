"""SPA refraction model."""
import numpy as np


def spa(elevation, pressure=101325, temperature=12, atmos_refract=0.5667):
    """
    Atmospheric refraction correction of solar position based on SPA.

    This function calculates the atmospheric refraction correction of the solar
    elevation angle using the method described in Reda and Andreas [1]_.

    Parameters
    ----------
    elevation : numeric
        True solar elevation angle (not accounting for refraction). [degrees]
    pressure : numeric, default 101325
        Local atmospheric pressure. [Pascal]
    temperature : numeric, default 12
        Local air temperature. [C]
    atmos_refract : float, default 0.5667
        The value of 0.5667 is typically adopted for the atmospheric refraction
        at sunrise and sunset times. [degrees]

    Returns
    -------
    refraction_correction : numeric
        Refraction correction. [degrees]

    Notes
    -----
    The equation to calculate the refraction correction is given by:

    .. math::

       ref = \frac{P}{1010} * \frac{283}{273 + T} * \frac{1.02}{60 * tan(el + \frac{10.3}{el + 
5.11})}

    where :math:`P` is the local air pressure, :math:`T` is the local air
    temperature and :math:`el` is the true solar elevation angle.

    References
    ----------
    .. [1] I. Reda, A. Andreas "Solar Position Algorithm for Solar Radiation
       Applications (Revised)." 2008. NREL Report No. TP-560-34302, pp. 55
       :doi:`10.2172/15003974`.

    """  # noqa: #501

    pressure = pressure / 100  # convert to hPa
    # switch sets elevation when the sun is below the horizon
    switch = elevation >= -1.0 * (0.26667 + atmos_refract)

    refraction_correction = (
        (pressure / 1010.0) * (283.0 / (273 + temperature))
        * 1.02 / (60 * np.tan(np.radians(elevation + 10.3 /
                                         (elevation + 5.11))))) * switch

    return refraction_correction
