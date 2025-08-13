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

- Python 3.11 or higher
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

Server configurations are stored in `mcp_servers.json` in the application directory. You can:

- Manually edit this file when the application is not running
- Use the built-in JSON editor (View JSON button)
- Import/export configurations using the JSON import/export features

## License

This project is licensed under the MIT License - see the LICENSE file for details.
