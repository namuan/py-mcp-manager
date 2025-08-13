import json
import os
import sys

from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from models import ServerConfig
from process_manager import ProcessManager
from server_editor_dialog import ServerEditorDialog


class ServerListItemWidget(QWidget):
    def __init__(self, server_config: ServerConfig, parent=None):
        super().__init__(parent)
        self.server_id = server_config.id
        self._status = getattr(server_config, "status", "offline") or "offline"

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(6)

        # Status dot
        self.dot = QLabel()
        self.dot.setFixedSize(12, 12)
        self.dot.setObjectName("StatusDot")
        self.dot.setToolTip(self._status.capitalize())
        self._apply_dot_style(self._status)

        # Display Name only (hide ID in the list)
        self.name_label = QLabel(server_config.name)
        self.name_label.setObjectName("ServerNameLabel")

        text_box = QVBoxLayout()
        text_box.setContentsMargins(0, 0, 0, 0)
        text_box.setSpacing(0)
        text_row = QHBoxLayout()
        text_row.setContentsMargins(0, 0, 0, 0)
        text_row.setSpacing(6)
        text_row.addWidget(self.name_label)
        text_row.addStretch()
        text_box.addLayout(text_row)

        layout.addWidget(self.dot)
        layout.addLayout(text_box)
        layout.addStretch()
        self.setObjectName("ServerListItem")

    def _apply_dot_style(self, status: str):
        color = "#ADB5BD"  # default/offline
        if status == "online":
            color = "#28A745"  # green
        elif status == "starting":
            color = "#FFC107"  # yellow
        elif status == "error":
            color = "#DC3545"  # red
        # circle using border-radius
        self.dot.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        self.dot.setToolTip(status.capitalize())

    def update_status(self, status: str):
        self._status = status
        self._apply_dot_style(status)


class ServerEditorPanel(QWidget):
    saved = pyqtSignal(ServerConfig)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        self.id_input = QLineEdit()
        form_layout.addRow("Server ID:", self.id_input)

        self.name_input = QLineEdit()
        form_layout.addRow("Display Name:", self.name_input)

        self.command_input = QLineEdit()
        form_layout.addRow("Command:", self.command_input)

        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_directory)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(browse_btn)
        form_layout.addRow("Working Directory:", dir_layout)

        layout.addLayout(form_layout)

        # Arguments table
        args_label = QLabel("Arguments:")
        layout.addWidget(args_label)
        self.args_table = QTableWidget()
        self.args_table.setColumnCount(1)
        self.args_table.setHorizontalHeaderLabels(["Argument"])
        self.args_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.args_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        args_btns = QHBoxLayout()
        add_arg = QPushButton("Add Argument")
        add_arg.clicked.connect(lambda: self._add_table_row(self.args_table))
        rm_arg = QPushButton("Remove Selected")
        rm_arg.clicked.connect(lambda: self._remove_selected_rows(self.args_table))
        args_btns.addWidget(add_arg)
        args_btns.addWidget(rm_arg)

        layout.addWidget(self.args_table)
        layout.addLayout(args_btns)

        # Env vars table
        env_label = QLabel("Environment Variables:")
        layout.addWidget(env_label)
        self.env_table = QTableWidget()
        self.env_table.setColumnCount(2)
        self.env_table.setHorizontalHeaderLabels(["Variable", "Value"])
        self.env_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.env_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.env_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        env_btns = QHBoxLayout()
        add_env = QPushButton("Add Variable")
        add_env.clicked.connect(lambda: self._add_table_row(self.env_table, 2))
        rm_env = QPushButton("Remove Selected")
        rm_env.clicked.connect(lambda: self._remove_selected_rows(self.env_table))
        env_btns.addWidget(add_env)
        env_btns.addWidget(rm_env)

        layout.addWidget(self.env_table)
        layout.addLayout(env_btns)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset")
        self.save_btn.clicked.connect(self._on_save)
        self.reset_btn.clicked.connect(self._on_reset)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.reset_btn)
        layout.addLayout(btn_row)

    def load_config(self, config: ServerConfig):
        self.current_config = config
        if not config:
            # Clear inputs
            self.id_input.clear()
            self.name_input.clear()
            self.command_input.clear()
            self.dir_input.clear()
            self._populate_table(self.args_table, [])
            self._populate_table(self.env_table, [])
            return
        self.id_input.setText(config.id)
        self.name_input.setText(config.name)
        self.command_input.setText(config.command)
        self.dir_input.setText(config.working_dir)
        self._populate_table(self.args_table, config.arguments)
        self._populate_table(self.env_table, list(config.env_vars.items()))

    def _populate_table(self, table, items):
        table.setRowCount(len(items))
        for i, item in enumerate(items):
            if table.columnCount() == 1:
                table.setItem(i, 0, QTableWidgetItem(str(item)))
            else:
                key, value = item
                table.setItem(i, 0, QTableWidgetItem(key))
                table.setItem(i, 1, QTableWidgetItem(value))

    def _add_table_row(self, table, columns=1):
        row = table.rowCount()
        table.insertRow(row)
        for col in range(columns):
            table.setItem(row, col, QTableWidgetItem(""))

    def _remove_selected_rows(self, table):
        selected = table.selectionModel().selectedRows()
        for index in sorted(selected, reverse=True):
            table.removeRow(index.row())

    def _browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Working Directory")
        if dir_path:
            self.dir_input.setText(dir_path)

    def _get_table_items(self, table):
        items = []
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.text().strip():
                items.append(item.text().strip())
        return items

    def _get_env_vars(self):
        env_vars = {}
        for row in range(self.env_table.rowCount()):
            key_item = self.env_table.item(row, 0)
            value_item = self.env_table.item(row, 1)
            if key_item and key_item.text().strip():
                key = key_item.text().strip()
                value = value_item.text().strip() if value_item else ""
                env_vars[key] = value
        return env_vars

    def validate(self):
        errors = []
        if not self.id_input.text().strip():
            errors.append("Server ID is required")
        if not self.command_input.text().strip():
            errors.append("Command is required")
        return errors

    def _on_save(self):
        errors = self.validate()
        if errors:
            QMessageBox.critical(self, "Validation Error", "\n".join(errors))
            return
        config = ServerConfig(
            id=self.id_input.text().strip(),
            name=self.name_input.text().strip(),
            command=self.command_input.text().strip(),
            arguments=self._get_table_items(self.args_table),
            env_vars=self._get_env_vars(),
            working_dir=self.dir_input.text().strip(),
        )
        self.saved.emit(config)

    def _on_reset(self):
        self.load_config(self.current_config)


class MCPManagerWindow(QMainWindow):
    CONFIG_FILE = "mcp_servers.json"  # Config file in the same folder

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCP Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.setObjectName("MainWindow")

        self.process_manager = ProcessManager()
        self.servers = []  # List of ServerConfig objects
        self.server_item_widgets = {}  # server_id: ServerListItemWidget
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
        self.container_layout.setContentsMargins(12, 8, 12, 8)
        self.container_layout.setSpacing(12)
        self.main_layout.addWidget(self.container_widget)

        # Create main two-pane UI (servers list on left, logs on right)
        self._create_main_panes()

        # Apply styles
        self.setStyleSheet(self._get_style_sheet())

        # Connect process manager signals (moved from header creation)
        self.process_manager.status_changed.connect(self._update_server_status)
        self.process_manager.output_received.connect(self._handle_server_output)
        self.process_manager.error_occurred.connect(self._handle_server_error)
        self.process_manager.logs_updated.connect(self._on_logs_updated)

        # Load servers from config file and populate list
        self._load_servers_from_file()

    def _create_main_panes(self):
        # Main horizontal splitter-like layout without header/footer
        main_row = QHBoxLayout()
        main_row.setContentsMargins(0, 0, 0, 0)
        main_row.setSpacing(12)

        # Left: server list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Buttons row for Add and Clone
        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(0, 0, 0, 0)
        buttons_row.setSpacing(6)

        self.add_server_button = QPushButton("+ Add Server")
        self.add_server_button.setObjectName("AddServerButton")
        self.add_server_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_server_button.clicked.connect(self._add_new_server)
        buttons_row.addWidget(self.add_server_button)

        self.clone_server_button = QPushButton("Clone Server")
        self.clone_server_button.setObjectName("CloneServerButton")
        self.clone_server_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clone_server_button.clicked.connect(self._clone_server)
        buttons_row.addWidget(self.clone_server_button)

        left_layout.addLayout(buttons_row)

        self.server_list = QListWidget()
        self.server_list.setObjectName("ServerList")
        self.server_list.currentItemChanged.connect(self._on_server_selected)
        left_layout.addWidget(self.server_list)

        # Right: tabs (Logs, Config)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)

        # Control buttons row (outside tabs)
        controls_row = QHBoxLayout()
        controls_row.setContentsMargins(0, 0, 0, 0)
        controls_row.setSpacing(6)

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.delete_button = QPushButton("Delete")
        for b in (self.start_button, self.stop_button, self.delete_button):
            b.setObjectName("ActionButton")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self._on_start_clicked)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)

        controls_row.addWidget(self.start_button)
        controls_row.addWidget(self.stop_button)
        controls_row.addWidget(self.delete_button)
        controls_row.addStretch()

        right_layout.addLayout(controls_row)

        self.tabs = QTabWidget()
        right_layout.addWidget(self.tabs)

        # Logs tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        logs_layout.setContentsMargins(0, 0, 0, 0)
        logs_layout.setSpacing(6)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setObjectName("LogDisplay")

        logs_layout.addWidget(self.log_display)

        self.tabs.addTab(logs_tab, "Logs")

        # Config tab
        self.config_panel = ServerEditorPanel(self)
        self.config_panel.saved.connect(self._on_config_saved)
        self.tabs.addTab(self.config_panel, "Config")

        # Assemble row
        main_row.addWidget(left_widget, 1)
        main_row.addWidget(right_widget, 3)

        self.container_layout.addLayout(main_row)

        # Internal state
        self.selected_server_id = None
        self._update_controls_enabled()

    def _populate_server_list(self):
        self.server_list.clear()
        self.server_item_widgets = {}
        for s in self.servers:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, s.id)
            # Item sizing
            item.setSizeHint(QSize(10, 36))
            widget = ServerListItemWidget(s, self.server_list)
            self.server_item_widgets[s.id] = widget
            self.server_list.addItem(item)
            self.server_list.setItemWidget(item, widget)
        # Select first item if available
        if self.server_list.count() > 0:
            self.server_list.setCurrentRow(0)
        else:
            self.selected_server_id = None
            self.log_display.clear()
            self._update_controls_enabled()

    def _on_server_selected(self, current, previous):
        server_id = None
        if current is not None:
            server_id = current.data(Qt.ItemDataRole.UserRole)
        self.selected_server_id = server_id
        self._update_controls_enabled()
        if server_id:
            self._show_logs_for_server_id(server_id)
            server = self._find_server_by_id(server_id)
            if server and hasattr(self, "config_panel"):
                self.config_panel.load_config(server)
                # Enable editing only when offline
                self.config_panel.setEnabled(server.status == "offline")
        else:
            if hasattr(self, "config_panel"):
                self.config_panel.load_config(None)
                self.config_panel.setEnabled(False)

    def _show_logs_for_server_id(self, server_id):
        logs = self.process_manager.get_logs(server_id)
        self.log_display.setText(logs)
        # Scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)

    def _on_logs_updated(self, server_id):
        if self.selected_server_id == server_id:
            self._show_logs_for_server_id(server_id)

    # ruff: noqa: C901
    def _on_config_saved(self, updated_config: ServerConfig):
        if not self.selected_server_id:
            return
        server = self._find_server_by_id(self.selected_server_id)
        if not server:
            return
        if server.status != "offline":
            QMessageBox.information(
                self,
                "Server Running",
                "Stop the server before editing its configuration.",
            )
            return
        # Duplicate ID check (allow unchanged ID)
        if updated_config.id != server.id and any(s.id == updated_config.id for s in self.servers):
            QMessageBox.warning(
                self,
                "Duplicate ID",
                f"A server with ID '{updated_config.id}' already exists.",
            )
            return
        # Preserve runtime status
        updated_config.status = server.status
        old_id = server.id
        new_id = updated_config.id
        # Replace in list
        for i, s in enumerate(self.servers):
            if s.id == old_id:
                self.servers[i] = updated_config
                break
        # Migrate logs if ID changed
        if new_id != old_id:
            if hasattr(self.process_manager, "logs") and old_id in self.process_manager.logs:
                self.process_manager.logs[new_id] = self.process_manager.logs.pop(old_id)
            self.selected_server_id = new_id
        # Save and refresh UI
        self._save_servers_to_file()
        self._populate_server_list()
        # Reselect updated server
        for i in range(self.server_list.count()):
            item = self.server_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == new_id:
                self.server_list.setCurrentRow(i)
                break
        # Ensure editor shows the saved config and enabled state
        if hasattr(self, "config_panel"):
            self.config_panel.load_config(updated_config)
            self.config_panel.setEnabled(updated_config.status == "offline")

    def _on_clear_logs_clicked(self):
        if not self.selected_server_id:
            return
        self.process_manager.clear_logs(self.selected_server_id)
        self.log_display.clear()

    def _find_server_by_id(self, server_id):
        return next((s for s in self.servers if s.id == server_id), None)

    def _on_start_clicked(self):
        if not self.selected_server_id:
            return
        # Switch to Logs tab and show current logs
        if hasattr(self, "tabs"):
            self.tabs.setCurrentIndex(0)
        self._show_logs_for_server_id(self.selected_server_id)
        server = self._find_server_by_id(self.selected_server_id)
        if server and server.status == "offline":
            self.process_manager.start_server(server)

    def _on_stop_clicked(self):
        if not self.selected_server_id:
            return
        # Switch to Logs tab and show current logs
        if hasattr(self, "tabs"):
            self.tabs.setCurrentIndex(0)
        self._show_logs_for_server_id(self.selected_server_id)
        server = self._find_server_by_id(self.selected_server_id)
        if server and server.status != "offline":
            self.process_manager.stop_server(server.id)

    def _on_delete_clicked(self):
        if not self.selected_server_id:
            return
        server = self._find_server_by_id(self.selected_server_id)
        if not server:
            return

        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the server '{server.name}' (ID: {server.id})?\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Stop if running
            self.process_manager.stop_server(server.id)
            # Remove from list and UI
            self.servers = [s for s in self.servers if s.id != server.id]
            self._save_servers_to_file()
            self._populate_server_list()
            # Clear logs view if deleted server was selected
            self.log_display.clear()

    def _update_controls_enabled(self):
        has_selection = self.selected_server_id is not None
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.delete_button.setEnabled(has_selection)
        if hasattr(self, "config_panel"):
            # Enable config tab panel only if a server is selected and offline
            if has_selection:
                server = self._find_server_by_id(self.selected_server_id)
                self.config_panel.setEnabled(bool(server and server.status == "offline"))
            else:
                self.config_panel.setEnabled(False)
        if has_selection:
            server = self._find_server_by_id(self.selected_server_id)
            if server:
                self.start_button.setEnabled(server.status == "offline")
                self.stop_button.setEnabled(server.status != "offline")

    def _load_servers_from_file(self):
        """Load server configurations from the config file"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE) as f:
                    data = json.load(f)

                if isinstance(data, list):
                    self.servers = []
                    for item in data:
                        if isinstance(item, dict):
                            self.servers.append(ServerConfig.from_dict(item))

                    print(f"[DEBUG] Loaded servers from file: {[s.id for s in self.servers]}")
                    # Populate the left-side server list
                    self._populate_server_list()
                    return
            except Exception as e:
                print(f"[ERROR] Loading config file: {e}")

        # If no config file exists or loading failed, load sample data
        print("[DEBUG] Loading sample data (no config file found)")
        self._load_sample_data()

    def _load_sample_data(self):
        """Load sample server configurations for demonstration"""
        sample_server1 = ServerConfig(
            id="brave-search",
            name="Brave Search",
            command="npx",
            arguments=["run", "brave"],
            env_vars={"PORT": "3000"},
            working_dir="",
        )

        sample_server2 = ServerConfig(
            id="postgres",
            name="Postgres",
            command="docker",
            arguments=["run", "postgres"],
            env_vars={"POSTGRES_PASSWORD": "secret"},
            working_dir="",
        )

        self.servers = [sample_server1, sample_server2]

        # Populate the left-side server list
        self._populate_server_list()

        # Save the sample data to file for future use
        self._save_servers_to_file()

    def _save_servers_to_file(self):
        """Save current server configurations to the config file"""
        try:
            configs = [s.to_dict() for s in self.servers]
            print(f"[DEBUG] Saving servers to {self.CONFIG_FILE}: {[s.id for s in self.servers]}")
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(configs, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Saving config file: {e}")

    def _add_new_server(self):
        """Open dialog to add a new server"""
        dialog = ServerEditorDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_config = dialog.get_config()
            # Prevent duplicate IDs
            if any(s.id == new_config.id for s in self.servers):
                QMessageBox.warning(
                    self,
                    "Duplicate ID",
                    f"A server with ID '{new_config.id}' already exists.",
                )
                return
            self.servers.append(new_config)
            self._save_servers_to_file()
            # Refresh list and select the newly added server
            self._populate_server_list()
            # Find and select the new item
            for i in range(self.server_list.count()):
                item = self.server_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == new_config.id:
                    self.server_list.setCurrentRow(i)
                    break

    def _clone_server(self):
        """Clone the currently selected server configuration"""
        if not self.selected_server_id:
            print("[DEBUG] Clone attempt with no server selected")
            QMessageBox.information(self, "No Server Selected", "Please select a server to clone.")
            return

        server = self._find_server_by_id(self.selected_server_id)
        if not server:
            print(f"[DEBUG] Server not found for ID: {self.selected_server_id}")
            return

        print(f"[DEBUG] Cloning server: {server.id} ({server.name})")

        # Create a copy of the server configuration
        new_config = server.copy()

        # Generate a new unique ID by appending "_clone" and then numbers if necessary
        base_id = new_config.id + "_clone"
        new_id = base_id
        count = 1
        while any(s.id == new_id for s in self.servers):
            new_id = f"{base_id}_{count}"
            count += 1

        print(f"[DEBUG] Generated new clone ID: {new_id} (after {count - 1} attempts)")
        new_config.id = new_id

        # Reset status to offline
        new_config.status = "offline"

        # Add the cloned server to the list
        self.servers.append(new_config)
        print(f"[DEBUG] Added clone to server list. Total servers: {len(self.servers)}")

        # Save and refresh UI
        self._save_servers_to_file()
        self._populate_server_list()

        # Select the cloned server in the list
        for i in range(self.server_list.count()):
            item = self.server_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == new_id:
                self.server_list.setCurrentRow(i)
                print(f"[DEBUG] Selected cloned server in UI: {new_id}")
                break

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

        # Update item traffic light in the list
        widget = self.server_item_widgets.get(server_id) if hasattr(self, "server_item_widgets") else None
        if widget:
            widget.update_status(status)

        # Update controls based on new status
        if hasattr(self, "_update_controls_enabled"):
            self._update_controls_enabled()

        # Update status label
        status_label = getattr(server, "status_label", None)
        if status_label:
            status_label.setText(status.capitalize())

            # Update style
            if status == "online":
                status_label.setObjectName("StatusOnline")
            elif status == "error":
                status_label.setObjectName("StatusError")
            else:
                status_label.setObjectName("StatusOffline")
            status_label.style().unpolish(status_label)
            status_label.style().polish(status_label)

        # Update start/stop button text
        if hasattr(server, "start_stop_button") and server.start_stop_button:
            if status == "online":
                server.start_stop_button.setText("Stop")
            else:
                server.start_stop_button.setText("Start")

    def _handle_server_output(self, server_id, output):
        """Handle server output without showing alerts"""
        print(f"Server {server_id} output: {output}")
        # Store output in ProcessManager logs
        if hasattr(self.process_manager, "logs") and server_id in self.process_manager.logs:
            self.process_manager.logs[server_id].append(output)
            self.process_manager.logs_updated.emit(server_id)

    def _handle_server_error(self, server_id, error):
        """Handle server errors without showing alerts"""
        print(f"Server {server_id} error: {error}")
        self._update_server_status(server_id, "error")
        # Store error in ProcessManager logs
        if hasattr(self.process_manager, "logs") and server_id in self.process_manager.logs:
            self.process_manager.logs[server_id].append(f"ERROR: {error}")
            self.process_manager.logs_updated.emit(server_id)

    def _get_style_sheet(self):
        # Delegated to external module for maintainability
        from ui_styles import get_style_sheet

        return get_style_sheet()


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    window = MCPManagerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
