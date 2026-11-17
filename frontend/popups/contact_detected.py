from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@dataclass(frozen=True)
class ContactNotification:
    contact_id: str
    contact_name: str
    last_interaction: str
    last_topic: str
    direction: str


class ContactDetectedPopup(QWidget):
    contact_requested = Signal(str)
    do_not_disturb_requested = Signal()
    dismissed = Signal()
    minimize_requested = Signal()

    def __init__(
        self,
        notification: ContactNotification,
        parent=None,
    ):
        super().__init__(parent)
        self.notification = notification
        self.setObjectName("notificationOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setStyleSheet(
            """
            QWidget#notificationOverlay {
                background-color: rgba(20, 28, 40, 105);
            }
            QFrame#popupCard {
                background-color: white;
                border: 1px solid #888888;
                border-radius: 8px;
            }
            QLabel#popupTitle {
                font-size: 19px;
                font-weight: 700;
            }
            QLabel#contactName {
                color: #167045;
                font-size: 15px;
                font-weight: 600;
            }
            QLabel#contactDetails {
                color: #777777;
                font-size: 11px;
            }
            QPushButton {
                min-height: 34px;
                padding: 0 12px;
                border: 1px solid #bbbbbb;
                background-color: white;
            }
            QPushButton#openContact {
                color: white;
                background-color: #167045;
                border: none;
                font-weight: 600;
            }
            QPushButton#minimizeNotification {
                min-width: 64px;
                max-width: 80px;
                min-height: 30px;
                max-height: 30px;
                padding: 0 6px;
                font-weight: 700;
            }
            """
        )

        overlay_layout = QVBoxLayout(self)
        overlay_layout.setContentsMargins(24, 24, 24, 24)
        overlay_layout.addStretch()

        card_row = QHBoxLayout()
        card_row.addStretch()

        card = QFrame()
        card.setObjectName("popupCard")
        card.setFixedWidth(420)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Contact Detected")
        title.setObjectName("popupTitle")
        header.addWidget(title)
        header.addStretch()

        minimize_button = QPushButton("Minimize")
        minimize_button.setObjectName("minimizeNotification")
        minimize_button.setToolTip("Minimize notification")
        minimize_button.setAccessibleName("Minimize notification")
        minimize_button.clicked.connect(self.minimize)
        header.addWidget(minimize_button)
        layout.addLayout(header)

        name = QLabel(notification.contact_name)
        name.setObjectName("contactName")
        layout.addWidget(name)

        details = QLabel(
            f"Last interaction: {notification.last_interaction}\n"
            f"Last topic: {notification.last_topic}\n"
            f"Direction detected: {notification.direction}"
        )
        details.setObjectName("contactDetails")
        details.setWordWrap(True)
        layout.addWidget(details)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)

        open_button = QPushButton("Open Contact")
        open_button.setObjectName("openContact")
        open_button.clicked.connect(self.open_contact)
        buttons.addWidget(open_button)

        dismiss_button = QPushButton("Dismiss")
        dismiss_button.clicked.connect(self.dismiss)
        buttons.addWidget(dismiss_button)

        dnd_button = QPushButton("Do Not Disturb")
        dnd_button.clicked.connect(self.enable_do_not_disturb)
        buttons.addWidget(dnd_button)

        layout.addLayout(buttons)
        card_row.addWidget(card)
        card_row.addStretch()
        overlay_layout.addLayout(card_row)
        overlay_layout.addStretch()

    def open_contact(self):
        self.contact_requested.emit(self.notification.contact_id)
        self.dismiss()

    def enable_do_not_disturb(self):
        self.do_not_disturb_requested.emit()
        self.dismiss()

    def dismiss(self):
        self.hide()
        self.dismissed.emit()

    def minimize(self):
        self.hide()
        self.minimize_requested.emit()

    def mousePressEvent(self, event):
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss()
            return
        super().keyPressEvent(event)


class MinimizedContactNotification(QPushButton):
    restore_requested = Signal()

    def __init__(self, notification: ContactNotification, parent=None):
        super().__init__(parent)
        self.notification = notification
        self.setObjectName("minimizedNotification")
        self.setFixedSize(224, 38)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(notification.contact_name)
        self.setAccessibleName(
            f"Restore notification for {notification.contact_name}"
        )
        self.setText(
            QFontMetrics(self.font()).elidedText(
                notification.contact_name,
                Qt.TextElideMode.ElideRight,
                188,
            )
        )
        self.setStyleSheet(
            """
            QPushButton#minimizedNotification {
                color: white;
                background-color: #3c467e;
                border: 1px solid #303963;
                border-radius: 4px;
                padding: 0 12px;
                text-align: left;
                font-weight: 600;
            }
            QPushButton#minimizedNotification:hover {
                background-color: #4a558f;
            }
            """
        )
        self.clicked.connect(self.restore_requested.emit)