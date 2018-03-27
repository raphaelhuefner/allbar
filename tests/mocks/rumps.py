
def alert():
    pass


def quit_application():
    pass


# this is a decorator
def timer(interval):
    def wrapping(func):
        secs = interval
        # pretend to register func as a callback in a timer
        return func
    return wrapping


class App():
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

    def open(self, *args):
        pass

    def run(self):
        pass


class Menu():
    def __init__(self):
        pass

    def clear(self):
        pass

    def add(self, iterable):
        pass

    def update(self, iterable):
        pass


class MenuItem():
    def __init__(self, title, callback):
        self.title = title
        self.callback = callback


class Window():
    def __init__(self):
        pass

    def add_button(self, name):
        pass

    def run(self):
        return Response(0, '')
        pass


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

