import contextlib
import io
import urllib.request

mock_responses = {}

def urlopen(url_or_request):
    global mock_responses
    if isinstance(url_or_request, urllib.request.Request):
        url = url_or_request.get_full_url()
    elif isinstance(url_or_request, str):
        url = url_or_request
    else:
        raise ValueError('Do not know how to mock urllib.request.urlopen({req}).'.format(req=repr(url_or_request)))
    response = mock_responses[url] if url in mock_responses else HTTPResponse(404, b'')
    return contextlib.closing(response)


class HTTPResponse():
    def __init__(self, code, body, headers={}):
        self._code = code
        if isinstance(body, bytes):
            body = body
        elif isinstance(body, str):
            body = body.encode()
        self._body = io.BytesIO(body)

    def getcode(self):
        return self._code

    def read(self):
        return self._body.read()

    def close(self):
        self._body.close()

    