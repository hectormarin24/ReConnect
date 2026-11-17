
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QSizePolicy,
)


# Sample records based on the ReConnect Figma Contacts screen.
# These will be replaced with backend data in a later sprint.
SAMPLE_CONTACTS = [
    {
        "name": "Dr. Aisha Rahman",
        "email": "aisha@example.org",
        "organization": "Community Health Network",
        "tags": ["Doctor", "Donor"],
        "last_interaction": "Sep 22",
        "next_outreach": "Oct 5",
        "status": "Scheduled",
    },
    {
        "name": "Ahmed Khan",
        "email": "ahmed@example.org",
        "organization": "Community Volunteers",
        "tags": ["Volunteer", "Mentor"],
        "last_interaction": "Sep 18",
        "next_outreach": "Oct 2",
        "status": "Upcoming",
    },
    {
        "name": "Yusuf Khan",
        "email": "yusuf@example.org",
        "organization": "Community Partner",
        "tags": ["Community Partner"],
        "last_interaction": "Sep 28",
        "next_outreach": "Sep 28",
        "status": "Overdue",
    },
    {
        "name": "Sarah Ahmed",
        "email": "sarah@example.org",
        "organization": "Tarbiya Institute",
        "tags": ["Donor"],
        "last_interaction": "Sep 14",
        "next_outreach": "Sep 30",
        "status": "Due Today",
    },
]


class ContactsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Contacts | ReConnect")
        self.resize(1250, 700)
        self.setMinimumSize(1000, 650)

        self.contacts = SAMPLE_CONTACTS
        self.selected_filter = "All"
        self.filter_buttons = {}

        self.build_ui()
        self.apply_styles()
        self.update_contacts()

    def build_ui(self):
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------------------------
        # Sidebar
        # ----------------------------------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(25, 20, 25, 20)
        sidebar_layout.setSpacing(30)

        logo = QLabel("ReConnect")
        logo.setObjectName("logo")
        sidebar_layout.addWidget(logo)

        navigation_items = [
            "Dashboard",
            "Contacts",
            "Cases",
            "Calendar",
            "To-Do",
            "Notifications",
            "Admin",
            "Settings",
        ]

        for item in navigation_items:
            label = QLabel(item)
            label.setObjectName(
                "activeNav" if item == "Contacts" else "navItem"
            )
            label.setAlignment(Qt.AlignCenter)
            sidebar_layout.addWidget(label)

        sidebar_layout.addStretch()

        # ----------------------------------
        # Main content
        # ----------------------------------
        content = QFrame()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 15, 30, 30)
        content_layout.setSpacing(0)

        heading = QLabel("Contacts")
        heading.setObjectName("heading")

        subtitle = QLabel(
            "Search, organize, import, and maintain your community relationships"
        )
        subtitle.setObjectName("subtitle")

        content_layout.addWidget(heading)
        content_layout.addWidget(subtitle)

        # ----------------------------------
        # Search and action controls
        # ----------------------------------
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 25, 0, 0)
        actions_layout.setSpacing(20)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(
            "Search contacts by name, email, or organization..."
        )
        self.search_input.setAccessibleName("Search Contacts")
        self.search_input.textChanged.connect(self.update_contacts)

        # Buttons stacked on the right, as in Figma.
        button_column = QVBoxLayout()
        button_column.setSpacing(6)

        self.add_button = QPushButton("+ Add Contact")
        self.add_button.setObjectName("addButton")

        self.import_button = QPushButton("Import Contacts")
        self.import_button.setObjectName("importButton")

        button_column.addWidget(self.add_button)
        button_column.addWidget(self.import_button)

        actions_layout.addWidget(self.search_input, 1)
        actions_layout.addLayout(button_column)

        content_layout.addLayout(actions_layout)

        # ----------------------------------
        # Tag filter buttons
        # ----------------------------------
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(0, 30, 0, 30)
        filter_layout.setSpacing(12)

        categories = [
            "All",
            "Donors",
            "Volunteers",
            "Scholars",
            "Doctors",
            "Lawyers",
        ]

        for category in categories:
            button = QPushButton(category)
            button.setObjectName("filterButton")
            button.setCheckable(True)

            button.clicked.connect(
                lambda checked, tag=category: self.set_filter(tag)
            )

            self.filter_buttons[category] = button
            filter_layout.addWidget(button)

        filter_layout.addStretch()
        content_layout.addLayout(filter_layout)

        # ----------------------------------
        # Contacts table
        # ----------------------------------
        table_container = QFrame()
        table_container.setObjectName("tableContainer")

        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(20, 20, 20, 20)

        self.table = QTableWidget()
        self.table.setObjectName("contactsTable")

        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name",
            "Tags",
            "Last Interaction",
            "Next Outreach",
            "Status",
        ])

        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SingleSelection
        )
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.verticalHeader().setDefaultSectionSize(65)

        self.table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding,
        )

        table_layout.addWidget(self.table)

        self.empty_message = QLabel(
            "No contacts found."
        )
        self.empty_message.setObjectName("emptyMessage")
        self.empty_message.setAlignment(Qt.AlignCenter)
        self.empty_message.hide()

        table_layout.addWidget(self.empty_message)

        content_layout.addWidget(table_container, 1)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, 1)

        # Start with All selected.
        self.filter_buttons["All"].setChecked(True)

    def set_filter(self, category):
        """Select a tag filter and refresh the contacts table."""
        self.selected_filter = category

        for name, button in self.filter_buttons.items():
            button.setChecked(name == category)

        self.update_contacts()

    def update_contacts(self, *_):
        """Apply the search query and selected tag filter."""
        query = self.search_input.text().strip().casefold()

        # Figma uses plural labels; stored tags are singular.
        tag_mapping = {
            "Donors": "Donor",
            "Volunteers": "Volunteer",
            "Scholars": "Scholar",
            "Doctors": "Doctor",
            "Lawyers": "Lawyer",
        }

        selected_tag = tag_mapping.get(
            self.selected_filter
        )

        matching_contacts = []

        for contact in self.contacts:
            searchable_text = " ".join([
                contact["name"],
                contact["email"],
                contact["organization"],
            ]).casefold()

            matches_search = (
                not query or query in searchable_text
            )

            matches_tag = (
                selected_tag is None
                or selected_tag in contact["tags"]
            )

            if matches_search and matches_tag:
                matching_contacts.append(contact)

        self.table.setRowCount(len(matching_contacts))

        for row, contact in enumerate(matching_contacts):
            values = [
                contact["name"],
                " • ".join(contact["tags"]),
                contact["last_interaction"],
                contact["next_outreach"],
                contact["status"],
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(
                    Qt.AlignVCenter | Qt.AlignLeft
                )

                if column == 0:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                if column == 4 and value == "Overdue":
                    item.setForeground(
                        Qt.red
                    )

                self.table.setItem(row, column, item)

        has_results = bool(matching_contacts)
        self.table.setVisible(has_results)
        self.empty_message.setVisible(not has_results)

    def apply_styles(self):
        """Apply styling based on the ReConnect Figma mockup."""
        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                color: #111111;
            }

            QFrame#sidebar {
                background-color: #3C457B;
            }

            QLabel#logo {
                color: white;
                font-size: 32px;
            }

            QLabel#navItem {
                color: white;
                font-size: 21px;
                padding: 10px;
            }

            QLabel#activeNav {
                color: white;
                background-color: #16805D;
                font-size: 21px;
                font-weight: bold;
                border-radius: 3px;
                padding: 10px;
            }

            QFrame#content {
                background-color: #E7ECEF;
            }

            QLabel#heading {
                color: #111111;
                font-size: 32px;
                font-weight: bold;
            }

            QLabel#subtitle {
                color: #64748B;
                font-size: 12px;
                font-weight: bold;
            }

            QLineEdit#searchInput {
                background-color: white;
                border: 1px solid #D7DEE2;
                border-radius: 4px;
                padding: 8px 12px;
                min-height: 25px;
                font-size: 13px;
            }

            QLineEdit#searchInput:focus {
                border: 2px solid #226F5C;
            }

            QPushButton#addButton {
                background-color: #226F5C;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 10px 16px;
                font-weight: bold;
            }

            QPushButton#addButton:hover {
                background-color: #185542;
            }

            QPushButton#importButton {
                background-color: white;
                color: #226F5C;
                border: 1px solid #226F5C;
                border-radius: 3px;
                padding: 9px 14px;
                font-weight: bold;
            }

            QPushButton#importButton:hover {
                background-color: #E8F3EF;
            }

            QPushButton#filterButton {
                background-color: white;
                color: #226F5C;
                border: 1px solid #D5DFE3;
                border-radius: 4px;
                padding: 9px 16px;
                font-weight: bold;
                min-width: 45px;
            }

            QPushButton#filterButton:hover {
                background-color: #E8F3EF;
            }

            QPushButton#filterButton:checked {
                background-color: #226F5C;
                color: white;
                border: 1px solid #226F5C;
            }

            QFrame#tableContainer {
                background-color: white;
                border-radius: 5px;
            }

            QTableWidget#contactsTable {
                background-color: white;
                alternate-background-color: white;
                border: none;
                gridline-color: transparent;
                font-size: 12px;
            }

            QTableWidget#contactsTable::item {
                padding-left: 10px;
                border: none;
            }

            QTableWidget#contactsTable::item:selected {
                background-color: #E8F3EF;
                color: #111111;
            }

            QHeaderView::section {
                background-color: white;
                color: #64748B;
                border: none;
                padding: 12px;
                font-size: 11px;
                font-weight: bold;
            }

            QLabel#emptyMessage {
                color: #64748B;
                font-size: 15px;
                padding: 30px;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContactsWindow()
    window.show()
    sys.exit(app.exec())
