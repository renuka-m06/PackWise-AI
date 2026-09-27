import os
import json
from typing import Dict, Any, Optional

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CONFIG_DIR, "config", "rules_config.json")


class RuleConfigRegistry:
    """
    Singleton-style accessor for the rule configuration registry.
    Ensures scientific thresholds and sources are never hardcoded.
    """
    _instance: Optional["RuleConfigRegistry"] = None

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or CONFIG_FILE
        self._config_data: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"version": "m2.0.0", "rules": {}}

    @classmethod
    def get_instance(cls) -> "RuleConfigRegistry":
        if cls._instance is None:
            cls._instance = RuleConfigRegistry()
        return cls._instance

    @property
    def version(self) -> str:
        return self._config_data.get("version", "m2.0.0")

    def get_rule_def(self, rule_id: str) -> Dict[str, Any]:
        return self._config_data.get("rules", {}).get(rule_id, {})

    def get_parameter(self, rule_id: str, param_name: str, default: Any = None) -> Any:
        rule = self.get_rule_def(rule_id)
        return rule.get("parameters", {}).get(param_name, default)


def get_rule_config() -> RuleConfigRegistry:
    return RuleConfigRegistry.get_instance()
