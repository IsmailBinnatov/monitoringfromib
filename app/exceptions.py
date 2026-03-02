from fastapi import HTTPException, status


def bad_request_exception_400(detail: str = "Bad request!"):
    """Throws a 400 bad request error with a message (detail)"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )


def credentials_exception_401(detail: str = "Could not validate credentials"):
    """Throws a 401 error when there are problems with the token or authorization"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_exception_403(detail: str = "Access denied"):
    """Throws a 403 error when permissions are insufficient (e.g., not a super admin)"""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def not_found_exception_404(item_name: str = "Item"):
    """Throws a 404 error if the record is not found in the database"""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{item_name} not found"
    )


def too_many_requests_429(detail: str):
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail
    )
