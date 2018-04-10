
import timetracker.app
import timetracker.configuration
import timetracker.datastore

class Logging():
    def __init__(self):
        self._file = None

    def set_logfile(self, file):
        self._file = file

    def log(self, *args):
        print(*args, file=self._file, flush=True)

# logging = Logging()
# logger = logging.log
# logger = print
logger = None


app = timetracker.app.TimeTrackerStatusBarApp(logger=logger)

config = timetracker.configuration.TimeTrackerConfiguration(app, logger=logger)
app.set_config(config)

store = timetracker.datastore.TimeTrackerDataStore(logger=logger)
app.set_datastore(store)

# with app.open('timetracker.log', 'w') as logfile:
#     logging.set_logfile(logfile)
#     app.run(debug=True)

app.run()
