import numpy as np
import pandas as pd
from solposx.tools import _pandas_to_utc


def enea(times, latitude, longitude, air_pressure=101325, temperature=12, delta_t=67.0):
    """
    Calculate solar position using the ENEA algorithm.

    The ENEA algorithm [1]_ has a stated accuracy of 0.0027 degrees
    from 2003–2023.

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
    delta_t : numeric, default : 67.0
        Difference between terrestrial time and UT1. [seconds]

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
    .. [1] R. Grena, "An algorithm for the computation of the solar
       position," Solar Energy, vol. 82, no. 5, pp. 462–470, May 2008,
       :doi:`10.1016/j.solener.2007.10.001`
    """
    phi = np.radians(latitude)
    theta = np.radians(longitude)

    times_utc = _pandas_to_utc(times)
    y = np.asarray(times_utc.year)
    m = np.asarray(times_utc.month)
    d = np.asarray(times_utc.day)
    UT = np.asarray(times_utc.hour) + np.asarray(times_utc.minute) / 60 + np.asarray(times_utc.second) / 3600

    mask = m <= 2
    mb = np.where(mask, m+12, m)
    yb = np.where(mask, y-1, y)
    tG = (
        np.trunc(365.25 * (yb - 2000))
        + np.trunc(30.6001 * (mb + 1))
        + d + UT/24 - 1158.5
    )
    t = tG + delta_t / 86400

    # section 3 - heliocentric longitude
    sigma = 1.72019e-2 * t - 0.0563
    Ly = (
        1.74094 + 1.7202768683e-2 * t + 3.34118e-2 * np.sin(sigma)
        + 3.488e-4 * np.sin(2*sigma)
    )
    Lm = 3.13e-5 * np.sin(0.2127730 * t - 0.585)
    Lh = (
         1.26e-5 * np.sin(4.243e-3 * t + 1.46) +
         2.35e-5 * np.sin(1.0727e-2 * t + 0.72) +
         2.76e-5 * np.sin(1.5799e-2 * t + 2.35) +
         2.75e-5 * np.sin(2.1551e-2 * t - 1.98) +
         1.26e-5 * np.sin(3.1490e-2 * t - 0.80)
    )
    t2 = 0.001 * t
    Lp = (
        ((-2.30796e-7*t2 + 3.7976e-6) * t2 - 2.0458e-5) * t2 + 3.976e-5
    ) * t2**2
    L = Ly + Lm + Lh + Lp

    delta_gamma = 8.33e-5 * np.sin(9.262e-4 * t - 1.173)
    epsilon = -6.21e-9 * t + 0.409086 + 4.46e-5 * np.sin(9.252e-4 * t + 0.397)
    gamma = L + np.pi + delta_gamma - 9.932e-5
    
    alpha = np.arctan2(np.sin(gamma)*np.cos(epsilon), np.cos(gamma))
    delta = np.arcsin(np.sin(epsilon)*np.sin(gamma))
    h = 6.30038809903 * tG + 4.8824623 + 0.9174 * delta_gamma + theta - alpha
    delta_alpha = -4.26e-5 * np.cos(phi) * np.sin(h)
    
    alpha_topo = alpha + delta_alpha
    delta_topo = delta - 4.26e-5 * (np.sin(phi) - delta * np.cos(phi))

    h_topo = h - delta_alpha
    ch_topo = np.cos(h) + delta_alpha * np.sin(h)
    sh_topo = np.sin(h) - delta_alpha * np.cos(h)

    e0 = np.arcsin(
        np.sin(phi) * np.sin(delta_topo) +
        np.cos(phi) * np.cos(delta_topo) * ch_topo
    )
    delta_e = (
        0.084217 * (air_pressure/101325) / ((273+temperature) * 
        np.tan(e0 + 0.0031376 / (e0 + 0.089186)))
    )
    # no lower limit specified; uses same limit as SPA    
    delta_e = np.where(e0 > np.radians(-0.83337), delta_e, 0)
    
    az = np.arctan2(sh_topo, ch_topo * np.sin(phi) - np.tan(delta_topo) * np.cos(phi))

    e0 = np.degrees(e0)
    delta_e = np.degrees(delta_e)
    az = np.degrees(az) + 180

    result = pd.DataFrame(
        {
            "elevation": e0,
            "apparent_elevation": e0 + delta_e,
            "zenith": 90 - e0,
            "apparent_zenith": 90 - (e0 + delta_e),
            "azimuth": az,
        },
        index=times,
    )
    return result
