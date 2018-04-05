import urllib.request
import webbrowser

import pytest

from timetracker.app import TimeTrackerStatusBarApp
from timetracker.configuration import TimeTrackerConfiguration
from timetracker.datastore import TimeTrackerDataStore
from timetracker.update import is_valid as is_update_valid
from timetracker.utility import is_url_valid

import tests.mocks.rumps as rumps
import tests.mocks.urllib

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

    def get_minimal_update_json(self):
        return """
            {
                "ttl": 8,
                "indicators": ["a", "b"],
                "menu": [
                    {
                        "title": "Menu Item 1",
                        "url": "https://under.testing/menu-item-1",
                        "action": "get_url",
                        "active": false
                    },
                    {
                        "title": "Menu Item 2",
                        "url": "https://under.testing/menu-item-2",
                        "action": "post_url",
                        "active": false,
                        "prompt_title": "POST prompt title",
                        "prompt_message": "POST prompt message"
                    },
                    {
                        "title": "Menu Item 3",
                        "url": "https://under.testing/menu-item-3",
                        "action": "open_url",
                        "active": false
                    }
                ]
            }
        """

    def test_update_is_valid_accepts_schematic_json_string(self):
        assert is_update_valid(self.get_minimal_update_json())

    def test_update_is_valid_rejects_non_json_strings(self):
        assert not is_update_valid("Hello World!")

    def test_update_is_valid_rejects_unschematic_updates(self):
        assert not is_update_valid({"ttl":"invalid"})

    def test_datastore_corrupt_data_does_not_update(self, monkeypatch, app):
        monkeypatch.setattr(urllib.request, 'urlopen', tests.mocks.urllib.urlopen)
        app.datastore.set_update_url('https://under.testing/update')
        corrupt_responses = [
            tests.mocks.urllib.HTTPResponse(404, 'not found'),
            tests.mocks.urllib.HTTPResponse(200, '{"funny":"json"}'),
        ]
        for response in corrupt_responses:
            tests.mocks.urllib.mock_responses['https://under.testing/update'] = response
            assert [] == app.datastore.get_current_menu_settings()
            assert '0:00' == app.datastore.get_current_indicator()
            assert '0:00' == app.datastore.get_current_indicator()

    def test_datastore_updates(self, monkeypatch, app):
        new_data = self.get_minimal_update_json()
        tests.mocks.urllib.mock_responses['https://under.testing/update'] = tests.mocks.urllib.HTTPResponse(200, new_data)
        monkeypatch.setattr(urllib.request, 'urlopen', tests.mocks.urllib.urlopen)
        app.datastore.set_update_url('https://under.testing/update')
        expected_menu = [
            {
                "title": "Menu Item 1",
                "url": "https://under.testing/menu-item-1",
                "action": "get_url",
                "active": False
            },
            {
                "title": "Menu Item 2",
                "url": "https://under.testing/menu-item-2",
                "action": "post_url",
                "active": False,
                "prompt_title": "POST prompt title",
                "prompt_message": "POST prompt message"
            },
            {
                "title": "Menu Item 3",
                "url": "https://under.testing/menu-item-3",
                "action": "open_url",
                "active": False
            }
        ]
        assert expected_menu == app.datastore.get_current_menu_settings()
        app.datastore.current_indicator_index = 0
        assert 'b' == app.datastore.get_current_indicator()
        assert 'a' == app.datastore.get_current_indicator()
        assert 'b' == app.datastore.get_current_indicator()
        assert 'a' == app.datastore.get_current_indicator()

    def test_app_refreshes_with_new_data(self, monkeypatch, app):
        app.mock_files({
            app.config.file_name: """
                [timetracker]
                update_url=https://under.testing/update
            """
        })

        new_data = self.get_minimal_update_json()
        tests.mocks.urllib.mock_responses['https://under.testing/update'] = tests.mocks.urllib.HTTPResponse(200, new_data)
        monkeypatch.setattr(urllib.request, 'urlopen', tests.mocks.urllib.urlopen)

        app.refresh(None)
        assert 'b' == app.title
        assert 'https://under.testing/menu-item-1' == app.menu.mock_get_item(0).url
        assert 'https://under.testing/menu-item-2' == app.menu.mock_get_item(1).url
        assert 'https://under.testing/menu-item-3' == app.menu.mock_get_item(2).url

    def test_app_menu_callbacks(self, monkeypatch, app):
        app.mock_files({
            app.config.file_name: """
                [timetracker]
                update_url=https://under.testing/update
            """
        })

        new_data = self.get_minimal_update_json()
        tests.mocks.urllib.mock_responses['https://under.testing/update'] = tests.mocks.urllib.HTTPResponse(200, new_data)
        monkeypatch.setattr(urllib.request, 'urlopen', tests.mocks.urllib.urlopen)

        app.refresh(None)

        app.get_url(app.menu.mock_get_item(0))
        # assert ?

        app.post_url(app.menu.mock_get_item(1))
        # assert ?

        mock_new_tab_url = None
        def open_new_tab(url):
            nonlocal mock_new_tab_url
            mock_new_tab_url = url
        monkeypatch.setattr(webbrowser, 'open_new_tab', open_new_tab)
        app.open_url(app.menu.mock_get_item(2))
        assert 'https://under.testing/menu-item-3' == mock_new_tab_url

        app.preferences(None)
        # assert ?
