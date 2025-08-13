import os
import shlex
import subprocess

from PyQt6.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSignal

from models import ServerConfig


class ProcessManager(QObject):
    status_changed = pyqtSignal(str, str)  # server_id, new_status
    output_received = pyqtSignal(str, str)  # server_id, output
    error_occurred = pyqtSignal(str, str)  # server_id, error
    logs_updated = pyqtSignal(str)  # server_id

    def __init__(self):
        super().__init__()
        self.processes = {}  # server_id: QProcess
        self.configs = {}  # server_id: ServerConfig
        self.logs = {}  # server_id: list of log entries

    # ruff: noqa: C901
    def start_server(self, config: ServerConfig):
        """Start a server process using its configuration"""
        server_id = config.id

        if server_id in self.processes:
            self.error_occurred.emit(server_id, "Server already running")
            return False

        # Initialize logs for this server
        self.logs[server_id] = []
        self.logs[server_id].append(f"Starting server '{server_id}'...")
        self.logs[server_id].append(f"Command: {config.command} {" ".join(config.arguments)}")
        if config.working_dir:
            self.logs[server_id].append(f"Working directory: {config.working_dir}")
        if config.env_vars:
            self.logs[server_id].append(f"Environment variables: {config.env_vars}")

        # Build shell-wrapped command so user shell environment is available
        if os.name == "nt":
            shell = os.environ.get("COMSPEC", "cmd.exe")
            # Properly quote the command line for cmd.exe
            full_cmd = subprocess.list2cmdline([config.command, *list(config.arguments)])
            shell_args = ["/C", full_cmd]
        else:
            shell = os.environ.get("SHELL", "/bin/bash") or "/bin/bash"
            # Safely quote for POSIX shells
            try:
                full_cmd = shlex.join([config.command, *list(config.arguments)])
            except AttributeError:
                # Fallback if shlex.join is unavailable
                full_cmd = " ".join(shlex.quote(x) for x in [config.command, *list(config.arguments)])
            # Use a login shell to load user profiles, and execute the command
            shell_args = ["-lc", full_cmd]

        self.logs[server_id].append(f"Shell: {shell}")
        self.logs[server_id].append(f"Shell command: {shell} {" ".join(shell_args)}")
        self.logs[server_id].append("--- Server Output ---")
        self.logs_updated.emit(server_id)

        # Create and configure process
        process = QProcess()
        process.setProgram(shell)
        process.setArguments(shell_args)

        # Set environment variables
        env = QProcessEnvironment.systemEnvironment()
        for key, value in config.env_vars.items():
            env.insert(key, value)
        process.setProcessEnvironment(env)

        # Set working directory if specified
        if config.working_dir:
            process.setWorkingDirectory(config.working_dir)

        # Connect signals
        process.readyReadStandardOutput.connect(lambda: self._handle_stdout(server_id, process))
        process.readyReadStandardError.connect(lambda: self._handle_stderr(server_id, process))
        process.stateChanged.connect(lambda state: self._handle_state_change(server_id, state))
        process.finished.connect(
            lambda exit_code, exit_status: self._handle_finished(server_id, exit_code, exit_status)
        )

        # Start process
        try:
            process.start()

            # Check if process started successfully
            if not process.waitForStarted(3000):  # Wait up to 3 seconds
                error_msg = f"Failed to start process: {process.errorString()}"
                self.logs[server_id].append(f"ERROR: {error_msg}")
                self.logs_updated.emit(server_id)
                self.error_occurred.emit(server_id, error_msg)
                return False

            self.processes[server_id] = process
            self.configs[server_id] = config

            # Add startup log entry
            if server_id in self.logs:
                self.logs[server_id].append("Process started successfully")
                self.logs_updated.emit(server_id)

            self.status_changed.emit(server_id, "starting")
            return True

        except Exception as e:
            error_msg = f"Exception starting process: {e!s}"
            self.logs[server_id].append(f"ERROR: {error_msg}")
            self.logs_updated.emit(server_id)
            self.error_occurred.emit(server_id, error_msg)
            return False

    def get_logs(self, server_id):
        """Get logs for a server"""
        return "\n".join(self.logs.get(server_id, []))

    def clear_logs(self, server_id):
        """Clear logs for a server"""
        if server_id in self.logs:
            self.logs[server_id] = []
            self.logs_updated.emit(server_id)

    def stop_server(self, server_id):
        """Stop a running server process"""
        if server_id not in self.processes:
            return False

        process = self.processes[server_id]
        if process.state() == QProcess.ProcessState.Running:
            # Try graceful termination first
            process.terminate()
            if not process.waitForFinished(5000):  # 5s timeout
                process.kill()
        return True

    def get_status(self, server_id):
        """Get current status of a server"""
        if server_id not in self.processes:
            return "offline"

        process = self.processes[server_id]
        state = process.state()

        if state == QProcess.ProcessState.Running:
            return "online"
        elif state == QProcess.ProcessState.Starting:
            return "starting"
        else:
            return "offline"

    def _handle_stdout(self, server_id, process):
        """Handle standard output from process"""
        output = bytes(process.readAllStandardOutput()).decode("utf-8")
        self.output_received.emit(server_id, output)
        if server_id in self.logs:
            self.logs[server_id].append(output)
            self.logs_updated.emit(server_id)

    def _handle_stderr(self, server_id, process):
        """Handle error output from process"""
        error = bytes(process.readAllStandardError()).decode("utf-8")
        self.error_occurred.emit(server_id, error)
        self.status_changed.emit(server_id, "error")
        if server_id in self.logs:
            self.logs[server_id].append(f"ERROR: {error}")
            self.logs_updated.emit(server_id)

    def _handle_state_change(self, server_id, state):
        """Handle process state changes"""
        if state == QProcess.ProcessState.Running:
            self.status_changed.emit(server_id, "online")
            if server_id in self.logs:
                self.logs[server_id].append("Server is now running")
                self.logs_updated.emit(server_id)
        elif state == QProcess.ProcessState.NotRunning:
            self.status_changed.emit(server_id, "offline")
            if server_id in self.logs:
                self.logs[server_id].append("Server stopped")
                self.logs_updated.emit(server_id)

    def _handle_finished(self, server_id, exit_code, exit_status):
        """Clean up when process finishes"""
        if server_id in self.processes:
            self.processes.pop(server_id)
            self.configs.pop(server_id)
            self.status_changed.emit(server_id, "offline")
            if server_id in self.logs:
                self.logs[server_id].append(f"Process exited with code {exit_code}")
                self.logs_updated.emit(server_id)
