from fastapi.exceptions import HTTPException


class UserBaseException(HTTPException):
    def __init__(
        self,
        detail: str = "User error",
        status_code: int = 400,
        email: str = None,
    ):
        if email:
            detail = f"User with email {email}, {detail}"
        super().__init__(status_code=status_code, detail=detail)


class UserNotFoundException(UserBaseException):
    def __init__(self, detail: str = "User not found", email: str = None):
        super().__init__(status_code=404, detail=detail, email=email)


class UserInactiveException(UserBaseException):
    def __init__(self, detail: str = "User is inactive", email: str = None):
        super().__init__(status_code=401, detail=detail, email=email)


class UserNotSuperuserException(UserBaseException):
    def __init__(
        self, detail: str = "User is not a superuser", email: str = None
    ):
        super().__init__(status_code=403, detail=detail, email=email)


class UserWrongPasswordException(UserBaseException):
    def __init__(self, detail: str = "Wrong password", email: str = None):
        super().__init__(status_code=401, detail=detail, email=email)
