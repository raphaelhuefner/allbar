import configparser
import json
import sys
import urllib.parse
import urllib.request
import webbrowser

if ('pytest' not in sys.modules):
    import rumps as rumps
else:
    import tests.mocks.rumps as rumps

class TimeTrackerStatusBarApp(rumps.App):
    def __init__(self, logger=None):
        super(TimeTrackerStatusBarApp, self).__init__("Time Tracker", "0:00")
        self.menu = rumps.MenuItem('Preferences', self.preferences)
        self.config = None # inject with set_config() before calling run()
        self.datastore = None # inject with set_datastore() before calling run()
        self.previous_indicator = ''
        self.previous_menu_settings = []
        self.logger = logger

    def log(self, *args):
        if hasattr(self.logger, '__call__'):
            self.logger(*args)

    def set_config(self, config):
        self.config = config

    def set_datastore(self, datastore):
        self.datastore = datastore

    def update_indicator(self):
        current_indicator = self.datastore.get_current_indicator()
        if self.previous_indicator != current_indicator:
            self.previous_indicator = current_indicator
            self.title = current_indicator

    def update_menu(self):
        current_menu_settings = self.datastore.get_current_menu_settings()
        if self.previous_menu_settings != current_menu_settings:
            self.previous_menu_settings = current_menu_settings
            self.menu.clear()
            for menu_setting in current_menu_settings:
                self.menu.add(self.make_menu_item(menu_setting))
            self.menu.add(rumps.MenuItem('Preferences', self.preferences))
            self.menu.add(rumps.MenuItem('Quit', rumps.quit_application))

    def make_menu_item(self, settings):
        title = settings['title']
        if 'open' in settings:
            menu_item = self.make_open_menu_item(title, settings)
        if 'request' in settings:
            menu_item = self.make_request_menu_item(title, settings)
        menu_item.state = settings['active']
        return menu_item

    def make_open_menu_item(self, title, settings):
        menu_item = rumps.MenuItem(title, self.open_url)
        menu_item.open_url = settings['open']
        return menu_item

    def open_url(self, sender):
        webbrowser.open_new_tab(sender.open_url)

    def make_request_menu_item(self, title, settings):
        menu_item = rumps.MenuItem(title, self.send_request)
        settings['request']['method'] = settings['request']['method'] if 'method' in settings['request'] else 'GET'
        menu_item.request = settings['request']
        if 'prompt' in settings:
            menu_item.prompt = settings['prompt']
        return menu_item

    def send_request(self, sender):
        prompt_response, prompt_varname = self.prompt_user(sender)
        if prompt_response:
            request_config = self.put_prompt_data_into_request(sender.request, prompt_response, prompt_varname)
        else:
            request_config = sender.request
        # request_config['method'] = request_config['method'] if 'method' in request_config else 'GET'
        request = urllib.request.Request(**request_config)
        with urllib.request.urlopen(request) as http_response:
            self.log('got {code} for {method} {url}'.format(code=http_response.getcode(), **request_config))
            self.datastore.invalidate_cache()

    def prompt_user(self, sender):
        try:
            prompt = sender.prompt
        except Exception as e:
            return None, None
        message = prompt['message']
        title = prompt['title']
        response = rumps.Window(message=message, title=title).run()
        if response.clicked:
            return response.text, prompt['placeholder']
        return None, None

    def put_prompt_data_into_request(self, request_config, prompt_response, prompt_varname):
        new_request = {'method': request_config['method']}
        new_request['url'] = request_config['url'].replace(prompt_varname, urllib.parse.quote(prompt_response))
        if 'headers' in request_config:
            new_request['headers'] = {}
            for key, value in request_config['headers'].items():
                new_request['headers'][key] = request_config['headers'][key].replace(prompt_varname, urllib.parse.quote(prompt_response))
            if 'Content-Type' in request_config['headers']:
                if 'application/x-www-form-urlencoded' == request_config['headers']['Content-Type']:
                    new_request['data'] = urllib.parse.urlencode({prompt_varname:prompt_response}).encode()
                if 'application/json' == request_config['headers']['Content-Type']:
                    new_request['data'] = json.dumps({prompt_varname:prompt_response}).encode()
        return new_request

    def preferences(self, sender):
        self.config.show_ui()

    def ensure_current_update_url(self):
        update_url = self.config.get_update_url()
        self.datastore.set_update_url(update_url)

    @rumps.timer(1)
    def refresh(self, _):
        self.ensure_current_update_url()
        self.update_menu()
        self.update_indicator()
