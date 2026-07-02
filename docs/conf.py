"""Sphinx configuration for inito's documentation."""

from __future__ import annotations

from inito import __version__

project = "inito"
copyright = "2026, Swetank Subham"
author = "Swetank Subham"
version = __version__
release = __version__

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = ["colon_fence"]
myst_heading_anchors = 3

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# --- HTML theme: PyData Sphinx Theme (NumPy-style layout) -------------------
html_theme = "pydata_sphinx_theme"
html_title = "inito"

# Served as a GitHub Pages project site under the account's custom domain,
# i.e. https://swetanksubham.com/inito/. Sphinx uses relative links for
# navigation and assets, so the site works under this subpath; html_baseurl
# only sets the canonical URL (SEO) and any absolute references.
html_baseurl = "https://swetanksubham.com/inito/"

html_theme_options = {
    "logo": {"text": "inito"},
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/swtnk/inito",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/inito/",
            "icon": "fa-brands fa-python",
        },
    ],
    "use_edit_page_button": True,
    "navbar_align": "left",
    "header_links_before_dropdown": 5,
    "show_toc_level": 2,
    "show_prev_next": True,
    "navigation_with_keys": False,
    "footer_start": ["copyright"],
    "footer_end": ["theme-version"],
}

# Powers the "Edit on GitHub" button and source links.
html_context = {
    "github_user": "swtnk",
    "github_repo": "inito",
    "github_version": "main",
    "doc_path": "docs",
    "default_mode": "auto",
}

# Left sidebar shows the section navigation; the landing page hides it so the
# hero + cards get the full width (NumPy does the same on its front page).
html_sidebars = {
    "index": [],
}

autodoc_member_order = "bysource"
autodoc_typehints = "description"
napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
