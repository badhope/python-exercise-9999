# -----------------------------
# 题目：实现规则引擎。
# -----------------------------

from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum

class Operator(Enum):
    EQ = "=="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    IN = "in"
    NOT_IN = "not in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"

@dataclass
class Condition:
    field: str
    operator: Operator
    value: Any

@dataclass
class Rule:
    name: str
    conditions: List[Condition]
    action: Callable
    priority: int = 0
    enabled: bool = True

class RuleEngine:
    def __init__(self):
        self.rules: List[Rule] = []
    
    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def remove_rule(self, name: str):
        self.rules = [r for r in self.rules if r.name != name]
    
    def evaluate(self, context: Dict[str, Any]) -> List[Any]:
        results = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_conditions(rule.conditions, context):
                result = rule.action(context)
                results.append((rule.name, result))
        
        return results
    
    def evaluate_first(self, context: Dict[str, Any]) -> Optional[Any]:
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            if self._evaluate_conditions(rule.conditions, context):
                return rule.action(context)
        
        return None
    
    def _evaluate_conditions(self, conditions: List[Condition], context: Dict[str, Any]) -> bool:
        for condition in conditions:
            if not self._evaluate_condition(condition, context):
                return False
        return True
    
    def _evaluate_condition(self, condition: Condition, context: Dict[str, Any]) -> bool:
        field_value = self._get_field_value(condition.field, context)
        
        if condition.operator == Operator.EQ:
            return field_value == condition.value
        elif condition.operator == Operator.NE:
            return field_value != condition.value
        elif condition.operator == Operator.GT:
            return field_value > condition.value
        elif condition.operator == Operator.GE:
            return field_value >= condition.value
        elif condition.operator == Operator.LT:
            return field_value < condition.value
        elif condition.operator == Operator.LE:
            return field_value <= condition.value
        elif condition.operator == Operator.IN:
            return field_value in condition.value
        elif condition.operator == Operator.NOT_IN:
            return field_value not in condition.value
        elif condition.operator == Operator.CONTAINS:
            return condition.value in str(field_value)
        elif condition.operator == Operator.STARTS_WITH:
            return str(field_value).startswith(condition.value)
        elif condition.operator == Operator.ENDS_WITH:
            return str(field_value).endswith(condition.value)
        
        return False
    
    def _get_field_value(self, field: str, context: Dict[str, Any]) -> Any:
        keys = field.split('.')
        value = context
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value

class RuleBuilder:
    def __init__(self, name: str):
        self.name = name
        self.conditions: List[Condition] = []
        self.action: Callable = None
        self.priority: int = 0
    
    def when(self, field: str, operator: Operator, value: Any) -> 'RuleBuilder':
        self.conditions.append(Condition(field, operator, value))
        return self
    
    def then(self, action: Callable) -> 'RuleBuilder':
        self.action = action
        return self
    
    def with_priority(self, priority: int) -> 'RuleBuilder':
        self.priority = priority
        return self
    
    def build(self) -> Rule:
        return Rule(
            name=self.name,
            conditions=self.conditions,
            action=self.action,
            priority=self.priority
        )

class RuleSet:
    def __init__(self, name: str):
        self.name = name
        self.rules: List[Rule] = []
    
    def add(self, rule: Rule):
        self.rules.append(rule)
    
    def evaluate(self, context: Dict[str, Any]) -> List[Any]:
        engine = RuleEngine()
        for rule in self.rules:
            engine.add_rule(rule)
        return engine.evaluate(context)

def main():
    print("=== 创建规则引擎 ===")
    engine = RuleEngine()
    
    rule1 = (RuleBuilder("VIP折扣规则")
             .when("user.level", Operator.EQ, "VIP")
             .when("order.amount", Operator.GE, 1000)
             .then(lambda ctx: {"discount": 0.8, "message": "VIP用户享受8折优惠"})
             .with_priority(10)
             .build())
    
    rule2 = (RuleBuilder("普通折扣规则")
             .when("order.amount", Operator.GE, 500)
             .then(lambda ctx: {"discount": 0.9, "message": "满500享9折"})
             .with_priority(5)
             .build())
    
    rule3 = (RuleBuilder("新用户优惠")
             .when("user.is_new", Operator.EQ, True)
             .then(lambda ctx: {"discount": 0.85, "message": "新用户首单85折"})
             .with_priority(8)
             .build())
    
    engine.add_rule(rule1)
    engine.add_rule(rule2)
    engine.add_rule(rule3)
    
    print("\n=== 测试VIP用户 ===")
    context = {
        "user": {"level": "VIP", "is_new": False},
        "order": {"amount": 1500}
    }
    results = engine.evaluate(context)
    for name, result in results:
        print(f"  {name}: {result}")
    
    print("\n=== 测试新用户 ===")
    context = {
        "user": {"level": "普通", "is_new": True},
        "order": {"amount": 300}
    }
    results = engine.evaluate(context)
    for name, result in results:
        print(f"  {name}: {result}")
    
    print("\n=== 测试普通用户大额订单 ===")
    context = {
        "user": {"level": "普通", "is_new": False},
        "order": {"amount": 800}
    }
    results = engine.evaluate(context)
    for name, result in results:
        print(f"  {name}: {result}")


if __name__ == "__main__":
    main()
