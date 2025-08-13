import sys
from contextlib import suppress

from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class LogViewerDialog(QDialog):
    def __init__(self, server_id, logs, parent=None):
        super().__init__(parent)
        self.server_id = server_id
        self.parent_window = parent
        self.setWindowTitle(f"Logs - {server_id}")
        self.setMinimumSize(800, 600)

        # Connect to process manager for real-time updates
        if parent and hasattr(parent, "process_manager"):
            parent.process_manager.logs_updated.connect(self._on_logs_updated)

        layout = QVBoxLayout()

        # Header
        header = QLabel(f"Server: {server_id}")
        header_font = QFont()
        header_font.setBold(True)
        header_font.setPointSize(14)
        header.setFont(header_font)
        layout.addWidget(header)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Monospace"))
        self.log_display.setText(logs)

        # Auto-scroll to bottom
        self.log_display.moveCursor(QTextCursor.MoveOperation.End)

        layout.addWidget(self.log_display)

        # Buttons
        btn_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear Logs")
        clear_btn.clicked.connect(self.clear_logs)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def clear_logs(self):
        self.log_display.clear()
        # Also clear logs in ProcessManager
        if self.parent_window and hasattr(self.parent_window, "process_manager"):
            self.parent_window.process_manager.clear_logs(self.server_id)

    def _on_logs_updated(self, server_id):
        """Update log display when new logs are received"""
        if server_id == self.server_id and self.parent_window and hasattr(self.parent_window, "process_manager"):
            updated_logs = self.parent_window.process_manager.get_logs(server_id)
            self.log_display.setText(updated_logs)
            # Auto-scroll to bottom
            self.log_display.moveCursor(QTextCursor.MoveOperation.End)

    def closeEvent(self, event):
        """Disconnect signals when dialog is closed"""
        if self.parent_window and hasattr(self.parent_window, "process_manager"):
            with suppress(TypeError):
                self.parent_window.process_manager.logs_updated.disconnect(self._on_logs_updated)
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = LogViewerDialog("Test Server", "Sample log output")
    dialog.exec()
