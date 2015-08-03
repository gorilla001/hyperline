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
class ValidatedError(Exception):
    """Validate error"""

def validate_format():
    """
    Validator message format
    """
    def _do(msg):
        if 'type' not in set(msg):
            return False
        return True

    return _do

def validate_int(val):
    """
    Validate int value

    FIXME: If it is better to implemented this method as a decorator?
    """
    # def _do(val):
    #     if not isinstance(val, int):
    #         return False
    #
    #     return True
    #
    # return _do
    if not isinstance(val, int):
        raise ValidatedError(val)


def validate_str(val):
    """
    Validate str value

    FIXME: If it is better to implemented this method as a decorator?
    """
    # def _do(val):
    #     if not isinstance(val, six.string_types):
    #         return False
    #
    #     return True
    # return _do
    if not isinstance(val, six.string_types):
        raise ValidatedError(val)

if __name__ == '__main__':
    validate_int('test must be integer')
