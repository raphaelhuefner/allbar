"""Provide a data model class for our config data."""

from datetime import datetime
import json
import urllib.request

import allbar.update
import allbar.utility


class AllBarDataStore():
    """Access status bar and menu config data via a central place."""

    def __init__(self, logger=None):
        """Set up the model."""
        self.cache = {
            'ttl': 1,
            'indicators': ['0:00'],
            'menu': []
        }
        self.cache_last_updated = self.invalidate_cache()
        self.update_url = None
        self.current_indicator_index = 0
        self.validator = allbar.update.Validator(logger)
        self.logger = logger

    def log(self, *args):
        """Log events in this class if configured.

        Defaults to no logging. (See __init__() for changing that.)
        """
        if hasattr(self.logger, '__call__'):
            self.logger(*args)

    def set_update_url(self, update_url):
        """Set URL to get the config data from."""
        if update_url is None:
            self.load_demo_mode()
        if self.update_url is not update_url:
            self.invalidate_cache()
        self.update_url = update_url

    def load_demo_mode(self):
        """Load pre-packaged config data."""
        demo_mode = allbar.utility.load_packaged_json_file('demo_mode.json')
        self.cache = json.loads(demo_mode)
        self.cache_last_updated = datetime.now()

    def is_cache_valid(self):
        """Decide if config data is past it's TTL."""
        if 'ttl' in self.cache:
            time_since_last_update = datetime.now() - self.cache_last_updated
            if time_since_last_update.total_seconds() < int(self.cache['ttl']):
                return True
        return False

    def invalidate_cache(self):
        """Mark the cache as invalid."""
        self.cache_last_updated = datetime(1970, 1, 1)
        return self.cache_last_updated

    def is_new_data_valid(self, new_data):
        """Validate incoming config data."""
        return self.validator.is_valid(new_data)

    def update(self):
        """Pull new config data from URL."""
        if self.is_cache_valid():
            return
        if not allbar.utility.is_url_valid(self.update_url):
            return
        # pylint: disable=broad-except
        # ^^ TODO determine list of possible exceptions and name them here.
        try:
            with urllib.request.urlopen(self.update_url) as http_response:
                new_data = json.loads(http_response.read())
                if self.is_new_data_valid(new_data):
                    self.cache = new_data
                    self.cache_last_updated = datetime.now()
                else:
                    self.log('New data incomplete:', repr(new_data))
        except Exception as exception:
            self.log(exception)

    def get_current_menu_settings(self):
        """Access menu config data."""
        self.update()
        return self.cache['menu']

    def get_current_indicator(self):
        """Access status bar config data.

        With each access, cycle through all available alternatives.
        """
        self.update()
        self.current_indicator_index += 1
        self.current_indicator_index %= len(self.cache['indicators'])
        return self.cache['indicators'][self.current_indicator_index]
