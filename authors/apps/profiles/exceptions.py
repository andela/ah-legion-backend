from rest_framework.exceptions import APIException


class ProfileDoesNotExist(APIException):
    status_code = 400
    default_detail = 'The requested profile does not exist.'


class UserIsNotAuthenticated(APIException):
    status_code = 403
    default_detail = 'You should be logged in to proceed.'
