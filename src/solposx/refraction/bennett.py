"""Bennett refraction model."""

from pvlib.tools import tand


def bennett(apparent_elevation, pressure=101325.0, temperature=12.0):
    r"""
    Atmospheric refraction correction based on the Bennett algorithm.

    Calculation of atmospheric refraction correction based on the
    apparent solar elevation angle using the method developed by
    Bennett [1]_.

    Parameters
    ----------
    apparent_elevation : array-like
        Apparent solar elevation angle (accounting for refraction). [degrees]
    pressure : numeric, default 101325
        Annual average atmospheric pressure. [Pascal]
    temperature : numeric, default 12
        Annual average air temperature. [C]

    Returns
    -------
    np.array or pd.Series
        Atmospheric refraction angle. [degrees]

    Warning
    -------
    The Bennet refraction algorithm calculates refraction based on the apparent
    solar position, which is in contrast to most refraction algorithms, which
    calculate refraction from the unrefracted true solar position.

    Notes
    -----
    The equation to calculate the refraction correction is given by:

    .. math::

       ref = \frac{0.28*P}{T+273} \cdot \frac{0.016667}{\text{tan}(el_a + 7.31 / (el_a+4.4))}

    where :math:`P` is the local air pressure, :math:`T` is the local air
    temperature, and :math:`el_a` is the apparent (corrected) solar elevation angle.

    References
    ----------
    .. [1] G. Bennett, "The calculation of astronomical refraction in marine
       navigation," Journal of Navigation, vol. 35, issue 2, pp. 255-259,
       1982, :doi:`10.1017/S0373463300022037`.
    """  # noqa: E501

    pressure = pressure / 100  # convert to hPa

    r = 0.016667 / tand(apparent_elevation + 7.31 / (apparent_elevation + 4.4))

    d = r * (0.28 * pressure / (temperature + 273.0))

    return d
