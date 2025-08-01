
from skyfield.api import load, wgs84
import pandas as pd

DE440 = load('de440.bsp')
TS = load.timescale()


def skyfield(times, latitude, longitude, de=DE440):

    earth = de['Earth']
    sun = de['Sun']

    dts = TS.from_datetimes(times.to_pydatetime())
    location = earth + wgs84.latlon(latitude, longitude)
    alt, az, _ = location.at(dts).observe(sun).apparent().altaz()

    result = pd.DataFrame({
        'elevation': alt.degrees,
        'azimuth': az.degrees,
    }, index=times)

    return result
