"""SPA NREL implementation in Python, wraps pvlib."""

import pvlib


def spa(time, latitude, longitude, elevation=0., *, air_pressure=101325.,
        temperature=12., delta_t=67.0, atmos_refract=None, **kwargs):
    """
    Calculate the solar position using a python implementation of the NREL SPA algorithm.

    The details of the NREL SPA algorithm are described in [1]_, [2]_.

    If numba is installed, the functions can be compiled to
    machine code and the function can be multithreaded.
    Without numba, the function evaluates via numpy with
    a slight performance hit.

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
    elevation : float, default : 0
        Altitude of the location of interest. [m]
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
    atmos_refract : float, optional
        The approximate atmospheric refraction (in degrees)
        at sunrise and sunset.

    Extra Parameters
    ----------------
    how : str, optional, default 'numpy'
        Options are 'numpy' or 'numba'. If numba >= 0.17.0
        is installed, how='numba' will compile the spa functions
        to machine code and run them multithreaded.
    numthreads : int, optional, default 4
        Number of threads to use if how == 'numba'.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the following columns (all values in degrees):

        - elevation : actual sun elevation (not accounting for refraction). [°]
        - apparent_elevation : sun elevation, accounting for
          atmospheric refraction. [°]
        - zenith : actual sun zenith (not accounting for refraction). [°]
        - apparent_zenith : sun zenith, accounting for atmospheric
          refraction. [°]
        - azimuth : sun azimuth, east of north. [°]
        - equation_of_time. [minutes]

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
    """  # slightly modified docstring compared to pvlib original
    # if you want to view the source code for pvlib.solarposition.spa_python, it is
    # located in pvlib/solarposition.py and belongs to the repo pvlib/pvlib-python
    solpos = pvlib.solarposition.spa_python(
        time=time,
        latitude=latitude,
        longitude=longitude,
        altitude=elevation,
        pressure=air_pressure,
        temperature=temperature,
        delta_t=delta_t,
        atmos_refract=atmos_refract,
        **kwargs,
    )

    reordered_columns = [
        'elevation', 'apparent_elevation', 'zenith', 'apparent_zenith',
        'azimuth', 'equation_of_time']

    solpos = solpos[reordered_columns]

    return solpos
