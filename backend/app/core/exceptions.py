from fastapi import HTTPException, status


class DomainEngineNotImplementedException(HTTPException):
    """
    Raised when an engine (ML inference, recommendation synthesis) is requested
    prior to empirical dataset ingestion, adhering strictly to zero fake-data policy.
    """
    def __init__(self, message: str = "Engine computation pending empirical dataset ingestion in Phase 1."):
        super().__init__(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": "EngineNotImplemented",
                "message": message,
                "milestone": "M0",
                "policy": "Strict Zero Synthetic/Fake Data Policy"
            }
        )


class ResourceNotFoundException(HTTPException):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ResourceNotFound",
                "message": f"{resource} with identifier '{identifier}' was not found."
            }
        )


class ValidationRuleException(HTTPException):
    def __init__(self, rule_name: str, reason: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "RuleValidationError",
                "rule": rule_name,
                "reason": reason
            }
        )
