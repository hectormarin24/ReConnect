import sys
from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


STYLESHEET = """
QWidget {
    background-color: white;
    color: #111111;
    font-family: "Segoe UI";
    font-size: 13px;
}

QFrame#sidebar {
    background-color: #3c467e;
    border: none;
}

QWidget#navContainer {
    background: transparent;
}

QFrame#brandHeader {
    background-color: #101943;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}

QLabel#brand {
    background: transparent;
    color: white;
    font-weight: 700;
}

QPushButton#navButton {
    background: transparent;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0;
    text-align: left;
    padding-left: 18px;
}

QPushButton#navButton:hover {
    background-color: #4a558f;
}

QPushButton#navButton:checked {
    background-color: #6074b0;
}

QPushButton#navButton:pressed {
    background-color: #303a70;
}

QPushButton#navButton:focus {
    border: 1px solid #b7bee6;
}

QLabel#pageTitle {
    font-size: 26px;
    font-weight: 700;
}

QLabel#sectionTitle {
    font-size: 24px;
    font-weight: 700;
}

QFrame#card, QFrame#approvalsPanel {
    background-color: white;
    border: 1px solid #eeeeee;
}

QLabel#cardTitle {
    font-size: 16px;
}

QLabel#cardValue {
    color: #00852c;
    font-size: 26px;
    font-weight: 700;
}

QLabel#tableHeader {
    font-size: 11px;
}

QLabel#tableCell {
    font-size: 11px;
}

QLabel#userName {
    font-size: 11px;
    font-weight: 600;
}

QPushButton#approveButton {
    background-color: #008900;
    color: white;
    border: 1px solid #dddddd;
    font-size: 16px;
    font-weight: 600;
}

QPushButton#approveButton:hover {
    background-color: #007000;
}

QPushButton#rejectButton {
    background-color: white;
    color: #d50000;
    border: 1px solid #e4e4e4;
    font-size: 16px;
}

QPushButton#rejectButton:hover {
    background-color: #fff0f0;
}

QPushButton#approveButton:focus,
QPushButton#rejectButton:focus {
    border: 2px solid #3c467e;
}

QLabel#feedback {
    color: #596174;
    font-size: 12px;
}
"""


def create_label(text, object_name):
    label = QLabel(text)
    label.setObjectName(object_name)
    return label


def add_shadow(widget):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(3)
    shadow.setOffset(0, 2)
    shadow.setColor(QColor(0, 0, 0, 90))
    widget.setGraphicsEffect(shadow)


class StatCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumHeight(72)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 10, 20, 10)
        layout.setSpacing(10)

        layout.addWidget(create_label(title, "cardTitle"))

        self.value_label = create_label(str(value), "cardValue")
        layout.addWidget(self.value_label)

        add_shadow(self)

    def set_value(self, value):
        self.value_label.setText(str(value))


class AdministrationPage(QWidget):
    def __init__(self):
        super().__init__()

        self.user_count = 6
        self.pending_users = [
            {
                "id": 1,
                "name": "Fatima Ali",
                "email": "fatima@example.org",
                "requested": "Sep 29",
            },
            {
                "id": 2,
                "name": "Omar Hasan",
                "email": "omar@example.org",
                "requested": "Sep 30",
            },
        ]

        layout = QVBoxLayout(self)
        self.page_layout = layout
        layout.setContentsMargins(42, 50, 100, 30)
        layout.setSpacing(0)

        layout.addWidget(create_label("Administration", "pageTitle"))
        layout.addSpacing(12)

        description = QLabel(
            "Manage users, approvals, archived contacts, "
            "and administrative activity"
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        layout.addSpacing(23)

        cards_layout = QHBoxLayout()
        self.cards_layout = cards_layout
        cards_layout.setSpacing(34)

        self.users_card = StatCard("Users", self.user_count)
        self.pending_card = StatCard(
            "Pending Approvals", len(self.pending_users)
        )
        self.archived_card = StatCard("Archived Contacts", 0)

        cards_layout.addWidget(self.users_card, 1)
        cards_layout.addWidget(self.pending_card, 1)
        cards_layout.addWidget(self.archived_card, 1)

        layout.addLayout(cards_layout)
        layout.addSpacing(55)

        layout.addWidget(
            create_label("Pending User Approvals", "sectionTitle")
        )
        layout.addSpacing(8)

        panel = QFrame()
        panel.setObjectName("approvalsPanel")
        panel.setMinimumHeight(172)
        add_shadow(panel)

        panel_layout = QVBoxLayout(panel)
        self.panel_layout = panel_layout
        panel_layout.setContentsMargins(32, 8, 32, 22)
        panel_layout.setSpacing(0)

        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        header_layout.addWidget(create_label("User", "tableHeader"), 2)
        header_layout.addWidget(create_label("Email", "tableHeader"), 3)

        requested_header = create_label("Requested", "tableHeader")
        requested_header.setFixedWidth(85)
        header_layout.addWidget(requested_header)

        action_header = create_label("Action", "tableHeader")
        action_header.setFixedWidth(176)
        header_layout.addWidget(action_header)

        panel_layout.addWidget(header)

        self.rows_widget = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_widget)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(0)

        panel_layout.addWidget(self.rows_widget)

        self.empty_label = QLabel("No pending user approvals.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setMinimumHeight(100)
        panel_layout.addWidget(self.empty_label)

        panel_layout.addStretch()

        layout.addWidget(panel)

        self.feedback = create_label("", "feedback")
        layout.addSpacing(12)
        layout.addWidget(self.feedback)
        layout.addStretch()

        self.refresh_rows()

    def resizeEvent(self, event):
        width = self.width()
        horizontal_margin = max(24, min(42, round(width * 0.04)))
        right_margin = max(32, min(100, round(width * 0.1)))
        self.page_layout.setContentsMargins(
            horizontal_margin, 30, right_margin, 24
        )
        self.cards_layout.setSpacing(max(16, min(34, round(width * 0.032))))

        panel_margin = max(16, min(32, round(width * 0.032)))
        self.panel_layout.setContentsMargins(panel_margin, 8, panel_margin, 22)
        super().resizeEvent(event)

    def refresh_rows(self):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.deleteLater()

        for user in self.pending_users:
            self.rows_layout.addWidget(self.create_user_row(user))

        self.empty_label.setVisible(not self.pending_users)
        self.pending_card.set_value(len(self.pending_users))

    def create_user_row(self, user):
        row = QWidget()
        row.setFixedHeight(56)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        name = create_label(user["name"], "userName")
        name.setToolTip(user["name"])
        layout.addWidget(name, 2)

        email = create_label(user["email"], "tableCell")
        email.setToolTip(user["email"])
        layout.addWidget(email, 3)

        requested = create_label(user["requested"], "tableCell")
        requested.setFixedWidth(85)
        layout.addWidget(requested)

        actions = QWidget()
        actions.setFixedWidth(176)

        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(4)

        approve = QPushButton("Approve")
        approve.setObjectName("approveButton")
        approve.setFixedSize(86, 28)
        approve.setCursor(Qt.CursorShape.PointingHandCursor)
        approve.setAccessibleName(f"Approve {user['name']}")
        approve.clicked.connect(
            lambda checked=False, uid=user["id"]:
            self.resolve_user(uid, approved=True)
        )

        reject = QPushButton("Reject")
        reject.setObjectName("rejectButton")
        reject.setFixedSize(86, 28)
        reject.setCursor(Qt.CursorShape.PointingHandCursor)
        reject.setAccessibleName(f"Reject {user['name']}")
        reject.clicked.connect(
            lambda checked=False, uid=user["id"]:
            self.resolve_user(uid, approved=False)
        )

        actions_layout.addWidget(approve)
        actions_layout.addWidget(reject)

        layout.addWidget(actions)
        return row

    def resolve_user(self, user_id, approved):
        # Demo behavior: updates local data only.
        user = next(
            (u for u in self.pending_users if u["id"] == user_id),
            None,
        )
        if user is None:
            return

        self.pending_users.remove(user)

        if approved:
            self.user_count += 1
            self.users_card.set_value(self.user_count)

        result = "approved" if approved else "rejected"
        self.feedback.setText(f"{user['name']} {result}.")
        self.refresh_rows()


class ReConnectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReConnect — Administration")
        self.resize(1208, 680)
        self.setMinimumSize(900, 560)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.pages = {}

        main_layout.addWidget(self.create_sidebar())
        main_layout.addWidget(self.stack, 1)

        self.add_page("Admin", AdministrationPage())

        for name in (
            "Dashboard", "Contacts", "Cases", "Calendar",
            "To-Do", "Notifications", "Settings",
        ):
            self.add_page(name, self.create_placeholder(name))

        self.show_page("Admin")

    def create_sidebar(self):
        sidebar = QFrame()
        self.sidebar = sidebar
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        brand_header = QFrame()
        brand_header.setObjectName("brandHeader")
        brand_header.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        brand_layout = QVBoxLayout(brand_header)
        brand_layout.setContentsMargins(12, 8, 12, 8)
        self.brand = create_label("ReConnect", "brand")
        self.brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_layout.addWidget(self.brand)
        layout.addWidget(brand_header)
        layout.addSpacing(10)

        nav_container = QWidget()
        nav_container.setObjectName("navContainer")
        self.nav_layout = QVBoxLayout(nav_container)
        self.nav_layout.setContentsMargins(16, 0, 16, 0)
        self.nav_layout.setSpacing(0)
        layout.addWidget(nav_container, 1)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons = []

        for name in (
            "Dashboard", "Contacts", "Cases", "Calendar",
            "To-Do", "Notifications", "Admin", "Settings",
        ):
            button = QPushButton(name)
            button.setObjectName("navButton")
            button.setCheckable(True)
            button.setChecked(name == "Admin")
            button.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(
                lambda checked=False, page=name: self.show_page(page)
            )

            self.nav_group.addButton(button)
            self.nav_buttons.append(button)
            self.nav_layout.addWidget(button, 1)

        return sidebar

    def resizeEvent(self, event):
        sidebar_width = max(200, min(300, round(self.width() * 0.2)))
        self.sidebar.setFixedWidth(sidebar_width)

        side_margin = max(10, min(18, round(sidebar_width * 0.075)))
        self.nav_layout.setContentsMargins(side_margin, 0, side_margin, 0)
        self.sidebar.layout().setSpacing(max(6, round(sidebar_width * 0.05)))

        brand_font = QFont(self.brand.font())
        brand_font.setPixelSize(max(22, min(34, round(sidebar_width * 0.14))))
        self.brand.setFont(brand_font)

        self.sidebar.layout().activate()
        nav_font = QFont(self.nav_buttons[0].font())
        nav_font.setPixelSize(max(18, min(32, round(sidebar_width * 0.1))))
        for button in self.nav_buttons:
            button.setFont(nav_font)

        super().resizeEvent(event)

    def create_placeholder(self, name):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(42, 50, 42, 30)

        layout.addWidget(create_label(name, "pageTitle"))
        layout.addWidget(QLabel("This page is ready for your content."))
        layout.addStretch()

        return page

    def add_page(self, name, widget):
        self.pages[name] = widget
        self.stack.addWidget(widget)

    def show_page(self, name):
        self.stack.setCurrentWidget(self.pages[name])
        title = "Administration" if name == "Admin" else name
        self.setWindowTitle(f"ReConnect — {title}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    window = ReConnectWindow()
    window.show()

    sys.exit(app.exec())