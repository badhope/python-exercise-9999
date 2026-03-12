# -----------------------------
# 题目：医院挂号系统。
# 描述：实现科室管理、挂号、查询功能。
# -----------------------------

class Department:
    def __init__(self, dept_id, name):
        self.dept_id = dept_id
        self.name = name
        self.doctors = []

class Doctor:
    def __init__(self, doctor_id, name, title):
        self.doctor_id = doctor_id
        self.name = name
        self.title = title
        self.appointments = []

class Appointment:
    def __init__(self, patient_name, doctor, date):
        self.patient_name = patient_name
        self.doctor = doctor
        self.date = date
        self.status = "已预约"

class HospitalSystem:
    def __init__(self):
        self.departments = {}
        self.doctors = {}
    
    def add_department(self, dept_id, name):
        self.departments[dept_id] = Department(dept_id, name)
    
    def add_doctor(self, doctor_id, name, title, dept_id):
        doctor = Doctor(doctor_id, name, title)
        self.doctors[doctor_id] = doctor
        if dept_id in self.departments:
            self.departments[dept_id].doctors.append(doctor)
    
    def make_appointment(self, patient_name, doctor_id, date):
        if doctor_id in self.doctors:
            doctor = self.doctors[doctor_id]
            appointment = Appointment(patient_name, doctor, date)
            doctor.appointments.append(appointment)
            return appointment
        return None

def main():
    hospital = HospitalSystem()
    hospital.add_department("D001", "内科")
    hospital.add_doctor("DOC001", "王医生", "主任医师", "D001")
    appointment = hospital.make_appointment("张三", "DOC001", "2024-01-15")
    print(f"挂号成功: {appointment.patient_name} -> {appointment.doctor.name} ({appointment.date})")


if __name__ == "__main__":
    main()
