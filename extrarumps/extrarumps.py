import rumps

import AppKit

from .utility import get_data_from_base64_data_url
from .png import get_png_dimensions

def _nsimage_from_data_url(data_url, dimensions=None, template=None):
    """Take a "data:" URL of a PNG image file and return an NSImage object."""
    data = get_data_from_base64_data_url(data_url)
    image = AppKit.NSImage.alloc().initWithData_(data)
    image.setScalesWhenResized_(True)
    image.setSize_(get_png_dimensions(data) if dimensions is None else dimensions)
    if not template is None:
        image.setTemplate_(template)
    return image

class App(rumps.App):
    @rumps.App.icon.setter
    def icon(self, icon_data_url):
        new_icon = _nsimage_from_data_url(icon_data_url, template=self._template) if icon_data_url is not None else None
        self._icon = icon_data_url
        self._icon_nsimage = new_icon
        try:
            self._nsapp.setStatusBarIcon()
        except AttributeError as e:
            pass
