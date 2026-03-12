# -----------------------------
# 题目：实现简单的预约系统。
# 描述：管理预约时间槽和预约记录。
# -----------------------------

from datetime import datetime, date, time, timedelta

class TimeSlot:
    def __init__(self, slot_id, start_time, end_time):
        self.id = slot_id
        self.start_time = start_time
        self.end_time = end_time
        self.is_booked = False
        self.booked_by = None
    
    def book(self, user_id):
        if self.is_booked:
            return False
        self.is_booked = True
        self.booked_by = user_id
        return True
    
    def cancel(self):
        self.is_booked = False
        self.booked_by = None

class Appointment:
    def __init__(self, appointment_id, user_id, slot_id, date, note=""):
        self.id = appointment_id
        self.user_id = user_id
        self.slot_id = slot_id
        self.date = date
        self.note = note
        self.status = "confirmed"
        self.created_at = datetime.now()

class AppointmentSystem:
    def __init__(self):
        self.slots = {}
        self.appointments = {}
        self.next_slot_id = 1
        self.next_appointment_id = 1
    
    def add_slot(self, start_time, end_time):
        slot = TimeSlot(self.next_slot_id, start_time, end_time)
        self.slots[self.next_slot_id] = slot
        self.next_slot_id += 1
        return slot.id
    
    def get_available_slots(self, target_date):
        available = []
        for slot in self.slots.values():
            if not slot.is_booked:
                available.append(slot)
        return available
    
    def book_appointment(self, user_id, slot_id, target_date, note=""):
        slot = self.slots.get(slot_id)
        if not slot:
            return None, "时间段不存在"
        
        if slot.is_booked:
            return None, "时间段已被预约"
        
        slot.book(user_id)
        
        appointment = Appointment(
            self.next_appointment_id,
            user_id,
            slot_id,
            target_date,
            note
        )
        self.appointments[self.next_appointment_id] = appointment
        self.next_appointment_id += 1
        
        return appointment.id, "预约成功"
    
    def cancel_appointment(self, appointment_id):
        appointment = self.appointments.get(appointment_id)
        if not appointment:
            return False, "预约不存在"
        
        slot = self.slots.get(appointment.slot_id)
        if slot:
            slot.cancel()
        
        appointment.status = "cancelled"
        return True, "取消成功"
    
    def get_user_appointments(self, user_id):
        return [
            a for a in self.appointments.values()
            if a.user_id == user_id and a.status == "confirmed"
        ]
    
    def get_appointments_by_date(self, target_date):
        return [
            a for a in self.appointments.values()
            if a.date == target_date and a.status == "confirmed"
        ]
    
    def get_stats(self):
        total_slots = len(self.slots)
        booked_slots = sum(1 for s in self.slots.values() if s.is_booked)
        total_appointments = len(self.appointments)
        
        return {
            'total_slots': total_slots,
            'booked_slots': booked_slots,
            'available_slots': total_slots - booked_slots,
            'total_appointments': total_appointments
        }

def main():
    system = AppointmentSystem()
    
    system.add_slot(time(9, 0), time(10, 0))
    system.add_slot(time(10, 0), time(11, 0))
    system.add_slot(time(11, 0), time(12, 0))
    system.add_slot(time(14, 0), time(15, 0))
    
    today = date.today()
    
    appt1, _ = system.book_appointment("user1", 1, today, "体检")
    appt2, _ = system.book_appointment("user2", 2, today, "咨询")
    
    print("预约统计:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n可用时间段:")
    for slot in system.get_available_slots(today):
        print(f"  {slot.start_time} - {slot.end_time}")


if __name__ == "__main__":
    main()
