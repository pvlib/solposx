import numpy as np
import pandas as pd

from pvlib.solarposition import _datetime_to_unixtime

_PSA_PARAMS = {
    2020: [
        2.267127827, -9.300339267e-4, 4.895036035, 1.720279602e-2,
        6.239468336, 1.720200135e-2, 3.338320972e-2, 3.497596876e-4,
        -1.544353226e-4, -8.689729360e-6, 4.090904909e-1, -6.213605399e-9,
        4.418094944e-5, 6.697096103, 6.570984737e-2,
    ],
    2001: [
        2.1429, -0.0010394594, 4.8950630, 0.017202791698, 6.2400600,
        0.0172019699, 0.03341607, 0.00034894, -0.0001134, -0.0000203,
        0.4090928, -6.2140e-09, 0.0000396, 6.6974243242, 0.0657098283,
    ]
}

def psa(times, latitude, longitude, coefficients=2020):
    """
    Calculate solar position using the algorithm developed at the
    Plataforma Solar de Almería (PSA).

    This algorithm can use two sets of coefficients: TODO
    2001 - tuned to the range XX, with accuracy YY
    2020 - tuned to the range XX, with accuracy YY

    Parameters
    ----------
    times : pandas.DatetimeIndex
        Must be localized or UTC will be assumed.
    latitude : float
        Latitude in decimal degrees. Positive north of equator, negative
        to south.
    longitude : float
        Longitude in decimal degrees. Positive east of prime meridian,
        negative to west.
    coefficients : TYPE, optional
        DESCRIPTION. The default is 2020.

    Raises
    ------
    ValueError
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    References
    ----------
    .. [1] Blanco, M., Alarcón, D., López, T., Lara, M. "Computing the Solar
       Vector" Solar Energy Vol. 70, No. 5, 2001.
       :doi:`10.1016/S0038-092X(00)00156-0`
    .. [2] Blanco, M., Milidonis, K., Bonanos A., "Updating the PSA sun
       position algorithm." Solar Energy, Vol. 212, 2020.
       :doi:`10.1016/j.solener.2020.10.084`
    """

    if isinstance(coefficients, int):
        try:
            p = _PSA_PARAMS[coefficients]
        except KeyError:
            raise ValueError(f"unknown coefficients set: {coefficients}")
    else:
        p = coefficients

    phi = np.radians(latitude)
    lambda_t = longitude

    # The julian day calculation in the reference is awkward, as it relies
    # on C-style integer division (round toward zero) and thus requires
    # tedious floating point divisions with manual integer casts to work
    # around python's integer division (round down).  It is also slow.
    # Faster and simpler to calculate the "elapsed julian day" number
    # via unixtime:
    unixtime = _datetime_to_unixtime(times)
    # unix time is the number of seconds since 1970-01-01, but PSA needs the
    # number of days since 2000-01-01 12:00.  The difference is 10957.5 days.
    n = unixtime / 86400 - 10957.5
    h = ((unixtime / 86400) % 1)*24

    # ecliptic longitude (lambda_e) and obliquity (epsilon):
    omega = p[0] + p[1] * n  # Eq 3
    L = p[2] + p[3] * n  # Eq 4
    g = p[4] + p[5] * n  # Eq 5
    lambda_e = (
        L
        + p[6] * np.sin(g)
        + p[7] * np.sin(2*g)
        + p[8]
        + p[9] * np.sin(omega)
    )  # Eq 6
    epsilon = p[10] + p[11] * n + p[12] * np.cos(omega)  # Eq 7

    # celestial right ascension (ra) and declination (d):
    ra = np.arctan2(np.cos(epsilon) * np.sin(lambda_e), np.cos(lambda_e))  # Eq 8
    ra = ra % (2 * np.pi)
    d = np.arcsin(np.sin(epsilon) * np.sin(lambda_e))  # Eq 9

    # local coordinates:
    gmst = p[13] + p[14] * n + h  # Eq 10
    lmst = (gmst * 15 + lambda_t) * np.pi/180  # Eq 11
    w = lmst - ra  # Eq 12
    theta_z = np.arccos(np.cos(phi) * np.cos(w) * np.cos(d) + np.sin(d) * np.sin(phi))  # Eq 13
    gamma = np.arctan2(-np.sin(w), (np.tan(d) * np.cos(phi) - np.sin(phi) * np.cos(w)))  # Eq 14

    EMR = 6371.01  # Earth Mean Radius in km
    AU = 149597890  # Astronomical Unit in km
    theta_z = theta_z + (EMR / AU) * np.sin(theta_z)  # Eq 15,16

    result = pd.DataFrame({
        'elevation': 90 - np.degrees(theta_z),
        'zenith': np.degrees(theta_z),
        'azimuth': np.degrees(gamma) % 360,
    }, index=times)

    return result
