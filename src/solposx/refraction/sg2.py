"""SG2 refraction model."""
import numpy as np


def sg2(elevation, pressure=101325., temperature=12.):
    """
    Atmospheric refraction correction of solar position based on SG2.

    This function calculates the atmospheric refraction correction of the solar
    elevation angle using the method developed by Ph. Blanc and L. Wald [1]_.

    Parameters
    ----------
    elevation : numeric
        True solar elevation angle (not accounting for refraction). [degrees]
    pressure : numeric, default 101325
        Local atmospheric pressure. [Pascal]
    temperature : numeric, default 12
        Local air temperature. [C]

    Returns
    -------
    refraction_correction : numeric
        Refraction correction. [degrees]

    Notes
    -----
    The equation to calculate the refraction correction is given by:

    .. math::
       For el > -0.01 [rad]:
           ref = \frac{P}{1010}*\frac{283}{273+T}*\frac{2.96706*10^{-4}}{tan(el+0.0031376*(el+0.089186)^{-1})}

       For el < -0.01 [rad]:
           ref = -\frac{P}{1010}*\frac{283}{273+T}*\frac{1.005516*10^{-4}}{tan(el)}

    where :math:`P` is the local air pressure, :math:`T` is the local air
    temperature, and :math:`el` is the true solar elevation angle.

    References
    ----------
    .. [1] Blanc, Ph., Wald, L. The SG2 algorithm for a fast and accurate
       computation of the position of the sun for multidecadal time period.
       Solar Energy vol. 86 (10), pp. 3072-3083.
       :doi:`10.1016/j.solener.2012.07.018`.
    """
    pressure = pressure / 100  # convert Pa to hPa
    elevation_rad = np.deg2rad(elevation)

    refraction = np.where(
        elevation_rad > -0.01,
        ((pressure * 283 * 2.96706 * 10**-4) /
         (1010 * (273 + temperature)
          * np.tan(elevation_rad + 0.0031376 *
                   (elevation_rad + 0.089186)**-1))),
        ((-pressure * 283 * 1.005516*10**-4) /
         (1010 * (273 + temperature) * np.tan(elevation_rad)))
        )

    return np.rad2deg(refraction)
