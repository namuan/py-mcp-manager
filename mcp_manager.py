import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize

class MCPManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MCP Manager")
        self.setGeometry(100, 100, 1200, 800)
        self.setObjectName("MainWindow")

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

    def _create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 15)

        title_label = QLabel("MCP Manager")
        title_label.setObjectName("MainTitle")

        header_layout.addWidget(title_label)
        header_layout.addStretch()

        visual_editor_button = QPushButton("Visual Editor")
        visual_editor_button.setObjectName("HeaderButton")
        visual_editor_button.setCursor(Qt.CursorShape.PointingHandCursor)

        view_json_button = QPushButton("View JSON")
        view_json_button.setObjectName("ViewJsonButton")
        view_json_button.setCursor(Qt.CursorShape.PointingHandCursor)

        header_layout.addWidget(visual_editor_button)
        header_layout.addWidget(view_json_button)

        self.container_layout.addWidget(header_widget)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setObjectName("Separator")
        self.container_layout.addWidget(line)

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

        check_all_button = QPushButton("Check All Statuses")
        check_all_button.setObjectName("ActionButton")
        check_all_button.setCursor(Qt.CursorShape.PointingHandCursor)

        paste_json_button = QPushButton("Paste from JSON")
        paste_json_button.setObjectName("ActionButton")
        paste_json_button.setCursor(Qt.CursorShape.PointingHandCursor)

        add_server_button = QPushButton("+ Add Server")
        add_server_button.setObjectName("AddServerButton")
        add_server_button.setCursor(Qt.CursorShape.PointingHandCursor)

        servers_header_layout.addWidget(check_all_button)
        servers_header_layout.addWidget(paste_json_button)
        servers_header_layout.addWidget(add_server_button)

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

        self._add_server_row(2, "brave-search", "npx", "2 arguments", "1 variable")
        self._add_server_row(3, "postgres", "npx", "3 arguments", "No env vars")

        servers_layout.addWidget(servers_list_widget)
        self.container_layout.addWidget(servers_container)

    def _create_server_list_header(self):
        headers = ["Status", "Server ID", "Command", "Arguments", "Env Variables", "Actions"]
        for i, header_text in enumerate(headers):
            label = QLabel(header_text)
            label.setObjectName("GridHeader")
            self.grid_layout.addWidget(label, 0, i, Qt.AlignmentFlag.AlignLeft)

    def _add_server_row(self, row, server_id, command, args, env_vars):
        # Status
        status_label = QLabel("Offline")
        status_label.setObjectName("StatusOffline")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(status_label, row, 0)

        # Server ID
        self.grid_layout.addWidget(QLabel(server_id), row, 1)

        # Command
        self.grid_layout.addWidget(QLabel(command), row, 2)

        # Arguments
        self.grid_layout.addWidget(QLabel(args), row, 3)

        # Env Variables
        self.grid_layout.addWidget(QLabel(env_vars), row, 4)

        # Actions
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        edit_button = QPushButton("Edit")
        edit_button.setObjectName("ActionButton")
        edit_button.setCursor(Qt.CursorShape.PointingHandCursor)

        delete_button = QPushButton("Delete")
        delete_button.setObjectName("ActionButton")
        delete_button.setCursor(Qt.CursorShape.PointingHandCursor)

        actions_layout.addWidget(edit_button)
        actions_layout.addWidget(delete_button)

        self.grid_layout.addWidget(actions_widget, row, 5, Qt.AlignmentFlag.AlignRight)

        # Row separator
        line_separator = QFrame()
        line_separator.setFrameShape(QFrame.Shape.HLine)
        line_separator.setObjectName("Separator")
        self.grid_layout.addWidget(line_separator, row + 1, 0, 1, 6)


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
            #Footer {
                background-color: #F8F9FA;
                border-top: 1px solid #DEE2E6;
            }
            #FooterLabel {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                font-size: 14px;
                color: #6C757D;
            }
        """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MCPManagerWindow()
    window.show()
    sys.exit(app.exec())