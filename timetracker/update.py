import json

import jsonschema

def get_schema_json():
    return """
        {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "title": "Update Record",
            "description": "macOS Status Bar Time Tracker Update Record.",
            "type": "object",
            "properties": {
                "ttl": {
                    "title": "Time To Live",
                    "description": "The time this data is valid for in seconds.",
                    "type": "integer",
                    "minimum": 0
                },
                "indicators": {
                    "title": "Status Bar Indicator Strings",
                    "description": "A list of strings to show in the status bar. Rotated 1 per second.",
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string"
                    }
                },
                "menu": {
                    "title": "Menu Items",
                    "description": "The list of menu items to show. Without 'Preferences' nor 'Quit', those are hard-coded.",
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string"
                            },
                            "url": {
                                "type": "string",
                                "format": "uri"
                            },
                            "action": {
                                "type": "string",
                                "enum": ["get_url", "open_url", "post_url"]
                            },
                            "active": {
                                "type": "boolean"
                            },
                            "prompt_title": {
                                "type": "string"
                            },
                            "prompt_message": {
                                "type": "string"
                            }
                        },
                        "required": ["title", "url", "action", "active"],
                        "dependencies": {
                            "prompt_title": {
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "enum": ["post_url"]
                                    }
                                },
                                "required": ["prompt_message"]
                            },
                            "prompt_message": {
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "enum": ["post_url"]
                                    }
                                },
                                "required": ["prompt_title"]
                            }
                        }                            
                    }
                }
            },
            "required": ["ttl", "indicators", "menu"]
        }
    """


def get_schema():
    return json.loads(get_schema_json())


def is_valid(update):
    if isinstance(update, str):
        try:
            update = json.loads(update)
        except Exception:
            return False
    validator = jsonschema.Draft4Validator(get_schema(), format_checker=jsonschema.draft4_format_checker)
    try:
        validator.validate(update)
        return True
    except Exception:
        return False
