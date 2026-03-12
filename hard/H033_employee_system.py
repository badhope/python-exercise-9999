# -----------------------------
# 题目：实现员工管理系统。
# 描述：管理员工信息、部门、考勤、薪资等。
# -----------------------------

from datetime import datetime, date

class Department:
    def __init__(self, dept_id, name):
        self.id = dept_id
        self.name = name
        self.manager_id = None
        self.employees = []

class Employee:
    def __init__(self, emp_id, name, dept_id, position, salary, hire_date):
        self.id = emp_id
        self.name = name
        self.dept_id = dept_id
        self.position = position
        self.salary = salary
        self.hire_date = hire_date
        self.status = "active"
        self.attendance = {}
    
    def get_years_of_service(self):
        today = date.today()
        return (today - self.hire_date).days // 365

class Attendance:
    def __init__(self, date, check_in=None, check_out=None):
        self.date = date
        self.check_in = check_in
        self.check_out = check_out
        self.status = "absent"
    
    def calculate_hours(self):
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            return delta.total_seconds() / 3600
        return 0

class Payroll:
    def __init__(self, payroll_id, emp_id, month, base_salary, bonus, deductions):
        self.id = payroll_id
        self.emp_id = emp_id
        self.month = month
        self.base_salary = base_salary
        self.bonus = bonus
        self.deductions = deductions
        self.net_salary = base_salary + bonus - deductions

class EmployeeSystem:
    def __init__(self):
        self.departments = {}
        self.employees = {}
        self.payrolls = {}
        self.next_dept_id = 1
        self.next_emp_id = 1
        self.next_payroll_id = 1
    
    def add_department(self, name):
        dept = Department(self.next_dept_id, name)
        self.departments[self.next_dept_id] = dept
        self.next_dept_id += 1
        return dept.id
    
    def add_employee(self, name, dept_id, position, salary, hire_date=None):
        if hire_date is None:
            hire_date = date.today()
        
        emp = Employee(self.next_emp_id, name, dept_id, position, salary, hire_date)
        self.employees[self.next_emp_id] = emp
        
        if dept_id in self.departments:
            self.departments[dept_id].employees.append(emp.id)
        
        self.next_emp_id += 1
        return emp.id
    
    def check_in(self, emp_id, check_time=None):
        emp = self.employees.get(emp_id)
        if emp and emp.status == "active":
            today = date.today()
            if today not in emp.attendance:
                if check_time is None:
                    check_time = datetime.now()
                emp.attendance[today] = Attendance(today, check_time)
                return True
        return False
    
    def check_out(self, emp_id, check_time=None):
        emp = self.employees.get(emp_id)
        if emp:
            today = date.today()
            if today in emp.attendance:
                if check_time is None:
                    check_time = datetime.now()
                emp.attendance[today].check_out = check_time
                emp.attendance[today].status = "present"
                return True
        return False
    
    def calculate_monthly_salary(self, emp_id, month, bonus=0, deductions=0):
        emp = self.employees.get(emp_id)
        if not emp:
            return None
        
        payroll = Payroll(self.next_payroll_id, emp_id, month, 
                         emp.salary, bonus, deductions)
        self.payrolls[self.next_payroll_id] = payroll
        self.next_payroll_id += 1
        return payroll.id
    
    def get_department_employees(self, dept_id):
        return [self.employees[eid] for eid in self.departments.get(dept_id, Department(0, "")).employees 
                if eid in self.employees]
    
    def get_employee_attendance(self, emp_id, month=None):
        emp = self.employees.get(emp_id)
        if emp:
            records = emp.attendance.values()
            if month:
                records = [r for r in records if r.date.month == month]
            return list(records)
        return []
    
    def get_employee_payroll(self, emp_id):
        return [p for p in self.payrolls.values() if p.emp_id == emp_id]
    
    def get_stats(self):
        return {
            'departments': len(self.departments),
            'employees': len(self.employees),
            'active_employees': sum(1 for e in self.employees.values() if e.status == "active"),
            'total_payrolls': len(self.payrolls)
        }

def main():
    system = EmployeeSystem()
    
    d1 = system.add_department("技术部")
    d2 = system.add_department("市场部")
    
    e1 = system.add_employee("张三", d1, "工程师", 15000, date(2020, 1, 15))
    e2 = system.add_employee("李四", d1, "经理", 20000, date(2019, 6, 1))
    e3 = system.add_employee("王五", d2, "销售", 10000, date(2021, 3, 10))
    
    system.check_in(e1)
    system.check_in(e2)
    system.check_out(e1)
    
    system.calculate_monthly_salary(e1, 1, bonus=2000, deductions=500)
    
    print("员工系统统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n技术部员工:")
    for emp in system.get_department_employees(d1):
        print(f"  {emp.name} - {emp.position} - 入职{emp.get_years_of_service()}年")


if __name__ == "__main__":
    main()
