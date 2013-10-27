class UserException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


#main
class ArgumentsError(UserException):
    """
    Raised when no arguments provided by user
    """
    pass


#HyperDex
class NoSpaceSelected(UserException):
    pass


class InvalidSpaceDefinition(UserException):
    pass