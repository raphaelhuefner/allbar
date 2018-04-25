import configparser
import json
import urllib.parse
import urllib.request
import webbrowser

import extrarumps as rumps

class AllBarApp(rumps.App):
    def __init__(self, logger=None):
        super(AllBarApp, self).__init__("AllBar", "x:xx")
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
            if isinstance(current_indicator, str):
                self.icon = None
                self.title = current_indicator
            else:
                self.icon = current_indicator['icon']
                self.title = current_indicator['title']

    def update_menu(self):
        current_menu_settings = self.datastore.get_current_menu_settings()
        if self.previous_menu_settings != current_menu_settings:
            self.previous_menu_settings = current_menu_settings
            self.menu.clear()
            for menu_setting in current_menu_settings:
                self.menu.add(self.make_menu_item(menu_setting))
            self.menu.add(None)
            self.menu.add(rumps.MenuItem('Preferences', self.preferences))
            self.menu.add(rumps.MenuItem('Quit', rumps.quit_application))

    def make_menu_item(self, settings):
        if 'separator' in settings:
            return None
        title = settings['title']
        if 'disabled' in settings:
            menu_item = self.make_disabled_menu_item(title, settings)
        if 'open' in settings:
            menu_item = self.make_open_menu_item(title, settings)
        if 'request' in settings:
            menu_item = self.make_request_menu_item(title, settings)
        menu_item.state = settings['active']
        return menu_item

    def make_disabled_menu_item(self, title, settings):
        menu_item = rumps.MenuItem(title, None)
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
        if self.has_prompt(sender):
            prompt_response = self.prompt_user(sender.prompt)
            if prompt_response:
                request = self.make_request_with_prompt_data(sender.request, prompt_response, sender.prompt['placeholder'])
            else:
                return
        else:
            request = self.make_request(sender.request)
        with urllib.request.urlopen(request) as http_response:
            self.log('got {code} for {method} {url}'.format(code=http_response.getcode(), method=request.method, url=request.full_url))
            self.datastore.invalidate_cache()

    def has_prompt(self, sender):
        try:
            prompt = sender.prompt
            return True
        except Exception as e:
            return False

    def prompt_user(self, prompt):
        response = rumps.Window(
            message = prompt['message'],
            title = prompt['title'],
            cancel = True,
        ).run()
        return response.text if response.clicked else None

    def make_request_with_prompt_data(self, request_config, prompt_response, prompt_placeholder):
        url = request_config['url'].replace(prompt_placeholder, urllib.parse.quote(prompt_response))
        request = urllib.request.Request(url, method=request_config['method'])
        if 'headers' in request_config:
            for key, value in request_config['headers'].items():
                new_value = value.replace(prompt_placeholder, urllib.parse.quote(prompt_response))
                request.add_header(key, new_value)
        if 'body' in request_config:
            body = self.put_prompt_data_into_body(request_config['body'], prompt_response, prompt_placeholder)
            self.encode_body(request, body)
        return request

    def put_prompt_data_into_body(self, body, prompt_response, prompt_placeholder):
        if isinstance(body, dict):
            new_body = {}
            for i in body:
                new_body[i] = self.put_prompt_data_into_body(body[i], prompt_response, prompt_placeholder)
            return new_body
        elif isinstance(body, list):
            new_body = []
            for i in body:
                new_body.append(self.put_prompt_data_into_body(i, prompt_response, prompt_placeholder))
            return new_body
        elif isinstance(body, str):
            return body.replace(prompt_placeholder, prompt_response)
        else:
            return body

    def make_request(self, request_config):
        url = request_config['url']
        headers = request_config['headers'] if 'headers' in request_config else {}
        request = urllib.request.Request(url, headers=headers, method=request_config['method'])
        if 'body' in request_config:
            self.encode_body(request, request_config['body'])
        return request

    def encode_body(self, request, body):
        content_type = self.ensure_content_type(request)
        if 'application/x-www-form-urlencoded' == content_type:
            request.data = urllib.parse.urlencode(body).encode()
        elif 'application/json' == content_type:
            request.data = json.dumps(body).encode()

    def ensure_content_type(self, request):
        if not request.has_header('Content-type'):
            request.add_header('Content-type', 'application/json')
        return request.get_header('Content-type')

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
