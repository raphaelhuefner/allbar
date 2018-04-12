from setuptools import setup

APP = ['run_app.py']
DATA_FILES = []
PY2APP_OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'],
}

setup(
    # name='MacOS Status Bar Productivity Reminder', # use with pypi
    name='Productivity Reminder', # use with py2app
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': PY2APP_OPTIONS},
    setup_requires=['py2app'],
    package_data={
        'productivityreminder': ['json/*.json']
    }
)
