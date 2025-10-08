"""
Custom renderers and parsers for automatic case conversion
Converts between Django's snake_case and JavaScript's camelCase
"""

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import re


def camel_to_snake(name):
    """Convert camelCase to snake_case"""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def snake_to_camel(name):
    """Convert snake_case to camelCase"""
    if name.startswith("_"):
        return name
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_dict_keys(data, converter):
    """Recursively convert dictionary keys"""
    if isinstance(data, dict):
        return {
            converter(key): convert_dict_keys(value, converter)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [convert_dict_keys(item, converter) for item in data]
    else:
        return data


class CamelCaseJSONRenderer(JSONRenderer):
    """Renderer that converts snake_case to camelCase"""

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Convert keys to camelCase
        if data is not None:
            data = convert_dict_keys(data, snake_to_camel)
        return super().render(data, accepted_media_type, renderer_context)


class CamelCaseJSONParser(JSONParser):
    """Parser that converts camelCase to snake_case"""

    def parse(self, stream, media_type=None, parser_context=None):
        data = super().parse(stream, media_type, parser_context)
        # Convert keys to snake_case
        return convert_dict_keys(data, camel_to_snake)
