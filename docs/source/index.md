# solposx

**Sol**ar**Pos**ition**X** (`solposx`) is a Python package for determining solar position and atmospheric refraction. The package contains reference implementations of common solar position algorithms used for solar energy applications. Additionally, the package also features several algorithms for approximating atmospheric refraction in order to calculate the apparent position of the sun.

The functions currently support calculating time series of solar position and atmospheric refraction for a single-point of interst. The functions are implemented following as close as possible to the original paper, allowing for a baseline comparison of computational speed across algorithms. Speed improvements can be achieved for most if not all algorithms by refactoring the code and or/using specialized pacakges.

If you are new to this package, check out the introduction to [solar position algorithms](solarposition_introduction) and [refraction models](refraction_introduction). Alternatively, you may wish to dive straight into the [documentation](documentation), check out how to [install the solposx package](installation), or get updated on [recent developments](whatsnew).


## Contributing
Contributions to the repository, e.g., bug fixes, feature requests, are more than welcome! The package is openly developed on [GitHub](https://github.com/AssessingSolar/solposx).


## License
[BSD 3-clause](https://github.com/assessingsolar/solposx/blob/main/LICENSE).


```{toctree}
:maxdepth: 1
:hidden:

solarposition_introduction
refraction_introduction
installation
documentation
whatsnew
```
