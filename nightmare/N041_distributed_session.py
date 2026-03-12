# -----------------------------
# 题目：实现分布式会话管理。
# 描述：支持会话存储、会话同步、会话过期。
# -----------------------------

import time
import threading
import hashlib
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Session:
    session_id: str
    user_id: str
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    expires_at: float = 0
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    def touch(self, ttl: int):
        self.last_accessed = time.time()
        self.expires_at = self.last_accessed + ttl
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'data': self.data,
            'created_at': self.created_at,
            'last_accessed': self.last_accessed,
            'expires_at': self.expires_at,
            'metadata': self.metadata
        }

class SessionStore:
    def __init__(self, default_ttl: int = 1800):
        self.default_ttl = default_ttl
        self.sessions: Dict[str, Session] = {}
        self._user_sessions: Dict[str, List[str]] = {}
        self._lock = threading.RLock()
    
    def create(self, user_id: str, data: Dict = None, ttl: int = None) -> Session:
        ttl = ttl or self.default_ttl
        
        session_id = self._generate_session_id(user_id)
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            data=data or {},
            expires_at=time.time() + ttl
        )
        
        with self._lock:
            self.sessions[session_id] = session
            
            if user_id not in self._user_sessions:
                self._user_sessions[user_id] = []
            self._user_sessions[user_id].append(session_id)
        
        return session
    
    def get(self, session_id: str) -> Optional[Session]:
        with self._lock:
            session = self.sessions.get(session_id)
            
            if session and session.is_expired():
                self.delete(session_id)
                return None
            
            return session
    
    def update(self, session_id: str, data: Dict[str, Any], ttl: int = None) -> bool:
        with self._lock:
            session = self.sessions.get(session_id)
            
            if not session or session.is_expired():
                return False
            
            session.data.update(data)
            session.touch(ttl or self.default_ttl)
            
            return True
    
    def delete(self, session_id: str) -> bool:
        with self._lock:
            session = self.sessions.pop(session_id, None)
            
            if session:
                user_sessions = self._user_sessions.get(session.user_id, [])
                if session_id in user_sessions:
                    user_sessions.remove(session_id)
                return True
            
            return False
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        with self._lock:
            session_ids = self._user_sessions.get(user_id, [])
            return [
                self.sessions[sid] for sid in session_ids
                if sid in self.sessions and not self.sessions[sid].is_expired()
            ]
    
    def invalidate_user_sessions(self, user_id: str) -> int:
        with self._lock:
            session_ids = self._user_sessions.get(user_id, [])
            count = 0
            
            for sid in session_ids:
                if sid in self.sessions:
                    del self.sessions[sid]
                    count += 1
            
            self._user_sessions[user_id] = []
            
            return count
    
    def cleanup_expired(self) -> int:
        with self._lock:
            expired = [
                sid for sid, session in self.sessions.items()
                if session.is_expired()
            ]
            
            for sid in expired:
                self.delete(sid)
            
            return len(expired)
    
    def _generate_session_id(self, user_id: str) -> str:
        data = f"{user_id}:{time.time()}:{id(self)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

class DistributedSessionManager:
    def __init__(self, default_ttl: int = 1800):
        self.default_ttl = default_ttl
        self.stores: Dict[str, SessionStore] = {}
        self._primary_store: Optional[str] = None
        self._lock = threading.Lock()
    
    def add_store(self, store_id: str, store: SessionStore):
        with self._lock:
            self.stores[store_id] = store
            if not self._primary_store:
                self._primary_store = store_id
    
    def create_session(self, user_id: str, data: Dict = None, ttl: int = None) -> Session:
        store = self.stores.get(self._primary_store)
        if store:
            return store.create(user_id, data, ttl)
        raise Exception("No session store available")
    
    def get_session(self, session_id: str) -> Optional[Session]:
        for store in self.stores.values():
            session = store.get(session_id)
            if session:
                return session
        return None
    
    def update_session(self, session_id: str, data: Dict[str, Any], ttl: int = None) -> bool:
        for store in self.stores.values():
            if store.update(session_id, data, ttl):
                return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        for store in self.stores.values():
            if store.delete(session_id):
                return True
        return False
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        all_sessions = []
        for store in self.stores.values():
            all_sessions.extend(store.get_user_sessions(user_id))
        return all_sessions
    
    def invalidate_user(self, user_id: str) -> int:
        total = 0
        for store in self.stores.values():
            total += store.invalidate_user_sessions(user_id)
        return total
    
    def start_cleanup(self, interval: int = 60):
        def cleanup_loop():
            while True:
                time.sleep(interval)
                for store in self.stores.values():
                    store.cleanup_expired()
        
        thread = threading.Thread(target=cleanup_loop)
        thread.daemon = True
        thread.start()

class SessionMiddleware:
    def __init__(self, manager: DistributedSessionManager):
        self.manager = manager
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        session_id = request.get('headers', {}).get('X-Session-Id')
        
        if session_id:
            session = self.manager.get_session(session_id)
            if session:
                request['session'] = session
                return request
        
        request['session'] = None
        return request
    
    def process_response(self, response: Dict[str, Any], session: Session = None) -> Dict[str, Any]:
        if session:
            response['headers'] = response.get('headers', {})
            response['headers']['X-Session-Id'] = session.session_id
        
        return response

def main():
    manager = DistributedSessionManager(default_ttl=3600)
    
    store1 = SessionStore(default_ttl=3600)
    store2 = SessionStore(default_ttl=3600)
    
    manager.add_store("store-1", store1)
    manager.add_store("store-2", store2)
    
    print("创建会话...")
    session = manager.create_session("user-123", {"role": "admin", "name": "张三"})
    print(f"  会话ID: {session.session_id}")
    print(f"  用户ID: {session.user_id}")
    print(f"  过期时间: {datetime.fromtimestamp(session.expires_at)}")
    
    print("\n更新会话...")
    manager.update_session(session.session_id, {"last_page": "/dashboard"})
    updated = manager.get_session(session.session_id)
    print(f"  数据: {updated.data}")
    
    print("\n获取用户所有会话:")
    sessions = manager.get_user_sessions("user-123")
    for s in sessions:
        print(f"  - {s.session_id[:16]}... (创建于 {datetime.fromtimestamp(s.created_at)})")
    
    print("\n使会话失效:")
    count = manager.invalidate_user("user-123")
    print(f"  已失效 {count} 个会话")
    
    session = manager.get_session(session.session_id)
    print(f"  会话是否还存在: {session is not None}")

if __name__ == "__main__":
    main()
