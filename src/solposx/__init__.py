from importlib.metadata import PackageNotFoundError, version

try:  # pragma: no cover
    __version__ = version(__package__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0+unknown"

# Make the modules directly available to the package
from solposx import (  # noqa: F401
    solarposition,
    refraction,
    tools,
)
