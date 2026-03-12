# -----------------------------
# 题目：实现规则引擎。
# -----------------------------

from enum import Enum
import re

class RuleType(Enum):
    EQUAL = "=="
    NOT_EQUAL = "!="
    GREATER = ">"
    LESS = "<"
    CONTAINS = "contains"
    MATCHES = "matches"

class Rule:
    def __init__(self, field, rule_type, value, action=None):
        self.field = field
        self.rule_type = rule_type
        self.value = value
        self.action = action
    
    def evaluate(self, context):
        field_value = context.get(self.field)
        
        if self.rule_type == RuleType.EQUAL:
            return field_value == self.value
        elif self.rule_type == RuleType.NOT_EQUAL:
            return field_value != self.value
        elif self.rule_type == RuleType.GREATER:
            return field_value > self.value
        elif self.rule_type == RuleType.LESS:
            return field_value < self.value
        elif self.rule_type == RuleType.CONTAINS:
            return self.value in field_value
        elif self.rule_type == RuleType.MATCHES:
            return bool(re.match(self.value, str(field_value)))
        return False

class RuleEngine:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule):
        self.rules.append(rule)
    
    def evaluate(self, context):
        for rule in self.rules:
            if rule.evaluate(context):
                if rule.action:
                    rule.action(context)
                return True
        return False
    
    def evaluate_all(self, context):
        results = []
        for rule in self.rules:
            result = rule.evaluate(context)
            results.append((rule, result))
        return results

def discount_action(context):
    context["discount"] = 0.1
    print("10% discount applied!")

if __name__ == "__main__":
    engine = RuleEngine()
    
    engine.add_rule(Rule("age", RuleType.GREATER, 60, discount_action))
    engine.add_rule(Rule("membership", RuleType.EQUAL, "gold", discount_action))
    
    context1 = {"age": 65, "name": "John"}
    engine.evaluate(context1)
    print(f"Context1: {context1}")
    
    context2 = {"age": 30, "membership": "gold", "name": "Jane"}
    engine.evaluate(context2)
    print(f"Context2: {context2}")
