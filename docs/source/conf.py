# Configuration file for the Sphinx documentation builder.
# Disclaimer: this doc configuration is heavily inspired by rameau's documentation.

# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os, sys
# sys.path.insert(0, '../../src')
from gridmarthe import __version__

project = 'gridmarthe'
authors = 'Jean-Pierre Vergnes, Adrien Manlay'
# copyright = '2024,  BRGM.\nAuthors: {}'.format(authors)
copyright = '2024,  BRGM'

release = __version__
language = 'en'

html_short_title = project
html_title = project

html_baseurl = 'https://gridmarthe.readthedocs.io/'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# memo with sphinx.ext.autopi : sphinx-apidoc -o ../docs/source/user_guide ../src

extensions = [
    'pydata_sphinx_theme',
    'sphinx.ext.duration',
    'sphinx.ext.autodoc',           # Core library for html generation from docstrings
    'sphinx.ext.autosummary',       # Create neat summary tables, by importing code. autoapi just parse the code
    'sphinx.ext.mathjax',
    'sphinx.ext.doctest',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',          # allow different style of docstrings
    'sphinx.ext.intersphinx',
    'sphinx_design',                # grid layout
    'sphinxcontrib.bibtex',
    'myst_nb',                      # for notebooks
    'sphinx_copybutton',            # copy button in code samples
    'sphinx.ext.autosectionlabel',  # better cross ref
]

templates_path = ['_templates']
pygments_style = 'sphinx'
highlight_language = 'python'
exclude_patterns = []
todo_include_todos = False  # Do not show TODOs in docs


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'furo'
html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# version switcher
json_url = html_baseurl + language + '/latest/_static/switcher.json'
version_match = os.environ.get("READTHEDOCS_VERSION")

# If READTHEDOCS_VERSION doesn't exist, we're not on RTD
# If it is an integer, we're in a PR build and the version isn't correct.
# If it's "latest" → change to "dev" (that's what we want the switcher to call it)
if not version_match or version_match.isdigit() or version_match in ["latest", "dev"]:
    # For local development, infer the version to match from the package.
    version_match = "dev"
    json_url = "_static/switcher.json"
elif version_match == "stable":
    version_match = f"v{release}"

# adapted from gardenia/rameau doc:
html_permalinks_icon = '<span class="fa fa-link">'
html_theme_options = {
    "icon_links": [
        {
            "name": "GitLab",
            "url" : "https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe.git",
            "icon": "fa-brands fa-gitlab",
            "type": "fontawesome",
        }
    ],
    "navbar_align": "content",
    "navbar_start": ["navbar-logo"],
    "navbar_end": ["version-switcher", "theme-switcher", "navbar-icon-links"],
    "footer_start": ["copyright", "sphinx-version", "last-updated"],
    "footer_end": ["brgm-logo-{}".format(language)],
    "show_toc_level": 1,
    "show_nav_level": 1,
    "header_links_before_dropdown": 6,
    "show_prev_next": False,
     "switcher": {
        "json_url": json_url,
        "version_match": version_match,
    },
}

html_last_updated_fmt = '%b %d, %Y'
html_use_index = True


# ----------------------------------------------------------------------
# Options for *sphinx.ext.autosummary* extension
# ----------------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html

autosummary_generate = True
autosummary_template = 'autosummary/module.rst'  # add template to always show doc in module


# ----------------------------------------------------------------------
# Options for *sphinx.ext.autodoc* extension
# ----------------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

autodoc_member_order = 'bysource'
#autodoc_default_options = {"members":True}#, "show-inheritance":True}  # could be enought instead of tpl ?
autodoc_typehints = 'none' # signature, description, none, both
autoclass_content = 'class'

# ----------------------------------------------------------------------
# Options for *sphinx.ext.napoleon* extension
# ----------------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

napoleon_use_rtype = False


# ----------------------------------------------------------------------
# Options for *sphinxcontrib.bibtex* extension
# ----------------------------------------------------------------------
# https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html

bibtex_bibfiles = ['refs.bib']
bibtex_reference_style = 'author_year'


# ----------------------------------------------------------------------
# Options for *sphinx.ext.intersphinx* extension
# ----------------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

intersphinx_mapping = {
    'sphinx': ('https://www.sphinx-doc.org/en/master/',  None),
    'python': ('https://docs.python.org/3', None),
    'numpy' : ('https://docs.scipy.org/doc/numpy', None),
    'pandas': ("https://pandas.pydata.org/docs/", None),
    # 'xarray': ("https://docs.xarray.dev/", None),
}

intersphinx_cache_limit = 5
