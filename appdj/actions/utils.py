import json


class SkipJSONEncoder(json.JSONEncoder):
    def default(self, obj): # pyltint: disable=arguments-differ
        try:
            return super().default(obj)
        except TypeError:
            return None
