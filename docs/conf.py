# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

project = 'zyntex'
copyright = '2025, xXenvy'
author = 'xXenvy'
release = "0.2.3"

package_source = Path(__file__).resolve().parents[1] / "python" / "src" / "__init__.py"
package_spec = spec_from_file_location("zyntex", package_source)
package = module_from_spec(package_spec)
sys.modules["zyntex"] = package
package_spec.loader.exec_module(package)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinxext.opengraph",
    "sphinx_inline_tabs",
]

templates_path = ['_templates']
exclude_patterns = ['_build']

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ['_static']
