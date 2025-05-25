# import pandas as pd
import numpy as np
import pytest
from solposx.refraction import hughes


@pytest.fixture
def elevation_angles():
    return np.array([0, 10, 86])


def test_hughes_refraction(elevation_angles):
    expected = np.array([0.47856238, 0.08750312, 0.])
    result = hughes(elevation_angles)
    np.testing.assert_allclose(result, expected)
