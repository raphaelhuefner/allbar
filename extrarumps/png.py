import struct

def get_png_dimensions(data):
    if is_png(data):
        w, h = struct.unpack('>LL', data[16:24])
        return int(w), int(h)
    else:
        return None, None

def is_png(data):
    return (
        (data[:8] == b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A')
        and
        (data[12:16] == b'IHDR')
    )
