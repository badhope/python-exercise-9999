# -----------------------------
# 题目：实现规则引擎。
# 描述：支持规则定义、条件评估、动作执行。
# -----------------------------

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import re

class RuleStatus(Enum):
    ENABLED = "enabled"
    DISABLED = "disabled"

class Operator(Enum):
    EQ = "=="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    MATCHES = "matches"

@dataclass
class Condition:
    field: str
    operator: Operator
    value: Any
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        actual = self._get_field_value(context)
        
        if actual is None:
            return False
        
        if self.operator == Operator.EQ:
            return actual == self.value
        elif self.operator == Operator.NE:
            return actual != self.value
        elif self.operator == Operator.GT:
            return actual > self.value
        elif self.operator == Operator.GE:
            return actual >= self.value
        elif self.operator == Operator.LT:
            return actual < self.value
        elif self.operator == Operator.LE:
            return actual <= self.value
        elif self.operator == Operator.IN:
            return actual in self.value
        elif self.operator == Operator.NOT_IN:
            return actual not in self.value
        elif self.operator == Operator.CONTAINS:
            return self.value in actual
        elif self.operator == Operator.MATCHES:
            return bool(re.match(self.value, str(actual)))
        
        return False
    
    def _get_field_value(self, context: Dict[str, Any]) -> Any:
        keys = self.field.split('.')
        value = context
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

@dataclass
class Rule:
    rule_id: str
    name: str
    conditions: List[Condition]
    actions: List[Callable[[Dict], Any]]
    priority: int = 0
    status: RuleStatus = RuleStatus.ENABLED
    logical_operator: str = "AND"
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        if self.status == RuleStatus.DISABLED:
            return False
        
        results = [cond.evaluate(context) for cond in self.conditions]
        
        if self.logical_operator == "AND":
            return all(results)
        elif self.logical_operator == "OR":
            return any(results)
        
        return False
    
    def execute(self, context: Dict[str, Any]) -> List[Any]:
        results = []
        for action in self.actions:
            try:
                result = action(context)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        return results

class RuleGroup:
    def __init__(self, group_id: str, name: str):
        self.group_id = group_id
        self.name = name
        self.rules: List[Rule] = []
        self.logical_operator: str = "AND"
    
    def add_rule(self, rule: Rule):
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def evaluate(self, context: Dict[str, Any]) -> List[Rule]:
        matched_rules = []
        
        for rule in self.rules:
            if rule.evaluate(context):
                matched_rules.append(rule)
        
        return matched_rules

class RuleEngine:
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.groups: Dict[str, RuleGroup] = {}
        self._execution_log: List[Dict[str, Any]] = []
    
    def add_rule(self, rule: Rule):
        self.rules[rule.rule_id] = rule
    
    def add_group(self, group: RuleGroup):
        self.groups[group.group_id] = group
    
    def evaluate_rule(self, rule_id: str, context: Dict[str, Any]) -> bool:
        rule = self.rules.get(rule_id)
        if not rule:
            return False
        return rule.evaluate(context)
    
    def execute_rule(self, rule_id: str, context: Dict[str, Any]) -> List[Any]:
        rule = self.rules.get(rule_id)
        if not rule:
            return []
        return rule.execute(context)
    
    def evaluate_all(self, context: Dict[str, Any]) -> List[Rule]:
        matched = []
        for rule in sorted(self.rules.values(), key=lambda r: r.priority, reverse=True):
            if rule.evaluate(context):
                matched.append(rule)
        return matched
    
    def execute_all(self, context: Dict[str, Any]) -> Dict[str, List[Any]]:
        results = {}
        matched_rules = self.evaluate_all(context)
        
        for rule in matched_rules:
            results[rule.rule_id] = rule.execute(context)
            self._log_execution(rule, context)
        
        return results
    
    def evaluate_group(self, group_id: str, context: Dict[str, Any]) -> List[Rule]:
        group = self.groups.get(group_id)
        if not group:
            return []
        return group.evaluate(context)
    
    def _log_execution(self, rule: Rule, context: Dict[str, Any]):
        self._execution_log.append({
            'rule_id': rule.rule_id,
            'timestamp': __import__('time').time(),
            'context_keys': list(context.keys())
        })
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        return self._execution_log.copy()
    
    def create_rule_from_dict(self, data: Dict[str, Any]) -> Rule:
        conditions = []
        for cond_data in data.get('conditions', []):
            conditions.append(Condition(
                field=cond_data['field'],
                operator=Operator(cond_data['operator']),
                value=cond_data['value']
            ))
        
        actions = []
        for action_data in data.get('actions', []):
            if action_data.get('type') == 'set':
                actions.append(
                    lambda ctx, k=action_data['key'], v=action_data['value']: ctx.update({k: v})
                )
        
        return Rule(
            rule_id=data['rule_id'],
            name=data['name'],
            conditions=conditions,
            actions=actions,
            priority=data.get('priority', 0)
        )

def main():
    engine = RuleEngine()
    
    def discount_action(context):
        discount = context.get('discount', 0)
        new_discount = discount + 0.1
        context['discount'] = new_discount
        return f"应用10%折扣，当前折扣: {new_discount*100}%"
    
    def free_shipping_action(context):
        context['free_shipping'] = True
        return "免运费"
    
    rule1 = Rule(
        rule_id="vip_discount",
        name="VIP会员折扣",
        conditions=[
            Condition("user.level", Operator.EQ, "VIP"),
            Condition("order.amount", Operator.GE, 100)
        ],
        actions=[discount_action],
        priority=10
    )
    
    rule2 = Rule(
        rule_id="large_order_free_shipping",
        name="大额订单免运费",
        conditions=[
            Condition("order.amount", Operator.GE, 200)
        ],
        actions=[free_shipping_action],
        priority=5
    )
    
    rule3 = Rule(
        rule_id="new_user_bonus",
        name="新用户优惠",
        conditions=[
            Condition("user.is_new", Operator.EQ, True),
            Condition("order.amount", Operator.GT, 50)
        ],
        actions=[discount_action],
        priority=8
    )
    
    engine.add_rule(rule1)
    engine.add_rule(rule2)
    engine.add_rule(rule3)
    
    context1 = {
        'user': {'level': 'VIP', 'is_new': False},
        'order': {'amount': 150}
    }
    
    print("场景1: VIP用户，订单150元")
    matched = engine.evaluate_all(context1)
    print(f"匹配规则: {[r.name for r in matched]}")
    results = engine.execute_all(context1)
    print(f"执行结果: {results}")
    print(f"最终上下文: {context1}")
    
    context2 = {
        'user': {'level': '普通', 'is_new': True},
        'order': {'amount': 100}
    }
    
    print("\n场景2: 新用户，订单100元")
    matched = engine.evaluate_all(context2)
    print(f"匹配规则: {[r.name for r in matched]}")

if __name__ == "__main__":
    main()
