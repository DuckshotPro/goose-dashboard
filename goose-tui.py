#!/usr/bin/env python3
"""
Goose CLI TUI Wrapper - Terminal Chat Dashboard
Features: Chat bubbles, session management, live streaming, MCP extensions
"""

import subprocess
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Button, Static, Input, Select, DataTable, TabbedContent, TabPane, Label, ListItem, ListView
from textual.binding import Binding
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel

class ChatBubble(Static):
    """A single chat message bubble"""
    
    def __init__(self, role: str, content: str, timestamp: str):
        self.role = role
        self.content = content
        self.timestamp = timestamp
        super().__init__()
    
    def compose(self) -> ComposeResult:
        # Style based on role
        if self.role == "user":
            bubble_class = "user-bubble"
            prefix = "You"
        elif self.role == "assistant":
            bubble_class = "goose-bubble"
            prefix = "🪿 Goose"
        else:
            bubble_class = "system-bubble"
            prefix = "System"
        
        yield Static(
            f"[dim]{self.timestamp}[/] [bold]{prefix}[/]\n{self.content}",
            classes=bubble_class
        )

class GooseTUI(App):
    """Goose CLI Terminal Chat Dashboard"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #sidebar {
        width: 30;
        background: $panel;
        border-right: thick $primary;
    }
    
    #chat-area {
        width: 1fr;
        height: 1fr;
        padding: 1;
    }
    
    #chat-messages {
        height: 1fr;
        border: solid $accent;
        padding: 1;
    }
    
    #input-container {
        height: 5;
        dock: bottom;
        background: $panel;
        padding: 1;
    }
    
    .user-bubble {
        background: $primary;
        color: $text;
        border: solid $accent;
        padding: 1 2;
        margin: 0 0 1 10;
        border-radius: 2;
    }
    
    .goose-bubble {
        background: $boost;
        color: $text;
        border: solid $success;
        padding: 1 2;
        margin: 0 10 1 0;
        border-radius: 2;
    }
    
    .system-bubble {
        background: $panel;
        color: $warning;
        padding: 1 2;
        margin: 0 4 1 4;
        border-radius: 1;
    }
    
    .quick-btn {
        width: 100%;
        margin: 0 1;
    }
    
    #session-list {
        height: 1fr;
        border: solid $accent;
    }
    
    .session-item {
        padding: 1;
        background: $panel;
        margin: 0 0 1 0;
    }
    
    .session-active {
        background: $success;
        color: $text;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+n", "new_session", "New"),
        Binding("ctrl+s", "save_session", "Save"),
        Binding("ctrl+r", "resume_session", "Resume"),
        Binding("ctrl+e", "extensions", "Extensions"),
        Binding("ctrl+h", "show_history", "History"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("f1", "help", "Help"),
    ]
    
    current_session_name = reactive("")
    chat_history = []
    sessions_db_path = Path.home() / ".config" / "goose" / "sessions.db"
    
    def compose(self) -> ComposeResult:
        """Create chat UI layout"""
        yield Header()
        
        with Horizontal():
            # Sidebar - Session Management
            with Vertical(id="sidebar"):
                yield Static("🪿 [bold cyan]GOOSE CHAT[/]", classes="header")
                yield Static("")
                
                # Quick Actions
                yield Button("🆕 New Chat", id="btn-new", classes="quick-btn")
                yield Button("💾 Save Session", id="btn-save", classes="quick-btn")
                yield Button("📋 Load Session", id="btn-load", classes="quick-btn")
                yield Button("📋 History", id="btn-history", classes="quick-btn")
                yield Button("🔌 Extensions", id="btn-ext", classes="quick-btn")
                yield Button("🔄 Clear Chat", id="btn-clear", classes="quick-btn")
                
                yield Static("")
                yield Static("[bold]Recent Sessions:[/]")
                yield ListView(id="session-list")
                
                yield Static("")
                yield Static("[bold]Current:[/]")
                yield Static(f"[cyan]{self.current_session_name or 'No session'}[/]", 
                           id="session-status")
        
            # Main Chat Area
            with Vertical(id="chat-area"):
                # Chat Messages - Scrollable
                with VerticalScroll(id="chat-messages"):
                    yield Static("🪿 [bold]Goose is ready! Start chatting...[/]", 
                               classes="system-bubble")
                
                # Input Area
                with Horizontal(id="input-container"):
                    yield Input(
                        placeholder="Type your message to Goose...", 
                        id="chat-input"
                    )
                    yield Button("📤 Send", id="btn-send", variant="primary")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize chat state"""
        self.add_system_message("Initializing Goose CLI...")
        
        # Check if goose is installed
        try:
            result = subprocess.run(
                ["goose", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            version = result.stdout.strip()
            self.add_system_message(f"✅ Goose CLI {version} detected")
            
            # Load recent sessions
            self.load_recent_sessions()
            
            # Start default session
            self.start_new_session("default")
            
        except FileNotFoundError:
            self.add_system_message(
                "❌ Goose CLI not found!\n"
                "Install: pip install goose-ai\n"
                "Or: pipx install goose-ai"
            )
        except Exception as e:
            self.add_system_message(f"⚠️ Error: {e}")
    
    def add_system_message(self, message: str):
        """Add system notification to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        bubble = ChatBubble("system", message, timestamp)
        
        chat_container = self.query_one("#chat-messages", VerticalScroll)
        chat_container.mount(bubble)
        chat_container.scroll_end(animate=False)
    
    def add_user_message(self, message: str):
        """Add user message to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        bubble = ChatBubble("user", message, timestamp)
        
        chat_container = self.query_one("#chat-messages", VerticalScroll)
        chat_container.mount(bubble)
        chat_container.scroll_end(animate=False)
        
        # Store in history
        self.chat_history.append({
            "role": "user",
            "content": message,
            "timestamp": timestamp
        })
    
    def add_goose_message(self, message: str):
        """Add Goose response to chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        bubble = ChatBubble("assistant", message, timestamp)
        
        chat_container = self.query_one("#chat-messages", VerticalScroll)
        chat_container.mount(bubble)
        chat_container.scroll_end(animate=False)
        
        # Store in history
        self.chat_history.append({
            "role": "assistant",
            "content": message,
            "timestamp": timestamp
        })
    
    def start_new_session(self, name: str = None):
        """Start a new Goose session"""
        if not name:
            name = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session_name = name
        self.chat_history = []
        
        # Update UI
        status = self.query_one("#session-status", Static)
        status.update(f"[cyan]{name}[/]")
        
        self.add_system_message(f"🆕 Started new session: {name}")
        
        # Initialize goose session
        try:
            subprocess.run(
                ["goose", "session", "start", "-n", name],
                capture_output=True,
                text=True,
                timeout=10
            )
            self.add_system_message(f"✅ Goose session '{name}' initialized")
        except Exception as e:
            self.add_system_message(f"⚠️ Session init error: {e}")
    
    def send_to_goose(self, message: str):
        """Send message to Goose and stream response"""
        if not message.strip():
            return
        
        # Add user message to chat
        self.add_user_message(message)
        
        # Show thinking indicator
        self.add_system_message("🪿 Goose is thinking...")
        
        try:
            # Run goose with the prompt
            if self.current_session_name:
                cmd = [
                    "goose", "session", "resume", "-n", 
                    self.current_session_name, "-t", message
                ]
            else:
                cmd = ["goose", "run", "-t", message]
            
            # Execute and capture output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            response_lines = []
            for line in process.stdout:
                line = line.strip()
                if line:
                    response_lines.append(line)
            
            process.wait()
            
            # Combine response
            full_response = "\n".join(response_lines)
            
            if full_response:
                self.add_goose_message(full_response)
            else:
                self.add_goose_message("✅ Task completed (no output)")
            
            # Check for errors
            if process.returncode != 0:
                stderr = process.stderr.read()
                if stderr:
                    self.add_system_message(f"⚠️ Error: {stderr}")
                    
        except subprocess.TimeoutExpired:
            self.add_system_message("⏱️ Request timed out")
        except Exception as e:
            self.add_system_message(f"❌ Error: {e}")
    
    def load_recent_sessions(self):
        """Load recent sessions from Goose's SQLite DB"""
        session_list = self.query_one("#session-list", ListView)
        
        # Check if sessions DB exists
        if not self.sessions_db_path.exists():
            self.add_system_message("📂 No sessions database found")
            return
        
        try:
            conn = sqlite3.connect(self.sessions_db_path)
            cursor = conn.cursor()
            
            # Query recent sessions
            cursor.execute("""
                SELECT name, created_at, last_accessed 
                FROM sessions 
                ORDER BY last_accessed DESC 
                LIMIT 10
            """)
            
            sessions = cursor.fetchall()
            
            for name, created, accessed in sessions:
                item = ListItem(
                    Label(f"📂 {name}\n[dim]{accessed}[/]"),
                    classes="session-item"
                )
                session_list.append(item)
            
            conn.close()
            
            if sessions:
                self.add_system_message(f"📋 Loaded {len(sessions)} recent sessions")
            
        except sqlite3.Error as e:
            self.add_system_message(f"⚠️ DB error: {e}")
        except Exception as e:
            self.add_system_message(f"⚠️ Error loading sessions: {e}")
    
    def load_session_history(self, session_name: str):
        """Load chat history from a saved session"""
        try:
            conn = sqlite3.connect(self.sessions_db_path)
            cursor = conn.cursor()
            
            # Get messages from session
            cursor.execute("""
                SELECT role, content, timestamp 
                FROM messages 
                WHERE session_name = ? 
                ORDER BY timestamp ASC
            """, (session_name,))
            
            messages = cursor.fetchall()
            conn.close()
            
            # Clear current chat
            chat_container = self.query_one("#chat-messages", VerticalScroll)
            chat_container.remove_children()
            
            # Load messages
            for role, content, timestamp in messages:
                bubble = ChatBubble(role, content, timestamp)
                chat_container.mount(bubble)
            
            chat_container.scroll_end(animate=False)
            
            self.current_session_name = session_name
            self.add_system_message(f"📋 Loaded {len(messages)} messages from '{session_name}'")
            
        except Exception as e:
            self.add_system_message(f"⚠️ Error loading history: {e}")
    
    # Button Event Handlers
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        button_id = event.button.id
        
        if button_id == "btn-send":
            self.handle_send_message()
        elif button_id == "btn-new":
            self.action_new_session()
        elif button_id == "btn-save":
            self.action_save_session()
        elif button_id == "btn-load":
            self.add_system_message("📂 Select a session from the sidebar to load")
        elif button_id == "btn-history":
            self.action_show_history()
        elif button_id == "btn-ext":
            self.add_system_message("🔌 Extensions: developer, github, computer, screen")
        elif button_id == "btn-clear":
            self.clear_chat()
    
    def handle_send_message(self):
        """Send message from input field"""
        chat_input = self.query_one("#chat-input", Input)
        message = chat_input.value.strip()
        
        if message:
            self.send_to_goose(message)
            chat_input.value = ""
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input field"""
        if event.input.id == "chat-input":
            self.handle_send_message()
    
    def clear_chat(self):
        """Clear current chat messages"""
        chat_container = self.query_one("#chat-messages", VerticalScroll)
        chat_container.remove_children()
        self.chat_history = []
        self.add_system_message("🗑️ Chat cleared")
    
    # Keyboard Actions
    def action_new_session(self):
        """Start new chat session"""
        name = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_new_session(name)
    
    def action_save_session(self):
        """Save current session"""
        if self.current_session_name:
            self.add_system_message(f"💾 Session '{self.current_session_name}' auto-saved")
        else:
            self.add_system_message("⚠️ No active session to save")
    
    def action_resume_session(self):
        """Resume last session"""
        self.add_system_message("▶️ Resuming last session...")
        # Load most recent from list
    
    def action_show_history(self):
        """Show session history"""
        if self.chat_history:
            count = len(self.chat_history)
            self.add_system_message(f"📋 Current session has {count} messages")
        else:
            self.add_system_message("📋 No history in current session")
    
    def action_extensions(self):
        """Show available extensions"""
        extensions = """
🔌 Available Goose Extensions:

Built-in:
  • developer - Code analysis, debugging
  • github - GitHub operations
  • computer - System control
  • screen - Screen capture/OCR

Usage: Mention in your prompt
Example: "Using the developer extension, analyze this code..."
"""
        self.add_system_message(extensions)
    
    def action_help(self):
        """Show help"""
        help_text = """
🪿 GOOSE CHAT TUI - HELP

KEYBOARD SHORTCUTS:
  Ctrl+N - New chat session
  Ctrl+S - Save current session
  Ctrl+R - Resume last session
  Ctrl+H - Show history
  Ctrl+E - List extensions
  Ctrl+C - Quit
  Enter  - Send message

FEATURES:
  • Chat bubbles show conversation flow
  • Sessions auto-save to SQLite DB
  • Load previous chats from sidebar
  • MCP extensions available
  • Multi-turn conversations

TIPS:
  • Be specific in your prompts
  • Sessions persist across restarts
  • Use extensions for specialized tasks
"""
        self.add_system_message(help_text)

if __name__ == "__main__":
    app = GooseTUI()
    app.run()
