
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


class CreateAccountWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create Account | ReConnect")
        self.setObjectName("createAccountWindow")
        self.resize(1920, 1080)
        self.setMinimumSize(1050, 700)

        # Main layout: branding on the left, account creation on the right.
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

        tagline = QLabel("Build meaningful connections.")
        tagline.setObjectName("tagline")

        organization = QLabel("Tarbiya Institute")
        organization.setObjectName("organization")

        branding_layout.addWidget(brand_title)
        branding_layout.addWidget(tagline)
        branding_layout.addStretch()
        branding_layout.addWidget(organization)

        # Center the account creation card inside the right panel.
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(35, 35, 35, 35)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedSize(460, 700)

        right_layout.addWidget(
            card,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 28, 32, 22)
        card_layout.setSpacing(0)

        heading = QLabel("Create Account")
        heading.setObjectName("heading")

        subtitle = QLabel("Join ReConnect and get started.")
        subtitle.setObjectName("subtitle")

        card_layout.addWidget(heading)
        card_layout.addSpacing(8)
        card_layout.addWidget(subtitle)
        card_layout.addSpacing(24)

        # Full name field
        name_label = QLabel("Full Name")
        name_label.setObjectName("fieldLabel")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your full name")
        self.name_input.setFixedHeight(46)
        self.name_input.setAccessibleName("Full Name")
        name_label.setBuddy(self.name_input)

        card_layout.addWidget(name_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.name_input)
        card_layout.addSpacing(14)

        # Email field
        email_label = QLabel("Email Address")
        email_label.setObjectName("fieldLabel")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setFixedHeight(46)
        self.email_input.setAccessibleName("Email Address")
        email_label.setBuddy(self.email_input)

        card_layout.addWidget(email_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.email_input)
        card_layout.addSpacing(14)

        # Password field
        password_label = QLabel("Password")
        password_label.setObjectName("fieldLabel")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Create a password")
        self.password_input.setFixedHeight(46)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAccessibleName("Password")
        password_label.setBuddy(self.password_input)

        card_layout.addWidget(password_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(14)

        # Confirm password field
        confirm_label = QLabel("Confirm Password")
        confirm_label.setObjectName("fieldLabel")

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Re-enter your password")
        self.confirm_input.setFixedHeight(46)
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setAccessibleName("Confirm Password")
        confirm_label.setBuddy(self.confirm_input)

        card_layout.addWidget(confirm_label)
        card_layout.addSpacing(6)
        card_layout.addWidget(self.confirm_input)
        card_layout.addSpacing(16)

        # Terms and conditions
        self.terms_checkbox = QCheckBox(
            "I agree to the Terms of Service and Privacy Policy"
        )
        card_layout.addWidget(self.terms_checkbox)
        card_layout.addSpacing(20)

        # Create account button
        create_button = QPushButton("CREATE ACCOUNT")
        create_button.setObjectName("signInButton")
        create_button.setFixedHeight(50)
        create_button.setCursor(Qt.CursorShape.PointingHandCursor)
        create_button.clicked.connect(self.create_account)

        card_layout.addWidget(create_button)
        card_layout.addSpacing(12)

        # Link back to login
        login_button = QPushButton("Already have an account? Sign In")
        login_button.setObjectName("createButton")
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.clicked.connect(self.sign_in)

        card_layout.addWidget(login_button)
        card_layout.addSpacing(6)

        self.status = QLabel("")
        self.status.setObjectName("status")
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(30)
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(self.status)
        card_layout.addStretch()

        # Pressing Enter submits the form.
        self.confirm_input.returnPressed.connect(self.create_account)

        self.apply_styles()

    def create_account(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_input.text()

        if not name or not email or not password or not confirm_password:
            self.status.setText("Please complete all fields.")
            return

        if "@" not in email or "." not in email.split("@")[-1]:
            self.status.setText("Please enter a valid email address.")
            return

        if len(password) < 8:
            self.status.setText(
                "Password must be at least 8 characters."
            )
            return

        if password != confirm_password:
            self.status.setText("Passwords do not match.")
            return

        if not self.terms_checkbox.isChecked():
            self.status.setText("Please accept the terms to continue.")
            return

        self.status.setText(
            "Form validated! Account creation is not connected yet."
        )

    def sign_in(self):
        self.status.setText("Sign-in navigation is not connected yet.")

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
                font-size: 32px;
                font-weight: bold;
            }

            QLabel#subtitle {
                font-size: 15px;
                color: #444444;
            }

            QLabel#fieldLabel {
                font-size: 15px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: #D9D9D9;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 0 12px;
                font-size: 14px;
                selection-background-color: #3C457B;
                selection-color: white;
            }

            QLineEdit:focus {
                border: 2px solid #3C457B;
            }

            QCheckBox {
                font-size: 11px;
                spacing: 6px;
            }

            QPushButton#signInButton {
                background-color: #193D20;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 15px;
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

            QPushButton#createButton {
                color: #193D20;
                font-weight: bold;
            }

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
    window = CreateAccountWindow()
    window.show()
    sys.exit(app.exec())
