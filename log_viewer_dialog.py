import sys
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout,
    QApplication, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor

class LogViewerDialog(QDialog):
    def __init__(self, server_id, logs, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Logs - {server_id}")
        self.setMinimumSize(800, 600)
        
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = LogViewerDialog("Test Server", "Sample log output")
    dialog.exec()