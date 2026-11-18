import re
import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)


class RecoveryEmailWindow(QWidget):
    # Connect these signals to your application's navigation and backend.
    recovery_requested = Signal(str)
    cancel_requested = Signal()
    create_account_requested = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Recovery Email | ReConnect")
        self.setObjectName("recoveryEmailWindow")
        self.resize(1030, 580)
        self.setMinimumSize(1030, 580)

        # Main layout: branding on the left, recovery form on the right.
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        branding = QFrame()
        branding.setObjectName("branding")

        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")

        main_layout.addWidget(branding, 474)
        main_layout.addWidget(right_panel, 526)

        # Branding panel
        branding_layout = QVBoxLayout(branding)
        branding_layout.setContentsMargins(55, 82, 40, 17)
        branding_layout.setSpacing(0)

        brand_title = QLabel("ReConnect")
        brand_title.setObjectName("brandTitle")

        tagline = QLabel("Stay connected. Never let a\nrelationship fall through the cracks.")
        tagline.setObjectName("tagline")

        organization = QLabel("Tarbiya Institute")
        organization.setObjectName("organization")

        branding_layout.addWidget(brand_title)
        branding_layout.addWidget(tagline)
        branding_layout.addStretch()
        branding_layout.addWidget(organization)

        # Center the recovery card inside the right panel.
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(35, 35, 35, 35)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(377, 461)

        right_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(25, 33, 33, 22)
        card_layout.setSpacing(0)

        heading = QLabel("Recovery Email")
        heading.setObjectName("heading")
        heading.setFixedHeight(43)

        subtitle = QLabel("Please enter the email that is\nlinked to your account.")
        subtitle.setObjectName("subtitle")
        subtitle.setContentsMargins(8, 0, 0, 0)
        subtitle.setFixedHeight(44)

        card_layout.addWidget(heading)
        card_layout.addSpacing(7)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(43)

        # Email field
        email_label = QLabel("Email Address")
        email_label.setObjectName("fieldLabel")
        email_label.setContentsMargins(8, 0, 0, 0)
        email_label.setFixedHeight(18)

        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(44)
        self.email_input.setAccessibleName("Email Address")
        email_label.setBuddy(self.email_input)

        field_layout = QHBoxLayout()
        field_layout.setContentsMargins(8, 0, 0, 0)
        field_layout.addWidget(self.email_input)

        card_layout.addWidget(email_label)
        card_layout.addSpacing(7)
        card_layout.addLayout(field_layout)
        card_layout.addSpacing(31)

        # Cancel and send email buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(18)

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setFixedHeight(44)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.clicked.connect(self.cancel)

        send_button = QPushButton("Send Email")
        send_button.setObjectName("sendButton")
        send_button.setFixedHeight(44)
        send_button.setCursor(Qt.CursorShape.PointingHandCursor)
        send_button.clicked.connect(self.send_email)

        button_layout.addWidget(cancel_button, 148)
        button_layout.addWidget(send_button, 153)
        card_layout.addLayout(button_layout)
        card_layout.addSpacing(5)

        create_button = QPushButton("New to ReConnect? Create Account!")
        create_button.setObjectName("createButton")
        create_button.setFixedHeight(20)
        create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        create_button.clicked.connect(self.create_account)
        card_layout.addWidget(create_button)

        self.status = QLabel("")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status)
        card_layout.addStretch()

        self.email_input.returnPressed.connect(self.send_email)
        self.apply_styles()

    def send_email(self):
        email = self.email_input.text().strip()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
            self.status.setText("Please enter a valid email address.")
            self.email_input.setFocus()
            return

        self.status.setText("Recovery service is not connected yet.")
        self.recovery_requested.emit(email)

    def cancel(self):
        self.email_input.clear()
        self.status.clear()
        self.cancel_requested.emit()

    def create_account(self):
        self.create_account_requested.emit()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                color: #000000;
            }
            QFrame#branding {
                background-color: #3C457B;
            }
            QFrame#branding QLabel {
                color: white;
                background-color: transparent;
            }
            QLabel#brandTitle {
                font-size: 36px;
                font-weight: bold;
            }
            QLabel#tagline, QLabel#organization {
                font-size: 13px;
                font-weight: bold;
            }
            QFrame#rightPanel {
                background-color: #CECECE;
            }
            QFrame#loginCard {
                background-color: white;
                border-radius: 27px;
            }
            QLabel#heading {
                font-size: 36px;
                font-weight: bold;
            }
            QLabel#subtitle {
                font-size: 18px;
            }
            QLabel#fieldLabel {
                font-size: 13px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #D9D9D9;
                border: 2px solid transparent;
                border-radius: 9px;
                padding: 0 12px;
                font-size: 14px;
                selection-background-color: #3C457B;
                selection-color: white;
            }
            QLineEdit:focus {
                border-color: #3C457B;
            }
            QPushButton#cancelButton, QPushButton#sendButton {
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton#cancelButton {
                background-color: #D9D9D9;
            }
            QPushButton#cancelButton:hover {
                background-color: #C9C9C9;
            }
            QPushButton#sendButton {
                background-color: #193D20;
                color: white;
            }
            QPushButton#sendButton:hover {
                background-color: #285630;
            }
            QPushButton#createButton {
                background-color: transparent;
                border: none;
                font-size: 9px;
            }
            QPushButton#createButton:hover {
                text-decoration: underline;
            }
            QPushButton:focus {
                border: 1px solid #3C457B;
            }
            QLabel#status {
                font-size: 11px;
                color: #555555;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecoveryEmailWindow()
    window.show()
    sys.exit(app.exec())
