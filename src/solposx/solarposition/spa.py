import pandas as pd
import numpy as np
from pvlib import tools

from importlib import reload
import warnings
import os

def _spa_python_import(how):
    """Compile spa.py appropriately"""

    from pvlib import spa

    # check to see if the spa module was compiled with numba
    using_numba = spa.USE_NUMBA

    if how == 'numpy' and using_numba:
        # the spa module was compiled to numba code, so we need to
        # reload the module without compiling
        # the PVLIB_USE_NUMBA env variable is used to tell the module
        # to not compile with numba
        warnings.warn('Reloading spa to use numpy')
        os.environ['PVLIB_USE_NUMBA'] = '0'
        spa = reload(spa)
        del os.environ['PVLIB_USE_NUMBA']
    elif how == 'numba' and not using_numba:
        # The spa module was not compiled to numba code, so set
        # PVLIB_USE_NUMBA so it does compile to numba on reload.
        warnings.warn('Reloading spa to use numba')
        os.environ['PVLIB_USE_NUMBA'] = '1'
        spa = reload(spa)
        del os.environ['PVLIB_USE_NUMBA']
    elif how != 'numba' and how != 'numpy':
        raise ValueError("how must be either 'numba' or 'numpy'")

    return spa


def _datetime_to_unixtime(dtindex):
    # convert a pandas datetime index to unixtime, making sure to handle
    # different pandas units (ns, us, etc) and time zones correctly
    if dtindex.tz is not None:
        # epoch is 1970-01-01 00:00 UTC, but we need to match the input tz
        # for compatibility with older pandas versions (e.g. v1.3.5)
        epoch = pd.Timestamp("1970-01-01", tz="UTC").tz_convert(dtindex.tz)
    else:
        epoch = pd.Timestamp("1970-01-01")

    return np.array((dtindex - epoch) / pd.Timedelta("1s"))

def spa(time, latitude, longitude,
               altitude=0., pressure=101325., temperature=12., delta_t=67.0,
               atmos_refract=None, how='numpy', numthreads=4):
    """
    Calculate the solar position using a python implementation of the
    NREL SPA algorithm.

    The details of the NREL SPA algorithm are described in [1]_, [2]_.

    If numba is installed, the functions can be compiled to
    machine code and the function can be multithreaded.
    Without numba, the function evaluates via numpy with
    a slight performance hit.

    Parameters
    ----------
    time : pandas.DatetimeIndex
        Must be localized or UTC will be assumed.
    latitude : float
        Latitude in decimal degrees. Positive north of equator, negative
        to south.
    longitude : float
        Longitude in decimal degrees. Positive east of prime meridian,
        negative to west.
    altitude : float, default 0.0
        Distance above sea level.
    pressure : int or float, optional, default 101325.0
        avg. yearly air pressure in Pascals.
    temperature : int or float, optional, default 12.0
        avg. yearly air temperature in degrees C.
    delta_t : float or array, optional, default 67.0
        Difference between terrestrial time and UT1.
        If delta_t is None, uses spa.calculate_deltat
        using time.year and time.month from pandas.DatetimeIndex.
        For most simulations the default delta_t is sufficient.
        The USNO has historical and forecasted delta_t [3]_.
    atmos_refrac : float, optional
        The approximate atmospheric refraction (in degrees)
        at sunrise and sunset.
    how : str, optional, default 'numpy'
        Options are 'numpy' or 'numba'. If numba >= 0.17.0
        is installed, how='numba' will compile the spa functions
        to machine code and run them multithreaded.
    numthreads : int, optional, default 4
        Number of threads to use if how == 'numba'.

    Returns
    -------
    DataFrame
        The DataFrame will have the following columns:

        - apparent_zenith (degrees),
        - zenith (degrees),
        - apparent_elevation (degrees),
        - elevation (degrees),
        - azimuth (degrees),
        - equation_of_time (minutes).

    References
    ----------
    .. [1] I. Reda and A. Andreas, Solar position algorithm for solar
       radiation applications. Solar Energy, vol. 76, no. 5, pp. 577-589, 2004.
       :doi:`10.1016/j.solener.2003.12.003`.

    .. [2] I. Reda and A. Andreas, Corrigendum to Solar position algorithm for
       solar radiation applications. Solar Energy, vol. 81, no. 6, p. 838,
       2007. :doi:`10.1016/j.solener.2007.01.003`.

    .. [3] `U.S. Naval Observatory, delta T
       <https://maia.usno.navy.mil/products/deltaT>`_

    See also
    --------
    pyephem, spa_c, ephemeris
    """

    # Added by Tony Lorenzo (@alorenzo175), University of Arizona, 2015

    lat = latitude
    lon = longitude
    elev = altitude
    pressure = pressure / 100  # pressure must be in millibars for calculation

    atmos_refract = atmos_refract or 0.5667

    if not isinstance(time, pd.DatetimeIndex):
        try:
            time = pd.DatetimeIndex(time)
        except (TypeError, ValueError):
            time = pd.DatetimeIndex([time, ])

    unixtime = _datetime_to_unixtime(time)

    spa = _spa_python_import(how)

    if delta_t is None:
        time_utc = tools._pandas_to_utc(time)
        delta_t = spa.calculate_deltat(time_utc.year, time_utc.month)

    app_zenith, zenith, app_elevation, elevation, azimuth, eot = \
        spa.solar_position(unixtime, lat, lon, elev, pressure, temperature,
                           delta_t, atmos_refract, numthreads)

    result = pd.DataFrame({'apparent_zenith': app_zenith, 'zenith': zenith,
                           'apparent_elevation': app_elevation,
                           'elevation': elevation, 'azimuth': azimuth,
                           'equation_of_time': eot},
                          index=time)

    return result
