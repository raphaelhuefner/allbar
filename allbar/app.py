"""Define a fully customizable macOS status bar app class."""

import json
import urllib.parse
import urllib.request
import webbrowser

import extrarumps as rumps

import allbar.configuration
import allbar.datastore


class AllBarApp(rumps.App):
    """Provide a fully customizable macOS status bar app."""

    # pylint: disable=too-many-instance-attributes
    # ^^ The app ties everything together. Not "too many" but "just right".

    def __init__(self, config, datastore, logger=None):
        """Set up app."""
        super(AllBarApp, self).__init__("AllBar", "x:xx")
        self.menu = rumps.MenuItem('Preferences', self.preferences)

        self.set_config(config)

        self.set_datastore(datastore)

        self.previous_indicator = ''
        self.previous_menu_settings = []
        self.logger = logger

    def log(self, *args):
        """Log events in this class as configured.

        Defaults to no logging. (See __init__() for changing that.)
        """
        if hasattr(self.logger, '__call__'):
            self.logger(*args)

    def set_config(self, config):
        """Inject AllBarConfiguration (or subclass) as dependency."""
        if not isinstance(config, allbar.configuration.AllBarConfiguration):
            msg = 'Can not use as configuration: {cfg}'
            raise ValueError(msg.format(cfg=repr(config)))
        self.config = config
        self.config.set_app(self)

    def set_datastore(self, datastore):
        """Inject AllBarDataStore (or subclass) as dependency."""
        if not isinstance(datastore, allbar.datastore.AllBarDataStore):
            msg = 'Can not use as datastore: {store}'
            raise ValueError(msg.format(store=repr(datastore)))
        self.datastore = datastore

    def update_indicator(self):
        """Change icon and text visible in the status bar."""
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
        """Change the pull-down menu of our status bar item."""
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
        """Create a rumps menu item according to incoming JSON settings."""
        if 'separator' in settings:
            return None
        title = settings['title']
        if 'disabled' in settings:
            menu_item = self.make_disabled_menu_item(title)
        if 'open' in settings:
            menu_item = self.make_open_menu_item(title, settings)
        if 'request' in settings:
            menu_item = self.make_request_menu_item(title, settings)
        menu_item.state = settings['active']
        return menu_item

    def make_disabled_menu_item(self, title):
        """Create an unclickable rumps menu item with greyed-out text."""
        # pylint: disable=no-self-use
        # ^^ keep this inside class along sister methods make_*_menu_item()
        # see https://en.wikipedia.org/wiki/Principle_of_least_astonishment
        menu_item = rumps.MenuItem(title, None)
        return menu_item

    def make_open_menu_item(self, title, settings):
        """Create rumps menu item which opens a URL in a browser."""
        menu_item = rumps.MenuItem(title, self.open_url)
        menu_item.open_url = settings['open']
        return menu_item

    def open_url(self, sender):
        """Menu callback to open a URL in a browser."""
        # pylint: disable=no-self-use
        # ^^ keep this inside class along sister menu callback methods
        # see https://en.wikipedia.org/wiki/Principle_of_least_astonishment
        webbrowser.open_new_tab(sender.open_url)

    def make_request_menu_item(self, title, settings):
        """Create rumps menu item which sends an HTTP request."""
        menu_item = rumps.MenuItem(title, self.send_request)
        if 'method' not in settings['request']:
            settings['request']['method'] = 'GET'
        menu_item.request = settings['request']
        if 'prompt' in settings:
            menu_item.prompt = settings['prompt']
        return menu_item

    def send_request(self, sender):
        """Menu callback to send an HTTP request."""
        # pylint: disable=fixme
        # TODO Refactor HTTP request sending into separate module.
        # see https://github.com/raphaelhuefner/allbar/issues/1
        if hasattr(sender, 'prompt'):
            prompt_response = self.prompt_user(sender.prompt)
            if prompt_response:
                request = self.make_request_with_prompt_data(
                    sender.request,
                    prompt_response,
                    sender.prompt['placeholder']
                )
            else:
                return
        else:
            request = self.make_request(sender.request)
        with urllib.request.urlopen(request) as http_response:
            self.log('got {code} for {method} {url}'.format(
                code=http_response.getcode(),
                method=request.method,
                url=request.full_url
            ))
            self.datastore.invalidate_cache()

    def prompt_user(self, prompt):
        """Show GUI text-field dialog and collect user response."""
        # pylint: disable=no-self-use
        # pylint: disable=fixme
        # TODO Refactor user prompting sending into separate module.
        # see https://github.com/raphaelhuefner/allbar/issues/2
        response = rumps.Window(
            message=prompt['message'],
            title=prompt['title'],
            cancel=True,
        ).run()
        return response.text if response.clicked else None

    def make_request_with_prompt_data(self, request_config, prompt_response,
                                      prompt_placeholder):
        """Create HTTP request with user input from GUI text-field dialog."""
        url_response = urllib.parse.quote(prompt_response)
        url = request_config['url'].replace(prompt_placeholder, url_response)
        request = urllib.request.Request(url, method=request_config['method'])
        if 'headers' in request_config:
            for key, value in request_config['headers'].items():
                new_value = value.replace(prompt_placeholder, url_response)
                request.add_header(key, new_value)
        if 'body' in request_config:
            body = self.put_prompt_data_into_body(
                request_config['body'],
                prompt_response,
                prompt_placeholder
            )
            self.encode_body(request, body)
        return request

    def put_prompt_data_into_body(self, body,
                                  prompt_response, prompt_placeholder):
        """Replace placeholders in HTTP request body config with user input."""
        if isinstance(body, dict):
            new_body = {}
            for i in body:
                new_body[i] = self.put_prompt_data_into_body(
                    body[i], prompt_response, prompt_placeholder
                )
            return new_body
        elif isinstance(body, list):
            new_body = []
            for i in body:
                new_body.append(self.put_prompt_data_into_body(
                    i, prompt_response, prompt_placeholder
                ))
            return new_body
        elif isinstance(body, str):
            return body.replace(prompt_placeholder, prompt_response)
        return body

    def make_request(self, cfg):
        """Create HTTP request without user input."""
        req_cfg = {
            'url': cfg['url'],
            'headers': cfg['headers'] if 'headers' in cfg else {},
            'method': cfg['method'] if 'method' in cfg else 'GET'
        }
        request = urllib.request.Request(**req_cfg)
        if 'body' in cfg:
            self.encode_body(request, cfg['body'])
        return request

    def encode_body(self, request, body):
        """Encode HTTP request body according to 'Content-type' header."""
        content_type = self.ensure_content_type(request)
        if content_type == 'application/x-www-form-urlencoded':
            request.data = urllib.parse.urlencode(body).encode()
        elif content_type == 'application/json':
            request.data = json.dumps(body).encode()

    def ensure_content_type(self, request):
        """Get 'Content-type' header or default it to JSON."""
        # pylint: disable=no-self-use
        # pylint: disable=fixme
        # TODO Refactor HTTP request sending into separate module.
        # see https://github.com/raphaelhuefner/allbar/issues/1
        if not request.has_header('Content-type'):
            request.add_header('Content-type', 'application/json')
        return request.get_header('Content-type')

    def preferences(self, _):
        """Menu callback to show GUI text-field dialog for config URL."""
        self.config.show_ui()

    def ensure_current_update_url(self):
        """Make sure the datastore is using the current config URL."""
        update_url = self.config.get_update_url()
        self.datastore.set_update_url(update_url)

    @rumps.timer(1)
    def refresh(self, _):
        """Update UI to current (or cached) config once a second."""
        self.ensure_current_update_url()
        self.update_menu()
        self.update_indicator()
