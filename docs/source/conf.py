# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os, sys
sys.path.insert(0, '../../src')

project = 'gridmarthe'
copyright = '2024, Adrien Manlay, Jean-Pierre Vergnes - BRGM'
author = 'Jean-Pierre Vergnes, Adrien Manlay'
release = '0.0.1'

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
html_short_title = "gridmarthe"
html_title = 'gridmarthe'
html_static_path = ['_static']
# html_css_files = ['custom.css']

# adapted from gardenia/ramo doc:
html_permalinks_icon = '<span class="fa fa-link">'
html_theme_options = {
    # "logo": {
    #     "text": 'aquida'
    # },
    "icon_links": [
        {
            "name": "GitLab",
            "url": f"https://gitlab.com/brgm/hydrogeological-modelling/marthe-tools/gridmarthe.git",
            "icon": "fa-brands fa-gitlab",
            "type": "fontawesome",
        }
    ],
    "show_prev_next": False,
    "show_toc_level": 1,
    "show_nav_level": 1,
    "navbar_align": "content",
    "navbar_start": ["navbar-logo"],
    "navbar_end": ["version-switcher","theme-switcher", "navbar-icon-links"],
    "footer_start": ["copyright", "sphinx-version", "last-updated"],
    # "footer_end": ["corporate-logo"],
    "header_links_before_dropdown": 6,
    "switcher": {
    #     "json_url": f"{html_baseurl}/_static/switcher.json",
        "json_url": "./switcher.json",
        "version_match": release
    },
}

html_last_updated_fmt = '%b %d, %Y'
html_use_index = True


# ----------------------------------------------------------------------
# Options for *sphinx.ext.autosummary* extension
# ----------------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html

autosummary_generate = True


# ----------------------------------------------------------------------
# Options for *sphinx.ext.autodoc* extension
# ----------------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

autodoc_member_order = 'bysource'
#autodoc_default_options = {"members":True}#, "show-inheritance":True}
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
    'numpy': ('https://docs.scipy.org/doc/numpy', None),
    'pandas': ("https://pandas.pydata.org/docs/", None),
}

intersphinx_cache_limit = 5
