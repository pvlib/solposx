import numpy as np
import pandas as pd
from solposx.tools import _pandas_to_utc
from pvlib.solarposition import _datetime_to_unixtime


def _grena_start(times, deltaT):
    times = _pandas_to_utc(times)
    y = times.year
    m = times.month
    d = times.day
    h = times.hour + times.minute / 60 + times.second / 3600

    mask = m <= 2
    mb = np.where(mask, m+12, m)
    yb = np.where(mask, y-1, y)
    t = (
        np.trunc(365.25 * (yb - 2000))
        + np.trunc(30.6001 * (mb + 1))
        - np.trunc(0.01 * yb)
        + d + h/24 - 21958
    ).values
    te = t + 1.1574e-5 * deltaT
    return t, te


def _grena_start_unixtime(times, deltaT):
    unixtime = _datetime_to_unixtime(times)
    # unix time is the number of seconds since 1970-01-01, but Grena needs
    # number of days since 2060-01-01.  The difference is 32872 days.
    t = unixtime / 86400 - 32872
    te = t + 1.1574e-5 * deltaT
    return t, te


def _grena_end(delta, H, lat, air_temperature, pressure):
    phi = lat
    sphi = np.sin(phi)
    cphi = np.sqrt(1 - sphi*sphi)
    sdel = np.sin(delta)
    cdel = np.sqrt(1 - sdel*sdel)
    sH = np.sin(H)
    cH = np.cos(H)

    se0 = sphi*sdel + cphi*cdel*cH
    ep = np.asin(se0) - 4.26e-5 * np.sqrt(1-se0*se0)

    gamma = np.atan2(sH, cH*sphi - sdel*cphi/cdel)
    gamma = gamma + np.pi  # not in the paper, but seems necessary to achieve into pvlib's convention
    gamma = gamma % (2 * np.pi)

    dele = 0.08422 * (pressure/101000) / (273 + air_temperature) / np.tan(ep + 0.003138 / (ep + 0.08919))
    # step 8 (modified)
    # Grena doesn't specify an exact lower limit for applying the refraction correction.
    # Per the paper: "this formula is meaningful only when ep + Δre is positive."
    # unfortunately, the formula for Δre has some nasty behavior near elevation=-5.11595116 degrees,
    # and ep + Δre can be positive even though clearly it shouldn't be.  So here we apply
    # the same refraction limit as in the NREL SPA function, using default values:
    e = np.where(ep > np.radians(-0.83337), ep + dele, ep)
    return e, ep, gamma


def _grena_out(apparent_elevation, true_elevation, azimuth, times):
    apparent_elevation = np.degrees(apparent_elevation)
    true_elevation = np.degrees(true_elevation)
    azimuth = np.degrees(azimuth)

    out = pd.DataFrame({
        "elevation": true_elevation,
        "apparent_elevation": apparent_elevation,
        "zenith": 90 - true_elevation,
        "apparent_zenith": 90 - apparent_elevation,
        "azimuth": azimuth,
    }, index=times)
    return out


def grena1(times, latitude, longitude, air_temperature=12, pressure=101325, deltaT=67.0):
    """
    Calculate solar position using Grena's algorithm 1.

    Grena's algorithm 1 [1]_ has a stated accuracy of 0.19 degrees
    from 2010–2110.

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
        negative to west. [degrees]
    delta_t : numeric, default : 67.0
        Difference between terrestrial time and UT1.
        If ``delta_t`` is None, uses :py:func:`pvlib.spa.calculate_deltat`
        using ``times.year`` and ``times.month`` from pandas.DatetimeIndex.
        For most simulations the default ``delta_t`` is sufficient.
        The USNO has historical and forecasted ``delta_t`` [3]_. [seconds]

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

    Notes
    -----
    This implementation follows the "computationally optimized" procedure
    given in [1]_.

    References
    ----------
    .. [1] R. Grena, "Five new algorithms for the computation of sun
           position from 2010 to 2110," Solar Energy, vol. 86, no. 5,
           pp. 1323–1337, May 2012, :doi:`10.1016/j.solener.2012.01.024` 
    """
    lat = np.radians(latitude)
    lon = np.radians(longitude)
    t, te = _grena_start_unixtime(times, deltaT)
    theta = lon

    w = 0.017202786
    s1 = np.sin(w * te)
    c1 = np.cos(w * te)

    s2 = 2*s1*c1
    c2 = (c1+s1) * (c1-s1)
    alpha = -1.38880 + 1.7202790e-2 * te + 3.199e-2*s1 - 2.65e-3*c1 + 4.050e-2*s2 + 1.525e-2*c2
    delta = 6.57e-3 + 7.347e-2*s1 - 3.9919e-1*c1 + 7.3e-4*s2 - 6.60e-3*c2
    H = 1.75283 + 6.3003881*t + theta - alpha
    
    apparent_elevation, true_elevation, azimuth = _grena_end(delta, H, lat, air_temperature, pressure)
    out = _grena_out(apparent_elevation, true_elevation, azimuth, times)
    return out


def grena2(times, latitude, longitude, air_temperature=12, pressure=101325, deltaT=67.0):
    """
    Calculate solar position using Grena's algorithm 2.

    Grena's algorithm 2 [1]_ has a stated accuracy of 0.034 degrees
    from 2010–2110.

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
        negative to west. [degrees]
    delta_t : numeric, default : 67.0
        Difference between terrestrial time and UT1.
        If ``delta_t`` is None, uses :py:func:`pvlib.spa.calculate_deltat`
        using ``times.year`` and ``times.month`` from pandas.DatetimeIndex.
        For most simulations the default ``delta_t`` is sufficient.
        The USNO has historical and forecasted ``delta_t`` [3]_. [seconds]

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

    Notes
    -----
    This implementation follows the "computationally optimized" procedure
    given in [1]_.

    References
    ----------
    .. [1] R. Grena, "Five new algorithms for the computation of sun
           position from 2010 to 2110," Solar Energy, vol. 86, no. 5,
           pp. 1323–1337, May 2012, :doi:`10.1016/j.solener.2012.01.024` 
    """
    lat = np.radians(latitude)
    lon = np.radians(longitude)
    t, te = _grena_start_unixtime(times, deltaT)
    theta = lon

    w = 0.017202786
    s1 = np.sin(w * te)
    c1 = np.cos(w * te)
    s2 = 2 * s1 * c1
    c2 = (c1 + s1) * (c1 - s1)
    s3 = s2 * c1 + c2 * s1
    c3 = c2 * c1 - s2 * s1
    s4 = 2 * s2 * c2
    c4 = (c2 + s2) * (c2 - s2)

    alpha = (
        -1.38880 + 1.7202790e-2 * te + 3.199e-2*s1 - 2.65e-3*c1
        + 4.050e-2*s2 + 1.525e-2*c2 + 1.33e-3*s3 + 3.8e-4*c3
        + 7.3e-4*s4 + 6.2e-4*c4
    )
    delta = (
        6.57e-3 + 7.347e-2*s1 - 3.9919e-1*c1 + 7.3e-4*s2
        - 6.60e-3*c2 + 1.50e-3*s3 - 2.58e-3*c3 + 6e-5*s4
        - 1.3e-4*c4
    )
    H = 1.75283 + 6.3003881*t + theta - alpha

    apparent_elevation, true_elevation, azimuth = _grena_end(delta, H, lat, air_temperature, pressure)
    out = _grena_out(apparent_elevation, true_elevation, azimuth, times)
    return out


def grena3(times, latitude, longitude, air_temperature=12, pressure=101325, deltaT=67.0):
    """
    Calculate solar position using Grena's algorithm 3.

    Grena's algorithm 3 [1]_ has a stated accuracy of 0.0094 degrees
    from 2010–2110.

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
        negative to west. [degrees]
    delta_t : numeric, default : 67.0
        Difference between terrestrial time and UT1.
        If ``delta_t`` is None, uses :py:func:`pvlib.spa.calculate_deltat`
        using ``times.year`` and ``times.month`` from pandas.DatetimeIndex.
        For most simulations the default ``delta_t`` is sufficient.
        The USNO has historical and forecasted ``delta_t`` [3]_. [seconds]

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

    Notes
    -----
    This implementation follows the "computationally optimized" procedure
    given in [1]_.

    References
    ----------
    .. [1] R. Grena, "Five new algorithms for the computation of sun
           position from 2010 to 2110," Solar Energy, vol. 86, no. 5,
           pp. 1323–1337, May 2012, :doi:`10.1016/j.solener.2012.01.024` 
    """
    lat = np.radians(latitude)
    lon = np.radians(longitude)
    t, te = _grena_start_unixtime(times, deltaT)
    theta = lon

    wa = 0.0172019715

    lam = (
        -1.388803 + 1.720279216e-2*te
        + 3.3366e-2 * np.sin(wa*te - 0.06172)
        + 3.53e-4 * np.sin(2*wa*te - 0.1163)
    )
    eps = 4.089567e-1 - 6.19e-9*te

    slam = np.sin(lam)
    clam = np.cos(lam)
    seps = np.sin(eps)
    ceps = np.sqrt(1-seps**2)
    alpha = np.arctan2(slam*ceps, clam)
    delta = np.arcsin(slam*seps)
    H = 1.7528311 + 6.300388099*t + theta - alpha

    apparent_elevation, true_elevation, azimuth = _grena_end(delta, H, lat, air_temperature, pressure)
    out = _grena_out(apparent_elevation, true_elevation, azimuth, times)
    return out


def grena4(times, latitude, longitude, air_temperature=12, pressure=101325, deltaT=67.0):
    """
    Calculate solar position using Grena's algorithm 4.

    Grena's algorithm 4 [1]_ has a stated accuracy of 0.0094 degrees
    from 2010–2110.

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
        negative to west. [degrees]
    delta_t : numeric, default : 67.0
        Difference between terrestrial time and UT1.
        If ``delta_t`` is None, uses :py:func:`pvlib.spa.calculate_deltat`
        using ``times.year`` and ``times.month`` from pandas.DatetimeIndex.
        For most simulations the default ``delta_t`` is sufficient.
        The USNO has historical and forecasted ``delta_t`` [3]_. [seconds]

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

    Notes
    -----
    This implementation follows the "computationally optimized" procedure
    given in [1]_.

    References
    ----------
    .. [1] R. Grena, "Five new algorithms for the computation of sun
           position from 2010 to 2110," Solar Energy, vol. 86, no. 5,
           pp. 1323–1337, May 2012, :doi:`10.1016/j.solener.2012.01.024` 
    """
    lat = np.radians(latitude)
    lon = np.radians(longitude)
    t, te = _grena_start_unixtime(times, deltaT)
    theta = lon

    L = (
        1.752790 + 1.720279216e-2*te
        + 3.3366e-2 * np.sin(wa*te - 0.06172)
        + 3.53e-4 * np.sin(2*wa*te - 0.1163)
    )
    v = wn * te - 0.8
    dlam = 8.34e-5 * np.sin(v)
    lam = L + np.pi + dlam
    eps = 4.089567e-1 - 6.19e-9*te + 4.46e-5*np.cos(v)

    slam = np.sin(lam)
    clam = np.cos(lam)
    seps = np.sin(eps)
    ceps = np.sqrt(1-seps**2)
    alpha = np.arctan2(slam*ceps, clam)
    delta = np.arcsin(slam*seps)
    H = 1.7528311 + 6.300388099*t + theta - alpha + 0.92*dlam

    apparent_elevation, true_elevation, azimuth = _grena_end(delta, H, lat, air_temperature, pressure)
    out = _grena_out(apparent_elevation, true_elevation, azimuth, times)
    return out


L0 = 1.7527901
L1 = 1.7202792159e-2

wa = 0.0172019715

a1 = 3.33024e-2
a2 = 3.512e-4
a3 = 5.2e-6

b1 = -2.0582e-3
b2 = -4.07e-5
b3 = -9e-7

beta = 2.92e-5
dbeta = -8.23e-5

w = np.array([1.49e-3, 4.31e-3, 1.076e-2, 1.575e-2, 2.152e-2, 3.152e-2, 2.1277e-1])[np.newaxis, :]
d = np.array([1.27e-5, 1.21e-5, 2.33e-5, 3.49e-5, 2.67e-5, 1.28e-5, 3.14e-5])[np.newaxis, :]
phi = np.array([-2.337, 3.065, -1.533, -2.358, 0.074, 1.547, -0.488])[np.newaxis, :]

wn = 9.282e-4  # given in the text, last sentence on page 1331

def grena5(times, latitude, longitude, air_temperature=12, pressure=101325, deltaT=67.0):
    """
    Calculate solar position using Grena's algorithm 5.

    Grena's algorithm 5 [1]_ has a stated accuracy of 0.0027 degrees
    from 2010–2110.

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
        negative to west. [degrees]
    delta_t : numeric, default : 67.0
        Difference between terrestrial time and UT1.
        If ``delta_t`` is None, uses :py:func:`pvlib.spa.calculate_deltat`
        using ``times.year`` and ``times.month`` from pandas.DatetimeIndex.
        For most simulations the default ``delta_t`` is sufficient.
        The USNO has historical and forecasted ``delta_t`` [3]_. [seconds]

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

    Notes
    -----
    This implementation follows the "computationally optimized" procedure
    given in [1]_.

    References
    ----------
    .. [1] R. Grena, "Five new algorithms for the computation of sun
           position from 2010 to 2110," Solar Energy, vol. 86, no. 5,
           pp. 1323–1337, May 2012, :doi:`10.1016/j.solener.2012.01.024` 
    """
    lat = np.radians(latitude)
    lon = np.radians(longitude)
    t, te = _grena_start_unixtime(times, deltaT)
    theta = lon

    s1 = np.sin(wa * te)
    c1 = np.cos(wa * te)
    s2 = 2 * s1 * c1
    c2 = (c1+s1) * (c1-s1)
    s3 = s2*c1 + c2*s1
    c3 = c2*c1 - s2*s1

    L = (
        L0 + L1*te +
        (a1*s1 + a2*s2 + a3*s3 + b1*c1 + b2*c2 + b3*c3) +
        dbeta * s1 * np.sin(beta*te) +
        np.sum(d * np.sin(w*te[:, np.newaxis] + phi), axis=1)
    )

    v = wn * te - 0.8
    delta_lam = 8.34e-5 * np.sin(v)
    lam = L + np.pi + delta_lam
    eps = 4.089567e-1 - 6.19e-9*te + 4.46e-5*np.cos(v)

    slam = np.sin(lam)
    clam = np.cos(lam)
    seps = np.sin(eps)
    ceps = np.sqrt(1 - seps*seps)
    alpha = np.atan2(slam*ceps, clam)

    # step 12 (don't need it)
    # alpha = np.where(alpha < 0, alpha + 2 * np.pi, alpha)

    delta = np.asin(slam * seps)
    H = 1.7528311 + 6.300388099*t + theta - alpha + 0.92*delta_lam

    # step 15 (don't need it)
    # H = (H + np.pi) % (2 * np.pi) - np.pi

    apparent_elevation, true_elevation, azimuth = _grena_end(delta, H, lat, air_temperature, pressure)
    out = _grena_out(apparent_elevation, true_elevation, azimuth, times)
    return out
