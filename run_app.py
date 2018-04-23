
import allbar.app
import allbar.configuration
import allbar.datastore

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


app = allbar.app.AllBarApp(logger=logger)

config = allbar.configuration.AllBarConfiguration(app, logger=logger)
app.set_config(config)

store = allbar.datastore.AllBarDataStore(logger=logger)
app.set_datastore(store)

# with app.open('allbar.log', 'w') as logfile:
#     logging.set_logfile(logfile)
#     app.run(debug=True)

app.run()
