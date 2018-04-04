import urllib.parse

def is_url_valid(url, accepted_url_schemes=['http', 'https', 'file']):
    url_parts = urllib.parse.urlparse(url)
    return (
        url_parts.scheme in accepted_url_schemes
        and
        (
            '' != url_parts.netloc
            or
            (
                'file' == url_parts.scheme
                and
                '' != url_parts.path
            )
        )
    )
