import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, 
    QTableWidget, QTableWidgetItem, QPushButton, QFileDialog,
    QHeaderView, QAbstractItemView, QLabel, QMessageBox
)
from PyQt6.QtCore import Qt
from models import ServerConfig

class ServerEditorDialog(QDialog):
    def __init__(self, config=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Server Configuration")
        self.setMinimumSize(600, 600)
        
        self.config = config or ServerConfig("", "", "", [], {}, "")
        self.is_new = config is None
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Form layout for basic fields
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        
        self.id_input = QLineEdit()
        self.id_input.setText(self.config.id)
        form_layout.addRow("Server ID:", self.id_input)
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.config.name)
        form_layout.addRow("Display Name:", self.name_input)
        
        self.command_input = QLineEdit()
        self.command_input.setText(self.config.command)
        form_layout.addRow("Command:", self.command_input)
        
        # Working directory
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setText(self.config.working_dir)
        dir_button = QPushButton("Browse...")
        dir_button.clicked.connect(self._browse_directory)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        form_layout.addRow("Working Directory:", dir_layout)
        
        layout.addLayout(form_layout)
        
        # Arguments table
        layout.addWidget(QLabel("Arguments:"))
        self.args_table = QTableWidget()
        self.args_table.setColumnCount(1)
        self.args_table.setHorizontalHeaderLabels(["Argument"])
        self.args_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.args_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._populate_table(self.args_table, self.config.arguments)
        
        args_btn_layout = QHBoxLayout()
        add_arg_btn = QPushButton("Add Argument")
        add_arg_btn.clicked.connect(lambda: self._add_table_row(self.args_table))
        remove_arg_btn = QPushButton("Remove Selected")
        remove_arg_btn.clicked.connect(lambda: self._remove_selected_rows(self.args_table))
        args_btn_layout.addWidget(add_arg_btn)
        args_btn_layout.addWidget(remove_arg_btn)
        
        layout.addWidget(self.args_table)
        layout.addLayout(args_btn_layout)
        
        # Environment variables table
        layout.addWidget(QLabel("Environment Variables:"))
        self.env_table = QTableWidget()
        self.env_table.setColumnCount(2)
        self.env_table.setHorizontalHeaderLabels(["Variable", "Value"])
        self.env_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.env_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.env_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._populate_table(self.env_table, list(self.config.env_vars.items()))
        
        env_btn_layout = QHBoxLayout()
        add_env_btn = QPushButton("Add Variable")
        add_env_btn.clicked.connect(lambda: self._add_table_row(self.env_table, 2))
        remove_env_btn = QPushButton("Remove Selected")
        remove_env_btn.clicked.connect(lambda: self._remove_selected_rows(self.env_table))
        env_btn_layout.addWidget(add_env_btn)
        env_btn_layout.addWidget(remove_env_btn)
        
        layout.addWidget(self.env_table)
        layout.addLayout(env_btn_layout)
        
        # Dialog buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def _populate_table(self, table, items):
        table.setRowCount(len(items))
        for i, item in enumerate(items):
            if table.columnCount() == 1:
                table.setItem(i, 0, QTableWidgetItem(str(item)))
            else:  # env vars table
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
    
    def get_config(self):
        """Return the updated configuration"""
        # Create new config from inputs
        config = ServerConfig(
            id=self.id_input.text().strip(),
            name=self.name_input.text().strip(),
            command=self.command_input.text().strip(),
            arguments=self._get_table_items(self.args_table),
            env_vars=self._get_env_vars(),
            working_dir=self.dir_input.text().strip()
        )
        return config
    
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
        """Validate form inputs"""
        errors = []
        if not self.id_input.text().strip():
            errors.append("Server ID is required")
        if not self.command_input.text().strip():
            errors.append("Command is required")
        return errors
    
    def accept(self):
        """Override accept to add validation"""
        errors = self.validate()
        if errors:
            QMessageBox.critical(self, "Validation Error", "\n".join(errors))
            return
        
        super().accept()