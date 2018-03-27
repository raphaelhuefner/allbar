
import timetracker.app
import timetracker.configuration
import timetracker.datastore

logger = None
# logger = print

app = timetracker.app.TimeTrackerStatusBarApp(logger=logger)

config = timetracker.configuration.TimeTrackerConfiguration(app, logger=logger)
app.set_config(config)

store = timetracker.datastore.TimeTrackerDataStore(logger=logger)
app.set_datastore(store)

app.run()
