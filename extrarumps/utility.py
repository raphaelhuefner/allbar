import base64

def get_data_from_base64_data_url(data_url):
    header, encoded = data_url.split(',', 1)
    return base64.b64decode(encoded)
