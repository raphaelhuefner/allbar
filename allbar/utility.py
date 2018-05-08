import os.path

import modulegraph.zipio
import rfc3987


def is_url_valid(url, valid_schemes=['http', 'https', 'file', 'data', 'ftp']):
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
            '' != parts['authority']
            or
            (
                'file' == parts['scheme']
                and
                '' != parts['path']
            )
        )
    )


def load_packaged_json_file(filename):
    fullfilename = os.path.join(os.path.dirname(__file__), 'json', filename)
    with modulegraph.zipio.open(fullfilename) as f:
        filecontents = f.read()
    return filecontents
