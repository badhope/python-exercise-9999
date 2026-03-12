# -----------------------------
# 题目：实现客户关系管理系统。
# 描述：管理客户信息、跟进记录、销售机会等。
# -----------------------------

from datetime import datetime, date

class Customer:
    def __init__(self, customer_id, name, phone, email, company=""):
        self.id = customer_id
        self.name = name
        self.phone = phone
        self.email = email
        self.company = company
        self.level = "普通客户"
        self.source = ""
        self.created_at = datetime.now()
        self.follow_ups = []
        self.opportunities = []

class FollowUp:
    def __init__(self, follow_id, customer_id, content, next_action, operator):
        self.id = follow_id
        self.customer_id = customer_id
        self.content = content
        self.next_action = next_action
        self.operator = operator
        self.time = datetime.now()

class Opportunity:
    def __init__(self, opp_id, customer_id, name, amount, stage):
        self.id = opp_id
        self.customer_id = customer_id
        self.name = name
        self.amount = amount
        self.stage = stage
        self.probability = self._get_probability(stage)
        self.created_at = datetime.now()
    
    def _get_probability(self, stage):
        probabilities = {
            "初步接触": 10,
            "需求确认": 30,
            "方案报价": 50,
            "商务谈判": 70,
            "合同签订": 90,
            "成交": 100
        }
        return probabilities.get(stage, 0)

class CRMSystem:
    def __init__(self):
        self.customers = {}
        self.follow_ups = []
        self.opportunities = []
        self.next_customer_id = 1
        self.next_follow_id = 1
        self.next_opp_id = 1
    
    def add_customer(self, name, phone, email, company=""):
        customer = Customer(self.next_customer_id, name, phone, email, company)
        self.customers[self.next_customer_id] = customer
        self.next_customer_id += 1
        return customer.id
    
    def update_customer_level(self, customer_id, level):
        customer = self.customers.get(customer_id)
        if customer:
            customer.level = level
            return True
        return False
    
    def add_follow_up(self, customer_id, content, next_action, operator):
        customer = self.customers.get(customer_id)
        if customer:
            follow = FollowUp(self.next_follow_id, customer_id, content, next_action, operator)
            self.follow_ups.append(follow)
            customer.follow_ups.append(follow.id)
            self.next_follow_id += 1
            return follow.id
        return None
    
    def add_opportunity(self, customer_id, name, amount, stage):
        customer = self.customers.get(customer_id)
        if customer:
            opp = Opportunity(self.next_opp_id, customer_id, name, amount, stage)
            self.opportunities.append(opp)
            customer.opportunities.append(opp.id)
            self.next_opp_id += 1
            return opp.id
        return None
    
    def update_opportunity_stage(self, opp_id, stage):
        for opp in self.opportunities:
            if opp.id == opp_id:
                opp.stage = stage
                opp.probability = opp._get_probability(stage)
                return True
        return False
    
    def get_customer_info(self, customer_id):
        customer = self.customers.get(customer_id)
        if customer:
            return {
                'id': customer.id,
                'name': customer.name,
                'phone': customer.phone,
                'email': customer.email,
                'company': customer.company,
                'level': customer.level,
                'follow_up_count': len(customer.follow_ups),
                'opportunity_count': len(customer.opportunities)
            }
        return None
    
    def get_customer_follow_ups(self, customer_id):
        return [f for f in self.follow_ups if f.customer_id == customer_id]
    
    def get_customer_opportunities(self, customer_id):
        return [o for o in self.opportunities if o.customer_id == customer_id]
    
    def get_pipeline(self):
        pipeline = {}
        for opp in self.opportunities:
            if opp.stage not in pipeline:
                pipeline[opp.stage] = {'count': 0, 'amount': 0, 'weighted': 0}
            pipeline[opp.stage]['count'] += 1
            pipeline[opp.stage]['amount'] += opp.amount
            pipeline[opp.stage]['weighted'] += opp.amount * opp.probability / 100
        return pipeline
    
    def get_expected_revenue(self):
        return sum(o.amount * o.probability / 100 for o in self.opportunities)
    
    def search_customers(self, keyword):
        keyword = keyword.lower()
        return [c for c in self.customers.values() 
                if keyword in c.name.lower() or keyword in c.phone or 
                   keyword in c.company.lower()]
    
    def get_stats(self):
        return {
            'customers': len(self.customers),
            'follow_ups': len(self.follow_ups),
            'opportunities': len(self.opportunities),
            'expected_revenue': self.get_expected_revenue()
        }

def main():
    crm = CRMSystem()
    
    c1 = crm.add_customer("张三", "13800138000", "zhangsan@example.com", "ABC公司")
    c2 = crm.add_customer("李四", "13900139000", "lisi@example.com", "XYZ公司")
    
    crm.update_customer_level(c1, "VIP客户")
    
    crm.add_follow_up(c1, "电话沟通，了解需求", "发送产品资料", "销售员A")
    crm.add_follow_up(c2, "初次拜访", "安排产品演示", "销售员B")
    
    crm.add_opportunity(c1, "软件采购项目", 50000, "方案报价")
    crm.add_opportunity(c2, "年度服务合同", 100000, "初步接触")
    
    print("CRM系统统计:")
    stats = crm.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n销售漏斗:")
    pipeline = crm.get_pipeline()
    for stage, data in pipeline.items():
        print(f"  {stage}: {data['count']}个机会, 金额{data['amount']}元")


if __name__ == "__main__":
    main()
