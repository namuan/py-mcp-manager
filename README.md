# MCP Manager

A desktop application for managing Model Context Protocol (MCP) servers with an intuitive graphical interface.

![MCP Manager Screenshot](screenshot.png) <!-- TODO: Add actual screenshot -->

## Overview

MCP Manager simplifies the process of configuring, starting, stopping, and monitoring multiple MCP servers from a single interface. Built with Python and PyQt6, it provides real-time status monitoring, configuration management, and log viewing capabilities.

## Features

- 🖥️ **Visual Server Management**: Intuitive GUI for managing all your MCP servers
- 🔄 **Real-time Status Monitoring**: Live status updates for each server
- 🛠️ **Advanced Configuration**: Full control over server commands, arguments, and environment variables
- 📋 **JSON Import/Export**: Easily share configurations between team members
- 🔍 **Direct JSON Editing**: Advanced users can edit configurations directly in JSON
- 📜 **Server Log Viewing**: Monitor server output in real-time
- 🧬 **Clone Servers**: Duplicate existing server configurations with one click

## Installation

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/mcp-manager.git
cd mcp-manager

# Install dependencies
make install

# Run the application
make run
```

### Using pip

```bash
# Clone the repository
git clone https://github.com/your-username/mcp-manager.git
cd mcp-manager

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Run the application
python mcp_manager.py
```

## Usage

1. Launch the application using one of the methods above
2. Click "+ Add Server" to create your first server configuration
3. Fill in the server details:
   - Server ID (unique identifier)
   - Display Name
   - Command to run the server
   - Arguments
   - Environment variables
   - Working directory
4. Click "Save"
5. Use the "Start" button to launch your server
6. Monitor logs and status in real-time

## Configuration

Server configurations are stored in a platform-appropriate user data directory:

- **macOS**: `~/Library/Application Support/MCP Manager/mcp_servers.json`
- **Windows**: `%APPDATA%\MCP Manager\mcp_servers.json`
- **Linux**: `~/.local/share/mcp-manager/mcp_servers.json`

You can:

- Manually edit this file when the application is not running
- Use the built-in JSON editor (View JSON button)
- Import/export configurations using the JSON import/export features

## Development

### Project Structure

```
mcp-manager/
├── mcp_manager.py       # Main application
├── models.py            # Data models
├── process_manager.py   # Server process management
├── server_editor_dialog.py  # Server configuration dialog
├── log_viewer_dialog.py # Log viewer dialog
├── json_io.py           # JSON import/export utilities
├── ui_styles.py         # Application styling
├── mcp_servers.json     # Server configurations (auto-generated)
├── USER_GUIDE.md        # User documentation
├── Makefile             # Build and run commands
├── pyproject.toml       # Project dependencies
├── mcp_manager.spec     # PyInstaller spec file for macOS app bundle
└── README.md            # This file
```

### Dependencies

- PyQt6: GUI framework
- Additional dependencies are listed in `pyproject.toml`

### Available Make Commands

- `make install` - Install dependencies and pre-commit hooks
- `make run` - Run the application
- `make check` - Run code quality tools
- `make build` - Build wheel file
- `make package` - Create macOS .app bundle
- `make install-macosx` - Install the app to /Applications folder
- `make help` - Show all available commands

### Building

To create a standalone executable:

```bash
# Create macOS .app bundle
make package

# Install to Applications folder
make install-macosx
```

### Code Quality

This project uses several tools to ensure code quality:

- **ruff**: Fast Python linter and formatter
- **pre-commit**: Framework for managing git hooks
- **pytest**: Testing framework

Run code quality checks with:

```bash
make check
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io) for the specification
- PyQt6 for the GUI framework
- All contributors to this project
