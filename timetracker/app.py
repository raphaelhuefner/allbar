import configparser
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
        self.accepted_actions = {
            'get_url': self.get_url,
            'open_url': self.open_url,
            'post_url': self.post_url,
        }
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
                title = menu_setting['title']
                action = self.accepted_actions[menu_setting['action']]
                menu_item = rumps.MenuItem(title, action)
                menu_item.state = menu_setting['active']
                menu_item.url = menu_setting['url']
                if 'post_url' == menu_setting['action']:
                    menu_item.prompt_title = menu_setting['prompt_title']
                    menu_item.prompt_message = menu_setting['prompt_message']
                self.menu.add(menu_item)
            self.menu.add(rumps.MenuItem('Preferences', self.preferences))
            self.menu.add(rumps.MenuItem('Quit', rumps.quit_application))

    def get_url(self, sender):
        with urllib.request.urlopen(sender.url) as http_response:
            self.log('got', http_response.getcode(), 'for GET', sender.url)
            self.datastore.invalidate_cache()

    def open_url(self, sender):
        webbrowser.open_new_tab(sender.url)

    def post_url(self, sender):
        message = sender.prompt_message
        title = sender.prompt_title
        prompt_response = rumps.Window(message=message, title=title).run()
        if prompt_response.clicked:
            payload = urllib.parse.urlencode({'value':prompt_response.text})
            request = urllib.request.Request(sender.url, data=payload.encode())
            with urllib.request.urlopen(request) as http_response:
                self.log('got', http_response.getcode(), 'for POST', sender.url)
                self.datastore.invalidate_cache()

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
