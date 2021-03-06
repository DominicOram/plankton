# -*- coding: utf-8 -*-
#
# plankton documentation build configuration file, created by
# sphinx-quickstart on Wed Nov  9 16:42:53 2016.
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

# -- General configuration ------------------------------------------------

needs_sphinx = '1.4.5'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.imgmath',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = u'plankton'
copyright = u'2016, European Spallation Source ERIC'
author = u'Michael Hart, Michael Wedel, Owen Arnold'

version = u'1.0'
release = u'1.0'

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'
todo_include_todos = False

modindex_common_prefix = ['plankton.']

# -- Options for HTML output ---------------------------------------------

# This is from the sphinx_rtd_theme documentation to make the page work with RTD
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:
    import sphinx_rtd_theme

    html_theme = "sphinx_rtd_theme"
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_static_path = []
html_show_sourcelink = True
htmlhelp_basename = 'planktondoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    'papersize': 'a4paper',
}

latex_documents = [
    (master_doc, 'plankton.tex', u'plankton Documentation',
     u'Michael Hart, Michael Wedel, Owen Arnold', 'manual'),
]
