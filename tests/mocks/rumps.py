import contextlib
import io

was_alert_shown = False
shown_alert_message = ''

def alert(message):
    global was_alert_shown, shown_alert_message
    was_alert_shown = True
    shown_alert_message = message


was_application_quit = False


def quit_application():
    global was_application_quit
    was_application_quit = True


# this is a decorator
def timer(interval):
    def wrapping(func):
        secs = interval
        # pretend to register func as a callback in a timer
        return func
    return wrapping


@contextlib.contextmanager
def mock_file_context(stringio, pre_closing_callback, *callback_args):
    try:
        yield stringio
    finally:
        pre_closing_callback(stringio.getvalue(), *callback_args)
        stringio.close()


class App():
    _files = {}

    def __init__(self, name, title=None):
        self._menu = Menu()
        self._title = title
        pass

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, iterable):
        self._menu.update(iterable)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @classmethod
    def mock_files(cls, files):
        cls._files = files

    @classmethod
    def get_mock_file(cls, file_name):
        return cls._files[file_name] if file_name in cls._files else None

    def open(self, file_name, mode):
        if 'r' == mode:
            if file_name in self._files:
                file_contents = self._files[file_name]
                return contextlib.closing(io.StringIO(file_contents))
            else:
                msg = "[Errno 2] No such file or directory: '{file_name}'"
                raise FileNotFoundError(msg.format(file_name=file_name))
        elif 'w' == mode:
            def callback(new_file_contents, file_name, files):
                files[file_name] = new_file_contents
            return mock_file_context(io.StringIO(''), callback, file_name, self._files)
        else:
            raise ValueError('Unsupported mock file mode "{mode}".'.format(mode=mode))

    def run(self):
        pass


class MenuItem():
    def __init__(self, title, callback):
        self.title = title
        self.callback = callback


class Menu():
    def __init__(self):
        self.clear()

    def clear(self):
        self._items = []

    def add(self, item):
        self._items.append(item)
        pass

    def update(self, iterable):
        self.clear()
        if isinstance(iterable, MenuItem):
            self.add(iterable)
        else:
            for item in iterable:
                self.add(item)

    def mock_get_item(self, index):
        return self._items[index]


class Response():
    def __init__(self, clicked, text):
        self._clicked = int(clicked)
        self._text = str(text)

    @property
    def clicked(self):
        return self._clicked

    @property
    def text(self):
        return self._text


class Window():
    _response = Response(0, '')

    def __init__(self, message='', title='', default_text='', ok=None, cancel=None, dimensions=(320, 160)):
        pass

    def add_button(self, name):
        pass

    @classmethod
    def mock_response(cls, response):
        cls._response = response

    def run(self):
        return self._response
        pass

