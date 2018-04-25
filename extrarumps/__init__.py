import sys

if ('pytest' not in sys.modules):
    from rumps import (separator, debug_mode, alert, notification,
                        application_support, timers, quit_application, timer,
                        clicked, notifications, MenuItem, Timer, Window)
    from extrarumps.extrarumps import (App, )
else:
    from tests.mocks.rumps import *
