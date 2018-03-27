import configparser
import sys

if ('pytest' not in sys.modules):
    import rumps as rumps
else:
    import tests.mocks.rumps as rumps

import timetracker.utility

class TimeTrackerConfiguration():
    def __init__(self, app, file_name='timetracker.ini', logger=None):
        self.app = app
        self.file_name = file_name
        self.logger = logger
        self.update_url = None
        self.is_cancelled = False

    def log(self, *args):
        if hasattr(self.logger, '__call__'):
            self.logger(*args)
        
    def show_ui(self):
        url = self.read()
        explanation = ' '.join((
            'URL for JSON updates.',
            'Must be a full absolute URL.',
            '(i.e. includes http:// or https://)'
        ))
        window = rumps.Window(
            message = explanation,
            title = 'Time Tracker Preferences',
            cancel = True,
            default_text = url if url else '',
            dimensions=(800, 40)
        )
        window.add_button('Quit')
        prompt_response = window.run()
        if 0 is prompt_response.clicked: # "Cancel" button
            self.is_cancelled = True
        if 1 is prompt_response.clicked: # "OK" button
            url = prompt_response.text.strip()
            if timetracker.utility.is_url_valid(url):
                self.write(url)
                return url
            else:
                rumps.alert(
                    'Unable to validate update URL. '
                    'Please input a valid URL!'
                )
        if 2 is prompt_response.clicked: # "Quit" button
            rumps.quit_application()
        return None

    def read(self):
        if self.update_url:
            return self.update_url
        try:
            with self.app.open(self.file_name, 'r') as configfile:
                config = configparser.ConfigParser()
                config.read_file(configfile)
                self.update_url = config['timetracker']['update_url']
                return self.update_url
        except Exception as e:
            self.log(e)
            return None

    def write(self, url):
        config = configparser.ConfigParser()
        config['timetracker'] = {
            'update_url': url
        }
        with self.app.open(self.file_name, 'w') as configfile:
            config.write(configfile)
            self.update_url = url

    def get_update_url(self):
        url = self.read()
        return url if url else self.show_ui() if not self.is_cancelled else None
