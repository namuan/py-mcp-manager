import json
from collections.abc import Callable

from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from models import ServerConfig


def build_json_view_dialog(parent, servers: list[ServerConfig], on_export: Callable[[], None] | None = None) -> QDialog:
    """Build a dialog that shows servers JSON and an optional Export button."""
    configs = [s.to_dict() for s in servers]
    json_str = json.dumps(configs, indent=2)

    dialog = QDialog(parent)
    dialog.setWindowTitle("Server Configuration JSON")
    dialog.setMinimumSize(600, 400)
    layout = QVBoxLayout()

    text_edit = QTextEdit()
    text_edit.setPlainText(json_str)
    text_edit.setReadOnly(True)
    layout.addWidget(text_edit)

    export_btn = QPushButton("Export to File")
    export_btn.setObjectName("ActionButton")
    if on_export is not None:
        export_btn.clicked.connect(on_export)  # type: ignore[arg-type]
    else:
        export_btn.setEnabled(False)
    layout.addWidget(export_btn)

    dialog.setLayout(layout)
    return dialog


def select_and_load_servers(parent) -> list[ServerConfig] | None:
    """Open a file dialog, load servers JSON, validate, and return list of ServerConfig.
    Shows message boxes on failure or cancellation and returns None in that case.
    """
    file_path, _ = QFileDialog.getOpenFileName(parent, "Import Server Configuration", "", "JSON Files (*.json)")
    if not file_path:
        return None

    try:
        with open(file_path) as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Invalid configuration format: expected a list of servers")

        new_servers: list[ServerConfig] = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("Each server configuration must be a dictionary")
            new_servers.append(ServerConfig.from_dict(item))

        QMessageBox.information(parent, "Import Successful", f"Imported {len(new_servers)} servers")
        return new_servers

    except Exception as e:
        QMessageBox.critical(parent, "Import Error", f"Failed to import configuration: {e!s}")
        return None


def select_and_save_servers(parent, servers: list[ServerConfig]) -> bool:
    """Open a save dialog and write servers JSON. Shows message boxes. Returns True on success."""
    file_path, _ = QFileDialog.getSaveFileName(parent, "Export Server Configuration", "", "JSON Files (*.json)")
    if not file_path:
        return False

    try:
        if not file_path.endswith(".json"):
            file_path += ".json"

        configs = [s.to_dict() for s in servers]
        with open(file_path, "w") as f:
            json.dump(configs, f, indent=2)

        QMessageBox.information(parent, "Export Successful", "Configuration exported successfully")
        return True

    except Exception as e:
        QMessageBox.critical(parent, "Export Error", f"Failed to export configuration: {e!s}")
        return False
