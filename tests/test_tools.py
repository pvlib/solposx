import pandas as pd
import numpy as np
import pytest
from solposx.tools import _pandas_to_utc, _fractional_hour, calc_error


@pytest.fixture
def times_index():
    return pd.date_range('2020-01-01', freq='1h', periods=10, tz=-60*60)


@pytest.fixture
def times_index_utc():
    return pd.date_range('2020-01-01 01', freq='1h', periods=10, tz='UTC')


def test_pandas_to_utc(times_index, times_index_utc):
    result = _pandas_to_utc(times_index)
    pd.testing.assert_index_equal(result, times_index_utc)


def test_pandas_to_utc_missing_tz():
    with pytest.raises(TypeError, match='stamps are timezone naive.'):
        _pandas_to_utc(pd.date_range('2020-01-01', '2020-01-02'))


@pytest.fixture
def expected_fractional_hour():
    return pd.Index([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])


def test_fractional_hour(times_index, expected_fractional_hour):
    result = _fractional_hour(times_index)
    pd.testing.assert_index_equal(result, expected_fractional_hour)


@pytest.fixture
def expected_calc_error():
    N = 10
    out = {
        'zenith_bias': np.zeros(N),
        'zenith_rmsd': np.zeros(N),
        'azimuth_bias': np.zeros(N),
        'azimuth_rmsd': np.zeros(N),
        'combined_rmsd': np.zeros(N),
    }
    return out


def test_calc_error(expected_calc_error):
    zeros = np.zeros(10)
    result = calc_error(zeros, zeros, zeros, zeros)
    for k in expected_calc_error.keys():
        np.testing.assert_equal(result[k], expected_calc_error[k])
