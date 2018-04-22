import rfc3987

def is_url_valid(url, accepted_url_schemes=['http', 'https', 'file', 'data', 'ftp']):
    if not isinstance(url, str):
        return False
    try:
        parts = rfc3987.parse(url, 'IRI')
    except ValueError:
        return False
    return (
        parts['scheme'] in accepted_url_schemes
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
