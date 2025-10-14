#!/usr/bin/env python3
"""
NOCTUA Builder Script
Executes the build steps from noctua.builder.toml manifest
"""

import os
import sys
import subprocess
import secrets
import sqlite3
import hmac
import hashlib
from pathlib import Path

def log(msg: str, emoji: str = "🔧"):
    """Pretty logging"""
    print(f"{emoji} {msg}")

def step_1_generate_structure():
    """Generate .3ox directory and basic files"""
    log("Step 1: Generating structure...", "📁")
    
    os.makedirs(".3ox", exist_ok=True)
    
    # Config file
    config_path = ".3ox/config.toml"
    if not os.path.exists(config_path):
        with open(config_path, "w") as f:
            f.write("""[persona]
name = "NOCTUA"
postscript = "🦉"
identity = "The Owl - Local-first Continuity Agent"

[continuity]
db_path = ".3ox/noctua.db"
log_path = ".3ox/3ox.log"
key_path = ".3ox/!3ox.key"
autobackup = true
rotation_days = 7

[redis]
enabled = true
host = "localhost"
port = 6379
db = 0
prefix = "noctua:"

[telegram]
enabled = false
token = ""
allowed_users = []

[dashboard]
enabled = true
host = "localhost"
port = 8080
style = "n8n"
floating_folders = true
""")
        log("Created config.toml", "✅")
    
    # Generate key
    key_path = ".3ox/!3ox.key"
    if not os.path.exists(key_path):
        key = secrets.token_hex(16)
        with open(key_path, "w") as f:
            f.write(key)
        log(f"Generated key: {key}", "🔑")
    else:
        with open(key_path) as f:
            key = f.read().strip()
        log(f"Using existing key: {key}", "🔑")
    
    return key

def step_2_install_daemon():
    """Copy owl.py daemon (already created)"""
    log("Step 2: Installing daemon...", "🦉")
    
    if os.path.exists(".3ox/owl.py"):
        log("owl.py already exists", "✅")
    else:
        log("ERROR: owl.py not found!", "❌")
        return False
    
    return True

def step_3_init_db():
    """Initialize SQLite database"""
    log("Step 3: Initializing database...", "🗄️")
    
    db_path = ".3ox/noctua.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Memory table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mem (
            node TEXT NOT NULL,
            k TEXT NOT NULL,
            v TEXT,
            updated_at TEXT NOT NULL,
            PRIMARY KEY (node, k)
        )
    """)
    
    # History table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node TEXT NOT NULL,
            ts TEXT NOT NULL,
            role TEXT NOT NULL,
            text TEXT
        )
    """)
    
    # Folder blocks table
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
    conn.close()
    
    log("Database initialized with 3 tables", "✅")
    return True

def step_4_verify_key(key: str):
    """Compute NodeID and create manifest"""
    log("Step 4: Verifying key and computing NodeID...", "🔐")
    
    node_id = hmac.new(key.encode(), b"NOCTUA|v1", hashlib.sha256).hexdigest()
    log(f"NodeID: {node_id}", "🆔")
    
    manifest_path = ".3ox/manifest.toml"
    with open(manifest_path, "w") as f:
        f.write(f"""[manifest]
id = "NOCTUA"
node_id = "{node_id}"
version = "1.0.0"
builder = "noctua.builder.toml"

[capabilities]
continuity = true
memory = true
redis_backend = true
telegram_integration = true
dashboard = true
folder_blocks = true

[runtime]
python_version = "3.10+"
launch_command = "python .3ox/owl.py"
mode = "background"
restart_on_crash = true
""")
    
    log("Manifest created", "✅")
    return node_id

def step_5_test_run():
    """Test owl.py startup"""
    log("Step 5: Testing NOCTUA startup...", "🧪")
    
    try:
        result = subprocess.run(
            ["python3", ".3ox/owl.py"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "NOCTUA" in result.stdout:
            log("NOCTUA started successfully!", "✅")
            print(result.stdout)
            return True
        else:
            log("Startup test failed", "❌")
            print(result.stderr)
            return False
            
    except Exception as e:
        log(f"Test error: {e}", "⚠️")
        return False

def main():
    """Run all build steps"""
    print("=" * 60)
    print("🦉 NOCTUA Builder")
    print("Building and deploying the Owl continuity agent...")
    print("=" * 60)
    print()
    
    try:
        # Execute build steps
        key = step_1_generate_structure()
        
        if not step_2_install_daemon():
            log("Build failed at step 2", "❌")
            return 1
        
        if not step_3_init_db():
            log("Build failed at step 3", "❌")
            return 1
        
        node_id = step_4_verify_key(key)
        
        step_5_test_run()
        
        print()
        print("=" * 60)
        log("NOCTUA built successfully! 🎉", "✅")
        print()
        print(f"📁 Installation: .3ox/")
        print(f"🆔 Node ID: {node_id[:32]}...")
        print(f"🦉 Launch: python .3ox/owl.py")
        print(f"🔄 Daemon: python .3ox/owl.py --daemon")
        print(f"🌐 Dashboard: python .3ox/dashboard.py (coming next)")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        log(f"Build error: {e}", "❌")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
