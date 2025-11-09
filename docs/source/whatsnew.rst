Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

1.0.1 - 2025-11-09
-------------------

Changed
^^^^^^^
* Moved the package GitHub repository from the GitHub organization AssessingSolar
  to the pvlib organization. (:pull:`134`)
* Improved error messages raised when optional packages are not available.
  (:issue:`86`, :pull:`122`)

Added
^^^^^
* Added optional ``refraction_correction`` parameter to
  :py:func:`solposx.solarposition.nasa_horizons`. (:issue:`83`, :pull:`133`)

1.0.0 - 2025-09-22
-------------------
First stable release.
