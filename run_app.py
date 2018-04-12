
import productivityreminder.app
import productivityreminder.configuration
import productivityreminder.datastore

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


app = productivityreminder.app.ProductivityReminderStatusBarApp(logger=logger)

config = productivityreminder.configuration.ProductivityReminderConfiguration(app, logger=logger)
app.set_config(config)

store = productivityreminder.datastore.ProductivityReminderDataStore(logger=logger)
app.set_datastore(store)

# with app.open('productivityreminder.log', 'w') as logfile:
#     logging.set_logfile(logfile)
#     app.run(debug=True)

app.run()
