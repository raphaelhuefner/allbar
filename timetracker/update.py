import json
import os.path

import jsonschema
import modulegraph.zipio

class Validator():
    def __init__(self, logger=None):
        self._schema_json = None
        self._validator = None
        self._logger = logger

    def log(self, *args):
        if hasattr(self._logger, '__call__'):
            self._logger(*args)

    def get_schema_json(self):
        if not self._schema_json:
            file_name = os.path.join(os.path.dirname(__file__), 'json/update_schema.json')
            with modulegraph.zipio.open(file_name) as f:
                self._schema_json = f.read()
        return self._schema_json

    def get_schema(self):
        return json.loads(self.get_schema_json())

    def get_validator(self):
        if not self._validator:
            self._validator = jsonschema.Draft4Validator(
                self.get_schema(),
                format_checker=jsonschema.draft4_format_checker
            )
        return self._validator

    def is_valid(self, update):
        if isinstance(update, str):
            try:
                update = json.loads(update)
            except Exception as e:
                self.log(e)
                return False
        try:
            self.get_validator().validate(update)
            return True
        except Exception as e:
            self.log(e)
            return False
