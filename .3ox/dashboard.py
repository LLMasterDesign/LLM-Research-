#!/usr/bin/env python3
"""
NOCTUA Dashboard
A beautiful n8n-inspired node-based interface with floating folder blocks
Web-based interface for managing NOCTUA agents and workflows
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Flask for web interface
try:
    from flask import Flask, render_template_string, jsonify, request
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️  Flask not available. Install with: pip install flask flask-cors")

# TOML config
try:
    import tomli as toml
except ImportError:
    try:
        import tomllib as toml
    except ImportError:
        print("❌ Install tomli: pip install tomli")
        exit(1)


# HTML Template - N8N-inspired dark theme
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦉 NOCTUA Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', sans-serif;
            background: #1a1a2e;
            color: #e4e4e7;
            overflow: hidden;
        }
        
        .header {
            background: #16213e;
            padding: 16px 24px;
            border-bottom: 1px solid #0f3460;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .status {
            display: flex;
            gap: 16px;
            align-items: center;
            font-size: 14px;
        }
        
        .status-badge {
            padding: 6px 12px;
            background: #059669;
            border-radius: 16px;
            font-weight: 500;
            font-size: 12px;
        }
        
        .canvas {
            position: relative;
            width: 100%;
            height: calc(100vh - 64px);
            background: 
                linear-gradient(90deg, rgba(15, 52, 96, 0.1) 1px, transparent 1px),
                linear-gradient(rgba(15, 52, 96, 0.1) 1px, transparent 1px);
            background-size: 40px 40px;
            overflow: auto;
        }
        
        .folder-block {
            position: absolute;
            width: 280px;
            background: #16213e;
            border: 2px solid #0f3460;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.4);
            transition: all 0.2s;
            cursor: move;
        }
        
        .folder-block:hover {
            border-color: #e94560;
            box-shadow: 0 12px 32px rgba(233, 69, 96, 0.3);
        }
        
        .folder-block.selected {
            border-color: #e94560;
            box-shadow: 0 0 0 3px rgba(233, 69, 96, 0.2);
        }
        
        .block-header {
            padding: 16px;
            border-bottom: 1px solid #0f3460;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-radius: 10px 10px 0 0;
        }
        
        .block-type {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #e94560;
            font-weight: 600;
        }
        
        .block-icon {
            font-size: 20px;
        }
        
        .block-body {
            padding: 16px;
        }
        
        .block-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        
        .block-path {
            font-size: 12px;
            color: #a1a1aa;
            font-family: 'Courier New', monospace;
            margin-bottom: 12px;
            word-break: break-all;
        }
        
        .block-meta {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .meta-tag {
            font-size: 11px;
            padding: 4px 8px;
            background: #0f3460;
            border-radius: 4px;
            color: #a1a1aa;
        }
        
        .sidebar {
            position: fixed;
            right: 0;
            top: 64px;
            width: 320px;
            height: calc(100vh - 64px);
            background: #16213e;
            border-left: 1px solid #0f3460;
            padding: 24px;
            overflow-y: auto;
        }
        
        .sidebar h2 {
            font-size: 18px;
            margin-bottom: 16px;
            color: #e94560;
        }
        
        .add-block-btn {
            width: 100%;
            padding: 12px;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 24px;
        }
        
        .add-block-btn:hover {
            background: #d63651;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(233, 69, 96, 0.4);
        }
        
        .stats {
            background: #0f3460;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 16px;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .stat-label {
            color: #a1a1aa;
        }
        
        .stat-value {
            color: #e94560;
            font-weight: 600;
        }
        
        .connection-line {
            position: absolute;
            pointer-events: none;
            z-index: -1;
        }
        
        .mini-map {
            position: fixed;
            bottom: 24px;
            left: 24px;
            width: 200px;
            height: 150px;
            background: rgba(22, 33, 62, 0.9);
            border: 1px solid #0f3460;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading {
            animation: pulse 2s infinite;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>
            <span>🦉</span>
            <span>NOCTUA Dashboard</span>
        </h1>
        <div class="status">
            <span>Node: <code>{{ node_id[:12] }}...</code></span>
            <span class="status-badge">● ONLINE</span>
        </div>
    </div>
    
    <div class="canvas" id="canvas">
        <!-- Folder blocks will be dynamically added here -->
    </div>
    
    <div class="sidebar">
        <h2>🧩 Blocks</h2>
        <button class="add-block-btn" onclick="addNewBlock()">+ Add Folder Block</button>
        
        <div class="stats">
            <div class="stat-row">
                <span class="stat-label">Total Blocks</span>
                <span class="stat-value" id="total-blocks">{{ blocks|length }}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Memory Keys</span>
                <span class="stat-value" id="memory-keys">{{ memory_count }}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">History Items</span>
                <span class="stat-value" id="history-items">{{ history_count }}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Redis</span>
                <span class="stat-value">{{ 'ON' if redis_enabled else 'OFF' }}</span>
            </div>
        </div>
        
        <h2>📊 Block Types</h2>
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <button onclick="addBlockType('config')" style="padding: 8px; background: #0f3460; border: none; border-radius: 4px; color: white; cursor: pointer;">⚙️ Config</button>
            <button onclick="addBlockType('data')" style="padding: 8px; background: #0f3460; border: none; border-radius: 4px; color: white; cursor: pointer;">📦 Data</button>
            <button onclick="addBlockType('task')" style="padding: 8px; background: #0f3460; border: none; border-radius: 4px; color: white; cursor: pointer;">✅ Task</button>
            <button onclick="addBlockType('telegram')" style="padding: 8px; background: #0f3460; border: none; border-radius: 4px; color: white; cursor: pointer;">💬 Telegram</button>
        </div>
    </div>
    
    <div class="mini-map">
        <canvas id="minimap" width="200" height="150"></canvas>
    </div>
    
    <script>
        // Load existing blocks
        let blocks = {{ blocks_json | safe }};
        
        // Render blocks
        function renderBlocks() {
            const canvas = document.getElementById('canvas');
            canvas.innerHTML = '';
            
            blocks.forEach(block => {
                const blockEl = createBlockElement(block);
                canvas.appendChild(blockEl);
            });
            
            updateStats();
        }
        
        function createBlockElement(block) {
            const div = document.createElement('div');
            div.className = 'folder-block';
            div.style.left = block.position[0] + 'px';
            div.style.top = block.position[1] + 'px';
            div.setAttribute('data-id', block.id);
            
            const icon = {
                'config': '⚙️',
                'data': '📦',
                'task': '✅',
                'telegram': '💬'
            }[block.block_type] || '📁';
            
            div.innerHTML = `
                <div class="block-header">
                    <span class="block-icon">${icon}</span>
                    <span class="block-type">${block.block_type}</span>
                </div>
                <div class="block-body">
                    <div class="block-title">${block.config.name || 'Unnamed Block'}</div>
                    <div class="block-path">${block.folder_path}</div>
                    <div class="block-meta">
                        <span class="meta-tag">📅 ${new Date(block.updated_at).toLocaleDateString()}</span>
                        <span class="meta-tag">🆔 ${block.id.slice(0,8)}</span>
                    </div>
                </div>
            `;
            
            // Make draggable
            makeDraggable(div);
            
            return div;
        }
        
        function makeDraggable(element) {
            let isDragging = false;
            let currentX, currentY, initialX, initialY;
            
            element.addEventListener('mousedown', e => {
                if (e.target.tagName === 'BUTTON') return;
                isDragging = true;
                initialX = e.clientX - element.offsetLeft;
                initialY = e.clientY - element.offsetTop;
                element.classList.add('selected');
            });
            
            document.addEventListener('mousemove', e => {
                if (!isDragging) return;
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                element.style.left = currentX + 'px';
                element.style.top = currentY + 'px';
            });
            
            document.addEventListener('mouseup', () => {
                if (isDragging) {
                    isDragging = false;
                    element.classList.remove('selected');
                    // Save position
                    const id = element.getAttribute('data-id');
                    const block = blocks.find(b => b.id === id);
                    if (block) {
                        block.position = [parseInt(element.style.left), parseInt(element.style.top)];
                        saveBlocks();
                    }
                }
            });
        }
        
        function addNewBlock() {
            const folderPath = prompt('Enter folder path:', '/workspace/.3ox');
            if (!folderPath) return;
            
            const blockType = prompt('Block type (config/data/task/telegram):', 'config');
            const name = prompt('Block name:', 'New Block');
            
            fetch('/api/blocks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    folder_path: folderPath,
                    block_type: blockType,
                    config: {name: name, editable: true},
                    position: [Math.random() * 500 + 100, Math.random() * 300 + 100]
                })
            })
            .then(r => r.json())
            .then(data => {
                blocks.push(data.block);
                renderBlocks();
            });
        }
        
        function addBlockType(type) {
            const folderPath = prompt('Enter folder path:', '/workspace');
            if (!folderPath) return;
            
            fetch('/api/blocks', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    folder_path: folderPath,
                    block_type: type,
                    config: {name: type.charAt(0).toUpperCase() + type.slice(1) + ' Block'},
                    position: [Math.random() * 500 + 100, Math.random() * 300 + 100]
                })
            })
            .then(r => r.json())
            .then(data => {
                blocks.push(data.block);
                renderBlocks();
            });
        }
        
        function saveBlocks() {
            fetch('/api/blocks/save', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({blocks: blocks})
            });
        }
        
        function updateStats() {
            document.getElementById('total-blocks').textContent = blocks.length;
        }
        
        // Initial render
        renderBlocks();
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('memory-keys').textContent = data.memory_count;
                    document.getElementById('history-items').textContent = data.history_count;
                });
        }, 10000);
    </script>
</body>
</html>
"""


class NoctuaDashboard:
    """Dashboard interface for NOCTUA"""
    
    def __init__(self, config_path: str = ".3ox/config.toml"):
        self.config_path = Path(config_path)
        self.base_dir = self.config_path.parent
        self.config = self._load_config()
        
        # Database connection
        db_path = self.base_dir / self.config['continuity']['db_path'].replace('.3ox/', '')
        self.db = sqlite3.connect(str(db_path), check_same_thread=False)
        
        # Load node ID
        manifest_path = self.base_dir / "manifest.toml"
        with open(manifest_path, 'rb') as f:
            manifest = toml.load(f)
            self.node_id = manifest['manifest']['node_id']
        
        # Flask app
        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            CORS(self.app)
            self._setup_routes()
    
    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, 'rb') as f:
            return toml.load(f)
    
    def _setup_routes(self):
        @self.app.route('/')
        def index():
            blocks = self._get_blocks()
            memory_count = self._get_memory_count()
            history_count = self._get_history_count()
            
            return render_template_string(
                DASHBOARD_HTML,
                node_id=self.node_id,
                blocks=blocks,
                blocks_json=json.dumps(blocks),
                memory_count=memory_count,
                history_count=history_count,
                redis_enabled=self.config['redis']['enabled']
            )
        
        @self.app.route('/api/blocks', methods=['GET'])
        def get_blocks():
            return jsonify({"blocks": self._get_blocks()})
        
        @self.app.route('/api/blocks', methods=['POST'])
        def create_block():
            data = request.json
            block_id = self._create_block(
                data['folder_path'],
                data['block_type'],
                data['config'],
                tuple(data['position'])
            )
            
            blocks = self._get_blocks()
            block = next((b for b in blocks if b['id'] == block_id), None)
            
            return jsonify({"success": True, "block": block})
        
        @self.app.route('/api/blocks/save', methods=['POST'])
        def save_blocks():
            # Update positions in database
            data = request.json
            cur = self.db.cursor()
            
            for block in data['blocks']:
                cur.execute("""
                    UPDATE folder_blocks
                    SET position_x = ?, position_y = ?, updated_at = ?
                    WHERE id = ?
                """, (block['position'][0], block['position'][1], 
                      datetime.utcnow().isoformat(), block['id']))
            
            self.db.commit()
            return jsonify({"success": True})
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            return jsonify({
                "memory_count": self._get_memory_count(),
                "history_count": self._get_history_count(),
                "blocks_count": len(self._get_blocks())
            })
    
    def _get_blocks(self) -> List[Dict[str, Any]]:
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
                "position": [row[4], row[5]],
                "updated_at": row[6]
            })
        return blocks
    
    def _create_block(self, folder_path: str, block_type: str, 
                     config: Dict[str, Any], position: tuple) -> str:
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
        
        return block_id
    
    def _get_memory_count(self) -> int:
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM mem WHERE node = ?", (self.node_id,))
        return cur.fetchone()[0]
    
    def _get_history_count(self) -> int:
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM history WHERE node = ?", (self.node_id,))
        return cur.fetchone()[0]
    
    def run(self):
        """Start the dashboard server"""
        if not FLASK_AVAILABLE:
            print("❌ Flask is required. Install: pip install flask flask-cors")
            return
        
        host = self.config['dashboard']['host']
        port = self.config['dashboard']['port']
        
        print("=" * 60)
        print(f"🦉 NOCTUA Dashboard Starting...")
        print(f"🌐 URL: http://{host}:{port}")
        print(f"🆔 Node: {self.node_id[:32]}...")
        print("=" * 60)
        
        self.app.run(host=host, port=port, debug=False)


def main():
    """Main entry point"""
    try:
        dashboard = NoctuaDashboard()
        dashboard.run()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
