from rest_framework.exceptions import APIException
from rest_framework import status


class Error(APIException):
    status_code = 250
    default_detail = '执行出错！'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        super().__init__(detail, code)
