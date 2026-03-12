# -----------------------------
# 题目：组合模式实现组织架构管理。
# -----------------------------

class OrganizationComponent:
    def __init__(self, name):
        self.name = name
    
    def get_name(self):
        return self.name
    
    def get_salary(self):
        pass
    
    def display(self, indent=0):
        pass

class Employee(OrganizationComponent):
    def __init__(self, name, position, salary):
        super().__init__(name)
        self.position = position
        self.salary = salary
    
    def get_salary(self):
        return self.salary
    
    def display(self, indent=0):
        print("  " * indent + f"👤 {self.name} ({self.position}) - ¥{self.salary}")

class Department(OrganizationComponent):
    def __init__(self, name):
        super().__init__(name)
        self.members = []
    
    def add(self, component):
        self.members.append(component)
    
    def remove(self, component):
        if component in self.members:
            self.members.remove(component)
    
    def get_salary(self):
        return sum(member.get_salary() for member in self.members)
    
    def get_employee_count(self):
        count = 0
        for member in self.members:
            if isinstance(member, Employee):
                count += 1
            else:
                count += member.get_employee_count()
        return count
    
    def display(self, indent=0):
        print("  " * indent + f"🏢 {self.name}/")
        for member in self.members:
            member.display(indent + 1)
    
    def find_employee(self, name):
        for member in self.members:
            if isinstance(member, Employee) and member.name == name:
                return member
            elif isinstance(member, Department):
                result = member.find_employee(name)
                if result:
                    return result
        return None
    
    def get_employees_by_position(self, position):
        result = []
        for member in self.members:
            if isinstance(member, Employee) and member.position == position:
                result.append(member)
            elif isinstance(member, Department):
                result.extend(member.get_employees_by_position(position))
        return result

class Company:
    def __init__(self, name):
        self.name = name
        self.departments = []
    
    def add_department(self, department):
        self.departments.append(department)
    
    def get_total_salary(self):
        return sum(dept.get_salary() for dept in self.departments)
    
    def get_total_employees(self):
        return sum(dept.get_employee_count() for dept in self.departments)
    
    def display_structure(self):
        print(f"=== {self.name} 组织架构 ===")
        for dept in self.departments:
            dept.display()
    
    def find_employee(self, name):
        for dept in self.departments:
            result = dept.find_employee(name)
            if result:
                return result
        return None

def main():
    company = Company("科技有限公司")
    
    tech_dept = Department("技术部")
    tech_dept.add(Employee("张三", "技术总监", 50000))
    tech_dept.add(Employee("李四", "高级工程师", 30000))
    tech_dept.add(Employee("王五", "工程师", 20000))
    tech_dept.add(Employee("赵六", "工程师", 20000))
    
    frontend_team = Department("前端组")
    frontend_team.add(Employee("钱七", "前端组长", 25000))
    frontend_team.add(Employee("孙八", "前端工程师", 18000))
    tech_dept.add(frontend_team)
    
    product_dept = Department("产品部")
    product_dept.add(Employee("周九", "产品总监", 45000))
    product_dept.add(Employee("吴十", "产品经理", 25000))
    product_dept.add(Employee("郑十一", "产品助理", 15000))
    
    hr_dept = Department("人力资源部")
    hr_dept.add(Employee("王十二", "HR总监", 35000))
    hr_dept.add(Employee("冯十三", "HR专员", 12000))
    
    company.add_department(tech_dept)
    company.add_department(product_dept)
    company.add_department(hr_dept)
    
    company.display_structure()
    
    print(f"\n总员工数: {company.get_total_employees()}")
    print(f"总薪资: ¥{company.get_total_salary()}")
    
    print("\n=== 搜索员工 ===")
    emp = company.find_employee("李四")
    if emp:
        print(f"找到: {emp.name} - {emp.position}")
    
    print("\n=== 按职位筛选 ===")
    engineers = tech_dept.get_employees_by_position("工程师")
    for eng in engineers:
        print(f"  {eng.name}")


if __name__ == "__main__":
    main()
