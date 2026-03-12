# -----------------------------
# 题目：实现简单的地址簿。
# 描述：管理联系人信息。
# -----------------------------

from datetime import datetime
import re

class Contact:
    def __init__(self, contact_id, name, phone="", email="", address=""):
        self.id = contact_id
        self.name = name
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AddressBook:
    def __init__(self):
        self.contacts = {}
        self.next_id = 1
    
    def add(self, name, phone="", email="", address=""):
        if not self._validate_phone(phone) and phone:
            return None, "无效的电话号码"
        if not self._validate_email(email) and email:
            return None, "无效的邮箱地址"
        
        contact = Contact(self.next_id, name, phone, email, address)
        self.contacts[self.next_id] = contact
        self.next_id += 1
        return contact.id, "添加成功"
    
    def _validate_phone(self, phone):
        if not phone:
            return True
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
    
    def _validate_email(self, email):
        if not email:
            return True
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def get(self, contact_id):
        return self.contacts.get(contact_id)
    
    def update(self, contact_id, **kwargs):
        contact = self.contacts.get(contact_id)
        if contact:
            if 'phone' in kwargs and not self._validate_phone(kwargs['phone']):
                return False, "无效的电话号码"
            if 'email' in kwargs and not self._validate_email(kwargs['email']):
                return False, "无效的邮箱地址"
            contact.update(**kwargs)
            return True, "更新成功"
        return False, "联系人不存在"
    
    def delete(self, contact_id):
        if contact_id in self.contacts:
            del self.contacts[contact_id]
            return True
        return False
    
    def search(self, keyword):
        results = []
        keyword = keyword.lower()
        for contact in self.contacts.values():
            if (keyword in contact.name.lower() or
                keyword in contact.phone or
                keyword in contact.email.lower()):
                results.append(contact)
        return results
    
    def get_all(self, sort_by='name'):
        contacts = list(self.contacts.values())
        if sort_by == 'name':
            contacts.sort(key=lambda c: c.name)
        elif sort_by == 'created_at':
            contacts.sort(key=lambda c: c.created_at)
        return contacts
    
    def get_stats(self):
        return {
            'total': len(self.contacts),
            'with_phone': sum(1 for c in self.contacts.values() if c.phone),
            'with_email': sum(1 for c in self.contacts.values() if c.email)
        }
    
    def export_list(self):
        return [c.to_dict() for c in self.get_all()]

def main():
    book = AddressBook()
    
    book.add("张三", "13800138000", "zhangsan@example.com", "北京市")
    book.add("李四", "13900139000", "lisi@example.com", "上海市")
    book.add("王五", "13700137000", "", "广州市")
    
    print("所有联系人:")
    for contact in book.get_all():
        print(f"  {contact.name}: {contact.phone}, {contact.email}")
    
    print("\n搜索'张':")
    results = book.search("张")
    for contact in results:
        print(f"  {contact.name}")
    
    print(f"\n统计: {book.get_stats()}")


if __name__ == "__main__":
    main()
