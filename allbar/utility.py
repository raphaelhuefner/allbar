"""Provide general toolbox."""

import os.path

import modulegraph.zipio
import rfc3987


def is_url_valid(url, valid_schemes=('http', 'https', 'file', 'data', 'ftp')):
    """Validate URLs usable with Python's urllib.request.urlopen()."""
    if not isinstance(url, str):
        return False
    try:
        parts = rfc3987.parse(url, 'IRI')
    except ValueError:
        return False
    return (
        parts['scheme'] in valid_schemes
        and
        (
            parts['authority'] != ''
            or
            (
                parts['scheme'] == 'file'
                and
                parts['path'] != ''
            )
        )
    )


def load_packaged_json_file(filename):
    """Load JSON files from a ZIP file when packaged as a macOS app."""
    fullfilename = os.path.join(os.path.dirname(__file__), 'json', filename)
    with modulegraph.zipio.open(fullfilename) as file:
        filecontents = file.read()
    return filecontents
