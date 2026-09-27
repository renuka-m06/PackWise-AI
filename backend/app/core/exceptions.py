"""
PackWise AI - Domain Exceptions & Structured Error Representations (Milestone M5)
Enforces consistent, audited error contracts without exposing stack traces or internals.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error classification code")
    message: str = Field(..., description="Human-readable error explanation")
    details: Dict[str, Any] = Field(default_factory=dict, description="Contextual error metadata")


class StructuredErrorResponse(BaseModel):
    error: ErrorDetail
    request_id: Optional[str] = Field(default=None, description="Correlation request ID for audit traceability")


class PackWiseAPIException(HTTPException):
    """Base structured exception for PackWise domain and operational failures."""
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.code = code
        self.error_message = message
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "code": self.code,
                "message": self.error_message,
                "details": self.details
            }
        )


class ResourceNotFoundException(PackWiseAPIException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} with identifier '{identifier}' was not found.",
            details={"resource": resource, "identifier": identifier}
        )


class ValidationRuleException(PackWiseAPIException):
    def __init__(self, rule_name: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="RULE_VALIDATION_ERROR",
            message=f"Rule validation failure: {reason}",
            details={"rule": rule_name, "reason": reason, **(details or {})}
        )


class DomainEngineNotImplementedException(PackWiseAPIException):
    def __init__(self, message: str = "Engine computation pending empirical dataset ingestion."):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            code="ENGINE_NOT_IMPLEMENTED",
            message=message,
            details={"policy": "Strict Zero Synthetic/Fake Data Policy"}
        )


class InvalidParameterException(PackWiseAPIException):
    def __init__(self, parameter: str, reason: str, value: Any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_PARAMETER",
            message=f"Invalid parameter '{parameter}': {reason}",
            details={"parameter": parameter, "reason": reason, "value": str(value)}
        )
