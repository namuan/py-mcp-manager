import json
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGridLayout, QSpacerItem, QSizePolicy,
    QDialog, QMessageBox, QFileDialog, QTextEdit
)

from models import ServerConfig
from process_manager import ProcessManager
from server_editor_dialog import ServerEditorDialog


class MCPManagerWindow(QMainWindow):
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
        
        # Load sample data for demonstration
        self._load_sample_data()

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
        self.grid_layout.setColumnStretch(0, 0) # Status
        self.grid_layout.setColumnStretch(1, 1) # Server ID
        self.grid_layout.setColumnStretch(2, 1) # Command
        self.grid_layout.setColumnStretch(3, 1) # Arguments
        self.grid_layout.setColumnStretch(4, 1) # Env Variables
        self.grid_layout.setColumnStretch(5, 0) # Actions

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
        
        # Show message immediately if no servers
        if not self.servers:
            self.no_servers_label.show()

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
            
    def _add_new_server(self):
        """Open dialog to add a new server"""
        dialog = ServerEditorDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_config = dialog.get_config()
            self.servers.append(new_config)
            row = len(self.servers) + 1
            self._add_server_row(new_config, row)
            
    def _edit_server(self, server_config):
        """Open dialog to edit existing server"""
        dialog = ServerEditorDialog(server_config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_config = dialog.get_config()
            # Update the server config
            server_config.__dict__.update(updated_config.__dict__)
            # TODO: Refresh the row
            
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
            self.no_servers_label.show()
            
    def _toggle_server(self, server_config):
        """Start or stop a server"""
        if server_config.status == "offline":
            self.process_manager.start_server(server_config)
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
            
    def _handle_server_output(self, server_id, output):
        """Handle server output with optional notification for important messages"""
        print(f"Server {server_id} output: {output}")
        
        # Check for important keywords in output
        important_keywords = ["error", "fail", "warning", "exception"]
        if any(kw in output.lower() for kw in important_keywords):
            # Find server name for notification
            server = next((s for s in self.servers if s.id == server_id), None)
            server_name = server.name if server else server_id
            
            # Show warning notification
            QMessageBox.warning(
                self,
                "Server Output",
                f"Server '{server_name}' reported:\n\n{output[:500]}"  # Limit message length
            )
        
    def _handle_server_error(self, server_id, error):
        """Handle server errors with user notification"""
        print(f"Server {server_id} error: {error}")
        self._update_server_status(server_id, "error")
        
        # Find server name for notification
        server = next((s for s in self.servers if s.id == server_id), None)
        server_name = server.name if server else server_id
        
        # Show critical error notification
        QMessageBox.critical(
            self,
            "Server Error",
            f"Server '{server_name}' encountered an error:\n\n{error}"
        )
        
    def _view_logs(self, server_config):
        """View logs for a server"""
        from log_viewer_dialog import LogViewerDialog
        logs = self.process_manager.get_logs(server_config.id)
        dialog = LogViewerDialog(server_config.id, logs, self)
        dialog.exec()
        
    def _view_json(self):
        """Show JSON representation of all servers with export option"""
        configs = [s.to_dict() for s in self.servers]
        json_str = json.dumps(configs, indent=2)
        
        # Show in a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Server Configuration JSON")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout()
        
        text_edit = QTextEdit()
        text_edit.setPlainText(json_str)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Add export button
        export_btn = QPushButton("Export to File")
        export_btn.setObjectName("ActionButton")
        export_btn.clicked.connect(self._export_to_json)
        layout.addWidget(export_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
        
    def _import_from_json(self):
        """Import server configurations from JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Server Configuration",
            "",
            "JSON Files (*.json)"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Validate the JSON structure
            if not isinstance(data, list):
                raise ValueError("Invalid configuration format: expected a list of servers")
                
            new_servers = []
            for item in data:
                if not isinstance(item, dict):
                    raise ValueError("Each server configuration must be a dictionary")
                # Create ServerConfig from dictionary
                new_servers.append(ServerConfig.from_dict(item))
                
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
                
            QMessageBox.information(self, "Import Successful", f"Imported {len(new_servers)} servers")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import configuration: {str(e)}")
            
    def _export_to_json(self):
        """Export server configurations to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Server Configuration",
            "",
            "JSON Files (*.json)"
        )
        if not file_path:
            return
            
        try:
            # Ensure .json extension
            if not file_path.endswith('.json'):
                file_path += '.json'
                
            configs = [s.to_dict() for s in self.servers]
            with open(file_path, 'w') as f:
                json.dump(configs, f, indent=2)
                
            QMessageBox.information(self, "Export Successful", "Configuration exported successfully")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export configuration: {str(e)}")
            
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
            self.no_servers_label.show()

    def _get_style_sheet(self):
        return """
            #MainWindow {
                background-color: #F8F9FA;
            }
            #ContainerWidget {
                background-color: #FFFFFF;
                border: 1px solid #DEE2E6;
                border-radius: 8px;
            }
            #MainTitle {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 28px;
                font-weight: 600;
                color: #212529;
            }
            #SectionTitle {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 20px;
                font-weight: 600;
                color: #212529;
            }
            #HeaderButton, #ActionButton {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: #FFFFFF;
                color: #212529;
                border: 1px solid #CED4DA;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
            }
            #HeaderButton:hover, #ActionButton:hover {
                background-color: #F8F9FA;
            }
            #ViewJsonButton {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: #E9ECEF;
                color: #212529;
                border: 1px solid #E9ECEF;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
            }
             #ViewJsonButton:hover {
                background-color: #DEE2E6;
                border-color: #DEE2E6;
            }
            #AddServerButton {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: #E9ECEF;
                color: #212529;
                border: 1px solid #CED4DA;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 14px;
                font-weight: 500;
            }
            #AddServerButton:hover {
                background-color: #DEE2E6;
            }
            .QFrame#Separator {
                background-color: #E9ECEF;
                height: 1px;
            }
            #GridHeader {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 13px;
                font-weight: 600;
                color: #495057;
            }
            QLabel {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                color: #212529;
            }
            #StatusOffline {
                background-color: #DC3545;
                color: white;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            #StatusOnline {
                background-color: #28A745;
                color: white;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            #StatusError {
                background-color: #FFC107;
                color: black;
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
            }
            #Footer {
                background-color: #F8F9FA;
                border-top: 1px solid #DEE2E6;
            }
            #FooterLabel {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                color: #6C757D;
            }
            #NoServersLabel {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 16px;
                color: #6C757D;
                font-style: italic;
                padding: 20px;
            }
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MCPManagerWindow()
    window.show()
    sys.exit(app.exec())