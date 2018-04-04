import pytest

import timetracker.utility

from timetracker.app import TimeTrackerStatusBarApp
from timetracker.configuration import TimeTrackerConfiguration
from timetracker.datastore import TimeTrackerDataStore
from timetracker.utility import is_url_valid

import tests.mocks.rumps as rumps

class TestTimeTracker():

    @pytest.fixture(scope="class")
    def app(self):
        def noop(*args):
            pass
        logger = noop
        # logger = print

        app = TimeTrackerStatusBarApp(logger=logger)

        config = TimeTrackerConfiguration(app, logger=logger)
        app.set_config(config)

        store = TimeTrackerDataStore(logger=logger)
        app.set_datastore(store)

        return app

    def test_has_pytest(self):
        import sys
        assert 'pytest' in sys.modules

    def test_url_validation(self):
        assert not is_url_valid('http')
        assert not is_url_valid('https')
        assert not is_url_valid('https://')
        assert not is_url_valid('Hello World!')
        assert is_url_valid('http://google.com')
        assert is_url_valid('https://google.com')
        assert is_url_valid('file://localhost/Users/raphael/.DS_Store')
        assert is_url_valid('file:///Users/raphael/.DS_Store')

    def test_can_run(self, app):
        app.run()

    def test_can_refresh(self, app):
        app.refresh(None)

    def test_read_non_existing_config_file(self, app):
        app.mock_files({})
        assert None == app.config.read()
        assert None == app.config.update_url

    def test_read_existing_config_file(self, app):
        app.mock_files({
            app.config.file_name: """
                [timetracker]
                update_url=https://under.testing/update
            """
        })
        assert 'https://under.testing/update' == app.config.read()
        assert 'https://under.testing/update' == app.config.update_url

        app.mock_files({})
        assert 'https://under.testing/update' == app.config.read()
        assert 'https://under.testing/update' == app.config.update_url

    def test_config_ui_cancel(self, app):
        app.config.is_cancelled = False
        rumps.Window.mock_response(rumps.Response(0, 'https://under.testing/update'))
        app.config.show_ui()
        assert app.config.is_cancelled

    def test_config_ui_save(self, app):
        app.mock_files({})
        rumps.Window.mock_response(rumps.Response(1, 'https://under.testing/update'))
        app.config.show_ui()
        assert app.get_mock_file(app.config.file_name) == '[timetracker]\nupdate_url = https://under.testing/update\n\n'

    def test_config_ui_invalid_udate_url(self, app):
        app.mock_files({})
        rumps.was_alert_shown = False
        rumps.shown_alert_message = ''
        rumps.Window.mock_response(rumps.Response(1, 'invalid_url://under.testing/update'))
        app.config.show_ui()
        assert rumps.was_alert_shown
        assert rumps.shown_alert_message == 'Unable to validate update URL. Please input a valid URL!'
        assert None == app.get_mock_file(app.config.file_name)

    def test_config_ui_quit(self, app):
        rumps.was_application_quit = False
        rumps.Window.mock_response(rumps.Response(2, 'https://under.testing/update'))
        app.config.show_ui()
        assert rumps.was_application_quit
