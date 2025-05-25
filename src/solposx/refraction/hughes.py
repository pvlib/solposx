"""Hughes refraction model."""
import numpy as np
import pandas as pd


def hughes(elevation, pressure=101325., temperature=12.):
    r"""
    Atmospheric refraction correction of solar position based on Grover Hughes.

    This function was developed by G. Hughes as part of the SUNAEP software
    [1]_.
    It is also used to calculate the refraction correction in the NOAA
    solar position algorithm using a fixed pressure = 101325 Pa and
    temperature = 10 [C]

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

        For 5° < el <= 90°:
            ref = \frac{58.1}{tan(el)} - \frac{0.07}{tan(el)^3} + \frac{8.6*10^{-5}}{tan(el)^5}

        For -0.575 < el <= 5:
            ref = el *(-518.2 + el *(103.4 + el *(-12.79 + el *0.711))) + 1735

        For el <= -0.575:
            ref = \frac{-20.774}{tan(el)}

    where :math:`el` is the true solar elevation angle.

    References
    ----------
    .. [1] J. C. Zimmerman, "Sun-pointing programs and their accuracy."
       SANDIA Technical Report SAND-81-0761, :doi:`10.2172/6377969`
    """
    TanEl = pd.Series(np.tan(np.radians(elevation)))
    Refract = pd.Series(0, TanEl.index, dtype=np.float64)

    Refract[(elevation > 5) & (elevation <= 85)] = (
        58.1/TanEl - 0.07/(TanEl**3) + 8.6e-05/(TanEl**5))

    Refract[(elevation > -0.575) & (elevation <= 5)] = (
        elevation *
        (-518.2 + elevation*(103.4 + elevation*(-12.79 + elevation*0.711))) +
        1735)

    Refract[elevation <= -0.575] = -20.774 / TanEl
    Refract *= (283/(273. + temperature)) * (pressure/101325.) / 3600.

    return Refract.values
