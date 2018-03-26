from datetime import datetime
import json
import urllib.request

import utility

class TimeTrackerDataStore():
    def __init__(self, logger=None):
        self.cache = {
            'ttl': 1,
            'indicators': ['0:00'],
            'menu': []
        }
        self.invalidate_cache()
        self.update_url = None
        self.current_indicator_index = 0
        self.logger = logger

    def log(self, *args):
        if hasattr(self.logger, '__call__'):
            self.logger(*args)

    def set_udate_url(self, update_url):
        if self.update_url is not update_url:
            self.invalidate_cache()
        self.update_url = update_url

    def is_cache_valid(self):
        if 'ttl' in self.cache:
            time_since_last_update = datetime.now() - self.cache_last_updated
            if time_since_last_update.total_seconds() < int(self.cache['ttl']):
                return True
        return False

    def invalidate_cache(self):
        self.cache_last_updated = datetime(1970, 1, 1)

    def is_new_data_valid(self, new_data):
        return (
            'ttl' in new_data
            and
            'indicators' in new_data
            and
            'menu' in new_data
        )

    def update(self):
        if self.is_cache_valid():
            return
        if not utility.is_url_valid(self.update_url):
            return
        try:
            with urllib.request.urlopen(self.update_url) as http_response:
                new_data = json.loads(http_response.read())
                if self.is_new_data_valid(new_data):
                    self.cache = new_data
                    self.cache_last_updated = datetime.now()
                else:
                    self.log('New data incomplete:', repr(new_data))
        except Exception as e:
            self.log(e)

    def get_current_menu_settings(self):
        self.update()
        return self.cache['menu']

    def get_current_indicator(self):
        self.update()
        self.current_indicator_index += 1
        self.current_indicator_index %= len(self.cache['indicators'])
        return self.cache['indicators'][self.current_indicator_index]
