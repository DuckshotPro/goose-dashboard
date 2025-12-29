# 🪿 Goose Dashboard

**Hybrid Terminal TUI + Web UI wrapper for Goose CLI** - Chat sessions, MCP extensions, and remote management

<div align="center">

![Goose Dashboard](https://img.shields.io/badge/Goose-Dashboard-00D9FF?style=for-the-badge&logo=go&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

## 🚀 Features

### 🖥️ Terminal TUI (Text User Interface)
- ✅ **Chat Bubble Interface** - Conversational UI in your terminal
- ✅ **Session Management** - Save/resume/switch between chats
- ✅ **Live Streaming** - Real-time Goose responses
- ✅ **Keyboard Shortcuts** - `Ctrl+N` new, `Ctrl+S` save, `Ctrl+H` history
- ✅ **MCP Extensions** - Built-in support for developer, github, computer tools
- ✅ **SQLite Integration** - Persistent chat history

### 🌐 Web UI (Browser Dashboard)
- ✅ **Remote Access** - Control Goose from any device
- ✅ **Configuration Panel** - Set providers, API keys, models
- ✅ **Session Browser** - Visual session management
- ✅ **Extension Manager** - Configure MCP servers
- ✅ **Recipe Editor** - Save multi-step workflows
- ✅ **Real-time Logs** - Monitor Goose activity

### 🔗 Hybrid Mode
- Run both TUI + Web UI simultaneously
- TUI for quick terminal access
- Web UI for configuration and remote management
- Shared session state via SQLite

## 📦 Installation

### Prerequisites
```bash
# Install Goose CLI first
pip install goose-ai
# or
pipx install goose-ai
```

### Quick Install
```bash
# Clone repo
git clone https://github.com/DuckshotPro/goose-dashboard.git
cd goose-dashboard

# Install dependencies
pip install -r requirements.txt

# Make TUI executable
chmod +x goose-tui.py
```

## 🎯 Usage

### Terminal TUI Only
```bash
# Launch terminal interface
./goose-tui.py

# Or with python
python goose-tui.py
```

### Web UI Only
```bash
# Start web server (default port 8080)
python goose-web.py

# Custom port
python goose-web.py --port 3000

# Open browser to http://localhost:8080
```

### Hybrid Mode (Both)
```bash
# Start both interfaces
python goose-hybrid.py

# TUI runs in terminal
# Web UI available at http://localhost:8080
```

## ⌨️ TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+N` | New chat session |
| `Ctrl+S` | Save current session |
| `Ctrl+R` | Resume last session |
| `Ctrl+H` | Show history |
| `Ctrl+E` | List extensions |
| `Ctrl+C` | Quit |
| `Enter` | Send message |
| `F1` | Help |

## 🔌 MCP Extensions

Built-in extensions available:
- **developer** - Code analysis, debugging
- **github** - GitHub operations
- **computer** - System control
- **screen** - Screen capture/OCR

Add extensions via Web UI or mention in prompts:
```
"Using the developer extension, analyze this Python code..."
```

## 📋 Configuration

### TUI Config
Config stored in `~/.config/goose/`
- Sessions: `sessions.db` (SQLite)
- Settings: `config.yaml`

### Web UI Config
Edit `config.json` or use web interface:
```json
{
  "provider": "openai",
  "model": "gpt-4",
  "api_key": "sk-...",
  "port": 8080,
  "host": "localhost"
}
```

## 🏗️ Architecture

```
goose-dashboard/
├── goose-tui.py       # Terminal TUI (Textual)
├── goose-web.py       # Web UI server (Flask)
├── goose-hybrid.py    # Combined launcher
├── templates/
│   └── dashboard.html # Web UI frontend
├── static/
│   ├── css/
│   └── js/
├── requirements.txt
└── README.md
```

## 🔧 Development

### Run Tests
```bash
python -m pytest tests/
```

### Hot Reload (Web UI)
```bash
FLASK_ENV=development python goose-web.py
```

### Debug TUI
```bash
textual run --dev goose-tui.py
```

## 🚀 Deployment

### Self-Hosted VPS
```bash
# Run as systemd service
sudo cp goose-dashboard.service /etc/systemd/system/
sudo systemctl enable goose-dashboard
sudo systemctl start goose-dashboard

# Access via your-server.com:8080
```

### Docker
```bash
# Build image
docker build -t goose-dashboard .

# Run container
docker run -p 8080:8080 -v ~/.config/goose:/root/.config/goose goose-dashboard
```

## 🤝 Contributing

Contributions welcome! Areas to improve:
- [ ] Real-time websocket streaming for web UI
- [ ] Multi-user session support
- [ ] Plugin system for custom extensions
- [ ] Mobile-responsive web UI
- [ ] Export sessions to markdown/JSON
- [ ] Voice input support

## 📝 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- [Goose CLI](https://github.com/block/goose) by Block
- [Textual](https://github.com/Textualize/textual) TUI framework
- [Rich](https://github.com/Textualize/rich) terminal formatting

## 🐛 Issues

Found a bug? [Open an issue](https://github.com/DuckshotPro/goose-dashboard/issues)

---

<div align="center">

**Made with ❤️ for the Goose community**

[Report Bug](https://github.com/DuckshotPro/goose-dashboard/issues) · [Request Feature](https://github.com/DuckshotPro/goose-dashboard/issues)

</div>