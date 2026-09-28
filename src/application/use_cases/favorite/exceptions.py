from src.shared.exceptions import CustomHttpException


class FavoriteProductNotFoundError(CustomHttpException):
    pass


class FavoriteProductAlreadyExistsError(CustomHttpException):
    pass
