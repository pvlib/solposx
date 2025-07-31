# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------

project = 'solposx'
copyright = '2025 Adam R. Jensen'
author = 'Adam R. Jensen, Kevin S. Anderson, & Ioannis Sifnaios'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_nb',  # markdown and jupyter-notebook parsing
    'sphinx.ext.autodoc',  # generate documentation from docstrings
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',  # parsing of Numpy docstrings
    'sphinx.ext.extlinks',
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = "sphinx_book_theme"
html_title = "solposx"
# html_logo = "_static/solposx_logo.svg"
# html_favicon = "_static/solposx_logo.svg"

html_theme_options = {
    "repository_url": "https://github.com/assessingsolar/solposx",
    "use_issues_button": True,
    "use_repository_button": True,
    "use_download_button": False,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "matplotlib": ("https://matplotlib.org/stable", None),
    "shapely": ("https://shapely.readthedocs.io/en/stable/", None),
    "pvlib": ("https://pvlib-python.readthedocs.io/en/stable/", None),
}

extlinks = {
    "issue": ("https://github.com/assessingsolar/solposx/issues/%s", "GH%s"),
    "pull": ("https://github.com/assesingsolar/solposx/pull/%s", "GH%s"),
    "ghuser": ("https://github.com/%s", "@%s"),
    "doi": ("http://dx.doi.org/%s", "DOI: %s"),
}


# Number of seconds for a cell to execute before timeout (default=30)
nb_execution_timeout = 120
