"""
Пользовательские исключения приложения
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseAppException(Exception):
    """Базовое исключение приложения"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(BaseAppException):
    """Ошибка - ресурс не найден"""
    pass


class ValidationError(BaseAppException):
    """Ошибка валидации данных"""
    pass


class AlreadyExistsError(BaseAppException):
    """Ошибка - ресурс уже существует"""
    pass


class DependencyExistsError(BaseAppException):
    """Ошибка - существуют зависимые ресурсы"""
    pass


# Функции для конвертации в HTTP исключения
def not_found_exception(message: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """Создает HTTP исключение 404"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "not_found",
            "message": message,
            "details": details or {}
        }
    )


def validation_exception(message: str, details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """Создает HTTP исключение 400"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "error": "validation_error",
            "message": message,
            "details": details or {}
        }
    )


def conflict_exception(message: str, error_type: str = "already_exists", details: Optional[Dict[str, Any]] = None) -> HTTPException:
    """Создает HTTP исключение 409"""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail={
            "error": error_type,
            "message": message,
            "details": details or {}
        }
    )


def internal_server_exception(message: str = "Internal server error") -> HTTPException:
    """Создает HTTP исключение 500"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "internal_error",
            "message": message
        }
    )
