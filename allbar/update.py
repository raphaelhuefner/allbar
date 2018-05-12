"""Provide customized JSON validation."""

import json

import jsonschema

from allbar.utility import load_packaged_json_file


class Validator():
    """Wrap JSON validation from jsonschema module as needed for this app."""

    def __init__(self, logger=None):
        """Set up validator wrapper."""
        self._schema_json = None
        self._validator = None
        self._logger = logger

    def log(self, *args):
        """Log events in this class if configured.

        Defaults to no logging. (See __init__() for changing that.)
        """
        if hasattr(self._logger, '__call__'):
            self._logger(*args)

    def get_schema_json(self):
        """Load update data JSON schema from packaged JSON file."""
        if not self._schema_json:
            self._schema_json = load_packaged_json_file('update_schema.json')
        return self._schema_json

    def get_schema(self):
        """Load update data JSON schema as Python data structure."""
        return json.loads(self.get_schema_json())

    def get_validator(self):
        """Instantiate and cache JSON schema validator for our update data."""
        if not self._validator:
            self._validator = jsonschema.Draft4Validator(
                self.get_schema(),
                format_checker=jsonschema.draft4_format_checker
            )
        return self._validator

    def is_valid(self, update):
        """Validate an actual update data JSON payload."""
        if isinstance(update, str):
            # pylint: disable=broad-except
            # ^^ TODO determine list of possible exceptions and name them here.
            try:
                update = json.loads(update)
            except Exception as exception:
                self.log(exception)
                return False
        # pylint: disable=broad-except
        # ^^ TODO determine list of possible exceptions and name them here.
        try:
            self.get_validator().validate(update)
            return True
        except Exception as exception:
            self.log(exception)
            return False
