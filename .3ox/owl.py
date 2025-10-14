#!/usr/bin/env python3
"""
NOCTUA OWL.PY - The Continuity Daemon
A local-first agent with Redis backend, memory persistence, and restart-proof operation.
"""

import os
import sys
import time
import json
import sqlite3
import hmac
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING

# Optional Redis support
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None  # type: ignore
    print("⚠️  Redis not available - running in SQLite-only mode")

# TOML config parsing
try:
    import tomli as toml
except ImportError:
    try:
        import tomllib as toml
    except ImportError:
        print("❌ TOML parser not found. Install tomli: pip install tomli")
        sys.exit(1)


class NoctuaOwl:
    """
    The Owl - NOCTUA's continuity daemon
    Manages memory, state, and cross-session persistence
    """
    
    def __init__(self, config_path: str = ".3ox/config.toml"):
        self.config_path = Path(config_path)
        self.base_dir = self.config_path.parent
        self.config = self._load_config()
        
        # Setup logging
        log_path = self.base_dir / self.config['continuity']['log_path'].replace('.3ox/', '')
        self._setup_logging(log_path)
        
        # Load identity
        self.key = self._load_key()
        self.node_id = self._compute_node_id()
        
        # Initialize databases
        self.db = self._init_sqlite()
        self.redis = self._init_redis() if self.config['redis']['enabled'] and REDIS_AVAILABLE else None
        
        self.logger.info(f"🦉 NOCTUA online | NodeID: {self.node_id[:16]}...")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from TOML"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'rb') as f:
            return toml.load(f)
    
    def _setup_logging(self, log_path: Path):
        """Setup logging to file and console"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('NOCTUA')
    
    def _load_key(self) -> bytes:
        """Load the cryptographic key"""
        key_path = self.base_dir / self.config['continuity']['key_path'].replace('.3ox/', '')
        if not key_path.exists():
            raise FileNotFoundError(f"Key not found: {key_path}")
        return key_path.read_bytes().strip()
    
    def _compute_node_id(self) -> str:
        """Compute unique node ID from key"""
        return hmac.new(self.key, b"NOCTUA|v1", hashlib.sha256).hexdigest()
    
    def _init_sqlite(self) -> sqlite3.Connection:
        """Initialize SQLite database for local persistence"""
        db_path = self.base_dir / self.config['continuity']['db_path'].replace('.3ox/', '')
        conn = sqlite3.connect(str(db_path), check_same_thread=False)
        cur = conn.cursor()
        
        # Memory table: key-value store with node scoping
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mem (
                node TEXT NOT NULL,
                k TEXT NOT NULL,
                v TEXT,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (node, k)
            )
        """)
        
        # History table: conversation and event log
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node TEXT NOT NULL,
                ts TEXT NOT NULL,
                role TEXT NOT NULL,
                text TEXT
            )
        """)
        
        # Folder blocks table: n8n-style node storage
        cur.execute("""
            CREATE TABLE IF NOT EXISTS folder_blocks (
                id TEXT PRIMARY KEY,
                node TEXT NOT NULL,
                folder_path TEXT NOT NULL,
                block_type TEXT NOT NULL,
                config TEXT,
                position_x REAL,
                position_y REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        conn.commit()
        self.logger.info("✅ SQLite database initialized")
        return conn
    
    def _init_redis(self) -> Optional[Any]:
        """Initialize Redis connection for distributed continuity"""
        try:
            r = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            r.ping()
            self.logger.info("✅ Redis connected")
            return r
        except Exception as e:
            self.logger.warning(f"⚠️  Redis connection failed: {e}")
            return None
    
    def set_memory(self, key: str, value: str, sync_redis: bool = True):
        """Store a memory value"""
        now = datetime.utcnow().isoformat()
        
        # SQLite storage
        cur = self.db.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO mem (node, k, v, updated_at)
            VALUES (?, ?, ?, ?)
        """, (self.node_id, key, value, now))
        self.db.commit()
        
        # Redis sync
        if sync_redis and self.redis:
            redis_key = f"{self.config['redis']['prefix']}mem:{self.node_id}:{key}"
            self.redis.set(redis_key, value)
            self.redis.hset(f"{self.config['redis']['prefix']}meta:{self.node_id}:{key}", 
                           "updated_at", now)
        
        self.logger.debug(f"📝 Memory set: {key} = {value[:50]}...")
    
    def get_memory(self, key: str, check_redis: bool = True) -> Optional[str]:
        """Retrieve a memory value"""
        # Try Redis first (faster)
        if check_redis and self.redis:
            redis_key = f"{self.config['redis']['prefix']}mem:{self.node_id}:{key}"
            value = self.redis.get(redis_key)
            if value:
                return value
        
        # Fallback to SQLite
        cur = self.db.cursor()
        cur.execute("SELECT v FROM mem WHERE node = ? AND k = ?", (self.node_id, key))
        row = cur.fetchone()
        return row[0] if row else None
    
    def log_history(self, role: str, text: str, sync_redis: bool = True):
        """Log conversation history"""
        now = datetime.utcnow().isoformat()
        
        # SQLite storage
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO history (node, ts, role, text)
            VALUES (?, ?, ?, ?)
        """, (self.node_id, now, role, text))
        self.db.commit()
        
        # Redis stream
        if sync_redis and self.redis:
            stream_key = f"{self.config['redis']['prefix']}history:{self.node_id}"
            self.redis.xadd(stream_key, {
                "role": role,
                "text": text,
                "ts": now
            })
        
        self.logger.debug(f"📜 History logged: {role}")
    
    def create_folder_block(self, folder_path: str, block_type: str, 
                           config: Dict[str, Any], position: tuple = (0, 0)) -> str:
        """Create a floating folder block (n8n-style node)"""
        import uuid
        block_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        cur = self.db.cursor()
        cur.execute("""
            INSERT INTO folder_blocks 
            (id, node, folder_path, block_type, config, position_x, position_y, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (block_id, self.node_id, folder_path, block_type, json.dumps(config), 
              position[0], position[1], now, now))
        self.db.commit()
        
        # Sync to Redis
        if self.redis:
            redis_key = f"{self.config['redis']['prefix']}blocks:{self.node_id}:{block_id}"
            self.redis.hset(redis_key, mapping={
                "folder_path": folder_path,
                "block_type": block_type,
                "config": json.dumps(config),
                "position_x": position[0],
                "position_y": position[1],
                "updated_at": now
            })
        
        self.logger.info(f"🧩 Folder block created: {block_id} ({block_type} @ {folder_path})")
        return block_id
    
    def get_folder_blocks(self) -> list:
        """Get all folder blocks for the dashboard"""
        cur = self.db.cursor()
        cur.execute("""
            SELECT id, folder_path, block_type, config, position_x, position_y, updated_at
            FROM folder_blocks
            WHERE node = ?
            ORDER BY created_at
        """, (self.node_id,))
        
        blocks = []
        for row in cur.fetchall():
            blocks.append({
                "id": row[0],
                "folder_path": row[1],
                "block_type": row[2],
                "config": json.loads(row[3]) if row[3] else {},
                "position": (row[4], row[5]),
                "updated_at": row[6]
            })
        return blocks
    
    def backup(self):
        """Create a backup of the database"""
        if self.config['continuity']['autobackup']:
            backup_dir = self.base_dir / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"noctua_{timestamp}.db"
            
            # SQLite backup
            backup_conn = sqlite3.connect(str(backup_path))
            self.db.backup(backup_conn)
            backup_conn.close()
            
            self.logger.info(f"💾 Backup created: {backup_path.name}")
    
    def run_daemon(self, interval: int = 60):
        """Run as a background daemon"""
        self.logger.info("🦉 NOCTUA daemon started - Press Ctrl+C to stop")
        
        try:
            while True:
                # Periodic backup
                self.backup()
                
                # Sync stats
                if self.redis:
                    self.redis.hset(f"{self.config['redis']['prefix']}status:{self.node_id}",
                                   "last_seen", datetime.utcnow().isoformat())
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 NOCTUA shutting down gracefully...")
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        self.backup()
        self.db.close()
        if self.redis:
            self.redis.close()
        self.logger.info("👋 NOCTUA offline")


def main():
    """Main entry point"""
    print("🦉 NOCTUA - The Owl Continuity Agent")
    print("=" * 50)
    
    try:
        owl = NoctuaOwl()
        
        # Test basic operations
        owl.set_memory("boot_time", datetime.utcnow().isoformat())
        owl.log_history("system", "NOCTUA online")
        
        # Create a sample folder block
        owl.create_folder_block(
            folder_path="/workspace/.3ox",
            block_type="config",
            config={"name": "Core Config", "editable": True},
            position=(100, 100)
        )
        
        print(f"\n✅ Node ID: {owl.node_id}")
        print(f"✅ SQLite: {owl.config['continuity']['db_path']}")
        print(f"✅ Redis: {'Connected' if owl.redis else 'Disabled'}")
        print(f"✅ Folder Blocks: {len(owl.get_folder_blocks())}")
        
        # Run as daemon if requested
        if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
            owl.run_daemon()
        else:
            print("\n🎯 Ready! Run with --daemon to start background service")
            owl.shutdown()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
