#!/usr/bin/env python3
"""
Goose Web UI - Flask-based dashboard for remote access and configuration
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import threading
import click

app = Flask(__name__)
app.config['SECRET_KEY'] = 'goose-dashboard-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
current_process = None
sessions_db = Path.home() / ".config" / "goose" / "sessions.db"
config_file = Path("config.json")

# Load configuration
def load_config():
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    return {
        "provider": "openai",
        "model": "gpt-4",
        "port": 8080,
        "host": "localhost"
    }

config = load_config()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration"""
    global config
    
    if request.method == 'POST':
        data = request.json
        config.update(data)
        
        # Save to file
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({"status": "success", "config": config})
    
    return jsonify(config)

@app.route('/api/sessions')
def api_sessions():
    """List all sessions"""
    if not sessions_db.exists():
        return jsonify({"sessions": []})
    
    try:
        conn = sqlite3.connect(sessions_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, created_at, last_accessed, directory
            FROM sessions
            ORDER BY last_accessed DESC
        """)
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "name": row[0],
                "created": row[1],
                "accessed": row[2],
                "directory": row[3]
            })
        
        conn.close()
        return jsonify({"sessions": sessions})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/session/<name>/history')
def api_session_history(name):
    """Get chat history for a session"""
    if not sessions_db.exists():
        return jsonify({"messages": []})
    
    try:
        conn = sqlite3.connect(sessions_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, content, timestamp
            FROM messages
            WHERE session_name = ?
            ORDER BY timestamp ASC
        """, (name,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        
        conn.close()
        return jsonify({"messages": messages})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/extensions')
def api_extensions():
    """List available extensions"""
    extensions = [
        {
            "name": "developer",
            "status": "available",
            "description": "Code analysis, debugging, file operations"
        },
        {
            "name": "github",
            "status": "available",
            "description": "GitHub repository operations"
        },
        {
            "name": "computer",
            "status": "available",
            "description": "System control and automation"
        },
        {
            "name": "screen",
            "status": "available",
            "description": "Screen capture and OCR"
        }
    ]
    
    return jsonify({"extensions": extensions})

@socketio.on('connect')
def handle_connect():
    """Client connected via WebSocket"""
    emit('status', {'message': 'Connected to Goose Dashboard'})

@socketio.on('send_message')
def handle_message(data):
    """Handle chat message from client"""
    message = data.get('message', '')
    session_name = data.get('session', 'default')
    
    if not message:
        return
    
    # Echo user message
    emit('message', {
        'role': 'user',
        'content': message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Run goose command in thread
    def run_goose():
        try:
            cmd = ['goose', 'session', 'resume', '-n', session_name, '-t', message]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Stream output
            response_lines = []
            for line in process.stdout:
                line = line.strip()
                if line:
                    response_lines.append(line)
                    # Emit partial response
                    socketio.emit('partial_response', {'content': line})
            
            process.wait()
            
            # Send complete response
            full_response = '\n'.join(response_lines)
            socketio.emit('message', {
                'role': 'assistant',
                'content': full_response,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            socketio.emit('error', {'message': str(e)})
    
    thread = threading.Thread(target=run_goose)
    thread.daemon = True
    thread.start()

@socketio.on('new_session')
def handle_new_session(data):
    """Create new session"""
    name = data.get('name') or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        subprocess.run(
            ['goose', 'session', 'start', '-n', name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        emit('session_created', {'name': name, 'status': 'success'})
    except Exception as e:
        emit('error', {'message': f'Failed to create session: {e}'})

@click.command()
@click.option('--port', default=8080, help='Port to run web server on')
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--debug', is_flag=True, help='Run in debug mode')
def main(port, host, debug):
    """Launch Goose Web UI"""
    print(f"🪿 Goose Web UI starting on http://{host}:{port}")
    print(f"Press Ctrl+C to stop")
    
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        allow_unsafe_werkzeug=True
    )

if __name__ == '__main__':
    main()
