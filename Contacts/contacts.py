
import sys
# Provides Qt constants used for curser behavior and alignment
from PySide6.QtCore import Qt

# Allows for the use of QColor to set custom colors in the application
from PySide6.QtGui import QColor

# Imports widgets needed for the GUI, including layouts, labels, buttons, line edits, and tables
from PySide6.QtWidgets import (
    QApplication, QMessageBox, QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QButtonGroup, QAbstractItemView
)

# Sample contact data for demonstration purposes
CONTACTS = [
    ('Dr. Aisha Rahman', 'Doctor, Donor', 'Sep 22', 'Oct 5', 'Scheduled'),
    ('Ahmed Khan', 'Volunteer, Mentor', 'Sep 19', 'Oct 1', 'Upcoming'),
    ('Farah Farhan', 'Community Partner', 'Sep 20', 'Sep 28', 'Overdue'),
    ('Sarah Ahmed', 'Donor', 'Sep 14', 'Sep 30', 'No Tasks'),
    ('Maya Chen', 'Student, Volunteer', 'Oct 2', 'Oct 12', 'Scheduled'),
]

# The ContactsPage class defines the main window for the contacts management application.
class ContactsPage(QWidget):
    def __init__(self):
        super().__init__()

        # Set the window title and size
        self.setWindowTitle('ReConnect — Contacts')
        self.resize(1100, 650)

        # Sets the overall style of the application using a stylesheet
        # The stylesheet defines the appearance of various widgets, including the sidebar, buttons, labels, and table.
        self.setStyleSheet('''
            QWidget {
                background: #e7ecef;
                color: #1d2834;
                font-family: Segoe UI;
                font-size: 12px;
            }
         
            QFrame#sidebar {
                background: #384b85;
            }

            QLabel#brand {
                background: transparent;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }

            QPushButton#nav {
                color: white;
                background: transparent;
                border: none;
                text-align: left;
                padding: 11px 16px;
            }

            QPushButton#nav:hover {
                background: #4c619b;
            }

            QPushButton#navActive {
                color: white;
                background: #138447;
                border: none;
                text-align: left;
                padding: 11px 16px;
            }

            QLabel#heading {
                font-size: 23px;
                font-weight: 700;
            }

            QLabel#subtitle {
                color: #6d7880;
            }

            QLineEdit {
                background: white;
                border: 1px solid #d5dde1;
                border-radius: 4px;
                padding: 10px;
            }

            QPushButton#primary {
                background: #087c42;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 16px;
                font-weight: 600;
            }

            QPushButton#primary:hover {
                background: #096636;
            }

            QPushButton#filter {
                background: white;
                color: #167045;
                border: 1px solid #d8e4dd;
                border-radius: 4px;
                padding: 9px 15px;
            }

            QPushButton#filter:checked {
                background: #087c42;
                color: white;
            }

            QTableWidget {
                background-color: white;
                color: #1d2834;
                border: 1px solid #d8e0e4;
                border-radius: 5px;
                gridline-color: #edf0f2;
                selection-background-color: #e3f1e9;
                selection-color: #1d2834;
            }

            QTableWidget::item {
            padding: 8px;
            }

            QTableWidget::item:selected {
            background-color: #e3f1e9;
            color: #1d2834;
            }

            QHeaderView::section {
                background: white;
                color: #66737d;
                border: none;
                border-bottom: 1px solid #e4e9ec;
                padding: 13px;
                font-weight: 600;
            }
        ''')
        # Create the main layout
        # The main layout is a horizontal box layout that contains the sidebar and the main content area.
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        sidebar = QFrame(objectName='sidebar')
        sidebar.setFixedWidth(185)

        side = QVBoxLayout(sidebar)
        side.setContentsMargins(12, 20, 12, 20)

        brand = QLabel('ReConnect', objectName='brand')
        side.addWidget(brand)
        side.addSpacing(20)

        # Navigation buttons
        for name in (
            'Dashboard', 'Contacts', 'Cases', 'Calendar',
            'To-Do', 'Notifications', 'Admin', 'Settings'
        ):
            button = QPushButton(name)
            button.setObjectName(
                'navActive' if name == 'Contacts' else 'nav'
            )
            button.setCursor(Qt.PointingHandCursor)
            side.addWidget(button)

        side.addStretch()
        root.addWidget(sidebar)

        # Main content area
        main = QWidget()
        content = QVBoxLayout(main)
        content.setContentsMargins(32, 28, 32, 32)
        content.setSpacing(18)

        heading = QLabel('Contacts', objectName='heading')

        subtitle = QLabel(
            'Search, organize, import, and manage your community relationships.',
            objectName='subtitle'
        )

        content.addWidget(heading)
        content.addWidget(subtitle)

        # Search bar and buttons
        search_row = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText(
            'Search contacts by name, tags, or organization...'
        )
        self.search.textChanged.connect(self.update_contacts)

        search_row.addWidget(self.search, 1)

        add_btn = QPushButton('+ Add Contact', objectName='primary')
        add_btn.clicked.connect(
            lambda: self.show_placeholder('Add New Contact')
        )
        search_row.addWidget(add_btn)

        import_btn = QPushButton(
            'Import Contacts', objectName='filter'
        )
        import_btn.clicked.connect(
            lambda: self.show_placeholder('Import Contacts')
        )
        search_row.addWidget(import_btn)

        content.addLayout(search_row)

        # Tag filters
        filters = QHBoxLayout()
        filters.setSpacing(8)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)

        self.filter_buttons = {}

        # Create filter buttons for different contact tags
        for tag in ('All', 'Donor', 'Volunteer', 'Scholar', 'Doctor', 'Lawyer'):
            btn = QPushButton(tag, objectName='filter')
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)

            self.group.addButton(btn)
            btn.clicked.connect(self.update_contacts)

            filters.addWidget(btn)
            self.filter_buttons[tag] = btn

        self.filter_buttons['All'].setChecked(True)

        filters.addStretch()
        content.addLayout(filters)

        # Contacts table
        self.table = QTableWidget(0, 5)

        self.table.setHorizontalHeaderLabels([
            'Name',
            'Tags',
            'Last Interaction',
            'Next Outreach',
            'Status'
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)

        self.table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.table.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.table.setShowGrid(False)

        content.addWidget(self.table, 1)

        self.count = QLabel(objectName='subtitle')
        content.addWidget(self.count)

        root.addWidget(main, 1)

        self.update_contacts()

    # Search and filter contacts
    def update_contacts(self):
        query = self.search.text().strip().lower()

        tag = next(
            (
                name for name, btn in self.filter_buttons.items()
                if btn.isChecked()
            ),
            'All'
        )

        visible = [
            c for c in CONTACTS
            if (
                not query or query in ' '.join(c).lower()
            )
            and (
                tag == 'All'
                or tag.lower() in [
                t.strip().lower() for t in c[1].split(',')
            ]
        )
    ]
        # Update the table with the filtered contacts
        self.table.setRowCount(len(visible))

        
        # Loop through every matching contact
        for row, contact in enumerate(visible):
            self.table.setRowHeight(row, 55)

    
            for col, value in enumerate(contact):
                item = QTableWidgetItem(str(value))
                
                item.setForeground(QColor("#1d2834"))
                item.setTextAlignment(
                    Qt.AlignLeft | Qt.AlignVCenter
                )

        
                if col == 0:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

        
                elif col == 1:
                    item.setForeground(QColor("#167045"))

        
                elif col == 2:
                    item.setForeground(QColor("#66737d"))

       
                elif col == 3:
                    item.setForeground(QColor("#66737d"))

        
                elif col == 4:
                    status_colors = {
                        "Overdue": "#d84949",
                        "Scheduled": "#147b48",
                        "Upcoming": "#9b6a17",
                        "No Tasks": "#66737d"
                    }

                    color = status_colors.get(value, "#66737d")
                    item.setForeground(QColor(color))
                    item.setTextAlignment(Qt.AlignCenter)
                    
                self.table.setItem(row, col, item)
                print(f"Row {row}, Column {col}: {item.text()}")
                    

            self.count.setText(
                f"{len(visible)} contact(s) found."
            )


    # Placeholder for additional pages
    def show_placeholder(self, title):
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            title,
            f'{title} Placeholder for additional page.'
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = ContactsPage()
    window.show()

    sys.exit(app.exec())
