import sys
import httpx
from contact_validation import validate_contact
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QPlainTextEdit
    )

class createContactWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Create Contact | ReConnect")
        self.setObjectName("createContactWindow")
        self.resize(1920, 1080)
        self.setMinimumSize(1050, 700)

        main_section = QHBoxLayout(self)
        main_section.setContentsMargins(0, 0, 0, 0)
        main_section.setSpacing(0)

        sidebar_container = QFrame()
        sidebar_container.setObjectName("branding")

        contact_container = QFrame()
        contact_container.setObjectName("contactPanel")

        main_section.addWidget(sidebar_container, 20)
        main_section.addWidget(contact_container, 80)

        contact_layout_VBox = QVBoxLayout(contact_container)
        contact_layout_VBox.setContentsMargins(20, 10, 10, 20)
        contact_layout_VBox.setSpacing(0)


        # Heading and subheading mini section
        heading = QLabel("Create Contact")
        heading.setObjectName("heading")

        subheading = QLabel("Create Contact Manually")
        subheading.setObjectName("subheading")

        heading_layout = QVBoxLayout()
        heading_layout.addWidget(heading, alignment=Qt.AlignTop)
        heading_layout.addWidget(subheading, alignment=Qt.AlignTop)
        heading_layout.setSpacing(1)

        contact_layout_VBox.addLayout(heading_layout)

        # Contact Form Section
        form_Grid = QGridLayout()
        form_Grid.setContentsMargins(0, 20, 0, 0)
        form_Grid.setSpacing(5)

        full_name_label = QLabel("Full Name")
        full_name_label.setObjectName("fullNameLabel")
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("First And Last Name")
        self.full_name_input.setAccessibleName("Full Name Input")
        full_name_label.setBuddy(self.full_name_input)

        email_label = QLabel("Email")
        email_label.setObjectName("emailLabel")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email Address")
        self.email_input.setAccessibleName("Email Address Input")
        email_label.setBuddy(self.email_input)

        phone_label = QLabel("Phone")
        phone_label.setObjectName("phoneLabel")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number")
        self.phone_input.setAccessibleName("Phone Number Input")
        phone_label.setBuddy(self.phone_input)

        organization_label = QLabel("Organization")
        organization_label.setObjectName("organizationLabel")
        self.organization_input = QLineEdit()
        self.organization_input.setPlaceholderText("Organization Name")
        self.organization_input.setAccessibleName("Organization Name Input")
        organization_label.setBuddy(self.organization_input)

        position_label = QLabel("Position")
        position_label.setObjectName("positionLabel")
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Position")
        self.position_input.setAccessibleName("Position Input")
        position_label.setBuddy(self.position_input)

        tags_label = QLabel("Tags")
        tags_label.setObjectName("tagsLabel")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags")
        self.tags_input.setAccessibleName("Tags Input")
        tags_label.setBuddy(self.tags_input)

        notes_label = QLabel("Notes")
        notes_label.setObjectName("notesLabel")
        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        self.notes_input.setAccessibleName("Notes Input")
        notes_label.setBuddy(self.notes_input)

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")

        saveContact_button = QPushButton("Save Contact")
        saveContact_button.setObjectName("saveContactButton")
        saveContact_button.clicked.connect(self.create_contact)

        form_Grid.addWidget(full_name_label, 0,0)
        form_Grid.addWidget(self.full_name_input, 1,0, 1,1)
        form_Grid.addWidget(email_label, 2,0)
        form_Grid.addWidget(self.email_input, 3,0)
        form_Grid.addWidget(phone_label, 2,1)
        form_Grid.addWidget(self.phone_input, 3,1)
        form_Grid.addWidget(organization_label, 4,0)
        form_Grid.addWidget(self.organization_input, 5,0)
        form_Grid.addWidget(position_label, 4,1)
        form_Grid.addWidget(self.position_input, 5,1)
        form_Grid.addWidget(tags_label, 6,0)
        form_Grid.addWidget(self.tags_input, 7,0)
        form_Grid.addWidget(notes_label, 8,0)
        form_Grid.addWidget(self.notes_input, 9,0)
        form_Grid.addWidget(cancel_button, 10,0)
        form_Grid.addWidget(saveContact_button, 10,1)

        contact_layout_VBox.addLayout(form_Grid)
        #contact_layout_VBox.addStretch()

        self.status = QLabel("")
        self.status.setObjectName("status")
        contact_layout_VBox.addWidget(self.status)

        self.apply_styles()

    def create_contact(self):
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        organization = self.organization_input.text().strip()
        position = self.position_input.text().strip()
        tags = self.tags_input.text().strip()
        notes = self.notes_input.toPlainText().strip()
        is_valid, error_message = validate_contact(full_name, email, phone)

        if not is_valid:
            self.status.setText(error_message)
            return


        try:
            response = httpx.post(
            "http://127.0.0.1:8000/auth/contacts",
                json={
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "organization": organization,
                    "position": position,
                    "tags": tags,
                    "notes": notes
                },
                timeout=5,
            )

            if response.status_code == 200:
                self.status.setText(
                    "Account created successfully."
                )
            elif response.status_code == 409:
                self.status.setText(
                    "That email is already registered."
                )
            else:
                self.status.setText(
                    "Account creation failed."
            )

        except httpx.RequestError:
            self.status.setText(
                "Unable to connect to the backend."
            )
        
    def apply_styles(self):
        self.setStyleSheet("""

            QGridLayout {

                spacing: 20px;
            }

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

            QFrame#contactPanel {
                background-color: #F5F5F5;
            }

            QLabel {
                font-size: 12x;
                font-weight: bold;
                background-color: transparent;
                padding-bottom: 5px;
                padding-top: 10px;
            }

            QLabel#heading {
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 5px;
            }

            QLabel#subheading {
                font-size: 16x;
                font-weight: normal;
                color: #444444;
                margin-bottom: 10px;
            }

            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 0 12px;
                min-height: 38px;
                font-size: 14px;
                selection-background-color: #3C457B;
                selection-color: white;
                margin-bottom: 15px;
            }
            
            QPlainTextEdit{
                min-height: 80px;
            }

            QLineEdit:focus {
                border: 2px solid #3C457B;
            }

            QPushButton {
                margin-top: 15px;
            }
            QPushButton#saveContactButton {
                background-color: #193D20;
                color: white;
                border: none;
                border-radius: 10px;
                min-height: 40px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton#saveContactButton:hover {
                background-color: #285630;
            }

            QPushButton#saveContactButton:pressed {
                background-color: #102B16;
            }

            QPushButton#cancelButton {
                background-color: transparent;
                color: #111111;
                border: 2px solid #CECECE;
                border-radius: 10px;
                min-height: 40px;
                font-size: 15px;
                font-weight: bold;
            }

            QPushButton#cancelButton:hover {
                background-color: #EFEFEF;
            }

            QPushButton#cancelButton:pressed {
                background-color: #D9D9D9;
            }

            QPushButton:focus {
                border: 2px solid #3C457B;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = createContactWindow()
    window.show()
    sys.exit(app.exec())





