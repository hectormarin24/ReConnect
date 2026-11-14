"""Contact information screen for the ReConnect desktop application.

This module intentionally uses sample data only.  It can be run on its own
while the contact-detail, case, interaction, note, and follow-up APIs are being
designed.
"""

import sys

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDateEdit,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class FollowUpDialog(QDialog):
    """Small UI-only dialog used by the Schedule Follow-up button."""

    follow_up_saved = Signal(QDate, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Schedule Follow-up")
        self.setModal(True)
        self.setMinimumWidth(410)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        heading = QLabel("Schedule Follow-up")
        heading.setObjectName("dialogHeading")

        date_label = QLabel("Outreach date")
        date_label.setObjectName("dialogLabel")

        self.date_input = QDateEdit(QDate.currentDate().addDays(1))
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("MMMM d, yyyy")
        self.date_input.setMinimumDate(QDate.currentDate())

        note_label = QLabel("Optional note")
        note_label.setObjectName("dialogLabel")

        self.note_input = QPlainTextEdit()
        self.note_input.setPlaceholderText("Add a reminder for this outreach...")
        self.note_input.setFixedHeight(90)

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("dialogCancelButton")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save Follow-up")
        save_button.setObjectName("dialogSaveButton")
        save_button.clicked.connect(self.save_follow_up)

        button_row.addWidget(cancel_button)
        button_row.addWidget(save_button)

        layout.addWidget(heading)
        layout.addSpacing(6)
        layout.addWidget(date_label)
        layout.addWidget(self.date_input)
        layout.addSpacing(6)
        layout.addWidget(note_label)
        layout.addWidget(self.note_input)
        layout.addSpacing(8)
        layout.addLayout(button_row)

        self.setStyleSheet("""
            QDialog {
                background-color: #F7F9FA;
                font-family: Arial;
                color: #111111;
            }

            QLabel#dialogHeading {
                font-size: 22px;
                font-weight: bold;
            }

            QLabel#dialogLabel {
                font-size: 13px;
                font-weight: bold;
            }

            QDateEdit,
            QPlainTextEdit {
                background-color: white;
                border: 1px solid #CBD5DB;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }

            QPushButton {
                border-radius: 5px;
                padding: 9px 15px;
                font-weight: bold;
            }

            QPushButton#dialogCancelButton {
                background-color: white;
                color: #334155;
                border: 1px solid #CBD5DB;
            }

            QPushButton#dialogSaveButton {
                background-color: #157A08;
                color: white;
                border: 1px solid #157A08;
            }

            QPushButton#dialogSaveButton:hover {
                background-color: #116506;
            }
        """)

    def save_follow_up(self):
        self.follow_up_saved.emit(
            self.date_input.date(),
            self.note_input.toPlainText().strip(),
        )
        self.accept()


class ContactInfoWindow(QWidget):
    """UI-only version of the Contact Info mockup."""

    navigation_requested = Signal(str)

    NAVIGATION_ITEMS = [
        "Dashboard",
        "Contacts",
        "Cases",
        "Calendar",
        "To-Do",
        "Notifications",
        "Admin",
        "Settings",
    ]

    TABS = ["Overview", "Cases", "Interaction History", "Notes"]

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Contact Info | ReConnect")
        self.resize(1250, 760)
        self.setMinimumSize(1000, 650)

        self.nav_buttons = {}
        self.tab_buttons = {}

        self.build_ui()
        self.apply_styles()

    def build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(26, 18, 30, 24)
        root_layout.setSpacing(8)

        page_label = QLabel("Contact Info")
        page_label.setObjectName("pageLabel")
        root_layout.addWidget(page_label)

        workspace = QFrame()
        workspace.setObjectName("workspace")
        workspace_layout = QHBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        workspace_layout.addWidget(self.create_sidebar())
        workspace_layout.addWidget(self.create_content(), 1)
        root_layout.addWidget(workspace, 1)

        self.status_label = QLabel(
            "UI preview: backend connections are intentionally disabled."
        )
        self.status_label.setObjectName("statusLabel")
        self.status_label.setWordWrap(True)
        root_layout.addWidget(self.status_label)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 18, 20, 24)
        layout.setSpacing(8)

        logo = QLabel("ReConnect")
        logo.setObjectName("logo")
        layout.addWidget(logo)
        layout.addSpacing(8)

        group = QButtonGroup(self)
        group.setExclusive(True)

        for item in self.NAVIGATION_ITEMS:
            button = QPushButton(item)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, name=item: self.select_navigation(name)
            )
            group.addButton(button)
            self.nav_buttons[item] = button
            layout.addWidget(button)

        self.nav_buttons["Contacts"].setChecked(True)
        layout.addStretch()
        return sidebar

    def create_content(self):
        content = QFrame()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 28, 28)
        content_layout.setSpacing(0)

        heading = QLabel("Dr. Aisha Rahman")
        heading.setObjectName("heading")

        subtitle = QLabel("Doctor · Donor · Community Partner")
        subtitle.setObjectName("subtitle")

        content_layout.addWidget(heading)
        content_layout.addSpacing(3)
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(30)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(34)
        body_layout.addWidget(self.create_contact_card())
        body_layout.addLayout(self.create_detail_area(), 1)

        content_layout.addLayout(body_layout, 1)
        return content

    def create_contact_card(self):
        card = QFrame()
        card.setObjectName("contactCard")
        card.setFixedWidth(300)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(4)

        avatar = QLabel("AR")
        avatar.setObjectName("avatar")
        avatar.setFixedSize(72, 72)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name = QLabel("Dr. Aisha Rahman")
        name.setObjectName("cardName")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        email = QLabel("aisha@example.org")
        email.setObjectName("contactDetail")
        email.setAlignment(Qt.AlignmentFlag.AlignCenter)

        phone = QLabel("(916) 555-0104")
        phone.setObjectName("contactDetail")
        phone.setAlignment(Qt.AlignmentFlag.AlignCenter)

        organization = QLabel("Community Health Network")
        organization.setObjectName("contactDetail")
        organization.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(5)
        layout.addWidget(name)
        layout.addWidget(email)
        layout.addWidget(phone)
        layout.addWidget(organization)
        layout.addStretch()

        tags_heading = QLabel("Tags")
        tags_heading.setObjectName("tagsHeading")
        layout.addWidget(tags_heading)

        tag_row = QHBoxLayout()
        tag_row.setSpacing(8)
        for text in ("Doctor", "Donor", "Health"):
            tag = QLabel(text)
            tag.setObjectName("tag")
            tag_row.addWidget(tag)
        tag_row.addStretch()
        layout.addLayout(tag_row)
        layout.addSpacing(12)

        schedule_button = QPushButton("SCHEDULE FOLLOW-UP")
        schedule_button.setObjectName("scheduleButton")
        schedule_button.setCursor(Qt.CursorShape.PointingHandCursor)
        schedule_button.clicked.connect(self.open_follow_up_dialog)
        layout.addWidget(schedule_button)

        return card

    def create_detail_area(self):
        area = QVBoxLayout()
        area.setSpacing(16)

        tab_row = QHBoxLayout()
        tab_row.setSpacing(8)

        group = QButtonGroup(self)
        group.setExclusive(True)

        for index, tab_name in enumerate(self.TABS):
            button = QPushButton(tab_name)
            button.setObjectName("tabButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, page=index, name=tab_name:
                self.select_tab(page, name)
            )
            group.addButton(button)
            self.tab_buttons[tab_name] = button
            tab_row.addWidget(button)

        self.tab_buttons["Overview"].setChecked(True)
        tab_row.addStretch()
        area.addLayout(tab_row)

        self.pages = QStackedWidget()
        self.pages.setObjectName("detailPages")
        self.pages.addWidget(self.create_overview_page())
        self.pages.addWidget(
            self.create_placeholder_page(
                "Cases",
                "No cases are connected to this contact yet.",
            )
        )
        self.pages.addWidget(
            self.create_placeholder_page(
                "Interaction History",
                "Sep 22, 2026 · Phone Call · Outgoing\n\n"
                "Discuss the upcoming community health event and volunteer support.",
            )
        )
        self.pages.addWidget(
            self.create_placeholder_page(
                "Notes",
                "Key community health partner. Interested in youth wellness programming.",
            )
        )
        area.addWidget(self.pages, 1)
        return area

    def create_overview_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(10)

        history_heading = QLabel("Interaction History")
        history_heading.setObjectName("sectionHeading")
        layout.addWidget(history_heading)

        history_card = QFrame()
        history_card.setObjectName("infoCard")
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(20, 14, 20, 16)

        history_title = QLabel("Sep 22, 2026 · Phone Call · Outgoing")
        history_title.setObjectName("historyTitle")

        history_text = QLabel(
            "Discuss the upcoming community health event and volunteer support."
        )
        history_text.setObjectName("cardText")
        history_text.setWordWrap(True)

        history_layout.addWidget(history_title)
        history_layout.addSpacing(8)
        history_layout.addWidget(history_text)
        layout.addWidget(history_card)
        layout.addSpacing(4)

        lower_grid = QGridLayout()
        lower_grid.setContentsMargins(0, 0, 0, 0)
        lower_grid.setHorizontalSpacing(18)
        lower_grid.setVerticalSpacing(8)

        outreach_heading = QLabel("Next Outreach")
        outreach_heading.setObjectName("sectionHeading")
        notes_heading = QLabel("Relationship Notes")
        notes_heading.setObjectName("sectionHeading")

        lower_grid.addWidget(outreach_heading, 0, 0)
        lower_grid.addWidget(notes_heading, 0, 1)

        outreach_card = QFrame()
        outreach_card.setObjectName("infoCard")
        outreach_layout = QVBoxLayout(outreach_card)
        outreach_layout.setContentsMargins(20, 14, 20, 16)

        self.outreach_date = QLabel("October 5, 2026")
        self.outreach_date.setObjectName("outreachDate")
        self.outreach_note = QLabel("Schedule phone follow-up")
        self.outreach_note.setObjectName("cardText")
        self.outreach_note.setWordWrap(True)

        outreach_layout.addWidget(self.outreach_date)
        outreach_layout.addStretch()
        outreach_layout.addWidget(self.outreach_note)

        notes_card = QFrame()
        notes_card.setObjectName("infoCard")
        notes_layout = QVBoxLayout(notes_card)
        notes_layout.setContentsMargins(20, 14, 20, 16)

        note_text = QLabel(
            "Key community health partner. Interested in youth wellness programming."
        )
        note_text.setObjectName("centeredCardText")
        note_text.setWordWrap(True)
        note_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notes_layout.addWidget(note_text)

        lower_grid.addWidget(outreach_card, 1, 0)
        lower_grid.addWidget(notes_card, 1, 1)
        lower_grid.setColumnStretch(0, 1)
        lower_grid.setColumnStretch(1, 1)

        layout.addLayout(lower_grid)
        layout.addStretch()
        return page

    def create_placeholder_page(self, title, message):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 8, 0, 0)

        heading = QLabel(title)
        heading.setObjectName("sectionHeading")

        card = QFrame()
        card.setObjectName("placeholderCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)

        text = QLabel(message)
        text.setObjectName("placeholderText")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setWordWrap(True)

        card_layout.addStretch()
        card_layout.addWidget(text)
        card_layout.addStretch()

        layout.addWidget(heading)
        layout.addSpacing(8)
        layout.addWidget(card, 1)
        return page

    def select_navigation(self, item):
        self.nav_buttons[item].setChecked(True)
        self.navigation_requested.emit(item)

        if item == "Contacts":
            message = "Contacts selected."
        else:
            message = f"{item} selected. Navigation is ready to be connected."

        self.status_label.setText(message)

    def select_tab(self, index, name):
        self.pages.setCurrentIndex(index)
        self.status_label.setText(f"Showing {name}.")

    def open_follow_up_dialog(self):
        dialog = FollowUpDialog(self)
        dialog.follow_up_saved.connect(self.update_follow_up)
        dialog.exec()

    def update_follow_up(self, date, note):
        self.outreach_date.setText(date.toString("MMMM d, yyyy"))
        self.outreach_note.setText(note or "Scheduled follow-up")
        self.status_label.setText(
            f"Follow-up scheduled for {date.toString('MMMM d, yyyy')}."
        )

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                color: #111111;
            }

            ContactInfoWindow {
                background-color: #F7F7F7;
            }

            QLabel#pageLabel {
                color: #9AA0A6;
                font-size: 12px;
            }

            QFrame#sidebar {
                background-color: #3C497F;
            }

            QLabel#logo {
                color: white;
                font-size: 28px;
                padding: 2px 10px 12px 10px;
            }

            QPushButton#navButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 11px 10px;
                text-align: center;
                font-size: 15px;
            }

            QPushButton#navButton:hover {
                background-color: #4B598F;
            }

            QPushButton#navButton:checked {
                background-color: #226F5C;
                font-weight: bold;
            }

            QFrame#content {
                background-color: #E8EDF0;
            }

            QLabel#heading {
                font-size: 28px;
                font-weight: bold;
            }

            QLabel#subtitle {
                color: #666666;
                font-size: 12px;
            }

            QFrame#contactCard,
            QFrame#infoCard,
            QFrame#placeholderCard {
                background-color: #FFFBFB;
                border: none;
                border-radius: 12px;
            }

            QLabel#avatar {
                background-color: #EDF7ED;
                color: #0B6508;
                border-radius: 36px;
                font-size: 29px;
                font-weight: bold;
            }

            QLabel#cardName {
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#contactDetail,
            QLabel#cardText,
            QLabel#centeredCardText {
                color: #666666;
                font-size: 12px;
            }

            QLabel#tagsHeading {
                color: #666666;
                font-size: 11px;
            }

            QLabel#tag {
                color: #0B6508;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton#scheduleButton {
                background-color: #157A08;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 13px 12px;
                font-size: 11px;
                font-weight: bold;
            }

            QPushButton#scheduleButton:hover {
                background-color: #116506;
            }

            QPushButton#scheduleButton:pressed {
                background-color: #0B4F05;
            }

            QPushButton#tabButton {
                background-color: transparent;
                color: #0D5C16;
                border: none;
                border-bottom: 2px solid transparent;
                padding: 8px 7px;
                font-size: 12px;
                font-weight: bold;
            }

            QPushButton#tabButton:hover {
                color: #118221;
            }

            QPushButton#tabButton:checked {
                border-bottom: 2px solid #157A08;
                color: #157A08;
            }

            QLabel#sectionHeading {
                font-size: 16px;
                font-weight: bold;
            }

            QLabel#historyTitle {
                font-size: 12px;
                font-weight: bold;
            }

            QLabel#outreachDate {
                color: #087A0B;
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#placeholderText {
                color: #58656D;
                font-size: 14px;
            }

            QLabel#statusLabel {
                color: #64748B;
                font-size: 11px;
                min-height: 16px;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContactInfoWindow()
    window.show()
    sys.exit(app.exec())
