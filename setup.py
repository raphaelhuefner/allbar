from setuptools import setup

APP = ['timetracker.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'],
}

setup(
    # name='MacOS Status Bar Time Tracker', # use with pypi
    name='Time Tracker', # use with py2app
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
