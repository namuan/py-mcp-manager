# MCP Manager User Guide

## Overview
MCP Manager is a desktop application for managing Model Context Protocol (MCP) servers. It provides an intuitive interface to configure, monitor, and manage your MCP servers.

## Key Features
- 🖥️ Visual Server Management
- 🔄 Real-time Status Monitoring
- 🛠️ Advanced Configuration
- 📋 JSON Import/Export
- 🔍 Direct JSON Editing
- 📜 Server Log Viewing

## Getting Started
1. Launch the application
2. Click "+ Add Server" to create your first server configuration
3. Fill in the server details:
   - Server ID
   - Command
   - Arguments
   - Environment variables
   - Working directory
4. Click "Save"

## Managing Servers
- **Start/Stop**: Click the Start/Stop button in the Actions column
- **Edit**: Click Edit to modify server configuration
- **Delete**: Click Delete to remove a server
- **View Logs**: Click View Logs to see server output

## Importing/Exporting
- **Import**: Click "Paste from JSON" to import server configurations
- **Export**: Click "View JSON" then "Export to File"

## Status Indicators
- <span style="color:green">● Online</span>: Server is running
- <span style="color:red">● Offline</span>: Server is stopped
- <span style="color:orange">● Error</span>: Server encountered an error
- <span style="color:yellow">● Starting</span>: Server is starting up

## Troubleshooting
- Check server logs for error messages
- Verify command paths and arguments
- Ensure environment variables are correctly set
- Check for error notifications in the application

## Keyboard Shortcuts
- Ctrl+N: Add new server
- Ctrl+E: Edit selected server
- Ctrl+S: Save configurations
- Ctrl+Q: Quit application