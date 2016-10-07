import datetime
from json import dumps, loads, JSONEncoder, JSONDecoder
import pickle

# Stolen from http://stackoverflow.com/questions/8230315/python-sets-are-not-json-serializable
class PythonObjectEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
            return JSONEncoder.default(self, obj)
        elif isinstance(obj, datetime.datetime):
            # We should be returning an .isoformat() and then
            # pretty printing it on the other side, but life is too short.
            return obj.strftime("%d-%b-%Y %I:%M%p")
        return {'_python_object': pickle.dumps(obj)}

def as_python_object(dct):
    if '_python_object' in dct:
        return pickle.loads(str(dct['_python_object']))
    return dct
