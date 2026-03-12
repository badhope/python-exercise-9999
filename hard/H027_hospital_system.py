# -----------------------------
# 题目：实现医院挂号系统。
# 描述：管理科室、医生、预约挂号等功能。
# -----------------------------

from datetime import datetime, date, time

class Department:
    def __init__(self, dept_id, name):
        self.id = dept_id
        self.name = name
        self.doctors = []

class Doctor:
    def __init__(self, doctor_id, name, title, dept_id):
        self.id = doctor_id
        self.name = name
        self.title = title
        self.dept_id = dept_id
        self.schedule = {}

class Schedule:
    def __init__(self, schedule_id, doctor_id, date, time_slot, max_patients):
        self.id = schedule_id
        self.doctor_id = doctor_id
        self.date = date
        self.time_slot = time_slot
        self.max_patients = max_patients
        self.booked = 0
    
    def is_available(self):
        return self.booked < self.max_patients
    
    def book(self):
        if self.is_available():
            self.booked += 1
            return True
        return False
    
    def cancel(self):
        if self.booked > 0:
            self.booked -= 1
            return True
        return False

class Appointment:
    def __init__(self, appointment_id, patient_name, patient_phone, doctor_id, schedule_id):
        self.id = appointment_id
        self.patient_name = patient_name
        self.patient_phone = patient_phone
        self.doctor_id = doctor_id
        self.schedule_id = schedule_id
        self.status = "booked"
        self.created_at = datetime.now()

class HospitalSystem:
    def __init__(self):
        self.departments = {}
        self.doctors = {}
        self.schedules = {}
        self.appointments = {}
        self.next_dept_id = 1
        self.next_doctor_id = 1
        self.next_schedule_id = 1
        self.next_appointment_id = 1
    
    def add_department(self, name):
        dept = Department(self.next_dept_id, name)
        self.departments[self.next_dept_id] = dept
        self.next_dept_id += 1
        return dept.id
    
    def add_doctor(self, name, title, dept_id):
        doctor = Doctor(self.next_doctor_id, name, title, dept_id)
        self.doctors[self.next_doctor_id] = doctor
        
        if dept_id in self.departments:
            self.departments[dept_id].doctors.append(doctor.id)
        
        self.next_doctor_id += 1
        return doctor.id
    
    def add_schedule(self, doctor_id, schedule_date, time_slot, max_patients=20):
        schedule = Schedule(self.next_schedule_id, doctor_id, schedule_date, 
                           time_slot, max_patients)
        self.schedules[self.next_schedule_id] = schedule
        self.next_schedule_id += 1
        return schedule.id
    
    def get_doctors_by_dept(self, dept_id):
        return [self.doctors[did] for did in self.departments.get(dept_id, Department(0, "")).doctors 
                if did in self.doctors]
    
    def get_available_schedules(self, doctor_id, schedule_date=None):
        schedules = []
        for schedule in self.schedules.values():
            if schedule.doctor_id == doctor_id and schedule.is_available():
                if schedule_date is None or schedule.date == schedule_date:
                    schedules.append(schedule)
        return schedules
    
    def book_appointment(self, patient_name, patient_phone, schedule_id):
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return None, "排班不存在"
        
        if not schedule.book():
            return None, "号源已满"
        
        appointment = Appointment(self.next_appointment_id, patient_name, 
                                 patient_phone, schedule.doctor_id, schedule_id)
        self.appointments[self.next_appointment_id] = appointment
        self.next_appointment_id += 1
        
        return appointment.id, f"挂号成功，预约号: {schedule.booked}"
    
    def cancel_appointment(self, appointment_id):
        appointment = self.appointments.get(appointment_id)
        if not appointment:
            return False, "预约不存在"
        
        if appointment.status != "booked":
            return False, "预约已取消或已完成"
        
        schedule = self.schedules.get(appointment.schedule_id)
        if schedule:
            schedule.cancel()
        
        appointment.status = "cancelled"
        return True, "取消成功"
    
    def get_patient_appointments(self, patient_phone):
        return [a for a in self.appointments.values() 
                if a.patient_phone == patient_phone and a.status == "booked"]
    
    def get_stats(self):
        return {
            'departments': len(self.departments),
            'doctors': len(self.doctors),
            'total_schedules': len(self.schedules),
            'total_appointments': len(self.appointments),
            'active_appointments': sum(1 for a in self.appointments.values() 
                                      if a.status == "booked")
        }

def main():
    hospital = HospitalSystem()
    
    d1 = hospital.add_department("内科")
    d2 = hospital.add_department("外科")
    
    doc1 = hospital.add_doctor("王医生", "主任医师", d1)
    doc2 = hospital.add_doctor("李医生", "副主任医师", d2)
    
    today = date.today()
    hospital.add_schedule(doc1, today, "上午", 20)
    hospital.add_schedule(doc1, today, "下午", 15)
    hospital.add_schedule(doc2, today, "上午", 10)
    
    a1, _ = hospital.book_appointment("张三", "13800138000", 1)
    a2, _ = hospital.book_appointment("李四", "13900139000", 1)
    
    print("医院统计:")
    stats = hospital.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\n医生{doc1}可用排班:")
    schedules = hospital.get_available_schedules(doc1)
    for s in schedules:
        print(f"  {s.date} {s.time_slot}: 剩余{s.max_patients - s.booked}号")


if __name__ == "__main__":
    main()
