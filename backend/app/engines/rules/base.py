from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RuleEvaluationResult:
    rule_name: str
    passed: bool
    explanation: str
    details: Dict[str, Any] | None = None


class BaseRule(ABC):
    """
    Abstract Base Class for domain rules.
    Rules deterministically screen packaging materials against commodity and storage constraints.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the rule."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable explanation of the rule's scientific principle."""
        pass

    @abstractmethod
    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any]
    ) -> RuleEvaluationResult:
        """
        Evaluate if a material candidate complies with the rule.
        """
        pass
