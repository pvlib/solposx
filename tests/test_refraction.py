import pandas as pd
import numpy as np
import pytest
from solposx.refraction import archer
from solposx.refraction import bennett
from solposx.refraction import hughes
from solposx.refraction import michalsky
from solposx.refraction import sg2
from solposx.refraction import spa


@pytest.fixture
def test_elevation_angles():
    # unit: degrees
    return np.array([-1, -0.6, 0, 1, 4, 6, 10, 90])


def expected_archer():
    # unit: degrees
    return np.array([
        0.76852998, 0.61784902, 0.47556015, 0.34104051, 0.17880831,
        0.13306518, 0.08518174, -0.00218662])


def expected_bennett():
    # unit: degrees
    return np.array([
        0.826520608, 0.718039255, 0.572036066, 0.403658095,
        0.194720611, 0.141175878, 0.089453486, -0.000022424])


def expected_hughes():
    # unit: degrees
    return np.array([
        0.32827494, 0.54716046, 0.47856238, 0.360817, 0.1875788,
        0.13769375, 0.08750312, 0.00000000])


def expected_michalsky():
    # unit: degrees
    return np.array([
        0.5600000, 0.560000000, 0.56038823, 0.39595124, 0.19147691,
        0.13805928, 0.08665373, 0.01003072])


def expected_sg2():
    # unit: degrees
    return np.array([
        0.328796332, 0.548029502, 0.481177890, 0.361009325,
        0.188613883, 0.139390534, 0.089783442, -0.000032010])


def expected_spa():
    # unit: degrees
    return np.array([
        0.00000000, 0.5760885771, 0.481185828, 0.361012918,
        0.188614492, 0.139390797, 0.0897835168, -0.000032010])


@pytest.mark.parametrize('algorithm,expected,kwargs', [
    (archer, expected_archer, {}),
    (bennett, expected_bennett, {}),
    (bennett, expected_bennett, {'pressure': 101325., 'temperature': 12.}),
    (hughes, expected_hughes, {}),
    (hughes, expected_hughes, {'pressure': 101325., 'temperature': 12.}),
    (michalsky, expected_michalsky, {}),
    (sg2, expected_sg2, {}),
    (sg2, expected_sg2, {'pressure': 101325., 'temperature': 12.}),
    (spa, expected_spa, {}),
    (spa, expected_spa, {'pressure': 101325., 'temperature': 12.}),
])
def test_algorithm(algorithm, expected, kwargs, test_elevation_angles):
    # numpy array input
    result = algorithm(elevation=test_elevation_angles, **kwargs)
    np.testing.assert_almost_equal(expected(), result)

    # pandas series input
    series_index = pd.date_range('2020-01-01', periods=len(test_elevation_angles), freq='1h')
    test_elevation_angles_series = pd.Series(test_elevation_angles, index=series_index)
    expected_series = pd.Series(expected(), index=series_index)
    result_series = algorithm(elevation=test_elevation_angles_series, **kwargs)
    pd.testing.assert_series_equal(expected_series, result_series)


def test_spa_refraction_limit():
    assert spa(elevation=-2, refraction_limit=-1) == 0
    assert spa(elevation=-2, refraction_limit=-3) != 0
    assert spa(elevation=-2, refraction_limit=-2) != 0
    assert spa(elevation=-0.26667, refraction_limit=0) != 0
    assert spa(elevation=-0.26668, refraction_limit=0) != 1
