import pandas as pd
import numpy as np
from solposx.tools import _pandas_to_utc
from pvlib.solarposition import _datetime_to_unixtime


def soltrack(times, latitude, longitude, air_pressure=101325, temperature=12):
    """
    Calculate solar position using the SolTrack algorithm.

    The SolTrack algorithm [1]_ has a stated uncertainty of 0.0036 ± 0.0042◦
    from years 2017–2116.

    Parameters
    ----------
    times : pandas.DatetimeIndex
        Timestamps - must be localized. Prior to 1970 and far in
        the future UTC and UT1 may deviate significantly. For such use
        cases,  UT1 times should be provided.
    latitude : float
        Latitude in decimal degrees. Positive north of equator, negative
        to south. [degrees]
    longitude : float
        Longitude in decimal degrees. Positive east of prime meridian,
        negative to west. [degrees]
    air_pressure : float, default : 101325
        Annual average air pressure. [Pa]
    temperature : float, default : 12
        Annual average air temperature. [°C]

    Returns
    -------
    pandas.DataFrame
        DataFrame with the following columns (all values in degrees):

        - elevation : actual sun elevation (not accounting for refraction).
        - apparent_elevation : sun elevation, accounting for
          atmospheric refraction.
        - zenith : actual sun zenith (not accounting for refraction).
        - apparent_zenith : sun zenith, accounting for atmospheric
          refraction.
        - azimuth : sun azimuth, east of north.

    References
    ----------
    .. [1] Marc van der Sluys and Paul van Kan, "SolTrack: a free,
       fast and accurate routine to compute the position of the Sun,"
       2022, arXiv. :doi:`10.48550/arXiv.2209.01557`
    """
    times_utc = _pandas_to_utc(times)
    tJd = np.asarray(times_utc.to_julian_date()) - 2451545
    tJc = tJd / 36525

    # angular quantities are in radians
    latitude = np.radians(latitude)
    longitude = np.radians(longitude)

    # Eqs 2 and 3
    lam0 = 4.895063168 + 628.331966786 * tJc + 5.291838e-6 * tJc**2
    M = 6.240060141 + 628.301955152 * tJc - 2.682571e-6 * tJc**2 

    # Eqs 4 and 5
    C = (
        (3.34161088e-2 - 8.40725e-5*tJc - 2.443e-7*tJc**2) * np.sin(M) +
        (3.489437e-4 - 1.76278e-6 * tJc) * np.sin(2*M)
    )
    lam = lam0 + C

    # Eq 6
    omega = 2.1824390725 - 33.7570464271 * tJc + 3.622256e-5 * tJc**2 

    # Eq 7
    delta_psi = -8.338601e-5 * np.sin(omega)

    # Eqs 8, 9, 10
    e = 0.016708634 - 4.2037e-5 * tJc - 1.267e-7 * tJc**2
    v = M + C
    R = 1.0000010178 * (1 - e**2) / (1 + e * np.cos(v))

    # Eq 11
    # R = 1.0000010178

    # Eq 12
    delta_lam = -9.93087e-5 / R

    # Eq 13
    lam = lam + delta_lam + delta_psi

    # Eq 14
    # beta = 0

    # Eqs 15, 16, 17
    eps0 = 0.409092804222 - 2.26965525e-4 * tJc - 2.86e-9 * tJc**2
    delta_eps = 4.4615e-5 * np.cos(omega)
    eps = eps0 + delta_eps

    # Eqs 18, 19
    # simplified because beta=0
    alpha = np.arctan2(np.sin(lam) * np.cos(eps), np.cos(lam))
    delta = np.arcsin(np.sin(eps) * np.sin(lam))

    # Eqs 20, 21, 22, 23
    delta_theta = delta_psi * np.cos(eps)
    theta0 = 4.89496121 + 6.300388098985 * tJd + 6.77e-6 * tJc**2
    theta = theta0 + delta_theta + longitude
    H = theta - alpha

    # Eqs 24, 25
    h = np.arcsin(np.sin(delta) * np.sin(latitude) +
                  np.cos(H) * np.cos(delta) * np.cos(latitude))
    A = np.arctan2(np.sin(H),
                   np.cos(H)*np.sin(latitude) -np.tan(delta)*np.cos(latitude))

    # nearly same as SPA, but constants are very slightly different
    refraction_correction = (
        0.0002967 /
        np.tan(h + 0.0031376 / (h + 0.0892)) *
        (283 / (temperature+273.15)) *
        (air_pressure / 101000)
    )

    elevation = np.degrees(h)
    apparent_elevation = np.degrees(h + refraction_correction)
    azimuth = (np.degrees(A) + 180) % 360
    zenith = 90 - elevation
    apparent_zenith = 90 - apparent_elevation

    result = pd.DataFrame(
        {
            "elevation": elevation,
            "apparent_elevation": apparent_elevation,
            "zenith": zenith,
            "apparent_zenith": apparent_zenith,
            "azimuth": azimuth,
        },
        index=times,
    )
    return result
