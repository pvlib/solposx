.. currentmodule:: solposx


Refraction correction algorithms
================================

Methods for calculating the effect of atmospheric refraction on solar elevation.
Some methods account for secondary effects from temperature and pressure.

The following refraction correction algorithms estimate refraction from the
true solar (unrefracted) elevation angle:

.. autosummary::
   :toctree: generated/

   refraction.archer
   refraction.hughes
   refraction.michalsky
   refraction.sg2
   refraction.spa

The following refraction correction algorithm calculates refraction from the
apparent (refracted) solar elevation:

.. autosummary::
   :toctree: generated/

   refraction.bennett
