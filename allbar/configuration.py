"""Provide config file handler class."""

import configparser

import extrarumps as rumps

import allbar.utility


class AllBarConfiguration():
    """Read and write app config file, present GUI to change config.

    So far there is only one config value, a URL to fetch all further actual
    config from.
    """

    def __init__(self, file_name='allbar.ini', logger=None):
        """Set up config file handler."""
        self.app = None
        self.file_name = file_name
        self.logger = logger
        self.update_url = None
        self.is_cancelled = False

    def log(self, *args):
        """Log events in this class if configured.

        Defaults to no logging. (See __init__() for changing that.)
        """
        if hasattr(self.logger, '__call__'):
            self.logger(*args)

    def set_app(self, app):
        """Inject AllBarApp as dependency."""
        self.app = app

    def show_ui(self):
        """Present GUI to change the single config value, a URL for updates."""
        url = self.read()
        explanation = ' '.join((
            'URL for JSON updates.',
            'Must be a full absolute URL.',
            '(i.e. includes http:// or https://)'
        ))
        window = rumps.Window(
            message=explanation,
            title='AllBar Preferences',
            cancel=True,
            default_text=url if url else '',
            dimensions=(800, 40)
        )
        window.add_button('Quit')
        prompt_response = window.run()
        if 0 is prompt_response.clicked:  # "Cancel" button
            self.is_cancelled = True
        if 1 is prompt_response.clicked:  # "OK" button
            url = prompt_response.text.strip()
            if allbar.utility.is_url_valid(url):
                self.write(url)
                return url
            else:
                rumps.alert(
                    'Unable to validate update URL. '
                    'Please input a valid URL!'
                )
        if 2 is prompt_response.clicked:  # "Quit" button
            rumps.quit_application()
        return None

    def read(self):
        """Read update URL from config file."""
        if self.update_url:
            return self.update_url
        # pylint: disable=broad-except
        # ^^ TODO determine list of possible exceptions and name them here.
        try:
            with self.app.open(self.file_name, 'r') as configfile:
                config = configparser.ConfigParser()
                config.read_file(configfile)
                self.update_url = config['allbar']['update_url']
                return self.update_url
        except Exception as exception:
            self.log(exception)
            return None

    def write(self, url):
        """Write update URL to config file."""
        config = configparser.ConfigParser()
        config['allbar'] = {
            'update_url': url
        }
        with self.app.open(self.file_name, 'w') as configfile:
            config.write(configfile)
            self.update_url = url

    def get_update_url(self):
        """Retrieve the single config value, an update URL."""
        url = self.read()
        return url if url else None
