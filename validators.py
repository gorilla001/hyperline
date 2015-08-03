__author__ = 'nmg'

import six
# def validate_json():
#     """
#     If message is json object, return True; else return False.
#     """
#
#     def _do(msg):
#         try:
#             e = json.loads(message)  # message is json object
#         except ValueError:
#             return False
#         return True
def validate_format():
    """
    Validator message format
    """
    def _do(msg):
        if 'type' not in set(msg):
            return False
        return True

    return _do

def validate_int():
    """
    Validate int value
    """
    def _do(val):
        if not isinstance(val, int):
            return False

        return True

    return _do

def validate_str():
    """
    Validate str value
    """
    def _do(val):
        if not isinstance(val, six.string_types):
            return False

        return True
    return _do

