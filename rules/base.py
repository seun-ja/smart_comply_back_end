from dataclasses import dataclass


@dataclass
class RuleResult:
    triggered: bool

    score: int

    severity: str

    message: str

    rule_name: str


class Rule:
    def evaluate(self, transaction):
        raise NotImplementedError
