import numpy as np

def R1(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    O = np.ones_like(theta)
    Z = np.zeros_like(theta)

    out = np.array([
        [O, Z, Z],
        [Z, c, s],
        [Z, -s, c],
    ])
    if not np.isscalar(theta):
        out = out.transpose((2, 0, 1))
    return out

def R2(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    O = np.ones_like(theta)
    Z = np.zeros_like(theta)

    out = np.array([
        [c, Z, -s],
        [Z, O, Z],
        [s, Z, c],
    ])
    if not np.isscalar(theta):
        out = out.transpose((2, 0, 1))
    return out

def R3(theta):
    c = np.cos(theta)
    s = np.sin(theta)
    O = np.ones_like(theta)
    Z = np.zeros_like(theta)

    out = np.array([
        [c, s, Z],
        [-s, c, Z],
        [Z, Z, O],
    ])
    if not np.isscalar(theta):
        out = out.transpose((2, 0, 1))
    return out

J = np.array([
    [0, 0, 1],
    [0, 1, 0],
    [1, 0, 0],
])


def fr(a, b):
    cos_b = np.cos(b)
    return np.array([
        np.cos(a) * cos_b,
        np.sin(a) * cos_b,
        np.sin(b)
    ]).T

def gs(v):
    vx, vy, vz = v[:, 0], v[:, 1], v[:, 2]
    a = np.arctan2(vy, vx)
    b = np.arctan2(vz, np.sqrt(vx*vx + vy*vy))
    return a, b

def to_equatorial(lambda_s, beta_s, epsilon, delta_psi):
    """
    Section 3.2 of Hoadley 2021.

    Parameters
    ----------
    lambda_s : Ecliptic longitude of the sun
    beta_s : Ecliptic latitude of the sun
    epsilon : Obliquity of the ecliptic
    delta_psi : Nutation in longitude

    Returns
    -------
    qhat : Geocentric direction, in equatorial coordinates
    Eq : equation of the equinoxes
    """

    # unit vector of the ecliptic coordinates
    phat = fr(lambda_s, beta_s)

    # convert ecliptic coordinates to equatorial coordinates
    qhat = np.matvec(R1(-epsilon), phat)

    # Equation of the equinoxes
    Eq = delta_psi * np.cos(epsilon)

    # right ascension and declination
    # (not required)
    # alpha, delta = gs(qhat)

    return qhat, Eq

def to_terrestrial(gmst, Eq, qhat):
    """
    Section 3.3 of Hoadley 2021.

    Parameters
    ----------
    gmst : Greenwich Mean Sidereal Time
    Eq : Equation of the equinoxes
    qhat : equatorial position vector

    Returns
    -------
    r : Geocentric direction, in terrestrial
        intermediate coordinates
    """
    gast = gmst + Eq
    r = np.matvec(R3(gast), qhat)
    return r

def to_topocentric(r, R, latitude, longitude, altitude):
    """
    Section 3.4 of Hoadley 2021.

    Parameters
    ----------
    r : geocentric position vector
    R : sun-earth distance
    latitude : latitude
    longitude : longitude
    altitude : height above reference ellipsoid [m]
               (approximately, height above mean sea level)

    Returns
    -------
    s : Topocentric direction, in horizon coordinates
    """
    # Table 5 constants
    ae = 6378.137  # Equatorial radius of Earth [km]
    f = 1/298.257223563  # Flattening factor of Earth [-]
    Ua = 149597871.464  # 1 Astronomical unit [km]
    c0 = 299792.458  # speed of light [km/s]
    ws = 7.292115e-5  # rotational speed of Earth [rad/s]

    # Section 5.1
    L = J @ R2(-latitude) @ R3(longitude)

    # Section 5.2
    sin_phi = np.sin(latitude)
    cos_phi = np.cos(latitude)
    h = altitude

    C = 1 / np.sqrt(cos_phi**2 + (1 - f)**2 * sin_phi**2)
    dx = (ae * C * (2*f - f**2) * sin_phi * cos_phi) / Ua
    dz = -(ae/C + h/1000) / Ua
    #dy = (ae * C + h/1000) * (ws/c0) * cos_phi
    dy = 0

    s = np.matvec(L, r) + np.array([dx / R, np.full_like(R, dy), dz / R]).T
    return s

def to_altaz(s):
    """
    Section 3.5 of Hoadley 2021.

    Parameters
    ----------
    s : Topocentric position vector

    Returns
    -------
    azimuth, elevation : topocentric angles [rad]
    """
    A, e0 = gs(s)
    return A, e0


def hoadley(lambda_s, beta_s, epsilon, delta_psi, gmst, R, lat, lon, altitude):
    """
    Compute solar position using rectangular coordinates
    following Hoadley 2021.

    All angular inputs in radians.

    Parameters
    ----------
    lambda_s : Ecliptic longitude of the sun
    beta_s : Ecliptic latitude of the sun
    epsilon : Obliquity of the ecliptic
    delta_psi : Nutation in longitude
    gmst : Greenwich Mean Sidereal Time
    R : sun-earth distance
    lat : latitude
    lon : longitude
    altitude : altitude

    Returns
    -------
    azimuth, elevation

    References
    ----------
    .. [1] D. Hoadley, "Efficient calculation of solar
       position using rectangular coordinates," Solar Energy,
       vol. 220, pp. 80–87, May 2021,
       :doi:`10.1016/j.solener.2021.02.019`.
    """
    qhat, Eq = to_equatorial(lambda_s, beta_s, epsilon, delta_psi)
    r = to_terrestrial(gmst, Eq, qhat)
    s = to_topocentric(r, R, np.radians(lat), np.radians(lon), altitude)
    az, el = to_altaz(s)

    return {
        "azimuth": np.degrees(az) % 360,
        "elevation": np.degrees(el),
    }
