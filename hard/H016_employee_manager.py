# -----------------------------
# 题目：员工管理系统。
# 描述：实现员工信息管理系统，支持添加、删除、查询员工。
# -----------------------------

class Employee:
    def __init__(self, emp_id, name, department, salary):
        self.emp_id = emp_id
        self.name = name
        self.department = department
        self.salary = salary
    
    def __str__(self):
        return f"工号: {self.emp_id}, 姓名: {self.name}, 部门: {self.department}, 薪资: {self.salary}"

class EmployeeManager:
    def __init__(self):
        self.employees = {}
    
    def add_employee(self, employee):
        self.employees[employee.emp_id] = employee
    
    def remove_employee(self, emp_id):
        if emp_id in self.employees:
            del self.employees[emp_id]
            return True
        return False
    
    def find_employee(self, emp_id):
        return self.employees.get(emp_id)
    
    def list_by_department(self, department):
        return [emp for emp in self.employees.values() if emp.department == department]
    
    def total_salary(self):
        return sum(emp.salary for emp in self.employees.values())

def main():
    manager = EmployeeManager()
    manager.add_employee(Employee("E001", "张三", "技术部", 15000))
    manager.add_employee(Employee("E002", "李四", "市场部", 12000))
    manager.add_employee(Employee("E003", "王五", "技术部", 18000))
    print("技术部员工:")
    for emp in manager.list_by_department("技术部"):
        print(emp)
    print(f"总薪资: {manager.total_salary()}")


if __name__ == "__main__":
    main()
