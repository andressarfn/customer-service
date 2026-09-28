from src.shared.exceptions import CustomHttpException


class NotFoundException(CustomHttpException):
    pass


class EmailAlreadyExistsException(CustomHttpException):
    pass
