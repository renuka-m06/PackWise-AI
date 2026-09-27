from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RuleSeverity(str, Enum):
    HARD = "HARD"
    SOFT = "SOFT"


class RuleStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class RuleCategory(str, Enum):
    DATA_VALIDITY = "DATA_VALIDITY"
    SAFETY = "SAFETY"
    STORAGE = "STORAGE"
    BARRIER = "BARRIER"
    MATERIAL = "MATERIAL"
    MAP = "MAP"
    COMPATIBILITY = "COMPATIBILITY"


@dataclass
class RuleEvaluationResult:
    """
    Standardized, explainable evaluation result emitted by every rule.
    Supports evidence graph reconstruction and deterministic audit trails.
    """
    rule_id: str
    rule_name: str
    rule_category: str
    status: str  # PASS, FAIL, INSUFFICIENT_DATA
    severity: str  # HARD, SOFT
    passed: bool  # True only if status == "PASS"
    observed_value: Any = None
    required_value: Any = None
    unit: Optional[str] = None
    source_id: str = "DERIVED_ENGINEERING_RULE"
    scientific_basis: str = ""
    reason: str = ""
    explanation: str = ""
    details: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.explanation and self.reason:
            self.explanation = self.reason
        elif not self.reason and self.explanation:
            self.reason = self.explanation


class BaseRule(ABC):
    """
    Abstract Base Class for all scientific and engineering rules.
    Every rule must be deterministic, explainable, testable, and source-aware.
    """
    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier (e.g. RULE-SAF-001)."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the rule."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Rule category (RuleCategory enum)."""
        pass

    @property
    @abstractmethod
    def severity(self) -> str:
        """HARD (causes rejection) or SOFT (score modifier)."""
        pass

    @property
    @abstractmethod
    def source_id(self) -> str:
        """Primary provenance source ID or DERIVED_ENGINEERING_RULE."""
        pass

    @property
    @abstractmethod
    def scientific_basis(self) -> str:
        """Summary of the underlying physical, biochemical, or statutory standard."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Concise statement of what this rule verifies."""
        pass

    @property
    def input_fields(self) -> List[str]:
        """Fields evaluated by this rule."""
        return []

    @abstractmethod
    def evaluate(
        self,
        commodity: Dict[str, Any],
        material: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Optional[Any] = None
    ) -> RuleEvaluationResult:
        """
        Evaluate if a material candidate complies with the rule given commodity and storage contexts.
        """
        pass
