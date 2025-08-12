import sys
import os
import json

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGridLayout, QSpacerItem, QSizePolicy,
    QDialog, QMessageBox
)

from models import ServerConfig
from process_manager import ProcessManager
from server_editor_dialog import ServerEditorDialog


class MCPManagerWindow(QMainWindow):
    CONFIG_FILE = "mcp_servers.json"  # Config file in the same folder
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCP Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.setObjectName("MainWindow")

        self.process_manager = ProcessManager()
        self.servers = []  # List of ServerConfig objects
        self.server_rows = {}  # server_id: row_index
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._check_statuses)
        self.status_timer.start(5000)  # Check status every 5 seconds

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Main container for padding
        self.container_widget = QWidget()
        self.container_widget.setObjectName("ContainerWidget")
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setContentsMargins(40, 20, 40, 20)
        self.container_layout.setSpacing(20)
        self.main_layout.addWidget(self.container_widget)

        # Header
        self._create_header()

        # Servers Section
        self._create_servers_section()

        # Spacer to push footer to the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.container_layout.addItem(spacer)

        # Footer
        self._create_footer()

        self.setStyleSheet(self._get_style_sheet())

        # Load servers from config file
        self._load_servers_from_file()

    def _create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 15)

        title_label = QLabel("MCP Manager")
        title_label.setObjectName("MainTitle")

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.visual_editor_button = QPushButton("Visual Editor")
        self.visual_editor_button.setObjectName("HeaderButton")
        self.visual_editor_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.view_json_button = QPushButton("View JSON")
        self.view_json_button.setObjectName("ViewJsonButton")
        self.view_json_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_json_button.clicked.connect(self._view_json)

        header_layout.addWidget(self.visual_editor_button)
        header_layout.addWidget(self.view_json_button)

        self.container_layout.addWidget(header_widget)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setObjectName("Separator")
        self.container_layout.addWidget(line)

        # Connect process manager signals
        self.process_manager.status_changed.connect(self._update_server_status)
        self.process_manager.output_received.connect(self._handle_server_output)
        self.process_manager.error_occurred.connect(self._handle_server_error)

    def _create_servers_section(self):
        servers_container = QWidget()
        servers_layout = QVBoxLayout(servers_container)
        servers_layout.setContentsMargins(0, 20, 0, 0)
        servers_layout.setSpacing(20)

        # Servers Header Bar
        servers_header_bar = QWidget()
        servers_header_layout = QHBoxLayout(servers_header_bar)
        servers_header_layout.setContentsMargins(0, 0, 0, 0)

        servers_title = QLabel("MCP Servers")
        servers_title.setObjectName("SectionTitle")

        servers_header_layout.addWidget(servers_title)
        servers_header_layout.addStretch()

        self.check_all_button = QPushButton("Check All Statuses")
        self.check_all_button.setObjectName("ActionButton")
        self.check_all_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_all_button.clicked.connect(self._check_statuses)

        self.paste_json_button = QPushButton("Paste from JSON")
        self.paste_json_button.setObjectName("ActionButton")
        self.paste_json_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.paste_json_button.clicked.connect(self._import_from_json)

        self.add_server_button = QPushButton("+ Add Server")
        self.add_server_button.setObjectName("AddServerButton")
        self.add_server_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_server_button.clicked.connect(self._add_new_server)

        servers_header_layout.addWidget(self.check_all_button)
        servers_header_layout.addWidget(self.paste_json_button)
        servers_header_layout.addWidget(self.add_server_button)

        servers_layout.addWidget(servers_header_bar)

        # Servers List
        servers_list_widget = QWidget()
        self.grid_layout = QGridLayout(servers_list_widget)
        self.grid_layout.setContentsMargins(0, 10, 0, 0)
        self.grid_layout.setHorizontalSpacing(40)
        self.grid_layout.setVerticalSpacing(15)

        # Set column stretch
        self.grid_layout.setColumnStretch(0, 0)  # Status
        self.grid_layout.setColumnStretch(1, 1)  # Server ID
        self.grid_layout.setColumnStretch(2, 1)  # Command
        self.grid_layout.setColumnStretch(3, 1)  # Arguments
        self.grid_layout.setColumnStretch(4, 1)  # Env Variables
        self.grid_layout.setColumnStretch(5, 0)  # Actions

        self._create_server_list_header()

        # Separator before first item
        line_separator = QFrame()
        line_separator.setFrameShape(QFrame.Shape.HLine)
        line_separator.setObjectName("Separator")
        self.grid_layout.addWidget(line_separator, 1, 0, 1, 6)

        # Servers will be added in _load_sample_data
        self.servers_list_widget = servers_list_widget

        servers_layout.addWidget(servers_list_widget)
        self.container_layout.addWidget(servers_container)

    def _create_server_list_header(self):
        headers = ["Status", "Server ID", "Command", "Arguments", "Env Variables", "Actions"]
        for i, header_text in enumerate(headers):
            label = QLabel(header_text)
            label.setObjectName("GridHeader")
            self.grid_layout.addWidget(label, 0, i, Qt.AlignmentFlag.AlignLeft)

        # Add a row for the "No servers" message
        self.no_servers_label = QLabel("No MCP servers configured. Click '+ Add Server' to get started.")
        self.no_servers_label.setObjectName("NoServersLabel")
        self.grid_layout.addWidget(self.no_servers_label, 2, 0, 1, 6, Qt.AlignmentFlag.AlignCenter)
        self.no_servers_label.hide()
        
        # Note: Don't show the message here - it will be handled after servers are loaded

    def _add_server_row(self, server_config, row):
        # Remove "no servers" message if shown
        if self.no_servers_label.isVisible():
            self.no_servers_label.hide()

        # Status
        status_label = QLabel("Offline")
        if server_config.status == "online":
            status_label.setObjectName("StatusOnline")
        elif server_config.status == "error":
            status_label.setObjectName("StatusError")
        else:
            status_label.setObjectName("StatusOffline")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(status_label, row, 0)
        server_config.status_label = status_label

        # Server ID
        self.grid_layout.addWidget(QLabel(server_config.id), row, 1)

        # Command
        self.grid_layout.addWidget(QLabel(server_config.command), row, 2)

        # Arguments
        args_str = " ".join(server_config.arguments)
        self.grid_layout.addWidget(QLabel(args_str), row, 3)

        # Env Variables
        env_str = ", ".join([f"{k}={v}" for k, v in server_config.env_vars.items()])
        self.grid_layout.addWidget(QLabel(env_str), row, 4)

        # Actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        start_stop_button = QPushButton("Start" if server_config.status == "offline" else "Stop")
        start_stop_button.setObjectName("ActionButton")
        start_stop_button.setCursor(Qt.CursorShape.PointingHandCursor)
        start_stop_button.clicked.connect(lambda: self._toggle_server(server_config))
        server_config.start_stop_button = start_stop_button  # Store reference for status updates

        edit_button = QPushButton("Edit")
        edit_button.setObjectName("ActionButton")
        edit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_button.clicked.connect(lambda: self._edit_server(server_config))

        logs_button = QPushButton("View Logs")
        logs_button.setObjectName("ActionButton")
        logs_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logs_button.clicked.connect(lambda: self._view_logs(server_config))

        delete_button = QPushButton("Delete")
        delete_button.setObjectName("ActionButton")
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_button.clicked.connect(lambda: self._delete_server(server_config))

        actions_layout.addWidget(start_stop_button)
        actions_layout.addWidget(edit_button)
        actions_layout.addWidget(logs_button)
        actions_layout.addWidget(delete_button)

        self.grid_layout.addWidget(actions_widget, row, 5, Qt.AlignmentFlag.AlignRight)
        server_config.actions_widget = actions_widget

        # Row separator
        line_separator = QFrame()
        line_separator.setFrameShape(QFrame.Shape.HLine)
        line_separator.setObjectName("Separator")
        self.grid_layout.addWidget(line_separator, row + 1, 0, 1, 6)

        # Store the row index for this server
        self.server_rows[server_config.id] = row

    def _create_footer(self):
        footer_widget = QWidget()
        footer_widget.setObjectName("Footer")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(0, 10, 0, 10)

        footer_label = QLabel("MCP Manager - Manage your Model Context Protocol servers")
        footer_label.setObjectName("FooterLabel")

        footer_layout.addStretch()
        footer_layout.addWidget(footer_label)
        footer_layout.addStretch()

        self.main_layout.addWidget(footer_widget)

    def _load_servers_from_file(self):
        """Load server configurations from the config file"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    self.servers = []
                    for item in data:
                        if isinstance(item, dict):
                            self.servers.append(ServerConfig.from_dict(item))
                    
                    # Add servers to UI
                    for i, server in enumerate(self.servers):
                        self._add_server_row(server, i + 2)
                    
                    # Show no servers message if list is empty
                    if not self.servers:
                        self._show_no_servers_message()
                    
                    return
            except Exception as e:
                print(f"Error loading config file: {e}")
        
        # If no config file exists or loading failed, load sample data
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample server configurations for demonstration"""
        sample_server1 = ServerConfig(
            id="brave-search",
            name="Brave Search",
            command="npx",
            arguments=["run", "brave"],
            env_vars={"PORT": "3000"},
            working_dir=""
        )

        sample_server2 = ServerConfig(
            id="postgres",
            name="Postgres",
            command="docker",
            arguments=["run", "postgres"],
            env_vars={"POSTGRES_PASSWORD": "secret"},
            working_dir=""
        )

        self.servers = [sample_server1, sample_server2]

        # Add servers to UI
        for i, server in enumerate(self.servers):
            self._add_server_row(server, i + 2)
        
        # Show no servers message if list is empty (shouldn't happen with sample data)
        if not self.servers:
            self._show_no_servers_message()
        
        # Save the sample data to file for future use
        self._save_servers_to_file()
    
    def _save_servers_to_file(self):
        """Save current server configurations to the config file"""
        try:
            configs = [s.to_dict() for s in self.servers]
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(configs, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {e}")

    def _add_new_server(self):
        """Open dialog to add a new server"""
        dialog = ServerEditorDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_config = dialog.get_config()
            self.servers.append(new_config)
            row = len(self.servers) + 1
            self._add_server_row(new_config, row)
            self._save_servers_to_file()

    def _edit_server(self, server_config):
        """Open dialog to edit existing server"""
        dialog = ServerEditorDialog(server_config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_config = dialog.get_config()
            # Update the server config
            server_config.__dict__.update(updated_config.__dict__)
            # TODO: Refresh the row
            self._save_servers_to_file()

    def _delete_server(self, server_config):
        """Delete a server configuration"""
        # Stop server if running
        self.process_manager.stop_server(server_config.id)

        # Remove from list
        self.servers = [s for s in self.servers if s.id != server_config.id]

        # Remove from UI
        row = self.server_rows.get(server_config.id)
        if row:
            # Remove all widgets in the row
            for col in range(6):
                item = self.grid_layout.itemAtPosition(row, col)
                if item and item.widget():
                    item.widget().deleteLater()

            # Remove separator
            sep_row = row + 1
            for col in range(6):
                item = self.grid_layout.itemAtPosition(sep_row, col)
                if item and item.widget():
                    item.widget().deleteLater()

            # Remove row mapping
            del self.server_rows[server_config.id]

        # Show "no servers" message if empty
        if not self.servers:
            self._show_no_servers_message()
        
        # Save changes to file
        self._save_servers_to_file()

    def _toggle_server(self, server_config):
        """Start or stop a server"""
        if server_config.status == "offline":
            self.process_manager.start_server(server_config)
            # Automatically open log viewer to show startup progress
            self._view_logs(server_config)
        else:
            self.process_manager.stop_server(server_config.id)

    def _check_statuses(self):
        """Check status of all servers"""
        for server in self.servers:
            status = self.process_manager.get_status(server.id)
            self._update_server_status(server.id, status)

    def _update_server_status(self, server_id, status):
        """Update UI for a server's status"""
        server = next((s for s in self.servers if s.id == server_id), None)
        if not server:
            return

        server.status = status
        
        # Update status label
        if server.status_label:
            server.status_label.setText(status.capitalize())

            # Update style
            if status == "online":
                server.status_label.setObjectName("StatusOnline")
            elif status == "error":
                server.status_label.setObjectName("StatusError")
            else:
                server.status_label.setObjectName("StatusOffline")
            server.status_label.style().unpolish(server.status_label)
            server.status_label.style().polish(server.status_label)
        
        # Update start/stop button text
        if hasattr(server, 'start_stop_button') and server.start_stop_button:
            if status == "online":
                server.start_stop_button.setText("Stop")
            else:
                server.start_stop_button.setText("Start")

    def _handle_server_output(self, server_id, output):
        """Handle server output without showing alerts"""
        print(f"Server {server_id} output: {output}")
        # Store output in ProcessManager logs
        if hasattr(self.process_manager, 'logs') and server_id in self.process_manager.logs:
            self.process_manager.logs[server_id].append(output)
            self.process_manager.logs_updated.emit(server_id)

    def _handle_server_error(self, server_id, error):
        """Handle server errors without showing alerts"""
        print(f"Server {server_id} error: {error}")
        self._update_server_status(server_id, "error")
        # Store error in ProcessManager logs
        if hasattr(self.process_manager, 'logs') and server_id in self.process_manager.logs:
            self.process_manager.logs[server_id].append(f"ERROR: {error}")
            self.process_manager.logs_updated.emit(server_id)

    def _view_logs(self, server_config):
        """View logs for a server"""
        from log_viewer_dialog import LogViewerDialog
        logs = self.process_manager.get_logs(server_config.id)
        dialog = LogViewerDialog(server_config.id, logs, self)
        dialog.exec()

    def _view_json(self):
        """Show JSON representation of all servers with export option"""
        from json_io import build_json_view_dialog
        dialog = build_json_view_dialog(self, self.servers, self._export_to_json)
        dialog.exec()

    def _import_from_json(self):
        """Import server configurations from JSON"""
        from json_io import select_and_load_servers
        new_servers = select_and_load_servers(self)
        if not new_servers:
            return

        # Stop all running servers
        for server in self.servers:
            self.process_manager.stop_server(server.id)

        # Replace the current server list
        self.servers = new_servers

        # Clear the current UI grid
        self._clear_servers_grid()

        # Rebuild the UI with the new servers
        for i, server in enumerate(self.servers):
            self._add_server_row(server, i + 2)
        
        # Save the imported servers to file
        self._save_servers_to_file()

    def _export_to_json(self):
        """Export server configurations to JSON file"""
        from json_io import select_and_save_servers
        select_and_save_servers(self, self.servers)

    def _clear_servers_grid(self):
        """Clear the servers grid except the header and separator"""
        # Remove all rows except the first two (header and separator)
        for row in range(self.grid_layout.rowCount() - 1, 1, -1):
            for col in range(self.grid_layout.columnCount()):
                item = self.grid_layout.itemAtPosition(row, col)
                if item and item.widget():
                    item.widget().deleteLater()

        # Clear the server_rows dictionary
        self.server_rows = {}

        # Show the "no servers" message if the list is empty
        if not self.servers:
            self._show_no_servers_message()
    
    def _show_no_servers_message(self):
        """Show the no servers message, creating it if necessary"""
        try:
            # Check if the label still exists and is valid
            if hasattr(self, 'no_servers_label') and self.no_servers_label is not None:
                self.no_servers_label.show()
            else:
                # Recreate the label if it was deleted
                self.no_servers_label = QLabel("No MCP servers configured. Click '+ Add Server' to get started.")
                self.no_servers_label.setObjectName("NoServersLabel")
                self.grid_layout.addWidget(self.no_servers_label, 2, 0, 1, 6, Qt.AlignmentFlag.AlignCenter)
                self.no_servers_label.show()
        except RuntimeError:
            # Handle case where the widget was deleted
            self.no_servers_label = QLabel("No MCP servers configured. Click '+ Add Server' to get started.")
            self.no_servers_label.setObjectName("NoServersLabel")
            self.grid_layout.addWidget(self.no_servers_label, 2, 0, 1, 6, Qt.AlignmentFlag.AlignCenter)
            self.no_servers_label.show()

    def _get_style_sheet(self):
        # Delegated to external module for maintainability
        from ui_styles import get_style_sheet
        return get_style_sheet()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MCPManagerWindow()
    window.show()
    sys.exit(app.exec())
