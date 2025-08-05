---
title: 'solposx: A Python package determining the solar position for solar energy applications'
tags:
 - Python
 - solar energy
 - photovoltaics
 - solar position
authors:
  - name: Adam R Jensen
    corresponding: true
    orcid: 0000-0002-5554-9856
    equal-contrib: true
    affiliation: 1
  - name: Ioannis Sifnaios
    orcid: 0000-0003-0933-2952
    equal-contrib: true
    affiliation: 1
  - name: Kevin S. Anderson
    orcid: 0000-0002-1166-7957
    equal-contrib: true
    affiliation: 2
affiliations:
- name: Technical University of Denmark (DTU), Denmark
  index: 1
  ror: 04qtj9h94
- name: Sandia National Laboratories, USA
  index: 2
  ror: 01apwpt12
date: 13 August 2025
bibliography: paper.bib
---

# Summary
**Sol**ar**Pos**ition**X** (solposx) is a Python package for calculating the sun’s position and atmospheric refraction. It includes 11 solar position algorithms and 6 refraction models from the past 50 years. All functions come with a consistent and easy-to-use interface. Designed for comparison, validation, and implementation in other tools or languages, solposx offers reliable reference code, follows modern development practices, and is fully open-source.


# Statement of need

Calculating the sun's position is a fundamental task in solar energy research, for example, when modeling solar irradiance, estimating the yield of photovoltaic (PV) systems, or determining rotation angles for solar trackers. For this reason, the literature contains numerous solar position algorithms (SPAs), some of which are: `[@spencer1971fourier; @walraven1978calculating; @michalsky1988astronomical, @reda2004spa, @blanco2020updating]`.

Existing SPAs vary in (1) accuracy, (2) computational speed, and (3) period of validity. These characteristics are usually tradeoffs, and thus the choice of algorithm depends on the application. Some algorithms have been developed to be computationally lightweight for use in solar tracker microcontrollers, and as a tradeoff, are inaccurate for past and future years. In contrast, high-accuracy algorithms may consist of several hundred mathematical operations to retain validity for hundreds or even thousands of years. One example of such an algorithm is the SPA from NREL, whose high accuracy and extensive period of validity come at the cost of being computationally expensive and impractical for non-experts to implement.

Solar position algorithms are already available in several open source software packages, such as the PV modeling software packages pvlib [@pvlib] and pysolar [@pysolar], the astronomy packages pyephem [@pyephem] and skyfield [@skyfield], and the sun physics package sunpy [@sunpy]. However, these packages are tailored to very specific purposes and only contain one or a few solar position algorithms. Consequently, there are many solar position algorithms for which open source reference implementations are not available. This makes it difficult to evaluate the tradeoffs of the various solar position algorithms, which is necessary in order to make informed decisions on which algorithm to choose for a specific application.

SolarPositionX (the X is for eXtreme awesomeness) is a Python package for calculating solar position angles and atmospheric refraction corrections. The package provides reference implementations of a large number of solar position and refraction correction algorithms spanning 50 years of the scientific literature. The SPAs range from simple algorithms based on fitted equations to research-grade astronomy algorithms based on complex ephemerides. As of solposx version v1.0.0, the package includes 11 different solar position algorithms and 6 algorithms for estimating atmospheric refraction. An overview of the modules and functions is provided in \autoref{fig:package}.


The solar position functions follow a standard pattern, taking three main input parameters (times, latitude, and longitude) and returning a pandas DataFrame with solar elevation, zenith, and azimuth angles. This makes it extremely easy to compare and switch between SPAs, regardless of whether the functions execute code from within the solposx package or rely on external Python packages (which is the case for the skyfield and sg2 functions). The refraction correction models also follow a standardized pattern where the main input is an array or series of solar elevation angles and the output is the atmospheric refraction correction angle.

![Overview of modules and functions in the solposx package.\label{fig:package}](solposx_package_structure.png)

The package relies heavily on the pandas Python package [@pandas], due to its convenient DatetimeIndex class. The reason for this choice is that it offers a very convenient way to handle timestamps, including timezone information and conversion between different timezones. The refraction correction algorithms are not reliant on pandas but can be used with most Python array libraries.

Besides direct applications involving calculating solar positions, one of the main use cases of the package is providing verified reference implementations to users who are implementing algorithms in other languages. Having access to verified reference implementations is an essential tool as solar position algorithms tend to be sensitive to small implementation details. For example, using an incorrect rounding convention, e.g., rounding towards zero vs. rounding down, can result in solar position angles being off by more than 0.1 degrees, an error much larger than the claimed accuracy of most SPAs. Such subtle but serious implementation errors are, in the authors’ experience, almost inevitable when implementing SPAs, creating a need for correct and accessible reference implementations. With access to vetted and tested reference implementations of these SPAs, users can generate reliable test values for validating and debugging their own implementations. Notably, the solposx package has already been used for research purposes, most recently in a study comparing the performance of solar position algorithms for PV applications [@pvpmc].

solposx is developed openly on GitHub and released under a BSD 3-clause license, allowing permissive use with attribution. The package is extensively tested, ensuring that the algorithms work for a large range of inputs and remain consistent. In general, solposx has been developed following modern best practices for packaging, documentation, and testing. Additional algorithms are expected to be added as new algorithms are developed or if additional historical algorithms of interest are identified.


# References