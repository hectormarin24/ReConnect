import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ReConnect")
        self.setObjectName("loginWindow")
        self.resize(1920, 1080)
        self.setMinimumSize(1050, 700)

        # Main layout: branding on the left, login on the right.
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        branding = QFrame()
        branding.setObjectName("branding")

        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")

        main_layout.addWidget(branding, 47)
        main_layout.addWidget(right_panel, 53)

        # Branding panel
        branding_layout = QVBoxLayout(branding)
        branding_layout.setContentsMargins(55, 90, 40, 30)
        branding_layout.setSpacing(5)

        brand_title = QLabel("ReConnect")
        brand_title.setObjectName("brandTitle")

        organization = QLabel("Tarbiya Institute")
        organization.setObjectName("organization")

        branding_layout.addWidget(brand_title)
        branding_layout.addStretch()
        branding_layout.addWidget(organization)

        # Center the white card inside the right panel.
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(35, 35, 35, 35)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(460, 580)

        right_layout.addWidget(
            card,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 22)
        card_layout.setSpacing(0)

        heading = QLabel("Welcome Back!")
        heading.setObjectName("heading")

        subtitle = QLabel("Sign in to continue to ReConnect.")
        subtitle.setObjectName("subtitle")

        card_layout.addWidget(heading)
        card_layout.addSpacing(10)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(32)

        # Email field
        email_label = QLabel("Email Address")
        email_label.setObjectName("fieldLabel")

        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(50)
        self.email_input.setAccessibleName("Email Address")
        email_label.setBuddy(self.email_input)

        card_layout.addWidget(email_label)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(20)

        # Password field
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")

        self.password_input = QLineEdit()
        self.password_input.setFixedHeight(50)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAccessibleName("Password")
        password_label.setBuddy(self.password_input)

        card_layout.addWidget(password_label)
        card_layout.addSpacing(8)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(24)

        # Remember me and forgot password
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)

        self.remember_me = QCheckBox("Remember me")

        forgot_button = QPushButton("Forgot password?")
        forgot_button.setObjectName("forgotButton")
        forgot_button.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_button.clicked.connect(self.forgot_password)

        options_layout.addWidget(self.remember_me)
        options_layout.addStretch()
        options_layout.addWidget(forgot_button)

        card_layout.addLayout(options_layout)
        card_layout.addSpacing(28)

        # Sign-in button
        sign_in_button = QPushButton("SIGN IN")
        sign_in_button.setObjectName("signInButton")
        sign_in_button.setFixedHeight(50)
        sign_in_button.setCursor(Qt.CursorShape.PointingHandCursor)
        sign_in_button.clicked.connect(self.sign_in)

        card_layout.addWidget(sign_in_button)
        card_layout.addSpacing(20)

        # Account creation link
        create_button = QPushButton(
            "New to ReConnect? Create Account!"
        )
        create_button.setObjectName("createButton")
        create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        create_button.clicked.connect(self.create_account)

        card_layout.addWidget(create_button)
        card_layout.addSpacing(8)

        self.status = QLabel("")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(30)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(self.status)
        card_layout.addStretch()

        # Pressing Enter in either field submits the form.
        self.email_input.returnPressed.connect(self.sign_in)
        self.password_input.returnPressed.connect(self.sign_in)
        self.email_input.setFocus()

        self.apply_styles()

    def sign_in(self):
        email = self.email_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            self.status.setText("Please enter your email and password.")
            return

        self.status.setText("Authentication is not connected yet.")

    def forgot_password(self):
        self.status.setText("Password reset is not connected yet.")

    def create_account(self):
        self.status.setText("Account creation is not connected yet.")

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                color: #111111;
            }

            QFrame#branding {
                background-color: #3C457B;
            }

            QFrame#branding QLabel {
                color: white;
                background-color: transparent;
            }

            QLabel#brandTitle {
                font-size: 42px;
                font-weight: bold;
            }

            QLabel#tagline {
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#organization {
                font-size: 18px;
                font-weight: bold;
            }

            QFrame#rightPanel {
                background-color: #CECECE;
            }

            QFrame#loginCard {
                background-color: white;
                border-radius: 32px;
            }

            QLabel#heading {
                font-size: 36px;
                font-weight: bold;
            }

            QLabel#subtitle {
                font-size: 17px;
                color: #444444;
            }

            QLabel#fieldLabel {
                font-size: 18px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: #D9D9D9;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 0 12px;
                font-size: 17px;
                selection-background-color: #3C457B;
                selection-color: white;
            }

            QLineEdit:focus {
                border: 2px solid #3C457B;
            }

            QCheckBox {
                font-size: 12px;
                spacing: 6px;
            }

            QPushButton#signInButton {
                background-color: #193D20;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 17px;
                font-weight: bold;
            }

            QPushButton#signInButton:hover {
                background-color: #285630;
            }

            QPushButton#signInButton:pressed {
                background-color: #102B16;
            }

            QPushButton#forgotButton,
            QPushButton#createButton {
                background-color: transparent;
                border: none;
                padding: 6px;
                font-size: 12px;
            }

            QPushButton#forgotButton {
                color: #193D20;
                font-weight: bold;
            }

            QPushButton#forgotButton:hover,
            QPushButton#createButton:hover {
                text-decoration: underline;
            }

            QPushButton:focus {
                border: 1px solid #3C457B;
            }

            QLabel#status {
                font-size: 12px;
                color: #555555;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())