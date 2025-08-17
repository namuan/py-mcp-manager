from __future__ import annotations

import contextlib
import logging
from collections import deque
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtCore import QEasingCurve, QEvent, QPoint, QPropertyAnimation, Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget


class ToastLevel(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


logger = logging.getLogger(__name__)


@dataclass
class ToastConfig:
    duration_ms: int = 3500
    position: str = "top-right"  # top-right, top-left, bottom-right, bottom-left
    margin: int = 16
    max_queue: int = 50
    width: int = 320


class ToastWidget(QWidget):
    def __init__(self, parent: QWidget, message: str, level: ToastLevel, width: int):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Content
        container = QWidget(self)
        container.setObjectName("ToastContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 10, 12, 10)

        label = QLabel(message)
        label.setWordWrap(True)
        label.setObjectName("ToastLabel")
        f = QFont()
        f.setPointSize(10)
        label.setFont(f)
        layout.addWidget(label)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)

        # Style by level via object names
        self.setObjectName(f"Toast-{level.value}")
        container.setObjectName(f"ToastContainer-{level.value}")

        # Size
        self.setFixedWidth(width)
        self.adjustSize()

        # Fade effect
        self._opacity = QGraphicsOpacityEffect(self)
        self._opacity.setOpacity(0.0)
        self.setGraphicsEffect(self._opacity)

        self._fade_anim = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade_anim.setDuration(220)
        self._fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    def fade_in(self):
        self._fade_anim.stop()
        self._fade_anim.setStartValue(0.0)
        self._fade_anim.setEndValue(1.0)
        self._fade_anim.start()

    def fade_out(self, finished_cb):
        def _on_finished():
            finished_cb()

        self._fade_anim.stop()
        self._fade_anim.setStartValue(self._opacity.opacity())
        self._fade_anim.setEndValue(0.0)
        self._fade_anim.finished.connect(_on_finished)
        self._fade_anim.start()


class ToastManager(QWidget):
    """A simple queued toast system for a top-level window.

    Two modes:
    - overlay (default): floating toast widgets in a corner
    - status-bar: queued messages displayed via QMainWindow.statusBar()
    """

    def __init__(self, parent: QWidget, config: ToastConfig | None = None):
        super().__init__(parent)
        self.setObjectName("ToastManager")
        self._cfg = config or ToastConfig()
        self._queue: deque[tuple[str, ToastLevel]] = deque()
        self._current: ToastWidget | bool | None = None  # bool used as placeholder in status-bar mode
        self._timer: QTimer | None = None
        self._parent = parent

        # Ensure we stay on top of parent contents
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.hide()

        # Install stylesheet additions on parent if possible (overlay mode only)
        if self._cfg.position != "status-bar":
            self._install_styles(parent)

        # Track parent move/resize to keep position (overlay mode only)
        if parent is not None and self._cfg.position != "status-bar":
            parent.installEventFilter(self)

    def _install_styles(self, parent: QWidget):
        # Append minimal styles for the toast containers
        style = parent.styleSheet() if hasattr(parent, "styleSheet") else ""
        extra = """
        /* Toast base */
        QWidget#ToastContainer-info, QWidget#ToastContainer-success,
        QWidget#ToastContainer-warning, QWidget#ToastContainer-error {
            background: #212529; /* default dark */
            color: #fff;
            border-radius: 8px;
            border: 1px solid rgba(0,0,0,0.2);
        }
        QWidget#ToastContainer-success { background: #198754; }
        QWidget#ToastContainer-warning { background: #FFC107; color: #212529; }
        QWidget#ToastContainer-error { background: #DC3545; }
        QLabel#ToastLabel { color: inherit; }
        """
        with contextlib.suppress(Exception):
            parent.setStyleSheet((style or "") + "\n" + extra)

    def show_toast(self, message: str, level: ToastLevel | str = ToastLevel.INFO):
        lvl = ToastLevel(level) if not isinstance(level, ToastLevel) else level
        # Enforce max queue length
        if len(self._queue) >= self._cfg.max_queue:
            # Drop oldest to keep memory bounded
            self._queue.popleft()
        self._queue.append((message, lvl))
        if not self._current:
            self._dequeue_and_show()

    # Public convenience shortcuts
    def info(self, msg: str):
        self.show_toast(msg, ToastLevel.INFO)

    def success(self, msg: str):
        self.show_toast(msg, ToastLevel.SUCCESS)

    def warning(self, msg: str):
        self.show_toast(msg, ToastLevel.WARNING)

    def error(self, msg: str):
        self.show_toast(msg, ToastLevel.ERROR)

    def _dequeue_and_show(self):
        if not self._queue:
            self._current = None
            if self._cfg.position != "status-bar":
                self.hide()
            return

        msg, lvl = self._queue.popleft()

        if self._cfg.position == "status-bar" and self._parent and hasattr(self._parent, "statusBar"):
            # Status bar mode: show message with styling, use timer for queueing
            self._show_in_status_bar(msg, lvl)
            self._current = True
        else:
            # Overlay mode
            self._current = ToastWidget(self.parentWidget(), msg, lvl, self._cfg.width)
            self._position_current()
            self._current.show()
            self._current.raise_()
            self._current.fade_in()

        # Duration timer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dismiss_current)
        self._timer.start(self._cfg.duration_ms)

    def _dismiss_current(self):
        if not self._current:
            self._dequeue_and_show()
            return

        if self._cfg.position == "status-bar" and self._parent and hasattr(self._parent, "statusBar"):
            # Clear style optionally; QStatusBar will auto-clear message after timeout, but we manage queue here
            try:
                sb = self._parent.statusBar()
                if sb is not None:
                    # Do not clear immediately to avoid flicker; proceed to next
                    ...
            except Exception as exc:
                logger.debug("ToastManager._dismiss_current: error accessing status bar: %s", exc)
            self._current = None
            self._dequeue_and_show()
            return

        def _after():
            if self._current:
                self._current.hide()
                self._current.setParent(None)
            self._current = None
            self._dequeue_and_show()

        # Overlay fade out
        self._current.fade_out(_after)

    def _position_current(self):
        if not self._current:
            return
        if self._cfg.position == "status-bar":
            return
        parent = self.parentWidget()
        if not parent:
            return
        parent_rect = parent.rect()
        gpos = parent.mapToGlobal(parent_rect.topLeft())

        margin = self._cfg.margin
        tw = self._current.width()
        th = self._current.height()

        if self._cfg.position == "top-right":
            x = gpos.x() + parent_rect.width() - tw - margin
            y = gpos.y() + margin
        elif self._cfg.position == "top-left":
            x = gpos.x() + margin
            y = gpos.y() + margin
        elif self._cfg.position == "bottom-right":
            x = gpos.x() + parent_rect.width() - tw - margin
            y = gpos.y() + parent_rect.height() - th - margin
        else:  # bottom-left
            x = gpos.x() + margin
            y = gpos.y() + parent_rect.height() - th - margin

        self._current.move(QPoint(x, y))

    def resizeEvent(self, event):
        # Reposition on parent resize (overlay mode only)
        if self._cfg.position != "status-bar":
            self._position_current()
        return super().resizeEvent(event)

    def eventFilter(self, obj, event):
        if (
            self._cfg.position != "status-bar"
            and obj is self.parentWidget()
            and event.type() in (QEvent.Type.Resize, QEvent.Type.Move, QEvent.Type.Show)
        ):
            self._position_current()
        return False

    # ---------- Status bar helpers ----------
    def _show_in_status_bar(self, message: str, level: ToastLevel):
        try:
            if not self._parent or not hasattr(self._parent, "statusBar"):
                return
            sb = self._parent.statusBar()
            if sb is None:
                return
            # Neutral styling for all notifications (no per-level backgrounds)
            # Matches app neutral palette
            sb.setStyleSheet("QStatusBar { background-color: #E9ECEF; color: #212529; }")

            # Show plain message without emojis or level-specific prefixes
            sb.showMessage(message, self._cfg.duration_ms)
        except Exception as exc:
            # Log and continue (styling issues should not be fatal)
            logger.debug("ToastManager._show_in_status_bar: failed to show message: %s", exc)
