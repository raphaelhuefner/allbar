import pytest

import timetracker.utility

from timetracker.app import TimeTrackerStatusBarApp
from timetracker.configuration import TimeTrackerConfiguration
from timetracker.datastore import TimeTrackerDataStore

class TestTimeTracker():

    def test_has_pytest(self):
        import sys
        assert 'pytest' in sys.modules

    def test_can_run(self):
        logger = None
        # logger = print

        app = TimeTrackerStatusBarApp(logger=logger)

        config = TimeTrackerConfiguration(app, logger=logger)
        app.set_config(config)

        store = TimeTrackerDataStore(logger=logger)
        app.set_datastore(store)

        app.run()
