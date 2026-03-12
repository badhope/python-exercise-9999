# -----------------------------
# 题目：实现数据迁移工具。
# 描述：支持版本管理、迁移脚本、回滚操作。
# -----------------------------

import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class MigrationStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class Migration:
    version: str
    name: str
    up_script: str
    down_script: str
    created_at: float = field(default_factory=time.time)
    status: MigrationStatus = MigrationStatus.PENDING
    executed_at: Optional[float] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None

@dataclass
class MigrationRecord:
    version: str
    name: str
    executed_at: float
    execution_time: float
    status: str

class MigrationHistory:
    def __init__(self):
        self._records: List[MigrationRecord] = []
    
    def add(self, record: MigrationRecord):
        self._records.append(record)
    
    def get_executed_versions(self) -> List[str]:
        return [r.version for r in self._records if r.status == "completed"]
    
    def get_last_version(self) -> Optional[str]:
        completed = [r for r in self._records if r.status == "completed"]
        if completed:
            return completed[-1].version
        return None
    
    def remove(self, version: str) -> bool:
        for i, record in enumerate(self._records):
            if record.version == version:
                self._records.pop(i)
                return True
        return False
    
    def get_all(self) -> List[MigrationRecord]:
        return self._records.copy()

class MigrationRunner:
    def __init__(self):
        self._migrations: Dict[str, Migration] = {}
        self._history = MigrationHistory()
        self._lock = False
    
    def register(self, migration: Migration):
        self._migrations[migration.version] = migration
    
    def create_migration(
        self,
        version: str,
        name: str,
        up_script: str,
        down_script: str
    ) -> Migration:
        migration = Migration(
            version=version,
            name=name,
            up_script=up_script,
            down_script=down_script
        )
        self._migrations[version] = migration
        return migration
    
    def get_pending_migrations(self) -> List[Migration]:
        executed = set(self._history.get_executed_versions())
        pending = [
            m for m in self._migrations.values()
            if m.version not in executed
        ]
        return sorted(pending, key=lambda m: m.version)
    
    def migrate(self, target_version: str = None) -> List[MigrationRecord]:
        pending = self.get_pending_migrations()
        
        if target_version:
            pending = [m for m in pending if m.version <= target_version]
        
        results = []
        
        for migration in pending:
            record = self._run_migration(migration)
            results.append(record)
            
            if record.status == "failed":
                break
        
        return results
    
    def _run_migration(self, migration: Migration) -> MigrationRecord:
        migration.status = MigrationStatus.RUNNING
        start_time = time.time()
        
        try:
            self._execute_script(migration.up_script)
            
            migration.status = MigrationStatus.COMPLETED
            migration.executed_at = time.time()
            migration.execution_time = migration.executed_at - start_time
            
            record = MigrationRecord(
                version=migration.version,
                name=migration.name,
                executed_at=migration.executed_at,
                execution_time=migration.execution_time,
                status="completed"
            )
            
            self._history.add(record)
            return record
        
        except Exception as e:
            migration.status = MigrationStatus.FAILED
            migration.error = str(e)
            
            return MigrationRecord(
                version=migration.version,
                name=migration.name,
                executed_at=time.time(),
                execution_time=time.time() - start_time,
                status="failed"
            )
    
    def rollback(self, steps: int = 1) -> List[MigrationRecord]:
        executed = self._history.get_executed_versions()
        results = []
        
        for version in reversed(executed[-steps:]):
            migration = self._migrations.get(version)
            if migration:
                record = self._run_rollback(migration)
                results.append(record)
        
        return results
    
    def _run_rollback(self, migration: Migration) -> MigrationRecord:
        start_time = time.time()
        
        try:
            self._execute_script(migration.down_script)
            
            migration.status = MigrationStatus.ROLLED_BACK
            
            self._history.remove(migration.version)
            
            return MigrationRecord(
                version=migration.version,
                name=migration.name,
                executed_at=time.time(),
                execution_time=time.time() - start_time,
                status="rolled_back"
            )
        
        except Exception as e:
            return MigrationRecord(
                version=migration.version,
                name=migration.name,
                executed_at=time.time(),
                execution_time=time.time() - start_time,
                status="failed"
            )
    
    def _execute_script(self, script: str):
        print(f"执行脚本: {script[:50]}...")
    
    def get_status(self) -> Dict[str, Any]:
        pending = self.get_pending_migrations()
        executed = self._history.get_executed_versions()
        
        return {
            'total_migrations': len(self._migrations),
            'pending_count': len(pending),
            'executed_count': len(executed),
            'current_version': self._history.get_last_version(),
            'pending_versions': [m.version for m in pending]
        }

class MigrationBuilder:
    def __init__(self, runner: MigrationRunner):
        self.runner = runner
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> str:
        cols = []
        for name, dtype in columns.items():
            cols.append(f"{name} {dtype}")
        
        return f"CREATE TABLE {table_name} ({', '.join(cols)})"
    
    def drop_table(self, table_name: str) -> str:
        return f"DROP TABLE IF EXISTS {table_name}"
    
    def add_column(self, table_name: str, column_name: str, column_type: str) -> str:
        return f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
    
    def drop_column(self, table_name: str, column_name: str) -> str:
        return f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
    
    def create_index(self, table_name: str, index_name: str, columns: List[str]) -> str:
        return f"CREATE INDEX {index_name} ON {table_name} ({', '.join(columns)})"
    
    def drop_index(self, index_name: str) -> str:
        return f"DROP INDEX IF EXISTS {index_name}"

def main():
    runner = MigrationRunner()
    builder = MigrationBuilder(runner)
    
    runner.create_migration(
        version="20240101001",
        name="create_users_table",
        up_script=builder.create_table("users", {
            "id": "INTEGER PRIMARY KEY",
            "username": "VARCHAR(50)",
            "email": "VARCHAR(100)"
        }),
        down_script=builder.drop_table("users")
    )
    
    runner.create_migration(
        version="20240101002",
        name="add_user_status",
        up_script=builder.add_column("users", "status", "VARCHAR(20)"),
        down_script=builder.drop_column("users", "status")
    )
    
    runner.create_migration(
        version="20240101003",
        name="create_orders_table",
        up_script=builder.create_table("orders", {
            "id": "INTEGER PRIMARY KEY",
            "user_id": "INTEGER",
            "amount": "DECIMAL(10,2)"
        }),
        down_script=builder.drop_table("orders")
    )
    
    print("迁移状态:")
    status = runner.get_status()
    print(f"  总迁移数: {status['total_migrations']}")
    print(f"  待执行数: {status['pending_count']}")
    print(f"  当前版本: {status['current_version']}")
    
    print("\n执行迁移:")
    results = runner.migrate()
    for r in results:
        print(f"  {r.version} {r.name}: {r.status} ({r.execution_time:.3f}s)")
    
    print("\n迁移后状态:")
    status = runner.get_status()
    print(f"  当前版本: {status['current_version']}")
    
    print("\n回滚一步:")
    rollback_results = runner.rollback(1)
    for r in rollback_results:
        print(f"  {r.version} {r.name}: {r.status}")

if __name__ == "__main__":
    main()
